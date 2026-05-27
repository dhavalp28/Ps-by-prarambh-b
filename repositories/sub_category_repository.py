from sqlalchemy.orm import Session
from typing import Optional

from db.models.sub_category import SubCategory


def get_all_sub_categories(db: Session, city_id: Optional[int] = None):
    query = db.query(SubCategory)
    if city_id:
        query = query.filter(SubCategory.city_id == city_id)
    return query.all()


def get_sub_categories_by_category(db: Session, category_id: int, city_id: Optional[int] = None):
    query = db.query(SubCategory).filter(SubCategory.category_id == category_id)
    if city_id:
        query = query.filter(SubCategory.city_id == city_id)
    return query.all()


def get_sub_category_by_id(db: Session, sub_category_id: int):
    return db.query(SubCategory).filter(SubCategory.id == sub_category_id).first()


def get_sub_category_by_name_and_category(db: Session, name: str, category_id: int):
    return (
        db.query(SubCategory)
        .filter(SubCategory.name == name, SubCategory.category_id == category_id)
        .first()
    )


def create_sub_category(db: Session, sub_category_data: dict):
    sub_category = SubCategory(**sub_category_data)

    db.add(sub_category)
    db.commit()
    db.refresh(sub_category)

    return sub_category


def update_sub_category(db: Session, sub_category: SubCategory, update_data: dict):
    for key, value in update_data.items():
        setattr(sub_category, key, value)

    db.commit()
    db.refresh(sub_category)

    return sub_category


def delete_sub_category(db: Session, sub_category: SubCategory):
    db.delete(sub_category)
    db.commit()
