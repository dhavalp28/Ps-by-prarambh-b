from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from routers.deps import get_db
from schemas.state import StateCreate, StateUpdate, StateResponse
from services import state_service
from utils.response import (
    success_list, success_create, success_update, success_delete,
    error_not_found, error_duplicate, error_server
)

router = APIRouter()


@router.get("/")
def list_states(db: Session = Depends(get_db)):
    try:
        states = state_service.get_all_states(db)
        return success_list(title="States List", data=states)
    except Exception as e:
        return error_server(title="States List", error=str(e))


@router.get("/{state_id}")
def get_state(state_id: int, db: Session = Depends(get_db)):
    try:
        state = state_service.get_state(db, state_id)
        if not state:
            return error_not_found(title="Get State", resource="State")
        return success_list(title="State Details", data=state)
    except Exception as e:
        return error_server(title="Get State", error=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_state(payload: StateCreate, db: Session = Depends(get_db)):
    try:
        state = state_service.create_state(db, payload)
        return success_create(title="State Created", data=state)
    except ValueError as e:
        return error_duplicate(title="Create State", resource="State")
    except Exception as e:
        return error_server(title="Create State", error=str(e))


@router.put("/{state_id}")
def update_state(state_id: int, payload: StateUpdate, db: Session = Depends(get_db)):
    try:
        state = state_service.update_state(db, state_id, payload)
        if not state:
            return error_not_found(title="Update State", resource="State")
        return success_update(title="State Updated", data=state)
    except Exception as e:
        return error_server(title="Update State", error=str(e))


@router.delete("/{state_id}")
def delete_state(state_id: int, db: Session = Depends(get_db)):
    try:
        state = state_service.delete_state(db, state_id)
        if not state:
            return error_not_found(title="Delete State", resource="State")
        return success_delete(title="State Deleted")
    except Exception as e:
        return error_server(title="Delete State", error=str(e))
