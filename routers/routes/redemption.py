from datetime import datetime
from typing import Optional

from core.rbac import ROLE_ADMIN
from fastapi import APIRouter, Depends, Query
from routers.deps import get_admin_user, get_current_user, get_db
from schemas.business_code import BusinessCodeValidateRequest
from schemas.redemption_history import (
    CouponClaimRequest,
    CouponClaimResponse,
    RedemptionHistoryResponse,
)
from services import business_code_service, redemption_service
from sqlalchemy.orm import Session
from utils.response import error_server, success_create, success_list

router = APIRouter()


@router.post("/claim")
def claim_coupon(
    payload: CouponClaimRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Claim a coupon only after QR verification using business_id + coupon_id + scanned business code.
    The coupon_id is stored as the claim reference in redemption history.
    """
    try:
        result = redemption_service.claim_coupon(
            db,
            user_id=current_user.id,
            business_id=payload.business_id,
            coupon_id=payload.coupon_id,
            business_code=payload.code,
        )
        return success_create(
            title="Coupon Claimed",
            data=CouponClaimResponse(**result),
        )
    except Exception as e:
        error_detail = getattr(e, "detail", e)
        return error_server(title="Coupon Claim", error=str(error_detail))


@router.post("/validate-code")
def validate_business_code(
    payload: BusinessCodeValidateRequest, db: Session = Depends(get_db)
):
    """
    Validate a business code (Public endpoint)
    """
    try:
        result = business_code_service.validate_business_code(db, payload.code)
        return success_list(title="Business Code Validation", data=result)
    except Exception as e:
        return error_server(title="Validate Business Code", error=str(e))


@router.get("/summary")
def get_redemption_summary(
    current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get user redemption summary (Authenticated users only)
    """
    try:
        summary = redemption_service.get_user_redemption_summary(db, current_user.id)
        return success_list(title="Redemption Summary", data=summary)
    except Exception as e:
        return error_server(title="Get Redemption Summary", error=str(e))


@router.get("/history")
def get_redemption_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    user_id: Optional[int] = None,
    business_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get redemption history with filters and pagination (Authenticated users only)

    Admin users can filter by any user_id, regular users can only see their own history
    """
    try:
        user_role = (getattr(current_user, "role", None) or "user").lower()

        # If not admin, only allow viewing own history
        if user_role != ROLE_ADMIN and user_id and user_id != current_user.id:
            return error_server(
                title="Get Redemption History",
                error="You can only view your own redemption history",
            )

        # If not admin and no user_id specified, default to current user
        if user_role != ROLE_ADMIN and not user_id:
            user_id = current_user.id

        redemptions, total = redemption_service.get_redemptions_with_filters(
            db,
            skip=skip,
            limit=limit,
            user_id=user_id,
            business_id=business_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
        )

        data = {
            "items": [RedemptionHistoryResponse.model_validate(r) for r in redemptions],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

        return success_list(title="Redemption History", data=data)
    except Exception as e:
        return error_server(title="Get Redemption History", error=str(e))


@router.get("/analytics", dependencies=[Depends(get_admin_user)])
def get_analytics(db: Session = Depends(get_db)):
    """
    Get redemption analytics (Admin only)
    """
    try:
        analytics = redemption_service.get_analytics(db)
        return success_list(title="Redemption Analytics", data=analytics)
    except Exception as e:
        return error_server(title="Get Analytics", error=str(e))
