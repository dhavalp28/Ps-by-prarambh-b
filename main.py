import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.db.session import engine
from app.db.base import Base

Base.metadata.create_all(bind=engine)

# Ensure upload directory exists
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads", "banners")
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
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "uploads")),
    name="static",
)

app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "API Running Successfully"}
