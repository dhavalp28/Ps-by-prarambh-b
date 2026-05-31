from core.rbac import ROLE_ADMIN, ROLE_USER, ROLE_VENDOR
from core.security import decode_access_token
from db.session import SessionLocal
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from repositories.auth_session_repository import get_auth_session_by_key
from repositories.user_repository import get_user_by_id
from repositories.vendor_repository import get_vendor_by_id

security = HTTPBearer()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_current_auth_session(
    credentials: HTTPAuthorizationCredentials = Depends(security), db=Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        session_key = payload.get("sid")
        subject = payload.get("sub")
        if not session_key or subject is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth_session = get_auth_session_by_key(db, session_key)
    if auth_session is None or not bool(getattr(auth_session, "is_active", False)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"payload": payload, "auth_session": auth_session}


def get_current_user(
    current_auth=Depends(get_current_auth_session), db=Depends(get_db)
):
    payload = current_auth["payload"]
    entity_type = (payload.get("entity_type") or "user").lower()
    if entity_type == "vendor":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    user = get_user_by_id(db, int(user_id)) if user_id is not None else None
    if user is None or not bool(getattr(user, "is_active", True)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_admin_user(current_user=Depends(get_current_user)):
    user_role = (getattr(current_user, "role", None) or ROLE_USER).lower()
    if user_role != ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def get_current_vendor(
    current_auth=Depends(get_current_auth_session), db=Depends(get_db)
):
    payload = current_auth["payload"]
    vendor_id = payload.get("sub")
    role = (payload.get("role") or "").lower()
    entity_type = (payload.get("entity_type") or "").lower()

    if vendor_id is None or role != ROLE_VENDOR or entity_type != "vendor":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid vendor authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    vendor = get_vendor_by_id(db, int(vendor_id))
    if vendor is None or not bool(getattr(vendor, "is_active", False)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Vendor not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return vendor
