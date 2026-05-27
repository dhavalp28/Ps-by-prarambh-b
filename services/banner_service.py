from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile, status

from repositories import banner_repository
from utils.upload import save_upload, delete_upload


def get_all_banners(db: Session, city_id: Optional[int] = None):
    return banner_repository.get_all_banners(db, city_id)


def get_banner(db: Session, banner_id: int):
    banner = banner_repository.get_banner_by_id(db, banner_id)

    if not banner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Banner not found"
        )

    return banner


async def create_banner(
    db: Session,
    title: str,
    image: UploadFile,
    subtitle: Optional[str] = None,
    redirect_url: Optional[str] = None,
    description: Optional[str] = None,
    sort_order: int = 0,
    city_id: Optional[int] = None,
):
    existing = banner_repository.get_banner_by_title(db, title)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Banner with this title already exists"
        )

    image_url = await save_upload(image, folder="banners")

    banner_data = {
        "title": title,
        "subtitle": subtitle or None,
        "image_url": image_url,
        "redirect_url": redirect_url or None,
        "description": description or None,
        "sort_order": sort_order,
        "city_id": city_id,
    }

    return banner_repository.create_banner(db, banner_data)


async def update_banner(
    db: Session,
    banner_id: int,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    redirect_url: Optional[str] = None,
    description: Optional[str] = None,
    sort_order: Optional[int] = None,
    is_active: Optional[bool] = None,
    city_id: Optional[int] = None,
    image: Optional[UploadFile] = None,
):
    banner = banner_repository.get_banner_by_id(db, banner_id)

    if not banner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Banner not found"
        )

    update_data = {}

    if title is not None:
        if title != banner.title:
            existing = banner_repository.get_banner_by_title(db, title)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Banner with this title already exists"
                )
        update_data["title"] = title

    if subtitle is not None:
        update_data["subtitle"] = subtitle or None

    if redirect_url is not None:
        update_data["redirect_url"] = redirect_url or None

    if description is not None:
        update_data["description"] = description or None

    if sort_order is not None:
        update_data["sort_order"] = sort_order

    if is_active is not None:
        update_data["is_active"] = is_active

    if city_id is not None:
        update_data["city_id"] = city_id

    # If a new image was uploaded, save it and delete the old one
    if image and image.filename:
        old_url = banner.image_url
        update_data["image_url"] = await save_upload(image, folder="banners")
        delete_upload(old_url)

    return banner_repository.update_banner(db, banner, update_data)


def delete_banner(db: Session, banner_id: int):
    banner = banner_repository.get_banner_by_id(db, banner_id)

    if not banner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Banner not found"
        )

    # Delete the image file from disk
    delete_upload(banner.image_url)

    banner_repository.delete_banner(db, banner)
    return banner
