from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from repositories import category_repository
from schemas.category import CategoryCreate, CategoryUpdate


def get_all_categories(db: Session):
    return category_repository.get_all_categories(db)


def get_category(db: Session, category_id: int):
    category = category_repository.get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


def create_category(db: Session, payload: CategoryCreate):
    existing = category_repository.get_category_by_name(db, payload.name)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )

    return category_repository.create_category(db, payload.model_dump())


def update_category(db: Session, category_id: int, payload: CategoryUpdate):
    category = category_repository.get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # If name is being changed, check it's not taken by another category
    if payload.name and payload.name != category.name:
        existing = category_repository.get_category_by_name(db, payload.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )

    update_data = payload.model_dump(exclude_unset=True)

    return category_repository.update_category(db, category, update_data)


def delete_category(db: Session, category_id: int):
    category = category_repository.get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    category_repository.delete_category(db, category)
