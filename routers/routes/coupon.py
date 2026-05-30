from typing import Optional

from fastapi import APIRouter, Depends, Query, Request, status
from routers.deps import get_admin_user, get_db
from schemas.coupon import CouponCreate, CouponResponse, CouponUpdate
from services import coupon_service
from services.audit_log_service import log_admin_action
from sqlalchemy.orm import Session
from utils.response import (
    error_not_found,
    error_server,
    success_create,
    success_delete,
    success_list,
    success_update,
)

router = APIRouter()


@router.get("/")
def list_coupons(
    business_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        coupons = coupon_service.get_all_coupons(
            db, business_id=business_id, is_active=is_active, search=search
        )
        return success_list(
            title="Coupons List",
            data=[
                CouponResponse.model_validate(coupon_service.serialize_coupon(c))
                for c in coupons
            ],
        )
    except Exception as e:
        return error_server(title="Coupons List", error=str(e))


@router.get("/{coupon_id}")
def get_coupon(coupon_id: int, db: Session = Depends(get_db)):
    try:
        coupon = coupon_service.get_coupon(db, coupon_id)
        return success_create(
            title="Coupon Details",
            data=CouponResponse.model_validate(coupon_service.serialize_coupon(coupon)),
        )
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_not_found(title="Get Coupon", resource="Coupon")
        return error_server(title="Get Coupon", error=str(e))


@router.post(
    "/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_user)]
)
def create_coupon(
    payload: CouponCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
):
    try:
        coupon = coupon_service.create_coupon(db, payload)
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="create",
            resource_type="coupon",
            resource_id=coupon.id,
            method=request.method,
            path=str(request.url.path),
            details={
                "coupon_name": coupon.coupon_name,
                "business_id": coupon.business_id,
            },
        )
        return success_create(
            title="Coupon Created",
            data=CouponResponse.model_validate(coupon_service.serialize_coupon(coupon)),
        )
    except Exception as e:
        detail = getattr(e, "detail", None)
        if detail is not None:
            return error_server(title="Create Coupon", error=str(detail))
        return error_server(title="Create Coupon", error=str(e))


@router.put("/{coupon_id}", dependencies=[Depends(get_admin_user)])
def update_coupon(
    coupon_id: int,
    payload: CouponUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
):
    try:
        coupon = coupon_service.update_coupon(db, coupon_id, payload)
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="update",
            resource_type="coupon",
            resource_id=coupon.id,
            method=request.method,
            path=str(request.url.path),
            details={
                "updated_fields": list(payload.model_dump(exclude_unset=True).keys())
            },
        )
        return success_update(
            title="Coupon Updated",
            data=CouponResponse.model_validate(coupon_service.serialize_coupon(coupon)),
        )
    except Exception as e:
        if hasattr(e, "status_code") and getattr(e, "status_code") == 404:
            return error_not_found(title="Update Coupon", resource="Coupon")
        if hasattr(e, "status_code"):
            return error_server(
                title="Update Coupon", error=str(getattr(e, "detail", e))
            )
        return error_server(title="Update Coupon", error=str(e))


@router.delete("/{coupon_id}", dependencies=[Depends(get_admin_user)])
def delete_coupon(
    coupon_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
):
    try:
        coupon = coupon_service.delete_coupon(db, coupon_id)
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="delete",
            resource_type="coupon",
            resource_id=coupon.id,
            method=request.method,
            path=str(request.url.path),
            details={"coupon_name": coupon.coupon_name},
        )
        return success_delete(title="Coupon Deleted", resource_id=coupon_id)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_not_found(title="Delete Coupon", resource="Coupon")
        return error_server(title="Delete Coupon", error=str(e))


@router.patch("/{coupon_id}/toggle-active", dependencies=[Depends(get_admin_user)])
def toggle_coupon_active(
    coupon_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
):
    try:
        coupon = coupon_service.toggle_active(db, coupon_id)
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="toggle_active",
            resource_type="coupon",
            resource_id=coupon.id,
            method=request.method,
            path=str(request.url.path),
            details={"is_active": coupon.is_active},
        )
        return success_update(
            title="Coupon Status Updated",
            data=CouponResponse.model_validate(coupon_service.serialize_coupon(coupon)),
        )
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_not_found(title="Toggle Coupon Active", resource="Coupon")
        return error_server(title="Toggle Coupon Active", error=str(e))
