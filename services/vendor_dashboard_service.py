from datetime import datetime

from repositories.business_repository import get_businesses_by_owner_id
from repositories.redemption_history_repository import (
    get_vendor_redemption_history,
    get_vendor_today_redemptions_count,
    get_vendor_top_redeemed_businesses,
    get_vendor_total_redemptions_count,
)
from sqlalchemy.orm import Session


def get_vendor_businesses(db: Session, vendor_id: int):
    return get_businesses_by_owner_id(db, vendor_id)


def get_vendor_summary(db: Session, vendor):
    businesses = get_businesses_by_owner_id(db, vendor.id)
    total_businesses = len(businesses)
    active_businesses = len([b for b in businesses if b.is_active])
    inactive_businesses = total_businesses - active_businesses

    return {
        "vendor_id": vendor.id,
        "vendor_name": vendor.name,
        "total_businesses": total_businesses,
        "active_businesses": active_businesses,
        "inactive_businesses": inactive_businesses,
        "total_redemptions": get_vendor_total_redemptions_count(db, vendor.id),
        "today_redemptions": get_vendor_today_redemptions_count(db, vendor.id),
    }


def get_vendor_redemptions(
    db: Session,
    vendor_id: int,
    skip: int = 0,
    limit: int = 10,
    business_id: int | None = None,
    status: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
):
    return get_vendor_redemption_history(
        db,
        owner_id=vendor_id,
        skip=skip,
        limit=limit,
        business_id=business_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )


def get_vendor_analytics(db: Session, vendor):
    summary = get_vendor_summary(db, vendor)
    businesses = {
        b.id: b.business_name for b in get_businesses_by_owner_id(db, vendor.id)
    }
    top_rows = get_vendor_top_redeemed_businesses(db, vendor.id)

    top_businesses = [
        {
            "business_id": business_id,
            "business_name": businesses.get(business_id, "Unknown Business"),
            "redemption_count": redemption_count,
        }
        for business_id, redemption_count in top_rows
    ]

    return {
        "summary": summary,
        "top_businesses": top_businesses,
    }
