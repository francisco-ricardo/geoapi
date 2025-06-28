#!/usr/bin/env python3
"""
Analyze the original Parquet data to understand structure and content.
"""

import pandas as pd
import json
from shapely.geometry import shape

def analyze_link_data():
    """Analyze the link_info.parquet.gz dataset."""
    print("=" * 80)
    print(" ANALYZING LINK INFO DATASET")
    print("=" * 80)
    
    # Load the dataset
    link_df = pd.read_parquet("/workspace/data/raw/link_info.parquet.gz")
    
    print(f"Total links: {len(link_df):,}")
    print(f"Columns: {list(link_df.columns)}")
    print(f"Data types:\n{link_df.dtypes}")
    
    # Examine sample data
    print("\nSample rows:")
    print(link_df.head())
    
    # Check for missing values
    print(f"\nMissing values:")
    print(link_df.isnull().sum())
    
    # Analyze geo_json column specifically
    print("\nGeo_json analysis:")
    if 'geo_json' in link_df.columns:
        sample_geo = link_df['geo_json'].iloc[0]
        print(f"Sample geo_json type: {type(sample_geo)}")
        print(f"Sample geo_json content (first 200 chars): {str(sample_geo)[:200]}")
        
        # Try to parse the GeoJSON
        try:
            if isinstance(sample_geo, str):
                geo_data = json.loads(sample_geo)
            else:
                geo_data = sample_geo
            
            print(f"GeoJSON type: {geo_data.get('type', 'Unknown')}")
            if 'coordinates' in geo_data:
                coords = geo_data['coordinates']
                print(f"Coordinates structure: {type(coords)}, length: {len(coords) if hasattr(coords, '__len__') else 'N/A'}")
                
            # Convert to Shapely geometry
            geom = shape(geo_data)
            print(f"Shapely geometry type: {geom.geom_type}")
            print(f"Geometry bounds: {geom.bounds}")
            
        except Exception as e:
            print(f"Error parsing geo_json: {e}")
    
    return link_df

def analyze_speed_data():
    """Analyze the duval_jan1_2024.parquet.gz dataset."""
    print("\n" + "=" * 80)
    print(" ANALYZING SPEED DATASET")
    print("=" * 80)
    
    # Load the dataset
    speed_df = pd.read_parquet("/workspace/data/raw/duval_jan1_2024.parquet.gz")
    
    print(f"Total speed records: {len(speed_df):,}")
    print(f"Columns: {list(speed_df.columns)}")
    print(f"Data types:\n{speed_df.dtypes}")
    
    # Examine sample data
    print("\nSample rows:")
    print(speed_df.head())
    
    # Check for missing values
    print(f"\nMissing values:")
    print(speed_df.isnull().sum())
    
    # Analyze key columns
    if 'period' in speed_df.columns:
        print(f"\nPeriod values: {sorted(speed_df['period'].unique())}")
    
    if 'average_speed' in speed_df.columns:
        print(f"\nSpeed statistics:")
        print(speed_df['average_speed'].describe())
    
    if 'link_id' in speed_df.columns:
        print(f"\nUnique links in speed data: {speed_df['link_id'].nunique():,}")
    
    if 'date_time' in speed_df.columns:
        print(f"\nDate range: {speed_df['date_time'].min()} to {speed_df['date_time'].max()}")
    
    return speed_df

def check_data_compatibility(link_df, speed_df):
    """Check compatibility between datasets."""
    print("\n" + "=" * 80)
    print(" CHECKING DATA COMPATIBILITY")
    print("=" * 80)
    
    # Check link_id overlap
    link_ids_in_links = set(link_df['link_id'].unique()) if 'link_id' in link_df.columns else set()
    link_ids_in_speed = set(speed_df['link_id'].unique()) if 'link_id' in speed_df.columns else set()
    
    print(f"Unique link_ids in link_info: {len(link_ids_in_links):,}")
    print(f"Unique link_ids in speed_data: {len(link_ids_in_speed):,}")
    print(f"Common link_ids: {len(link_ids_in_links & link_ids_in_speed):,}")
    print(f"Link_ids only in link_info: {len(link_ids_in_links - link_ids_in_speed):,}")
    print(f"Link_ids only in speed_data: {len(link_ids_in_speed - link_ids_in_links):,}")

def main():
    """Main analysis function."""
    print("URBAN SDK DATA ANALYSIS")
    print("Analyzing Parquet datasets before ingestion...")
    
    try:
        # Analyze both datasets
        link_df = analyze_link_data()
        speed_df = analyze_speed_data()
        
        # Check compatibility
        check_data_compatibility(link_df, speed_df)
        
        print("\n" + "=" * 80)
        print(" ANALYSIS COMPLETED")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
