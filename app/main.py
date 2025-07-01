"""
FastAPI main application.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import aggregates, links
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, logger
from app.middleware import setup_logging_middleware

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
    redoc_url="/redoc",
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
app.include_router(links.router, tags=["links"])
app.include_router(aggregates.router, tags=["aggregations"])


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
        "debug": settings.debug,
    }


@app.get("/health")
async def health_check(request: Request):
    """Health check endpoint."""
    # Access the request-scoped logger
    request.state.logger.info("Health check performed")

    return {"status": "healthy", "debug": settings.debug}


# Log application startup
logger.info(f"Application initialized: {settings.app_name} v{settings.app_version}")
