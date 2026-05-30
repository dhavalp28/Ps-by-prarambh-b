from typing import Optional

from fastapi import HTTPException, UploadFile, status
from repositories import business_repository, business_review_repository
from repositories.brand_repository import get_brand_by_id
from repositories.category_repository import get_category_by_id
from repositories.city_repository import get_city_by_id
from repositories.service_facility_repository import get_service_facilities_by_ids
from repositories.state_repository import get_state_by_id
from repositories.sub_category_repository import get_sub_category_by_id
from repositories.vendor_repository import get_vendor_by_id
from schemas.business import (
    BusinessCouponOfferResponse,
    BusinessCreate,
    BusinessDetailsResponse,
    BusinessFacilityResponse,
    BusinessResponse,
    BusinessUpdate,
)
from services import business_code_service, coupon_service
from sqlalchemy.orm import Session
from utils.upload import delete_upload, save_upload

BUSINESS_SPECIAL_FIELDS = {
    "facility_ids",
    "gallery_items",
    "gallery_delete_ids",
    "gallery_reorder",
}


def _validate_location(db: Session, state_id: int, city_id: int):
    state = get_state_by_id(db, state_id)
    if state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="State not found"
        )

    city = get_city_by_id(db, city_id)
    if city is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="City not found"
        )

    city_state_id = getattr(city, "state_id", None)
    if not isinstance(city_state_id, int) or city_state_id != state_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City does not belong to the selected state",
        )


def _validate_category(db: Session, category_id: int, sub_category_id: int | None):
    category = get_category_by_id(db, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    if sub_category_id is not None:
        sub = get_sub_category_by_id(db, sub_category_id)
        if sub is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sub-category not found"
            )
        sub_category_parent_id = getattr(sub, "category_id", None)
        if (
            not isinstance(sub_category_parent_id, int)
            or sub_category_parent_id != category_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sub-category does not belong to the selected category",
            )


def _normalize_optional_id(value):
    if value in (None, "", 0, "0"):
        return None
    return int(value)


def _validate_brand(db: Session, brand_id: int | None):
    if brand_id is None:
        return

    brand = get_brand_by_id(db, brand_id)
    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found"
        )


def _validate_owner(db: Session, owner_id: int | None):
    if owner_id is None:
        return

    owner = get_vendor_by_id(db, owner_id)
    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor owner not found"
        )


def _validate_facility_ids(db: Session, facility_ids: list[int]):
    if not facility_ids:
        return

    facilities = get_service_facilities_by_ids(db, facility_ids)
    found_ids = {facility.id for facility in facilities}
    missing_ids = [
        facility_id for facility_id in facility_ids if facility_id not in found_ids
    ]
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Facilities/Services not found: {missing_ids}",
        )


def _build_business_persist_data(payload_data: dict):
    return {
        key: value
        for key, value in payload_data.items()
        if key not in BUSINESS_SPECIAL_FIELDS
    }


def _build_gallery_items_to_add(
    gallery_items: list[dict], uploaded_urls: list[str], base_sort_order: int
):
    items_to_add: list[dict] = []

    for item in gallery_items:
        items_to_add.append(
            {
                "image_url": item["image_url"],
                "sort_order": int(item.get("sort_order", 0)),
            }
        )

    next_sort_order = base_sort_order
    if items_to_add:
        next_sort_order = max(
            next_sort_order, max(item["sort_order"] for item in items_to_add)
        )

    for image_url in uploaded_urls:
        next_sort_order += 1
        items_to_add.append({"image_url": image_url, "sort_order": next_sort_order})

    return items_to_add


def _serialize_business_coupon(coupon) -> dict:
    serialized = coupon_service.serialize_coupon(coupon)
    serialized.pop("business", None)
    return BusinessCouponOfferResponse.model_validate(serialized).model_dump()


