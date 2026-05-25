from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from routers.deps import get_db
from schemas.user import UserResponse, UserUpdate
from services import user_service
from utils.response import (
    success_list, success_update, success_delete,
    error_not_found, error_server
)

router = APIRouter()


@router.get("/")
def list_users(db: Session = Depends(get_db)):
    try:
        users = user_service.get_all_users(db)
        return success_list(title="Users List", data=users)
    except Exception as e:
        return error_server(title="Users List", error=str(e))


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user = user_service.get_user(db, user_id)
        if not user:
            return error_not_found(title="Get User", resource="User")
        return success_list(title="User Details", data=user)
    except Exception as e:
        return error_server(title="Get User", error=str(e))


@router.put("/{user_id}")
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    try:
        user = user_service.update_user(db, user_id, payload)
        if not user:
            return error_not_found(title="Update User", resource="User")
        return success_update(title="User Updated", data=user)
    except Exception as e:
        return error_server(title="Update User", error=str(e))


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user = user_service.delete_user(db, user_id)
        if not user:
            return error_not_found(title="Delete User", resource="User")
        return success_delete(title="User Deleted")
    except Exception as e:
        return error_server(title="Delete User", error=str(e))
