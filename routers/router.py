from fastapi import APIRouter
from routers.routes import auth, user, category, sub_category, state, city, banner, vendor, business, subscription_plan, redemption, qr_code, business_code, profile

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(profile.router, prefix="/auth", tags=["Profile"])
api_router.include_router(user.router, prefix="/users", tags=["User"])
api_router.include_router(vendor.router, prefix="/vendors", tags=["Vendor"])
api_router.include_router(business.router, prefix="/businesses", tags=["Business"])
api_router.include_router(state.router, prefix="/states", tags=["State"])
api_router.include_router(city.router, prefix="/cities", tags=["City"])
api_router.include_router(category.router, prefix="/categories", tags=["Category"])
api_router.include_router(sub_category.router, prefix="/sub-categories", tags=["Sub-Category"])
api_router.include_router(banner.router, prefix="/banners", tags=["Banner"])
api_router.include_router(subscription_plan.router, prefix="/subscription-plans", tags=["Subscription Plan"])
api_router.include_router(redemption.router, prefix="/redemptions", tags=["Redemption"])
api_router.include_router(qr_code.router, prefix="/qr-codes", tags=["QR Code"])
api_router.include_router(business_code.router, prefix="/business-codes", tags=["Business Code"])