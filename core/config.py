import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    ENVIRONMENT = os.getenv("VERCEL_ENV", "development")

    # Auth session configuration
    ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    )
    ADMIN_REFRESH_TOKEN_EXPIRE_DAYS = int(
        os.getenv("ADMIN_REFRESH_TOKEN_EXPIRE_DAYS", 14)
    )
    VENDOR_ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("VENDOR_ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    )
    VENDOR_REFRESH_TOKEN_EXPIRE_DAYS = int(
        os.getenv("VENDOR_REFRESH_TOKEN_EXPIRE_DAYS", 14)
    )
    USER_ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("USER_ACCESS_TOKEN_EXPIRE_MINUTES", 43200)
    )
    USER_REFRESH_TOKEN_EXPIRE_DAYS = int(
        os.getenv("USER_REFRESH_TOKEN_EXPIRE_DAYS", 3650)
    )

    # Razorpay
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")


settings = Settings()
