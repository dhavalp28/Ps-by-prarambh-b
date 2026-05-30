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


# ============ Profile Management ============

def get_user_profile(db: Session, user_id: int):
    """
    Get current user profile
    """
    from repositories.user_repository import get_user_by_id
    
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone,
        "is_phone_verified": user.is_phone_verified,
        "city": {
            "id": user.city.id,
            "name": user.city.name,
            "state": {
                "id": user.city.state.id,
                "name": user.city.state.name
            }
        } if user.city else None,
        "referral_code": user.referral_code
    }


def update_user_profile(db: Session, user_id: int, data):
    """
    Update user profile (name, email, location)
    """
    from repositories.user_repository import get_user_by_id
    
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Check if new email is already registered (if email is being changed)
    if data.email and data.email != user.email:
        existing_email = get_user_by_email(db, data.email)
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
    
    # Validate state and city if provided
    if data.state_id or data.city_id:
        state_id = data.state_id or user.city.state_id
        city_id = data.city_id or user.city_id
        
        state = get_state_by_id(db, state_id)
        if not state:
            raise HTTPException(
                status_code=404,
                detail="State not found"
            )
        
        city = get_city_by_id(db, city_id)
        if not city:
            raise HTTPException(
                status_code=404,
                detail="City not found"
            )
        
        if city.state_id != state_id:
            raise HTTPException(
                status_code=400,
                detail="City does not belong to the selected state"
            )
    
    # Prepare update data
    update_data = {}
    if data.first_name:
        update_data["first_name"] = data.first_name
    if data.last_name:
        update_data["last_name"] = data.last_name
    if data.email:
        update_data["email"] = data.email
    if data.state_id:
        update_data["state_id"] = data.state_id
    if data.city_id:
        update_data["city_id"] = data.city_id
    
    # Update user
    updated_user = update_user(db, user, update_data)
    
    return {
        "id": updated_user.id,
        "first_name": updated_user.first_name,
        "last_name": updated_user.last_name,
        "email": updated_user.email,
        "phone": updated_user.phone,
        "is_phone_verified": updated_user.is_phone_verified,
        "city": {
            "id": updated_user.city.id,
            "name": updated_user.city.name,
            "state": {
                "id": updated_user.city.state.id,
                "name": updated_user.city.state.name
            }
        } if updated_user.city else None,
        "referral_code": updated_user.referral_code
    }


def change_phone_init(db: Session, user_id: int, new_phone: str):
    """
    Step 1: Initiate phone change - send OTP to new phone
    """
    from repositories.user_repository import get_user_by_id
    
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Check if new phone is already registered
    existing_user = get_user_by_phone(db, new_phone)
    if existing_user and existing_user.id != user_id:
        raise HTTPException(
            status_code=400,
            detail="Phone number already registered"
        )
    
    # Generate OTP
    otp = generate_otp()
    expires_at = get_otp_expiry_time(minutes=10)
    
    # Store temporary data
    temp_data = {
        "user_id": user_id,
        "old_phone": user.phone,
        "new_phone": new_phone
    }
    
    # Create OTP session
    otp_session = create_otp_session(
        db=db,
        phone=new_phone,
        otp=otp,
        purpose="change_phone",
        expires_at=expires_at,
        temp_user_data=json.dumps(temp_data)
    )
    
    # TODO: Send OTP to new phone number
    
    return {
        "otp_session_id": otp_session.id,
        "phone": new_phone,
        "expires_at": otp_session.expires_at.isoformat(),
        "message": "OTP sent to new phone number. Please verify within 10 minutes.",
        "otp": otp  # Remove in production
    }


def change_phone_verify(db: Session, otp_session_id: int, entered_otp: str):
    """
    Step 2: Verify OTP and complete phone change
    """
    from repositories.user_repository import get_user_by_id
    
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
    
    # Check max attempts
    if otp_session.attempts >= 5:
        delete_otp_session(db, otp_session_id)
        raise HTTPException(
            status_code=400,
            detail="Maximum OTP attempts exceeded. Please request a new OTP."
        )
    
    # Increment attempts
    increment_attempts(db, otp_session_id)
    
    # Verify OTP
    is_development = True  # Set to False in production
    if not verify_otp(entered_otp, otp_session.otp, is_development=is_development):
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP. Please try again."
        )
    
    # Parse temporary data
    temp_data = json.loads(otp_session.temp_user_data)
    user_id = temp_data["user_id"]
    new_phone = temp_data["new_phone"]
    
    # Get user
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Update phone
    updated_user = update_user(db, user, {"phone": new_phone})
    
    # Mark OTP session as verified
    update_otp_session(db, otp_session_id, is_verified=True)
    
    return {
        "id": updated_user.id,
        "first_name": updated_user.first_name,
        "last_name": updated_user.last_name,
        "email": updated_user.email,
        "phone": updated_user.phone,
        "is_phone_verified": updated_user.is_phone_verified,
        "city": {
            "id": updated_user.city.id,
            "name": updated_user.city.name,
            "state": {
                "id": updated_user.city.state.id,
                "name": updated_user.city.state.name
            }
        } if updated_user.city else None,
        "referral_code": updated_user.referral_code,
        "message": "Phone number updated successfully"
    }
