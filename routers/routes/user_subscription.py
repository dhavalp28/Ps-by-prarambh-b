from fastapi import APIRouter, Depends, Query
from routers.deps import get_admin_user, get_current_user, get_db
from schemas.payment_order import (
    PaymentOrderAdminResponse,
    SubscriptionPaymentVerifyRequest,
    SubscriptionPurchaseCreateRequest,
)
from schemas.user_subscription import UserSubscriptionResponse
from services import payment_service
from sqlalchemy.orm import Session
from utils.response import error_server, success_create, success_list

router = APIRouter()


@router.post("/purchase-order")
def create_purchase_order(
    payload: SubscriptionPurchaseCreateRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        result = payment_service.create_subscription_purchase_order(
            db, current_user.id, payload.subscription_plan_id
        )
        return success_create(title="Subscription Purchase Order Created", data=result)
    except Exception as e:
        return error_server(title="Create Subscription Purchase Order", error=str(e))


@router.post("/verify-payment")
def verify_payment(
    payload: SubscriptionPaymentVerifyRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        result = payment_service.verify_subscription_payment(
            db,
            user_id=current_user.id,
            razorpay_order_id=payload.razorpay_order_id,
            razorpay_payment_id=payload.razorpay_payment_id,
            razorpay_signature=payload.razorpay_signature,
        )
        return success_create(title="Subscription Payment Verified", data=result)
    except Exception as e:
        return error_server(title="Verify Subscription Payment", error=str(e))


@router.get("/me")
def get_my_subscription(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        result = payment_service.get_my_subscription_details(db, current_user.id)
        return success_list(title="My Subscription", data=result)
    except Exception as e:
        return error_server(title="Get My Subscription", error=str(e))


@router.get("/history")
def get_my_subscription_history(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        result = payment_service.get_my_subscription_history(db, current_user.id)
        return success_list(
            title="My Subscription History",
            data=[UserSubscriptionResponse.model_validate(item) for item in result],
        )
    except Exception as e:
        return error_server(title="Get My Subscription History", error=str(e))


@router.get("/admin/payment-orders", dependencies=[Depends(get_admin_user)])
def list_payment_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    try:
        items, total = payment_service.get_admin_payment_orders(
            db, skip=skip, limit=limit
        )
        return success_list(
            title="Payment Orders",
            data={
                "items": [
                    PaymentOrderAdminResponse.model_validate(item) for item in items
                ],
                "total": total,
                "skip": skip,
                "limit": limit,
            },
        )
    except Exception as e:
        return error_server(title="List Payment Orders", error=str(e))
