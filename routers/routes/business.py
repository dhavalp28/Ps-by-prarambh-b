from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request, status
from routers.deps import get_admin_user, get_db
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
        return success_list(
            title="Business Details", data=BusinessResponse.model_validate(business)
        )
    except Exception as e:
        return error_server(title="Get Business", error=str(e))


@router.post(
    "/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_user)]
)
def create_business(
    payload: BusinessCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
):
    """Admin only - Create a new business"""
    try:
        business = business_service.create_business(db, payload)
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="create",
            resource_type="business",
            resource_id=business.id,
            method=request.method,
            path=str(request.url.path),
            details={"business_name": business.business_name},
        )
        return success_create(
            title="Business Created", data=BusinessResponse.model_validate(business)
        )
    except ValueError as e:
        return error_duplicate(title="Create Business", resource="Business")
    except Exception as e:
        return error_server(title="Create Business", error=str(e))


@router.put("/{business_id}", dependencies=[Depends(get_admin_user)])
def update_business(
    business_id: int,
    payload: BusinessUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
):
    """Admin only - Update an existing business"""
    try:
        business = business_service.update_business(db, business_id, payload)
        if not business:
            return error_not_found(title="Update Business", resource="Business")
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="update",
            resource_type="business",
            resource_id=business.id,
            method=request.method,
            path=str(request.url.path),
            details={
                "updated_fields": list(payload.model_dump(exclude_unset=True).keys())
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
        return success_delete(title="Business Deleted", resource_id=business.id)
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
