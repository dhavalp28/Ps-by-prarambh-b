import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from api.router import api_router
from db.session import engine
from db.base import Base

Base.metadata.create_all(bind=engine)

# Writable upload root (bundle is read-only on Vercel except /tmp)
_BASE_DIR = (
    "/tmp/ps_by_prarambh"
    if os.environ.get("VERCEL")
    else os.path.dirname(__file__)
)

# Ensure upload directory exists
UPLOAD_DIR = os.path.join(_BASE_DIR, "uploads", "banners")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="MyAreaPlus API")

# CORS — allow admin panel origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files at /static
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(_BASE_DIR, "uploads")),
    name="static",
)

app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "API Running Successfully"}
