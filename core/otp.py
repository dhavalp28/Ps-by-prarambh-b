import random
import string
from datetime import datetime, timedelta, timezone

STATIC_OTP = "123456"  # For development/testing only


def generate_otp(length: int = 6) -> str:
    """Generate a random OTP of specified length"""
    return ''.join(random.choices(string.digits, k=length))


def verify_otp(entered_otp: str, real_otp: str, is_development: bool = True) -> bool:
    """
    Verify OTP with development bypass option.
    
    Args:
        entered_otp: The OTP entered by user
        real_otp: The actual OTP sent to user
        is_development: If True, allows "123456" as bypass (development only)
    
    Returns:
        True if OTP is valid, False otherwise
    """
    # Development bypass - REMOVE IN PRODUCTION
    if is_development and entered_otp == STATIC_OTP:
        return True
    
    return entered_otp == real_otp


def get_otp_expiry_time(minutes: int = 10) -> datetime:
    """Get OTP expiry time (default 10 minutes from now) - Returns timezone-aware datetime"""
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)


def is_otp_expired(expires_at: datetime) -> bool:
    """Check if OTP has expired - Handles both naive and aware datetimes"""
    # Get current time in UTC
    current_time = datetime.now(timezone.utc)
    
    # If expires_at is naive, assume it's UTC and make it aware
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    # If current_time is naive (shouldn't happen), make it aware
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)
    
    return current_time > expires_at
