from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from repositories import business_repository
from repositories.state_repository import get_state_by_id
from repositories.city_repository import get_city_by_id
from repositories.category_repository import get_category_by_id
from repositories.sub_category_repository import get_sub_category_by_id
from schemas.business import BusinessCreate, BusinessUpdate


def _validate_location(db: Session, state_id: int, city_id: int):
    state = get_state_by_id(db, state_id)
    if not state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="State not found")

    city = get_city_by_id(db, city_id)
    if not city:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")

    if city.state_id != state_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City does not belong to the selected state"
        )


def _validate_category(db: Session, category_id: int, sub_category_id: int | None):
    category = get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    if sub_category_id:
        sub = get_sub_category_by_id(db, sub_category_id)
        if not sub:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sub-category not found")
        if sub.category_id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sub-category does not belong to the selected category"
            )


def get_all_businesses(db: Session):
    return business_repository.get_all_businesses(db)


def get_business(db: Session, business_id: int):
    business = business_repository.get_business_by_id(db, business_id)
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    return business


def create_business(db: Session, payload: BusinessCreate):
    _validate_location(db, payload.state_id, payload.city_id)
    _validate_category(db, payload.category_id, payload.sub_category_id)

    return business_repository.create_business(db, payload.model_dump())


def update_business(db: Session, business_id: int, payload: BusinessUpdate):
    business = business_repository.get_business_by_id(db, business_id)
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")

    update_data = payload.model_dump(exclude_unset=True)

    new_state_id = update_data.get("state_id", business.state_id)
    new_city_id  = update_data.get("city_id",  business.city_id)
    if "state_id" in update_data or "city_id" in update_data:
        _validate_location(db, new_state_id, new_city_id)

    new_category_id     = update_data.get("category_id",     business.category_id)
    new_sub_category_id = update_data.get("sub_category_id", business.sub_category_id)
    if "category_id" in update_data or "sub_category_id" in update_data:
        _validate_category(db, new_category_id, new_sub_category_id)

    return business_repository.update_business(db, business, update_data)


def delete_business(db: Session, business_id: int):
    business = business_repository.get_business_by_id(db, business_id)
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    business_repository.delete_business(db, business)
    return business


def toggle_active(db: Session, business_id: int):
    business = business_repository.get_business_by_id(db, business_id)
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    return business_repository.update_business(db, business, {"is_active": not business.is_active})
