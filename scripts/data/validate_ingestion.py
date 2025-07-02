#!/usr/bin/env python3
"""
Data Validation Script for Parquet to PostgreSQL Ingestion.

This script validates the data ingestion process by comparing original Parquet
data with imported database records. It performs detailed field-by-field
comparison to ensure data integrity and accuracy.

This is NOT a unit test - it's a validation tool for production data quality.
"""

import json
import os
import sys
from typing import Tuple

import pandas as pd

sys.path.insert(0, "/workspace")

from shapely.geometry import MultiLineString, shape
from sqlalchemy import text

from app.core.database import get_session_factory
from app.models.link import Link
from app.models.speed_record import SpeedRecord


class DataValidationError(Exception):
    """Custom exception for data validation errors."""

    pass


def main():
    """Main validation function."""
    print_section("PARQUET <-> DATABASE VALIDATION")
    print(
        "Validating data integrity between original Parquet files and PostgreSQL database"
    )
    print("This validates the ingestion process accuracy and data quality")

    try:
        # Configuration
        sample_size = 50  # Number of records to validate in detail

        # Load sample data
        link_sample, speed_sample = load_sample_parquet_data(sample_size)

        # Run validations
        validations = [
            ("Link Data Validation", lambda: validate_link_data(link_sample)),
            ("Speed Data Validation", lambda: validate_speed_data(speed_sample)),
            ("Data Integrity Validation", validate_data_integrity),
            ("Statistical Consistency Validation", validate_statistical_consistency),
        ]

        all_passed = True
        results = {}

        for validation_name, validation_func in validations:
            try:
                passed = validation_func()
                results[validation_name] = passed
                all_passed = all_passed and passed
            except Exception as e:
                print_result(False, f"{validation_name} failed with error: {e}")
                results[validation_name] = False
                all_passed = False

        # Final results
        print_section("VALIDATION RESULTS SUMMARY")

        for validation_name, passed in results.items():
            status = "PASSED" if passed else "FAILED"
            print(f"{validation_name}: {status}")

        if all_passed:
            print_result(True, "ALL VALIDATIONS PASSED - Data ingestion is accurate")
            print(
                "\n*** Data integrity confirmed! The ingestion process worked correctly. ***"
            )
        else:
            print_result(False, "SOME VALIDATIONS FAILED - Data ingestion has issues")
            print(
                "\n*** WARNING: Data integrity issues detected. Please review the failed validations above. ***"
            )
            sys.exit(1)

    except Exception as e:
        print(f"\nCritical error during validation: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_result(passed: bool, message: str):
    """Print validation result with status."""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {message}")
    return passed


def load_sample_parquet_data(
    sample_size: int = 100,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load sample data from original Parquet files."""
    print_section("LOADING SAMPLE PARQUET DATA")

    # Load Link Info Dataset
    link_info_path = "/workspace/data/raw/link_info.parquet.gz"
    if not os.path.exists(link_info_path):
        raise FileNotFoundError(f"Link info dataset not found: {link_info_path}")

    link_df = pd.read_parquet(link_info_path)
    print(f"Total links in Parquet: {len(link_df):,}")

    # Sample links (ensure we get a representative sample)
    link_sample = link_df.sample(n=min(sample_size, len(link_df)), random_state=42)
    print(f"Selected {len(link_sample)} link samples")

    # Load Speed Data Dataset
    speed_data_path = "/workspace/data/raw/duval_jan1_2024.parquet.gz"
    if not os.path.exists(speed_data_path):
        raise FileNotFoundError(f"Speed data dataset not found: {speed_data_path}")

    speed_df = pd.read_parquet(speed_data_path)
    print(f"Total speed records in Parquet: {len(speed_df):,}")

    # Sample speed records from the same links we sampled
    sample_link_ids = set(link_sample["link_id"].tolist())
    speed_sample = speed_df[speed_df["link_id"].isin(sample_link_ids)]

    # If we don't have enough speed records from sampled links, sample more
    if len(speed_sample) < sample_size:
        additional_speeds = speed_df[~speed_df["link_id"].isin(sample_link_ids)].sample(
            n=min(sample_size - len(speed_sample), len(speed_df) - len(speed_sample)),
            random_state=42,
        )
        speed_sample = pd.concat([speed_sample, additional_speeds])

    print(f"Selected {len(speed_sample)} speed record samples")

    return link_sample, speed_sample


def validate_link_data(link_sample: pd.DataFrame) -> bool:
    """Validate link data between Parquet and database."""
    print_section("VALIDATING LINK DATA")

    Session = get_session_factory()
    all_passed = True

    with Session() as session:
        for idx, parquet_row in link_sample.iterrows():
            link_id = int(parquet_row["link_id"])

            # Get corresponding database record
            db_link = session.query(Link).filter(Link.link_id == link_id).first()

            if not db_link:
                all_passed = print_result(
                    False, f"Link {link_id} not found in database"
                )
                continue

            # Validate basic fields
            expected_road_name = (
                parquet_row["road_name"] if pd.notna(parquet_row["road_name"]) else None
            )
            actual_road_name = db_link.road_name

            if expected_road_name != actual_road_name:
                all_passed = print_result(
                    False,
                    f"Link {link_id} road_name mismatch: expected '{expected_road_name}', got '{actual_road_name}'",
                )
                continue

            # Validate length (with tolerance for float precision)
            expected_length = None
            if pd.notna(parquet_row["_length"]) and parquet_row["_length"] != "":
                try:
                    expected_length = float(parquet_row["_length"])
                except (ValueError, TypeError):
                    expected_length = None

            actual_length = db_link.length

            if expected_length is not None and actual_length is not None:
                if (
                    abs(expected_length - actual_length) > 0.0001
                ):  # Tolerance for float precision
                    all_passed = print_result(
                        False,
                        f"Link {link_id} length mismatch: expected {expected_length}, got {actual_length}",
                    )
                    continue
            elif expected_length != actual_length:  # Both None or one is None
                all_passed = print_result(
                    False,
                    f"Link {link_id} length mismatch: expected {expected_length}, got {actual_length}",
                )
                continue

            # Validate geometry
            if not validate_link_geometry(session, link_id, parquet_row["geo_json"]):
                all_passed = False
                continue

            print_result(True, f"Link {link_id} validation passed")

    return all_passed


def validate_link_geometry(session, link_id: int, original_geojson: str) -> bool:
    """Validate geometry data for a specific link."""
    try:
        # Parse original GeoJSON
        if isinstance(original_geojson, str):
            geo_data = json.loads(original_geojson)
        else:
            geo_data = original_geojson

        # Convert to Shapely geometry
        original_geom = shape(geo_data)

        # Handle MultiLineString to LineString conversion (as done in ingestion)
        if original_geom.geom_type == "MultiLineString":
            if (
                isinstance(original_geom, MultiLineString)
                and len(original_geom.geoms) > 0
            ):
                original_geom = original_geom.geoms[0]
            else:
                return print_result(False, f"Link {link_id} has empty MultiLineString")

        # Get geometry from database as GeoJSON
        result = session.execute(
            text(
                "SELECT ST_AsGeoJSON(geometry, 6) as geom_json FROM links WHERE link_id = :link_id"
            ),
            {"link_id": link_id},
        ).fetchone()

        if not result or not result.geom_json:
            return print_result(False, f"Link {link_id} has no geometry in database")

        # Parse database GeoJSON
        db_geo_data = json.loads(result.geom_json)
        db_geom = shape(db_geo_data)

        # Compare geometries (with small tolerance for precision)
        if not original_geom.equals(db_geom):
            # Check if they're almost equal (allowing for small precision differences)
            if original_geom.distance(db_geom) > 0.000001:  # Very small tolerance
                return print_result(
                    False,
                    f"Link {link_id} geometry mismatch: shapes significantly different",
                )

        return True

    except Exception as e:
        return print_result(False, f"Link {link_id} geometry validation error: {e}")


def validate_speed_data(speed_sample: pd.DataFrame) -> bool:
    """Validate speed data between Parquet and database."""
    print_section("VALIDATING SPEED DATA")

    Session = get_session_factory()
    all_passed = True

    # Period mapping (same as in ingestion script)
    period_mapping = {
        1: "Overnight",
        2: "Early Morning",
        3: "AM Peak",
        4: "Midday",
        5: "Early Afternoon",
        6: "PM Peak",
        7: "Evening",
    }

    with Session() as session:
        for idx, parquet_row in speed_sample.iterrows():
            link_id = int(parquet_row["link_id"])
            timestamp = pd.to_datetime(parquet_row["date_time"])
            expected_speed = float(parquet_row["average_speed"])
            expected_period = period_mapping.get(parquet_row["period"], None)

            # Find corresponding database record
            db_speed = (
                session.query(SpeedRecord)
                .filter(
                    SpeedRecord.link_id == link_id, SpeedRecord.timestamp == timestamp
                )
                .first()
            )

            if not db_speed:
                all_passed = print_result(
                    False,
                    f"Speed record for link {link_id} at {timestamp} not found in database",
                )
                continue

            # Validate speed (with tolerance for float precision)
            if abs(expected_speed - db_speed.speed) > 0.01:  # 0.01 mph tolerance
                all_passed = print_result(
                    False,
                    f"Speed mismatch for link {link_id}: expected {expected_speed}, got {db_speed.speed}",
                )
                continue

            # Validate time period
            if expected_period != db_speed.time_period:
                all_passed = print_result(
                    False,
                    f"Time period mismatch for link {link_id}: expected '{expected_period}', got '{db_speed.time_period}'",
                )
                continue

            print_result(
                True,
                f"Speed record for link {link_id} at {timestamp} validation passed",
            )

    return all_passed


def validate_data_integrity() -> bool:
    """Validate overall data integrity and relationships."""
    print_section("VALIDATING DATA INTEGRITY")

    Session = get_session_factory()
    all_passed = True

    with Session() as session:
        # Check that all speed records have valid links
        orphaned_speeds = session.execute(
            text(
                """
            SELECT COUNT(*) as count
            FROM speed_records s
            LEFT JOIN links l ON s.link_id = l.link_id
            WHERE l.link_id IS NULL
        """
            )
        ).fetchone()

        if orphaned_speeds.count > 0:
            all_passed = print_result(
                False,
                f"Found {orphaned_speeds.count} orphaned speed records (no corresponding link)",
            )
        else:
            print_result(True, "All speed records have valid link references")

        # Check that all links have valid geometries
        invalid_geometries = session.execute(
            text(
                """
            SELECT COUNT(*) as count
            FROM links
            WHERE geometry IS NULL OR NOT ST_IsValid(geometry)
        """
            )
        ).fetchone()

        if invalid_geometries.count > 0:
            all_passed = print_result(
                False, f"Found {invalid_geometries.count} links with invalid geometries"
            )
        else:
            print_result(True, "All links have valid geometries")

        # Check coordinate system consistency
        srid_check = session.execute(
            text(
                """
            SELECT DISTINCT ST_SRID(geometry) as srid, COUNT(*) as count
            FROM links
            GROUP BY ST_SRID(geometry)
        """
            )
        ).fetchall()

        if len(srid_check) != 1 or srid_check[0].srid != 4326:
            all_passed = print_result(False, "Inconsistent SRID values found")
        else:
            print_result(
                True, f"All geometries use consistent SRID: {srid_check[0].srid}"
            )

    return all_passed


def validate_statistical_consistency() -> bool:
    """Validate statistical consistency between Parquet and database."""
    print_section("VALIDATING STATISTICAL CONSISTENCY")

    all_passed = True

    # Load full datasets for statistical comparison
    link_df = pd.read_parquet("/workspace/data/raw/link_info.parquet.gz")
    speed_df = pd.read_parquet("/workspace/data/raw/duval_jan1_2024.parquet.gz")

    Session = get_session_factory()

    with Session() as session:
        # Compare record counts
        db_link_count = session.query(Link).count()
        parquet_link_count = len(link_df)

        if db_link_count != parquet_link_count:
            all_passed = print_result(
                False,
                f"Link count mismatch: Parquet has {parquet_link_count}, DB has {db_link_count}",
            )
        else:
            print_result(True, f"Link counts match: {db_link_count}")

        db_speed_count = session.query(SpeedRecord).count()
        parquet_speed_count = len(speed_df)

        if db_speed_count != parquet_speed_count:
            all_passed = print_result(
                False,
                f"Speed record count mismatch: Parquet has {parquet_speed_count}, DB has {db_speed_count}",
            )
        else:
            print_result(True, f"Speed record counts match: {db_speed_count}")

        # Compare average speeds by period
        period_mapping = {
            1: "Overnight",
            2: "Early Morning",
            3: "AM Peak",
            4: "Midday",
            5: "Early Afternoon",
            6: "PM Peak",
            7: "Evening",
        }

        for period_id, period_name in period_mapping.items():
            parquet_avg = speed_df[speed_df["period"] == period_id][
                "average_speed"
            ].mean()

            db_avg_result = session.execute(
                text(
                    """
                SELECT AVG(speed) as avg_speed
                FROM speed_records
                WHERE time_period = :period_name
            """
                ),
                {"period_name": period_name},
            ).fetchone()

            db_avg = float(db_avg_result.avg_speed) if db_avg_result.avg_speed else 0

            if abs(parquet_avg - db_avg) > 0.1:  # 0.1 mph tolerance
                all_passed = print_result(
                    False,
                    f"Average speed mismatch for {period_name}: Parquet {parquet_avg:.2f}, DB {db_avg:.2f}",
                )
            else:
                print_result(
                    True, f"Average speed for {period_name} matches: {db_avg:.2f} mph"
                )

    return all_passed


if __name__ == "__main__":
    main()
