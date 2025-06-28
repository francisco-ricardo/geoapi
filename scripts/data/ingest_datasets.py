#!/usr/bin/env python3
"""
Data ingestion script for GeoSpatial Links API.

This script ingests the Parquet datasets into PostgreSQL/PostGIS database:
- Link Info Dataset: Road segments with geometry
- Speed Data: Traffic speed measurements

Designed to run inside the Docker container with all dependencies available.
"""

import sys
import os
import pandas as pd
import json
from datetime import datetime
from sqlalchemy import text
from shapely.geometry import shape
from shapely import wkt

# Add project root to Python path
sys.path.insert(0, '/workspace')

from app.core.database import get_engine, get_session_factory
from app.models.link import Link
from app.models.speed_record import SpeedRecord


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_step(step, description):
    """Print a formatted step."""
    print(f"\n[{step}] {description}")
    print("-" * 60)


def load_datasets():
    """Load both Parquet datasets."""
    print_step(1, "LOADING DATASETS")
    
    # Load Link Info Dataset
    print("Loading link_info.parquet.gz...")
    link_info_path = "/workspace/data/raw/link_info.parquet.gz"
    if not os.path.exists(link_info_path):
        raise FileNotFoundError(f"Link info dataset not found: {link_info_path}")
    
    link_df = pd.read_parquet(link_info_path)
    print(f"  Links loaded: {len(link_df):,}")
    print(f"  Columns: {list(link_df.columns)}")
    
    # Load Speed Data Dataset
    print("\nLoading duval_jan1_2024.parquet.gz...")
    speed_data_path = "/workspace/data/raw/duval_jan1_2024.parquet.gz"
    if not os.path.exists(speed_data_path):
        raise FileNotFoundError(f"Speed data dataset not found: {speed_data_path}")
    
    speed_df = pd.read_parquet(speed_data_path)
    print(f"  Speed records loaded: {len(speed_df):,}")
    print(f"  Columns: {list(speed_df.columns)}")
    
    return link_df, speed_df


def convert_geometry_to_wkt(geo_json_str):
    """Convert GeoJSON string to WKT format for PostGIS."""
    try:
        # Parse JSON string
        geo_json = json.loads(geo_json_str) if isinstance(geo_json_str, str) else geo_json_str
        
        # Convert to Shapely geometry
        geom = shape(geo_json)
        
        # Convert MultiLineString to LineString (take first linestring)
        if geom.geom_type == 'MultiLineString':
            try:
                # Cast to MultiLineString and access first geometry
                from shapely.geometry import MultiLineString
                if isinstance(geom, MultiLineString) and len(geom.geoms) > 0:
                    geom = geom.geoms[0]
                else:
                    return None
            except (IndexError, AttributeError):
                return None
        
        # Return as WKT
        return geom.wkt
    except Exception as e:
        print(f"Error converting geometry: {e}")
        return None


def prepare_link_data(link_df):
    """Prepare link data for database insertion."""
    print_step(2, "PREPARING LINK DATA")
    
    prepared_links = []
    
    for idx, row in link_df.iterrows():
        try:
            # Convert geometry
            geometry_wkt = convert_geometry_to_wkt(row['geo_json'])
            if not geometry_wkt:
                print(f"Skipping link {row['link_id']} - invalid geometry")
                continue
            
            # Convert length to float
            length = None
            if pd.notna(row['_length']) and row['_length'] != '':
                try:
                    length = float(row['_length'])
                except (ValueError, TypeError):
                    length = None
            
            # Prepare link data
            link_data = {
                'link_id': int(row['link_id']),
                'road_name': row['road_name'] if pd.notna(row['road_name']) else None,
                'length': length,
                'road_type': None,  # Not in dataset
                'speed_limit': None,  # Not in dataset
                'geometry': f"SRID=4326;{geometry_wkt}"
            }
            
            prepared_links.append(link_data)
            
            if len(prepared_links) % 10000 == 0:
                print(f"  Processed {len(prepared_links):,} links...")
                
        except Exception as e:
            print(f"Error processing link {row.get('link_id', 'unknown')}: {e}")
            continue
    
    print(f"  Successfully prepared {len(prepared_links):,} links")
    return prepared_links


def prepare_speed_data(speed_df):
    """Prepare speed data for database insertion."""
    print_step(3, "PREPARING SPEED DATA")
    
    prepared_speeds = []
    
    for idx, row in speed_df.iterrows():
        try:
            # Convert datetime
            timestamp = pd.to_datetime(row['date_time'])
            
            # Map period to string (optional)
            period_mapping = {
                1: 'Overnight',
                2: 'Early Morning', 
                3: 'AM Peak',
                4: 'Midday',
                5: 'Early Afternoon',
                6: 'PM Peak',
                7: 'Evening'
            }
            
            period_name = period_mapping.get(row['period'], None)
            
            speed_data = {
                'link_id': int(row['link_id']),
                'timestamp': timestamp,
                'speed': float(row['average_speed']),  # Using 'speed' column (mph)
                'period': period_name
            }
            
            prepared_speeds.append(speed_data)
            
            if len(prepared_speeds) % 50000 == 0:
                print(f"  Processed {len(prepared_speeds):,} speed records...")
                
        except Exception as e:
            print(f"Error processing speed record {idx}: {e}")
            continue
    
    print(f"  Successfully prepared {len(prepared_speeds):,} speed records")
    return prepared_speeds


