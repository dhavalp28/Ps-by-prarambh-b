from db.base import Base
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_plan_id = Column(
        Integer, ForeignKey("subscription_plans.id"), nullable=False
    )

    # Subscription validity
    purchased_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    is_active = Column(Boolean, default=True)
    daily_redemption_count = Column(Integer, nullable=False, default=0)
    total_redemption_count = Column(Integer, nullable=False, default=0)
    last_redeemed_on = Column(Date, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user = relationship("User")
    subscription_plan = relationship("SubscriptionPlan")
