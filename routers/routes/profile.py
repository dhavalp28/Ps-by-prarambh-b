from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from routers.deps import get_db, get_current_user
from schemas.auth import ProfileUpdateSchema, ChangePhoneInitSchema, ChangePhoneVerifySchema, UserResponse
from services.otp_auth_service import (
    get_user_profile,
    update_user_profile,
    change_phone_init,
    change_phone_verify
)
from utils.response import success_list, success_update, error_server

router = APIRouter()


@router.get("/me", tags=["Profile"])
def get_profile(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get current user profile
    
    Returns the authenticated user's profile information including:
    - Personal details (name, email, phone)
    - Location (city and state)
    - Referral code
    - Phone verification status
    """
    try:
        profile = get_user_profile(db, current_user.id)
        return success_list(title="User Profile", data=profile)
    except Exception as e:
        return error_server(title="Get Profile", error=str(e))


@router.put("/me", tags=["Profile"])
def update_profile(
    payload: ProfileUpdateSchema,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile
    
    Update user information such as:
    - First name and last name
    - Email address
    - Location (state and city)
    
    Note: Phone number cannot be changed here. Use the change-phone endpoint instead.
    """
    try:
        updated_profile = update_user_profile(db, current_user.id, payload)
        return success_update(title="Profile Updated", data=updated_profile)
    except Exception as e:
        return error_server(title="Update Profile", error=str(e))


@router.post("/change-phone/init", tags=["Profile"])
def change_phone_init_endpoint(
    payload: ChangePhoneInitSchema,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate phone number change
    
    Step 1: Send OTP to the new phone number
    
    Returns:
    - otp_session_id: Use this in the verify endpoint
    - expires_at: OTP expiration time
    - message: Confirmation message
    """
    try:
        result = change_phone_init(db, current_user.id, payload.new_phone)
        return success_list(
            title="Phone Change Initiated",
            data={
                "otp_session_id": result["otp_session_id"],
                "phone": result["phone"],
                "expires_at": result["expires_at"]
            },
            message=result["message"]
        )
    except Exception as e:
        return error_server(title="Change Phone Init", error=str(e))


@router.post("/change-phone/verify", tags=["Profile"])
def change_phone_verify_endpoint(
    payload: ChangePhoneVerifySchema,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify phone number change
    
    Step 2: Verify OTP and complete the phone number change
    
    Requires:
    - otp_session_id: From the init endpoint
    - otp: The OTP sent to the new phone number
    
    Returns: Updated user profile with new phone number
    """
    try:
        result = change_phone_verify(db, payload.otp_session_id, payload.otp)
        return success_update(
            title="Phone Number Changed",
            data={
                "id": result["id"],
                "first_name": result["first_name"],
                "last_name": result["last_name"],
                "email": result["email"],
                "phone": result["phone"],
                "is_phone_verified": result["is_phone_verified"],
                "city": result["city"],
                "referral_code": result["referral_code"]
            }
        )
    except Exception as e:
        return error_server(title="Change Phone Verify", error=str(e))
