from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from routers.deps import get_db
from schemas.auth import (
    RegisterInitSchema,
    RegisterVerifySchema,
    LoginSendOtpSchema,
    LoginVerifySchema,
    ResendOtpSchema
)
from services.otp_auth_service import (
    register_init,
    register_verify,
    login_send_otp,
    login_verify,
    resend_otp,
    update_phone_during_registration
)
from utils.response import (
    success_create,
    error_server,
    error_validation
)

router = APIRouter()


# ============ OTP-Based Authentication (Production Flow) ============

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