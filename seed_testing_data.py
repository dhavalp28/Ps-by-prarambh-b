"""
Seed demo data covering every application table — Gujarat / Ahmedabad themed.

Creates (idempotently via natural keys):

  states · cities · categories · sub_categories
  users · vendors · businesses · banners

Default passwords (User + Vendor):
    TestPass123!

Usage:
    python seed_testing_data.py
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import Session

load_dotenv()

from core.security import hash_password

from db.models.banner import Banner
from db.models.business import Business
from db.models.category import Category
from db.models.city import City
from db.models.state import State
from db.models.sub_category import SubCategory
from db.models.user import User
from db.models.vendor import Vendor
from db.session import SessionLocal

# ---------------------------------------------------------------------------
# Canonical seed keys — change if these collide with production data you care about
# ---------------------------------------------------------------------------
DEFAULT_SEED_PASSWORD = "TestPass123!"
USER_EMAIL = "seed.user.psbyprarambh@example.local"
USER_PHONE = "+919876540001"

VENDOR_EMAIL = "seed.vendor.psbyprarambh@example.local"
VENDOR_PHONE = "+919876540002"
VENDOR_NAME = "Seed Vendor — Ahmedabad Unit"

BUSINESS_NAME = "Shree Shiv Sagar Restaurant (Seed)"
BUSINESS_PHONE = "+917940556677"

BANNER_TITLE_PRIMARY = "[SEED] PS By Prarambh — Welcome Ahmedabad"
BANNER_TITLE_SECONDARY = "[SEED] Discover local businesses"


def get_or_create_state(db: Session, name: str, *, active: bool = True) -> State:
    row = db.execute(select(State).where(State.name == name)).scalar_one_or_none()
    if row:
        print(f"– state '{name}' exists (id={row.id})")
        return row
    row = State(name=name, is_active=active)
    db.add(row)
    db.flush()
    print(f"✓ state '{name}' (id={row.id})")
    return row


def get_or_create_city(
    db: Session,
    *,
    name: str,
    state_id: int,
    active: bool = True,
) -> City:
    row = db.execute(
        select(City).where(City.name == name, City.state_id == state_id)
    ).scalar_one_or_none()
    if row:
        print(f"– city '{name}' (state={state_id}) id={row.id}")
        return row
    row = City(name=name, state_id=state_id, is_active=active)
    db.add(row)
    db.flush()
    print(f"✓ city '{name}' id={row.id}")
    return row


def get_or_create_category(db: Session, name: str, description: str | None = None) -> Category:
    row = db.execute(select(Category).where(Category.name == name)).scalar_one_or_none()
    if row:
        print(f"– category '{name}' id={row.id}")
        return row
    row = Category(name=name, description=description, is_active=True)
    db.add(row)
    db.flush()
    print(f"✓ category '{name}' id={row.id}")
    return row


def get_or_create_subcategory(
    db: Session,
    *,
    name: str,
    category_id: int,
    description: str | None = None,
) -> SubCategory:
    row = db.execute(
        select(SubCategory).where(
            SubCategory.name == name,
            SubCategory.category_id == category_id,
        )
    ).scalar_one_or_none()
    if row:
        print(f"– sub_category '{name}' cat={category_id} id={row.id}")
        return row
    row = SubCategory(
        name=name,
        description=description,
        category_id=category_id,
        is_active=True,
    )
    db.add(row)
    db.flush()
    print(f"✓ sub_category '{name}' id={row.id}")
    return row


def get_or_create_user(
    db: Session,
    *,
    email: str,
    phone: str,
    first_name: str,
    last_name: str,
    state_id: int,
    city_id: int,
    pwd_hash: str,
) -> User:
    row = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if row:
        print(f"– user email={email} id={row.id}")
        return row
    row = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        state_id=state_id,
        city_id=city_id,
        referral_code="SEEDAHD001",
        hashed_password=pwd_hash,
    )
    db.add(row)
    db.flush()
    print(f"✓ user email={email} id={row.id}")
    return row


def get_or_create_vendor(
    db: Session,
    *,
    email: str,
    phone: str,
    name: str,
    state_id: int,
    city_id: int,
    pwd_hash: str,
) -> Vendor:
    row = db.execute(select(Vendor).where(Vendor.email == email)).scalar_one_or_none()
    if row:
        print(f"– vendor email={email} id={row.id}")
        return row
    row = Vendor(
        name=name,
        email=email,
        phone=phone,
        alt_phone="+919876543210",
        gender="male",
        state_id=state_id,
        city_id=city_id,
        hashed_password=pwd_hash,
        is_active=True,
    )
    db.add(row)
    db.flush()
    print(f"✓ vendor email={email} id={row.id}")
    return row


def get_or_create_business(
    db: Session,
    *,
    business_phone: str,
    business_name: str,
    vendor: Vendor,
    state_id: int,
    city_id: int,
    category_id: int,
    sub_category_id: int,
) -> Business:
    row = db.execute(
        select(Business).where(Business.business_phone == business_phone)
    ).scalar_one_or_none()
    if row:
        print(f"– business phone={business_phone} id={row.id}")
        return row
    row = Business(
        business_name=business_name,
        title="Authentic Ahmedabad thali · seed listing",
        business_phone=business_phone,
        vendor_email=vendor.email,
        website="https://example.local/shiv-sagar-seed",
        logo_url="https://placehold.co/200x200/png?text=SS",
        cover_image_url="https://placehold.co/1200x400/png?text=Seed+Restaurant",
        owner_id=vendor.id,
        business_address="CG Road, Navrangpura, Ahmedabad, Gujarat 380009",
        map_link_url="https://maps.app.goo.gl/seed-ahmedabad",
        latitude=23.0365,
        longitude=72.5611,
        business_type="Pure vegetarian dining",
        state_id=state_id,
        city_id=city_id,
        category_id=category_id,
        sub_category_id=sub_category_id,
        open_time="08:30",
        close_time="23:30",
        cuisine="Gujarati · North Indian",
        open_days="Mon,Tue,Wed,Thu,Fri,Sat,Sun",
        about_us="Demo listing for PS By Prarambh — seeded for QA.",
        description="Test business row linked to seeded vendor/category.",
        instagram_url="https://instagram.com/example",
        payment_methods="UPI,Cards,Cash",
        highlights="Jain-friendly,Air-conditioned",
        amenities="Parking,Wi‑Fi",
        is_active=True,
    )
    db.add(row)
    db.flush()
    print(f"✓ business '{business_name}' id={row.id}")
    return row


def get_or_create_banner(
    db: Session,
    *,
    title: str,
    subtitle: str | None,
    image_url: str,
    redirect_url: str | None,
    sort_order: int,
) -> Banner:
    row = db.execute(select(Banner).where(Banner.title == title)).scalar_one_or_none()
    if row:
        print(f"– banner title={title!r} id={row.id}")
        return row
    row = Banner(
        title=title,
        subtitle=subtitle,
        image_url=image_url,
        redirect_url=redirect_url,
        description="Automated seed row — safe to delete in production cleanup.",
        sort_order=sort_order,
        is_active=True,
    )
    db.add(row)
    db.flush()
    print(f"✓ banner {title!r} id={row.id}")
    return row


def main() -> None:
    if not os.getenv("DATABASE_URL"):
        print("DATABASE_URL is not set (`.env`).", file=sys.stderr)
        sys.exit(1)

    db = SessionLocal()
    try:
        print("=== PS By Prarambh — full-table seed (Gujarat / Ahmedabad) ===\n")

        guj = get_or_create_state(db, "Gujarat")
        ahd = get_or_create_city(db, name="Ahmedabad", state_id=guj.id)
        get_or_create_city(db, name="Gandhinagar", state_id=guj.id)

        food = get_or_create_category(
            db, "Food & Dining", description="Restaurants and food places"
        )
        retail = get_or_create_category(
            db, "Retail & Shops", description="Retail and neighbourhood shops"
        )
        svc = get_or_create_category(
            db, "Professional Services",
            description="Salons, repairs, tutors, clinics (seed)",
        )

        sub_thali = get_or_create_subcategory(
            db,
            name="Thali Restaurant",
            category_id=food.id,
            description="Gujarati / Rajasthani thalis",
        )
        get_or_create_subcategory(
            db,
            name="Street Snacks",
            category_id=food.id,
            description="Khakhra, fafda, dhokla, etc.",
        )
        get_or_create_subcategory(
            db,
            name="Fashion & Lifestyle",
            category_id=retail.id,
            description="Local apparel and boutiques",
        )
        get_or_create_subcategory(
            db,
            name="Home & Repairs",
            category_id=svc.id,
            description="Electrician, carpenter, plumbers",
        )

        pwd_hash = hash_password(DEFAULT_SEED_PASSWORD)

        get_or_create_user(
            db,
            email=USER_EMAIL,
            phone=USER_PHONE,
            first_name="Meera",
            last_name="Shah",
            state_id=guj.id,
            city_id=ahd.id,
            pwd_hash=pwd_hash,
        )

        vendor = get_or_create_vendor(
            db,
            email=VENDOR_EMAIL,
            phone=VENDOR_PHONE,
            name=VENDOR_NAME,
            state_id=guj.id,
            city_id=ahd.id,
            pwd_hash=pwd_hash,
        )

        get_or_create_business(
            db,
            business_phone=BUSINESS_PHONE,
            business_name=BUSINESS_NAME,
            vendor=vendor,
            state_id=guj.id,
            city_id=ahd.id,
            category_id=food.id,
            sub_category_id=sub_thali.id,
        )

        get_or_create_banner(
            db,
            title=BANNER_TITLE_PRIMARY,
            subtitle="Powered by Neon · Gujarat pilot",
            image_url="https://placehold.co/1200x400/png?text=PS+By+Prarambh",
            redirect_url="/api/v1",
            sort_order=0,
        )
        get_or_create_banner(
            db,
            title=BANNER_TITLE_SECONDARY,
            subtitle="Bhojan · Bazars · Bazaar days",
            image_url="https://placehold.co/1200x400/png?text=Shop+Ahmedabad",
            redirect_url="/api/v1/categories/",
            sort_order=1,
        )

        db.commit()

        print("\n=== Tables touched ===")
        print(
            "  states · cities · categories · sub_categories · users · vendors · businesses · banners"
        )
        print("\n=== Demo logins (password for both) ===")
        print(f"  User:   email={USER_EMAIL}   phone={USER_PHONE}")
        print(f"  Vendor: email={VENDOR_EMAIL}  phone={VENDOR_PHONE}")
        print(f"  Password (both): {DEFAULT_SEED_PASSWORD}")
        print("\n✓ Seed complete.\n")

    except Exception as e:
        db.rollback()
        print(f"\n✗ Seed failed: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
