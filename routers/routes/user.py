from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from routers.deps import get_db, get_current_user, get_admin_user
from schemas.user import UserResponse, UserUpdate
from services import user_service
from utils.response import (
    success_list, success_update, success_delete,
    error_not_found, error_server
)

router = APIRouter()


@router.get("/", dependencies=[Depends(get_admin_user)])
def list_users(db: Session = Depends(get_db)):
    """
    List all users (Admin only)
    """
    try:
        users = user_service.get_all_users(db)
        return success_list(title="Users List", data=[UserResponse.model_validate(u) for u in users])
    except Exception as e:
        return error_server(title="Users List", error=str(e))


@router.get("/{user_id}", dependencies=[Depends(get_admin_user)])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get specific user (Admin only)
    """
    try:
        user = user_service.get_user(db, user_id)
        if not user:
            return error_not_found(title="Get User", resource="User")
        return success_list(title="User Details", data=UserResponse.model_validate(user))
    except Exception as e:
        return error_server(title="Get User", error=str(e))


@router.put("/{user_id}", dependencies=[Depends(get_admin_user)])
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    """
    Update user (Admin only)
    """
    try:
        user = user_service.update_user(db, user_id, payload)
        if not user:
            return error_not_found(title="Update User", resource="User")
        return success_update(title="User Updated", data=UserResponse.model_validate(user))
    except Exception as e:
        return error_server(title="Update User", error=str(e))


@router.delete("/{user_id}", dependencies=[Depends(get_admin_user)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete user (Admin only)
    """
    try:
        user = user_service.delete_user(db, user_id)
        if not user:
            return error_not_found(title="Delete User", resource="User")
        return success_delete(title="User Deleted", resource_id=user.id)
    except Exception as e:
        return error_server(title="Delete User", error=str(e))
