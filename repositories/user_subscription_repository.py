from typing import List, Optional

from db.models.user_subscription import UserSubscription
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session


def get_user_subscription_by_id(db: Session, subscription_id: int):
    return (
        db.query(UserSubscription)
        .filter(UserSubscription.id == subscription_id)
        .first()
    )


def get_active_user_subscription(db: Session, user_id: int):
    """Get the active subscription for a user"""
    return (
        db.query(UserSubscription)
        .filter(
            and_(
                UserSubscription.user_id == user_id, UserSubscription.is_active == True
            )
        )
        .order_by(desc(UserSubscription.created_at))
        .first()
    )


def get_user_subscriptions(db: Session, user_id: int):
    """Get all subscriptions for a user"""
    return (
        db.query(UserSubscription)
        .filter(UserSubscription.user_id == user_id)
        .order_by(desc(UserSubscription.created_at))
        .all()
    )


def deactivate_user_subscriptions(db: Session, user_id: int):
    subscriptions = (
        db.query(UserSubscription)
        .filter(
            and_(
                UserSubscription.user_id == user_id, UserSubscription.is_active == True
            )
        )
        .all()
    )
    for subscription in subscriptions:
        subscription.is_active = False
    db.commit()
    return subscriptions


def create_user_subscription(db: Session, subscription_data: dict):
    subscription = UserSubscription(**subscription_data)
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


def update_user_subscription(
    db: Session, subscription: UserSubscription, update_data: dict
):
    for key, value in update_data.items():
        if value is not None:
            setattr(subscription, key, value)
    db.commit()
    db.refresh(subscription)
    return subscription


def delete_user_subscription(db: Session, subscription: UserSubscription):
    db.delete(subscription)
    db.commit()
