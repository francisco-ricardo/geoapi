"""
FastAPI main application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import links
from app.core.config import get_settings

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="GeoAPI - Geospatial Traffic Analytics",
    description="API for geospatial traffic data management with PostGIS integration",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(links.router, prefix="/api/v1", tags=["links"])

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "debug": settings.debug
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "debug": settings.debug}
