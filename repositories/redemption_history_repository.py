from datetime import datetime
from typing import Optional

from db.models.business import Business
from db.models.redemption_history import RedemptionHistory
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session, joinedload


def get_redemption_by_id(db: Session, redemption_id: int):
    return (
        db.query(RedemptionHistory)
        .filter(RedemptionHistory.id == redemption_id)
        .first()
    )


def get_user_redemptions_today(db: Session, user_id: int, user_subscription_id: int):
    """Get count of redemptions for a user today"""
    today = datetime.utcnow().date()
    return (
        db.query(RedemptionHistory)
        .filter(
            and_(
                RedemptionHistory.user_id == user_id,
                RedemptionHistory.user_subscription_id == user_subscription_id,
                RedemptionHistory.status == "success",
                func.date(RedemptionHistory.redeemed_at) == today,
            )
        )
        .count()
    )


def get_user_redemptions_total(db: Session, user_id: int, user_subscription_id: int):
    """Get total count of redemptions for a user in current subscription"""
    return (
        db.query(RedemptionHistory)
        .filter(
            and_(
                RedemptionHistory.user_id == user_id,
                RedemptionHistory.user_subscription_id == user_subscription_id,
                RedemptionHistory.status == "success",
            )
        )
        .count()
    )


def create_redemption(db: Session, redemption_data: dict):
    redemption = RedemptionHistory(**redemption_data)
    db.add(redemption)
    db.commit()
    db.refresh(redemption)
    return redemption


def get_redemption_history(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    user_id: Optional[int] = None,
    business_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    """Get redemption history with filters and pagination"""
    query = db.query(RedemptionHistory).options(
        joinedload(RedemptionHistory.user),
        joinedload(RedemptionHistory.business),
        joinedload(RedemptionHistory.coupon),
    )

    if user_id:
        query = query.filter(RedemptionHistory.user_id == user_id)
    if business_id:
        query = query.filter(RedemptionHistory.business_id == business_id)
    if status:
        query = query.filter(RedemptionHistory.status == status)
    if start_date:
        query = query.filter(RedemptionHistory.redeemed_at >= start_date)
    if end_date:
        query = query.filter(RedemptionHistory.redeemed_at <= end_date)

    total = query.count()
    redemptions = (
        query.order_by(desc(RedemptionHistory.redeemed_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return redemptions, total


def get_total_redemptions_count(db: Session):
    """Get total redemptions count"""
    return (
        db.query(RedemptionHistory)
        .filter(RedemptionHistory.status == "success")
        .count()
    )


def get_today_redemptions_count(db: Session):
    """Get today's redemptions count"""
    today = datetime.utcnow().date()
    return (
        db.query(RedemptionHistory)
        .filter(
            and_(
                RedemptionHistory.status == "success",
                func.date(RedemptionHistory.redeemed_at) == today,
            )
        )
        .count()
    )


def get_top_redeemed_businesses(db: Session, limit: int = 5):
    """Get top redeemed businesses"""
    return (
        db.query(
            RedemptionHistory.business_id,
            func.count(RedemptionHistory.id).label("redemption_count"),
        )
        .filter(RedemptionHistory.status == "success")
        .group_by(RedemptionHistory.business_id)
        .order_by(desc(func.count(RedemptionHistory.id)))
        .limit(limit)
        .all()
    )


def get_vendor_redemption_history(
    db: Session,
    owner_id: int,
    skip: int = 0,
    limit: int = 10,
    business_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    query = (
        db.query(RedemptionHistory)
        .join(Business, Business.id == RedemptionHistory.business_id)
        .options(
            joinedload(RedemptionHistory.user),
            joinedload(RedemptionHistory.business),
            joinedload(RedemptionHistory.coupon),
        )
        .filter(Business.owner_id == owner_id)
    )

    if business_id:
        query = query.filter(RedemptionHistory.business_id == business_id)
    if status:
        query = query.filter(RedemptionHistory.status == status)
    if start_date:
        query = query.filter(RedemptionHistory.redeemed_at >= start_date)
    if end_date:
        query = query.filter(RedemptionHistory.redeemed_at <= end_date)

    total = query.count()
    redemptions = (
        query.order_by(desc(RedemptionHistory.redeemed_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return redemptions, total


def get_vendor_total_redemptions_count(db: Session, owner_id: int):
    return (
        db.query(RedemptionHistory)
        .join(Business, Business.id == RedemptionHistory.business_id)
        .filter(
            and_(
                Business.owner_id == owner_id,
                RedemptionHistory.status == "success",
            )
        )
        .count()
    )


def get_vendor_today_redemptions_count(db: Session, owner_id: int):
    today = datetime.utcnow().date()
    return (
        db.query(RedemptionHistory)
        .join(Business, Business.id == RedemptionHistory.business_id)
        .filter(
            and_(
                Business.owner_id == owner_id,
                RedemptionHistory.status == "success",
                func.date(RedemptionHistory.redeemed_at) == today,
            )
        )
        .count()
    )


def get_vendor_top_redeemed_businesses(db: Session, owner_id: int, limit: int = 5):
    return (
        db.query(
            RedemptionHistory.business_id,
            func.count(RedemptionHistory.id).label("redemption_count"),
        )
        .join(Business, Business.id == RedemptionHistory.business_id)
        .filter(
            and_(
                Business.owner_id == owner_id,
                RedemptionHistory.status == "success",
            )
        )
        .group_by(RedemptionHistory.business_id)
        .order_by(desc(func.count(RedemptionHistory.id)))
        .limit(limit)
        .all()
    )
