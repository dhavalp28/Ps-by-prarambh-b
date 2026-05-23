from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories import state_repository
from app.schemas.state import StateCreate, StateUpdate


def get_all_states(db: Session):
    return state_repository.get_all_states(db)


def get_state(db: Session, state_id: int):
    state = state_repository.get_state_by_id(db, state_id)

    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="State not found"
        )

    return state


def create_state(db: Session, payload: StateCreate):
    existing = state_repository.get_state_by_name(db, payload.name)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="State with this name already exists"
        )

    return state_repository.create_state(db, payload.model_dump())


def update_state(db: Session, state_id: int, payload: StateUpdate):
    state = state_repository.get_state_by_id(db, state_id)

    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="State not found"
        )

    if payload.name and payload.name != state.name:
        existing = state_repository.get_state_by_name(db, payload.name)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State with this name already exists"
            )

    update_data = payload.model_dump(exclude_unset=True)

    return state_repository.update_state(db, state, update_data)


def delete_state(db: Session, state_id: int):
    state = state_repository.get_state_by_id(db, state_id)

    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="State not found"
        )

    state_repository.delete_state(db, state)
