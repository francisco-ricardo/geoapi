# Data Directory Structure

This directory contains the datasets used by the GeoSpatial Links API.

## Directory Structure

```
data/
├── raw/                     # Original datasets (Parquet files)
│   ├── link_info.parquet.gz        # Link information dataset
│   └── duval_jan1_2024.parquet.gz  # Speed data for January 1, 2024
└── processed/              # Processed/transformed data (optional)
    └── (generated files)
```

## Datasets Description

### 1. Link Info Dataset (`link_info.parquet.gz`)
- **Source**: https://cdn.urbansdk.com/data-engineering-interview/link_info.parquet.gz
- **Content**: Road segment information with geometry
- **Expected Fields**: link_id, road_name, geometry (LINESTRING), length, etc.

### 2. Speed Data (`duval_jan1_2024.parquet.gz`)
- **Source**: https://cdn.urbansdk.com/data-engineering-interview/duval_jan1_2024.parquet.gz
- **Content**: Traffic speed measurements for January 1, 2024
- **Expected Fields**: link_id, timestamp, speed, day_of_week, etc.

## Usage

Place the downloaded Parquet files in the `raw/` directory:

```bash
# Copy your downloaded files here
cp path/to/link_info.parquet.gz data/raw/
cp path/to/duval_jan1_2024.parquet.gz data/raw/
```

The ingestion scripts will automatically process these files and populate the PostgreSQL database.

## Ingestion Process

Run the data ingestion script:

```bash
python scripts/data/ingest_datasets.py
```

This will:
1. Read the Parquet files from `data/raw/`
2. Process and validate the data
3. Insert into PostgreSQL/PostGIS database
4. Create spatial indexes for performance
