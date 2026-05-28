from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from routers.deps import get_db
from schemas.business_code import BusinessCodeResponse
from repositories.business_code_repository import (
    get_business_code_by_id,
    get_business_code_by_code,
    get_business_code_by_business_id,
)
from utils.response import success_list, error_not_found, error_server

router = APIRouter()


@router.get("/")
def list_business_codes(db: Session = Depends(get_db)):
    """Get all business codes"""
    try:
        from db.models.business_code import BusinessCode
        codes = db.query(BusinessCode).all()
        return success_list(title="Business Codes List", data=[BusinessCodeResponse.model_validate(c) for c in codes])
    except Exception as e:
        return error_server(title="Business Codes List", error=str(e))


@router.get("/{code_id}")
def get_business_code(code_id: int, db: Session = Depends(get_db)):
    """Get a specific business code"""
    try:
        code = get_business_code_by_id(db, code_id)
        if not code:
            return error_not_found(title="Get Business Code", resource="Business Code")
        return success_list(title="Business Code Details", data=BusinessCodeResponse.model_validate(code))
    except Exception as e:
        return error_server(title="Get Business Code", error=str(e))


@router.get("/by-code/{code}")
def get_code_by_code(code: str, db: Session = Depends(get_db)):
    """Get business code by code string"""
    try:
        business_code = get_business_code_by_code(db, code)
        if not business_code:
            return error_not_found(title="Get Business Code", resource="Business Code")
        return success_list(title="Business Code Details", data=BusinessCodeResponse.model_validate(business_code))
    except Exception as e:
        return error_server(title="Get Business Code", error=str(e))


@router.get("/by-business/{business_id}")
def get_code_by_business(business_id: int, db: Session = Depends(get_db)):
    """Get business code by business ID"""
    try:
        business_code = get_business_code_by_business_id(db, business_id)
        if not business_code:
            return error_not_found(title="Get Business Code", resource="Business Code")
        return success_list(title="Business Code Details", data=BusinessCodeResponse.model_validate(business_code))
    except Exception as e:
        return error_server(title="Get Business Code", error=str(e))
