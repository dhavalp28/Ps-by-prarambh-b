from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from typing import Optional

from repositories import category_repository
from schemas.category import CategoryCreate, CategoryUpdate
from utils.upload import save_upload, delete_upload


def get_all_categories(db: Session, city_id: Optional[int] = None):
    return category_repository.get_all_categories(db, city_id)


def get_category(db: Session, category_id: int):
    category = category_repository.get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


async def create_category(
    db: Session,
    name: str,
    description: Optional[str] = None,
    city_id: Optional[int] = None,
    is_active: bool = True,
    icon: Optional[UploadFile] = None,
):
    existing = category_repository.get_category_by_name(db, name)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )

    icon_url = None
    if icon and icon.filename:
        icon_url = await save_upload(icon, folder="categories")

    category_data = {
        "name": name,
        "description": description or None,
        "city_id": city_id,
        "is_active": is_active,
        "icon": icon_url,
    }

    return category_repository.create_category(db, category_data)


async def update_category(
    db: Session,
    category_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    city_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    icon: Optional[UploadFile] = None,
):
    category = category_repository.get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    update_data = {}

    if name is not None:
        if name != category.name:
            existing = category_repository.get_category_by_name(db, name)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category with this name already exists"
                )
        update_data["name"] = name

    if description is not None:
        update_data["description"] = description or None

    if city_id is not None:
        update_data["city_id"] = city_id

    if is_active is not None:
        update_data["is_active"] = is_active

    # If a new icon was uploaded, save it and delete the old one
    if icon and icon.filename:
        old_url = category.icon
        update_data["icon"] = await save_upload(icon, folder="categories")
        if old_url:
            delete_upload(old_url)

    return category_repository.update_category(db, category, update_data)


def delete_category(db: Session, category_id: int):
    category = category_repository.get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Delete the icon file from disk if it exists
    if category.icon:
        delete_upload(category.icon)

    category_repository.delete_category(db, category)
    return category
