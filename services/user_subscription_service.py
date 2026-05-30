from datetime import datetime, timedelta

from fastapi import HTTPException
from repositories.user_subscription_repository import (
    create_user_subscription,
    deactivate_user_subscriptions,
    get_active_user_subscription,
    get_user_subscription_by_id,
    get_user_subscriptions,
    update_user_subscription,
)
from sqlalchemy.orm import Session


def get_active_subscription(db: Session, user_id: int):
    """Get active subscription for a user"""
    subscription = get_active_user_subscription(db, user_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    return subscription


def check_subscription_validity(db: Session, user_id: int):
    """Check if user has a valid active subscription"""
    subscription = get_active_user_subscription(db, user_id)

    if not subscription:
        return False, "No active subscription"

    if not subscription.is_active:
        return False, "Subscription is inactive"

    if subscription.expires_at < datetime.utcnow():
        # Mark as expired
        update_user_subscription(db, subscription, {"is_active": False})
        return False, "Subscription has expired"

    return True, "Subscription is valid"


def get_subscription_details(db: Session, user_id: int):
    """Get subscription details for a user"""
    subscription = get_active_user_subscription(db, user_id)

    if not subscription:
        return None

    days_remaining = (subscription.expires_at - datetime.utcnow()).days
    is_expired = subscription.expires_at < datetime.utcnow()

    return {
        "id": subscription.id,
        "user_id": subscription.user_id,
        "purchased_at": subscription.purchased_at,
        "expires_at": subscription.expires_at,
        "is_active": subscription.is_active,
        "subscription_plan": {
            "id": subscription.subscription_plan.id,
            "plan_name": subscription.subscription_plan.plan_name,
            "daily_coupon_limit": subscription.subscription_plan.daily_coupon_limit,
            "total_coupon_limit": subscription.subscription_plan.total_coupon_limit,
        },
        "days_remaining": max(0, days_remaining),
        "is_expired": is_expired,
    }


def create_subscription(
    db: Session, user_id: int, subscription_plan_id: int, validity_days: int
):
    """Create a new subscription for a user"""
    deactivate_user_subscriptions(db, user_id)
    subscription_data = {
        "user_id": user_id,
        "subscription_plan_id": subscription_plan_id,
        "expires_at": datetime.utcnow() + timedelta(days=validity_days),
        "is_active": True,
    }
    return create_user_subscription(db, subscription_data)


def get_user_subscription_history(db: Session, user_id: int):
    return get_user_subscriptions(db, user_id)
