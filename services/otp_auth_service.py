import json
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from repositories.user_repository import (
    get_user_by_phone,
    get_user_by_email,
    create_user,
    update_user
)
from repositories.otp_session_repository import (
    create_otp_session,
    get_otp_session_by_phone,
    get_otp_session_by_id,
    update_otp_session,
    increment_attempts,
    delete_otp_session
)
from repositories.state_repository import get_state_by_id
from repositories.city_repository import get_city_by_id

from core.otp import generate_otp, verify_otp, get_otp_expiry_time, is_otp_expired
from core.security import create_access_token


# ============ Registration Flow ============

def register_init(db: Session, data):
    """
    Step 1: Initialize registration - validate data and send OTP
    """
    # Check if phone already registered
    existing_phone = get_user_by_phone(db, data.phone)
    if existing_phone:
        raise HTTPException(
            status_code=400,
            detail="Phone already registered"
        )

    # Check if email already registered
    existing_email = get_user_by_email(db, data.email)
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Validate state exists
    state = get_state_by_id(db, data.state_id)
    if not state:
        raise HTTPException(
            status_code=404,
            detail="State not found"
        )

    # Validate city exists and belongs to the given state
    city = get_city_by_id(db, data.city_id)
    if not city:
        raise HTTPException(
            status_code=404,
            detail="City not found"
        )

    if city.state_id != data.state_id:
        raise HTTPException(
            status_code=400,
            detail="City does not belong to the selected state"
        )

    # Generate OTP
    otp = generate_otp()
    expires_at = get_otp_expiry_time(minutes=10)

    # Store temporary user data
    temp_user_data = {
        "first_name": data.first_name,
        "last_name": data.last_name,
        "email": data.email,
        "phone": data.phone,
        "state_id": data.state_id,
        "city_id": data.city_id,
        "referral_code": data.referral_code
    }

    # Create OTP session
    otp_session = create_otp_session(
        db=db,
        phone=data.phone,
        otp=otp,
        purpose="register",
        expires_at=expires_at,
        temp_user_data=json.dumps(temp_user_data)
    )

    # TODO: Send OTP via SMS/Email
    # For now, return OTP for testing (remove in production)
    
    return {
        "otp_session_id": otp_session.id,
        "phone": otp_session.phone,
        "expires_at": otp_session.expires_at.isoformat(),
        "message": "OTP sent successfully. Please verify within 10 minutes.",
        "otp": otp  # Remove in production
    }


def register_verify(db: Session, otp_session_id: int, entered_otp: str):
    """
    Step 2: Verify OTP and create user
    """
    # Get OTP session
    otp_session = get_otp_session_by_id(db, otp_session_id)
    if not otp_session:
        raise HTTPException(
            status_code=404,
            detail="OTP session not found"
        )

    # Check if OTP is expired
    if is_otp_expired(otp_session.expires_at):
        raise HTTPException(
            status_code=400,
            detail="OTP has expired. Please request a new one."
        )

    # Check max attempts (5 attempts)
    if otp_session.attempts >= 5:
        delete_otp_session(db, otp_session_id)
        raise HTTPException(
            status_code=400,
            detail="Maximum OTP attempts exceeded. Please request a new OTP."
        )

    # Increment attempts
    increment_attempts(db, otp_session_id)

    # Verify OTP (with development bypass)
    is_development = True  # Set to False in production
    if not verify_otp(entered_otp, otp_session.otp, is_development=is_development):
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP. Please try again."
        )

    # Parse temporary user data
    temp_user_data = json.loads(otp_session.temp_user_data)

    # Create user
    user_data = {
        "first_name": temp_user_data["first_name"],
        "last_name": temp_user_data["last_name"],
        "email": temp_user_data["email"],
        "phone": temp_user_data["phone"],
        "state_id": temp_user_data["state_id"],
        "city_id": temp_user_data["city_id"],
        "referral_code": temp_user_data.get("referral_code"),
        "hashed_password": None,  # No password for OTP-only login
        "is_phone_verified": True
    }

    user = create_user(db, user_data)

    # Mark OTP session as verified
    update_otp_session(db, otp_session_id, is_verified=True)

    # Create access token
    token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "is_phone_verified": user.is_phone_verified
        }
    }


# ============ Login Flow ============

