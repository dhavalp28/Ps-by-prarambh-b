from datetime import datetime, timedelta
from typing import Any

from core.config import settings
from core.rbac import ROLE_ADMIN, ROLE_USER, ROLE_VENDOR
from core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    generate_session_key,
    hash_token,
)
from fastapi import HTTPException, Request, status
from repositories.auth_session_repository import (
    create_auth_session,
    get_auth_session_by_key,
    revoke_all_user_sessions,
    revoke_all_vendor_sessions,
    revoke_auth_session,
    update_auth_session,
)
from repositories.user_repository import get_user_by_id
from repositories.vendor_repository import get_vendor_by_id
from sqlalchemy.orm import Session


def _get_lifetimes(role: str, session_type: str) -> tuple[timedelta, timedelta | None]:
    normalized_role = (role or ROLE_USER).lower()

    if normalized_role == ROLE_ADMIN:
        return (
            timedelta(minutes=settings.ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES),
            timedelta(days=settings.ADMIN_REFRESH_TOKEN_EXPIRE_DAYS),
        )

    if normalized_role == ROLE_VENDOR:
        return (
            timedelta(minutes=settings.VENDOR_ACCESS_TOKEN_EXPIRE_MINUTES),
            timedelta(days=settings.VENDOR_REFRESH_TOKEN_EXPIRE_DAYS),
        )

    # Mobile app users should remain signed in long-term.
    return (
        timedelta(minutes=settings.USER_ACCESS_TOKEN_EXPIRE_MINUTES),
        timedelta(days=settings.USER_REFRESH_TOKEN_EXPIRE_DAYS),
    )


def _build_claims(entity: Any, role: str, entity_type: str, session_key: str) -> dict:
    return {
        "sub": str(entity.id),
        "role": role,
        "entity_type": entity_type,
        "sid": session_key,
    }


def _extract_request_meta(
    request: Request,
    *,
    device_id: str | None = None,
    device_name: str | None = None,
    device_platform: str | None = None,
):
    forwarded_for = request.headers.get("x-forwarded-for", "")
    ip_address = forwarded_for.split(",")[0].strip() if forwarded_for else None
    if not ip_address and request.client is not None:
        ip_address = request.client.host

    return {
        "device_id": device_id,
        "device_name": device_name,
        "device_platform": device_platform,
        "user_agent": request.headers.get("user-agent"),
        "ip_address": ip_address,
    }


def _serialize_user(user: Any) -> dict:
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone,
        "role": getattr(user, "role", ROLE_USER),
        "is_phone_verified": getattr(user, "is_phone_verified", False),
        "is_active": bool(getattr(user, "is_active", True)),
    }


def _serialize_vendor(vendor: Any) -> dict:
    return {
        "id": vendor.id,
        "name": vendor.name,
        "email": vendor.email,
        "phone": vendor.phone,
        "role": ROLE_VENDOR,
        "entity_type": "vendor",
        "city_id": vendor.city_id,
        "state_id": vendor.state_id,
        "is_active": bool(getattr(vendor, "is_active", True)),
    }