def _serialize_business_details(business, latest_reviews: list):
    base_data = BusinessResponse.model_validate(business).model_dump()
    facilities = []
    for link in business.service_facility_links or []:
        facility = getattr(link, "facility", None)
        if facility is None or not bool(getattr(facility, "is_active", True)):
            continue
        facilities.append(
            BusinessFacilityResponse(
                id=facility.id,
                name=facility.name,
                icon=facility.icon,
                description=facility.description,
            ).model_dump()
        )

    return BusinessDetailsResponse.model_validate(
        {
            **base_data,
            "coupons": [
                _serialize_business_coupon(coupon)
                for coupon in business.coupons or []
                if coupon.is_active
            ],
            "facilities": facilities,
            "gallery_images": [
                {
                    "id": image.id,
                    "image_url": image.image_url,
                    "sort_order": image.sort_order,
                }
                for image in business.gallery_images or []
            ],
            "rating_summary": {
                "average_rating": float(
                    getattr(business, "average_rating", 0.0) or 0.0
                ),
                "total_reviews": int(getattr(business, "total_reviews", 0) or 0),
            },
            "latest_reviews": latest_reviews,
        }
    )


def get_all_businesses(db: Session, city_id: Optional[int] = None):
    return business_repository.get_all_businesses(db, city_id)


def get_business(db: Session, business_id: int):
    business = business_repository.get_business_by_id(db, business_id)
    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business not found"
        )
    return business


def get_business_branches(
    db: Session,
    business_id: int,
    search: str | None = None,
    limit: int = 50,
):
    business = get_business(db, business_id)
    brand_id = getattr(business, "brand_id", None)

    if not isinstance(brand_id, int):
        return []

    return business_repository.search_branches_by_brand_id(
        db,
        brand_id=brand_id,
        search=search,
        exclude_business_id=business_id,
        limit=limit,
    )


async def create_business(
    db: Session,
    payload: BusinessCreate,
    gallery_files: Optional[list[UploadFile]] = None,
):
    payload_data = payload.model_dump()
    payload_data["sub_category_id"] = _normalize_optional_id(
        payload_data.get("sub_category_id")
    )
    payload_data["owner_id"] = _normalize_optional_id(payload_data.get("owner_id"))
    payload_data["brand_id"] = _normalize_optional_id(payload_data.get("brand_id"))

    _validate_location(db, payload_data["state_id"], payload_data["city_id"])
    _validate_category(
        db, payload_data["category_id"], payload_data.get("sub_category_id")
    )
    _validate_brand(db, payload_data.get("brand_id"))
    _validate_owner(db, payload_data.get("owner_id"))
    _validate_facility_ids(db, payload_data.get("facility_ids") or [])

    saved_upload_urls: list[str] = []

    try:
        if gallery_files:
            for gallery_file in gallery_files:
                if gallery_file and gallery_file.filename:
                    saved_upload_urls.append(
                        await save_upload(gallery_file, folder="business-gallery")
                    )

        business = business_repository.create_business_instance(
            db, _build_business_persist_data(payload_data)
        )
        business_id_value = int(getattr(business, "id"))

        business_repository.replace_business_facilities(
            db, business_id_value, payload_data.get("facility_ids") or []
        )

        gallery_items_to_add = _build_gallery_items_to_add(
            payload_data.get("gallery_items") or [],
            saved_upload_urls,
            base_sort_order=0,
        )
        if gallery_items_to_add:
            business_repository.add_business_gallery_items(
                db, business_id_value, gallery_items_to_add
            )

        db.commit()
    except Exception:
        db.rollback()
        for upload_url in saved_upload_urls:
            delete_upload(upload_url)
        raise

    try:
        created_business_id = getattr(business, "id", None)
        if isinstance(created_business_id, int):
            business_code_service.create_business_code_for_business(
                db, created_business_id
            )
    except Exception as e:
        print(f"Error creating business code: {str(e)}")

    return get_business(db, business_id_value)