def login_send_otp(db: Session, phone: str):
    """
    Step 1: Send OTP for login
    """
    # Check if user exists
    user = get_user_by_phone(db, phone)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found. Please register first."
        )

    # Check if phone is verified
    if not user.is_phone_verified:
        raise HTTPException(
            status_code=400,
            detail="Phone number not verified. Please complete registration."
        )

    # Generate OTP
    otp = generate_otp()
    expires_at = get_otp_expiry_time(minutes=10)

    # Create OTP session
    otp_session = create_otp_session(
        db=db,
        phone=phone,
        otp=otp,
        purpose="login",
        expires_at=expires_at
    )

    # TODO: Send OTP via SMS/Email
    # For now, return OTP for testing (remove in production)

    return {
        "otp_session_id": otp_session.id,
        "phone": otp_session.phone,
        "expires_at": otp_session.expires_at.isoformat(),
        "message": "OTP sent successfully. Please verify within 10 minutes.",
        "otp": otp  # Remove in production
    }


def login_verify(db: Session, otp_session_id: int, entered_otp: str):
    """
    Step 2: Verify OTP and login user
    """
    # Get OTP session
    otp_session = get_otp_session_by_id(db, otp_session_id)
    if not otp_session:
        raise HTTPException(
            status_code=404,
            detail="OTP session not found"
        )

    # Check if OTP is expired
    if is_otp_expired(otp_session.expires_at):
        raise HTTPException(
            status_code=400,
            detail="OTP has expired. Please request a new one."
        )

    # Check max attempts (5 attempts)
    if otp_session.attempts >= 5:
        delete_otp_session(db, otp_session_id)
        raise HTTPException(
            status_code=400,
            detail="Maximum OTP attempts exceeded. Please request a new OTP."
        )

    # Increment attempts
    increment_attempts(db, otp_session_id)

    # Verify OTP (with development bypass)
    is_development = True  # Set to False in production
    if not verify_otp(entered_otp, otp_session.otp, is_development=is_development):
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP. Please try again."
        )

    # Get user
    user = get_user_by_phone(db, otp_session.phone)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Mark OTP session as verified
    update_otp_session(db, otp_session_id, is_verified=True)

    # Create access token
    token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "is_phone_verified": user.is_phone_verified
        }
    }


# ============ Resend OTP ============

def resend_otp(db: Session, otp_session_id: int):
    """
    Resend OTP - invalidate old OTP and generate new one
    """
    # Get OTP session
    otp_session = get_otp_session_by_id(db, otp_session_id)
    if not otp_session:
        raise HTTPException(
            status_code=404,
            detail="OTP session not found"
        )

    # Check if already verified
    if otp_session.is_verified:
        raise HTTPException(
            status_code=400,
            detail="OTP already verified"
        )

    # Generate new OTP
    new_otp = generate_otp()
    new_expires_at = get_otp_expiry_time(minutes=10)

    # Update OTP session with new OTP and reset attempts
    update_otp_session(
        db=db,
        otp_session_id=otp_session_id,
        otp=new_otp,
        expires_at=new_expires_at,
        attempts=0
    )

    # TODO: Send new OTP via SMS/Email

    return {
        "otp_session_id": otp_session_id,
        "phone": otp_session.phone,
        "expires_at": new_expires_at.isoformat(),
        "message": "New OTP sent successfully. Please verify within 10 minutes.",
        "otp": new_otp  # Remove in production
    }


# ============ Change Phone Number During Registration ============

def update_phone_during_registration(db: Session, otp_session_id: int, new_phone: str):
    """
    Update phone number during registration - invalidate old OTP and generate new one
    """
    # Get OTP session
    otp_session = get_otp_session_by_id(db, otp_session_id)
    if not otp_session:
        raise HTTPException(
            status_code=404,
            detail="OTP session not found"
        )

    # Check if already verified
    if otp_session.is_verified:
        raise HTTPException(
            status_code=400,
            detail="OTP already verified. Cannot change phone number."
        )

    # Check if new phone is already registered
    existing_user = get_user_by_phone(db, new_phone)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Phone number already registered"
        )

    # Generate new OTP
    new_otp = generate_otp()
    new_expires_at = get_otp_expiry_time(minutes=10)

    # Update OTP session with new phone and OTP
    update_otp_session(
        db=db,
        otp_session_id=otp_session_id,
        phone=new_phone,
        otp=new_otp,
        expires_at=new_expires_at,
        attempts=0
    )

    # TODO: Send new OTP to new phone number

    return {
        "otp_session_id": otp_session_id,
        "phone": new_phone,
        "expires_at": new_expires_at.isoformat(),
        "message": "OTP sent to new phone number. Please verify within 10 minutes.",
        "otp": new_otp  # Remove in production
    }
