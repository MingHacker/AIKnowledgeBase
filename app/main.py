from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .core.config import settings
from .core.database import engine, Base
from .api.api_v1.api import api_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    openapi_url=f"/api/v1/openapi.json" if settings.debug else None,
    debug=settings.debug
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Create upload directory if it doesn't exist
os.makedirs(settings.upload_directory, exist_ok=True)
os.makedirs(settings.chroma_persist_directory, exist_ok=True)

# Serve uploaded files
if os.path.exists(settings.upload_directory):
    app.mount("/uploads", StaticFiles(directory=settings.upload_directory), name="uploads")


@app.get("/")
async def root():
    return {"message": "AI Knowledge Base API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.environment}