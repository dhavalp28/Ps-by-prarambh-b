from core.rbac import ROLE_ADMIN
from core.security import create_access_token, hash_password, verify_password
from fastapi import HTTPException, status
from repositories.city_repository import get_city_by_id
from repositories.state_repository import get_state_by_id
from repositories.user_repository import (
    create_user,
    get_admin_user_count,
    get_user_by_email,
    get_user_by_email_case_insensitive,
    get_user_by_phone,
)
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session


def bootstrap_admin(db: Session, payload):
    try:
        admin_count = get_admin_user_count(db)
    except OperationalError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed during admin bootstrap. Please verify DATABASE_URL/SSL settings and try again.",
        ) from e
    if admin_count > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin already exists. Bootstrap is disabled.",
        )

    existing_email = get_user_by_email(db, payload.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    existing_phone = get_user_by_phone(db, payload.phone)
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone already registered",
        )

    if payload.state_id is not None:
        state = get_state_by_id(db, payload.state_id)
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="State not found",
            )

    if payload.city_id is not None:
        city = get_city_by_id(db, payload.city_id)
        if not city:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="City not found",
            )
        if payload.state_id is not None and city.state_id != payload.state_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="City does not belong to the selected state",
            )

    user = create_user(
        db,
        {
            "first_name": payload.first_name,
            "last_name": payload.last_name,
            "email": payload.email,
            "phone": payload.phone,
            "state_id": payload.state_id,
            "city_id": payload.city_id,
            "hashed_password": hash_password(payload.password),
            "role": ROLE_ADMIN,
            "is_phone_verified": True,
        },
    )

    token = create_access_token({"sub": str(user.id), "role": user.role})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "is_phone_verified": user.is_phone_verified,
        },
    }


def admin_login(db: Session, email: str, password: str):
    try:
        user = get_user_by_email_case_insensitive(db, email)
    except OperationalError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed during admin login. Please verify DATABASE_URL/SSL settings and try again.",
        ) from e
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if (user.role or "user").lower() != ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    token = create_access_token({"sub": str(user.id), "role": user.role})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "is_phone_verified": user.is_phone_verified,
        },
    }
