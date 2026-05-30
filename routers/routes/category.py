from fastapi import APIRouter, Depends, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from routers.deps import get_db, get_admin_user
from schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from services import category_service
from utils.response import (
    success_list, success_create, success_update, success_delete,
    error_not_found, error_duplicate, error_server
)

router = APIRouter()


@router.get("/")
def list_categories(city_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """List all categories (Public endpoint)"""
    try:
        categories = category_service.get_all_categories(db, city_id)
        return success_list(title="Categories List", data=[CategoryResponse.model_validate(c) for c in categories])
    except Exception as e:
        return error_server(title="Categories List", error=str(e))


@router.get("/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get specific category (Public endpoint)"""
    try:
        category = category_service.get_category(db, category_id)
        if not category:
            return error_not_found(title="Get Category", resource="Category")
        return success_list(title="Category Details", data=CategoryResponse.model_validate(category))
    except Exception as e:
        return error_server(title="Get Category", error=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_user)])
async def create_category(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    city_id: Optional[int] = Form(None),
    is_active: bool = Form(True),
    icon: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """Create category (Admin only)"""
    try:
        category = await category_service.create_category(
            db=db,
            name=name,
            description=description,
            city_id=city_id,
            is_active=is_active,
            icon=icon,
        )
        return success_create(title="Category Created", data=CategoryResponse.model_validate(category))
    except ValueError as e:
        return error_duplicate(title="Create Category", resource="Category")
    except Exception as e:
        return error_server(title="Create Category", error=str(e))


@router.put("/{category_id}", dependencies=[Depends(get_admin_user)])
async def update_category(
    category_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    city_id: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(None),
    icon: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """Update category (Admin only)"""
    try:
        category = await category_service.update_category(
            db=db,
            category_id=category_id,
            name=name,
            description=description,
            city_id=city_id,
            is_active=is_active,
            icon=icon,
        )
        if not category:
            return error_not_found(title="Update Category", resource="Category")
        return success_update(title="Category Updated", data=CategoryResponse.model_validate(category))
    except Exception as e:
        return error_server(title="Update Category", error=str(e))


@router.delete("/{category_id}", dependencies=[Depends(get_admin_user)])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete category (Admin only)"""
    try:
        category = category_service.delete_category(db, category_id)
        if not category:
            return error_not_found(title="Delete Category", resource="Category")
        return success_delete(title="Category Deleted", resource_id=category.id)
    except Exception as e:
        return error_server(title="Delete Category", error=str(e))
