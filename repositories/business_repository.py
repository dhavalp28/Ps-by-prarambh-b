from typing import Optional

from db.models.business import Business
from db.models.business_gallery import BusinessGallery
from db.models.business_service_facility import BusinessServiceFacility
from db.models.city import City
from db.models.coupon import Coupon
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload, selectinload


def _business_load_options(include_details: bool = False):
    options = [
        joinedload(Business.state),
        joinedload(Business.city),
        joinedload(Business.category),
        joinedload(Business.sub_category),
        joinedload(Business.owner),
        joinedload(Business.brand),
    ]

    if include_details:
        options.extend(
            [
                selectinload(Business.coupons),
                selectinload(Business.gallery_images),
                selectinload(Business.service_facility_links).joinedload(
                    BusinessServiceFacility.facility
                ),
            ]
        )

    return options


def get_all_businesses(db: Session, city_id: Optional[int] = None):
    query = db.query(Business).options(*_business_load_options())
    if city_id:
        query = query.filter(Business.city_id == city_id)
    return query.order_by(Business.created_at.desc()).all()


def get_business_by_id(db: Session, business_id: int):
    return (
        db.query(Business)
        .options(*_business_load_options())
        .filter(Business.id == business_id)
        .first()
    )


def get_business_details_by_id(db: Session, business_id: int):
    return (
        db.query(Business)
        .options(*_business_load_options(include_details=True))
        .filter(Business.id == business_id)
        .first()
    )


def get_businesses_by_ids(db: Session, business_ids: list[int]):
    if not business_ids:
        return []
    return (
        db.query(Business)
        .options(*_business_load_options())
        .filter(Business.id.in_(business_ids))
        .all()
    )


def get_businesses_by_brand_id(db: Session, brand_id: int):
    return (
        db.query(Business)
        .options(*_business_load_options())
        .filter(Business.brand_id == brand_id)
        .all()
    )


def search_branches_by_brand_id(
    db: Session,
    brand_id: int,
    search: Optional[str] = None,
    exclude_business_id: Optional[int] = None,
    limit: int = 50,
):
    query = (
        db.query(Business)
        .options(
            joinedload(Business.city).joinedload(City.state),
            joinedload(Business.brand),
        )
        .filter(Business.brand_id == brand_id, Business.is_active == True)
    )

    if exclude_business_id is not None:
        query = query.filter(Business.id != exclude_business_id)

    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Business.business_name.ilike(term),
                Business.business_address.ilike(term),
            )
        )

    return (
        query.order_by(Business.business_name.asc(), Business.id.asc())
        .limit(limit)
        .all()
    )


def get_businesses_by_owner_id(db: Session, owner_id: int):
    return (
        db.query(Business)
        .options(*_business_load_options(), joinedload(Business.business_code))
        .filter(Business.owner_id == owner_id)
        .order_by(Business.created_at.desc())
        .all()
    )


def create_business_instance(db: Session, data: dict):
    business = Business(**data)
    db.add(business)
    db.flush()
    return business


def update_business_instance(db: Session, business: Business, update_data: dict):
    for key, value in update_data.items():
        setattr(business, key, value)
    db.flush()
    return business


def delete_business(db: Session, business: Business):
    db.delete(business)
    db.commit()


def replace_business_facilities(db: Session, business_id: int, facility_ids: list[int]):
    db.query(BusinessServiceFacility).filter(
        BusinessServiceFacility.business_id == business_id
    ).delete(synchronize_session=False)

    unique_ids: list[int] = []
    for facility_id in facility_ids:
        facility_id = int(facility_id)
        if facility_id > 0 and facility_id not in unique_ids:
            unique_ids.append(facility_id)

    for facility_id in unique_ids:
        db.add(
            BusinessServiceFacility(
                business_id=business_id,
                facility_id=facility_id,
            )
        )

    db.flush()


def get_business_gallery_max_sort_order(db: Session, business_id: int) -> int:
    value = (
        db.query(func.max(BusinessGallery.sort_order))
        .filter(BusinessGallery.business_id == business_id)
        .scalar()
    )
    return int(value or 0)


def add_business_gallery_items(
    db: Session, business_id: int, gallery_items: list[dict]
):
    created_items: list[BusinessGallery] = []
    for item in gallery_items:
        gallery_item = BusinessGallery(
            business_id=business_id,
            image_url=item["image_url"],
            sort_order=int(item.get("sort_order", 0)),
        )
        db.add(gallery_item)
        created_items.append(gallery_item)
    db.flush()
    return created_items


def get_gallery_items_by_ids(db: Session, business_id: int, gallery_ids: list[int]):
    if not gallery_ids:
        return []
    return (
        db.query(BusinessGallery)
        .filter(
            BusinessGallery.business_id == business_id,
            BusinessGallery.id.in_(gallery_ids),
        )
        .all()
    )


def delete_gallery_items(db: Session, gallery_items: list[BusinessGallery]):
    for gallery_item in gallery_items:
        db.delete(gallery_item)
    db.flush()


def reorder_business_gallery_items(
    db: Session, business_id: int, gallery_reorder: list[dict]
):
    if not gallery_reorder:
        return

    reorder_map = {int(item["id"]): int(item["sort_order"]) for item in gallery_reorder}
    gallery_items = get_gallery_items_by_ids(db, business_id, list(reorder_map.keys()))

    for gallery_item in gallery_items:
        gallery_item_id = int(getattr(gallery_item, "id"))
        if gallery_item_id in reorder_map:
            setattr(gallery_item, "sort_order", int(reorder_map[gallery_item_id]))

    db.flush()


def get_active_coupons_for_business(db: Session, business_id: int):
    return (
        db.query(Coupon)
        .options(joinedload(Coupon.business))
        .filter(Coupon.business_id == business_id, Coupon.is_active == True)
        .order_by(Coupon.created_at.desc(), Coupon.id.desc())
        .all()
    )
