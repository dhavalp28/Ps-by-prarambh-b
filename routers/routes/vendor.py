from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from routers.deps import get_db
from schemas.vendor import VendorCreate, VendorUpdate, VendorResponse
from services import vendor_service
from utils.response import (
    success_list, success_create, success_update, success_delete,
    error_not_found, error_duplicate, error_server
)

router = APIRouter()


@router.get("/")
def list_vendors(db: Session = Depends(get_db)):
    try:
        vendors = vendor_service.get_all_vendors(db)
        return success_list(title="Vendors List", data=vendors)
    except Exception as e:
        return error_server(title="Vendors List", error=str(e))


@router.get("/{vendor_id}")
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    try:
        vendor = vendor_service.get_vendor(db, vendor_id)
        if not vendor:
            return error_not_found(title="Get Vendor", resource="Vendor")
        return success_list(title="Vendor Details", data=vendor)
    except Exception as e:
        return error_server(title="Get Vendor", error=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vendor(payload: VendorCreate, db: Session = Depends(get_db)):
    try:
        vendor = vendor_service.create_vendor(db, payload)
        return success_create(title="Vendor Created", data=vendor)
    except ValueError as e:
        return error_duplicate(title="Create Vendor", resource="Vendor")
    except Exception as e:
        return error_server(title="Create Vendor", error=str(e))


@router.put("/{vendor_id}")
def update_vendor(vendor_id: int, payload: VendorUpdate, db: Session = Depends(get_db)):
    try:
        vendor = vendor_service.update_vendor(db, vendor_id, payload)
        if not vendor:
            return error_not_found(title="Update Vendor", resource="Vendor")
        return success_update(title="Vendor Updated", data=vendor)
    except Exception as e:
        return error_server(title="Update Vendor", error=str(e))


@router.delete("/{vendor_id}")
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    try:
        vendor = vendor_service.delete_vendor(db, vendor_id)
        if not vendor:
            return error_not_found(title="Delete Vendor", resource="Vendor")
        return success_delete(title="Vendor Deleted", resource_id=vendor.id)
    except Exception as e:
        return error_server(title="Delete Vendor", error=str(e))


@router.patch("/{vendor_id}/toggle-active")
def toggle_active(vendor_id: int, db: Session = Depends(get_db)):
    try:
        vendor = vendor_service.toggle_active(db, vendor_id)
        if not vendor:
            return error_not_found(title="Toggle Vendor Active", resource="Vendor")
        return success_update(title="Vendor Status Updated", data=vendor)
    except Exception as e:
        return error_server(title="Toggle Vendor Active", error=str(e))
