from fastapi import HTTPException
from sqlalchemy.orm import Session
import random
import string

from repositories.business_code_repository import (
    get_business_code_by_code,
    get_business_code_by_business_id,
    create_business_code,
)


def generate_unique_business_code(db: Session, length: int = 8) -> str:
    """Generate a unique business code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        existing = get_business_code_by_code(db, code)
        if not existing:
            return code


def create_business_code_for_business(db: Session, business_id: int):
    """Create a business code for a new business"""
    # Check if code already exists
    existing_code = get_business_code_by_business_id(db, business_id)
    if existing_code:
        raise HTTPException(status_code=400, detail="Business code already exists for this business")
    
    code = generate_unique_business_code(db)
    return create_business_code(db, business_id, code)


def validate_business_code(db: Session, code: str):
    """Validate a business code"""
    business_code = get_business_code_by_code(db, code)
    
    if not business_code:
        return {
            "valid": False,
            "business_id": None,
            "business_name": None,
            "message": "Invalid business code"
        }
    
    if not business_code.is_active:
        return {
            "valid": False,
            "business_id": None,
            "business_name": None,
            "message": "Business code is inactive"
        }
    
    if not business_code.business.is_active:
        return {
            "valid": False,
            "business_id": None,
            "business_name": None,
            "message": "Business is inactive"
        }
    
    return {
        "valid": True,
        "business_id": business_code.business_id,
        "business_name": business_code.business.business_name,
        "message": "Valid business code"
    }
