from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile, status
from routers.deps import get_admin_user, get_db
from schemas.banner import BannerResponse
from services import banner_service
from services.audit_log_service import log_admin_action
from sqlalchemy.orm import Session
from utils.response import (
    error_not_found,
    error_server,
    success_create,
    success_delete,
    success_list,
    success_update,
)

router = APIRouter()


@router.get("/")
def list_banners(city_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """Public endpoint - List all banners"""
    try:
        banners = banner_service.get_all_banners(db, city_id)
        return success_list(
            title="Banners List",
            data=[BannerResponse.model_validate(b) for b in banners],
        )
    except Exception as e:
        return error_server(title="Banners List", error=str(e))


@router.get("/{banner_id}")
def get_banner(banner_id: int, db: Session = Depends(get_db)):
    """Public endpoint - Get banner details"""
    try:
        banner = banner_service.get_banner(db, banner_id)
        if not banner:
            return error_not_found(title="Get Banner", resource="Banner")
        return success_list(
            title="Banner Details", data=BannerResponse.model_validate(banner)
        )
    except Exception as e:
        return error_server(title="Get Banner", error=str(e))


@router.post(
    "/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_user)]
)
async def create_banner(
    title: str = Form(...),
    subtitle: Optional[str] = Form(None),
    redirect_url: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    sort_order: int = Form(0),
    city_id: Optional[int] = Form(None),
    is_active: bool = Form(True),
    image: UploadFile = File(...),
    request: Request = None,
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
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
            image=image,
        )
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="create",
            resource_type="banner",
            resource_id=banner.id,
            method=request.method if request else None,
            path=str(request.url.path) if request else None,
            details={"title": banner.title},
        )
        return success_create(
            title="Banner Created", data=BannerResponse.model_validate(banner)
        )
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
    request: Request = None,
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
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
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="update",
            resource_type="banner",
            resource_id=banner.id,
            method=request.method if request else None,
            path=str(request.url.path) if request else None,
            details={"title": banner.title},
        )
        return success_update(
            title="Banner Updated", data=BannerResponse.model_validate(banner)
        )
    except Exception as e:
        return error_server(title="Update Banner", error=str(e))


@router.delete("/{banner_id}", dependencies=[Depends(get_admin_user)])
def delete_banner(
    banner_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
):
    """Admin only - Delete a banner"""
    try:
        banner = banner_service.delete_banner(db, banner_id)
        if not banner:
            return error_not_found(title="Delete Banner", resource="Banner")
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="delete",
            resource_type="banner",
            resource_id=banner.id,
            method=request.method,
            path=str(request.url.path),
            details={"title": banner.title},
        )
        return success_delete(title="Banner Deleted", resource_id=banner.id)
    except Exception as e:
        return error_server(title="Delete Banner", error=str(e))
