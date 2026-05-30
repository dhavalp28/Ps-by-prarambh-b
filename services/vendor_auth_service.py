from core.rbac import ROLE_VENDOR
from core.security import create_access_token, verify_password
from fastapi import HTTPException, status
from repositories.vendor_repository import get_vendor_by_email
from sqlalchemy.orm import Session


def vendor_login(db: Session, email: str, password: str):
    vendor = get_vendor_by_email(db, email)

    if not vendor or not verify_password(password, vendor.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not vendor.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vendor account is inactive",
        )

    token = create_access_token(
        {"sub": str(vendor.id), "role": ROLE_VENDOR, "entity_type": "vendor"}
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": vendor.id,
            "name": vendor.name,
            "email": vendor.email,
            "phone": vendor.phone,
            "role": ROLE_VENDOR,
            "entity_type": "vendor",
            "city_id": vendor.city_id,
            "state_id": vendor.state_id,
        },
    }
