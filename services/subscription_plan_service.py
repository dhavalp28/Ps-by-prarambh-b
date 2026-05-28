from fastapi import HTTPException
from sqlalchemy.orm import Session

from repositories.subscription_plan_repository import (
    get_all_subscription_plans,
    get_subscription_plan_by_id,
    get_subscription_plan_by_name,
    create_subscription_plan,
    update_subscription_plan,
    delete_subscription_plan,
)


def get_all_plans(db: Session):
    return get_all_subscription_plans(db)


def get_plan(db: Session, plan_id: int):
    plan = get_subscription_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    return plan


def create_plan(db: Session, plan_data: dict):
    # Check if plan name already exists
    existing_plan = get_subscription_plan_by_name(db, plan_data.get("plan_name"))
    if existing_plan:
        raise HTTPException(status_code=400, detail="Plan name already exists")
    
    return create_subscription_plan(db, plan_data)


def update_plan(db: Session, plan_id: int, update_data: dict):
    plan = get_subscription_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    
    # Check if new plan name already exists (if being updated)
    if "plan_name" in update_data and update_data["plan_name"]:
        existing_plan = get_subscription_plan_by_name(db, update_data["plan_name"])
        if existing_plan and existing_plan.id != plan_id:
            raise HTTPException(status_code=400, detail="Plan name already exists")
    
    return update_subscription_plan(db, plan, update_data)


def delete_plan(db: Session, plan_id: int):
    plan = get_subscription_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    
    delete_subscription_plan(db, plan)
    return plan


def toggle_plan_active(db: Session, plan_id: int):
    plan = get_subscription_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    
    plan.is_active = not plan.is_active
    return update_subscription_plan(db, plan, {})
