from fastapi import HTTPException, status
from repositories import brand_repository, business_repository
from schemas.brand import BrandCreate, BrandUpdate
from sqlalchemy.orm import Session


def get_all_brands(db: Session):
    return brand_repository.get_all_brands(db)


def get_brand(db: Session, brand_id: int):
    brand = brand_repository.get_brand_by_id(db, brand_id)
    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found"
        )
    return brand


def get_brand_branches(
    db: Session,
    brand_id: int,
    search: str | None = None,
    exclude_business_id: int | None = None,
    limit: int = 50,
):
    get_brand(db, brand_id)
    return business_repository.search_branches_by_brand_id(
        db,
        brand_id=brand_id,
        search=search,
        exclude_business_id=exclude_business_id,
        limit=limit,
    )


def _sync_brand_businesses(db: Session, brand_id: int, business_ids: list[int]):
    target_ids = set(business_ids)
    current_businesses = business_repository.get_businesses_by_brand_id(db, brand_id)

    for business in current_businesses:
        if business.id not in target_ids:
            business_repository.update_business(db, business, {"brand_id": None})

    if target_ids:
        target_businesses = business_repository.get_businesses_by_ids(
            db, list(target_ids)
        )
        found_ids = {business.id for business in target_businesses}
        missing_ids = target_ids - found_ids
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Businesses not found: {', '.join(str(i) for i in sorted(missing_ids))}",
            )

        for business in target_businesses:
            if getattr(business, "brand_id", None) != brand_id:
                business_repository.update_business(
                    db, business, {"brand_id": brand_id}
                )


def create_brand(db: Session, payload: BrandCreate):
    existing = brand_repository.get_brand_by_name(db, payload.name.strip())
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand with this name already exists",
        )

    brand_data = {
        "name": payload.name.strip(),
        "description": (payload.description or "").strip() or None,
        "is_active": payload.is_active,
    }
    brand = brand_repository.create_brand(db, brand_data)
    created_brand_id = brand.__dict__.get("id")
    if not isinstance(created_brand_id, int):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve created brand ID",
        )

    _sync_brand_businesses(db, created_brand_id, payload.business_ids)
    return brand_repository.get_brand_by_id(db, created_brand_id)


def update_brand(db: Session, brand_id: int, payload: BrandUpdate):
    brand = brand_repository.get_brand_by_id(db, brand_id)
    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found"
        )

    update_data = payload.model_dump(exclude_unset=True)

    if "name" in update_data:
        new_name = update_data["name"].strip()
        existing = brand_repository.get_brand_by_name(db, new_name)
        current_brand_id = brand.__dict__.get("id")
        existing_brand_id = (
            existing.__dict__.get("id") if existing is not None else None
        )
        if existing is not None and existing_brand_id != current_brand_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Brand with this name already exists",
            )
        update_data["name"] = new_name

    business_ids = update_data.pop("business_ids", None)

    if "description" in update_data:
        update_data["description"] = (update_data["description"] or "").strip() or None

    brand_repository.update_brand(db, brand, update_data)

    if business_ids is not None:
        _sync_brand_businesses(db, brand_id, business_ids)

    return brand_repository.get_brand_by_id(db, brand_id)


def delete_brand(db: Session, brand_id: int):
    brand = brand_repository.get_brand_by_id(db, brand_id)
    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found"
        )

    for business in list(brand.businesses or []):
        business_repository.update_business(db, business, {"brand_id": None})

    brand_repository.delete_brand(db, brand)
    return brand


def toggle_active(db: Session, brand_id: int):
    brand = brand_repository.get_brand_by_id(db, brand_id)
    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found"
        )
    current_is_active = bool(brand.__dict__.get("is_active", False))
    return brand_repository.update_brand(
        db, brand, {"is_active": not current_is_active}
    )
