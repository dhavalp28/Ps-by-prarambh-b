from fastapi import APIRouter, Depends, Query
from routers.deps import get_current_user, get_db
from schemas.business_review import BusinessReviewResponse, BusinessReviewUpsert
from services import business_review_service, business_service
from sqlalchemy.orm import Session
from utils.response import error_server, success_list, success_update

router = APIRouter()


@router.get("/details/{business_id}")
def get_business_details(business_id: int, db: Session = Depends(get_db)):
    try:
        details = business_service.get_business_details(db, business_id)
        return success_list(title="Business Details", data=details)
    except Exception as e:
        return error_server(title="Business Details", error=str(e))


@router.get("/{business_id}/reviews")
def list_business_reviews(
    business_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    try:
        reviews, total = business_review_service.get_business_reviews(
            db, business_id=business_id, skip=skip, limit=limit
        )
        return success_list(
            title="Business Reviews",
            data={
                "items": [
                    BusinessReviewResponse.model_validate(review) for review in reviews
                ],
                "total": total,
                "skip": skip,
                "limit": limit,
            },
        )
    except Exception as e:
        return error_server(title="Business Reviews", error=str(e))


@router.put("/{business_id}/reviews/me")
def upsert_business_review(
    business_id: int,
    payload: BusinessReviewUpsert,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        review, summary = business_review_service.upsert_business_review(
            db,
            business_id=business_id,
            user_id=current_user.id,
            payload=payload,
        )
        return success_update(
            title="Business Review Saved",
            data={
                "review": BusinessReviewResponse.model_validate(review),
                "rating_summary": summary,
            },
        )
    except Exception as e:
        return error_server(title="Business Review Saved", error=str(e))
