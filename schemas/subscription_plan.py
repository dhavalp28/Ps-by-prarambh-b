from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class SubscriptionPlanCreate(BaseModel):
    plan_name: str
    description: Optional[str] = None
    price: float
    validity_days: int
    daily_coupon_limit: int
    total_coupon_limit: int
    is_active: bool = True


class SubscriptionPlanUpdate(BaseModel):
    plan_name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    validity_days: Optional[int] = None
    daily_coupon_limit: Optional[int] = None
    total_coupon_limit: Optional[int] = None
    is_active: Optional[bool] = None


class SubscriptionPlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    plan_name: str
    description: Optional[str]
    price: float
    validity_days: int
    daily_coupon_limit: int
    total_coupon_limit: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
