from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func

from db.base import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)

    plan_name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    validity_days = Column(Integer, nullable=False)
    daily_coupon_limit = Column(Integer, nullable=False)
    total_coupon_limit = Column(Integer, nullable=False)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
