import os

from core.config import settings
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

# Determine if we're in production (Vercel)
is_production = os.getenv("VERCEL_ENV") == "production"

# For production/serverless, use NullPool (no connection pooling)
# For development, use QueuePool for better connection management
pool_class = NullPool if is_production else QueuePool

try:
    connect_args = {
        "connect_timeout": 30,
    }

    database_url = settings.DATABASE_URL or ""
    if database_url.startswith("postgresql"):
        connect_args["sslmode"] = "require"

        # Keepalive options are helpful for psycopg2/Postgres, but can be flaky on
        # some Windows/local network combinations. Allow disabling via env.
        if os.getenv("DB_ENABLE_KEEPALIVES", "0").lower() in ("1", "true", "yes"):
            connect_args.update(
                {
                    "keepalives": 1,
                    "keepalives_idle": 30,
                    "keepalives_interval": 10,
                    "keepalives_count": 5,
                }
            )

    engine_kwargs = {
        "poolclass": pool_class,
        "connect_args": connect_args,
        "echo": False,
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # Only add pool_size and max_overflow for QueuePool (not NullPool)
    if not is_production:
        engine_kwargs["pool_size"] = 5
        engine_kwargs["max_overflow"] = 10

    engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

    @event.listens_for(engine, "connect")
    def _set_search_path(dbapi_conn, connection_record):  # noqa: ARG001
        cur = dbapi_conn.cursor()
        cur.execute("SET search_path TO public")
        cur.close()
except Exception as e:
    print(f"Error creating database engine: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
