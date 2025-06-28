#!/usr/bin/env python3
"""
PostGIS Geometry Verification Script

This script demonstrates how to properly query and display PostGIS geometry data
using various PostGIS functions for spatial analysis.
"""

import sys
sys.path.insert(0, '/workspace')

from app.core.database import get_session_factory
from sqlalchemy import text
import json

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def execute_query(session, query, description):
    """Execute a query and display results."""
    print(f"\n{description}")
    print("-" * 60)
    
    try:
        result = session.execute(text(query))
        rows = result.fetchall()
        
        if not rows:
            print("No results returned.")
            return
        
        # Print column headers
        if hasattr(result, 'keys'):
            headers = result.keys()
            print(" | ".join(f"{header:<20}" for header in headers))
            print("-" * (22 * len(headers)))
        
        # Print rows
        for row in rows:
            values = []
            for value in row:
                if isinstance(value, str) and len(value) > 50:
                    # Truncate long strings (like WKT)
                    values.append(value[:47] + "...")
                elif isinstance(value, float):
                    values.append(f"{value:.6f}")
                else:
                    values.append(str(value))
            print(" | ".join(f"{value:<20}" for value in values))
            
    except Exception as e:
        print(f"Error executing query: {e}")

def verify_postgis_geometries():
    """Verify PostGIS geometry data with comprehensive queries."""
    
    print_section("POSTGIS GEOMETRY VERIFICATION")
    
    Session = get_session_factory()
    
    with Session() as session:
        
        # 1. Basic PostGIS information
        execute_query(session, 
            "SELECT PostGIS_version();",
            "1. PostGIS Version Check")
        
        # 2. Geometry summary
        execute_query(session, """
            SELECT 
                COUNT(*) as total_links,
                COUNT(geometry) as links_with_geometry,
                COUNT(CASE WHEN ST_IsValid(geometry) THEN 1 END) as valid_geometries
            FROM links;
        """, "2. Geometry Summary")
        
        # 3. Geometry types
        execute_query(session, """
            SELECT 
                ST_GeometryType(geometry) as geom_type,
                COUNT(*) as count,
                ROUND(AVG(ST_Length(geometry))::numeric, 8) as avg_length_degrees,
                ROUND(AVG(ST_Length(ST_Transform(geometry, 3857)))::numeric, 2) as avg_length_meters
            FROM links 
            WHERE geometry IS NOT NULL
            GROUP BY ST_GeometryType(geometry);
        """, "3. Geometry Types and Statistics")
        
        # 4. Sample geometries as WKT
        execute_query(session, """
            SELECT 
                link_id,
                road_name,
                ST_AsText(geometry) as geometry_wkt,
                ST_SRID(geometry) as srid
            FROM links 
            WHERE geometry IS NOT NULL 
            ORDER BY link_id
            LIMIT 3;
        """, "4. Sample Geometries (WKT Format)")
        
        # 5. Sample geometries as GeoJSON (more readable)
        print("\n5. Sample Geometries (GeoJSON Format)")
        print("-" * 60)
        try:
            result = session.execute(text("""
                SELECT 
                    link_id,
                    road_name,
                    ST_AsGeoJSON(geometry, 6) as geometry_geojson,
                    ROUND(ST_Length(ST_Transform(geometry, 3857))::numeric, 2) as length_meters
                FROM links 
                WHERE geometry IS NOT NULL 
                ORDER BY link_id
                LIMIT 3;
            """))
            
            for row in result:
                print(f"\nLink ID: {row.link_id}")
                print(f"Road Name: {row.road_name}")
                print(f"Length (meters): {row.length_meters}")
                
                # Pretty print the GeoJSON
                geojson = json.loads(row.geometry_geojson)
                print(f"GeoJSON: {json.dumps(geojson, indent=2)}")
                print("-" * 40)
                
        except Exception as e:
            print(f"Error displaying GeoJSON: {e}")
        
        # 6. Data extent
        execute_query(session, """
            SELECT 
                ST_AsText(ST_Extent(geometry)) as data_extent
            FROM links;
        """, "6. Geographic Extent of Data")
        
        # 7. Coordinate system
        execute_query(session, """
            SELECT DISTINCT 
                ST_SRID(geometry) as srid,
                COUNT(*) as count
            FROM links 
            WHERE geometry IS NOT NULL
            GROUP BY ST_SRID(geometry);
        """, "7. Coordinate Reference Systems")
        
        # 8. Sample coordinate points
        execute_query(session, """
            SELECT 
                link_id,
                road_name,
                ROUND(ST_X(ST_StartPoint(geometry))::numeric, 6) as start_lon,
                ROUND(ST_Y(ST_StartPoint(geometry))::numeric, 6) as start_lat,
                ROUND(ST_X(ST_EndPoint(geometry))::numeric, 6) as end_lon,
                ROUND(ST_Y(ST_EndPoint(geometry))::numeric, 6) as end_lat,
                ST_NumPoints(geometry) as num_points
            FROM links 
            WHERE geometry IS NOT NULL 
            ORDER BY link_id
            LIMIT 5;
        """, "8. Sample Start/End Coordinates")
        
        # 9. Links with speed data
        execute_query(session, """
            SELECT 
                l.link_id,
                l.road_name,
                COUNT(s.id) as speed_records,
                ROUND(AVG(s.speed)::numeric, 2) as avg_speed_mph,
                ROUND(ST_Length(ST_Transform(l.geometry, 3857))::numeric, 2) as length_meters
            FROM links l
            LEFT JOIN speed_records s ON l.link_id = s.link_id
            WHERE l.geometry IS NOT NULL
            GROUP BY l.link_id, l.road_name, l.geometry
            HAVING COUNT(s.id) > 0
            ORDER BY avg_speed_mph DESC
            LIMIT 5;
        """, "9. Links with Speed Data (Top 5 by Average Speed)")

def main():
    """Main verification function."""
    try:
        verify_postgis_geometries()
        
        print_section("VERIFICATION COMPLETED")
        print("\nTo connect to PostgreSQL directly with psql:")
        print("1. From inside the container:")
        print("   psql -h postgres_db -U geoapi -d geoapi_db")
        print("2. Then run the queries from /workspace/scripts/database/postgis_queries.sql")
        print("\nPassword: geoapi_password")
        
    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
