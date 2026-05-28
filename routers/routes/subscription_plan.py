from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from routers.deps import get_db
from schemas.subscription_plan import SubscriptionPlanCreate, SubscriptionPlanUpdate, SubscriptionPlanResponse
from services import subscription_plan_service
from utils.response import (
    success_list, success_create, success_update, success_delete,
    error_not_found, error_duplicate, error_server
)

router = APIRouter()


@router.get("/")
def list_subscription_plans(db: Session = Depends(get_db)):
    try:
        plans = subscription_plan_service.get_all_plans(db)
        return success_list(title="Subscription Plans List", data=[SubscriptionPlanResponse.model_validate(p) for p in plans])
    except Exception as e:
        return error_server(title="Subscription Plans List", error=str(e))


@router.get("/{plan_id}")
def get_subscription_plan(plan_id: int, db: Session = Depends(get_db)):
    try:
        plan = subscription_plan_service.get_plan(db, plan_id)
        if not plan:
            return error_not_found(title="Get Subscription Plan", resource="Subscription Plan")
        return success_list(title="Subscription Plan Details", data=SubscriptionPlanResponse.model_validate(plan))
    except Exception as e:
        return error_server(title="Get Subscription Plan", error=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_subscription_plan(payload: SubscriptionPlanCreate, db: Session = Depends(get_db)):
    try:
        plan = subscription_plan_service.create_plan(db, payload.model_dump())
        return success_create(title="Subscription Plan Created", data=SubscriptionPlanResponse.model_validate(plan))
    except ValueError as e:
        return error_duplicate(title="Create Subscription Plan", resource="Subscription Plan")
    except Exception as e:
        return error_server(title="Create Subscription Plan", error=str(e))


@router.put("/{plan_id}")
def update_subscription_plan(plan_id: int, payload: SubscriptionPlanUpdate, db: Session = Depends(get_db)):
    try:
        plan = subscription_plan_service.update_plan(db, plan_id, payload.model_dump(exclude_unset=True))
        if not plan:
            return error_not_found(title="Update Subscription Plan", resource="Subscription Plan")
        return success_update(title="Subscription Plan Updated", data=SubscriptionPlanResponse.model_validate(plan))
    except Exception as e:
        return error_server(title="Update Subscription Plan", error=str(e))


@router.delete("/{plan_id}")
def delete_subscription_plan(plan_id: int, db: Session = Depends(get_db)):
    try:
        plan = subscription_plan_service.delete_plan(db, plan_id)
        if not plan:
            return error_not_found(title="Delete Subscription Plan", resource="Subscription Plan")
        return success_delete(title="Subscription Plan Deleted", resource_id=plan.id)
    except Exception as e:
        return error_server(title="Delete Subscription Plan", error=str(e))


@router.patch("/{plan_id}/toggle-active")
def toggle_subscription_plan_active(plan_id: int, db: Session = Depends(get_db)):
    try:
        plan = subscription_plan_service.toggle_plan_active(db, plan_id)
        if not plan:
            return error_not_found(title="Toggle Subscription Plan Active", resource="Subscription Plan")
        return success_update(title="Subscription Plan Status Updated", data=SubscriptionPlanResponse.model_validate(plan))
    except Exception as e:
        return error_server(title="Toggle Subscription Plan Active", error=str(e))
