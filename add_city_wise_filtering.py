#!/usr/bin/env python
"""
Script to add city_id column to category, sub_category, and banner tables
Run this script to update your database for city-wise filtering
"""

from sqlalchemy import text
from db.session import engine

def add_city_columns():
    """Add city_id columns to category, sub_category, and banner tables"""
    
    with engine.connect() as connection:
        try:
            # Add city_id to categories table
            print("Adding 'city_id' column to categories table...")
            try:
                connection.execute(
                    text("""
                        ALTER TABLE categories 
                        ADD COLUMN city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE
                    """)
                )
                connection.commit()
                print("✓ Column 'city_id' added to categories table")
            except Exception as e:
                if "already exists" in str(e):
                    print("✓ Column 'city_id' already exists in categories table")
                else:
                    raise
            
            # Add city_id to sub_categories table
            print("Adding 'city_id' column to sub_categories table...")
            try:
                connection.execute(
                    text("""
                        ALTER TABLE sub_categories 
                        ADD COLUMN city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE
                    """)
                )
                connection.commit()
                print("✓ Column 'city_id' added to sub_categories table")
            except Exception as e:
                if "already exists" in str(e):
                    print("✓ Column 'city_id' already exists in sub_categories table")
                else:
                    raise
            
            # Add city_id to banners table
            print("Adding 'city_id' column to banners table...")
            try:
                connection.execute(
                    text("""
                        ALTER TABLE banners 
                        ADD COLUMN city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE
                    """)
                )
                connection.commit()
                print("✓ Column 'city_id' added to banners table")
            except Exception as e:
                if "already exists" in str(e):
                    print("✓ Column 'city_id' already exists in banners table")
                else:
                    raise
            
            return True
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Add City-Wise Filtering")
    print("=" * 60)
    
    success = add_city_columns()
    
    if success:
        print("\n✓ Migration completed successfully!")
        print("\nYou can now use city-wise filtering for:")
        print("  - GET /businesses?city_id=1")
        print("  - GET /categories?city_id=1")
        print("  - GET /sub-categories?city_id=1")
        print("  - GET /banners?city_id=1")
        print("\nIf city_id is not provided, all records are returned.")
    else:
        print("\n✗ Migration failed. Please check the error above.")
