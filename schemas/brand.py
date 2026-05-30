from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from schemas.city import CityResponse


class BrandCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True
    business_ids: list[int] = Field(default_factory=list)


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    business_ids: Optional[list[int]] = None


class BrandResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    is_active: bool
    businesses_count: int
    created_at: datetime
    updated_at: datetime


class BranchBusinessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_name: str
    title: Optional[str]
    business_phone: str
    vendor_email: Optional[str]
    website: Optional[str]
    logo_url: Optional[str]
    cover_image_url: Optional[str]
    business_address: str
    map_link_url: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    city: CityResponse
    open_time: Optional[str]
    close_time: Optional[str]
    open_days: Optional[str]
    is_active: bool


class BrandDetailResponse(BrandResponse):
    businesses: list[BranchBusinessResponse] = Field(default_factory=list)


class BrandSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
