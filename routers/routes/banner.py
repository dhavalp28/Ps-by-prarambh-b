from fastapi import APIRouter, Depends, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from routers.deps import get_db, get_admin_user
from schemas.banner import BannerResponse
from services import banner_service
from utils.response import (
    success_list, success_create, success_update, success_delete,
    error_not_found, error_server
)

router = APIRouter()


@router.get("/")
def list_banners(city_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """Public endpoint - List all banners"""
    try:
        banners = banner_service.get_all_banners(db, city_id)
        return success_list(title="Banners List", data=[BannerResponse.model_validate(b) for b in banners])
    except Exception as e:
        return error_server(title="Banners List", error=str(e))


@router.get("/{banner_id}")
def get_banner(banner_id: int, db: Session = Depends(get_db)):
    """Public endpoint - Get banner details"""
    try:
        banner = banner_service.get_banner(db, banner_id)
        if not banner:
            return error_not_found(title="Get Banner", resource="Banner")
        return success_list(title="Banner Details", data=BannerResponse.model_validate(banner))
    except Exception as e:
        return error_server(title="Get Banner", error=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_user)])
async def create_banner(
    title: str = Form(...),
    subtitle: Optional[str] = Form(None),
    redirect_url: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    sort_order: int = Form(0),
    city_id: Optional[int] = Form(None),
    is_active: bool = Form(True),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Admin only - Create a new banner"""
    try:
        banner = await banner_service.create_banner(
            db=db,
            title=title,
            subtitle=subtitle,
            redirect_url=redirect_url,
            description=description,
            sort_order=sort_order,
            city_id=city_id,
            is_active=is_active,
            image=image,
        )
        return success_create(title="Banner Created", data=BannerResponse.model_validate(banner))
    except Exception as e:
        return error_server(title="Create Banner", error=str(e))


@router.put("/{banner_id}", dependencies=[Depends(get_admin_user)])
async def update_banner(
    banner_id: int,
    title: Optional[str] = Form(None),
    subtitle: Optional[str] = Form(None),
    redirect_url: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    sort_order: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(None),
    city_id: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """Admin only - Update an existing banner"""
    try:
        banner = await banner_service.update_banner(
            db=db,
            banner_id=banner_id,
            title=title,
            subtitle=subtitle,
            redirect_url=redirect_url,
            description=description,
            sort_order=sort_order,
            is_active=is_active,
            city_id=city_id,
            image=image,
        )
        if not banner:
            return error_not_found(title="Update Banner", resource="Banner")
        return success_update(title="Banner Updated", data=BannerResponse.model_validate(banner))
    except Exception as e:
        return error_server(title="Update Banner", error=str(e))


@router.delete("/{banner_id}", dependencies=[Depends(get_admin_user)])
def delete_banner(banner_id: int, db: Session = Depends(get_db)):
    """Admin only - Delete a banner"""
    try:
        banner = banner_service.delete_banner(db, banner_id)
        if not banner:
            return error_not_found(title="Delete Banner", resource="Banner")
        return success_delete(title="Banner Deleted", resource_id=banner.id)
    except Exception as e:
        return error_server(title="Delete Banner", error=str(e))
