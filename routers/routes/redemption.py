from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from routers.deps import get_db
from schemas.redemption_history import (
    RedemptionHistoryResponse,
    RedemptionSummaryResponse,
    RedemptionAnalyticsResponse,
)
from schemas.business_code import BusinessCodeValidateRequest, BusinessCodeValidateResponse
from services import redemption_service, business_code_service
from utils.response import (
    success_list, success_create, success_update, success_delete,
    error_not_found, error_duplicate, error_server
)

router = APIRouter()


@router.post("/redeem")
def redeem_coupon(payload: BusinessCodeValidateRequest, db: Session = Depends(get_db)):
    """Redeem a coupon using business code"""
    try:
        # Get user_id from auth (for now using a test user)
        # In production, this would come from the authenticated user
        user_id = 1  # TODO: Get from auth token
        
        result = redemption_service.redeem_coupon(db, user_id, payload.code)
        return success_create(title="Coupon Redeemed", data=result)
    except Exception as e:
        return error_server(title="Redeem Coupon", error=str(e))


@router.post("/validate-code")
def validate_business_code(payload: BusinessCodeValidateRequest, db: Session = Depends(get_db)):
    """Validate a business code"""
    try:
        result = business_code_service.validate_business_code(db, payload.code)
        return success_list(title="Business Code Validation", data=result)
    except Exception as e:
        return error_server(title="Validate Business Code", error=str(e))


@router.get("/summary")
def get_redemption_summary(db: Session = Depends(get_db)):
    """Get user redemption summary"""
    try:
        # Get user_id from auth
        user_id = 1  # TODO: Get from auth token
        
        summary = redemption_service.get_user_redemption_summary(db, user_id)
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
    db: Session = Depends(get_db)
):
    """Get redemption history with filters and pagination"""
    try:
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


@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    """Get redemption analytics"""
    try:
        analytics = redemption_service.get_analytics(db)
        return success_list(title="Redemption Analytics", data=analytics)
    except Exception as e:
        return error_server(title="Get Analytics", error=str(e))
