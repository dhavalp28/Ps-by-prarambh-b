#!/usr/bin/env python
"""
Script to add is_phone_verified column to users table
Run this script to update your database
"""

from sqlalchemy import text
from db.session import engine

def add_is_phone_verified_column():
    """Add is_phone_verified column to users table"""
    
    with engine.connect() as connection:
        try:
            # Check if column already exists
            result = connection.execute(
                text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='is_phone_verified'
                """)
            )
            
            if result.fetchone():
                print("✓ Column 'is_phone_verified' already exists")
                return True
            
            # Add the column
            print("Adding 'is_phone_verified' column to users table...")
            connection.execute(
                text("""
                    ALTER TABLE users 
                    ADD COLUMN is_phone_verified BOOLEAN NOT NULL DEFAULT FALSE
                """)
            )
            connection.commit()
            print("✓ Column 'is_phone_verified' added successfully")
            
            # Make hashed_password nullable
            print("Making 'hashed_password' nullable...")
            connection.execute(
                text("""
                    ALTER TABLE users 
                    ALTER COLUMN hashed_password DROP NOT NULL
                """)
            )
            connection.commit()
            print("✓ Column 'hashed_password' is now nullable")
            
            return True
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

if __name__ == "__main__":
    print("=" * 50)
    print("Database Migration: Add OTP Authentication Support")
    print("=" * 50)
    
    success = add_is_phone_verified_column()
    
    if success:
        print("\n✓ Migration completed successfully!")
        print("\nYou can now use the OTP authentication system.")
    else:
        print("\n✗ Migration failed. Please check the error above.")
