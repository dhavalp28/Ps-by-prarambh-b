"""
Migration script to add missing columns to categories and sub_categories tables.

This script adds the 'icon' column that was missing from the database schema.
"""

from sqlalchemy import text
from db.session import engine


def add_missing_columns():
    """Add missing columns to categories and sub_categories tables"""
    
    with engine.connect() as connection:
        try:
            # Check if icon column exists in categories table
            result = connection.execute(
                text("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'categories' AND column_name = 'icon'
                """)
            )
            
            if not result.fetchone():
                print("Adding 'icon' column to categories table...")
                connection.execute(
                    text("ALTER TABLE categories ADD COLUMN icon VARCHAR NULL")
                )
                connection.commit()
                print("✓ Successfully added 'icon' column to categories table")
            else:
                print("✓ 'icon' column already exists in categories table")
            
            # Check if icon column exists in sub_categories table
            result = connection.execute(
                text("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'sub_categories' AND column_name = 'icon'
                """)
            )
            
            if not result.fetchone():
                print("Adding 'icon' column to sub_categories table...")
                connection.execute(
                    text("ALTER TABLE sub_categories ADD COLUMN icon VARCHAR NULL")
                )
                connection.commit()
                print("✓ Successfully added 'icon' column to sub_categories table")
            else:
                print("✓ 'icon' column already exists in sub_categories table")
            
            print("\n✓ All missing columns have been added successfully!")
            
        except Exception as e:
            print(f"✗ Error adding columns: {str(e)}")
            raise


if __name__ == "__main__":
    print("Starting migration: Add missing columns to categories and sub_categories tables\n")
    add_missing_columns()
    print("\nMigration completed!")
