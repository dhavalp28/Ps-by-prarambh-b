from db.models.business import Business
from db.models.business_review import BusinessReview
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload


def get_business_review_by_business_and_user(
    db: Session, business_id: int, user_id: int
):
    return (
        db.query(BusinessReview)
        .options(joinedload(BusinessReview.user))
        .filter(
            BusinessReview.business_id == business_id,
            BusinessReview.user_id == user_id,
        )
        .first()
    )


def list_business_reviews(
    db: Session, business_id: int, skip: int = 0, limit: int = 10
):
    query = (
        db.query(BusinessReview)
        .options(joinedload(BusinessReview.user))
        .filter(
            BusinessReview.business_id == business_id,
            BusinessReview.is_active == True,
        )
    )
    total = query.count()
    items = (
        query.order_by(BusinessReview.updated_at.desc(), BusinessReview.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return items, total


def get_latest_business_reviews(db: Session, business_id: int, limit: int = 5):
    return (
        db.query(BusinessReview)
        .options(joinedload(BusinessReview.user))
        .filter(
            BusinessReview.business_id == business_id,
            BusinessReview.is_active == True,
        )
        .order_by(BusinessReview.updated_at.desc(), BusinessReview.id.desc())
        .limit(limit)
        .all()
    )


def refresh_business_rating_summary(db: Session, business_id: int):
    average_rating, total_reviews = (
        db.query(
            func.coalesce(func.avg(BusinessReview.rating), 0.0),
            func.count(BusinessReview.id),
        )
        .filter(
            BusinessReview.business_id == business_id,
            BusinessReview.is_active == True,
        )
        .one()
    )

    business = db.query(Business).filter(Business.id == business_id).first()
    if business is not None:
        setattr(business, "average_rating", float(average_rating or 0.0))
        setattr(business, "total_reviews", int(total_reviews or 0))
        db.flush()

    return {
        "average_rating": float(average_rating or 0.0),
        "total_reviews": int(total_reviews or 0),
    }
