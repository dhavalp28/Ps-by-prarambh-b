from pydantic import BaseModel, EmailStr
from typing import Optional
from schemas.city import CityResponse


# ============ Registration Flow ============

class RegisterInitSchema(BaseModel):
    """Initial registration request - send OTP"""
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    state_id: int
    city_id: int
    referral_code: Optional[str] = None


class RegisterVerifySchema(BaseModel):
    """Verify OTP and complete registration"""
    otp_session_id: int
    otp: str


# ============ Login Flow ============

class LoginSendOtpSchema(BaseModel):
    """Send OTP for login"""
    phone: str


class LoginVerifySchema(BaseModel):
    """Verify OTP for login"""
    otp_session_id: int
    otp: str


# ============ Resend OTP ============

class ResendOtpSchema(BaseModel):
    """Resend OTP"""
    otp_session_id: int


# ============ Profile Management ============

class ProfileUpdateSchema(BaseModel):
    """Update user profile"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    state_id: Optional[int] = None
    city_id: Optional[int] = None


class ChangePhoneInitSchema(BaseModel):
    """Initiate phone change - send OTP to new phone"""
    new_phone: str


class ChangePhoneVerifySchema(BaseModel):
    """Verify OTP and complete phone change"""
    otp_session_id: int
    otp: str


# ============ Response Schemas ============

class OtpSessionResponse(BaseModel):
    """OTP Session response"""
    id: int
    phone: str
    purpose: str
    expires_at: str
    attempts: int
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """User response"""
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    is_phone_verified: bool
    city: Optional[CityResponse] = None
    
    class Config:
        from_attributes = True


class AuthTokenResponse(BaseModel):
    """Authentication token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============ Legacy Schemas (kept for backward compatibility) ============

class RegisterSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    state_id: int
    city_id: int
    referral_code: Optional[str] = None
    password: str


class LoginSchema(BaseModel):
    phone: str
    password: str
