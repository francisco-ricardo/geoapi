#!/usr/bin/env python3
"""
Data exploration script to understand the structure of the Parquet datasets.

This script examines the datasets to understand their schema and content
before implementing the full ingestion process.
"""

import os
import sys
from pathlib import Path

import pandas as pd

# Add project root to Python path
sys.path.insert(0, "/workspace")


def explore_dataset(file_path, dataset_name):
    """Explore a single dataset and print its structure."""
    print(f"\n{'='*60}")
    print(f"EXPLORING {dataset_name.upper()}")
    print(f"File: {file_path}")
    print(f"{'='*60}")

    try:
        # Read the dataset
        print("Reading dataset...")
        df = pd.read_parquet(file_path)

        # Basic info
        print(f"\nDATASET INFO:")
        print(f"  Rows: {len(df):,}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

        # Column info
        print(f"\nCOLUMNS:")
        for i, col in enumerate(df.columns, 1):
            dtype = df[col].dtype
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100
            print(
                f"  {i:2d}. {col:<25} | {str(dtype):<15} | {null_count:>6} nulls ({null_pct:5.1f}%)"
            )

        # Sample data
        print(f"\nSAMPLE DATA (first 3 rows):")
        print(df.head(3).to_string())

        # Unique values for categorical columns
        print(f"\nCATEGORICAL ANALYSIS:")
        for col in df.columns:
            if df[col].dtype == "object" or df[col].dtype == "category":
                unique_count = df[col].nunique()
                if unique_count < 20:  # Show unique values if reasonable count
                    unique_vals = sorted(df[col].dropna().unique())
                    print(f"  {col}: {unique_count} unique values")
                    print(f"    Values: {unique_vals}")
                else:
                    print(
                        f"  {col}: {unique_count} unique values (too many to display)"
                    )

        # Numeric analysis
        print(f"\nNUMERIC ANALYSIS:")
        numeric_cols = df.select_dtypes(include=["number"]).columns
        if len(numeric_cols) > 0:
            print(df[numeric_cols].describe())

        # Datetime analysis
        datetime_cols = df.select_dtypes(include=["datetime64"]).columns
        if len(datetime_cols) > 0:
            print(f"\nDATETIME ANALYSIS:")
            for col in datetime_cols:
                min_date = df[col].min()
                max_date = df[col].max()
                print(f"  {col}: {min_date} to {max_date}")

        return df

    except Exception as e:
        print(f"ERROR reading {dataset_name}: {e}")
        return None


def main():
    """Main exploration function."""
    print("GeoSpatial Links API - Dataset Exploration")
    print("=" * 60)

    # Check if files exist
    raw_dir = Path("/workspace/data/raw")
    link_info_file = raw_dir / "link_info.parquet.gz"
    speed_data_file = raw_dir / "duval_jan1_2024.parquet.gz"

    if not link_info_file.exists():
        print(f"ERROR: {link_info_file} not found!")
        return False

    if not speed_data_file.exists():
        print(f"ERROR: {speed_data_file} not found!")
        return False

    # Explore both datasets
    print("Found both datasets, starting exploration...")

    # Explore Link Info dataset
    link_df = explore_dataset(link_info_file, "Link Info Dataset")

    # Explore Speed Data dataset
    speed_df = explore_dataset(speed_data_file, "Speed Data Dataset")

    # Cross-analysis if both loaded successfully
    if link_df is not None and speed_df is not None:
        print(f"\n{'='*60}")
        print("CROSS-DATASET ANALYSIS")
        print(f"{'='*60}")

        # Check for common link_ids
        if "link_id" in link_df.columns and "link_id" in speed_df.columns:
            link_ids_info = set(link_df["link_id"].unique())
            link_ids_speed = set(speed_df["link_id"].unique())

            print(f"Link IDs in Link Info: {len(link_ids_info):,}")
            print(f"Link IDs in Speed Data: {len(link_ids_speed):,}")
            print(f"Common Link IDs: {len(link_ids_info & link_ids_speed):,}")
            print(f"Link Info only: {len(link_ids_info - link_ids_speed):,}")
            print(f"Speed Data only: {len(link_ids_speed - link_ids_info):,}")

        # Check for geometry columns
        geometry_cols = [
            col
            for col in link_df.columns
            if "geometry" in col.lower()
            or "geom" in col.lower()
            or "wkt" in col.lower()
        ]
        if geometry_cols:
            print(f"\nGeometry columns found: {geometry_cols}")
            for col in geometry_cols:
                sample_geom = (
                    link_df[col].dropna().iloc[0]
                    if not link_df[col].dropna().empty
                    else None
                )
                if sample_geom:
                    print(f"  {col} sample: {str(sample_geom)[:100]}...")

    print(f"\n{'='*60}")
    print("EXPLORATION COMPLETE")
    print(f"{'='*60}")
    print("\nNext steps:")
    print("1. Review the data structure above")
    print("2. Run the ingestion script: python scripts/data/ingest_datasets.py")
    print("3. Verify data in database: make db-shell")

    return True


if __name__ == "__main__":
    try:
        success = main()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nExploration interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during exploration: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
