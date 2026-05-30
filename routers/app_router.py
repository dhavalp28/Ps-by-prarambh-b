from fastapi import APIRouter
from routers.routes import app_business

app_router = APIRouter(prefix="/app")
app_router.include_router(
    app_business.router, prefix="/businesses", tags=["App Business"]
)
