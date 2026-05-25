from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from routers.deps import get_db
from schemas.auth import RegisterSchema, LoginSchema
from services.auth_service import (
    register_user,
    login_user
)
from utils.response import (
    success_create, error_server, error_validation
)

router = APIRouter()

@router.post("/send-otp")
def send_otp(phone: str):
    try:
        # TODO: Implement actual OTP sending logic
        return success_create(
            title="OTP Sent",
            data={"otp": "123456"},
            message="OTP sent successfully to your phone"
        )
    except Exception as e:
        return error_server(title="Send OTP", error=str(e))

@router.post("/register")
def register(
    payload: RegisterSchema,
    db: Session = Depends(get_db)
):
    try:
        result = register_user(db, payload)
        if isinstance(result, dict) and "error" in result:
            return error_validation(title="Register", error=result["error"])
        return success_create(title="User Registered", data=result, message="Registration successful")
    except Exception as e:
        return error_server(title="Register", error=str(e))

@router.post("/login")
def login(
    payload: LoginSchema,
    db: Session = Depends(get_db)
):
    try:
        result = login_user(db, payload.phone, payload.password)
        if isinstance(result, dict) and "error" in result:
            return error_validation(title="Login", error=result["error"])
        return success_create(title="Login Successful", data=result, message="Login successful")
    except Exception as e:
        return error_server(title="Login", error=str(e))