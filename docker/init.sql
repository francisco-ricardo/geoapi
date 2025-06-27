-- Enable PostGIS extension for geospatial data support
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable topology extension for additional geometry types
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Create database tables
-- These tables will be created automatically when the container starts

-- Links table for road segments
CREATE TABLE IF NOT EXISTS links (
    link_id INTEGER PRIMARY KEY,
    road_name VARCHAR(255),
    length REAL CHECK (length >= 0),
    road_type VARCHAR(100),
    speed_limit INTEGER CHECK (speed_limit >= 0 AND speed_limit <= 200),
    geometry GEOMETRY(LINESTRING, 4326)
);

-- Speed records table for traffic measurements
CREATE TABLE IF NOT EXISTS speed_records (
    id SERIAL PRIMARY KEY,
    link_id INTEGER NOT NULL REFERENCES links(link_id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    speed_kph REAL NOT NULL CHECK (speed_kph >= 0 AND speed_kph <= 300),
    period VARCHAR(20)
);

-- Create spatial index for better performance
CREATE INDEX IF NOT EXISTS idx_links_geometry ON links USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_speed_records_link_id ON speed_records (link_id);
CREATE INDEX IF NOT EXISTS idx_speed_records_timestamp ON speed_records (timestamp);

-- Insert sample data for testing
INSERT INTO links (link_id, road_name, length, road_type, speed_limit, geometry) VALUES
(12345, 'Main Street', 1250.5, 'arterial', 50, ST_GeomFromText('LINESTRING(-122.4194 37.7749, -122.4094 37.7849)', 4326)),
(12346, 'Highway 101', 2500.0, 'highway', 65, ST_GeomFromText('LINESTRING(-122.4 37.8, -122.3 37.9)', 4326)),
(12347, 'Oak Avenue', 800.0, 'residential', 35, ST_GeomFromText('LINESTRING(-122.41 37.77, -122.40 37.78)', 4326))
ON CONFLICT (link_id) DO NOTHING;

-- Insert sample speed records
INSERT INTO speed_records (link_id, timestamp, speed_kph, period) VALUES
(12345, NOW() - INTERVAL '1 hour', 45.5, 'afternoon'),
(12345, NOW() - INTERVAL '2 hours', 52.0, 'afternoon'),
(12346, NOW() - INTERVAL '30 minutes', 68.2, 'afternoon'),
(12347, NOW() - INTERVAL '15 minutes', 32.1, 'afternoon')
ON CONFLICT DO NOTHING;

