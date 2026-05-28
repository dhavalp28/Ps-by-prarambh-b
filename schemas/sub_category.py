from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from schemas.category import CategoryResponse


class SubCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    category_id: int
    city_id: Optional[int] = None


class SubCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    category_id: Optional[int] = None
    city_id: Optional[int] = None
    is_active: Optional[bool] = None


class SubCategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    icon: Optional[str]
    category_id: int
    category: CategoryResponse
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
