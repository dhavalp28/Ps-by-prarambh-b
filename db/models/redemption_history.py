from db.base import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class RedemptionHistory(Base):
    __tablename__ = "redemption_history"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    business_code_id = Column(Integer, ForeignKey("business_codes.id"), nullable=False)
    user_subscription_id = Column(
        Integer, ForeignKey("user_subscriptions.id"), nullable=False
    )
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=True, index=True)
    claim_reference = Column(Integer, nullable=True, index=True)

    # Status
    status = Column(String, default="success")  # success, failed, expired

    # Remaining limits after redemption
    remaining_daily_limit = Column(Integer, nullable=False)
    remaining_total_limit = Column(Integer, nullable=False)

    redeemed_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")
    business = relationship("Business")
    business_code = relationship("BusinessCode")
    user_subscription = relationship("UserSubscription")
    coupon = relationship("Coupon")
