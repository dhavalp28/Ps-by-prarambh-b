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
    # Build engine kwargs based on pool class
    engine_kwargs = {
        "poolclass": pool_class,
        "connect_args": {
            "connect_timeout": 10,
            "keepalives": 1,
            "keepalives_idle": 30,
            "sslmode": "require",
        },
        "echo": False,
    }
    
    # Only add pool_size and max_overflow for QueuePool (not NullPool)
    if not is_production:
        engine_kwargs["pool_size"] = 5
        engine_kwargs["max_overflow"] = 10
    
    engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
except Exception as e:
    print(f"Error creating database engine: {e}")
    raise

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)