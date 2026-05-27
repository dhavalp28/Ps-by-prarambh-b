from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional

from repositories import sub_category_repository, category_repository
from schemas.sub_category import SubCategoryCreate, SubCategoryUpdate


def get_all_sub_categories(db: Session, city_id: Optional[int] = None):
    return sub_category_repository.get_all_sub_categories(db, city_id)


def get_sub_categories_by_category(db: Session, category_id: int, city_id: Optional[int] = None):
    # Ensure the parent category exists
    category = category_repository.get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return sub_category_repository.get_sub_categories_by_category(db, category_id, city_id)


def get_sub_category(db: Session, sub_category_id: int):
    sub_category = sub_category_repository.get_sub_category_by_id(db, sub_category_id)

    if not sub_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sub-category not found"
        )

    return sub_category


def create_sub_category(db: Session, payload: SubCategoryCreate):
    # Ensure the parent category exists
    category = category_repository.get_category_by_id(db, payload.category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Name must be unique within the same category
    existing = sub_category_repository.get_sub_category_by_name_and_category(
        db, payload.name, payload.category_id
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sub-category with this name already exists in the given category"
        )

    return sub_category_repository.create_sub_category(db, payload.model_dump())


def update_sub_category(db: Session, sub_category_id: int, payload: SubCategoryUpdate):
    sub_category = sub_category_repository.get_sub_category_by_id(db, sub_category_id)

    if not sub_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sub-category not found"
        )

    update_data = payload.model_dump(exclude_unset=True)

    # If category_id is being changed, validate the new category exists
    new_category_id = update_data.get("category_id", sub_category.category_id)

    if "category_id" in update_data:
        category = category_repository.get_category_by_id(db, new_category_id)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

    # If name is being changed, check uniqueness within the target category
    new_name = update_data.get("name", sub_category.name)

    if "name" in update_data or "category_id" in update_data:
        if new_name != sub_category.name or new_category_id != sub_category.category_id:
            existing = sub_category_repository.get_sub_category_by_name_and_category(
                db, new_name, new_category_id
            )

            if existing and existing.id != sub_category_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Sub-category with this name already exists in the given category"
                )

    return sub_category_repository.update_sub_category(db, sub_category, update_data)


def delete_sub_category(db: Session, sub_category_id: int):
    sub_category = sub_category_repository.get_sub_category_by_id(db, sub_category_id)

    if not sub_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sub-category not found"
        )

    sub_category_repository.delete_sub_category(db, sub_category)
    return sub_category
