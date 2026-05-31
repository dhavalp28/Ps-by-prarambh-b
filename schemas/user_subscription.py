from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserSubscriptionCreate(BaseModel):
    user_id: int
    subscription_plan_id: int
    expires_at: datetime


class UserSubscriptionUpdate(BaseModel):
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class SubscriptionPlanSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    plan_name: str
    daily_coupon_limit: int
    total_coupon_limit: int


class UserSubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    subscription_plan_id: int
    purchased_at: datetime
    expires_at: datetime
    is_active: bool
    daily_redemption_count: int
    total_redemption_count: int
    last_redeemed_on: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    subscription_plan: SubscriptionPlanSummary


class UserSubscriptionDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    purchased_at: datetime
    expires_at: datetime
    is_active: bool
    daily_redemption_count: int
    total_redemption_count: int
    last_redeemed_on: Optional[date] = None
    subscription_plan: SubscriptionPlanSummary
    days_remaining: int
    is_expired: bool
