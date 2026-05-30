from typing import Optional

from fastapi import APIRouter, Depends, Query, Request, status
from routers.deps import get_admin_user, get_db
from schemas.brand import (
    BranchBusinessResponse,
    BrandCreate,
    BrandDetailResponse,
    BrandResponse,
    BrandUpdate,
)
from services import brand_service
from services.audit_log_service import log_admin_action
from sqlalchemy.orm import Session
from utils.response import (
    error_duplicate,
    error_not_found,
    error_server,
    success_create,
    success_delete,
    success_list,
    success_update,
)

router = APIRouter()


@router.get("/")
def list_brands(db: Session = Depends(get_db)):
    try:
        brands = brand_service.get_all_brands(db)
        return success_list(
            title="Brands List",
            data=[BrandResponse.model_validate(brand) for brand in brands],
        )
    except Exception as e:
        return error_server(title="Brands List", error=str(e))


@router.get("/{brand_id}")
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    try:
        brand = brand_service.get_brand(db, brand_id)
        return success_create(
            title="Brand Details", data=BrandDetailResponse.model_validate(brand)
        )
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_not_found(title="Get Brand", resource="Brand")
        return error_server(title="Get Brand", error=str(e))


@router.get("/{brand_id}/branches")
def get_brand_branches(
    brand_id: int,
    search: Optional[str] = Query(None, description="Search by branch name or address"),
    exclude_business_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    try:
        branches = brand_service.get_brand_branches(
            db,
            brand_id=brand_id,
            search=search,
            exclude_business_id=exclude_business_id,
            limit=limit,
        )
        return success_list(
            title="Brand Branches",
            data=[BranchBusinessResponse.model_validate(branch) for branch in branches],
        )
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_not_found(title="Get Brand Branches", resource="Brand")
        return error_server(title="Get Brand Branches", error=str(e))


@router.post(
    "/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_user)]
)
def create_brand(
    payload: BrandCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
):
    try:
        brand = brand_service.create_brand(db, payload)
        if brand is None:
            return error_server(title="Create Brand", error="Brand creation failed")
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="create",
            resource_type="brand",
            resource_id=brand.id,
            method=request.method,
            path=str(request.url.path),
            details={"name": brand.name},
        )
        return success_create(
            title="Brand Created", data=BrandResponse.model_validate(brand)
        )
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_duplicate(title="Create Brand", resource="Brand")
        return error_server(title="Create Brand", error=str(e))


@router.put("/{brand_id}", dependencies=[Depends(get_admin_user)])
def update_brand(
    brand_id: int,
    payload: BrandUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
):
    try:
        brand = brand_service.update_brand(db, brand_id, payload)
        if brand is None:
            return error_not_found(title="Update Brand", resource="Brand")
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="update",
            resource_type="brand",
            resource_id=brand.id,
            method=request.method,
            path=str(request.url.path),
            details={
                "updated_fields": list(payload.model_dump(exclude_unset=True).keys())
            },
        )
        return success_update(
            title="Brand Updated", data=BrandResponse.model_validate(brand)
        )
    except Exception as e:
        if hasattr(e, "status_code") and getattr(e, "status_code") == 404:
            return error_not_found(title="Update Brand", resource="Brand")
        if hasattr(e, "status_code"):
            return error_duplicate(title="Update Brand", resource="Brand")
        return error_server(title="Update Brand", error=str(e))


@router.delete("/{brand_id}", dependencies=[Depends(get_admin_user)])
def delete_brand(
    brand_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
):
    try:
        brand = brand_service.delete_brand(db, brand_id)
        if brand is None:
            return error_not_found(title="Delete Brand", resource="Brand")
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="delete",
            resource_type="brand",
            resource_id=brand.id,
            method=request.method,
            path=str(request.url.path),
            details={"name": brand.name},
        )
        return success_delete(title="Brand Deleted", resource_id=brand_id)
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_not_found(title="Delete Brand", resource="Brand")
        return error_server(title="Delete Brand", error=str(e))


@router.patch("/{brand_id}/toggle-active", dependencies=[Depends(get_admin_user)])
def toggle_active(
    brand_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_admin_user),
):
    try:
        brand = brand_service.toggle_active(db, brand_id)
        if brand is None:
            return error_not_found(title="Toggle Brand Active", resource="Brand")
        log_admin_action(
            db,
            admin_user_id=admin_user.id,
            action="toggle_active",
            resource_type="brand",
            resource_id=brand.id,
            method=request.method,
            path=str(request.url.path),
            details={"is_active": brand.is_active},
        )
        return success_update(
            title="Brand Status Updated", data=BrandResponse.model_validate(brand)
        )
    except Exception as e:
        if hasattr(e, "status_code"):
            return error_not_found(title="Toggle Brand Active", resource="Brand")
        return error_server(title="Toggle Brand Active", error=str(e))
