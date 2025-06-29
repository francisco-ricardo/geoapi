"""
FastAPI main application.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import links
from app.core.config import get_settings
from app.core.logging import logger, get_logger
from app.middleware import setup_logging_middleware
from app.core.exceptions import register_exception_handlers

# Get settings
settings = get_settings()

# Configure logger
logger = get_logger(name="geoapi", log_level=settings.log_level)

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

# Setup logging middleware
setup_logging_middleware(app)

# Register exception handlers
register_exception_handlers(app)

# Include API routes
app.include_router(links.router, prefix="/api/v1", tags=["links"])

@app.get("/")
async def root(request: Request):
    """Root endpoint with API information."""
    # Access the request-scoped logger
    request.state.logger.info("Root endpoint accessed")
    
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc",
        "debug": settings.debug
    }

@app.get("/health")
async def health_check(request: Request):
    """Health check endpoint."""
    # Access the request-scoped logger
    request.state.logger.info("Health check performed")
    
    return {"status": "healthy", "debug": settings.debug}

# Log application startup
logger.info(f"Application initialized: {settings.app_name} v{settings.app_version}")
