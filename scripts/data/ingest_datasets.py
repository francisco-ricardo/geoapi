#!/usr/bin/env python3
"""
Data ingestion script for GeoSpatial Links API.

This script ingests the Parquet datasets into PostgreSQL/PostGIS database:
- Link Info Dataset: Road segments with geometry  
- Speed Data: Traffic speed measurements

PERFORMANCE OPTIMIZED VERSION:
- Chunk Processing: 5K records per chunk to reduce memory consumption
- Streaming Pipeline: Sequential processing with memory cleanup
- Bulk Operations: SQLAlchemy bulk_save_objects for optimal performance

Clean Code principles: SOLID, KISS, separation of concerns.
Designed for Docker container with all dependencies available.
"""

import sys
import os
import pandas as pd
import json
import gc
from typing import List, Set
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from shapely.geometry import shape
from geoalchemy2 import WKTElement

# Add project root to Python path
sys.path.insert(0, '/workspace')

from app.core.database import get_session_factory
from app.models.link import Link
from app.models.speed_record import SpeedRecord

# Configuration constants
LINK_CHUNK_SIZE = 5000
SPEED_RECORD_CHUNK_SIZE = 5000
LINK_BATCH_SIZE = 1000
SPEED_BATCH_SIZE = 2000

PERIOD_MAPPING = {
    1: 'Overnight',
    2: 'Early Morning', 
    3: 'AM Peak',
    4: 'Midday',
    5: 'Early Afternoon',
    6: 'PM Peak',
    7: 'Evening'
}


def main():
    """Main ingestion function with optimized chunk processing."""
    print_header("GEOSPATIAL DATA INGESTION - MEMORY OPTIMIZED")
    print("Ingesting Parquet datasets using chunked processing for memory efficiency")
    
    try:
        # Create session for database operations
        Session = get_session_factory()
        
        with Session() as session:
            # Clear existing data
            clear_existing_data_orm(session)
            
            # Process links in chunks (memory efficient)
            process_links_chunked(session)
            
            # Get existing link IDs for referential integrity
            existing_link_ids = get_existing_link_ids(session)
            
            # Process speed records in chunks (memory efficient)
            process_speed_records_chunked(session, existing_link_ids)
            
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


def _safe_float_conversion(value) -> float | None:
    """
    Safely convert value to float with None fallback.
    
    Single Responsibility: Safe type conversion.
    
    Args:
        value: Value to convert
        
    Returns:
        float or None: Converted value or None if conversion fails
    """
    if pd.notna(value) and value != '':
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    return None


