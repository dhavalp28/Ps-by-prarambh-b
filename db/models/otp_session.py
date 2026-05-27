from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func

from db.base import Base


class OtpSession(Base):
    __tablename__ = "otp_sessions"

    id = Column(Integer, primary_key=True, index=True)

    phone = Column(String, nullable=False, index=True)
    otp = Column(String, nullable=False)
    purpose = Column(String, nullable=False)  # 'register' or 'login'
    
    # Temporary user data for registration (stored as JSON string)
    temp_user_data = Column(String, nullable=True)
    
    expires_at = Column(DateTime(timezone=True), nullable=False)
    attempts = Column(Integer, default=0)
    
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
