#!/usr/bin/env python3
"""
Data ingestion script for GeoSpatial Links API.

This script ingests the Parquet datasets into PostgreSQL/PostGIS database:
- Link Info Dataset: Road segments with geometry
- Speed Data: Traffic speed measurements

Designed to run inside the Docker container with all dependencies available.
Uses SQLAlchemy ORM for robust data operations.
"""

import sys
import os
import pandas as pd
import json
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from shapely.geometry import shape
from geoalchemy2 import WKTElement

# Add project root to Python path
sys.path.insert(0, '/workspace')

from app.core.database import get_engine, get_session_factory
from app.models.link import Link
from app.models.speed_record import SpeedRecord


def main():
    """Main ingestion function."""
    print_header("GEOSPATIAL DATA INGESTION")
    print("Ingesting Parquet datasets into PostgreSQL/PostGIS database using SQLAlchemy ORM")
    
    try:
        # Load datasets
        link_df, speed_df = load_datasets()
        
        # Prepare data as ORM objects
        link_objects = prepare_link_objects(link_df)
        
        # Create session for database operations
        Session = get_session_factory()
        
        with Session() as session:
            # Clear existing data
            clear_existing_data_orm(session)
            
            # Insert links first
            insert_links_orm(session, link_objects)
            
            # Get existing link IDs for referential integrity
            existing_link_ids = get_existing_link_ids(session)
            
            # Prepare speed records with link validation
            speed_objects = prepare_speed_objects(speed_df, existing_link_ids)
            
            # Insert speed records
            insert_speed_records_orm(session, speed_objects)
            
            # Verify results
            verify_data_orm(session)
        
        print_header("INGESTION COMPLETED SUCCESSFULLY")
        print("Database is ready for API queries!")
        
    except Exception as e:
        print(f"\nError during ingestion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


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


def convert_geometry_to_wkt_element(geo_json_str):
    """Convert GeoJSON string to WKTElement for PostGIS via GeoAlchemy2."""
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
        
        # Return as WKTElement with SRID for GeoAlchemy2
        return WKTElement(geom.wkt, srid=4326)
        
    except Exception as e:
        print(f"Error converting geometry: {e}")
        return None


def prepare_link_objects(link_df) -> List[Link]:
    """Prepare link data as SQLAlchemy ORM objects."""
    print_step(2, "PREPARING LINK OBJECTS")
    
    link_objects = []
    
    for idx, row in link_df.iterrows():
        try:
            # Convert geometry
            geometry_element = convert_geometry_to_wkt_element(row['geo_json'])
            if not geometry_element:
                print(f"Skipping link {row['link_id']} - invalid geometry")
                continue
            
            # Convert length to float
            length = None
            if pd.notna(row['_length']) and row['_length'] != '':
                try:
                    length = float(row['_length'])
                except (ValueError, TypeError):
                    length = None
            
            # Create Link ORM object
            link_obj = Link(
                link_id=int(row['link_id']),
                road_name=row['road_name'] if pd.notna(row['road_name']) else None,
                length=length,
                road_type=None,  # Not in dataset
                speed_limit=None,  # Not in dataset
                geometry=geometry_element
            )
            
            link_objects.append(link_obj)
            
            if len(link_objects) % 10000 == 0:
                print(f"  Processed {len(link_objects):,} links...")
                
        except Exception as e:
            print(f"Error processing link {row.get('link_id', 'unknown')}: {e}")
            continue
    
    print(f"  Successfully prepared {len(link_objects):,} Link objects")
    return link_objects


def prepare_speed_objects(speed_df, existing_link_ids: set) -> List[SpeedRecord]:
    """Prepare speed data as SQLAlchemy ORM objects."""
    print_step(3, "PREPARING SPEED RECORD OBJECTS")
    
    speed_objects = []
    skipped_missing_links = 0
    
    # Map period to string
    period_mapping = {
        1: 'Overnight',
        2: 'Early Morning', 
        3: 'AM Peak',
        4: 'Midday',
        5: 'Early Afternoon',
        6: 'PM Peak',
        7: 'Evening'
    }
    
    for idx, row in speed_df.iterrows():
        try:
            link_id = int(row['link_id'])
            
            # Skip if link doesn't exist (referential integrity)
            if link_id not in existing_link_ids:
                skipped_missing_links += 1
                continue
            
            # Convert datetime
            timestamp = pd.to_datetime(row['date_time'])
            period_name = period_mapping.get(row['period'], None)
            
            # Create SpeedRecord ORM object
            speed_obj = SpeedRecord(
                link_id=link_id,
                timestamp=timestamp,
                speed=float(row['average_speed']),  # Using 'speed' column (mph)
                time_period=period_name
            )
            
            speed_objects.append(speed_obj)
            
            if len(speed_objects) % 50000 == 0:
                print(f"  Processed {len(speed_objects):,} speed records...")
                
        except Exception as e:
            print(f"Error processing speed record {idx}: {e}")
            continue
    
    print(f"  Successfully prepared {len(speed_objects):,} SpeedRecord objects")
    if skipped_missing_links > 0:
        print(f"  Skipped {skipped_missing_links:,} records with missing link references")
    
    return speed_objects


def clear_existing_data_orm(session: Session):
    """Clear existing data from tables using ORM."""
    print_step(4, "CLEARING EXISTING DATA (ORM)")
    
    try:
        # Clear speed records first (foreign key constraint)
        print("Clearing speed_records table...")
        deleted_speeds = session.query(SpeedRecord).delete()
        print(f"  Deleted {deleted_speeds:,} speed records")
        
        # Clear links
        print("Clearing links table...")
        deleted_links = session.query(Link).delete()
        print(f"  Deleted {deleted_links:,} links")
        
        session.commit()
        print("  Data cleared successfully")
        
    except Exception as e:
        print(f"Error clearing data: {e}")
        session.rollback()
        raise


def insert_links_orm(session: Session, link_objects: List[Link]):
    """Insert links using SQLAlchemy ORM bulk operations."""
    print_step(5, "INSERTING LINKS (ORM)")
    
    batch_size = 1000
    total_inserted = 0
    
    try:
        for i in range(0, len(link_objects), batch_size):
            batch = link_objects[i:i + batch_size]
            
            try:
                # Use bulk_save_objects for better performance
                session.bulk_save_objects(batch)
                session.commit()
                
                total_inserted += len(batch)
                print(f"  Inserted batch {i//batch_size + 1}: {total_inserted:,} links")
                
            except Exception as e:
                print(f"Error inserting link batch {i//batch_size + 1}: {e}")
                session.rollback()
                
                # Try individual inserts for this batch
                successful_individual = 0
                for link_obj in batch:
                    try:
                        session.add(link_obj)
                        session.commit()
                        successful_individual += 1
                    except Exception as individual_error:
                        session.rollback()
                        print(f"  Failed to insert link {link_obj.link_id}: {individual_error}")
                
                total_inserted += successful_individual
                print(f"  Recovered {successful_individual} links from failed batch")
    
        print(f"  Total links inserted: {total_inserted:,}")
        
    except Exception as e:
        print(f"Critical error in link insertion: {e}")
        session.rollback()
        raise


def get_existing_link_ids(session: Session) -> set:
    """Get set of existing link IDs for referential integrity."""
    print("Getting existing link IDs for referential integrity...")
    
    try:
        # Query all link_ids efficiently
        result = session.query(Link.link_id).all()
        link_ids = {row.link_id for row in result}
        print(f"  Found {len(link_ids):,} existing links")
        return link_ids
        
    except Exception as e:
        print(f"Error getting existing link IDs: {e}")
        return set()


def insert_speed_records_orm(session: Session, speed_objects: List[SpeedRecord]):
    """Insert speed records using SQLAlchemy ORM bulk operations."""
    print_step(6, "INSERTING SPEED RECORDS (ORM)")
    
    batch_size = 5000
    total_inserted = 0
    
    try:
        for i in range(0, len(speed_objects), batch_size):
            batch = speed_objects[i:i + batch_size]
            
            try:
                # Use bulk_save_objects for better performance
                session.bulk_save_objects(batch)
                session.commit()
                
                total_inserted += len(batch)
                print(f"  Inserted batch {i//batch_size + 1}: {total_inserted:,} speed records")
                
            except Exception as e:
                print(f"Error inserting speed batch {i//batch_size + 1}: {e}")
                session.rollback()
                continue
    
        print(f"  Total speed records inserted: {total_inserted:,}")
        
    except Exception as e:
        print(f"Critical error in speed record insertion: {e}")
        session.rollback()
        raise


def verify_data_orm(session: Session):
    """Verify inserted data using ORM queries."""
    print_step(7, "VERIFYING DATA (ORM)")
    
    try:
        # Count links using ORM
        link_count = session.query(Link).count()
        print(f"  Links in database: {link_count:,}")
        
        # Count speed records using ORM
        speed_count = session.query(SpeedRecord).count()
        print(f"  Speed records in database: {speed_count:,}")
        
        # Sample queries using ORM
        print("\n  Sample data verification:")
        
        # Sample link with geometry
        sample_link = session.query(Link).filter(Link.geometry.isnot(None)).first()
        if sample_link:
            print(f"    Sample link: {sample_link.link_id}, {sample_link.road_name}")
            # Note: Geometry display would require special handling with GeoAlchemy2
            print(f"    Has geometry: Yes")
        
        # Sample speed record with relationship
        sample_speed = session.query(SpeedRecord).first()
        if sample_speed:
            print(f"    Sample speed: Link {sample_speed.link_id}, {sample_speed.speed} mph at {sample_speed.timestamp}")
            if hasattr(sample_speed, 'time_period') and sample_speed.time_period is not None:
                print(f"    Time period: {sample_speed.time_period}")
            else:
                print("    Time period: Not set")
        
        # Advanced ORM query: Average speed by period
        print("\n  Advanced ORM verification:")
        try:
            # Try a simpler query first to test the connection
            total_records = session.query(SpeedRecord).count()
            print(f"    Total speed records: {total_records:,}")
            
            # Test time_period field existence
            records_with_period = session.query(SpeedRecord).filter(
                SpeedRecord.time_period.isnot(None)
            ).count()
            print(f"    Records with time_period: {records_with_period:,}")
            
            if records_with_period > 0:
                # Use a more compatible aggregation query
                period_averages = session.query(
                    SpeedRecord.time_period,
                    func.avg(SpeedRecord.speed).label('avg_speed'),
                    func.count(SpeedRecord.id).label('record_count')
                ).filter(
                    SpeedRecord.time_period.isnot(None)
                ).group_by(
                    SpeedRecord.time_period
                ).all()
                
                print("    Average speeds by time period:")
                for period_avg in period_averages:
                    print(f"      {period_avg.time_period}: {period_avg.avg_speed:.1f} mph ({period_avg.record_count:,} records)")
            else:
                print("    No records with time_period found - skipping aggregation")
                
        except Exception as query_error:
            print(f"    Error in advanced verification query: {query_error}")
            print("    Continuing with basic verification...")
            
    except Exception as e:
        print(f"Error during verification: {e}")
        raise




if __name__ == "__main__":
    main()
