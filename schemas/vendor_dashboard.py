from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict
from schemas.business import BusinessResponse


class VendorBusinessCodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_id: int
    code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class VendorBusinessListItem(BusinessResponse):
    business_code: Optional[VendorBusinessCodeResponse] = None


class VendorDashboardSummaryResponse(BaseModel):
    vendor_id: int
    vendor_name: str
    total_businesses: int
    active_businesses: int
    inactive_businesses: int
    total_redemptions: int
    today_redemptions: int


class VendorRedemptionBusinessSummary(BaseModel):
    business_id: int
    business_name: str
    redemption_count: int


class VendorRedemptionHistoryItem(BaseModel):
    id: int
    business_id: int
    business_name: str
    user_id: int
    user_name: str
    user_phone: str
    coupon_id: Optional[int] = None
    coupon_name: Optional[str] = None
    claim_reference: Optional[int] = None
    status: str
    remaining_daily_limit: int
    remaining_total_limit: int
    redeemed_at: datetime


class VendorRedemptionHistoryResponse(BaseModel):
    items: List[VendorRedemptionHistoryItem]
    total: int
    skip: int
    limit: int


class VendorDashboardAnalyticsResponse(BaseModel):
    summary: VendorDashboardSummaryResponse
    top_businesses: List[VendorRedemptionBusinessSummary]
