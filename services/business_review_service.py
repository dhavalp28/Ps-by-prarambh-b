from db.models.business_review import BusinessReview
from fastapi import HTTPException, status
from repositories import business_repository, business_review_repository
from schemas.business_review import BusinessReviewUpsert
from sqlalchemy.orm import Session


def _ensure_business_exists(db: Session, business_id: int):
    business = business_repository.get_business_by_id(db, business_id)
    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )
    return business


def get_business_reviews(db: Session, business_id: int, skip: int = 0, limit: int = 10):
    _ensure_business_exists(db, business_id)
    return business_review_repository.list_business_reviews(
        db, business_id=business_id, skip=skip, limit=limit
    )


def upsert_business_review(
    db: Session,
    business_id: int,
    user_id: int,
    payload: BusinessReviewUpsert,
):
    _ensure_business_exists(db, business_id)

    try:
        review = business_review_repository.get_business_review_by_business_and_user(
            db, business_id=business_id, user_id=user_id
        )

        if review is None:
            review = BusinessReview(
                business_id=business_id,
                user_id=user_id,
                rating=payload.rating,
                review=payload.review,
                is_active=payload.is_active,
            )
            db.add(review)
        else:
            setattr(review, "rating", payload.rating)
            setattr(review, "review", payload.review)
            setattr(review, "is_active", payload.is_active)

        db.flush()
        summary = business_review_repository.refresh_business_rating_summary(
            db, business_id
        )
        db.commit()
        db.refresh(review)

        return review, summary
    except Exception:
        db.rollback()
        raise
