from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from repositories import city_repository, state_repository
from schemas.city import CityCreate, CityUpdate


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

    return city_repository.update_city(db, city, update_data)


def delete_city(db: Session, city_id: int):
    city = city_repository.get_city_by_id(db, city_id)

    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found"
        )

    city_repository.delete_city(db, city)
