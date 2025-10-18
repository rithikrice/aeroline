-- Create Dynamic Tables for AeroLine

USE DATABASE AEROLINE_DB;
USE SCHEMA PUBLIC;

-- Dynamic table for flight features
CREATE OR REPLACE DYNAMIC TABLE DT_FLIGHT_FEATS
    TARGET_LAG = '15 minutes'
    WAREHOUSE = AEROLINE_WH
    AS
    SELECT 
        snapshot_ts,
        icao24,
        callsign,
        lat,
        lon,
        -- Calculate ETA drift (simplified - assumes destination at SFO)
        CASE 
            WHEN velocity > 0 THEN 
                (HAVERSINE(lat, lon, 37.6213, -122.3790) * 1000 / velocity - 7200) / 60
            ELSE 0
        END AS eta_drift_min,
        -- Calculate route deviation (simplified)
        ABS(HAVERSINE(lat, lon, 37.6213, -122.3790) - 
            HAVERSINE(lat - 5, lon - 5, 37.6213, -122.3790)) AS route_dev_km,
        -- Calculate speed z-score
        CASE 
            WHEN velocity IS NOT NULL THEN
                (velocity - AVG(velocity) OVER (PARTITION BY callsign)) / 
                NULLIF(STDDEV(velocity) OVER (PARTITION BY callsign), 0)
            ELSE 0
        END AS speed_zscore,
        -- Calculate FRS using sigmoid of weighted features
        1 / (1 + EXP(-(
            0.6 * LEAST(GREATEST(
                CASE WHEN velocity > 0 THEN 
                    (HAVERSINE(lat, lon, 37.6213, -122.3790) * 1000 / velocity - 7200) / 3600
                ELSE 0 END, -1), 1) +
            0.3 * LEAST(ABS(HAVERSINE(lat, lon, 37.6213, -122.3790) - 
                HAVERSINE(lat - 5, lon - 5, 37.6213, -122.3790)) / 100, 1) +
            0.1 * LEAST(GREATEST(
                CASE WHEN velocity IS NOT NULL THEN
                    ABS((velocity - AVG(velocity) OVER (PARTITION BY callsign)) / 
                    NULLIF(STDDEV(velocity) OVER (PARTITION BY callsign), 0)) / 3
                ELSE 0 END, -1), 1)
        ))) AS FRS,
        CURRENT_TIMESTAMP() AS computed_at
    FROM FLIGHTS_RAW
    WHERE snapshot_ts >= DATEADD(hour, -24, CURRENT_TIMESTAMP());

-- Dynamic table for maintenance features
CREATE OR REPLACE DYNAMIC TABLE DT_MAINT_FEATS
    TARGET_LAG = '15 minutes'
    WAREHOUSE = AEROLINE_WH
    AS
    SELECT 
        event_ts,
        machine_id,
        -- Z-scores for sensor readings
        (air_temp - AVG(air_temp) OVER w) / NULLIF(STDDEV(air_temp) OVER w, 0) AS air_temp_zscore,
        (process_temp - AVG(process_temp) OVER w) / NULLIF(STDDEV(process_temp) OVER w, 0) AS process_temp_zscore,
        (rotational_speed - AVG(rotational_speed) OVER w) / NULLIF(STDDEV(rotational_speed) OVER w, 0) AS rotational_speed_zscore,
        (torque - AVG(torque) OVER w) / NULLIF(STDDEV(torque) OVER w, 0) AS torque_zscore,
        tool_wear / 250.0 AS tool_wear_normalized,
        -- Combined temperature deviation
        ((air_temp - AVG(air_temp) OVER w) / NULLIF(STDDEV(air_temp) OVER w, 0) +
         (process_temp - AVG(process_temp) OVER w) / NULLIF(STDDEV(process_temp) OVER w, 0)) / 2 AS temp_deviation,
        -- Speed variance
        VARIANCE(rotational_speed) OVER w AS speed_variance,
        -- Calculate FLS using heuristic sigmoid
        1 / (1 + EXP(-(
            0.4 * LEAST(GREATEST(
                ((air_temp - AVG(air_temp) OVER w) / NULLIF(STDDEV(air_temp) OVER w, 0) +
                 (process_temp - AVG(process_temp) OVER w) / NULLIF(STDDEV(process_temp) OVER w, 0)) / 6, -1), 1) +
            0.3 * LEAST(tool_wear / 250.0, 1) +
            0.2 * LEAST(VARIANCE(rotational_speed) OVER w / 100, 1) +
            0.1 * LEAST(GREATEST(
                (torque - AVG(torque) OVER w) / NULLIF(STDDEV(torque) OVER w, 0) / 3, -1), 1)
        ))) AS FLS,
        CURRENT_TIMESTAMP() AS computed_at
    FROM MACHINES_RAW
    WHERE event_ts >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
    WINDOW w AS (PARTITION BY machine_id ORDER BY event_ts ROWS BETWEEN 9 PRECEDING AND CURRENT ROW);

