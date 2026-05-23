from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from schemas.state import StateResponse
from schemas.city import CityResponse
from schemas.category import CategoryResponse
from schemas.sub_category import SubCategoryResponse


# ── Nested owner summary ───────────────────────────────────────────────────────
class OwnerSummary(BaseModel):
    id: int
    name: str
    email: str
    phone: str

    class Config:
        from_attributes = True


# ── Create ─────────────────────────────────────────────────────────────────────
class BusinessCreate(BaseModel):
    # Basic Info
    business_name:   str
    title:           Optional[str] = None
    business_phone:  str
    vendor_email:    Optional[str] = None
    website:         Optional[str] = None
    logo_url:        Optional[str] = None
    cover_image_url: Optional[str] = None
    owner_id:        Optional[int] = None

    # Location
    business_address: str
    map_link_url:     Optional[str] = None
    latitude:         Optional[float] = None
    longitude:        Optional[float] = None
    business_type:    Optional[str] = None
    state_id:         int
    city_id:          int
    category_id:      int
    sub_category_id:  Optional[int] = None

    # Hours & Details
    open_time:    Optional[str] = None
    close_time:   Optional[str] = None
    cuisine:      Optional[str] = None
    open_days:    Optional[str] = None

    about_us:     Optional[str] = None
    description:  Optional[str] = None

    facebook_url:  Optional[str] = None
    twitter_url:   Optional[str] = None
    instagram_url: Optional[str] = None

    # Media & Lists
    payment_methods: Optional[str] = None
    highlights:      Optional[str] = None
    amenities:       Optional[str] = None
    other_phones:    Optional[str] = None
    terms_of_use:    Optional[str] = None
    guidelines:      Optional[str] = None
    interior_photos: Optional[str] = None


# ── Update ─────────────────────────────────────────────────────────────────────
class BusinessUpdate(BaseModel):
    business_name:   Optional[str] = None
    title:           Optional[str] = None
    business_phone:  Optional[str] = None
    vendor_email:    Optional[str] = None
    website:         Optional[str] = None
    logo_url:        Optional[str] = None
    cover_image_url: Optional[str] = None
    owner_id:        Optional[int] = None

    business_address: Optional[str] = None
    map_link_url:     Optional[str] = None
    latitude:         Optional[float] = None
    longitude:        Optional[float] = None
    business_type:    Optional[str] = None
    state_id:         Optional[int] = None
    city_id:          Optional[int] = None
    category_id:      Optional[int] = None
    sub_category_id:  Optional[int] = None

    open_time:    Optional[str] = None
    close_time:   Optional[str] = None
    cuisine:      Optional[str] = None
    open_days:    Optional[str] = None

    about_us:     Optional[str] = None
    description:  Optional[str] = None

    facebook_url:  Optional[str] = None
    twitter_url:   Optional[str] = None
    instagram_url: Optional[str] = None

    payment_methods: Optional[str] = None
    highlights:      Optional[str] = None
    amenities:       Optional[str] = None
    other_phones:    Optional[str] = None
    terms_of_use:    Optional[str] = None
    guidelines:      Optional[str] = None
    interior_photos: Optional[str] = None

    is_active: Optional[bool] = None


# ── Response ───────────────────────────────────────────────────────────────────
class BusinessResponse(BaseModel):
    id: int

    business_name:   str
    title:           Optional[str]
    business_phone:  str
    vendor_email:    Optional[str]
    website:         Optional[str]
    logo_url:        Optional[str]
    cover_image_url: Optional[str]
    owner_id:        Optional[int]
    owner:           Optional[OwnerSummary]

    business_address: str
    map_link_url:     Optional[str]
    latitude:         Optional[float]
    longitude:        Optional[float]
    business_type:    Optional[str]

    state_id:        int
    state:           StateResponse
    city_id:         int
    city:            CityResponse
    category_id:     int
    category:        CategoryResponse
    sub_category_id: Optional[int]
    sub_category:    Optional[SubCategoryResponse]

    open_time:  Optional[str]
    close_time: Optional[str]
    cuisine:    Optional[str]
    open_days:  Optional[str]

    about_us:    Optional[str]
    description: Optional[str]

    facebook_url:  Optional[str]
    twitter_url:   Optional[str]
    instagram_url: Optional[str]

    payment_methods: Optional[str]
    highlights:      Optional[str]
    amenities:       Optional[str]
    other_phones:    Optional[str]
    terms_of_use:    Optional[str]
    guidelines:      Optional[str]
    interior_photos: Optional[str]

    is_active:  bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