async def update_business(
    db: Session,
    business_id: int,
    payload: BusinessUpdate,
    gallery_files: Optional[list[UploadFile]] = None,
):
    business = business_repository.get_business_by_id(db, business_id)
    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business not found"
        )

    business_id_value = int(getattr(business, "id"))
    update_data = payload.model_dump(exclude_unset=True)
    if "sub_category_id" in update_data:
        update_data["sub_category_id"] = _normalize_optional_id(
            update_data.get("sub_category_id")
        )
    if "owner_id" in update_data:
        update_data["owner_id"] = _normalize_optional_id(update_data.get("owner_id"))
    if "brand_id" in update_data:
        update_data["brand_id"] = _normalize_optional_id(update_data.get("brand_id"))

    new_state_id = update_data.get("state_id", business.state_id)
    new_city_id = update_data.get("city_id", business.city_id)
    if "state_id" in update_data or "city_id" in update_data:
        _validate_location(db, new_state_id, new_city_id)

    new_category_id = update_data.get("category_id", business.category_id)
    new_sub_category_id = update_data.get("sub_category_id", business.sub_category_id)
    if "category_id" in update_data or "sub_category_id" in update_data:
        _validate_category(db, new_category_id, new_sub_category_id)

    if "brand_id" in update_data:
        _validate_brand(db, update_data.get("brand_id"))

    if "owner_id" in update_data:
        _validate_owner(db, update_data.get("owner_id"))

    if "facility_ids" in update_data and update_data.get("facility_ids") is not None:
        _validate_facility_ids(db, update_data.get("facility_ids") or [])

    saved_upload_urls: list[str] = []
    delete_after_commit: list[str] = []

    try:
        if gallery_files:
            for gallery_file in gallery_files:
                if gallery_file and gallery_file.filename:
                    saved_upload_urls.append(
                        await save_upload(gallery_file, folder="business-gallery")
                    )

        business_repository.update_business_instance(
            db, business, _build_business_persist_data(update_data)
        )

        if (
            "facility_ids" in update_data
            and update_data.get("facility_ids") is not None
        ):
            business_repository.replace_business_facilities(
                db, business_id_value, update_data.get("facility_ids") or []
            )

        gallery_delete_ids = update_data.get("gallery_delete_ids") or []
        if gallery_delete_ids:
            gallery_items = business_repository.get_gallery_items_by_ids(
                db, business_id_value, gallery_delete_ids
            )
            if len(gallery_items) != len(gallery_delete_ids):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="One or more gallery images were not found",
                )
            delete_after_commit.extend(
                [
                    str(getattr(gallery_item, "image_url"))
                    for gallery_item in gallery_items
                    if getattr(gallery_item, "image_url", None)
                ]
            )
            business_repository.delete_gallery_items(db, gallery_items)

        gallery_reorder = update_data.get("gallery_reorder") or []
        if gallery_reorder:
            existing_reorder_items = business_repository.get_gallery_items_by_ids(
                db,
                business_id_value,
                [int(item["id"]) for item in gallery_reorder],
            )
            if len(existing_reorder_items) != len(gallery_reorder):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="One or more gallery images for reorder were not found",
                )
            business_repository.reorder_business_gallery_items(
                db, business_id_value, gallery_reorder
            )

        gallery_items_to_add = _build_gallery_items_to_add(
            update_data.get("gallery_items") or [],
            saved_upload_urls,
            base_sort_order=business_repository.get_business_gallery_max_sort_order(
                db, business_id_value
            ),
        )
        if gallery_items_to_add:
            business_repository.add_business_gallery_items(
                db, business_id_value, gallery_items_to_add
            )

        db.commit()
    except Exception:
        db.rollback()
        for upload_url in saved_upload_urls:
            delete_upload(upload_url)
        raise

    for upload_url in delete_after_commit:
        delete_upload(upload_url)

    return get_business(db, business_id_value)


def delete_business(db: Session, business_id: int):
    business = business_repository.get_business_details_by_id(db, business_id)
    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business not found"
        )

    delete_urls = [
        str(getattr(image, "image_url"))
        for image in business.gallery_images or []
        if getattr(image, "image_url", None)
    ]
    for single_url in [
        getattr(business, "logo_url", None),
        getattr(business, "cover_image_url", None),
    ]:
        if single_url:
            delete_urls.append(str(single_url))

    interior_photos = getattr(business, "interior_photos", None)
    if isinstance(interior_photos, str) and interior_photos.strip():
        delete_urls.extend(
            [photo.strip() for photo in interior_photos.split(",") if photo.strip()]
        )

    business_repository.delete_business(db, business)
    for upload_url in delete_urls:
        delete_upload(upload_url)
    return business


def toggle_active(db: Session, business_id: int):
    business = business_repository.get_business_by_id(db, business_id)
    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business not found"
        )
    current_is_active = bool(getattr(business, "is_active", False))
    business_repository.update_business_instance(
        db, business, {"is_active": not current_is_active}
    )
    db.commit()
    return get_business(db, business_id)


def get_business_details(db: Session, business_id: int):
    business = business_repository.get_business_details_by_id(db, business_id)
    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business not found"
        )

    latest_reviews = business_review_repository.get_latest_business_reviews(
        db, business_id=business_id, limit=5
    )
    return _serialize_business_details(business, latest_reviews)
