from db.base import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True, index=True)

    role = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)  # user | admin | vendor
    session_type = Column(String, nullable=False)  # mobile | web

    session_key = Column(String, nullable=False, unique=True, index=True)
    refresh_token_hash = Column(String, nullable=True)

    device_id = Column(String, nullable=True, index=True)
    device_name = Column(String, nullable=True)
    device_platform = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)

    is_active = Column(Boolean, nullable=False, default=True)
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    access_expires_at = Column(DateTime(timezone=True), nullable=True)
    refresh_expires_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User")
    vendor = relationship("Vendor")
