from sqlalchemy.orm import Session
from typing import Optional

from db.models.subscription_plan import SubscriptionPlan


def get_all_subscription_plans(db: Session):
    return db.query(SubscriptionPlan).order_by(SubscriptionPlan.created_at.desc()).all()


def get_subscription_plan_by_id(db: Session, plan_id: int):
    return db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()


def get_subscription_plan_by_name(db: Session, plan_name: str):
    return db.query(SubscriptionPlan).filter(SubscriptionPlan.plan_name == plan_name).first()


def create_subscription_plan(db: Session, plan_data: dict):
    plan = SubscriptionPlan(**plan_data)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def update_subscription_plan(db: Session, plan: SubscriptionPlan, update_data: dict):
    for key, value in update_data.items():
        if value is not None:
            setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return plan


def delete_subscription_plan(db: Session, plan: SubscriptionPlan):
    db.delete(plan)
    db.commit()
