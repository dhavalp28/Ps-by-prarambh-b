from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    )
    
    # Auto-detect if running on Vercel and use connection pooler
    ENVIRONMENT = os.getenv("VERCEL_ENV", "development")
    
    @classmethod
    def get_database_url(cls):
        """Get appropriate database URL based on environment"""
        db_url = cls.DATABASE_URL
        
        # If in production on Vercel and using direct connection, suggest pooler
        if cls.ENVIRONMENT == "production" and "pooler" not in db_url:
            print("⚠️  Warning: Using direct connection in production. Consider using connection pooler.")
        
        return db_url

settings = Settings()