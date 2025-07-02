"""
Database configuration and session management.
"""

from functools import lru_cache
from typing import Generator, Optional

from sqlalchemy import Engine, MetaData, create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import get_settings

# Global variables (only metadata and base)
metadata = MetaData()
Base = declarative_base(metadata=metadata)

# Module-level cache for engine and session factory
_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker] = None


def _validate_database_url(database_url: str) -> None:
    """
    Validate database URL format.

    Args:
        database_url: Database connection URL to validate

    Raises:
        ValueError: If database URL format is invalid
    """
    url_lower = database_url.lower()

    if not any(
        url_lower.startswith(scheme) for scheme in ["sqlite", "postgresql", "mysql"]
    ):
        raise ValueError(
            f"Unsupported database URL scheme. "
            f"Expected sqlite, postgresql, or mysql. Got: {database_url[:20]}..."
        )

    if url_lower.startswith("postgresql") and "postgis" not in database_url.lower():
        # Warning: PostgreSQL without PostGIS might not support spatial operations
        pass


@lru_cache()
def get_engine() -> Engine:
    """
    Get or create database engine.

    Uses caching to ensure single engine instance per application.

    Returns:
        Engine: SQLAlchemy database engine with PostGIS support

    Raises:
        ValueError: If database URL is invalid
    """
    global _engine
    if _engine is None:
        settings = get_settings()

        # Validate database URL
        _validate_database_url(settings.database_url)

        # Configure connect_args based on database type
        connect_args = {}
        database_url = settings.database_url.lower()

        if database_url.startswith("sqlite"):
            # SQLite specific configuration
            connect_args = {
                "check_same_thread": False,  # Allow FastAPI to use SQLite
                "timeout": 30,  # Connection timeout in seconds
            }
        elif database_url.startswith("postgresql"):
            # PostgreSQL specific configuration
            connect_args = {
                "connect_timeout": 10,  # Connection timeout
                "application_name": "geoapi",  # For monitoring/debugging
            }

        _engine = create_engine(
            settings.database_url,
            echo=settings.debug,  # Log SQL queries when debug=True
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,  # Recycle connections every hour (was 300s)
            connect_args=connect_args,
        )
    return _engine


@lru_cache()
def get_session_factory() -> sessionmaker:
    """
    Get or create session factory.

    Uses caching to ensure single factory instance per application.

    Returns:
        sessionmaker: SQLAlchemy session factory
    """
    global _session_factory
    if _session_factory is None:
        engine = get_engine()
        _session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _session_factory


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.

    This function is used as a FastAPI dependency to provide
    database sessions to route handlers.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """
    Create all database tables.

    This function creates all tables defined by SQLAlchemy models
    that inherit from Base. It also ensures PostGIS extensions
    are available for PostgreSQL databases.

    Raises:
        RuntimeError: If PostGIS extension is not available for PostgreSQL
    """
    engine = get_engine()
    settings = get_settings()

    # Only check PostGIS for PostgreSQL databases
    database_url = settings.database_url.lower()
    if database_url.startswith("postgresql"):
        # Verify PostGIS is available
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text(
                        "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'postgis')"
                    )
                )
                postgis_exists = result.scalar()

                if not postgis_exists:
                    raise RuntimeError(
                        "PostGIS extension not found. "
                        "Please ensure PostGIS is installed and enabled: "
                        "CREATE EXTENSION IF NOT EXISTS postgis;"
                    )
        except Exception as e:
            if "postgis" in str(e).lower():
                raise RuntimeError(f"PostGIS verification failed: {e}")
            # Re-raise other database connection errors
            raise

    # Create all tables
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """
    Drop all database tables.

    Useful for testing and development. Use with caution in production.
    """
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)


def get_db_session() -> Session:
    """
    Get a database session for use outside of FastAPI context.

    This is useful for scripts, CLI commands, or other non-web contexts.
    Remember to close the session when done.

    Returns:
        Session: SQLAlchemy database session

    Example:
        db = get_db_session()
        try:
            # Use db session
            items = db.query(Item).all()
        finally:
            db.close()
    """
    session_factory = get_session_factory()
    return session_factory()


def health_check() -> bool:
    """
    Check if database connection is healthy.

    Returns:
        bool: True if database is accessible, False otherwise
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def reset_database_state() -> None:
    """
    Reset cached database state. Useful for testing.

    This function clears all cached instances and allows
    for fresh database connections with new configurations.
    """
    global _engine, _session_factory
    _engine = None
    _session_factory = None
    get_engine.cache_clear()
    get_session_factory.cache_clear()
