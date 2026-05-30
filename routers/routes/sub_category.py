from fastapi import APIRouter, Depends, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from routers.deps import get_db, get_admin_user
from schemas.sub_category import SubCategoryCreate, SubCategoryUpdate, SubCategoryResponse
from services import sub_category_service
from utils.response import (
    success_list, success_create, success_update, success_delete,
    error_not_found, error_duplicate, error_server
)

router = APIRouter()


@router.get("/")
def list_sub_categories(city_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """List all sub-categories (Public endpoint)"""
    try:
        sub_categories = sub_category_service.get_all_sub_categories(db, city_id)
        return success_list(title="Sub Categories List", data=[SubCategoryResponse.model_validate(sc) for sc in sub_categories])
    except Exception as e:
        return error_server(title="Sub Categories List", error=str(e))


@router.get("/by-category/{category_id}")
def list_sub_categories_by_category(category_id: int, city_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """List sub-categories by category (Public endpoint)"""
    try:
        sub_categories = sub_category_service.get_sub_categories_by_category(db, category_id, city_id)
        return success_list(title="Sub Categories by Category", data=[SubCategoryResponse.model_validate(sc) for sc in sub_categories])
    except Exception as e:
        return error_server(title="Sub Categories by Category", error=str(e))


@router.get("/{sub_category_id}")
def get_sub_category(sub_category_id: int, db: Session = Depends(get_db)):
    """Get specific sub-category (Public endpoint)"""
    try:
        sub_category = sub_category_service.get_sub_category(db, sub_category_id)
        if not sub_category:
            return error_not_found(title="Get Sub Category", resource="Sub Category")
        return success_list(title="Sub Category Details", data=SubCategoryResponse.model_validate(sub_category))
    except Exception as e:
        return error_server(title="Get Sub Category", error=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_user)])
async def create_sub_category(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    category_id: int = Form(...),
    city_id: Optional[int] = Form(None),
    is_active: bool = Form(True),
    icon: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """Create sub-category (Admin only)"""
    try:
        sub_category = await sub_category_service.create_sub_category(
            db=db,
            name=name,
            description=description,
            category_id=category_id,
            city_id=city_id,
            is_active=is_active,
            icon=icon,
        )
        return success_create(title="Sub Category Created", data=SubCategoryResponse.model_validate(sub_category))
    except ValueError as e:
        return error_duplicate(title="Create Sub Category", resource="Sub Category")
    except Exception as e:
        return error_server(title="Create Sub Category", error=str(e))


@router.put("/{sub_category_id}", dependencies=[Depends(get_admin_user)])
async def update_sub_category(
    sub_category_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    city_id: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(None),
    icon: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """Update sub-category (Admin only)"""
    try:
        sub_category = await sub_category_service.update_sub_category(
            db=db,
            sub_category_id=sub_category_id,
            name=name,
            description=description,
            category_id=category_id,
            city_id=city_id,
            is_active=is_active,
            icon=icon,
        )
        if not sub_category:
            return error_not_found(title="Update Sub Category", resource="Sub Category")
        return success_update(title="Sub Category Updated", data=SubCategoryResponse.model_validate(sub_category))
    except Exception as e:
        return error_server(title="Update Sub Category", error=str(e))


@router.delete("/{sub_category_id}", dependencies=[Depends(get_admin_user)])
def delete_sub_category(sub_category_id: int, db: Session = Depends(get_db)):
    """Delete sub-category (Admin only)"""
    try:
        sub_category = sub_category_service.delete_sub_category(db, sub_category_id)
        if not sub_category:
            return error_not_found(title="Delete Sub Category", resource="Sub Category")
        return success_delete(title="Sub Category Deleted", resource_id=sub_category.id)
    except Exception as e:
        return error_server(title="Delete Sub Category", error=str(e))
