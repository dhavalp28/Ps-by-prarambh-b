from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from api.deps import get_db
from schemas.vendor import VendorCreate, VendorUpdate, VendorResponse
from services import vendor_service

router = APIRouter()


@router.get("/", response_model=List[VendorResponse])
def list_vendors(db: Session = Depends(get_db)):
    return vendor_service.get_all_vendors(db)


@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    return vendor_service.get_vendor(db, vendor_id)


@router.post("/", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
def create_vendor(payload: VendorCreate, db: Session = Depends(get_db)):
    return vendor_service.create_vendor(db, payload)


@router.put("/{vendor_id}", response_model=VendorResponse)
def update_vendor(vendor_id: int, payload: VendorUpdate, db: Session = Depends(get_db)):
    return vendor_service.update_vendor(db, vendor_id, payload)


@router.delete("/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor_service.delete_vendor(db, vendor_id)


@router.patch("/{vendor_id}/toggle-active", response_model=VendorResponse)
def toggle_active(vendor_id: int, db: Session = Depends(get_db)):
    return vendor_service.toggle_active(db, vendor_id)
