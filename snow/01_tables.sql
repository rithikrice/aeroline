-- Create tables for AeroLine

USE DATABASE AEROLINE_DB;
USE SCHEMA PUBLIC;

-- Raw flight data from OpenSky
CREATE TABLE IF NOT EXISTS FLIGHTS_RAW (
    snapshot_ts TIMESTAMP NOT NULL,
    icao24 STRING NOT NULL,
    callsign STRING,
    origin_country STRING,
    time_position NUMBER,
    last_contact NUMBER,
    lon FLOAT,
    lat FLOAT,
    baro_altitude FLOAT,
    on_ground BOOLEAN DEFAULT FALSE,
    velocity FLOAT,
    true_track FLOAT,
    vertical_rate FLOAT,
    sensors ARRAY,
    geo_altitude FLOAT,
    squawk STRING,
    spi BOOLEAN,
    position_source NUMBER,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
) COMMENT = 'Raw flight tracking data from OpenSky or CSV replay';

-- Flight features table (materialized)
CREATE TABLE IF NOT EXISTS FLIGHT_FEATS (
    snapshot_ts TIMESTAMP NOT NULL,
    icao24 STRING NOT NULL,
    callsign STRING,
    lat FLOAT,
    lon FLOAT,
    eta_drift_min FLOAT COMMENT 'ETA drift in minutes (positive = late)',
    route_dev_km FLOAT COMMENT 'Route deviation in kilometers',
    speed_zscore FLOAT COMMENT 'Speed z-score relative to route average',
    FRS FLOAT COMMENT 'Flight Risk Score (0-1)',
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
) COMMENT = 'Engineered features for Flight Risk Score';

-- Raw machine data from UCI or stub
CREATE TABLE IF NOT EXISTS MACHINES_RAW (
    machine_id STRING NOT NULL,
    type STRING COMMENT 'Machine type: L, M, or H',
    air_temp FLOAT COMMENT 'Air temperature in Kelvin',
    process_temp FLOAT COMMENT 'Process temperature in Kelvin',
    rotational_speed FLOAT COMMENT 'Rotational speed in RPM',
    torque FLOAT COMMENT 'Torque in Nm',
    tool_wear FLOAT COMMENT 'Tool wear in units',
    failure_label INT COMMENT '0 = no failure, 1 = failure',
    event_ts TIMESTAMP NOT NULL,
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
) COMMENT = 'Raw machine sensor and maintenance data';

-- Maintenance features table (materialized)
CREATE TABLE IF NOT EXISTS MAINT_FEATS (
    event_ts TIMESTAMP NOT NULL,
    machine_id STRING NOT NULL,
    air_temp_zscore FLOAT,
    process_temp_zscore FLOAT,
    rotational_speed_zscore FLOAT,
    torque_zscore FLOAT,
    tool_wear_normalized FLOAT,
    temp_deviation FLOAT COMMENT 'Combined temperature deviation',
    speed_variance FLOAT COMMENT 'Speed variance over time window',
    FLS FLOAT COMMENT 'Failure Likelihood Score (0-1)',
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
) COMMENT = 'Engineered features for Failure Likelihood Score';

-- Jobs table (BOM/job mapping)
CREATE TABLE IF NOT EXISTS JOBS (
    job_id STRING NOT NULL PRIMARY KEY,
    machine_id STRING NOT NULL,
    bom_item STRING COMMENT 'Bill of Materials item',
    inbound_flight_callsign STRING COMMENT 'Flight bringing required parts',
    planned_start_ts TIMESTAMP NOT NULL,
    planned_end_ts TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
) COMMENT = 'Manufacturing jobs with dependencies on flights and machines';

-- Risk join table (will become dynamic table)
CREATE TABLE IF NOT EXISTS RISK_JOIN (
    job_id STRING NOT NULL,
    machine_id STRING NOT NULL,
    callsign STRING,
    FRS FLOAT DEFAULT 0.5,
    FLS FLOAT DEFAULT 0.5,
    otif_value FLOAT DEFAULT 10000,
    expedite_cost FLOAT DEFAULT 3000,
    downtime_cost FLOAT DEFAULT 3000,
    roi FLOAT DEFAULT 0,
    action STRING DEFAULT 'NO_ACTION',
    explain_json VARIANT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
) COMMENT = 'Joined risk assessment with prescriptions';

-- Cortex alerts table (fallback for when Cortex not available)
CREATE TABLE IF NOT EXISTS CORTEX_ALERTS (
    alert_id STRING DEFAULT UUID_STRING(),
    job_id STRING NOT NULL,
    alert_message STRING,
    alert_type STRING COMMENT 'INFO, WARNING, CRITICAL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
) COMMENT = 'Alert messages (templated when Cortex unavailable)';

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_flights_callsign ON FLIGHTS_RAW(callsign);
CREATE INDEX IF NOT EXISTS idx_flights_timestamp ON FLIGHTS_RAW(snapshot_ts);
CREATE INDEX IF NOT EXISTS idx_machines_id ON MACHINES_RAW(machine_id);
CREATE INDEX IF NOT EXISTS idx_machines_timestamp ON MACHINES_RAW(event_ts);
CREATE INDEX IF NOT EXISTS idx_jobs_machine ON JOBS(machine_id);
CREATE INDEX IF NOT EXISTS idx_jobs_callsign ON JOBS(inbound_flight_callsign);
