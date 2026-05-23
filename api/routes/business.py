from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessResponse
from app.services import business_service

router = APIRouter()


@router.get("/", response_model=List[BusinessResponse])
def list_businesses(db: Session = Depends(get_db)):
    return business_service.get_all_businesses(db)


@router.get("/{business_id}", response_model=BusinessResponse)
def get_business(business_id: int, db: Session = Depends(get_db)):
    return business_service.get_business(db, business_id)


@router.post("/", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
def create_business(payload: BusinessCreate, db: Session = Depends(get_db)):
    return business_service.create_business(db, payload)


@router.put("/{business_id}", response_model=BusinessResponse)
def update_business(business_id: int, payload: BusinessUpdate, db: Session = Depends(get_db)):
    return business_service.update_business(db, business_id, payload)


@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_business(business_id: int, db: Session = Depends(get_db)):
    business_service.delete_business(db, business_id)


@router.patch("/{business_id}/toggle-active", response_model=BusinessResponse)
def toggle_active(business_id: int, db: Session = Depends(get_db)):
    return business_service.toggle_active(db, business_id)
