from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from routers.deps import get_db
from schemas.sub_category import SubCategoryCreate, SubCategoryUpdate, SubCategoryResponse
from services import sub_category_service
from utils.response import (
    success_list, success_create, success_update, success_delete,
    error_not_found, error_duplicate, error_server
)

router = APIRouter()


@router.get("/")
def list_sub_categories(db: Session = Depends(get_db)):
    try:
        sub_categories = sub_category_service.get_all_sub_categories(db)
        return success_list(title="Sub Categories List", data=sub_categories)
    except Exception as e:
        return error_server(title="Sub Categories List", error=str(e))


@router.get("/by-category/{category_id}")
def list_sub_categories_by_category(category_id: int, db: Session = Depends(get_db)):
    try:
        sub_categories = sub_category_service.get_sub_categories_by_category(db, category_id)
        return success_list(title="Sub Categories by Category", data=sub_categories)
    except Exception as e:
        return error_server(title="Sub Categories by Category", error=str(e))


@router.get("/{sub_category_id}")
def get_sub_category(sub_category_id: int, db: Session = Depends(get_db)):
    try:
        sub_category = sub_category_service.get_sub_category(db, sub_category_id)
        if not sub_category:
            return error_not_found(title="Get Sub Category", resource="Sub Category")
        return success_list(title="Sub Category Details", data=sub_category)
    except Exception as e:
        return error_server(title="Get Sub Category", error=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_sub_category(payload: SubCategoryCreate, db: Session = Depends(get_db)):
    try:
        sub_category = sub_category_service.create_sub_category(db, payload)
        return success_create(title="Sub Category Created", data=sub_category)
    except ValueError as e:
        return error_duplicate(title="Create Sub Category", resource="Sub Category")
    except Exception as e:
        return error_server(title="Create Sub Category", error=str(e))


@router.put("/{sub_category_id}")
def update_sub_category(sub_category_id: int, payload: SubCategoryUpdate, db: Session = Depends(get_db)):
    try:
        sub_category = sub_category_service.update_sub_category(db, sub_category_id, payload)
        if not sub_category:
            return error_not_found(title="Update Sub Category", resource="Sub Category")
        return success_update(title="Sub Category Updated", data=sub_category)
    except Exception as e:
        return error_server(title="Update Sub Category", error=str(e))


@router.delete("/{sub_category_id}")
def delete_sub_category(sub_category_id: int, db: Session = Depends(get_db)):
    try:
        sub_category = sub_category_service.delete_sub_category(db, sub_category_id)
        if not sub_category:
            return error_not_found(title="Delete Sub Category", resource="Sub Category")
        return success_delete(title="Sub Category Deleted")
    except Exception as e:
        return error_server(title="Delete Sub Category", error=str(e))
