"""
Tests for configuration settings.
"""
import pytest
from unittest.mock import patch
import os

from app.core.config import get_settings, Settings


class TestSettings:
    """Test configuration settings."""
    
    def test_settings_creation_with_required_fields(self):
        """Test basic settings creation with required database_url."""
        # Note: Settings will still load from .env file even with patch.dict
        # because Pydantic Settings loads from file directly
        settings = Settings(
            database_url="postgresql://test:test@localhost:5432/test"
        )
        
        assert settings.database_url == "postgresql://test:test@localhost:5432/test"
        assert settings.api_host == "0.0.0.0"
        assert settings.api_port == 8000
        assert settings.app_name == "GeoAPI Test"  # From .env file
        # debug will be True because it's loaded from .env file
    
    def test_settings_from_env_variables(self):
        """Test settings loading from environment variables."""
        with patch.dict(os.environ, {
            'GEOAPI_DATABASE_URL': 'postgresql://env:env@localhost:5432/env',
            'GEOAPI_DEBUG': 'true',
            'GEOAPI_APP_NAME': 'Test App',
            'GEOAPI_API_PORT': '9000'
        }):
            settings = Settings()
            
            assert settings.database_url == 'postgresql://env:env@localhost:5432/env'
            assert settings.debug is True
            assert settings.app_name == 'Test App'
            assert settings.api_port == 9000
    
    def test_get_settings_caching(self):
        """Test that get_settings returns cached instance."""
        # Clear cache first
        get_settings.cache_clear()
        
        settings1 = get_settings()
        settings2 = get_settings()
        
        # Should be the same object (cached)
        assert settings1 is settings2
    
    def test_time_periods_structure(self):
        """Test time periods configuration structure."""
        settings = get_settings()
        
        assert isinstance(settings.time_periods, dict)
        assert len(settings.time_periods) == 7
        
        # Check first period
        period_1 = settings.time_periods[1]
        assert period_1["name"] == "Overnight"
        assert period_1["start"] == "00:00"
        assert period_1["end"] == "03:59"
        
        # Check AM Peak period
        period_3 = settings.time_periods[3]
        assert period_3["name"] == "AM Peak"
        assert period_3["start"] == "07:00"
        assert period_3["end"] == "09:59"
    
    def test_data_source_urls(self):
        """Test default data source URLs."""
        settings = get_settings()
        
        assert "link_info.parquet" in settings.link_info_url
        assert "duval_jan1_2024.parquet" in settings.speed_data_url
        assert settings.link_info_url.startswith("https://")
        assert settings.speed_data_url.startswith("https://")
    
    def test_optional_mapbox_token(self):
        """Test optional Mapbox token setting."""
        # Note: Will load from .env file in this environment
        settings = Settings(database_url="test://url")
        
        # Will get empty value since no token is set in .env file
        assert settings.mapbox_access_token == ""
        
        # Test with explicit environment variable override
        with patch.dict(os.environ, {'GEOAPI_MAPBOX_ACCESS_TOKEN': 'test_token_123'}):
            settings_with_token = Settings(database_url="test://url")
            assert settings_with_token.mapbox_access_token == 'test_token_123'
