from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from routers.deps import get_current_vendor, get_db
from schemas.vendor_dashboard import (
    VendorBusinessListItem,
    VendorDashboardAnalyticsResponse,
    VendorDashboardSummaryResponse,
    VendorRedemptionHistoryItem,
    VendorRedemptionHistoryResponse,
)
from services import vendor_dashboard_service
from sqlalchemy.orm import Session
from utils.response import error_server, success_list

router = APIRouter()


@router.get("/summary")
def get_summary(
    current_vendor=Depends(get_current_vendor), db: Session = Depends(get_db)
):
    try:
        summary = vendor_dashboard_service.get_vendor_summary(db, current_vendor)
        return success_list(
            title="Vendor Dashboard Summary",
            data=VendorDashboardSummaryResponse(**summary),
        )
    except Exception as e:
        return error_server(title="Vendor Dashboard Summary", error=str(e))


@router.get("/businesses")
def get_businesses(
    current_vendor=Depends(get_current_vendor), db: Session = Depends(get_db)
):
    try:
        businesses = vendor_dashboard_service.get_vendor_businesses(
            db, current_vendor.id
        )
        return success_list(
            title="Vendor Businesses",
            data=[VendorBusinessListItem.model_validate(b) for b in businesses],
        )
    except Exception as e:
        return error_server(title="Vendor Businesses", error=str(e))


@router.get("/redemptions")
def get_redemptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    business_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_vendor=Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    try:
        redemptions, total = vendor_dashboard_service.get_vendor_redemptions(
            db,
            vendor_id=current_vendor.id,
            skip=skip,
            limit=limit,
            business_id=business_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
        )

        data = {
            "items": [
                VendorRedemptionHistoryItem(
                    id=r.id,
                    business_id=r.business_id,
                    business_name=r.business.business_name if r.business else "—",
                    user_id=r.user_id,
                    user_name=(
                        f"{r.user.first_name} {r.user.last_name}".strip()
                        if r.user
                        else "—"
                    ),
                    user_phone=r.user.phone if r.user else "—",
                    coupon_id=r.coupon_id,
                    coupon_name=(r.coupon.coupon_name if r.coupon else None),
                    claim_reference=r.claim_reference,
                    status=r.status,
                    remaining_daily_limit=r.remaining_daily_limit,
                    remaining_total_limit=r.remaining_total_limit,
                    redeemed_at=r.redeemed_at,
                )
                for r in redemptions
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

        return success_list(
            title="Vendor Redemption History",
            data=VendorRedemptionHistoryResponse(**data),
        )
    except Exception as e:
        return error_server(title="Vendor Redemption History", error=str(e))


@router.get("/analytics")
def get_analytics(
    current_vendor=Depends(get_current_vendor), db: Session = Depends(get_db)
):
    try:
        analytics = vendor_dashboard_service.get_vendor_analytics(db, current_vendor)
        return success_list(
            title="Vendor Dashboard Analytics",
            data=VendorDashboardAnalyticsResponse(**analytics),
        )
    except Exception as e:
        return error_server(title="Vendor Dashboard Analytics", error=str(e))
