from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile, status
from routers.deps import get_admin_user, get_db
from schemas.service_facility import (
    ServiceFacilityCreate,
    ServiceFacilityResponse,
    ServiceFacilityUpdate,
)
from services import service_facility_service
from services.audit_log_service import log_admin_action
from sqlalchemy.orm import Session
from utils.response import (
    error_server,
    success_create,
    success_delete,
    success_list,
    success_update,
)

router = APIRouter()


@router.get("/")
def list_service_facilities(
    active_only: bool = Query(False),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        facilities = service_facility_service.get_all_service_facilities(
            db, active_only=active_only, search=search
        )
        return success_list(
            title="Facilities & Services List",
            data=[ServiceFacilityResponse.model_validate(item) for item in facilities],
        )
    except Exception as e:
        return error_server(title="Facilities & Services List", error=str(e))


@router.get("/{facility_id}")
def get_service_facility(facility_id: int, db: Session = Depends(get_db)):
    try:
        facility = service_facility_service.get_service_facility(db, facility_id)
        return success_create(
            title="Facility/Service Details",
            data=ServiceFacilityResponse.model_validate(facility),
            message=None,
        )
    except Exception as e:
        return error_server(title="Get Facility/Service", error=str(e))


@router.post(
    "/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_user)]
)
async def create_service_facility(
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    is_active: bool = Form(True),
    icon: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
):
    try:
        payload = ServiceFacilityCreate.model_validate(
            {
                "name": name,
                "description": description,
                "is_active": is_active,
            }
        )
        facility = await service_facility_service.create_service_facility(
            db=db, payload=payload, icon=icon
        )
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="create",
            resource_type="service_facility",
            resource_id=facility.id,
            method=request.method,
            path=str(request.url.path),
            details={"name": facility.name},
        )
        return success_create(
            title="Facility/Service Created",
            data=ServiceFacilityResponse.model_validate(facility),
        )
    except Exception as e:
        return error_server(title="Create Facility/Service", error=str(e))


@router.put("/{facility_id}", dependencies=[Depends(get_admin_user)])
async def update_service_facility(
    facility_id: int,
    request: Request,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    icon: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
):
    try:
        payload_data = {}
        if name is not None:
            payload_data["name"] = name
        if description is not None:
            payload_data["description"] = description
        if is_active is not None:
            payload_data["is_active"] = is_active

        payload = ServiceFacilityUpdate.model_validate(payload_data)
        facility = await service_facility_service.update_service_facility(
            db=db, facility_id=facility_id, payload=payload, icon=icon
        )
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="update",
            resource_type="service_facility",
            resource_id=facility.id,
            method=request.method,
            path=str(request.url.path),
            details={"updated_fields": list(payload_data.keys())},
        )
        return success_update(
            title="Facility/Service Updated",
            data=ServiceFacilityResponse.model_validate(facility),
        )
    except Exception as e:
        return error_server(title="Update Facility/Service", error=str(e))


@router.delete("/{facility_id}", dependencies=[Depends(get_admin_user)])
def delete_service_facility(
    facility_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
):
    try:
        facility = service_facility_service.delete_service_facility(db, facility_id)
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="delete",
            resource_type="service_facility",
            resource_id=facility.id,
            method=request.method,
            path=str(request.url.path),
            details={"name": facility.name},
        )
        return success_delete(
            title="Facility/Service Deleted",
            resource_id=int(getattr(facility, "id")),
        )
    except Exception as e:
        return error_server(title="Delete Facility/Service", error=str(e))
