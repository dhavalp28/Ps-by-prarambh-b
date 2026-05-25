from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
import ssl
import os

from core.config import settings

# Determine if we're in production (Vercel)
is_production = os.getenv("VERCEL_ENV") == "production"

# For production/serverless, use NullPool (no connection pooling)
# For development, use QueuePool for better connection management
pool_class = NullPool if is_production else QueuePool

# Create SSL context for secure connections
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

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
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)