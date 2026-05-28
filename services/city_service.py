from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from repositories import city_repository, state_repository, category_repository, sub_category_repository
from schemas.city import CityCreate, CityUpdate
from utils.upload import delete_upload


def get_all_cities(db: Session):
    return city_repository.get_all_cities(db)


def get_cities_by_state(db: Session, state_id: int):
    state = state_repository.get_state_by_id(db, state_id)

    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="State not found"
        )

    return city_repository.get_cities_by_state(db, state_id)


def get_city(db: Session, city_id: int):
    city = city_repository.get_city_by_id(db, city_id)

    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found"
        )

    return city


def create_city(db: Session, payload: CityCreate):
    state = state_repository.get_state_by_id(db, payload.state_id)

    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="State not found"
        )

    existing = city_repository.get_city_by_name_and_state(db, payload.name, payload.state_id)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City with this name already exists in the given state"
        )

    return city_repository.create_city(db, payload.model_dump())


def update_city(db: Session, city_id: int, payload: CityUpdate):
    city = city_repository.get_city_by_id(db, city_id)

    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found"
        )

    update_data = payload.model_dump(exclude_unset=True)

    new_state_id = update_data.get("state_id", city.state_id)

    if "state_id" in update_data:
        state = state_repository.get_state_by_id(db, new_state_id)

        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="State not found"
            )

    new_name = update_data.get("name", city.name)

    if "name" in update_data or "state_id" in update_data:
        if new_name != city.name or new_state_id != city.state_id:
            existing = city_repository.get_city_by_name_and_state(db, new_name, new_state_id)

            if existing and existing.id != city_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="City with this name already exists in the given state"
                )

    if "is_active" in update_data and not update_data["is_active"]:
        # If deactivating city, also deactivate all child categories and their sub-categories
        categories = category_repository.get_categories_by_city(db, city_id)
        for category in categories:
            # Deactivate all sub-categories of this category
            sub_categories = sub_category_repository.get_sub_categories_by_category_id(db, category.id)
            for sub_cat in sub_categories:
                sub_category_repository.update_sub_category(db, sub_cat, {"is_active": False})
            # Deactivate the category
            category_repository.update_category(db, category, {"is_active": False})

    return city_repository.update_city(db, city, update_data)


def delete_city(db: Session, city_id: int):
    city = city_repository.get_city_by_id(db, city_id)

    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found"
        )

    # Delete all child categories and their sub-categories
    categories = category_repository.get_categories_by_city(db, city_id)
    for category in categories:
        # Delete all sub-categories of this category
        sub_categories = sub_category_repository.get_sub_categories_by_category_id(db, category.id)
        for sub_cat in sub_categories:
            if sub_cat.icon:
                delete_upload(sub_cat.icon)
            sub_category_repository.delete_sub_category(db, sub_cat)
        
        # Delete the category icon
        if category.icon:
            delete_upload(category.icon)
        
        # Delete the category
        category_repository.delete_category(db, category)

    city_repository.delete_city(db, city)
    return city
