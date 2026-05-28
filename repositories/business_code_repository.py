from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from db.models.business_code import BusinessCode


def get_business_code_by_id(db: Session, code_id: int):
    return db.query(BusinessCode).filter(BusinessCode.id == code_id).first()


def get_business_code_by_code(db: Session, code: str):
    return db.query(BusinessCode).filter(BusinessCode.code == code).first()


def get_business_code_by_business_id(db: Session, business_id: int):
    return db.query(BusinessCode).filter(BusinessCode.business_id == business_id).first()


def create_business_code(db: Session, business_id: int, code: str):
    business_code = BusinessCode(business_id=business_id, code=code)
    db.add(business_code)
    db.commit()
    db.refresh(business_code)
    return business_code


def update_business_code(db: Session, business_code: BusinessCode, update_data: dict):
    for key, value in update_data.items():
        if value is not None:
            setattr(business_code, key, value)
    db.commit()
    db.refresh(business_code)
    return business_code


def delete_business_code(db: Session, business_code: BusinessCode):
    db.delete(business_code)
    db.commit()
