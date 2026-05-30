import json
from datetime import datetime
from uuid import uuid4

from core.payment import razorpay_client
from fastapi import HTTPException, status
from repositories.payment_order_repository import (
    create_payment_order,
    get_payment_order_by_provider_order_id,
    list_payment_orders,
    update_payment_order,
)
from repositories.subscription_plan_repository import get_subscription_plan_by_id
from services.user_subscription_service import (
    create_subscription,
    get_subscription_details,
    get_user_subscription_history,
)
from sqlalchemy.orm import Session


def create_subscription_purchase_order(
    db: Session, user_id: int, subscription_plan_id: int
):
    plan = get_subscription_plan_by_id(db, subscription_plan_id)
    if not plan or not plan.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found or inactive",
        )

    if not razorpay_client.is_configured():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Razorpay is not configured",
        )

    receipt = f"sub_{user_id}_{uuid4().hex[:12]}"
    amount_subunits = int(round(plan.price * 100))
    order = razorpay_client.create_order(
        amount_subunits=amount_subunits,
        currency="INR",
        receipt=receipt,
        notes={
            "user_id": str(user_id),
            "subscription_plan_id": str(plan.id),
            "plan_name": plan.plan_name,
        },
    )

    create_payment_order(
        db,
        {
            "user_id": user_id,
            "subscription_plan_id": plan.id,
            "provider": "razorpay",
            "provider_order_id": order["id"],
            "receipt": receipt,
            "amount": plan.price,
            "currency": "INR",
            "status": order.get("status", "created"),
            "notes": json.dumps(order.get("notes", {})),
        },
    )

    return {
        "order_id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"],
        "key": razorpay_client.key_id,
        "plan_id": plan.id,
        "plan_name": plan.plan_name,
    }


def verify_subscription_payment(
    db: Session,
    *,
    user_id: int,
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
):
    payment_order = get_payment_order_by_provider_order_id(db, razorpay_order_id)
    if not payment_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment order not found",
        )

    if payment_order.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot verify another user's payment",
        )

    if payment_order.status == "paid":
        return {
            "message": "Payment already verified",
            "subscription": get_subscription_details(db, user_id),
        }

    is_valid = razorpay_client.verify_signature(
        order_id=razorpay_order_id,
        payment_id=razorpay_payment_id,
        signature=razorpay_signature,
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Razorpay signature",
        )

    subscription = create_subscription(
        db,
        user_id=user_id,
        subscription_plan_id=payment_order.subscription_plan_id,
        validity_days=payment_order.subscription_plan.validity_days,
    )

    update_payment_order(
        db,
        payment_order,
        {
            "provider_payment_id": razorpay_payment_id,
            "status": "paid",
            "paid_at": datetime.utcnow(),
        },
    )

    return {
        "message": "Subscription purchased successfully",
        "subscription": get_subscription_details(db, user_id),
    }


def get_my_subscription_details(db: Session, user_id: int):
    return get_subscription_details(db, user_id)


def get_my_subscription_history(db: Session, user_id: int):
    return get_user_subscription_history(db, user_id)


def get_admin_payment_orders(db: Session, skip: int = 0, limit: int = 20):
    return list_payment_orders(db, skip=skip, limit=limit)
