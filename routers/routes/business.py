import json
from typing import Optional, cast

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from routers.deps import get_admin_user, get_db
from schemas.brand import BranchBusinessResponse
from schemas.business import BusinessCreate, BusinessResponse, BusinessUpdate
from services import business_service
from services.audit_log_service import log_admin_action
from sqlalchemy.orm import Session
from utils.response import (
    error_duplicate,
    error_not_found,
    error_server,
    success_create,
    success_delete,
    success_list,
    success_update,
)

router = APIRouter()

SPECIAL_LIST_FIELDS = {
    "facility_ids",
    "gallery_items",
    "gallery_delete_ids",
    "gallery_reorder",
}


def _clean_form_value(value):
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def _parse_list_field(form, field_name: str, expect_json: bool = False):
    values = form.getlist(field_name)
    if not values:
        return None

    if len(values) > 1 and not expect_json:
        return [
            _clean_form_value(value)
            for value in values
            if _clean_form_value(value) is not None
        ]

    raw_value = values[0]
    if raw_value in (None, ""):
        return []

    if not isinstance(raw_value, str):
        return raw_value

    raw_value = raw_value.strip()
    if not raw_value:
        return []

    if expect_json or raw_value.startswith("[") or raw_value.startswith("{"):
        try:
            return json.loads(raw_value)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSON for {field_name}",
            ) from exc

    if "," in raw_value:
        return [item.strip() for item in raw_value.split(",") if item.strip()]

    return [raw_value]


async def _parse_business_payload(request: Request, is_update: bool = False):
    content_type = (request.headers.get("content-type") or "").lower()
    model_cls = BusinessUpdate if is_update else BusinessCreate

    if (
        "multipart/form-data" in content_type
        or "application/x-www-form-urlencoded" in content_type
    ):
        form = await request.form()
        payload_data = {}

        for field_name in model_cls.model_fields.keys():
            if field_name in SPECIAL_LIST_FIELDS:
                continue
            if field_name in form:
                value = form.get(field_name)
                if hasattr(value, "filename"):
                    continue
                payload_data[field_name] = _clean_form_value(value)

        for field_name in SPECIAL_LIST_FIELDS:
            if field_name in form:
                payload_data[field_name] = _parse_list_field(
                    form,
                    field_name,
                    expect_json=field_name != "facility_ids",
                )

        gallery_files = [
            cast(UploadFile, file)
            for file in form.getlist("gallery_files")
            if getattr(file, "filename", None)
        ]
        return model_cls.model_validate(payload_data), gallery_files

    body = await request.json()
    return model_cls.model_validate(body), []


@router.get("/")
def list_businesses(
    city_id: Optional[int] = Query(None), db: Session = Depends(get_db)
):
    """Public endpoint - List all businesses"""
    try:
        businesses = business_service.get_all_businesses(db, city_id)
        return success_list(
            title="Businesses List",
            data=[BusinessResponse.model_validate(b) for b in businesses],
        )
    except Exception as e:
        return error_server(title="Businesses List", error=str(e))


@router.get("/{business_id}")
def get_business(business_id: int, db: Session = Depends(get_db)):
    """Public endpoint - Get business details"""
    try:
        business = business_service.get_business(db, business_id)
        if not business:
            return error_not_found(title="Get Business", resource="Business")
        return success_create(
            title="Business Details", data=BusinessResponse.model_validate(business)
        )
    except Exception as e:
        return error_server(title="Get Business", error=str(e))


@router.get("/{business_id}/branches")
def get_business_branches(
    business_id: int,
    search: Optional[str] = Query(None, description="Search by branch name or address"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Public endpoint - Get other branches of the same brand for a business"""
    try:
        branches = business_service.get_business_branches(
            db, business_id=business_id, search=search, limit=limit
        )
        return success_list(
            title="Business Branches",
            data=[BranchBusinessResponse.model_validate(branch) for branch in branches],
        )
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_not_found(title="Get Business Branches", resource="Business")
        return error_server(title="Get Business Branches", error=str(e))


@router.post(
    "/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_user)]
)
async def create_business(
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
):
    """Admin only - Create a new business. Supports JSON and multipart form-data."""
    try:
        payload, gallery_files = await _parse_business_payload(request, is_update=False)
        create_payload = cast(BusinessCreate, payload)
        business = await business_service.create_business(
            db, create_payload, gallery_files
        )
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="create",
            resource_type="business",
            resource_id=business.id,
            method=request.method,
            path=str(request.url.path),
            details={
                "business_name": business.business_name,
                "facility_ids": create_payload.facility_ids,
                "gallery_upload_count": len(gallery_files),
            },
        )
        return success_create(
            title="Business Created", data=BusinessResponse.model_validate(business)
        )
    except ValueError:
        return error_duplicate(title="Create Business", resource="Business")
    except Exception as e:
        return error_server(title="Create Business", error=str(e))


@router.put("/{business_id}", dependencies=[Depends(get_admin_user)])
async def update_business(
    business_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
):
    """Admin only - Update an existing business. Supports JSON and multipart form-data."""
    try:
        payload, gallery_files = await _parse_business_payload(request, is_update=True)
        update_payload = cast(BusinessUpdate, payload)
        business = await business_service.update_business(
            db, business_id, update_payload, gallery_files
        )
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="update",
            resource_type="business",
            resource_id=business.id,
            method=request.method,
            path=str(request.url.path),
            details={
                "updated_fields": list(
                    update_payload.model_dump(exclude_unset=True).keys()
                ),
                "gallery_upload_count": len(gallery_files),
            },
        )
        return success_update(
            title="Business Updated", data=BusinessResponse.model_validate(business)
        )
    except Exception as e:
        return error_server(title="Update Business", error=str(e))


@router.delete("/{business_id}", dependencies=[Depends(get_admin_user)])
def delete_business(
    business_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
):
    """Admin only - Delete a business"""
    try:
        business = business_service.delete_business(db, business_id)
        if not business:
            return error_not_found(title="Delete Business", resource="Business")
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="delete",
            resource_type="business",
            resource_id=business.id,
            method=request.method,
            path=str(request.url.path),
            details={"business_name": business.business_name},
        )
        return success_delete(title="Business Deleted", resource_id=business_id)
    except Exception as e:
        return error_server(title="Delete Business", error=str(e))


@router.patch("/{business_id}/toggle-active", dependencies=[Depends(get_admin_user)])
def toggle_active(
    business_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
):
    """Admin only - Toggle business active status"""
    try:
        business = business_service.toggle_active(db, business_id)
        if not business:
            return error_not_found(title="Toggle Business Active", resource="Business")
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="toggle_active",
            resource_type="business",
            resource_id=business.id,
            method=request.method,
            path=str(request.url.path),
            details={"is_active": business.is_active},
        )
        return success_update(
            title="Business Status Updated",
            data=BusinessResponse.model_validate(business),
        )
    except Exception as e:
        return error_server(title="Toggle Business Active", error=str(e))
