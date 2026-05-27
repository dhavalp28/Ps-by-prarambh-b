from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from repositories import vendor_repository
from repositories.state_repository import get_state_by_id
from repositories.city_repository import get_city_by_id
from schemas.vendor import VendorCreate, VendorUpdate
from core.security import hash_password

VALID_GENDERS = {"male", "female", "other"}


def _validate_location(db: Session, state_id: int, city_id: int):
    state = get_state_by_id(db, state_id)
    if not state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="State not found")

    city = get_city_by_id(db, city_id)
    if not city:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")

    if city.state_id != state_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City does not belong to the selected state"
        )


def get_all_vendors(db: Session):
    return vendor_repository.get_all_vendors(db)


def get_vendor(db: Session, vendor_id: int):
    vendor = vendor_repository.get_vendor_by_id(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    return vendor


def create_vendor(db: Session, payload: VendorCreate):
    if payload.gender.lower() not in VALID_GENDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid gender. Must be one of: {', '.join(VALID_GENDERS)}"
        )

    if vendor_repository.get_vendor_by_email(db, payload.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    if vendor_repository.get_vendor_by_phone(db, payload.phone):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone already registered")

    _validate_location(db, payload.state_id, payload.city_id)

    vendor_data = {
        "name": payload.name,
        "email": payload.email,
        "phone": payload.phone,
        "alt_phone": payload.alt_phone or None,
        "gender": payload.gender.lower(),
        "state_id": payload.state_id,
        "city_id": payload.city_id,
        "hashed_password": hash_password(payload.password),
    }

    return vendor_repository.create_vendor(db, vendor_data)


def update_vendor(db: Session, vendor_id: int, payload: VendorUpdate):
    vendor = vendor_repository.get_vendor_by_id(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    update_data = payload.model_dump(exclude_unset=True)

    if "gender" in update_data and update_data["gender"].lower() not in VALID_GENDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid gender. Must be one of: {', '.join(VALID_GENDERS)}"
        )

    if "email" in update_data and update_data["email"] != vendor.email:
        if vendor_repository.get_vendor_by_email(db, update_data["email"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")

    if "phone" in update_data and update_data["phone"] != vendor.phone:
        if vendor_repository.get_vendor_by_phone(db, update_data["phone"]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone already in use")

    # Validate location if either state or city is being changed
    new_state_id = update_data.get("state_id", vendor.state_id)
    new_city_id = update_data.get("city_id", vendor.city_id)

    if "state_id" in update_data or "city_id" in update_data:
        _validate_location(db, new_state_id, new_city_id)

    if "gender" in update_data:
        update_data["gender"] = update_data["gender"].lower()

    return vendor_repository.update_vendor(db, vendor, update_data)


def delete_vendor(db: Session, vendor_id: int):
    vendor = vendor_repository.get_vendor_by_id(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    vendor_repository.delete_vendor(db, vendor)
    return vendor


def toggle_active(db: Session, vendor_id: int):
    vendor = vendor_repository.get_vendor_by_id(db, vendor_id)
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    return vendor_repository.update_vendor(db, vendor, {"is_active": not vendor.is_active})
