from db.base import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)

    # ── Basic Info ─────────────────────────────────────────────────────────
    business_name = Column(String, nullable=False)
    title = Column(String, nullable=True)
    business_phone = Column(String, nullable=False)
    vendor_email = Column(String, nullable=True)
    website = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    cover_image_url = Column(String, nullable=True)

    owner_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    brand_id = Column(
        Integer, ForeignKey("brands.id", ondelete="SET NULL"), nullable=True
    )

    # ── Location ───────────────────────────────────────────────────────────
    business_address = Column(String, nullable=False)
    map_link_url = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    business_type = Column(String, nullable=True)

    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    sub_category_id = Column(Integer, ForeignKey("sub_categories.id"), nullable=True)

    # ── Hours & Details ────────────────────────────────────────────────────
    open_time = Column(String, nullable=True)
    close_time = Column(String, nullable=True)
    cuisine = Column(String, nullable=True)
    open_days = Column(String, nullable=True)  # comma-separated e.g. "Mon,Tue,Wed"

    about_us = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    facebook_url = Column(String, nullable=True)
    twitter_url = Column(String, nullable=True)
    instagram_url = Column(String, nullable=True)

    # ── Media & Lists ──────────────────────────────────────────────────────
    payment_methods = Column(String, nullable=True)  # comma-separated
    highlights = Column(String, nullable=True)  # comma-separated
    amenities = Column(String, nullable=True)  # comma-separated
    other_phones = Column(String, nullable=True)  # comma-separated
    terms_of_use = Column(String, nullable=True)  # comma-separated
    guidelines = Column(String, nullable=True)  # comma-separated
    interior_photos = Column(Text, nullable=True)  # comma-separated URLs

    # ── Meta ───────────────────────────────────────────────────────────────
    average_rating = Column(
        Float, nullable=False, default=0.0, server_default=text("0")
    )
    total_reviews = Column(Integer, nullable=False, default=0, server_default=text("0"))
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # ── Relationships ──────────────────────────────────────────────────────
    state = relationship("State")
    city = relationship("City")
    category = relationship("Category")
    sub_category = relationship("SubCategory")
    owner = relationship("Vendor")
    brand = relationship("Brand", back_populates="businesses")
    business_code = relationship(
        "BusinessCode", uselist=False, back_populates="business"
    )
    coupons = relationship("Coupon", back_populates="business")
    service_facility_links = relationship(
        "BusinessServiceFacility",
        back_populates="business",
        cascade="all, delete-orphan",
    )
    gallery_images = relationship(
        "BusinessGallery",
        back_populates="business",
        cascade="all, delete-orphan",
        order_by="BusinessGallery.sort_order.asc(), BusinessGallery.id.asc()",
    )
    reviews = relationship(
        "BusinessReview",
        back_populates="business",
        cascade="all, delete-orphan",
    )
