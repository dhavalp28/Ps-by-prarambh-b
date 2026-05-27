from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

# Neon (and some roles) leave search_path unset; DDL without a schema then fails with
# "no schema has been selected to create in". Pin default schema explicitly.
PUBLIC_SCHEMA_METADATA = MetaData(schema="public")

Base = declarative_base(metadata=PUBLIC_SCHEMA_METADATA)
