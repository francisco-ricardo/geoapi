#!/usr/bin/env python3
"""
Database setup script for creating PostgreSQL/PostGIS tables.

This script creates all tables defined in the SQLAlchemy models
and verifies the database structure is correct.
"""
import os
import sys

# Add project root to Python path
sys.path.insert(0, "/workspace")

from sqlalchemy import text

from app.core.database import Base, get_engine
from app.models.link import Link
from app.models.speed_record import SpeedRecord


def create_tables():
    """Create all tables defined in the models."""
    print("Creating database tables...")
    print("=" * 50)

    try:
        # Get database engine
        print("Connecting to database...")
        engine = get_engine()

        # Verify connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            row = result.fetchone()
            if row:
                version = row[0]
                print(f"Connected to PostgreSQL: {version[:50]}...")
            else:
                print("Connected to PostgreSQL")

        # Create all tables
        print("\nCreating tables...")
        print("   - Table 'links' (Link model)")
        print("   - Table 'speed_records' (SpeedRecord model)")

        Base.metadata.create_all(bind=engine)

        print("Tables created successfully!")

        # Verify tables were created
        print("\nVerifying created tables...")
        with engine.connect() as conn:
            # List tables
            result = conn.execute(
                text(
                    """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """
                )
            )
            tables = [row[0] for row in result.fetchall()]

            print(f"Tables found in database: {len(tables)}")
            for table in tables:
                print(f"   - {table}")

            # Check if required tables exist
            required_tables = ["links", "speed_records"]
            missing_tables = [table for table in required_tables if table not in tables]

            if missing_tables:
                print(f"\nMissing tables: {missing_tables}")
                return False
            else:
                print(f"\nAll required tables are present!")
                return True

    except Exception as e:
        print(f"Error creating tables: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = create_tables()
    if success:
        print("\n" + "=" * 50)
        print("Database ready for use!")
        print("You can now run endpoint tests.")
        print("=" * 50)
        sys.exit(0)
    else:
        print("\n" + "=" * 50)
        print("Failed to create tables")
        print("Check database configuration.")
        print("=" * 50)
        sys.exit(1)
