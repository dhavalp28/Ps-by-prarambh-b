from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from typing import Optional

from repositories import sub_category_repository, category_repository
from schemas.sub_category import SubCategoryCreate, SubCategoryUpdate
from utils.upload import save_upload, delete_upload


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


async def create_sub_category(
    db: Session,
    name: str,
    category_id: int,
    description: Optional[str] = None,
    city_id: Optional[int] = None,
    is_active: bool = True,
    icon: Optional[UploadFile] = None,
):
    # Ensure the parent category exists
    category = category_repository.get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Name must be unique within the same category
    existing = sub_category_repository.get_sub_category_by_name_and_category(
        db, name, category_id
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sub-category with this name already exists in the given category"
        )

    icon_url = None
    if icon and icon.filename:
        icon_url = await save_upload(icon, folder="sub_categories")

    sub_category_data = {
        "name": name,
        "description": description or None,
        "category_id": category_id,
        "city_id": city_id,
        "is_active": is_active,
        "icon": icon_url,
    }

    return sub_category_repository.create_sub_category(db, sub_category_data)


async def update_sub_category(
    db: Session,
    sub_category_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    category_id: Optional[int] = None,
    city_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    icon: Optional[UploadFile] = None,
):
    sub_category = sub_category_repository.get_sub_category_by_id(db, sub_category_id)

    if not sub_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sub-category not found"
        )

    update_data = {}

    if name is not None:
        update_data["name"] = name

    if description is not None:
        update_data["description"] = description or None

    if category_id is not None:
        # Validate the new category exists
        category = category_repository.get_category_by_id(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        update_data["category_id"] = category_id

    if city_id is not None:
        update_data["city_id"] = city_id

    if is_active is not None:
        update_data["is_active"] = is_active

    # Check uniqueness if name or category changed
    if name is not None or category_id is not None:
        new_name = name if name is not None else sub_category.name
        new_category_id = category_id if category_id is not None else sub_category.category_id
        
        if new_name != sub_category.name or new_category_id != sub_category.category_id:
            existing = sub_category_repository.get_sub_category_by_name_and_category(
                db, new_name, new_category_id
            )
            if existing and existing.id != sub_category_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Sub-category with this name already exists in the given category"
                )

    # If a new icon was uploaded, save it and delete the old one
    if icon and icon.filename:
        old_url = sub_category.icon
        update_data["icon"] = await save_upload(icon, folder="sub_categories")
        if old_url:
            delete_upload(old_url)

    return sub_category_repository.update_sub_category(db, sub_category, update_data)


def delete_sub_category(db: Session, sub_category_id: int):
    sub_category = sub_category_repository.get_sub_category_by_id(db, sub_category_id)

    if not sub_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sub-category not found"
        )

    # Delete the icon file from disk if it exists
    if sub_category.icon:
        delete_upload(sub_category.icon)

    sub_category_repository.delete_sub_category(db, sub_category)
    return sub_category
