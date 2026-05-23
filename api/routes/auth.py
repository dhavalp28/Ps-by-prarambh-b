from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_db
from schemas.auth import RegisterSchema, LoginSchema
from services.auth_service import (
    register_user,
    login_user
)

router = APIRouter()

@router.post("/send-otp")
def send_otp(phone: str):
    return {
        "message": "OTP sent successfully",
        "otp": "123456"
    }

@router.post("/register")
def register(
    payload: RegisterSchema,
    db: Session = Depends(get_db)
):
    return register_user(db, payload)

@router.post("/login")
def login(
    payload: LoginSchema,
    db: Session = Depends(get_db)
):
    return login_user(
        db,
        payload.phone,
        payload.password
    )