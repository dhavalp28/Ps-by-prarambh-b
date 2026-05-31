import json

from core.otp import generate_otp, get_otp_expiry_time, is_otp_expired, verify_otp
from fastapi import HTTPException, Request
from repositories.city_repository import get_city_by_id
from repositories.otp_session_repository import (
    create_otp_session,
    delete_otp_session,
    get_otp_session_by_id,
    increment_attempts,
    update_otp_session,
)
from repositories.state_repository import get_state_by_id
from repositories.user_repository import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_phone,
    update_user,
)
from services.session_auth_service import issue_session_tokens
from sqlalchemy.orm import Session


def _otp_expires_at(otp_session):
    return getattr(otp_session, "expires_at")


def _otp_attempts(otp_session) -> int:
    return int(getattr(otp_session, "attempts", 0) or 0)


def _otp_code(otp_session) -> str:
    return str(getattr(otp_session, "otp", "") or "")


def _otp_phone(otp_session) -> str:
    return str(getattr(otp_session, "phone", "") or "")


def _otp_is_verified(otp_session) -> bool:
    return bool(getattr(otp_session, "is_verified", False))


def _otp_temp_data(otp_session) -> dict:
    raw = getattr(otp_session, "temp_user_data", None)
    if not raw:
        return {}
    return json.loads(str(raw))


def _serialize_user_profile(user):
    city = getattr(user, "city", None)
    state = getattr(city, "state", None) if city is not None else None

    return {
        "id": getattr(user, "id"),
        "first_name": getattr(user, "first_name"),
        "last_name": getattr(user, "last_name"),
        "email": getattr(user, "email"),
        "phone": getattr(user, "phone"),
        "is_phone_verified": bool(getattr(user, "is_phone_verified", False)),
        "city": (
            {
                "id": getattr(city, "id"),
                "name": getattr(city, "name"),
                "state": (
                    {
                        "id": getattr(state, "id"),
                        "name": getattr(state, "name"),
                    }
                    if state is not None
                    else None
                ),
            }
            if city is not None
            else None
        ),
        "referral_code": getattr(user, "referral_code", None),
    }


# ============ Registration Flow ============


