from typing import List

from fastapi import APIRouter, Depends, Request, status
from routers.deps import get_admin_user, get_current_user, get_db
from schemas.user import UserResponse, UserUpdate
from services import user_service
from services.audit_log_service import log_admin_action
from sqlalchemy.orm import Session
from utils.response import (
    error_not_found,
    error_server,
    success_delete,
    success_list,
    success_update,
)

router = APIRouter()


@router.get("/", dependencies=[Depends(get_admin_user)])
def list_users(db: Session = Depends(get_db)):
    """
    List all users (Admin only)
    """
    try:
        users = user_service.get_all_users(db)
        return success_list(
            title="Users List", data=[UserResponse.model_validate(u) for u in users]
        )
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
        return success_list(
            title="User Details", data=UserResponse.model_validate(user)
        )
    except Exception as e:
        return error_server(title="Get User", error=str(e))


@router.put("/{user_id}", dependencies=[Depends(get_admin_user)])
def update_user(
    user_id: int,
    payload: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
):
    """
    Update user (Admin only)
    """
    try:
        user = user_service.update_user(db, user_id, payload)
        if not user:
            return error_not_found(title="Update User", resource="User")
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="update",
            resource_type="user",
            resource_id=user.id,
            method=request.method,
            path=str(request.url.path),
            details={
                "updated_fields": list(payload.model_dump(exclude_unset=True).keys())
            },
        )
        return success_update(
            title="User Updated", data=UserResponse.model_validate(user)
        )
    except Exception as e:
        return error_server(title="Update User", error=str(e))


@router.delete("/{user_id}", dependencies=[Depends(get_admin_user)])
def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
):
    """
    Delete user (Admin only)
    """
    try:
        user = user_service.delete_user(db, user_id)
        if not user:
            return error_not_found(title="Delete User", resource="User")
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="delete",
            resource_type="user",
            resource_id=user.id,
            method=request.method,
            path=str(request.url.path),
            details={"email": user.email},
        )
        return success_delete(title="User Deleted", resource_id=user.id)
    except Exception as e:
        return error_server(title="Delete User", error=str(e))
