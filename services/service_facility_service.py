from typing import Optional

from fastapi import HTTPException, UploadFile, status
from repositories import service_facility_repository
from schemas.service_facility import ServiceFacilityCreate, ServiceFacilityUpdate
from sqlalchemy.orm import Session
from utils.upload import delete_upload, save_upload


def get_all_service_facilities(
    db: Session, active_only: bool = False, search: Optional[str] = None
):
    return service_facility_repository.get_all_service_facilities(
        db, active_only=active_only, search=search
    )


def get_service_facility(db: Session, facility_id: int):
    facility = service_facility_repository.get_service_facility_by_id(db, facility_id)
    if facility is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facility/Service not found",
        )
    return facility


async def create_service_facility(
    db: Session,
    payload: ServiceFacilityCreate,
    icon: Optional[UploadFile] = None,
):
    existing = service_facility_repository.get_service_facility_by_name(
        db, payload.name
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Facility/Service with this name already exists",
        )

    icon_url = None
    if icon and icon.filename:
        icon_url = await save_upload(icon, folder="service-facilities")

    try:
        return service_facility_repository.create_service_facility(
            db,
            {
                "name": payload.name,
                "description": payload.description,
                "icon": icon_url,
                "is_active": payload.is_active,
            },
        )
    except Exception:
        if icon_url:
            delete_upload(str(icon_url))
        raise


async def update_service_facility(
    db: Session,
    facility_id: int,
    payload: ServiceFacilityUpdate,
    icon: Optional[UploadFile] = None,
):
    facility = get_service_facility(db, facility_id)
    update_data = payload.model_dump(exclude_unset=True)

    current_name = getattr(facility, "name", None)
    if "name" in update_data and update_data["name"] != current_name:
        existing = service_facility_repository.get_service_facility_by_name(
            db, update_data["name"]
        )
        if existing is not None and int(getattr(existing, "id")) != int(
            getattr(facility, "id")
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Facility/Service with this name already exists",
            )

    old_icon = getattr(facility, "icon", None)
    new_icon_url = None
    if icon and icon.filename:
        new_icon_url = await save_upload(icon, folder="service-facilities")
        update_data["icon"] = new_icon_url

    try:
        updated = service_facility_repository.update_service_facility(
            db, facility, update_data
        )
        if new_icon_url is not None and old_icon is not None:
            delete_upload(str(old_icon))
        return updated
    except Exception:
        if new_icon_url:
            delete_upload(new_icon_url)
        raise


def delete_service_facility(db: Session, facility_id: int):
    facility = get_service_facility(db, facility_id)
    icon_url = getattr(facility, "icon", None)
    service_facility_repository.delete_service_facility(db, facility)
    if icon_url:
        delete_upload(str(icon_url))
    return facility
