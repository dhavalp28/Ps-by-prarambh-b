from sqlalchemy.orm import Session

from db.models.business import Business


def get_all_businesses(db: Session):
    return db.query(Business).order_by(Business.created_at.desc()).all()


def get_business_by_id(db: Session, business_id: int):
    return db.query(Business).filter(Business.id == business_id).first()


def create_business(db: Session, data: dict):
    business = Business(**data)
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


def update_business(db: Session, business: Business, update_data: dict):
    for key, value in update_data.items():
        setattr(business, key, value)
    db.commit()
    db.refresh(business)
    return business


def delete_business(db: Session, business: Business):
    db.delete(business)
    db.commit()