def register_init(db: Session, data):
    existing_phone = get_user_by_phone(db, data.phone)
    if existing_phone:
        raise HTTPException(status_code=400, detail="Phone already registered")

    existing_email = get_user_by_email(db, data.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    state = get_state_by_id(db, data.state_id)
    if not state:
        raise HTTPException(status_code=404, detail="State not found")

    city = get_city_by_id(db, data.city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    if getattr(city, "state_id", None) != data.state_id:
        raise HTTPException(
            status_code=400, detail="City does not belong to the selected state"
        )

    otp = generate_otp()
    expires_at = get_otp_expiry_time(minutes=10)

    temp_user_data = {
        "first_name": data.first_name,
        "last_name": data.last_name,
        "email": data.email,
        "phone": data.phone,
        "state_id": data.state_id,
        "city_id": data.city_id,
        "referral_code": data.referral_code,
    }

    otp_session = create_otp_session(
        db=db,
        phone=data.phone,
        otp=otp,
        purpose="register",
        expires_at=expires_at,
        temp_user_data=json.dumps(temp_user_data),
    )

    return {
        "otp_session_id": getattr(otp_session, "id"),
        "phone": _otp_phone(otp_session),
        "expires_at": _otp_expires_at(otp_session).isoformat(),
        "message": "OTP sent successfully. Please verify within 10 minutes.",
        "otp": otp,
    }


def register_verify(
    db: Session, otp_session_id: int, entered_otp: str, payload, request: Request
):
    otp_session = get_otp_session_by_id(db, otp_session_id)
    if not otp_session:
        raise HTTPException(status_code=404, detail="OTP session not found")

    if is_otp_expired(_otp_expires_at(otp_session)):
        raise HTTPException(
            status_code=400, detail="OTP has expired. Please request a new one."
        )

    if _otp_attempts(otp_session) >= 5:
        delete_otp_session(db, otp_session_id)
        raise HTTPException(
            status_code=400,
            detail="Maximum OTP attempts exceeded. Please request a new OTP.",
        )

    increment_attempts(db, otp_session_id)

    is_development = True
    if not verify_otp(
        entered_otp, _otp_code(otp_session), is_development=is_development
    ):
        raise HTTPException(status_code=400, detail="Invalid OTP. Please try again.")

    temp_user_data = _otp_temp_data(otp_session)

    user = create_user(
        db,
        {
            "first_name": temp_user_data["first_name"],
            "last_name": temp_user_data["last_name"],
            "email": temp_user_data["email"],
            "phone": temp_user_data["phone"],
            "state_id": temp_user_data["state_id"],
            "city_id": temp_user_data["city_id"],
            "referral_code": temp_user_data.get("referral_code"),
            "hashed_password": None,
            "role": "user",
            "is_phone_verified": True,
            "is_active": True,
        },
    )

    update_otp_session(db, otp_session_id, is_verified=True)

    return issue_session_tokens(
        db,
        entity=user,
        role="user",
        entity_type="user",
        session_type="mobile",
        request=request,
        device_id=getattr(payload, "device_id", None),
        device_name=getattr(payload, "device_name", None),
        device_platform=getattr(payload, "device_platform", None),
    )


# ============ Login Flow ============


def login_send_otp(db: Session, phone: str):
    user = get_user_by_phone(db, phone)
    if not user:
        raise HTTPException(
            status_code=404, detail="User not found. Please register first."
        )

    if not bool(getattr(user, "is_phone_verified", False)):
        raise HTTPException(
            status_code=400,
            detail="Phone number not verified. Please complete registration.",
        )

    if not bool(getattr(user, "is_active", True)):
        raise HTTPException(status_code=403, detail="User account is inactive")

    otp = generate_otp()
    expires_at = get_otp_expiry_time(minutes=10)

    otp_session = create_otp_session(
        db=db, phone=phone, otp=otp, purpose="login", expires_at=expires_at
    )

    return {
        "otp_session_id": getattr(otp_session, "id"),
        "phone": _otp_phone(otp_session),
        "expires_at": _otp_expires_at(otp_session).isoformat(),
        "message": "OTP sent successfully. Please verify within 10 minutes.",
        "otp": otp,
    }


def login_verify(
    db: Session, otp_session_id: int, entered_otp: str, payload, request: Request
):
    otp_session = get_otp_session_by_id(db, otp_session_id)
    if not otp_session:
        raise HTTPException(status_code=404, detail="OTP session not found")

    if is_otp_expired(_otp_expires_at(otp_session)):
        raise HTTPException(
            status_code=400, detail="OTP has expired. Please request a new one."
        )

    if _otp_attempts(otp_session) >= 5:
        delete_otp_session(db, otp_session_id)
        raise HTTPException(
            status_code=400,
            detail="Maximum OTP attempts exceeded. Please request a new OTP.",
        )

    increment_attempts(db, otp_session_id)

    is_development = True
    if not verify_otp(
        entered_otp, _otp_code(otp_session), is_development=is_development
    ):
        raise HTTPException(status_code=400, detail="Invalid OTP. Please try again.")

    user = get_user_by_phone(db, _otp_phone(otp_session))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not bool(getattr(user, "is_active", True)):
        raise HTTPException(status_code=403, detail="User account is inactive")

    update_otp_session(db, otp_session_id, is_verified=True)

    return issue_session_tokens(
        db,
        entity=user,
        role=str(getattr(user, "role", "user")),
        entity_type="user",
        session_type="mobile",
        request=request,
        device_id=getattr(payload, "device_id", None),
        device_name=getattr(payload, "device_name", None),
        device_platform=getattr(payload, "device_platform", None),
    )


# ============ Resend OTP ============


def resend_otp(db: Session, otp_session_id: int):
    otp_session = get_otp_session_by_id(db, otp_session_id)
    if not otp_session:
        raise HTTPException(status_code=404, detail="OTP session not found")

    if _otp_is_verified(otp_session):
        raise HTTPException(status_code=400, detail="OTP already verified")

    new_otp = generate_otp()
    new_expires_at = get_otp_expiry_time(minutes=10)

    update_otp_session(
        db=db,
        otp_session_id=otp_session_id,
        otp=new_otp,
        expires_at=new_expires_at,
        attempts=0,
    )

    return {
        "otp_session_id": otp_session_id,
        "phone": _otp_phone(otp_session),
        "expires_at": new_expires_at.isoformat(),
        "message": "New OTP sent successfully. Please verify within 10 minutes.",
        "otp": new_otp,
    }


# ============ Change Phone Number During Registration ============


def update_phone_during_registration(db: Session, otp_session_id: int, new_phone: str):
    otp_session = get_otp_session_by_id(db, otp_session_id)
    if not otp_session:
        raise HTTPException(status_code=404, detail="OTP session not found")

    if _otp_is_verified(otp_session):
        raise HTTPException(
            status_code=400, detail="OTP already verified. Cannot change phone number."
        )

    existing_user = get_user_by_phone(db, new_phone)
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    new_otp = generate_otp()
    new_expires_at = get_otp_expiry_time(minutes=10)

    update_otp_session(
        db=db,
        otp_session_id=otp_session_id,
        phone=new_phone,
        otp=new_otp,
        expires_at=new_expires_at,
        attempts=0,
    )

    return {
        "otp_session_id": otp_session_id,
        "phone": new_phone,
        "expires_at": new_expires_at.isoformat(),
        "message": "OTP sent to new phone number. Please verify within 10 minutes.",
        "otp": new_otp,
    }


# ============ Profile Management ============


def get_user_profile(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return _serialize_user_profile(user)


def update_user_profile(db: Session, user_id: int, data):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    next_email = getattr(data, "email", None)
    if next_email and next_email != getattr(user, "email", None):
        existing_email = get_user_by_email(db, next_email)
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")

    next_state_id = getattr(data, "state_id", None)
    next_city_id = getattr(data, "city_id", None)
    if next_state_id is not None or next_city_id is not None:
        target_state_id = next_state_id or getattr(user, "state_id", None)
        target_city_id = next_city_id or getattr(user, "city_id", None)

        if target_state_id is not None:
            state = get_state_by_id(db, int(target_state_id))
            if not state:
                raise HTTPException(status_code=404, detail="State not found")

        if target_city_id is not None:
            city = get_city_by_id(db, int(target_city_id))
            if not city:
                raise HTTPException(status_code=404, detail="City not found")
            if target_state_id is not None and getattr(city, "state_id", None) != int(
                target_state_id
            ):
                raise HTTPException(
                    status_code=400,
                    detail="City does not belong to the selected state",
                )

    update_data = {}
    if getattr(data, "first_name", None):
        update_data["first_name"] = data.first_name
    if getattr(data, "last_name", None):
        update_data["last_name"] = data.last_name
    if next_email:
        update_data["email"] = next_email
    if next_state_id is not None:
        update_data["state_id"] = next_state_id
    if next_city_id is not None:
        update_data["city_id"] = next_city_id

    updated_user = update_user(db, user, update_data)
    return _serialize_user_profile(updated_user)


def change_phone_init(db: Session, user_id: int, new_phone: str):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_user = get_user_by_phone(db, new_phone)
    if existing_user and getattr(existing_user, "id", None) != user_id:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    otp = generate_otp()
    expires_at = get_otp_expiry_time(minutes=10)
    temp_data = {
        "user_id": user_id,
        "old_phone": getattr(user, "phone", None),
        "new_phone": new_phone,
    }

    otp_session = create_otp_session(
        db=db,
        phone=new_phone,
        otp=otp,
        purpose="change_phone",
        expires_at=expires_at,
        temp_user_data=json.dumps(temp_data),
    )

    return {
        "otp_session_id": getattr(otp_session, "id"),
        "phone": new_phone,
        "expires_at": _otp_expires_at(otp_session).isoformat(),
        "message": "OTP sent to new phone number. Please verify within 10 minutes.",
        "otp": otp,
    }


def change_phone_verify(db: Session, otp_session_id: int, entered_otp: str):
    otp_session = get_otp_session_by_id(db, otp_session_id)
    if not otp_session:
        raise HTTPException(status_code=404, detail="OTP session not found")

    if is_otp_expired(_otp_expires_at(otp_session)):
        raise HTTPException(
            status_code=400, detail="OTP has expired. Please request a new one."
        )

    if _otp_attempts(otp_session) >= 5:
        delete_otp_session(db, otp_session_id)
        raise HTTPException(
            status_code=400,
            detail="Maximum OTP attempts exceeded. Please request a new OTP.",
        )

    increment_attempts(db, otp_session_id)

    is_development = True
    if not verify_otp(
        entered_otp, _otp_code(otp_session), is_development=is_development
    ):
        raise HTTPException(status_code=400, detail="Invalid OTP. Please try again.")

    temp_data = _otp_temp_data(otp_session)
    user_id = int(temp_data["user_id"])
    new_phone = str(temp_data["new_phone"])

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = update_user(db, user, {"phone": new_phone})
    update_otp_session(db, otp_session_id, is_verified=True)

    return _serialize_user_profile(updated_user)
