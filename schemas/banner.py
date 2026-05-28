from pydantic import BaseModel, HttpUrl, ConfigDict
from typing import Optional
from datetime import datetime

from schemas.city import CityResponse


class BannerCreate(BaseModel):
    title: str
    subtitle: Optional[str] = None
    image_url: str
    redirect_url: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = 0
    city_id: Optional[int] = None


class BannerUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    image_url: Optional[str] = None
    redirect_url: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    city_id: Optional[int] = None


class BannerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    subtitle: Optional[str]
    image_url: str
    redirect_url: Optional[str]
    description: Optional[str]
    sort_order: int
    city: Optional[CityResponse]
    is_active: bool
    created_at: datetime
    updated_at: datetime
