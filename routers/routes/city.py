from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from routers.deps import get_db
from schemas.city import CityCreate, CityUpdate, CityResponse
from services import city_service
from utils.response import (
    success_list, success_create, success_update, success_delete,
    error_not_found, error_duplicate, error_server
)

router = APIRouter()


@router.get("/")
def list_cities(db: Session = Depends(get_db)):
    try:
        cities = city_service.get_all_cities(db)
        return success_list(title="Cities List", data=cities)
    except Exception as e:
        return error_server(title="Cities List", error=str(e))


@router.get("/by-state/{state_id}")
def list_cities_by_state(state_id: int, db: Session = Depends(get_db)):
    try:
        cities = city_service.get_cities_by_state(db, state_id)
        return success_list(title="Cities by State", data=cities)
    except Exception as e:
        return error_server(title="Cities by State", error=str(e))


@router.get("/{city_id}")
def get_city(city_id: int, db: Session = Depends(get_db)):
    try:
        city = city_service.get_city(db, city_id)
        if not city:
            return error_not_found(title="Get City", resource="City")
        return success_list(title="City Details", data=city)
    except Exception as e:
        return error_server(title="Get City", error=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_city(payload: CityCreate, db: Session = Depends(get_db)):
    try:
        city = city_service.create_city(db, payload)
        return success_create(title="City Created", data=city)
    except ValueError as e:
        return error_duplicate(title="Create City", resource="City")
    except Exception as e:
        return error_server(title="Create City", error=str(e))


@router.put("/{city_id}")
def update_city(city_id: int, payload: CityUpdate, db: Session = Depends(get_db)):
    try:
        city = city_service.update_city(db, city_id, payload)
        if not city:
            return error_not_found(title="Update City", resource="City")
        return success_update(title="City Updated", data=city)
    except Exception as e:
        return error_server(title="Update City", error=str(e))


@router.delete("/{city_id}")
def delete_city(city_id: int, db: Session = Depends(get_db)):
    try:
        city = city_service.delete_city(db, city_id)
        if not city:
            return error_not_found(title="Delete City", resource="City")
        return success_delete(title="City Deleted")
    except Exception as e:
        return error_server(title="Delete City", error=str(e))