-- Dynamic table for risk join
CREATE OR REPLACE DYNAMIC TABLE DT_RISK_JOIN
    TARGET_LAG = '15 minutes'
    WAREHOUSE = AEROLINE_WH
    AS
    SELECT 
        j.job_id,
        j.machine_id,
        j.inbound_flight_callsign AS callsign,
        j.bom_item,
        j.planned_start_ts,
        j.planned_end_ts,
        COALESCE(f.FRS, 0.5) AS FRS,
        COALESCE(m.FLS, 0.5) AS FLS,
        -- Cost parameters (could be job-specific in production)
        10000 AS otif_value,
        3000 AS expedite_cost,
        -- Downtime cost based on estimated hours
        1500 * GREATEST(2 * (1 + COALESCE(f.FRS, 0.5) * 2) * 
                        GREATEST(1 + COALESCE(m.FLS, 0.5) * 1.5, 1), 2) AS downtime_cost,
        -- Calculate ROI (simplified version)
        10000 - 3000 - 1500 * 2 - 
        (0.7 * COALESCE(f.FRS, 0.5) + 0.3 * COALESCE(m.FLS, 0.5)) * 5000 AS roi,
        -- Determine action based on rules
        CASE 
            WHEN COALESCE(f.FRS, 0.5) > 0.7 AND COALESCE(m.FLS, 0.5) > 0.6 THEN 'RESCHEDULE'
            WHEN COALESCE(f.FRS, 0.5) > 0.8 AND 3000 < 10000 * 0.25 THEN 'EXPEDITE'
            WHEN COALESCE(m.FLS, 0.5) > 0.65 THEN 'PULL_SPARES'
            ELSE 'NO_ACTION'
        END AS action,
        -- Create explanation JSON
        OBJECT_CONSTRUCT(
            'frs', COALESCE(f.FRS, 0.5),
            'fls', COALESCE(m.FLS, 0.5),
            'risk_level', 
                CASE 
                    WHEN (COALESCE(f.FRS, 0.5) + COALESCE(m.FLS, 0.5)) / 2 > 0.7 THEN 'CRITICAL'
                    WHEN (COALESCE(f.FRS, 0.5) + COALESCE(m.FLS, 0.5)) / 2 > 0.5 THEN 'HIGH'
                    WHEN (COALESCE(f.FRS, 0.5) + COALESCE(m.FLS, 0.5)) / 2 > 0.3 THEN 'MEDIUM'
                    ELSE 'LOW'
                END,
            'triggers', 
                ARRAY_CONSTRUCT_COMPACT(
                    CASE WHEN COALESCE(f.FRS, 0.5) > 0.7 THEN 'High FRS' END,
                    CASE WHEN COALESCE(m.FLS, 0.5) > 0.6 THEN 'High FLS' END
                )
        ) AS explain_json,
        CURRENT_TIMESTAMP() AS updated_at
    FROM JOBS j
    LEFT JOIN (
        SELECT 
            callsign, 
            FRS,
            ROW_NUMBER() OVER (PARTITION BY callsign ORDER BY snapshot_ts DESC) AS rn
        FROM DT_FLIGHT_FEATS
    ) f ON j.inbound_flight_callsign = f.callsign AND f.rn = 1
    LEFT JOIN (
        SELECT 
            machine_id, 
            FLS,
            ROW_NUMBER() OVER (PARTITION BY machine_id ORDER BY event_ts DESC) AS rn
        FROM DT_MAINT_FEATS
    ) m ON j.machine_id = m.machine_id AND m.rn = 1;
