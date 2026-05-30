from datetime import datetime
from typing import Any

from fastapi import HTTPException
from repositories.business_code_repository import get_business_code_by_code
from repositories.redemption_history_repository import (
    create_redemption,
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


def redeem_coupon(
    db: Session, user_id: int, business_code: str, coupon_id: int | None = None
):
    """Redeem a coupon for a user at a business"""

    # Validate business code
    code_validation = validate_business_code(db, business_code)
    if not code_validation["valid"]:
        raise HTTPException(status_code=400, detail=code_validation["message"])

    business_id = int(code_validation["business_id"])

    # Get business code object
    business_code_obj: Any = get_business_code_by_code(db, business_code)

    applied_coupon: Any = None
    if coupon_id is not None:
        applied_coupon = coupon_service.validate_coupon_for_redemption(
            db, coupon_id, business_id=business_id
        )

    # Check user subscription
    subscription: Any = get_active_user_subscription(db, user_id)
    if not subscription:
        raise HTTPException(status_code=400, detail="No active subscription found")

    is_valid, message = check_subscription_validity(db, user_id)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    # Get subscription plan limits
    plan = subscription.subscription_plan
    daily_limit = plan.daily_coupon_limit
    total_limit = plan.total_coupon_limit

    # Check daily limit
    today_count = get_user_redemptions_today(db, user_id, subscription.id)
    if today_count >= daily_limit:
        raise HTTPException(status_code=400, detail="Daily redemption limit exceeded")

    # Check total limit
    total_count = get_user_redemptions_total(db, user_id, subscription.id)
    if total_count >= total_limit:
        raise HTTPException(status_code=400, detail="Total redemption limit exceeded")

    # Calculate remaining limits
    remaining_daily = daily_limit - today_count - 1
    remaining_total = total_limit - total_count - 1

    # Create redemption entry
    redemption_data = {
        "user_id": user_id,
        "business_id": business_id,
        "business_code_id": business_code_obj.id,
        "user_subscription_id": subscription.id,
        "status": "success",
        "remaining_daily_limit": remaining_daily,
        "remaining_total_limit": remaining_total,
    }

    redemption = create_redemption(db, redemption_data)

    if applied_coupon is not None:
        applied_coupon = coupon_service.increment_coupon_redemption(
            db, applied_coupon.id
        )

    return {
        "success": True,
        "message": "Coupon redeemed successfully",
        "redemption_id": redemption.id,
        "business_name": business_code_obj.business.business_name,
        "remaining_daily_limit": remaining_daily,
        "remaining_total_limit": remaining_total,
        "coupon": (
            {
                "id": applied_coupon.id,
                "coupon_name": applied_coupon.coupon_name,
                "discount": float(applied_coupon.discount),
                "remaining_redemptions": max(
                    int(applied_coupon.max_redemption_count)
                    - int(applied_coupon.redemption_count),
                    0,
                ),
            }
            if applied_coupon is not None
            else None
        ),
    }


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
        }

    today_count = get_user_redemptions_today(db, user_id, subscription.id)
    total_count = get_user_redemptions_total(db, user_id, subscription.id)

    plan = subscription.subscription_plan

    return {
        "total_redeemed_today": today_count,
        "total_redeemed_all_time": total_count,
        "remaining_daily_limit": max(0, plan.daily_coupon_limit - today_count),
        "remaining_total_limit": max(0, plan.total_coupon_limit - total_count),
        "subscription_expires_at": subscription.expires_at,
        "is_subscription_active": subscription.is_active
        and subscription.expires_at > datetime.utcnow(),
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
