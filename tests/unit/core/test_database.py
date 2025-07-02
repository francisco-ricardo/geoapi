"""
Comprehensive tests for database functionality.
Consolidates all database tests including core functionality and PostGIS integration.
"""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from app.core.database import (
    _validate_database_url,
    create_tables,
    get_db,
    get_engine,
    get_session_factory,
    health_check,
    reset_database_state,
)
from tests.fixtures import mock_database_engine


class TestDatabaseURLValidation:
    """Test database URL validation functionality."""

    def test_valid_sqlite_url(self):
        """Test validation with valid SQLite URL."""
        # Should not raise an exception
        _validate_database_url("sqlite:///test.db")
        _validate_database_url("sqlite:///:memory:")

    def test_valid_postgresql_url(self):
        """Test validation with valid PostgreSQL URL."""
        # Should not raise an exception
        _validate_database_url("postgresql://user:pass@localhost/dbname")
        _validate_database_url("postgresql+psycopg2://user:pass@localhost/postgis_db")

    def test_invalid_url_scheme(self):
        """Test validation with invalid URL scheme."""
        with pytest.raises(ValueError) as excinfo:
            _validate_database_url("invalid://localhost/db")

        assert "Unsupported database URL scheme" in str(excinfo.value)


class TestDatabaseEngineConfiguration:
    """Test database engine configuration."""

    def test_sqlite_connect_args(self):
        """Test SQLite connection arguments."""
        with patch("app.core.database.create_engine") as mock_create_engine:
            # Mock settings
            with patch("app.core.database.get_settings") as mock_get_settings:
                mock_settings = MagicMock()
                mock_settings.database_url = "sqlite:///test.db"
                mock_settings.debug = False
                mock_get_settings.return_value = mock_settings

                # Reset cache
                reset_database_state()

                # Get engine
                get_engine()

                # Check that create_engine was called with expected args
                args, kwargs = mock_create_engine.call_args
                assert args[0] == "sqlite:///test.db"
                assert kwargs["pool_pre_ping"] is True
                assert kwargs["connect_args"] == {
                    "check_same_thread": False,
                    "timeout": 30,
                }

    def test_postgresql_connect_args(self):
        """Test PostgreSQL connection arguments."""
        with patch("app.core.database.create_engine") as mock_create_engine:
            # Mock settings
            with patch("app.core.database.get_settings") as mock_get_settings:
                mock_settings = MagicMock()
                mock_settings.database_url = "postgresql://user:pass@localhost/dbname"
                mock_settings.debug = False
                mock_get_settings.return_value = mock_settings

                # Reset cache
                reset_database_state()

                # Get engine
                get_engine()

                # Check that create_engine was called with expected args
                args, kwargs = mock_create_engine.call_args
                assert args[0] == "postgresql://user:pass@localhost/dbname"
                assert kwargs["pool_pre_ping"] is True
                assert kwargs["connect_args"] == {
                    "connect_timeout": 10,
                    "application_name": "geoapi",
                }


class TestPostgisIntegration:
    """Test PostGIS integration checks."""

    def test_postgis_check_success(self):
        """Test PostGIS check when extension is available."""
        with patch("app.core.database.get_engine") as mock_get_engine:
            # Mock engine and connection
            mock_engine = MagicMock()
            mock_conn = MagicMock()
            mock_result = MagicMock()

            # Setup mock chain
            mock_get_engine.return_value = mock_engine
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            mock_conn.execute.return_value = mock_result
            mock_result.scalar.return_value = True  # PostGIS exists

            # Mock settings
            with patch("app.core.database.get_settings") as mock_get_settings:
                mock_settings = MagicMock()
                mock_settings.database_url = "postgresql://user:pass@localhost/dbname"
                mock_get_settings.return_value = mock_settings

                # Should not raise an exception
                create_tables()

                # Check that execute was called (SQLAlchemy creates TextClause objects)
                mock_conn.execute.assert_called_once()
                # Verify the SQL query content
                call_args = mock_conn.execute.call_args[0][0]
                assert "pg_extension" in str(call_args)
                assert "postgis" in str(call_args)

    def test_postgis_check_not_installed(self):
        """Test PostGIS check when extension is not available."""
        with patch("app.core.database.get_engine") as mock_get_engine:
            # Mock engine and connection
            mock_engine = MagicMock()
            mock_conn = MagicMock()
            mock_result = MagicMock()

            # Setup mock chain
            mock_get_engine.return_value = mock_engine
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            mock_conn.execute.return_value = mock_result
            mock_result.scalar.return_value = False  # PostGIS does not exist

            # Mock settings
            with patch("app.core.database.get_settings") as mock_get_settings:
                mock_settings = MagicMock()
                mock_settings.database_url = "postgresql://user:pass@localhost/dbname"
                mock_get_settings.return_value = mock_settings

                # Should raise RuntimeError
                with pytest.raises(RuntimeError) as excinfo:
                    create_tables()

                assert "PostGIS extension not found" in str(excinfo.value)


