from db.base import Base
from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship


class BusinessServiceFacility(Base):
    __tablename__ = "business_service_facilities"
    __table_args__ = (
        UniqueConstraint(
            "business_id",
            "facility_id",
            name="uq_business_service_facilities_business_facility",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(
        Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False
    )
    facility_id = Column(
        Integer,
        ForeignKey("service_facilities.id", ondelete="CASCADE"),
        nullable=False,
    )

    business = relationship("Business", back_populates="service_facility_links")
    facility = relationship("ServiceFacility", back_populates="business_links")
