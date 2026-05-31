from datetime import datetime
from typing import Any

from db.models.redemption_history import RedemptionHistory
from fastapi import HTTPException, status
from repositories.business_code_repository import get_business_code_by_code
from repositories.redemption_history_repository import (
    get_redemption_history,
    get_today_redemptions_count,
    get_top_redeemed_businesses,
    get_total_redemptions_count,
    get_user_redemptions_today,
    get_user_redemptions_total,
)
from repositories.user_subscription_repository import get_active_user_subscription
from services import coupon_service
from services.business_code_service import validate_business_code
from services.user_subscription_service import check_subscription_validity
from sqlalchemy.orm import Session


def _get_valid_subscription(db: Session, user_id: int):
    is_valid, message = check_subscription_validity(db, user_id)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    subscription = get_active_user_subscription(db, user_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription found",
        )

    return subscription


def _get_subscription_usage(db: Session, user_id: int, subscription: Any):
    today = datetime.utcnow().date()

    history_today_count = get_user_redemptions_today(db, user_id, subscription.id)
    history_total_count = get_user_redemptions_total(db, user_id, subscription.id)

    stored_daily_count = (
        int(subscription.daily_redemption_count or 0)
        if subscription.last_redeemed_on == today
        else 0
    )
    stored_total_count = int(subscription.total_redemption_count or 0)

    return {
        "today": max(history_today_count, stored_daily_count),
        "total": max(history_total_count, stored_total_count),
        "today_date": today,
    }


def _validate_subscription_limits(subscription: Any, usage: dict[str, Any]):
    plan = subscription.subscription_plan
    daily_limit = int(plan.daily_coupon_limit or 0)
    total_limit = int(plan.total_coupon_limit or 0)

    today_count = int(usage["today"])
    total_count = int(usage["total"])

    if today_count >= daily_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Daily redemption limit exceeded",
        )

    if total_count >= total_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total redemption limit exceeded",
        )

    return {
        "daily_limit": daily_limit,
        "total_limit": total_limit,
        "today_count": today_count,
        "total_count": total_count,
        "remaining_daily": daily_limit - today_count - 1,
        "remaining_total": total_limit - total_count - 1,
    }


def _build_coupon_payload(coupon: Any):
    if coupon is None:
        return None

    return {
        "id": coupon.id,
        "coupon_name": coupon.coupon_name,
        "discount": float(coupon.discount),
        "is_active": bool(coupon.is_active),
    }


def _finalize_redemption(
    db: Session,
    user_id: int,
    business_id: int,
    business_code_obj: Any,
    coupon: Any | None = None,
):
    subscription = _get_valid_subscription(db, user_id)
    usage = _get_subscription_usage(db, user_id, subscription)
    limits = _validate_subscription_limits(subscription, usage)

    try:
        redemption = RedemptionHistory(
            user_id=user_id,
            business_id=business_id,
            business_code_id=business_code_obj.id,
            user_subscription_id=subscription.id,
            coupon_id=(coupon.id if coupon is not None else None),
            claim_reference=(coupon.id if coupon is not None else None),
            status="success",
            remaining_daily_limit=limits["remaining_daily"],
            remaining_total_limit=limits["remaining_total"],
        )
        db.add(redemption)

        if coupon is not None:
            coupon.redemption_count = int(coupon.redemption_count or 0) + 1

        setattr(subscription, "daily_redemption_count", limits["today_count"] + 1)
        setattr(subscription, "total_redemption_count", limits["total_count"] + 1)
        setattr(subscription, "last_redeemed_on", usage["today_date"])

        db.commit()
        db.refresh(redemption)
        if coupon is not None:
            db.refresh(coupon)
        db.refresh(subscription)
    except Exception:
        db.rollback()
        raise

    return {
        "success": True,
        "message": "Coupon redeemed successfully",
        "redemption_id": redemption.id,
        "claim_reference": coupon.id if coupon is not None else None,
        "coupon_id": coupon.id if coupon is not None else None,
        "business_id": business_id,
        "business_name": business_code_obj.business.business_name,
        "remaining_daily_limit": limits["remaining_daily"],
        "remaining_total_limit": limits["remaining_total"],
        "daily_redemption_count": int(
            getattr(subscription, "daily_redemption_count", 0) or 0
        ),
        "total_redemption_count": int(
            getattr(subscription, "total_redemption_count", 0) or 0
        ),
        "coupon": _build_coupon_payload(coupon),
    }


