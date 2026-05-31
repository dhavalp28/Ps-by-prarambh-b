from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RedemptionHistoryCreate(BaseModel):
    user_id: int
    business_id: int
    business_code_id: int
    user_subscription_id: int
    coupon_id: Optional[int] = None
    claim_reference: Optional[int] = None
    status: str = "success"
    remaining_daily_limit: int
    remaining_total_limit: int


class CouponClaimRequest(BaseModel):
    business_id: int = Field(gt=0)
    coupon_id: int = Field(gt=0)
    code: str = Field(min_length=1)


class RedemptionUserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    phone: str


class RedemptionBusinessSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_name: str


class RedemptionCouponSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    coupon_name: str
    discount: float
    is_active: bool


class RedemptionHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    business_id: int
    business_code_id: int
    user_subscription_id: int
    coupon_id: Optional[int] = None
    claim_reference: Optional[int] = None
    status: str
    remaining_daily_limit: int
    remaining_total_limit: int
    redeemed_at: datetime
    created_at: datetime
    user: Optional[RedemptionUserSummary] = None
    business: Optional[RedemptionBusinessSummary] = None
    coupon: Optional[RedemptionCouponSummary] = None


class RedemptionDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    business_id: int
    coupon_id: Optional[int] = None
    claim_reference: Optional[int] = None
    status: str
    remaining_daily_limit: int
    remaining_total_limit: int
    redeemed_at: datetime

    # Nested details
    user: Optional[dict] = None
    business: Optional[dict] = None
    business_code: Optional[dict] = None
    coupon: Optional[dict] = None


class RedemptionSummaryResponse(BaseModel):
    total_redeemed_today: int
    total_redeemed_all_time: int
    remaining_daily_limit: int
    remaining_total_limit: int
    subscription_expires_at: Optional[datetime] = None
    is_subscription_active: bool
    daily_redemption_count: int = 0
    total_redemption_count: int = 0
    last_redeemed_on: Optional[date] = None


class CouponClaimResponse(BaseModel):
    success: bool
    message: str
    redemption_id: int
    claim_reference: int
    coupon_id: int
    business_id: int
    business_name: str
    remaining_daily_limit: int
    remaining_total_limit: int
    daily_redemption_count: int
    total_redemption_count: int
    coupon: RedemptionCouponSummary


class RedemptionAnalyticsResponse(BaseModel):
    total_redemptions: int
    today_redemptions: int
    active_subscriptions: int
    top_redeemed_businesses: list
