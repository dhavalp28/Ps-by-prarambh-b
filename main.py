import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router

app = FastAPI(title="MyAreaPlus API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads", "banners")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Static files
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "uploads")),
    name="static",
)

# Routes
app.include_router(api_router)

# Root route
@app.get("/")
def root():
    return {"message": "API Running Successfully"}
