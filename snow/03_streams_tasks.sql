-- Create Streams and Tasks for AeroLine

USE DATABASE AEROLINE_DB;
USE SCHEMA PUBLIC;

-- Create streams on raw data tables
CREATE OR REPLACE STREAM FLIGHTS_RAW_STREAM 
    ON TABLE FLIGHTS_RAW
    APPEND_ONLY = TRUE
    COMMENT = 'Stream to track new flight data insertions';

CREATE OR REPLACE STREAM MACHINES_RAW_STREAM 
    ON TABLE MACHINES_RAW
    APPEND_ONLY = TRUE
    COMMENT = 'Stream to track new machine data insertions';

-- Task to refresh flight features when new data arrives
CREATE OR REPLACE TASK REFRESH_FLIGHT_FEATURES_TASK
    WAREHOUSE = AEROLINE_WH
    SCHEDULE = '15 MINUTE'
    COMMENT = 'Refresh flight features every 15 minutes'
AS
    -- Refresh the dynamic table
    ALTER DYNAMIC TABLE DT_FLIGHT_FEATS REFRESH;

-- Task to refresh maintenance features when new data arrives
CREATE OR REPLACE TASK REFRESH_MAINT_FEATURES_TASK
    WAREHOUSE = AEROLINE_WH
    SCHEDULE = '15 MINUTE'
    COMMENT = 'Refresh maintenance features every 15 minutes'
AS
    -- Refresh the dynamic table
    ALTER DYNAMIC TABLE DT_MAINT_FEATS REFRESH;

-- Task to refresh risk join and generate prescriptions
CREATE OR REPLACE TASK REFRESH_RISK_JOIN_TASK
    WAREHOUSE = AEROLINE_WH
    SCHEDULE = '15 MINUTE'
    COMMENT = 'Refresh risk join and prescriptions every 15 minutes'
AS
BEGIN
    -- Refresh the risk join dynamic table
    ALTER DYNAMIC TABLE DT_RISK_JOIN REFRESH;
    
    -- Call prescription procedure if it exists
    BEGIN
        CALL PRESCRIBE_ACTIONS();
    EXCEPTION
        WHEN OTHER THEN
            -- Procedure might not exist yet, continue
            NULL;
    END;
    
    -- Generate alerts for critical risks
    INSERT INTO CORTEX_ALERTS (job_id, alert_message, alert_type)
    SELECT 
        job_id,
        'Job ' || job_id || ': FRS=' || ROUND(FRS, 2) || ', FLS=' || ROUND(FLS, 2) || 
        ' → ' || action || '. Triggers: ' || 
        CASE 
            WHEN FRS > 0.7 AND FLS > 0.6 THEN 'High compound risk'
            WHEN FRS > 0.8 THEN 'Critical FRS'
            WHEN FLS > 0.65 THEN 'Critical FLS'
            ELSE 'Risk thresholds exceeded'
        END AS alert_message,
        CASE 
            WHEN FRS > 0.8 OR FLS > 0.7 THEN 'CRITICAL'
            WHEN FRS > 0.7 OR FLS > 0.6 THEN 'WARNING'
            ELSE 'INFO'
        END AS alert_type
    FROM DT_RISK_JOIN
    WHERE action != 'NO_ACTION'
    AND job_id NOT IN (
        SELECT job_id 
        FROM CORTEX_ALERTS 
        WHERE created_at >= DATEADD(hour, -1, CURRENT_TIMESTAMP())
    );
END;

-- Task to clean up old data (runs daily)
CREATE OR REPLACE TASK CLEANUP_OLD_DATA_TASK
    WAREHOUSE = AEROLINE_WH
    SCHEDULE = 'USING CRON 0 2 * * * America/Los_Angeles'
    COMMENT = 'Clean up data older than 30 days'
AS
BEGIN
    -- Delete old flight data
    DELETE FROM FLIGHTS_RAW 
    WHERE snapshot_ts < DATEADD(day, -30, CURRENT_TIMESTAMP());
    
    -- Delete old machine data
    DELETE FROM MACHINES_RAW 
    WHERE event_ts < DATEADD(day, -30, CURRENT_TIMESTAMP());
    
    -- Delete old alerts
    DELETE FROM CORTEX_ALERTS 
    WHERE created_at < DATEADD(day, -7, CURRENT_TIMESTAMP());
    
    -- Delete old feature data
    DELETE FROM FLIGHT_FEATS 
    WHERE computed_at < DATEADD(day, -7, CURRENT_TIMESTAMP());
    
    DELETE FROM MAINT_FEATS 
    WHERE computed_at < DATEADD(day, -7, CURRENT_TIMESTAMP());
END;

-- Create a task dependency chain
ALTER TASK REFRESH_MAINT_FEATURES_TASK 
    ADD AFTER REFRESH_FLIGHT_FEATURES_TASK;

ALTER TASK REFRESH_RISK_JOIN_TASK 
    ADD AFTER REFRESH_MAINT_FEATURES_TASK;

-- Enable tasks (comment out if you want to enable manually)
ALTER TASK REFRESH_FLIGHT_FEATURES_TASK RESUME;
ALTER TASK REFRESH_MAINT_FEATURES_TASK RESUME;
ALTER TASK REFRESH_RISK_JOIN_TASK RESUME;
ALTER TASK CLEANUP_OLD_DATA_TASK RESUME;
