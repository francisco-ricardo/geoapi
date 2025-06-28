-- PostGIS Geometry Verification Queries
-- Use these queries in psql to properly view spatial data

-- 1. BASIC GEOMETRY INFORMATION
-- Check if PostGIS is installed and working
SELECT PostGIS_version();

-- Count total records and geometries
SELECT 
    COUNT(*) as total_links,
    COUNT(geometry) as links_with_geometry,
    COUNT(CASE WHEN ST_IsValid(geometry) THEN 1 END) as valid_geometries
FROM links;

-- 2. GEOMETRY TYPES AND PROPERTIES
-- See geometry types and properties
SELECT 
    ST_GeometryType(geometry) as geom_type,
    COUNT(*) as count,
    AVG(ST_Length(geometry)) as avg_length_degrees,
    AVG(ST_Length(ST_Transform(geometry, 3857))) as avg_length_meters
FROM links 
WHERE geometry IS NOT NULL
GROUP BY ST_GeometryType(geometry);

-- 3. VIEW SAMPLE GEOMETRIES AS TEXT
-- View a few sample geometries as readable text
SELECT 
    link_id,
    road_name,
    ST_AsText(geometry) as geometry_wkt,
    ST_SRID(geometry) as srid,
    ST_Length(geometry) as length_degrees
FROM links 
WHERE geometry IS NOT NULL 
LIMIT 5;

-- 4. VIEW GEOMETRIES AS GEOJSON (Most readable format)
-- This is probably what you want to see
SELECT 
    link_id,
    road_name,
    ST_AsGeoJSON(geometry) as geometry_geojson,
    ST_Length(ST_Transform(geometry, 3857)) as length_meters
FROM links 
WHERE geometry IS NOT NULL 
LIMIT 3;

-- 5. BOUNDING BOX AND EXTENT
-- See the overall geographic extent of your data
SELECT 
    ST_AsText(ST_Extent(geometry)) as data_extent,
    ST_AsGeoJSON(ST_Extent(geometry)) as extent_geojson
FROM links;

-- 6. COORDINATE SYSTEM INFORMATION
-- Check coordinate reference system
SELECT DISTINCT 
    ST_SRID(geometry) as srid,
    COUNT(*) as count
FROM links 
WHERE geometry IS NOT NULL
GROUP BY ST_SRID(geometry);

-- 7. SAMPLE COORDINATES
-- Extract and display coordinate points
SELECT 
    link_id,
    road_name,
    ST_X(ST_StartPoint(geometry)) as start_lon,
    ST_Y(ST_StartPoint(geometry)) as start_lat,
    ST_X(ST_EndPoint(geometry)) as end_lon,
    ST_Y(ST_EndPoint(geometry)) as end_lat,
    ST_NumPoints(geometry) as num_points
FROM links 
WHERE geometry IS NOT NULL 
LIMIT 5;

-- 8. SPECIFIC LINK DETAILS
-- Look at a specific link in detail
SELECT 
    link_id,
    road_name,
    length,
    ST_AsText(geometry) as wkt,
    ST_AsGeoJSON(geometry, 6) as geojson,  -- 6 decimal places
    ST_Length(geometry) as length_degrees,
    ST_Length(ST_Transform(geometry, 3857)) as length_meters,
    ST_NumPoints(geometry) as point_count,
    ST_X(ST_Centroid(geometry)) as center_lon,
    ST_Y(ST_Centroid(geometry)) as center_lat
FROM links 
WHERE link_id = 1295558348;  -- Replace with any link_id you want to examine

-- 9. GEOGRAPHIC DISTRIBUTION
-- See geographic distribution of your links
SELECT 
    ROUND(ST_X(ST_Centroid(geometry))::numeric, 2) as longitude_bin,
    ROUND(ST_Y(ST_Centroid(geometry))::numeric, 2) as latitude_bin,
    COUNT(*) as link_count
FROM links 
WHERE geometry IS NOT NULL
GROUP BY 
    ROUND(ST_X(ST_Centroid(geometry))::numeric, 2),
    ROUND(ST_Y(ST_Centroid(geometry))::numeric, 2)
ORDER BY link_count DESC
LIMIT 10;

-- 10. JOIN WITH SPEED DATA
-- See links with their speed data
SELECT 
    l.link_id,
    l.road_name,
    ST_AsText(l.geometry) as geometry,
    COUNT(s.id) as speed_record_count,
    AVG(s.speed) as avg_speed,
    MIN(s.timestamp) as first_measurement,
    MAX(s.timestamp) as last_measurement
FROM links l
LEFT JOIN speed_records s ON l.link_id = s.link_id
WHERE l.geometry IS NOT NULL
GROUP BY l.link_id, l.road_name, l.geometry
HAVING COUNT(s.id) > 0
ORDER BY avg_speed DESC
LIMIT 5;
