from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.schemas.state import StateCreate, StateUpdate, StateResponse
from app.services import state_service

router = APIRouter()


@router.get("/", response_model=List[StateResponse])
def list_states(db: Session = Depends(get_db)):
    return state_service.get_all_states(db)


@router.get("/{state_id}", response_model=StateResponse)
def get_state(state_id: int, db: Session = Depends(get_db)):
    return state_service.get_state(db, state_id)


@router.post("/", response_model=StateResponse, status_code=status.HTTP_201_CREATED)
def create_state(payload: StateCreate, db: Session = Depends(get_db)):
    return state_service.create_state(db, payload)


@router.put("/{state_id}", response_model=StateResponse)
def update_state(state_id: int, payload: StateUpdate, db: Session = Depends(get_db)):
    return state_service.update_state(db, state_id, payload)


@router.delete("/{state_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_state(state_id: int, db: Session = Depends(get_db)):
    state_service.delete_state(db, state_id)
