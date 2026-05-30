from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from schemas.brand import BrandSummary
from schemas.business_review import (
    BusinessRatingSummaryResponse,
    BusinessReviewResponse,
)
from schemas.category import CategoryResponse
from schemas.city import CityResponse
from schemas.state import StateResponse
from schemas.sub_category import SubCategoryResponse


class OwnerSummary(BaseModel):
    id: int
    name: str
    email: str
    phone: str

    class Config:
        from_attributes = True


class BusinessGalleryImageCreate(BaseModel):
    image_url: str = Field(min_length=1)
    sort_order: int = Field(default=0, ge=0)

    @field_validator("image_url")
    @classmethod
    def validate_image_url(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Image URL is required")
        return cleaned


class BusinessGalleryImageReorder(BaseModel):
    id: int = Field(gt=0)
    sort_order: int = Field(ge=0)


class BusinessBase(BaseModel):
    business_name: str
    title: Optional[str] = None
    business_phone: str
    vendor_email: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    owner_id: Optional[int] = None
    brand_id: Optional[int] = None

    business_address: str
    map_link_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    business_type: Optional[str] = None
    state_id: int
    city_id: int
    category_id: int
    sub_category_id: Optional[int] = None

    open_time: Optional[str] = None
    close_time: Optional[str] = None
    cuisine: Optional[str] = None
    open_days: Optional[str] = None

    about_us: Optional[str] = None
    description: Optional[str] = None

    facebook_url: Optional[str] = None
    twitter_url: Optional[str] = None
    instagram_url: Optional[str] = None

    payment_methods: Optional[str] = None
    highlights: Optional[str] = None
    amenities: Optional[str] = None
    other_phones: Optional[str] = None
    terms_of_use: Optional[str] = None
    guidelines: Optional[str] = None
    interior_photos: Optional[str] = None

    facility_ids: list[int] = Field(default_factory=list)
    gallery_items: list[BusinessGalleryImageCreate] = Field(default_factory=list)

    @field_validator(
        "business_name",
        "business_phone",
        "business_address",
        mode="before",
    )
    @classmethod
    def validate_required_strings(cls, value):
        if value is None:
            raise ValueError("Field is required")
        cleaned = value.strip() if isinstance(value, str) else value
        if cleaned == "":
            raise ValueError("Field is required")
        return cleaned

    @field_validator(
        "title",
        "vendor_email",
        "website",
        "logo_url",
        "cover_image_url",
        "map_link_url",
        "business_type",
        "open_time",
        "close_time",
        "cuisine",
        "open_days",
        "about_us",
        "description",
        "facebook_url",
        "twitter_url",
        "instagram_url",
        "payment_methods",
        "highlights",
        "amenities",
        "other_phones",
        "terms_of_use",
        "guidelines",
        "interior_photos",
        mode="before",
    )
    @classmethod
    def normalize_optional_strings(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = value.strip()
            return cleaned or None
        return value

    @field_validator("facility_ids")
    @classmethod
    def validate_facility_ids(cls, value: list[int]) -> list[int]:
        normalized: list[int] = []
        for item in value:
            item_id = int(item)
            if item_id > 0 and item_id not in normalized:
                normalized.append(item_id)
        return normalized


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(BaseModel):
    business_name: Optional[str] = None
    title: Optional[str] = None
    business_phone: Optional[str] = None
    vendor_email: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    owner_id: Optional[int] = None
    brand_id: Optional[int] = None

    business_address: Optional[str] = None
    map_link_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    business_type: Optional[str] = None
    state_id: Optional[int] = None
    city_id: Optional[int] = None
    category_id: Optional[int] = None
    sub_category_id: Optional[int] = None

    open_time: Optional[str] = None
    close_time: Optional[str] = None
    cuisine: Optional[str] = None
    open_days: Optional[str] = None

    about_us: Optional[str] = None
    description: Optional[str] = None

    facebook_url: Optional[str] = None
    twitter_url: Optional[str] = None
    instagram_url: Optional[str] = None

    payment_methods: Optional[str] = None
    highlights: Optional[str] = None
    amenities: Optional[str] = None
    other_phones: Optional[str] = None
    terms_of_use: Optional[str] = None
    guidelines: Optional[str] = None
    interior_photos: Optional[str] = None

    facility_ids: Optional[list[int]] = None
    gallery_items: Optional[list[BusinessGalleryImageCreate]] = None
    gallery_delete_ids: Optional[list[int]] = None
    gallery_reorder: Optional[list[BusinessGalleryImageReorder]] = None
    is_active: Optional[bool] = None

    @field_validator(
        "business_name",
        "business_phone",
        "business_address",
        mode="before",
    )
    @classmethod
    def normalize_required_strings(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = value.strip()
            return cleaned or None
        return value

    @field_validator(
        "title",
        "vendor_email",
        "website",
        "logo_url",
        "cover_image_url",
        "map_link_url",
        "business_type",
        "open_time",
        "close_time",
        "cuisine",
        "open_days",
        "about_us",
        "description",
        "facebook_url",
        "twitter_url",
        "instagram_url",
        "payment_methods",
        "highlights",
        "amenities",
        "other_phones",
        "terms_of_use",
        "guidelines",
        "interior_photos",
        mode="before",
    )
    @classmethod
    def normalize_optional_strings(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = value.strip()
            return cleaned or None
        return value

    @field_validator("facility_ids")
    @classmethod
    def validate_facility_ids(cls, value: Optional[list[int]]) -> Optional[list[int]]:
        if value is None:
            return None
        normalized: list[int] = []
        for item in value:
            item_id = int(item)
            if item_id > 0 and item_id not in normalized:
                normalized.append(item_id)
        return normalized

    @field_validator("gallery_delete_ids")
    @classmethod
    def validate_gallery_delete_ids(
        cls, value: Optional[list[int]]
    ) -> Optional[list[int]]:
        if value is None:
            return None
        normalized: list[int] = []
        for item in value:
            item_id = int(item)
            if item_id > 0 and item_id not in normalized:
                normalized.append(item_id)
        return normalized


class BusinessGalleryImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_url: str
    sort_order: int


class BusinessFacilityResponse(BaseModel):
    id: int
    name: str
    icon: Optional[str]
    description: Optional[str] = None


class BusinessCouponOfferResponse(BaseModel):
    id: int
    coupon_name: str
    discount: float
    description: Optional[str]
    valid_till: Optional[date]
    validity_days: Optional[int]
    max_redemption_count: int
    redemption_count: int
    remaining_redemptions: int
    is_active: bool
    status: str
    not_valid_on: list[str]
    is_expired: bool
    can_redeem: bool
    effective_expiry_date: Optional[date]
    created_at: datetime
    updated_at: datetime


class BusinessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    business_name: str
    title: Optional[str]
    business_phone: str
    vendor_email: Optional[str]
    website: Optional[str]
    logo_url: Optional[str]
    cover_image_url: Optional[str]
    owner: Optional[OwnerSummary]
    brand: Optional[BrandSummary]

    business_address: str
    map_link_url: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    business_type: Optional[str]

    state: StateResponse
    city: CityResponse
    category: CategoryResponse
    sub_category: Optional[SubCategoryResponse]

    open_time: Optional[str]
    close_time: Optional[str]
    cuisine: Optional[str]
    open_days: Optional[str]

    about_us: Optional[str]
    description: Optional[str]

    facebook_url: Optional[str]
    twitter_url: Optional[str]
    instagram_url: Optional[str]

    payment_methods: Optional[str]
    highlights: Optional[str]
    amenities: Optional[str]
    other_phones: Optional[str]
    terms_of_use: Optional[str]
    guidelines: Optional[str]
    interior_photos: Optional[str]

    average_rating: float
    total_reviews: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class BusinessDetailsResponse(BusinessResponse):
    coupons: list[BusinessCouponOfferResponse] = Field(default_factory=list)
    facilities: list[BusinessFacilityResponse] = Field(default_factory=list)
    gallery_images: list[BusinessGalleryImageResponse] = Field(default_factory=list)
    rating_summary: BusinessRatingSummaryResponse
    latest_reviews: list[BusinessReviewResponse] = Field(default_factory=list)
