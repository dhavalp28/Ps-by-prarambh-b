from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from routers.deps import get_db
from schemas.auth import (
    RegisterInitSchema,
    RegisterVerifySchema,
    LoginSendOtpSchema,
    LoginVerifySchema,
    ResendOtpSchema,
    RegisterSchema,
    LoginSchema
)
from services.otp_auth_service import (
    register_init,
    register_verify,
    login_send_otp,
    login_verify,
    resend_otp,
    update_phone_during_registration
)
from services.auth_service import (
    register_user,
    login_user
)
from utils.response import (
    success_create,
    success_list,
    error_server,
    error_validation,
    error_not_found
)

router = APIRouter()


# ============ OTP-Based Authentication (New Flow) ============

@router.post("/register/init")
def register_init_endpoint(
    payload: RegisterInitSchema,
    db: Session = Depends(get_db)
):
    """
    Step 1: Initialize registration - validate data and send OTP
    """
    try:
        result = register_init(db, payload)
        return success_create(
            title="Registration Initiated",
            data={
                "otp_session_id": result["otp_session_id"],
                "phone": result["phone"],
                "expires_at": result["expires_at"]
            },
            message=result["message"]
        )
    except Exception as e:
        if hasattr(e, 'status_code'):
            return error_validation(title="Register Init", error=str(e.detail))
        return error_server(title="Register Init", error=str(e))


@router.post("/register/verify")
def register_verify_endpoint(
    payload: RegisterVerifySchema,
    db: Session = Depends(get_db)
):
    """
    Step 2: Verify OTP and create user
    """
    try:
        result = register_verify(db, payload.otp_session_id, payload.otp)
        return success_create(
            title="Registration Successful",
            data={
                "access_token": result["access_token"],
                "token_type": result["token_type"],
                "user": result["user"]
            },
            message="User registered and verified successfully"
        )
    except Exception as e:
        if hasattr(e, 'status_code'):
            return error_validation(title="Register Verify", error=str(e.detail))
        return error_server(title="Register Verify", error=str(e))


@router.post("/login/send-otp")
def login_send_otp_endpoint(
    payload: LoginSendOtpSchema,
    db: Session = Depends(get_db)
):
    """
    Step 1: Send OTP for login
    """
    try:
        result = login_send_otp(db, payload.phone)
        return success_create(
            title="OTP Sent",
            data={
                "otp_session_id": result["otp_session_id"],
                "phone": result["phone"],
                "expires_at": result["expires_at"]
            },
            message=result["message"]
        )
    except Exception as e:
        if hasattr(e, 'status_code'):
            return error_validation(title="Login Send OTP", error=str(e.detail))
        return error_server(title="Login Send OTP", error=str(e))


@router.post("/login/verify")
def login_verify_endpoint(
    payload: LoginVerifySchema,
    db: Session = Depends(get_db)
):
    """
    Step 2: Verify OTP and login user
    """
    try:
        result = login_verify(db, payload.otp_session_id, payload.otp)
        return success_create(
            title="Login Successful",
            data={
                "access_token": result["access_token"],
                "token_type": result["token_type"],
                "user": result["user"]
            },
            message="Login successful"
        )
    except Exception as e:
        if hasattr(e, 'status_code'):
            return error_validation(title="Login Verify", error=str(e.detail))
        return error_server(title="Login Verify", error=str(e))


@router.post("/resend-otp")
def resend_otp_endpoint(
    payload: ResendOtpSchema,
    db: Session = Depends(get_db)
):
    """
    Resend OTP - invalidate old OTP and generate new one
    """
    try:
        result = resend_otp(db, payload.otp_session_id)
        return success_create(
            title="OTP Resent",
            data={
                "otp_session_id": result["otp_session_id"],
                "phone": result["phone"],
                "expires_at": result["expires_at"]
            },
            message=result["message"]
        )
    except Exception as e:
        if hasattr(e, 'status_code'):
            return error_validation(title="Resend OTP", error=str(e.detail))
        return error_server(title="Resend OTP", error=str(e))


@router.post("/update-phone")
def update_phone_endpoint(
    otp_session_id: int,
    new_phone: str,
    db: Session = Depends(get_db)
):
    """
    Update phone number during registration - invalidate old OTP and generate new one
    """
    try:
        result = update_phone_during_registration(db, otp_session_id, new_phone)
        return success_create(
            title="Phone Updated",
            data={
                "otp_session_id": result["otp_session_id"],
                "phone": result["phone"],
                "expires_at": result["expires_at"]
            },
            message=result["message"]
        )
    except Exception as e:
        if hasattr(e, 'status_code'):
            return error_validation(title="Update Phone", error=str(e.detail))
        return error_server(title="Update Phone", error=str(e))


# ============ Legacy Password-Based Authentication (Kept for backward compatibility) ============

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