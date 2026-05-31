from fastapi import APIRouter, Depends, Request
from routers.deps import get_current_auth_session, get_db
from schemas.admin_auth import AdminBootstrapSchema, AdminLoginSchema
from schemas.auth import (
    LoginSendOtpSchema,
    LoginVerifySchema,
    LogoutRequest,
    RefreshTokenRequest,
    RegisterInitSchema,
    RegisterVerifySchema,
    ResendOtpSchema,
)
from schemas.vendor_auth import VendorLoginSchema
from services.admin_auth_service import admin_login, bootstrap_admin
from services.otp_auth_service import (
    login_send_otp,
    login_verify,
    register_init,
    register_verify,
    resend_otp,
    update_phone_during_registration,
)
from services.session_auth_service import (
    logout_all_sessions,
    logout_session_by_key,
    refresh_session_tokens,
)
from services.vendor_auth_service import vendor_login
from sqlalchemy.orm import Session
from utils.response import error_server, error_validation, success_create, success_list

router = APIRouter()


# ============ Admin Authentication ============


@router.post("/admin/bootstrap")
def admin_bootstrap_endpoint(
    payload: AdminBootstrapSchema, request: Request, db: Session = Depends(get_db)
):
    try:
        result = bootstrap_admin(db, payload, request)
        return success_create(
            title="Admin Bootstrap Successful",
            data=result,
            message="First admin account created successfully",
        )
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_validation(
                title="Admin Bootstrap", error=str(getattr(e, "detail", e))
            )
        return error_server(title="Admin Bootstrap", error=str(e))


@router.post("/admin/login")
def admin_login_endpoint(
    payload: AdminLoginSchema, request: Request, db: Session = Depends(get_db)
):
    try:
        result = admin_login(db, payload.email, payload.password, payload, request)
        return success_create(
            title="Admin Login Successful",
            data=result,
            message="Admin login successful",
        )
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_validation(
                title="Admin Login", error=str(getattr(e, "detail", e))
            )
        return error_server(title="Admin Login", error=str(e))


@router.post("/vendor/login")
def vendor_login_endpoint(
    payload: VendorLoginSchema, request: Request, db: Session = Depends(get_db)
):
    try:
        result = vendor_login(db, payload.email, payload.password, payload, request)
        return success_create(
            title="Vendor Login Successful",
            data=result,
            message="Vendor login successful",
        )
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_validation(
                title="Vendor Login", error=str(getattr(e, "detail", e))
            )
        return error_server(title="Vendor Login", error=str(e))


@router.post("/refresh")
def refresh_token_endpoint(
    payload: RefreshTokenRequest, request: Request, db: Session = Depends(get_db)
):
    try:
        result = refresh_session_tokens(
            db,
            refresh_token=payload.refresh_token,
            request=request,
        )
        return success_create(
            title="Token Refreshed",
            data=result,
            message="Session refreshed successfully",
        )
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_validation(
                title="Refresh Token", error=str(getattr(e, "detail", e))
            )
        return error_server(title="Refresh Token", error=str(e))


@router.post("/logout")
def logout_endpoint(
    payload: LogoutRequest,
    current_auth=Depends(get_current_auth_session),
    db: Session = Depends(get_db),
):
    try:
        session_key = current_auth["payload"].get("sid")
        if session_key:
            logout_session_by_key(db, session_key)
        return success_list(
            title="Logout Successful",
            data={"success": True},
            message="Session revoked successfully",
        )
    except Exception as e:
        return error_server(title="Logout", error=str(e))


@router.post("/logout-all")
def logout_all_endpoint(
    current_auth=Depends(get_current_auth_session),
    db: Session = Depends(get_db),
):
    try:
        payload = current_auth["payload"]
        subject = payload.get("sub")
        entity_type = (payload.get("entity_type") or "user").lower()
        if subject is None:
            return error_validation(title="Logout All", error="Invalid session")

        logout_all_sessions(db, entity_type=entity_type, entity_id=int(subject))
        return success_list(
            title="Logout All Successful",
            data={"success": True},
            message="All active sessions revoked successfully",
        )
    except Exception as e:
        return error_server(title="Logout All", error=str(e))


# ============ OTP-Based Authentication (Production Flow) ============


@router.post("/register/init")
def register_init_endpoint(payload: RegisterInitSchema, db: Session = Depends(get_db)):
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
                "expires_at": result["expires_at"],
            },
            message=result["message"],
        )
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_validation(
                title="Register Init", error=str(getattr(e, "detail", e))
            )
        return error_server(title="Register Init", error=str(e))


@router.post("/register/verify")
def register_verify_endpoint(
    payload: RegisterVerifySchema, request: Request, db: Session = Depends(get_db)
):
    """
    Step 2: Verify OTP and create user
    """
    try:
        result = register_verify(
            db, payload.otp_session_id, payload.otp, payload, request
        )
        return success_create(
            title="Registration Successful",
            data=result,
            message="User registered and verified successfully",
        )
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_validation(
                title="Register Verify", error=str(getattr(e, "detail", e))
            )
        return error_server(title="Register Verify", error=str(e))


@router.post("/login/send-otp")
def login_send_otp_endpoint(payload: LoginSendOtpSchema, db: Session = Depends(get_db)):
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
                "expires_at": result["expires_at"],
            },
            message=result["message"],
        )
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_validation(
                title="Login Send OTP", error=str(getattr(e, "detail", e))
            )
        return error_server(title="Login Send OTP", error=str(e))


@router.post("/login/verify")
def login_verify_endpoint(
    payload: LoginVerifySchema, request: Request, db: Session = Depends(get_db)
):
    """
    Step 2: Verify OTP and login user
    """
    try:
        result = login_verify(db, payload.otp_session_id, payload.otp, payload, request)
        return success_create(
            title="Login Successful",
            data=result,
            message="Login successful",
        )
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_validation(
                title="Login Verify", error=str(getattr(e, "detail", e))
            )
        return error_server(title="Login Verify", error=str(e))


@router.post("/resend-otp")
def resend_otp_endpoint(payload: ResendOtpSchema, db: Session = Depends(get_db)):
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
                "expires_at": result["expires_at"],
            },
            message=result["message"],
        )
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_validation(
                title="Resend OTP", error=str(getattr(e, "detail", e))
            )
        return error_server(title="Resend OTP", error=str(e))


@router.post("/update-phone")
def update_phone_endpoint(
    otp_session_id: int, new_phone: str, db: Session = Depends(get_db)
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
                "expires_at": result["expires_at"],
            },
            message=result["message"],
        )
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_validation(
                title="Update Phone", error=str(getattr(e, "detail", e))
            )
        return error_server(title="Update Phone", error=str(e))
