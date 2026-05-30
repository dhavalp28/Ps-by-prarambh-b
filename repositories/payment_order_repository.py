import json
from datetime import datetime

from db.models.payment_order import PaymentOrder
from sqlalchemy.orm import Session


def create_payment_order(db: Session, data: dict):
    payload = PaymentOrder(**data)
    db.add(payload)
    db.commit()
    db.refresh(payload)
    return payload


def get_payment_order_by_provider_order_id(db: Session, provider_order_id: str):
    return (
        db.query(PaymentOrder)
        .filter(PaymentOrder.provider_order_id == provider_order_id)
        .first()
    )


def get_payment_order_by_provider_payment_id(db: Session, provider_payment_id: str):
    return (
        db.query(PaymentOrder)
        .filter(PaymentOrder.provider_payment_id == provider_payment_id)
        .first()
    )


def update_payment_order(db: Session, payment_order: PaymentOrder, update_data: dict):
    for key, value in update_data.items():
        if key == "notes" and isinstance(value, dict):
            setattr(payment_order, key, json.dumps(value))
        else:
            setattr(payment_order, key, value)
    db.commit()
    db.refresh(payment_order)
    return payment_order


def list_payment_orders(db: Session, skip: int = 0, limit: int = 20):
    query = db.query(PaymentOrder).order_by(PaymentOrder.created_at.desc())
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total
