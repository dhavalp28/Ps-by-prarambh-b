from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Optional

from fastapi import HTTPException, status
from repositories import business_repository, coupon_repository
from schemas.coupon import CouponCreate, CouponUpdate
from sqlalchemy.orm import Session

WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def _serialize_business(business: Any):
    return {
        "id": business.id,
        "business_name": business.business_name,
        "is_active": bool(business.is_active),
    }


def _parse_not_valid_on(raw_value: Optional[str]) -> list[str]:
    if not raw_value:
        return []
    return [day for day in raw_value.split(",") if day]


def _stringify_not_valid_on(days: list[str]) -> Optional[str]:
    return ",".join(days) if days else None


def get_effective_expiry_date(coupon: Any) -> Optional[date]:
    if coupon.valid_till:
        return coupon.valid_till

    if coupon.validity_days:
        created_at = coupon.created_at or datetime.utcnow()
        return created_at.date() + timedelta(days=max(coupon.validity_days - 1, 0))

    return None


def is_coupon_expired(coupon: Any, reference_date: Optional[date] = None) -> bool:
    expiry_date = get_effective_expiry_date(coupon)
    if expiry_date is None:
        return False
    return (reference_date or date.today()) > expiry_date


def get_coupon_redeemability(coupon: Any, reference_date: Optional[date] = None):
    if not bool(coupon.is_active):
        return False, "Coupon is inactive"

    if not coupon.business or not bool(coupon.business.is_active):
        return False, "Business is inactive"

    if is_coupon_expired(coupon, reference_date=reference_date):
        return False, "Coupon has expired"

    current_day = WEEKDAYS[(reference_date or date.today()).weekday()]
    blocked_days = _parse_not_valid_on(coupon.not_valid_on)
    if current_day in blocked_days:
        return False, f"Coupon is not valid on {current_day}"

    if int(coupon.redemption_count or 0) >= int(coupon.max_redemption_count or 0):
        return False, "Coupon redemption limit reached"

    return True, None


def serialize_coupon(coupon: Any) -> dict:
    is_redeemable, _ = get_coupon_redeemability(coupon)
    return {
        "id": coupon.id,
        "business_id": coupon.business_id,
        "business": _serialize_business(coupon.business),
        "coupon_name": coupon.coupon_name,
        "discount": float(coupon.discount or Decimal("0")),
        "description": coupon.description,
        "valid_till": coupon.valid_till,
        "validity_days": coupon.validity_days,
        "max_redemption_count": coupon.max_redemption_count,
        "redemption_count": coupon.redemption_count,
        "remaining_redemptions": max(
            int(coupon.max_redemption_count or 0) - int(coupon.redemption_count or 0),
            0,
        ),
        "is_active": coupon.is_active,
        "status": "Active" if coupon.is_active else "Inactive",
        "not_valid_on": _parse_not_valid_on(coupon.not_valid_on),
        "is_expired": is_coupon_expired(coupon),
        "can_redeem": is_redeemable,
        "effective_expiry_date": get_effective_expiry_date(coupon),
        "created_at": coupon.created_at,
        "updated_at": coupon.updated_at,
    }


def _ensure_business_exists(db: Session, business_id: int) -> Any:
    business = business_repository.get_business_by_id(db, business_id)
    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business not found"
        )
    return business


def _validate_validity_fields(valid_till, validity_days):
    if valid_till and validity_days:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use either Valid Till or Validity Days, not both",
        )


def get_all_coupons(
    db: Session,
    business_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
):
    return coupon_repository.get_all_coupons(
        db, business_id=business_id, is_active=is_active, search=search
    )


def get_coupon(db: Session, coupon_id: int) -> Any:
    coupon = coupon_repository.get_coupon_by_id(db, coupon_id)
    if coupon is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Coupon not found"
        )
    return coupon


def create_coupon(db: Session, payload: CouponCreate):
    _ensure_business_exists(db, payload.business_id)
    _validate_validity_fields(payload.valid_till, payload.validity_days)

    existing = coupon_repository.get_coupon_by_business_and_name(
        db, payload.business_id, payload.coupon_name
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon with this name already exists for the selected business",
        )

    coupon = coupon_repository.create_coupon(
        db,
        {
            "business_id": payload.business_id,
            "coupon_name": payload.coupon_name,
            "discount": payload.discount,
            "description": payload.description,
            "valid_till": payload.valid_till,
            "validity_days": payload.validity_days,
            "max_redemption_count": payload.max_redemption_count,
            "redemption_count": 0,
            "is_active": payload.is_active,
            "not_valid_on": _stringify_not_valid_on(payload.not_valid_on),
        },
    )
    created_coupon_id = int(coupon.__dict__.get("id", 0))
    return get_coupon(db, created_coupon_id)


def update_coupon(db: Session, coupon_id: int, payload: CouponUpdate):
    coupon = get_coupon(db, coupon_id)
    update_data = payload.model_dump(exclude_unset=True)

    next_business_id = update_data.get("business_id", coupon.business_id)
    next_coupon_name = update_data.get("coupon_name", coupon.coupon_name)
    next_valid_till = update_data.get("valid_till", coupon.valid_till)
    next_validity_days = update_data.get("validity_days", coupon.validity_days)
    next_max_redemption_count = update_data.get(
        "max_redemption_count", coupon.max_redemption_count
    )

    _ensure_business_exists(db, next_business_id)
    _validate_validity_fields(next_valid_till, next_validity_days)

    existing = coupon_repository.get_coupon_by_business_and_name(
        db, next_business_id, next_coupon_name
    )
    if existing is not None and existing.id != coupon.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon with this name already exists for the selected business",
        )

    if int(coupon.redemption_count or 0) > int(next_max_redemption_count):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Max redemption count cannot be less than current redemption count",
        )

    if "not_valid_on" in update_data:
        update_data["not_valid_on"] = _stringify_not_valid_on(
            update_data.get("not_valid_on") or []
        )

    coupon_repository.update_coupon(db, coupon, update_data)
    return get_coupon(db, coupon_id)


def delete_coupon(db: Session, coupon_id: int):
    coupon = get_coupon(db, coupon_id)
    coupon_repository.delete_coupon(db, coupon)
    return coupon


def toggle_active(db: Session, coupon_id: int):
    coupon = get_coupon(db, coupon_id)
    coupon_repository.update_coupon(db, coupon, {"is_active": not coupon.is_active})
    return get_coupon(db, coupon_id)


def validate_coupon_for_redemption(
    db: Session,
    coupon_id: int,
    business_id: Optional[int] = None,
    reference_date: Optional[date] = None,
):
    coupon = get_coupon(db, coupon_id)

    if business_id is not None and coupon.business_id != business_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon does not belong to this business",
        )

    is_redeemable, message = get_coupon_redeemability(
        coupon, reference_date=reference_date
    )
    if not is_redeemable:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    return coupon


def increment_coupon_redemption(db: Session, coupon_id: int):
    coupon = get_coupon(db, coupon_id)
    is_redeemable, message = get_coupon_redeemability(coupon)
    if not is_redeemable:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    coupon_repository.update_coupon(
        db, coupon, {"redemption_count": int(coupon.redemption_count or 0) + 1}
    )
    return get_coupon(db, coupon_id)
