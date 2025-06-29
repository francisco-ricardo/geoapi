"""
Consolidated fixtures for all tests.
Centralized location for reusable test components.
"""
import tempfile
import os
from datetime import datetime, UTC
from typing import Generator
import pytest
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session
from unittest.mock import MagicMock

from app.core.database import Base
from tests.fixtures.models import SimplifiedLink, SimplifiedSpeedRecord, ModelBase


@pytest.fixture(scope="function")
def test_db_simple() -> Generator[Session, None, None]:
    """
    Create an in-memory SQLite database for testing with simplified models.
    This fixture provides fast, isolated tests without PostGIS dependencies.
    """
    # Create in-memory SQLite engine
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Create all tables
    ModelBase.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        ModelBase.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function") 
def mock_settings():
    """Mock settings for testing without actual configuration dependencies."""
    settings = MagicMock()
    settings.database_url = "sqlite:///:memory:"
    settings.log_to_file = False
    settings.log_file_path = None
    settings.log_format = "text"
    settings.log_level = "INFO"
    return settings


@pytest.fixture(scope="function")
def temp_log_file():
    """Create a temporary log file for testing file logging."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture(scope="function")
def sample_link_data():
    """Sample data for link testing."""
    return {
        "link_id": 1,
        "road_name": "Test Road",
        "length": 1000.0,
        "road_type": "Highway",
        "speed_limit": 60
    }


@pytest.fixture(scope="function")
def sample_speed_record_data():
    """Sample data for speed record testing."""
    return {
        "link_id": 1,
        "timestamp": datetime.now(UTC),
        "speed": 55.5,
        "day_of_week": "Monday",
        "time_period": "AM Peak"
    }


@pytest.fixture(scope="function")
def mock_database_engine():
    """Mock database engine for testing database operations."""
    engine = MagicMock()
    connection = MagicMock()
    engine.connect.return_value.__enter__.return_value = connection
    return engine, connection
