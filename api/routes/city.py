from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from api.deps import get_db
from schemas.city import CityCreate, CityUpdate, CityResponse
from services import city_service

router = APIRouter()


@router.get("/", response_model=List[CityResponse])
def list_cities(db: Session = Depends(get_db)):
    return city_service.get_all_cities(db)


@router.get("/by-state/{state_id}", response_model=List[CityResponse])
def list_cities_by_state(state_id: int, db: Session = Depends(get_db)):
    return city_service.get_cities_by_state(db, state_id)


@router.get("/{city_id}", response_model=CityResponse)
def get_city(city_id: int, db: Session = Depends(get_db)):
    return city_service.get_city(db, city_id)


@router.post("/", response_model=CityResponse, status_code=status.HTTP_201_CREATED)
def create_city(payload: CityCreate, db: Session = Depends(get_db)):
    return city_service.create_city(db, payload)


@router.put("/{city_id}", response_model=CityResponse)
def update_city(city_id: int, payload: CityUpdate, db: Session = Depends(get_db)):
    return city_service.update_city(db, city_id, payload)


@router.delete("/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_city(city_id: int, db: Session = Depends(get_db)):
    city_service.delete_city(db, city_id)
