"""
Pytest configuration and shared fixtures.
"""
import pytest
import os
from datetime import datetime
from unittest.mock import patch

from app.core.database import Base, reset_database_state


@pytest.fixture(scope="session", autouse=True)
def test_settings():
    """Override settings for testing using environment variables.""" 
    import os
    from app.core.config import get_settings
    
    # Clear the cache first
    get_settings.cache_clear()
    
    # Backup all original env vars
    original_env = {}
    test_env_vars = [
        "GEOAPI_DATABASE_URL",
        "GEOAPI_DEBUG", 
        "GEOAPI_APP_NAME",
        "GEOAPI_MAPBOX_ACCESS_TOKEN"
    ]
    
    for var in test_env_vars:
        original_env[var] = os.environ.get(var)
    
    # Set test environment variables
    os.environ["GEOAPI_DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["GEOAPI_DEBUG"] = "true"
    os.environ["GEOAPI_APP_NAME"] = "GeoAPI Test"
    os.environ["GEOAPI_MAPBOX_ACCESS_TOKEN"] = ""  # Empty for test
    
    # Clear cache to pick up new env vars
    get_settings.cache_clear()
    
    yield get_settings()
    
    # Restore original env vars
    for var, value in original_env.items():
        if value is None:
            os.environ.pop(var, None)
        else:
            os.environ[var] = value
    
    # Clear cache one more time
    get_settings.cache_clear()


@pytest.fixture(scope="function")
def test_db_simple(test_settings):
    """Create test database session with simplified models."""
    # Reset database state to use test settings
    reset_database_state()
    
    from app.core.database import get_engine, get_session_factory
    from tests.fixtures.models import ModelBase
    from sqlalchemy import event
    
    # Create engine and tables for simplified models
    engine = get_engine()
    
    # Enable foreign key constraints in SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    ModelBase.metadata.create_all(bind=engine)
    
    # Create session
    session_factory = get_session_factory()
    session = session_factory()
    
    yield session
    
    # Cleanup
    session.close()
    ModelBase.metadata.drop_all(bind=engine)
    reset_database_state()


@pytest.fixture(scope="function")
def test_db(test_settings):
    """Create test database session with actual models tables."""
    # Reset database state to use test settings
    reset_database_state()
    
    from app.core.database import get_engine, get_session_factory, Base
    
    # Create engine and tables for actual models
    engine = get_engine()
    
    # Patch GeoAlchemy2 functions for SQLite
    with patch('geoalchemy2.functions.GenericFunction.__init__', return_value=None):
        with patch('geoalchemy2.elements.WKTElement.__init__', return_value=None):
            with patch('geoalchemy2.elements.WKTElement.desc', return_value=None):
                with patch('geoalchemy2.elements.WKTElement.asc', return_value=None):
                    # Create tables - this will now work with SQLite
                    Base.metadata.create_all(bind=engine)
    
    # Create session
    session_factory = get_session_factory()
    session = session_factory()
    
    yield session
    
    # Cleanup
    session.close()
    
    # Drop tables
    Base.metadata.drop_all(bind=engine)
    reset_database_state()


@pytest.fixture
def sample_link_data():
    """Sample link data for testing (without geometry for SQLite)."""
    return {
        "link_id": 1,
        "road_name": "Test Highway",
        "length": 1500.0,
        "road_type": "Highway",
        "speed_limit": 65
    }


@pytest.fixture
def sample_link_data_with_geometry():
    """Sample link data with geometry for PostGIS tests."""
    return {
        "link_id": 1,
        "road_name": "Test Highway",
        "length": 1500.0,
        "road_type": "Highway", 
        "speed_limit": 65,
        # WKT for a simple linestring
        "geometry": "LINESTRING(-81.7 30.2, -81.6 30.3)"
    }


@pytest.fixture  
def sample_speed_record_data():
    """Sample speed record data for testing."""
    return {
        "link_id": 1,
        "timestamp": datetime(2024, 1, 1, 8, 30, 0),
        "speed": 55.5,
        "day_of_week": "Monday", 
        "time_period": "AM Peak"
    }


@pytest.fixture
def multiple_speed_records_data():
    """Multiple speed records for testing aggregations."""
    return [
        {
            "link_id": 1,
            "timestamp": datetime(2024, 1, 1, 8, 30, 0),
            "speed": 55.5,
            "day_of_week": "Monday",
            "time_period": "AM Peak"
        },
        {
            "link_id": 1,
            "timestamp": datetime(2024, 1, 1, 17, 30, 0),
            "speed": 45.2,
            "day_of_week": "Monday",
            "time_period": "PM Peak"
        },
        {
            "link_id": 2,
            "timestamp": datetime(2024, 1, 1, 8, 30, 0),
            "speed": 62.1,
            "day_of_week": "Monday",
            "time_period": "AM Peak"
        }
    ]
