from db.base import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class BusinessCode(Base):
    __tablename__ = "business_codes"

    id = Column(Integer, primary_key=True, index=True)

    business_id = Column(
        Integer, ForeignKey("businesses.id"), nullable=False, unique=True
    )
    code = Column(String, nullable=False, unique=True, index=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    business = relationship("Business", back_populates="business_code")
