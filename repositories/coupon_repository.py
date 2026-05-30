from typing import Optional

from db.models.coupon import Coupon
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload


def get_all_coupons(
    db: Session,
    business_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
):
    query = db.query(Coupon).options(joinedload(Coupon.business))

    if business_id is not None:
        query = query.filter(Coupon.business_id == business_id)

    if is_active is not None:
        query = query.filter(Coupon.is_active == is_active)

    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            (Coupon.coupon_name.ilike(term)) | (Coupon.description.ilike(term))
        )

    return query.order_by(Coupon.created_at.desc()).all()


def get_coupon_by_id(db: Session, coupon_id: int):
    return (
        db.query(Coupon)
        .options(joinedload(Coupon.business))
        .filter(Coupon.id == coupon_id)
        .first()
    )


def get_coupon_by_business_and_name(db: Session, business_id: int, coupon_name: str):
    return (
        db.query(Coupon)
        .filter(
            Coupon.business_id == business_id,
            func.lower(Coupon.coupon_name) == func.lower(coupon_name),
        )
        .first()
    )


def create_coupon(db: Session, coupon_data: dict):
    coupon = Coupon(**coupon_data)
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


def update_coupon(db: Session, coupon: Coupon, update_data: dict):
    for key, value in update_data.items():
        setattr(coupon, key, value)
    db.commit()
    db.refresh(coupon)
    return coupon


def delete_coupon(db: Session, coupon: Coupon):
    db.delete(coupon)
    db.commit()
