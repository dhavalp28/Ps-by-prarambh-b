from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

from schemas.category import CategoryResponse
from schemas.city import CityResponse


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
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str]
    icon: Optional[str]
    category: CategoryResponse
    city: Optional[CityResponse]
    is_active: bool
    created_at: datetime
    updated_at: datetime
