# Database Migration Guide - OTP Authentication

This guide explains how to migrate your database to support the new OTP-based authentication system.

## Overview

The OTP authentication system requires:
1. New `otp_sessions` table
2. New `is_phone_verified` column in `users` table
3. Make `hashed_password` nullable in `users` table

## Option 1: Using Alembic (Recommended)

### Step 1: Create Migration File

```bash
# Activate virtual environment
.\venv\Scripts\activate

# Generate migration
alembic revision --autogenerate -m "Add OTP authentication support"
```

This will create a new migration file in `db/migrations/versions/`.

### Step 2: Review Migration File

Open the generated migration file and verify it includes:

```python
def upgrade():
    # Create otp_sessions table
    op.create_table(
        'otp_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('otp', sa.String(), nullable=False),
        sa.Column('purpose', sa.String(), nullable=False),
        sa.Column('temp_user_data', sa.String(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_otp_sessions_phone'), 'otp_sessions', ['phone'], unique=False)
    
    # Add columns to users table
    op.add_column('users', sa.Column('is_phone_verified', sa.Boolean(), nullable=False, server_default='false'))
    
    # Make hashed_password nullable
    op.alter_column('users', 'hashed_password', existing_type=sa.String(), nullable=True)

def downgrade():
    # Reverse the changes
    op.alter_column('users', 'hashed_password', existing_type=sa.String(), nullable=False)
    op.drop_column('users', 'is_phone_verified')
    op.drop_index(op.f('ix_otp_sessions_phone'), table_name='otp_sessions')
    op.drop_table('otp_sessions')
```

### Step 3: Run Migration

```bash
# Run the migration
alembic upgrade head

# Verify migration
alembic current
```

### Step 4: Verify Database

```bash
# Connect to your database and verify tables
# For PostgreSQL:
\dt  # List all tables
\d otp_sessions  # Describe otp_sessions table
\d users  # Describe users table
```

---

## Option 2: Manual SQL (If Alembic is not configured)

### Step 1: Create OTP Sessions Table

```sql
CREATE TABLE otp_sessions (
    id SERIAL PRIMARY KEY,
    phone VARCHAR NOT NULL,
    otp VARCHAR NOT NULL,
    purpose VARCHAR NOT NULL,
    temp_user_data VARCHAR,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on phone for faster lookups
CREATE INDEX ix_otp_sessions_phone ON otp_sessions(phone);
```

### Step 2: Update Users Table

```sql
-- Add is_phone_verified column
ALTER TABLE users ADD COLUMN is_phone_verified BOOLEAN NOT NULL DEFAULT FALSE;

-- Make hashed_password nullable
ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL;
```

### Step 3: Verify Changes

```sql
-- Verify otp_sessions table
\d otp_sessions

-- Verify users table changes
\d users
```

---

## Option 3: Using Python Script (For Development)

If you want to create tables programmatically:

```python
# Run this in Python shell or create a script
from db.base import Base
from db.session import engine
from db.models import OtpSession, User

# Create all tables
Base.metadata.create_all(bind=engine)

print("Tables created successfully!")
```

---

## Verification Checklist

After migration, verify:

- [ ] `otp_sessions` table exists with all columns
- [ ] `otp_sessions.phone` column has index
- [ ] `users.is_phone_verified` column exists (default: FALSE)
- [ ] `users.hashed_password` column is nullable
- [ ] All existing users have `is_phone_verified = FALSE`
- [ ] All existing users have `hashed_password` values (not NULL)

### SQL Verification Queries

```sql
-- Check otp_sessions table
SELECT * FROM otp_sessions LIMIT 1;

-- Check users table structure
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;

-- Check if is_phone_verified column exists
SELECT COUNT(*) FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'is_phone_verified';

-- Check if hashed_password is nullable
SELECT is_nullable FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'hashed_password';
```

---

## Rollback (If Needed)

### Using Alembic

```bash
# Rollback to previous version
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>
```

### Manual SQL Rollback

```sql
-- Drop otp_sessions table
DROP TABLE IF EXISTS otp_sessions;

-- Remove is_phone_verified column
ALTER TABLE users DROP COLUMN IF EXISTS is_phone_verified;

-- Make hashed_password NOT NULL again
ALTER TABLE users ALTER COLUMN hashed_password SET NOT NULL;
```

---

## Data Migration (If Needed)

### Existing Users

If you have existing users and want to mark them as phone-verified:

```sql
-- Mark all existing users as phone-verified
UPDATE users SET is_phone_verified = TRUE WHERE hashed_password IS NOT NULL;

-- Or mark specific users
UPDATE users SET is_phone_verified = TRUE WHERE id IN (1, 2, 3);
```

---

## Testing After Migration

### Test OTP Session Creation

```python
from db.session import SessionLocal
from db.models import OtpSession
from datetime import datetime, timedelta

db = SessionLocal()

# Create test OTP session
otp_session = OtpSession(
    phone="+919876543210",
    otp="123456",
    purpose="register",
    expires_at=datetime.utcnow() + timedelta(minutes=10),
    attempts=0,
    is_verified=False
)

db.add(otp_session)
db.commit()
db.refresh(otp_session)

print(f"Created OTP session: {otp_session.id}")
```

### Test User Creation with OTP

```python
from db.session import SessionLocal
from db.models import User

db = SessionLocal()

# Create test user with OTP
user = User(
    first_name="Test",
    last_name="User",
    email="test@example.com",
    phone="+919876543210",
    hashed_password=None,  # No password for OTP-only login
    is_phone_verified=True,
    state_id=1,
    city_id=1
)

db.add(user)
db.commit()
db.refresh(user)

print(f"Created user: {user.id}")
```

---

## Troubleshooting

### Issue: "Table already exists"
- **Cause**: Table was already created
- **Solution**: Drop the table first or use `IF NOT EXISTS`

### Issue: "Column already exists"
- **Cause**: Column was already added
- **Solution**: Check existing schema before running migration

### Issue: "Foreign key constraint failed"
- **Cause**: Trying to add constraint on non-existent table
- **Solution**: Ensure all referenced tables exist first

### Issue: "Alembic revision not found"
- **Cause**: Migration file doesn't exist
- **Solution**: Create migration using `alembic revision --autogenerate`

---

## Environment-Specific Notes

### Local Development
- Use SQLite or local PostgreSQL
- Can safely drop and recreate tables
- Use Option 3 (Python script) for quick setup

### Staging
- Use Alembic migrations
- Test migrations before production
- Keep migration history

### Production
- Use Alembic migrations
- Test on staging first
- Have backup before migration
- Monitor migration execution
- Have rollback plan ready

---

## Post-Migration Steps

1. **Update Backend Code**
   - Pull latest code with OTP authentication
   - Restart backend server

2. **Update Frontend**
   - Update to use new OTP endpoints
   - Test registration and login flows

3. **Monitor**
   - Check application logs
   - Monitor database performance
   - Verify OTP sessions are being created

4. **Cleanup**
   - Remove old password-based auth if not needed
   - Archive old migration files if needed

---

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Alembic documentation: https://alembic.sqlalchemy.org/
3. Check PostgreSQL documentation: https://www.postgresql.org/docs/
4. Contact backend team

---

## Version History

- **v1.0** (2024-05-27): Initial migration guide for OTP authentication
