from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from routers.deps import get_db, get_admin_user
from schemas.business import BusinessCreate, BusinessUpdate, BusinessResponse
from services import business_service
from utils.response import (
    success_list, success_create, success_update, success_delete,
    error_not_found, error_duplicate, error_server
)

router = APIRouter()


@router.get("/")
def list_businesses(city_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """Public endpoint - List all businesses"""
    try:
        businesses = business_service.get_all_businesses(db, city_id)
        return success_list(title="Businesses List", data=[BusinessResponse.model_validate(b) for b in businesses])
    except Exception as e:
        return error_server(title="Businesses List", error=str(e))


@router.get("/{business_id}")
def get_business(business_id: int, db: Session = Depends(get_db)):
    """Public endpoint - Get business details"""
    try:
        business = business_service.get_business(db, business_id)
        if not business:
            return error_not_found(title="Get Business", resource="Business")
        return success_list(title="Business Details", data=BusinessResponse.model_validate(business))
    except Exception as e:
        return error_server(title="Get Business", error=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_user)])
def create_business(payload: BusinessCreate, db: Session = Depends(get_db)):
    """Admin only - Create a new business"""
    try:
        business = business_service.create_business(db, payload)
        return success_create(title="Business Created", data=BusinessResponse.model_validate(business))
    except ValueError as e:
        return error_duplicate(title="Create Business", resource="Business")
    except Exception as e:
        return error_server(title="Create Business", error=str(e))


@router.put("/{business_id}", dependencies=[Depends(get_admin_user)])
def update_business(business_id: int, payload: BusinessUpdate, db: Session = Depends(get_db)):
    """Admin only - Update an existing business"""
    try:
        business = business_service.update_business(db, business_id, payload)
        if not business:
            return error_not_found(title="Update Business", resource="Business")
        return success_update(title="Business Updated", data=BusinessResponse.model_validate(business))
    except Exception as e:
        return error_server(title="Update Business", error=str(e))


@router.delete("/{business_id}", dependencies=[Depends(get_admin_user)])
def delete_business(business_id: int, db: Session = Depends(get_db)):
    """Admin only - Delete a business"""
    try:
        business = business_service.delete_business(db, business_id)
        if not business:
            return error_not_found(title="Delete Business", resource="Business")
        return success_delete(title="Business Deleted", resource_id=business.id)
    except Exception as e:
        return error_server(title="Delete Business", error=str(e))


@router.patch("/{business_id}/toggle-active", dependencies=[Depends(get_admin_user)])
def toggle_active(business_id: int, db: Session = Depends(get_db)):
    """Admin only - Toggle business active status"""
    try:
        business = business_service.toggle_active(db, business_id)
        if not business:
            return error_not_found(title="Toggle Business Active", resource="Business")
        return success_update(title="Business Status Updated", data=BusinessResponse.model_validate(business))
    except Exception as e:
        return error_server(title="Toggle Business Active", error=str(e))
