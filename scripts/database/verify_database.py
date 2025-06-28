#!/usr/bin/env python3
"""
Verify the current state of the database after ingestion.
"""

import sys
sys.path.insert(0, '/workspace')

from app.core.database import get_session_factory
from app.models.link import Link
from app.models.speed_record import SpeedRecord
from sqlalchemy import text, func
from geoalchemy2.functions import ST_AsText

def check_database_state():
    """Check the current state of the database."""
    print("=" * 80)
    print(" DATABASE STATE VERIFICATION")
    print("=" * 80)
    
    Session = get_session_factory()
    
    with Session() as session:
        # Basic counts
        link_count = session.query(Link).count()
        speed_count = session.query(SpeedRecord).count()
        
        print(f"Links in database: {link_count:,}")
        print(f"Speed records in database: {speed_count:,}")
        
        # Check geometry data specifically
        print(f"\nGEOMETRY VERIFICATION:")
        links_with_geom = session.query(Link).filter(Link.geometry.isnot(None)).count()
        print(f"  Links with geometry: {links_with_geom:,}")
        
        if links_with_geom > 0:
            # Get a sample link with geometry
            sample_link = session.query(Link).filter(Link.geometry.isnot(None)).first()
            if sample_link:
                print(f"  Sample link ID: {sample_link.link_id}")
                print(f"  Sample link name: {sample_link.road_name}")
                
                # Try to get the geometry as text
                try:
                    # Use raw SQL to get geometry as text
                    result = session.execute(
                        text("SELECT ST_AsText(geometry) as geom_text FROM links WHERE link_id = :link_id"),
                        {"link_id": sample_link.link_id}
                    ).fetchone()
                    
                    if result and result.geom_text:
                        geom_text = result.geom_text
                        print(f"  Sample geometry type: {geom_text.split('(')[0]}")
                        print(f"  Sample geometry (first 100 chars): {geom_text[:100]}...")
                    else:
                        print("  Could not retrieve geometry as text")
                        
                except Exception as e:
                    print(f"  Error getting geometry: {e}")
        
        # Check speed records
        print(f"\nSPEED RECORDS VERIFICATION:")
        if speed_count > 0:
            sample_speed = session.query(SpeedRecord).first()
            if sample_speed:
                print(f"  Sample speed record: Link {sample_speed.link_id}, {sample_speed.speed} mph")
                print(f"  Sample timestamp: {sample_speed.timestamp}")
                print(f"  Sample time period: {sample_speed.time_period}")
        
        # Check relationship integrity
        print(f"\nRELATIONSHIP VERIFICATION:")
        try:
            # Count speed records that have valid links
            valid_speeds = session.query(SpeedRecord).join(Link, SpeedRecord.link_id == Link.link_id).count()
            print(f"  Speed records with valid links: {valid_speeds:,}")
            
            # Count links that have speed records
            links_with_speeds = session.query(Link).join(SpeedRecord, Link.link_id == SpeedRecord.link_id).distinct().count()
            print(f"  Links with speed records: {links_with_speeds:,}")
            
        except Exception as e:
            print(f"  Error checking relationships: {e}")
        
        # Test a geospatial query
        print(f"\nGEOSPATIAL QUERY TEST:")
        try:
            # Test a simple geospatial function
            result = session.execute(text("SELECT COUNT(*) FROM links WHERE ST_IsValid(geometry)")).fetchone()
            if result:
                valid_geometries = result[0]
                print(f"  Valid geometries: {valid_geometries:,}")
            
            # Test bounding box calculation
            result = session.execute(
                text("SELECT ST_AsText(ST_Extent(geometry)) as bbox FROM links LIMIT 1")
            ).fetchone()
            if result and result.bbox:
                print(f"  Data extent: {result.bbox}")
                
        except Exception as e:
            print(f"  Error in geospatial test: {e}")

def main():
    """Main verification function."""
    try:
        check_database_state()
        print("\n" + "=" * 80)
        print(" VERIFICATION COMPLETED")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
