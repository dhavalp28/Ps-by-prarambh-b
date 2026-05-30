from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SubscriptionPurchaseCreateRequest(BaseModel):
    subscription_plan_id: int


class RazorpayOrderResponse(BaseModel):
    order_id: str
    amount: int
    currency: str
    key: str
    plan_id: int
    plan_name: str


class SubscriptionPaymentVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PaymentOrderAdminResponse(BaseModel):
    id: int
    user_id: int
    subscription_plan_id: int
    provider: str
    provider_order_id: str
    provider_payment_id: Optional[str] = None
    amount: float
    currency: str
    status: str
    receipt: str
    created_at: datetime
    paid_at: Optional[datetime] = None
