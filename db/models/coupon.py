from db.base import Base
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(
        Integer, ForeignKey("businesses.id"), nullable=False, index=True
    )

    coupon_name = Column(String, nullable=False)
    discount = Column(Numeric(10, 2), nullable=False)
    description = Column(Text, nullable=True)

    valid_till = Column(Date, nullable=True)
    validity_days = Column(Integer, nullable=True)

    max_redemption_count = Column(Integer, nullable=False, default=1)
    redemption_count = Column(Integer, nullable=False, default=0)

    is_active = Column(Boolean, nullable=False, default=True)
    not_valid_on = Column(String, nullable=True)  # comma-separated weekdays

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    business = relationship("Business", back_populates="coupons")
