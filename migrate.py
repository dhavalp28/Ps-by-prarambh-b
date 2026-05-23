"""
Migration script — run once to sync the users table with the new schema.

What it does:
  1. Creates states / cities / categories / sub_categories / banners tables if missing
  2. Adds state_id and city_id FK columns to users (if not already there)
  3. Drops the old state and city string columns from users (if still there)

Run from the app/ directory:
    python migrate.py
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def run():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        print("=== Starting migration ===\n")

        # ── 1. Create states table ─────────────────────────────────────────
        cur.execute("""
            CREATE TABLE IF NOT EXISTS states (
                id         SERIAL PRIMARY KEY,
                name       VARCHAR NOT NULL UNIQUE,
                is_active  BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        print("✓ states table ready")

        # ── 2. Create cities table ─────────────────────────────────────────
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cities (
                id         SERIAL PRIMARY KEY,
                name       VARCHAR NOT NULL,
                state_id   INTEGER NOT NULL REFERENCES states(id) ON DELETE CASCADE,
                is_active  BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        print("✓ cities table ready")

        # ── 3. Create categories table ─────────────────────────────────────
        cur.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id          SERIAL PRIMARY KEY,
                name        VARCHAR NOT NULL UNIQUE,
                description VARCHAR,
                is_active   BOOLEAN NOT NULL DEFAULT TRUE,
                created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        print("✓ categories table ready")

        # ── 4. Create sub_categories table ────────────────────────────────
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sub_categories (
                id          SERIAL PRIMARY KEY,
                name        VARCHAR NOT NULL,
                description VARCHAR,
                category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
                is_active   BOOLEAN NOT NULL DEFAULT TRUE,
                created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        print("✓ sub_categories table ready")

        # ── 5. Create banners table ────────────────────────────────────────
        cur.execute("""
            CREATE TABLE IF NOT EXISTS banners (
                id           SERIAL PRIMARY KEY,
                title        VARCHAR NOT NULL UNIQUE,
                subtitle     VARCHAR,
                image_url    VARCHAR NOT NULL,
                redirect_url VARCHAR,
                description  TEXT,
                sort_order   INTEGER NOT NULL DEFAULT 0,
                is_active    BOOLEAN NOT NULL DEFAULT TRUE,
                created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        print("✓ banners table ready")

        # ── 6. Check which columns exist on users ──────────────────────────
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users';
        """)
        existing_cols = {row[0] for row in cur.fetchall()}
        print(f"\nExisting users columns: {sorted(existing_cols)}")

        # ── 7. Add state_id column if missing ──────────────────────────────
        if "state_id" not in existing_cols:
            # Add as nullable first (existing rows can't satisfy NOT NULL yet)
            cur.execute("""
                ALTER TABLE users
                ADD COLUMN state_id INTEGER REFERENCES states(id);
            """)
            print("✓ Added users.state_id")
        else:
            print("– users.state_id already exists, skipping")

        # ── 8. Add city_id column if missing ───────────────────────────────
        if "city_id" not in existing_cols:
            cur.execute("""
                ALTER TABLE users
                ADD COLUMN city_id INTEGER REFERENCES cities(id);
            """)
            print("✓ Added users.city_id")
        else:
            print("– users.city_id already exists, skipping")

        # ── 9. Drop old string columns if still present ────────────────────
        if "state" in existing_cols:
            cur.execute("ALTER TABLE users DROP COLUMN state;")
            print("✓ Dropped users.state (old string column)")
        else:
            print("– users.state already removed, skipping")

        if "city" in existing_cols:
            cur.execute("ALTER TABLE users DROP COLUMN city;")
            print("✓ Dropped users.city (old string column)")
        else:
            print("– users.city already removed, skipping")

        conn.commit()
        print("\n=== Migration completed successfully ===")
        print("\nNOTE: state_id and city_id are nullable for now.")
        print("Existing users have NULL values — assign them via the admin panel.")

    except Exception as e:
        conn.rollback()
        print(f"\n✗ Migration failed: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    run()
