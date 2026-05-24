from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from routers.deps import get_db
from schemas.sub_category import SubCategoryCreate, SubCategoryUpdate, SubCategoryResponse
from services import sub_category_service

router = APIRouter()


@router.get("/", response_model=List[SubCategoryResponse])
def list_sub_categories(db: Session = Depends(get_db)):
    return sub_category_service.get_all_sub_categories(db)


@router.get("/by-category/{category_id}", response_model=List[SubCategoryResponse])
def list_sub_categories_by_category(category_id: int, db: Session = Depends(get_db)):
    return sub_category_service.get_sub_categories_by_category(db, category_id)


@router.get("/{sub_category_id}", response_model=SubCategoryResponse)
def get_sub_category(sub_category_id: int, db: Session = Depends(get_db)):
    return sub_category_service.get_sub_category(db, sub_category_id)


@router.post("/", response_model=SubCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_sub_category(payload: SubCategoryCreate, db: Session = Depends(get_db)):
    return sub_category_service.create_sub_category(db, payload)


@router.put("/{sub_category_id}", response_model=SubCategoryResponse)
def update_sub_category(sub_category_id: int, payload: SubCategoryUpdate, db: Session = Depends(get_db)):
    return sub_category_service.update_sub_category(db, sub_category_id, payload)


@router.delete("/{sub_category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sub_category(sub_category_id: int, db: Session = Depends(get_db)):
    sub_category_service.delete_sub_category(db, sub_category_id)
