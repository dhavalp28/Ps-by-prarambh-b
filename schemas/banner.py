from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class BannerCreate(BaseModel):
    title: str
    subtitle: Optional[str] = None
    image_url: str
    redirect_url: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = 0


class BannerUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    image_url: Optional[str] = None
    redirect_url: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class BannerResponse(BaseModel):
    id: int
    title: str
    subtitle: Optional[str]
    image_url: str
    redirect_url: Optional[str]
    description: Optional[str]
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
