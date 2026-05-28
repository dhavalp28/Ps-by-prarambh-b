from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class RedemptionHistoryCreate(BaseModel):
    user_id: int
    business_id: int
    business_code_id: int
    user_subscription_id: int
    status: str = "success"
    remaining_daily_limit: int
    remaining_total_limit: int


class RedemptionHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    business_id: int
    business_code_id: int
    user_subscription_id: int
    status: str
    remaining_daily_limit: int
    remaining_total_limit: int
    redeemed_at: datetime
    created_at: datetime


class RedemptionDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    business_id: int
    status: str
    remaining_daily_limit: int
    remaining_total_limit: int
    redeemed_at: datetime
    
    # Nested details
    user: Optional[dict] = None
    business: Optional[dict] = None
    business_code: Optional[dict] = None


class RedemptionSummaryResponse(BaseModel):
    total_redeemed_today: int
    total_redeemed_all_time: int
    remaining_daily_limit: int
    remaining_total_limit: int
    subscription_expires_at: Optional[datetime] = None
    is_subscription_active: bool


class RedemptionAnalyticsResponse(BaseModel):
    total_redemptions: int
    today_redemptions: int
    active_subscriptions: int
    top_redeemed_businesses: list