def issue_session_tokens(
    db: Session,
    *,
    entity: Any,
    role: str,
    entity_type: str,
    session_type: str,
    request: Request,
    device_id: str | None = None,
    device_name: str | None = None,
    device_platform: str | None = None,
):
    access_delta, refresh_delta = _get_lifetimes(role, session_type)
    now = datetime.utcnow()
    session_key = generate_session_key()
    claims = _build_claims(entity, role, entity_type, session_key)

    meta = _extract_request_meta(
        request,
        device_id=device_id,
        device_name=device_name,
        device_platform=device_platform,
    )

    refresh_expires_at = now + refresh_delta if refresh_delta is not None else None
    auth_session = create_auth_session(
        db,
        {
            "user_id": entity.id if entity_type != "vendor" else None,
            "vendor_id": entity.id if entity_type == "vendor" else None,
            "role": role,
            "entity_type": entity_type,
            "session_type": session_type,
            "session_key": session_key,
            "refresh_token_hash": None,
            "device_id": meta["device_id"],
            "device_name": meta["device_name"],
            "device_platform": meta["device_platform"],
            "user_agent": meta["user_agent"],
            "ip_address": meta["ip_address"],
            "is_active": True,
            "last_seen_at": now,
            "access_expires_at": now + access_delta,
            "refresh_expires_at": refresh_expires_at,
        },
    )

    access_token = create_access_token(claims, expires_delta=access_delta)
    refresh_token = create_refresh_token(
        claims,
        expires_delta=refresh_delta
        or timedelta(days=settings.USER_REFRESH_TOKEN_EXPIRE_DAYS),
    )

    update_auth_session(
        db,
        auth_session,
        {
            "refresh_token_hash": hash_token(refresh_token),
            "last_seen_at": now,
            "access_expires_at": now + access_delta,
            "refresh_expires_at": refresh_expires_at,
        },
    )

    user_payload = (
        _serialize_vendor(entity)
        if entity_type == "vendor"
        else _serialize_user(entity)
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "access_expires_at": now + access_delta,
        "refresh_expires_at": refresh_expires_at,
        "session_id": auth_session.id,
        "user": user_payload,
    }


def refresh_session_tokens(db: Session, *, refresh_token: str, request: Request):
    payload = decode_refresh_token(refresh_token)
    session_key = payload.get("sid")
    subject = payload.get("sub")
    entity_type = (payload.get("entity_type") or "user").lower()
    role = (payload.get("role") or ROLE_USER).lower()

    if not session_key or not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    auth_session = get_auth_session_by_key(db, session_key)
    if not auth_session or not bool(getattr(auth_session, "is_active", False)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked",
        )

    expected_hash = hash_token(refresh_token)
    if getattr(auth_session, "refresh_token_hash", None) != expected_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token rotation detected",
        )

    refresh_expires_at = getattr(auth_session, "refresh_expires_at", None)
    if refresh_expires_at is not None and refresh_expires_at < datetime.utcnow():
        revoke_auth_session(db, auth_session)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )

    if entity_type == "vendor":
        entity = get_vendor_by_id(db, int(subject))
        if entity is None or not bool(getattr(entity, "is_active", False)):
            revoke_auth_session(db, auth_session)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Vendor not found or inactive",
            )
    else:
        entity = get_user_by_id(db, int(subject))
        if entity is None or not bool(getattr(entity, "is_active", True)):
            revoke_auth_session(db, auth_session)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

    access_delta, refresh_delta = _get_lifetimes(
        role, getattr(auth_session, "session_type", "web")
    )
    now = datetime.utcnow()
    claims = _build_claims(entity, role, entity_type, session_key)
    new_access_token = create_access_token(claims, expires_delta=access_delta)
    new_refresh_token = create_refresh_token(
        claims,
        expires_delta=refresh_delta
        or timedelta(days=settings.USER_REFRESH_TOKEN_EXPIRE_DAYS),
    )

    meta = _extract_request_meta(request)
    next_refresh_expires_at = now + refresh_delta if refresh_delta is not None else None
    update_auth_session(
        db,
        auth_session,
        {
            "refresh_token_hash": hash_token(new_refresh_token),
            "last_seen_at": now,
            "access_expires_at": now + access_delta,
            "refresh_expires_at": next_refresh_expires_at,
            "user_agent": meta["user_agent"],
            "ip_address": meta["ip_address"],
        },
    )

    user_payload = (
        _serialize_vendor(entity)
        if entity_type == "vendor"
        else _serialize_user(entity)
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "access_expires_at": now + access_delta,
        "refresh_expires_at": next_refresh_expires_at,
        "session_id": auth_session.id,
        "user": user_payload,
    }


def logout_session_by_key(db: Session, session_key: str):
    auth_session = get_auth_session_by_key(db, session_key)
    if auth_session is not None and bool(getattr(auth_session, "is_active", False)):
        revoke_auth_session(db, auth_session)
    return auth_session


def logout_all_sessions(db: Session, *, entity_type: str, entity_id: int):
    if entity_type == "vendor":
        return revoke_all_vendor_sessions(db, entity_id)
    return revoke_all_user_sessions(db, entity_id)