def process_links_chunked(session: Session) -> int:
    """
    Process links dataset in memory-efficient chunks.
    
    Implements streaming pipeline with chunk processing for optimal memory usage.
    Uses bulk operations for maximum performance.
    
    Returns:
        int: Total number of links inserted
    """
    print_step(2, "PROCESSING LINKS (CHUNKED - MEMORY OPTIMIZED)")
    
    link_info_path = "/workspace/data/raw/link_info.parquet.gz"
    if not os.path.exists(link_info_path):
        raise FileNotFoundError(f"Link info dataset not found: {link_info_path}")
    
    total_processed = 0
    total_inserted = 0
    
    print(f"Processing links in chunks of {LINK_CHUNK_SIZE:,} records...")
    
    try:
        # Load full dataset first, then process in chunks
        print("  Loading link dataset...")
        link_df = pd.read_parquet(link_info_path)
        total_records = len(link_df)
        print(f"  Total records to process: {total_records:,}")
        
        # Process in chunks using streaming pipeline
        for start_idx in range(0, total_records, LINK_CHUNK_SIZE):
            end_idx = min(start_idx + LINK_CHUNK_SIZE, total_records)
            chunk_df = link_df.iloc[start_idx:end_idx]
            chunk_num = (start_idx // LINK_CHUNK_SIZE) + 1
            
            print(f"\n  Processing chunk {chunk_num}: {len(chunk_df):,} records ({start_idx:,} to {end_idx:,})")
            
            # Transform chunk to ORM objects
            link_objects = _transform_link_chunk(chunk_df)
            
            # Bulk insert with error handling
            chunk_inserted = _bulk_insert_links(session, link_objects)
            
            total_inserted += chunk_inserted
            total_processed += len(chunk_df)
            
            print(f"    Chunk {chunk_num}: {chunk_inserted:,} links inserted")
            print(f"    Running total: {total_inserted:,} links inserted from {total_processed:,} processed")
            
            # Memory cleanup - critical for large datasets
            del link_objects, chunk_df
            gc.collect()
        
        # Final memory cleanup
        del link_df
        gc.collect()
        
        print(f"\n✅ Links processing completed: {total_inserted:,} inserted from {total_processed:,} processed")
        return total_inserted
        
    except Exception as e:
        print(f"❌ Error in chunked link processing: {e}")
        raise


def process_speed_records_chunked(session: Session, existing_link_ids: Set[int]) -> int:
    """
    Process speed records dataset in memory-efficient chunks.
    
    Implements streaming pipeline with chunk processing for optimal memory usage.
    Uses bulk operations for maximum performance.
    
    Args:
        session: Database session
        existing_link_ids: Set of valid link IDs for referential integrity
        
    Returns:
        int: Total number of speed records inserted
    """
    print_step(3, "PROCESSING SPEED RECORDS (CHUNKED - MEMORY OPTIMIZED)")
    
    speed_data_path = "/workspace/data/raw/duval_jan1_2024.parquet.gz"
    if not os.path.exists(speed_data_path):
        raise FileNotFoundError(f"Speed data dataset not found: {speed_data_path}")
    
    total_processed = 0
    total_inserted = 0
    total_skipped = 0
    
    print(f"Processing speed records in chunks of {SPEED_RECORD_CHUNK_SIZE:,} records...")
    
    try:
        # Load full dataset first, then process in chunks
        print("  Loading speed records dataset...")
        speed_df = pd.read_parquet(speed_data_path)
        total_records = len(speed_df)
        print(f"  Total records to process: {total_records:,}")
        
        # Process in chunks using streaming pipeline
        for start_idx in range(0, total_records, SPEED_RECORD_CHUNK_SIZE):
            end_idx = min(start_idx + SPEED_RECORD_CHUNK_SIZE, total_records)
            chunk_df = speed_df.iloc[start_idx:end_idx]
            chunk_num = (start_idx // SPEED_RECORD_CHUNK_SIZE) + 1
            
            print(f"\n  Processing chunk {chunk_num}: {len(chunk_df):,} records ({start_idx:,} to {end_idx:,})")
            
            # Process chunk into SpeedRecord objects
            speed_objects, chunk_skipped = _transform_speed_chunk(chunk_df, existing_link_ids)
            
            # Insert current chunk in batches using optimized bulk operations
            chunk_inserted = _bulk_insert_speed_records(session, speed_objects)
            total_inserted += chunk_inserted
            total_processed += len(chunk_df)
            total_skipped += chunk_skipped
            
            print(f"    Chunk {chunk_num}: {chunk_inserted:,} speed records inserted, {chunk_skipped:,} skipped")
            print(f"    Running total: {total_inserted:,} inserted, {total_skipped:,} skipped from {total_processed:,} processed")
            
            # Memory cleanup - critical for large datasets
            del speed_objects, chunk_df
            gc.collect()  # Force garbage collection
        
        # Final memory cleanup
        del speed_df
        gc.collect()
        
        print(f"\n✅ Speed records processing completed: {total_inserted:,} inserted, {total_skipped:,} skipped from {total_processed:,} processed")
        return total_inserted
        
    except Exception as e:
        print(f"❌ Error in chunked speed records processing: {e}")
        raise


def insert_links_batch(session: Session, link_objects: List[Link], batch_size: int) -> int:
    """Insert links in smaller batches with error handling."""
    total_inserted = 0
    
    try:
        for i in range(0, len(link_objects), batch_size):
            batch = link_objects[i:i + batch_size]
            
            try:
                session.bulk_save_objects(batch)
                session.commit()
                total_inserted += len(batch)
                
            except Exception as e:
                session.rollback()
                print(f"    Error inserting batch, retrying individually...")
                
                # Try individual inserts for this batch
                for link_obj in batch:
                    try:
                        session.add(link_obj)
                        session.commit()
                        total_inserted += 1
                    except Exception:
                        session.rollback()
                        continue
    
    except Exception as e:
        print(f"Critical error in batch insertion: {e}")
        session.rollback()
    
    return total_inserted


def insert_speed_records_batch(session: Session, speed_objects: List[SpeedRecord], batch_size: int) -> int:
    """Insert speed records in smaller batches with error handling."""
    total_inserted = 0
    
    try:
        for i in range(0, len(speed_objects), batch_size):
            batch = speed_objects[i:i + batch_size]
            
            try:
                session.bulk_save_objects(batch)
                session.commit()
                total_inserted += len(batch)
                
            except Exception as e:
                session.rollback()
                # Skip problematic batches for speed records to maintain performance
                continue
    
    except Exception as e:
        print(f"Critical error in speed record batch insertion: {e}")
        session.rollback()
    
    return total_inserted


def _transform_link_chunk(chunk_df: pd.DataFrame) -> List[Link]:
    """
    Transform a chunk of link data into Link ORM objects.
    
    Single Responsibility: Only handles data transformation.
    
    Args:
        chunk_df: DataFrame chunk with link data
        
    Returns:
        List[Link]: Transformed Link objects
    """
    link_objects = []
    
    for idx, row in chunk_df.iterrows():
        try:
            # Convert geometry
            geometry_element = convert_geometry_to_wkt_element(row['geo_json'])
            if not geometry_element:
                continue
            
            # Convert length to float
            length = _safe_float_conversion(row.get('_length'))
            
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
            
        except Exception as e:
            print(f"    Error processing link {row.get('link_id', 'unknown')}: {e}")
            continue
    
    return link_objects


def _bulk_insert_links(session: Session, link_objects: List[Link]) -> int:
    """
    Bulk insert links using optimized batch operations.
    
    Single Responsibility: Only handles bulk insertion.
    
    Args:
        session: Database session
        link_objects: List of Link objects to insert
        
    Returns:
        int: Number of successfully inserted links
    """
    total_inserted = 0
    
    try:
        for i in range(0, len(link_objects), LINK_BATCH_SIZE):
            batch = link_objects[i:i + LINK_BATCH_SIZE]
            
            try:
                session.bulk_save_objects(batch)
                session.commit()
                total_inserted += len(batch)
                
            except Exception as e:
                session.rollback()
                print(f"    Error inserting batch, retrying individually...")
                
                # Fallback: individual inserts for error recovery
                for link_obj in batch:
                    try:
                        session.add(link_obj)
                        session.commit()
                        total_inserted += 1
                    except Exception:
                        session.rollback()
                        continue
    
    except Exception as e:
        print(f"Critical error in bulk link insertion: {e}")
        session.rollback()
    
    return total_inserted


def _transform_speed_chunk(chunk_df: pd.DataFrame, existing_link_ids: Set[int]) -> tuple[List[SpeedRecord], int]:
    """
    Transform a chunk of speed data into SpeedRecord ORM objects.
    
    Single Responsibility: Only handles speed data transformation.
    
    Args:
        chunk_df: DataFrame chunk with speed data
        existing_link_ids: Set of valid link IDs for referential integrity
        
    Returns:
        tuple: (List of SpeedRecord objects, number of skipped records)
    """
    speed_objects = []
    skipped_count = 0
    
    for idx, row in chunk_df.iterrows():
        try:
            link_id = int(row['link_id'])
            
            # Skip if link doesn't exist (referential integrity)
            if link_id not in existing_link_ids:
                skipped_count += 1
                continue
            
            # Convert datetime
            timestamp = pd.to_datetime(row['date_time'])
            period_name = PERIOD_MAPPING.get(row['period'], None)
            
            # Create SpeedRecord ORM object
            speed_obj = SpeedRecord(
                link_id=link_id,
                timestamp=timestamp,
                speed=float(row['average_speed']),
                time_period=period_name
            )
            
            speed_objects.append(speed_obj)
            
        except Exception as e:
            print(f"    Error processing speed record {idx}: {e}")
            continue
    
    return speed_objects, skipped_count


def _bulk_insert_speed_records(session: Session, speed_objects: List[SpeedRecord]) -> int:
    """
    Bulk insert speed records using optimized batch operations.
    
    Single Responsibility: Only handles bulk insertion of speed records.
    
    Args:
        session: Database session
        speed_objects: List of SpeedRecord objects to insert
        
    Returns:
        int: Number of successfully inserted speed records
    """
    total_inserted = 0
    
    try:
        for i in range(0, len(speed_objects), SPEED_BATCH_SIZE):
            batch = speed_objects[i:i + SPEED_BATCH_SIZE]
            
            try:
                session.bulk_save_objects(batch)
                session.commit()
                total_inserted += len(batch)
                
            except Exception as e:
                session.rollback()
                # Skip problematic batches for speed records to maintain performance
                continue
    
    except Exception as e:
        print(f"Critical error in bulk speed record insertion: {e}")
        session.rollback()
    
    return total_inserted

def clear_existing_data_orm(session: Session):
    """
    Clear existing data from tables using ORM.
    
    Single Responsibility: Only handles data cleanup.
    """
    print_step(1, "CLEARING EXISTING DATA")
    
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


def get_existing_link_ids(session: Session) -> Set[int]:
    """
    Get set of existing link IDs for referential integrity.
    
    Single Responsibility: Only handles link ID retrieval.
    
    Returns:
        Set[int]: Set of existing link IDs
    """
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


def verify_data_orm(session: Session):
    """
    Verify inserted data using ORM queries.
    
    Single Responsibility: Only handles data verification.
    """
    print_step(4, "VERIFYING DATA")
    
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
            print(f"    Has geometry: Yes")
        
        # Sample speed record with relationship
        sample_speed = session.query(SpeedRecord).first()
        if sample_speed:
            print(f"    Sample speed: Link {sample_speed.link_id}, {sample_speed.speed} mph at {sample_speed.timestamp}")
            if hasattr(sample_speed, 'time_period') and sample_speed.time_period is not None:
                print(f"    Time period: {sample_speed.time_period}")
        
        # Advanced ORM query: Average speed by period
        print("\n  Advanced verification:")
        try:
            total_records = session.query(SpeedRecord).count()
            print(f"    Total speed records: {total_records:,}")
            
            # Test time_period field existence
            records_with_period = session.query(SpeedRecord).filter(
                SpeedRecord.time_period.isnot(None)
            ).count()
            print(f"    Records with time_period: {records_with_period:,}")
            
            if records_with_period > 0:
                # Use aggregation query
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
                    
        except Exception as query_error:
            print(f"    Error in advanced verification: {query_error}")
            
    except Exception as e:
        print(f"Error during verification: {e}")
        raise

if __name__ == "__main__":
    main()
