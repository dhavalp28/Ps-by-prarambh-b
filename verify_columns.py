"""
Verification script to check if missing columns were added successfully.
"""

from sqlalchemy import text
from db.session import engine


def verify_columns():
    """Verify that all required columns exist in the database"""
    
    with engine.connect() as connection:
        # Check categories table
        print("Checking categories table columns...")
        result = connection.execute(
            text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'categories' 
                ORDER BY ordinal_position
            """)
        )
        
        categories_columns = [row[0] for row in result]
        print(f"Categories columns: {categories_columns}")
        
        required_categories_columns = ['id', 'name', 'description', 'icon', 'city_id', 'is_active', 'created_at', 'updated_at']
        missing_categories = [col for col in required_categories_columns if col not in categories_columns]
        
        if missing_categories:
            print(f"✗ Missing columns in categories: {missing_categories}")
        else:
            print("✓ All required columns exist in categories table")
        
        # Check sub_categories table
        print("\nChecking sub_categories table columns...")
        result = connection.execute(
            text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'sub_categories' 
                ORDER BY ordinal_position
            """)
        )
        
        sub_categories_columns = [row[0] for row in result]
        print(f"Sub-categories columns: {sub_categories_columns}")
        
        required_sub_categories_columns = ['id', 'name', 'description', 'icon', 'category_id', 'city_id', 'is_active', 'created_at', 'updated_at']
        missing_sub_categories = [col for col in required_sub_categories_columns if col not in sub_categories_columns]
        
        if missing_sub_categories:
            print(f"✗ Missing columns in sub_categories: {missing_sub_categories}")
        else:
            print("✓ All required columns exist in sub_categories table")
        
        # Summary
        print("\n" + "="*50)
        if not missing_categories and not missing_sub_categories:
            print("✓ All columns verified successfully!")
            return True
        else:
            print("✗ Some columns are still missing")
            return False


if __name__ == "__main__":
    print("Verifying database schema...\n")
    success = verify_columns()
    print("\nVerification completed!")
    exit(0 if success else 1)