def claim_coupon(
    db: Session,
    user_id: int,
    business_id: int,
    coupon_id: int,
    business_code: str,
):
    code_validation = validate_business_code(db, business_code)
    if not code_validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=code_validation["message"],
        )

    scanned_business_id = int(code_validation["business_id"])
    if scanned_business_id != business_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scanned QR code does not belong to the selected business",
        )

    business_code_obj = get_business_code_by_code(db, business_code)
    if business_code_obj is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business code not found",
        )

    coupon = coupon_service.validate_coupon_for_redemption(
        db, coupon_id, business_id=business_id
    )

    return _finalize_redemption(
        db,
        user_id=user_id,
        business_id=business_id,
        business_code_obj=business_code_obj,
        coupon=coupon,
    )


def get_user_redemption_summary(db: Session, user_id: int):
    """Get redemption summary for a user"""
    subscription: Any = get_active_user_subscription(db, user_id)

    if not subscription:
        return {
            "total_redeemed_today": 0,
            "total_redeemed_all_time": 0,
            "remaining_daily_limit": 0,
            "remaining_total_limit": 0,
            "subscription_expires_at": None,
            "is_subscription_active": False,
            "daily_redemption_count": 0,
            "total_redemption_count": 0,
            "last_redeemed_on": None,
        }

    usage = _get_subscription_usage(db, user_id, subscription)
    today_count = int(usage["today"])
    total_count = int(usage["total"])
    plan = subscription.subscription_plan

    return {
        "total_redeemed_today": today_count,
        "total_redeemed_all_time": total_count,
        "remaining_daily_limit": max(
            0, int(plan.daily_coupon_limit or 0) - today_count
        ),
        "remaining_total_limit": max(
            0, int(plan.total_coupon_limit or 0) - total_count
        ),
        "subscription_expires_at": subscription.expires_at,
        "is_subscription_active": subscription.is_active
        and subscription.expires_at > datetime.utcnow(),
        "daily_redemption_count": int(
            getattr(subscription, "daily_redemption_count", 0) or 0
        )
        if getattr(subscription, "last_redeemed_on", None) == usage["today_date"]
        else 0,
        "total_redemption_count": int(
            getattr(subscription, "total_redemption_count", 0) or 0
        ),
        "last_redeemed_on": getattr(subscription, "last_redeemed_on", None),
    }


def get_redemptions_with_filters(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    user_id: int | None = None,
    business_id: int | None = None,
    status: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
):
    """Get redemption history with filters"""
    redemptions, total = get_redemption_history(
        db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        business_id=business_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )

    return redemptions, total


def get_analytics(db: Session):
    """Get redemption analytics"""
    total_redemptions = get_total_redemptions_count(db)
    today_redemptions = get_today_redemptions_count(db)

    # Get active subscriptions count
    from db.models.user_subscription import UserSubscription
    from sqlalchemy import and_

    active_subscriptions = (
        db.query(UserSubscription)
        .filter(
            and_(
                UserSubscription.is_active,
                UserSubscription.expires_at > datetime.utcnow(),
            )
        )
        .count()
    )

    # Get top redeemed businesses
    top_businesses_data = get_top_redeemed_businesses(db, limit=5)

    top_businesses = []
    for business_id, count in top_businesses_data:
        from repositories.business_repository import get_business_by_id

        business = get_business_by_id(db, business_id)
        if business:
            top_businesses.append(
                {
                    "business_id": business_id,
                    "business_name": business.business_name,
                    "redemption_count": count,
                }
            )

    return {
        "total_redemptions": total_redemptions,
        "today_redemptions": today_redemptions,
        "active_subscriptions": active_subscriptions,
        "top_redeemed_businesses": top_businesses,
    }
