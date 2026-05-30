from db.models.brand import Brand
from db.models.business import Business
from db.models.city import City
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload


def get_all_brands(db: Session):
    return (
        db.query(Brand)
        .options(joinedload(Brand.businesses))
        .order_by(Brand.created_at.desc())
        .all()
    )


def get_brand_by_id(db: Session, brand_id: int):
    return (
        db.query(Brand)
        .options(
            joinedload(Brand.businesses)
            .joinedload(Business.city)
            .joinedload(City.state)
        )
        .filter(Brand.id == brand_id)
        .first()
    )


def get_brand_by_name(db: Session, name: str):
    return (
        db.query(Brand)
        .options(joinedload(Brand.businesses))
        .filter(func.lower(Brand.name) == func.lower(name))
        .first()
    )


def create_brand(db: Session, brand_data: dict):
    brand = Brand(**brand_data)
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand


def update_brand(db: Session, brand: Brand, update_data: dict):
    for key, value in update_data.items():
        setattr(brand, key, value)

    db.commit()
    db.refresh(brand)
    return brand


def delete_brand(db: Session, brand: Brand):
    db.delete(brand)
    db.commit()
