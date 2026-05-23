from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from repositories import user_repository
from repositories.state_repository import get_state_by_id
from repositories.city_repository import get_city_by_id
from schemas.user import UserUpdate


def get_all_users(db: Session):
    return user_repository.get_all_users(db)


def get_user(db: Session, user_id: int):
    user = user_repository.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


def update_user(db: Session, user_id: int, payload: UserUpdate):
    user = user_repository.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    update_data = payload.model_dump(exclude_unset=True)

    # Validate email uniqueness if being changed
    if "email" in update_data and update_data["email"] != user.email:
        existing = user_repository.get_user_by_email(db, update_data["email"])
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )

    # Validate phone uniqueness if being changed
    if "phone" in update_data and update_data["phone"] != user.phone:
        existing = user_repository.get_user_by_phone(db, update_data["phone"])
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone already in use"
            )

    # Validate state if being changed
    if "state_id" in update_data:
        state = get_state_by_id(db, update_data["state_id"])
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="State not found"
            )

    # Validate city if being changed
    if "city_id" in update_data:
        city = get_city_by_id(db, update_data["city_id"])
        if not city:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="City not found"
            )

        # Ensure city belongs to the state
        target_state_id = update_data.get("state_id", user.state_id)
        if city.state_id != target_state_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="City does not belong to the selected state"
            )

    return user_repository.update_user(db, user, update_data)


def delete_user(db: Session, user_id: int):
    user = user_repository.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user_repository.delete_user(db, user)
