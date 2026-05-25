from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
import os

from core.config import settings

# Determine if we're in production (Vercel)
is_production = os.getenv("VERCEL_ENV") == "production"

# For production/serverless, use NullPool (no connection pooling)
# For development, use QueuePool for better connection management
pool_class = NullPool if is_production else QueuePool

try:
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=pool_class,
        connect_args={
            "connect_timeout": 10,
            "keepalives": 1,
            "keepalives_idle": 30,
            "sslmode": "require",
        },
        # For production, reduce pool size
        pool_size=5 if not is_production else 1,
        max_overflow=10 if not is_production else 0,
        echo=False,
    )
except Exception as e:
    print(f"Error creating database engine: {e}")
    raise

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)