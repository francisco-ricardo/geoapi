"""
Application configuration settings.
"""
from functools import lru_cache
from typing import Optional, Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database settings
    database_url: str = Field(
        default="",
        description="PostgreSQL database URL with PostGIS support"
    )
    
    # API settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port") 
    debug: bool = Field(default=False, description="Debug mode")
    
    # Application settings
    app_name: str = Field(default="GeoAPI", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    
    # Logging settings
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    log_format: Literal["console", "json"] = Field(
        default="console",
        description="Logging format (console for development, json for production)"
    )
    log_to_file: bool = Field(
        default=False,
        description="Whether to log to file"
    )
    log_file_path: Optional[str] = Field(
        default="/var/log/geoapi/app.log",
        description="Path to log file if log_to_file is True"
    )
    
    # Observability settings
    enable_tracing: bool = Field(
        default=False,
        description="Enable distributed tracing"
    )
    tracing_provider: Optional[Literal["otlp", "jaeger", "honeycomb"]] = Field(
        default=None,
        description="Tracing provider to use"
    )
    tracing_endpoint: Optional[str] = Field(
        default=None,
        description="Endpoint for tracing provider"
    )
    
    # Mapbox settings (optional for API, required for notebooks)
    mapbox_access_token: Optional[str] = Field(
        default=None, 
        description="Mapbox access token for visualization"
    )
    
    # Data source URLs
    link_info_url: str = Field(
        default="https://cdn.urbansdk.com/data-engineering-interview/link_info.parquet.gz",
        description="URL for link info dataset"
    )
    
    speed_data_url: str = Field(
        default="https://cdn.urbansdk.com/data-engineering-interview/duval_jan1_2024.parquet.gz",
        description="URL for speed data dataset" 
    )
    
    # Time periods configuration
    time_periods: dict = Field(
        default={
            1: {"name": "Overnight", "start": "00:00", "end": "03:59"},
            2: {"name": "Early Morning", "start": "04:00", "end": "06:59"},
            3: {"name": "AM Peak", "start": "07:00", "end": "09:59"},
            4: {"name": "Midday", "start": "10:00", "end": "12:59"},
            5: {"name": "Early Afternoon", "start": "13:00", "end": "15:59"},
            6: {"name": "PM Peak", "start": "16:00", "end": "18:59"},
            7: {"name": "Evening", "start": "19:00", "end": "23:59"},
        }
    )
    
    model_config = {"env_file": ".env", "env_prefix": "GEOAPI_", "case_sensitive": False}


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()

