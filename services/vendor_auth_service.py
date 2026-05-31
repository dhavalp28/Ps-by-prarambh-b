from core.rbac import ROLE_VENDOR
from core.security import verify_password
from fastapi import HTTPException, Request, status
from repositories.vendor_repository import get_vendor_by_email_case_insensitive
from services.session_auth_service import issue_session_tokens
from sqlalchemy.orm import Session


def vendor_login(db: Session, email: str, password: str, payload, request: Request):
    vendor = get_vendor_by_email_case_insensitive(db, email)

    if not vendor or not verify_password(
        password, getattr(vendor, "hashed_password", None)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not bool(getattr(vendor, "is_active", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vendor account is inactive",
        )

    return issue_session_tokens(
        db,
        entity=vendor,
        role=ROLE_VENDOR,
        entity_type="vendor",
        session_type="web",
        request=request,
        device_id=getattr(payload, "device_id", None),
        device_name=getattr(payload, "device_name", None),
        device_platform=getattr(payload, "device_platform", None),
    )