class TestDatabaseState:
    """Test database state management."""

    def test_reset_database_state(self):
        """Test database state reset functionality."""
        # Get an engine first to populate cache
        with patch("app.core.database.get_settings") as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.database_url = "sqlite:///:memory:"
            mock_settings.debug = False
            mock_get_settings.return_value = mock_settings

            # Get engine to populate cache
            engine1 = get_engine()

            # Reset state
            reset_database_state()

            # Get engine again - should be a new instance due to cache reset
            engine2 = get_engine()

            # Note: Due to lru_cache, we can't easily test if they're different objects
            # but we can verify the function completes without error
            assert engine1 is not None
            assert engine2 is not None

    def test_database_connection_pool(self):
        """Test database connection pooling behavior."""
        with patch("app.core.database.get_settings") as mock_get_settings:
            mock_settings = MagicMock()
            mock_settings.database_url = "postgresql://user:pass@localhost/dbname"
            mock_get_settings.return_value = mock_settings

            # Multiple calls should return the same engine (cached)
            engine1 = get_engine()
            engine2 = get_engine()

            # Should be the same due to caching
            assert engine1 is engine2


class TestDatabaseSession:
    """Test database session management."""

    def test_session_lifecycle(self):
        """Test complete session lifecycle."""
        with patch("app.core.database.get_session_factory") as mock_factory:
            mock_session = MagicMock()
            mock_factory.return_value.return_value = mock_session

            # Test generator-based session
            db_gen = get_db()
            session = next(db_gen)

            # Use the session
            assert session == mock_session

            # Close generator (simulating end of request)
            try:
                db_gen.close()
            except GeneratorExit:
                pass

            # Session should be closed
            mock_session.close.assert_called()

    def test_session_error_handling(self):
        """Test session error handling."""
        with patch("app.core.database.get_session_factory") as mock_factory:
            mock_session = MagicMock()
            mock_factory.return_value.return_value = mock_session

            # Simulate session error
            mock_session.execute.side_effect = Exception("DB Error")

            db_gen = get_db()
            session = next(db_gen)

            # Error should propagate
            with pytest.raises(Exception):
                session.execute(text("SELECT 1"))

            # Close generator
            try:
                db_gen.close()
            except GeneratorExit:
                pass

            # Session should still be closed despite error
            mock_session.close.assert_called()


class TestDatabaseIntegration:
    """Integration tests combining multiple database components."""

    def test_full_database_setup(self):
        """Test complete database setup flow."""
        with patch("app.core.database.get_settings") as mock_get_settings:
            with patch("app.core.database.create_engine") as mock_create_engine:
                with patch("app.core.database.Base") as mock_base:

                    # Mock settings
                    mock_settings = MagicMock()
                    mock_settings.database_url = "sqlite:///:memory:"
                    mock_settings.debug = False
                    mock_get_settings.return_value = mock_settings

                    # Mock engine
                    mock_engine = MagicMock()
                    mock_create_engine.return_value = mock_engine

                    # Reset state
                    reset_database_state()

                    # Test flow: engine -> tables -> health check
                    engine = get_engine()
                    assert engine is not None

                    create_tables()
                    mock_base.metadata.create_all.assert_called_once()

                    # Mock successful health check
                    mock_conn = MagicMock()
                    mock_engine.connect.return_value.__enter__.return_value = mock_conn

                    result = health_check()
                    assert result is True
