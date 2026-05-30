from typing import Optional

from db.models.service_facility import ServiceFacility
from sqlalchemy import func
from sqlalchemy.orm import Session


def get_all_service_facilities(
    db: Session, active_only: bool = False, search: Optional[str] = None
):
    query = db.query(ServiceFacility)

    if active_only:
        query = query.filter(ServiceFacility.is_active == True)

    if search:
        term = f"%{search.strip()}%"
        query = query.filter(ServiceFacility.name.ilike(term))

    return query.order_by(ServiceFacility.name.asc(), ServiceFacility.id.asc()).all()


def get_service_facility_by_id(db: Session, facility_id: int):
    return db.query(ServiceFacility).filter(ServiceFacility.id == facility_id).first()


def get_service_facility_by_name(db: Session, name: str):
    return (
        db.query(ServiceFacility)
        .filter(func.lower(ServiceFacility.name) == func.lower(name.strip()))
        .first()
    )


def get_service_facilities_by_ids(db: Session, facility_ids: list[int]):
    if not facility_ids:
        return []
    return db.query(ServiceFacility).filter(ServiceFacility.id.in_(facility_ids)).all()


def create_service_facility(db: Session, facility_data: dict):
    facility = ServiceFacility(**facility_data)
    db.add(facility)
    db.commit()
    db.refresh(facility)
    return facility


def update_service_facility(db: Session, facility: ServiceFacility, update_data: dict):
    for key, value in update_data.items():
        setattr(facility, key, value)
    db.commit()
    db.refresh(facility)
    return facility


def delete_service_facility(db: Session, facility: ServiceFacility):
    db.delete(facility)
    db.commit()
