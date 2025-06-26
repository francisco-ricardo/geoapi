"""
Tests for database configuration and management.
"""
import pytest
from unittest.mock import patch

from app.core.database import (
    get_engine, get_session_factory, get_db, 
    create_tables, drop_tables, health_check,
    reset_database_state, get_db_session
)


class TestDatabaseFactory:
    """Test database factory functions."""
    
    def test_get_engine_caching(self, test_settings):
        """Test engine caching behavior."""
        reset_database_state()
        
        engine1 = get_engine()
        engine2 = get_engine()
        
        # Should be the same cached object
        assert engine1 is engine2
        assert str(engine1.url) == "sqlite:///:memory:"
    
    def test_get_session_factory_caching(self, test_settings):
        """Test session factory caching behavior."""
        reset_database_state()
        
        factory1 = get_session_factory()
        factory2 = get_session_factory()
        
        # Should be the same cached object
        assert factory1 is factory2
    
    def test_get_db_dependency_generator(self, test_settings):
        """Test get_db dependency function returns generator."""
        reset_database_state()
        create_tables()
        
        db_generator = get_db()
        
        # Should be a generator
        assert hasattr(db_generator, '__next__')
        
        # Get session from generator
        db_session = next(db_generator)
        assert db_session is not None
        
        # Cleanup - close the generator
        try:
            next(db_generator)
        except StopIteration:
            pass  # Expected when generator is exhausted
    
    def test_get_db_session_direct(self, test_settings):
        """Test get_db_session for non-FastAPI contexts."""
        reset_database_state()
        create_tables()
        
        session = get_db_session()
        
        assert session is not None
        
        # Should be able to close manually
        session.close()
    
    def test_health_check_success(self, test_settings):
        """Test database health check with working connection."""
        reset_database_state()
        
        # Should work with SQLite in-memory
        assert health_check() is True
    
    def test_health_check_failure(self):
        """Test health check with invalid connection."""
        # Mock a failing engine
        with patch('app.core.database.get_engine') as mock_engine:
            mock_engine.return_value.connect.side_effect = Exception("Connection failed")
            
            assert health_check() is False
    
    def test_reset_database_state(self, test_settings):
        """Test database state reset functionality."""
        # Create engine first
        engine1 = get_engine()
        factory1 = get_session_factory()
        
        # Reset state
        reset_database_state()
        
        # Get new instances
        engine2 = get_engine()
        factory2 = get_session_factory()
        
        # Should be different objects after reset
        assert engine1 is not engine2
        assert factory1 is not factory2


class TestTableManagement:
    """Test table creation and management."""
    
    def test_create_tables_success(self, test_settings):
        """Test successful table creation."""
        reset_database_state()
        
        # Import models to ensure they are registered with Base
        from app.models import Link, SpeedRecord
        
        # Should not raise any exception
        create_tables()
        
        # Verify tables exist by checking engine metadata
        from app.core.database import Base
        engine = get_engine()
        
        # Check if tables were created
        inspector = __import__('sqlalchemy').inspect(engine)
        table_names = inspector.get_table_names()
        
        # Our models should create these tables
        expected_tables = ['links', 'speed_records']
        for table in expected_tables:
            assert table in table_names
    
    def test_drop_tables_success(self, test_settings):
        """Test successful table dropping."""
        reset_database_state()
        
        # Import models to ensure they are registered
        from app.models import Link, SpeedRecord
        
        # Create tables first
        create_tables()
        
        # Drop tables - should not raise
        drop_tables()
        
        # Verify tables are gone
        engine = get_engine()
        inspector = __import__('sqlalchemy').inspect(engine)
        table_names = inspector.get_table_names()
        
        # Tables should be dropped
        assert 'links' not in table_names
        assert 'speed_records' not in table_names
    
    def test_create_tables_without_postgis(self, test_settings):
        """Test table creation works with SQLite (no PostGIS)."""
        reset_database_state()
        
        # Import models to ensure they are registered
        from app.models import Link, SpeedRecord
        
        # Should work even without PostGIS for SQLite
        create_tables()
        
        # Verify basic tables exist
        engine = get_engine()
        inspector = __import__('sqlalchemy').inspect(engine)
        table_names = inspector.get_table_names()
        
        assert len(table_names) >= 2  # At least our two tables


class TestDatabaseIntegration:
    """Integration tests for database functionality."""
    
    def test_full_database_lifecycle(self, test_settings):
        """Test complete database lifecycle."""
        reset_database_state()
        
        # 1. Check health
        assert health_check() is True
        
        # 2. Create tables
        create_tables()
        
        # 3. Get session
        session = get_db_session()
        assert session is not None
        
        # 4. Close session
        session.close()
        
        # 5. Drop tables
        drop_tables()
        
        # 6. Reset state
        reset_database_state()
        
        # Should still be healthy
        assert health_check() is True
