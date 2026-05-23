from fastapi import HTTPException
from sqlalchemy.orm import Session

from repositories.user_repository import (
    get_user_by_phone,
    get_user_by_email,
    create_user
)
from repositories.state_repository import get_state_by_id
from repositories.city_repository import get_city_by_id

from core.security import (
    hash_password,
    verify_password,
    create_access_token
)




def register_user(db: Session, data):
    existing_phone = get_user_by_phone(db, data.phone)

    if existing_phone:
        raise HTTPException(
            status_code=400,
            detail="Phone already registered"
        )

    existing_email = get_user_by_email(db, data.email)

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Validate state exists
    state = get_state_by_id(db, data.state_id)

    if not state:
        raise HTTPException(
            status_code=404,
            detail="State not found"
        )

    # Validate city exists and belongs to the given state
    city = get_city_by_id(db, data.city_id)

    if not city:
        raise HTTPException(
            status_code=404,
            detail="City not found"
        )

    if city.state_id != data.state_id:
        raise HTTPException(
            status_code=400,
            detail="City does not belong to the selected state"
        )

    hashed_password = hash_password(data.password)

    user_data = {
        "first_name": data.first_name,
        "last_name": data.last_name,
        "email": data.email,
        "phone": data.phone,
        "state_id": data.state_id,
        "city_id": data.city_id,
        "referral_code": data.referral_code,
        "hashed_password": hashed_password
    }

    user = create_user(db, user_data)

    token = create_access_token(
        {"sub": str(user.id)}
    )

    return {
        "message": "User registered successfully",
        "access_token": token
    }


def login_user(db: Session, phone: str, password: str):
    user = get_user_by_phone(db, phone)

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid credentials"
        )

    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {"sub": str(user.id)}
    )

    return {
        "message": "Login successful",
        "access_token": token
    }
