from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from core.config import settings

# For Supabase connection pooler, use NullPool to avoid connection issues
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,
    connect_args={
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
    }
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)