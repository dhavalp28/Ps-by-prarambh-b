from db.base import Base
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class PaymentOrder(Base):
    __tablename__ = "payment_orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subscription_plan_id = Column(
        Integer, ForeignKey("subscription_plans.id"), nullable=False
    )

    provider = Column(String, nullable=False, default="razorpay")
    provider_order_id = Column(String, nullable=False, unique=True, index=True)
    provider_payment_id = Column(String, nullable=True, unique=True, index=True)
    receipt = Column(String, nullable=False, unique=True)

    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="INR")
    status = Column(String, nullable=False, default="created")
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    paid_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User")
    subscription_plan = relationship("SubscriptionPlan")
