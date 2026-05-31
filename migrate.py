"""
Bootstrap and migrate Postgres schema.

Use this after switching DATABASE_URL to Neon (or any Postgres).

What it does:
  1. Creates ALL tables from SQLAlchemy models under db/models/
     (states, cities, categories, sub_categories, banners, users, vendors,
     businesses, admin_audit_logs, payment_orders, user_subscriptions, redemption_history, … — exact match to ORM definitions).
  2. Applies legacy tweaks on `users` if you upgraded from an old schema:
     adds state_id / city_id / role if missing, drops old VARCHAR state/city columns
     when present, and backfills a default admin user role.

Prerequisites:
  - python-dotenv, sqlalchemy, psycopg2-binary (see requirements.txt)
  - DATABASE_URL set in `.env`, e.g. Neon:
      postgresql://USER:PASSWORD@EP-XXXX.us-east-2.aws.neon.tech/neondb?sslmode=require

Run:
    python migrate.py

Neon quirk: pooled DSN rejects ``options=-c search_path=...`` at connect; use listener + ORM schema.
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, event, inspect, text


def ensure_database_url() -> str:
    load_dotenv()
    url = os.getenv("DATABASE_URL")
    if not url:
        print("DATABASE_URL is not set. Put it in .env or export it.", file=sys.stderr)
        sys.exit(1)
    return url


def create_all_tables(engine) -> None:
    """Register every model against Base.metadata and CREATE TABLE IF missing."""
    import db.models.init  # noqa: F401 — loads all mapped classes onto Base
    from db.base import Base

    print("Creating any missing tables from SQLAlchemy models…")
    Base.metadata.create_all(bind=engine)
    print("✓ Model-driven schema is applied (tables created if they did not exist).")


def migrate_brand_support(engine) -> None:
    """Add brand_id to businesses for older installs."""
    insp = inspect(engine)
    schema = "public"

    if not insp.has_table("businesses", schema=schema):
        print("– businesses table missing; skipping brand support migration")
        return

    cols = {c["name"] for c in insp.get_columns("businesses", schema=schema)}
    if "brand_id" in cols:
        print("– Brand support already present on businesses; nothing to ALTER.")
        return

    with engine.begin() as conn:
        conn.execute(
            text(
                "ALTER TABLE public.businesses ADD COLUMN brand_id INTEGER REFERENCES public.brands(id) ON DELETE SET NULL;"
            )
        )
        print("✓ Added brand_id column to businesses.")


def migrate_business_module_extensions(engine) -> None:
    """Add business review summary columns and supporting indexes for new business module tables."""
    insp = inspect(engine)
    schema = "public"

    if not insp.has_table("businesses", schema=schema):
        print(
            "– businesses table missing; skipping business module extension migration"
        )
        return

    cols = {c["name"] for c in insp.get_columns("businesses", schema=schema)}
    stmts = []

    if "average_rating" not in cols:
        stmts.append(
            "ALTER TABLE public.businesses ADD COLUMN average_rating DOUBLE PRECISION NOT NULL DEFAULT 0;"
        )
    if "total_reviews" not in cols:
        stmts.append(
            "ALTER TABLE public.businesses ADD COLUMN total_reviews INTEGER NOT NULL DEFAULT 0;"
        )

    with engine.begin() as conn:
        for sql in stmts:
            conn.execute(text(sql))
        if stmts:
            print("✓ Added business review summary columns on businesses.")
        else:
            print("– Business review summary columns already present on businesses.")

        conn.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_business_service_facilities_business_facility ON public.business_service_facilities (business_id, facility_id);"
            )
        )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_business_gallery_business_sort_order ON public.business_gallery (business_id, sort_order);"
            )
        )
        conn.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_business_reviews_business_user ON public.business_reviews (business_id, user_id);"
            )
        )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_business_reviews_business_active_updated ON public.business_reviews (business_id, is_active, updated_at DESC);"
            )
        )
        print("✓ Ensured indexes for facilities, gallery, and reviews.")


def migrate_legacy_users(engine) -> None:
    """Handle old installs that stored state/city as strings on users."""
    insp = inspect(engine)
    schema = "public"

    if not insp.has_table("users", schema=schema):
        print(
            "– users table missing (unexpected after create_all); skipping legacy tweaks"
        )
        return

    cols = {c["name"] for c in insp.get_columns("users", schema=schema)}
    print(f"\nusers columns (for legacy checks): {sorted(cols)}")

    stmts = []
    # Add FK columns only if absent (normally already created by SQLAlchemy)
    if "state_id" not in cols:
        stmts.append(
            "ALTER TABLE public.users ADD COLUMN state_id INTEGER REFERENCES public.states(id);"
        )
    if "city_id" not in cols:
        stmts.append(
            "ALTER TABLE public.users ADD COLUMN city_id INTEGER REFERENCES public.cities(id);"
        )
    if "role" not in cols:
        stmts.append(
            "ALTER TABLE public.users ADD COLUMN role VARCHAR NOT NULL DEFAULT 'user';"
        )

    drops = []
    if "state" in cols:
        drops.append("ALTER TABLE public.users DROP COLUMN IF EXISTS state;")
    if "city" in cols:
        drops.append("ALTER TABLE public.users DROP COLUMN IF EXISTS city;")

    if not stmts and not drops:
        print("– Legacy user column migration already satisfied; nothing to ALTER.")
        return

    with engine.begin() as conn:
        for sql in stmts:
            conn.execute(text(sql))
        if stmts:
            print(
                "✓ Added missing FK columns on users (only if your DB predated the ORM)."
            )

        for sql in drops:
            conn.execute(text(sql))
        if drops:
            print(
                "✓ Dropped legacy VARCHAR state/city on users (if they still existed)."
            )

        conn.execute(
            text(
                "UPDATE public.users SET role = 'user' WHERE role IS NULL OR role = ''"
            )
        )
        conn.execute(text("UPDATE public.users SET role = 'admin' WHERE id = 1"))
        print(
            "✓ Backfilled user roles and promoted user id=1 to admin for compatibility."
        )


def migrate_coupon_claim_history_module(engine) -> None:
    """Add coupon claim history fields and subscription usage counters."""
    insp = inspect(engine)
    schema = "public"

    if insp.has_table("redemption_history", schema=schema):
        redemption_cols = {
            c["name"] for c in insp.get_columns("redemption_history", schema=schema)
        }
        with engine.begin() as conn:
            added_redemption_columns = False
            if "coupon_id" not in redemption_cols:
                conn.execute(
                    text(
                        "ALTER TABLE public.redemption_history ADD COLUMN coupon_id INTEGER REFERENCES public.coupons(id);"
                    )
                )
                added_redemption_columns = True
            if "claim_reference" not in redemption_cols:
                conn.execute(
                    text(
                        "ALTER TABLE public.redemption_history ADD COLUMN claim_reference INTEGER;"
                    )
                )
                added_redemption_columns = True

            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_redemption_history_coupon_id ON public.redemption_history (coupon_id);"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS ix_redemption_history_claim_reference ON public.redemption_history (claim_reference);"
                )
            )

            if added_redemption_columns:
                print("✓ Added coupon claim fields to redemption_history.")
            else:
                print("– Coupon claim fields already present on redemption_history.")
    else:
        print(
            "– redemption_history table missing; skipping coupon claim field migration"
        )

    if insp.has_table("user_subscriptions", schema=schema):
        subscription_cols = {
            c["name"] for c in insp.get_columns("user_subscriptions", schema=schema)
        }
        with engine.begin() as conn:
            added_subscription_columns = False
            if "daily_redemption_count" not in subscription_cols:
                conn.execute(
                    text(
                        "ALTER TABLE public.user_subscriptions ADD COLUMN daily_redemption_count INTEGER NOT NULL DEFAULT 0;"
                    )
                )
                added_subscription_columns = True
            if "total_redemption_count" not in subscription_cols:
                conn.execute(
                    text(
                        "ALTER TABLE public.user_subscriptions ADD COLUMN total_redemption_count INTEGER NOT NULL DEFAULT 0;"
                    )
                )
                added_subscription_columns = True
            if "last_redeemed_on" not in subscription_cols:
                conn.execute(
                    text(
                        "ALTER TABLE public.user_subscriptions ADD COLUMN last_redeemed_on DATE;"
                    )
                )
                added_subscription_columns = True

            conn.execute(
                text(
                    """
                    UPDATE public.user_subscriptions us
                    SET total_redemption_count = COALESCE(stats.total_count, 0),
                        daily_redemption_count = CASE
                            WHEN stats.last_redeemed_on = CURRENT_DATE THEN COALESCE(stats.today_count, 0)
                            ELSE 0
                        END,
                        last_redeemed_on = stats.last_redeemed_on
                    FROM (
                        SELECT
                            rh.user_subscription_id,
                            COUNT(*) FILTER (WHERE rh.status = 'success')::INTEGER AS total_count,
                            COUNT(*) FILTER (
                                WHERE rh.status = 'success'
                                  AND DATE(rh.redeemed_at) = CURRENT_DATE
                            )::INTEGER AS today_count,
                            MAX(DATE(rh.redeemed_at)) FILTER (WHERE rh.status = 'success') AS last_redeemed_on
                        FROM public.redemption_history rh
                        GROUP BY rh.user_subscription_id
                    ) AS stats
                    WHERE us.id = stats.user_subscription_id;
                    """
                )
            )

            if added_subscription_columns:
                print("✓ Added usage counters to user_subscriptions.")
            else:
                print("– Usage counters already present on user_subscriptions.")
    else:
        print("– user_subscriptions table missing; skipping usage counter migration")


def migrate_auth_session_module(engine) -> None:
    """Add auth session support and user active flag for session revocation."""
    insp = inspect(engine)
    schema = "public"

    if insp.has_table("users", schema=schema):
        user_cols = {c["name"] for c in insp.get_columns("users", schema=schema)}
        with engine.begin() as conn:
            if "is_active" not in user_cols:
                conn.execute(
                    text(
                        "ALTER TABLE public.users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;"
                    )
                )
                print("✓ Added is_active column to users.")
            else:
                print("– is_active column already present on users.")
    else:
        print("– users table missing; skipping auth user flag migration")

    if insp.has_table("auth_sessions", schema=schema):
        print("– auth_sessions table already present.")
        return

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS public.auth_sessions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES public.users(id),
                    vendor_id INTEGER REFERENCES public.vendors(id),
                    role VARCHAR NOT NULL,
                    entity_type VARCHAR NOT NULL,
                    session_type VARCHAR NOT NULL,
                    session_key VARCHAR NOT NULL UNIQUE,
                    refresh_token_hash VARCHAR NULL,
                    device_id VARCHAR NULL,
                    device_name VARCHAR NULL,
                    device_platform VARCHAR NULL,
                    user_agent TEXT NULL,
                    ip_address VARCHAR NULL,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    last_seen_at TIMESTAMPTZ DEFAULT NOW(),
                    access_expires_at TIMESTAMPTZ NULL,
                    refresh_expires_at TIMESTAMPTZ NULL,
                    revoked_at TIMESTAMPTZ NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            )
        )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_auth_sessions_user_id ON public.auth_sessions (user_id);"
            )
        )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_auth_sessions_vendor_id ON public.auth_sessions (vendor_id);"
            )
        )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_auth_sessions_device_id ON public.auth_sessions (device_id);"
            )
        )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_auth_sessions_session_key ON public.auth_sessions (session_key);"
            )
        )
        print("✓ Added auth_sessions table and indexes.")


def main() -> None:
    DATABASE_URL = ensure_database_url()

    print("Connecting with SQLAlchemy (pool_pre_ping enabled)…\n")

    # Neon pooled hosts reject startup GUCs in libpq `options=` (see Neon docs).
    # We set search_path after connect via the listener below; DDL uses MetaData(schema="public").
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )

    @event.listens_for(engine, "connect")
    def _set_search_path(dbapi_conn, connection_record):  # noqa: ARG001
        cur = dbapi_conn.cursor()
        cur.execute("SET search_path TO public")
        cur.close()

    # Ensure schema exists (some setups have no writable path until this runs)
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS public"))

    # Verify connection early
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    create_all_tables(engine)

    migrate_brand_support(engine)
    migrate_business_module_extensions(engine)
    migrate_legacy_users(engine)
    migrate_coupon_claim_history_module(engine)
    migrate_auth_session_module(engine)

    print("\n=== Done ===")
    print(
        "Ensure Vercel / local .env use the same DATABASE_URL if you migrated to Neon.\n"
    )


if __name__ == "__main__":
    main()
