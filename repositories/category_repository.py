from sqlalchemy.orm import Session

from db.models.category import Category


def get_all_categories(db: Session):
    return db.query(Category).all()


def get_category_by_id(db: Session, category_id: int):
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_name(db: Session, name: str):
    return db.query(Category).filter(Category.name == name).first()


def create_category(db: Session, category_data: dict):
    category = Category(**category_data)

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def update_category(db: Session, category: Category, update_data: dict):
    for key, value in update_data.items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)

    return category


def delete_category(db: Session, category: Category):
    db.delete(category)
    db.commit()