def clear_existing_data(engine):
    """Clear existing data from tables."""
    print_step(4, "CLEARING EXISTING DATA")
    
    with engine.connect() as conn:
        # Clear speed records first (foreign key constraint)
        print("Clearing speed_records table...")
        result = conn.execute(text("DELETE FROM speed_records"))
        print(f"  Deleted {result.rowcount} speed records")
        
        # Clear links
        print("Clearing links table...")
        result = conn.execute(text("DELETE FROM links"))
        print(f"  Deleted {result.rowcount} links")
        
        conn.commit()


def insert_links(engine, links_data):
    """Insert links data into database."""
    print_step(5, "INSERTING LINKS")
    
    batch_size = 1000
    total_inserted = 0
    
    with engine.connect() as conn:
        for i in range(0, len(links_data), batch_size):
            batch = links_data[i:i + batch_size]
            
            try:
                # Build INSERT statement
                sql = """
                INSERT INTO links (link_id, road_name, length, road_type, speed_limit, geometry)
                VALUES (:link_id, :road_name, :length, :road_type, :speed_limit, ST_GeomFromText(:geometry))
                ON CONFLICT (link_id) DO NOTHING
                """
                
                conn.execute(text(sql), batch)
                conn.commit()
                
                total_inserted += len(batch)
                print(f"  Inserted batch {i//batch_size + 1}: {total_inserted:,} links")
                
            except Exception as e:
                print(f"Error inserting link batch {i//batch_size + 1}: {e}")
                conn.rollback()
                continue
    
    print(f"  Total links inserted: {total_inserted:,}")


def insert_speed_records(engine, speed_data):
    """Insert speed records into database."""
    print_step(6, "INSERTING SPEED RECORDS")
    
    batch_size = 5000
    total_inserted = 0
    
    with engine.connect() as conn:
        for i in range(0, len(speed_data), batch_size):
            batch = speed_data[i:i + batch_size]
            
            try:
                sql = """
                INSERT INTO speed_records (link_id, timestamp, speed, time_period)
                VALUES (:link_id, :timestamp, :speed, :period)
                """
                
                conn.execute(text(sql), batch)
                conn.commit()
                
                total_inserted += len(batch)
                print(f"  Inserted batch {i//batch_size + 1}: {total_inserted:,} speed records")
                
            except Exception as e:
                print(f"Error inserting speed batch {i//batch_size + 1}: {e}")
                conn.rollback()
                continue
    
    print(f"  Total speed records inserted: {total_inserted:,}")


def verify_data(engine):
    """Verify inserted data."""
    print_step(7, "VERIFYING DATA")
    
    with engine.connect() as conn:
        # Count links
        result = conn.execute(text("SELECT COUNT(*) FROM links"))
        link_count = result.scalar()
        print(f"  Links in database: {link_count:,}")
        
        # Count speed records
        result = conn.execute(text("SELECT COUNT(*) FROM speed_records"))
        speed_count = result.scalar()
        print(f"  Speed records in database: {speed_count:,}")
        
        # Sample queries
        print("\n  Sample data verification:")
        
        # Sample link with geometry
        result = conn.execute(text("""
            SELECT link_id, road_name, ST_AsText(geometry) as geometry_text
            FROM links 
            WHERE geometry IS NOT NULL 
            LIMIT 1
        """))
        sample_link = result.fetchone()
        if sample_link:
            print(f"    Sample link: {sample_link.link_id}, {sample_link.road_name}")
            print(f"    Geometry: {sample_link.geometry_text[:100]}...")
        
        # Sample speed record
        result = conn.execute(text("""
            SELECT link_id, timestamp, speed, time_period
            FROM speed_records 
            LIMIT 1
        """))
        sample_speed = result.fetchone()
        if sample_speed:
            print(f"    Sample speed: Link {sample_speed.link_id}, {sample_speed.speed} mph at {sample_speed.timestamp}")
            if sample_speed.time_period:
                print(f"    Time period: {sample_speed.time_period}")


def main():
    """Main ingestion function."""
    print_header("GEOSPATIAL DATA INGESTION")
    print("Ingesting Parquet datasets into PostgreSQL/PostGIS database")
    
    try:
        # Load datasets
        link_df, speed_df = load_datasets()
        
        # Prepare data
        links_data = prepare_link_data(link_df)
        speed_data = prepare_speed_data(speed_df)
        
        # Database operations
        engine = get_engine()
        
        # Clear existing data
        clear_existing_data(engine)
        
        # Insert new data
        insert_links(engine, links_data)
        insert_speed_records(engine, speed_data)
        
        # Verify results
        verify_data(engine)
        
        print_header("INGESTION COMPLETED SUCCESSFULLY")
        print("Database is ready for API queries!")
        
    except Exception as e:
        print(f"\nError during ingestion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
