from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from routers.deps import get_db, get_admin_user
from schemas.vendor import VendorCreate, VendorUpdate, VendorResponse
from services import vendor_service
from utils.response import (
    success_list, success_create, success_update, success_delete,
    error_not_found, error_duplicate, error_server
)

router = APIRouter()


@router.get("/")
def list_vendors(db: Session = Depends(get_db)):
    """Public endpoint - List all vendors"""
    try:
        vendors = vendor_service.get_all_vendors(db)
        return success_list(title="Vendors List", data=[VendorResponse.model_validate(v) for v in vendors])
    except Exception as e:
        return error_server(title="Vendors List", error=str(e))


@router.get("/{vendor_id}")
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    """Public endpoint - Get vendor details"""
    try:
        vendor = vendor_service.get_vendor(db, vendor_id)
        if not vendor:
            return error_not_found(title="Get Vendor", resource="Vendor")
        return success_list(title="Vendor Details", data=VendorResponse.model_validate(vendor))
    except Exception as e:
        return error_server(title="Get Vendor", error=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_user)])
def create_vendor(payload: VendorCreate, db: Session = Depends(get_db)):
    """Admin only - Create a new vendor"""
    try:
        vendor = vendor_service.create_vendor(db, payload)
        return success_create(title="Vendor Created", data=VendorResponse.model_validate(vendor))
    except ValueError as e:
        return error_duplicate(title="Create Vendor", resource="Vendor")
    except Exception as e:
        return error_server(title="Create Vendor", error=str(e))


@router.put("/{vendor_id}", dependencies=[Depends(get_admin_user)])
def update_vendor(vendor_id: int, payload: VendorUpdate, db: Session = Depends(get_db)):
    """Admin only - Update an existing vendor"""
    try:
        vendor = vendor_service.update_vendor(db, vendor_id, payload)
        if not vendor:
            return error_not_found(title="Update Vendor", resource="Vendor")
        return success_update(title="Vendor Updated", data=VendorResponse.model_validate(vendor))
    except Exception as e:
        return error_server(title="Update Vendor", error=str(e))


@router.delete("/{vendor_id}", dependencies=[Depends(get_admin_user)])
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    """Admin only - Delete a vendor"""
    try:
        vendor = vendor_service.delete_vendor(db, vendor_id)
        if not vendor:
            return error_not_found(title="Delete Vendor", resource="Vendor")
        return success_delete(title="Vendor Deleted", resource_id=vendor.id)
    except Exception as e:
        return error_server(title="Delete Vendor", error=str(e))


@router.patch("/{vendor_id}/toggle-active", dependencies=[Depends(get_admin_user)])
def toggle_active(vendor_id: int, db: Session = Depends(get_db)):
    """Admin only - Toggle vendor active status"""
    try:
        vendor = vendor_service.toggle_active(db, vendor_id)
        if not vendor:
            return error_not_found(title="Toggle Vendor Active", resource="Vendor")
        return success_update(title="Vendor Status Updated", data=VendorResponse.model_validate(vendor))
    except Exception as e:
        return error_server(title="Toggle Vendor Active", error=str(e))
