from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

VALID_WEEKDAYS = {
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
}


class CouponBusinessSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_name: str
    is_active: bool


class CouponBase(BaseModel):
    business_id: int = Field(gt=0)
    coupon_name: str = Field(min_length=1)
    discount: float = Field(gt=0)
    description: Optional[str] = None
    valid_till: Optional[date] = None
    validity_days: Optional[int] = Field(default=None, ge=1)
    max_redemption_count: int = Field(gt=0)
    is_active: bool = True
    not_valid_on: list[str] = Field(default_factory=list)

    @field_validator("coupon_name")
    @classmethod
    def validate_coupon_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Coupon name is required")
        return cleaned

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("not_valid_on")
    @classmethod
    def validate_not_valid_on(cls, value: list[str]) -> list[str]:
        normalized: list[str] = []
        for day in value:
            cleaned = day.strip().title()
            if cleaned not in VALID_WEEKDAYS:
                raise ValueError(f"Invalid weekday: {day}")
            if cleaned not in normalized:
                normalized.append(cleaned)
        return normalized

    @model_validator(mode="after")
    def validate_validity_window(self):
        if self.valid_till and self.validity_days:
            raise ValueError("Use either Valid Till or Validity Days, not both")
        return self


class CouponCreate(CouponBase):
    pass


class CouponUpdate(BaseModel):
    business_id: Optional[int] = Field(default=None, gt=0)
    coupon_name: Optional[str] = Field(default=None, min_length=1)
    discount: Optional[float] = Field(default=None, gt=0)
    description: Optional[str] = None
    valid_till: Optional[date] = None
    validity_days: Optional[int] = Field(default=None, ge=1)
    max_redemption_count: Optional[int] = Field(default=None, gt=0)
    is_active: Optional[bool] = None
    not_valid_on: Optional[list[str]] = None

    @field_validator("coupon_name")
    @classmethod
    def validate_coupon_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Coupon name is required")
        return cleaned

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("not_valid_on")
    @classmethod
    def validate_not_valid_on(cls, value: Optional[list[str]]) -> Optional[list[str]]:
        if value is None:
            return None
        normalized: list[str] = []
        for day in value:
            cleaned = day.strip().title()
            if cleaned not in VALID_WEEKDAYS:
                raise ValueError(f"Invalid weekday: {day}")
            if cleaned not in normalized:
                normalized.append(cleaned)
        return normalized

    @model_validator(mode="after")
    def validate_validity_window(self):
        if self.valid_till and self.validity_days:
            raise ValueError("Use either Valid Till or Validity Days, not both")
        return self


class CouponResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_id: int
    business: CouponBusinessSummary
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
