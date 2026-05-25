from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from routers.deps import get_db
from schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from services import category_service
from utils.response import (
    success_list, success_create, success_update, success_delete,
    error_not_found, error_duplicate, error_server
)

router = APIRouter()


@router.get("/")
def list_categories(db: Session = Depends(get_db)):
    try:
        categories = category_service.get_all_categories(db)
        return success_list(title="Categories List", data=categories)
    except Exception as e:
        return error_server(title="Categories List", error=str(e))


@router.get("/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db)):
    try:
        category = category_service.get_category(db, category_id)
        if not category:
            return error_not_found(title="Get Category", resource="Category")
        return success_list(title="Category Details", data=category)
    except Exception as e:
        return error_server(title="Get Category", error=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    try:
        category = category_service.create_category(db, payload)
        return success_create(title="Category Created", data=category)
    except ValueError as e:
        return error_duplicate(title="Create Category", resource="Category")
    except Exception as e:
        return error_server(title="Create Category", error=str(e))


@router.put("/{category_id}")
def update_category(category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)):
    try:
        category = category_service.update_category(db, category_id, payload)
        if not category:
            return error_not_found(title="Update Category", resource="Category")
        return success_update(title="Category Updated", data=category)
    except Exception as e:
        return error_server(title="Update Category", error=str(e))


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    try:
        category = category_service.delete_category(db, category_id)
        if not category:
            return error_not_found(title="Delete Category", resource="Category")
        return success_delete(title="Category Deleted")
    except Exception as e:
        return error_server(title="Delete Category", error=str(e))
