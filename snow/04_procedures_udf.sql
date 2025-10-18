-- Create Stored Procedures and UDFs for AeroLine

USE DATABASE AEROLINE_DB;
USE SCHEMA PUBLIC;

-- Python UDF for cost function calculation
CREATE OR REPLACE FUNCTION COST_FUNCTION(
    otif_value FLOAT,
    expedite_cost FLOAT,
    downtime_cost FLOAT,
    frs FLOAT,
    fls FLOAT
)
RETURNS FLOAT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.8'
HANDLER = 'calculate_roi'
AS
$$
import math

def calculate_roi(otif_value, expedite_cost, downtime_cost, frs, fls):
    """
    Calculate ROI based on costs and risk scores.
    ROI = otif_value - expedite_cost - downtime_cost - penalty(frs, fls)
    """
    # Configuration parameters
    lambda_val = 1.0
    alpha = 0.7
    beta = 0.3
    
    # Ensure scores are within bounds
    frs = max(0, min(1, frs))
    fls = max(0, min(1, fls))
    
    # Calculate weighted penalty
    penalty = lambda_val * (alpha * frs + beta * fls)
    
    # Scale penalty based on risk levels
    combined_risk = (frs + fls) / 2
    if combined_risk > 0.7:
        # Exponential penalty for high risk
        penalty *= math.exp(combined_risk - 0.7)
    
    # Scale penalty to cost magnitude (max 50% of OTIF value)
    penalty_cost = penalty * (otif_value * 0.5)
    
    # Calculate ROI
    roi = otif_value - expedite_cost - downtime_cost - penalty_cost
    
    return roi
$$;

-- Python stored procedure to prescribe actions
CREATE OR REPLACE PROCEDURE PRESCRIBE_ACTIONS()
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = '3.8'
PACKAGES = ('snowflake-snowpark-python')
HANDLER = 'prescribe_actions'
AS
$$
import snowflake.snowpark as snowpark

def prescribe_actions(session: snowpark.Session) -> str:
    """
    Update RISK_JOIN table with prescribed actions based on ROI and risk thresholds.
    """
    try:
        # Get current risk data
        risk_df = session.table("RISK_JOIN").to_pandas()
        
        if risk_df.empty:
            return "No jobs to process"
        
        updates = []
        
        for _, row in risk_df.iterrows():
            job_id = row['JOB_ID']
            frs = row['FRS']
            fls = row['FLS']
            otif_value = row['OTIF_VALUE']
            expedite_cost = row['EXPEDITE_COST']
            
            # Decision rules
            action = 'NO_ACTION'
            
            # Rule 1: High compound risk
            if frs > 0.7 and fls > 0.6:
                # Check if expedite ROI is positive
                expedite_roi = otif_value - expedite_cost * 1.5 - 1000
                if expedite_roi > 0 and expedite_cost < otif_value * 0.4:
                    action = 'EXPEDITE'
                else:
                    action = 'RESCHEDULE'
            
            # Rule 2: Critical FRS with affordable expedite
            elif frs > 0.8 and expedite_cost < otif_value * 0.25:
                action = 'EXPEDITE'
            
            # Rule 3: High FLS - pull spares
            elif fls > 0.65:
                action = 'PULL_SPARES'
            
            # Rule 4: Moderate risk with positive ROI for expedite
            elif frs > 0.5 and expedite_cost < otif_value * 0.2:
                action = 'EXPEDITE'
            
            updates.append({
                'job_id': job_id,
                'action': action
            })
        
        # Update the table
        for update in updates:
            session.sql(f"""
                UPDATE RISK_JOIN 
                SET action = '{update['action']}',
                    updated_at = CURRENT_TIMESTAMP()
                WHERE job_id = '{update['job_id']}'
            """).collect()
        
        return f"Updated {len(updates)} jobs with prescribed actions"
        
    except Exception as e:
        return f"Error: {str(e)}"
$$;

-- UDF to generate alert messages (fallback when Cortex not available)
CREATE OR REPLACE FUNCTION GENERATE_ALERT_MESSAGE(
    job_id STRING,
    frs FLOAT,
    fls FLOAT,
    action STRING,
    triggers ARRAY
)
RETURNS STRING
LANGUAGE SQL
AS
$$
    'Job ' || job_id || ': FRS=' || ROUND(frs, 2) || ', FLS=' || ROUND(fls, 2) || 
    ' → ' || action || '. Triggers: ' || 
    CASE 
        WHEN ARRAY_SIZE(triggers) > 0 THEN ARRAY_TO_STRING(triggers, ', ')
        ELSE 'Normal parameters'
    END || '.'
$$;

-- Stored procedure to summarize alerts (would use Cortex LLM if available)
CREATE OR REPLACE PROCEDURE SUMMARIZE_ALERT(job_id STRING)
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    alert_message STRING;
    frs_val FLOAT;
    fls_val FLOAT;
    action_val STRING;
BEGIN
    -- Get job details
    SELECT FRS, FLS, action
    INTO :frs_val, :fls_val, :action_val
    FROM RISK_JOIN
    WHERE job_id = :job_id;
    
    -- Generate alert message
    -- In production, this would call Cortex Complete for natural language generation
    alert_message := 'ALERT: Job ' || :job_id || ' requires immediate attention. ';
    
    IF (:frs_val > 0.8) THEN
        alert_message := alert_message || 'Critical flight delay risk detected. ';
    ELSEIF (:frs_val > 0.6) THEN
        alert_message := alert_message || 'Elevated flight delay risk. ';
    END IF;
    
    IF (:fls_val > 0.7) THEN
        alert_message := alert_message || 'High machine failure probability. ';
    ELSEIF (:fls_val > 0.5) THEN
        alert_message := alert_message || 'Moderate machine failure risk. ';
    END IF;
    
    alert_message := alert_message || 'Recommended action: ' || :action_val || '. ';
    
    IF (:action_val = 'EXPEDITE') THEN
        alert_message := alert_message || 'Contact logistics to expedite shipment immediately.';
    ELSEIF (:action_val = 'PULL_SPARES') THEN
        alert_message := alert_message || 'Prepare spare parts from inventory.';
    ELSEIF (:action_val = 'RESCHEDULE') THEN
        alert_message := alert_message || 'Reschedule production to avoid cascading delays.';
    END IF;
    
    -- Insert into alerts table
    INSERT INTO CORTEX_ALERTS (job_id, alert_message, alert_type)
    VALUES (:job_id, :alert_message, 
            CASE 
                WHEN :frs_val > 0.8 OR :fls_val > 0.7 THEN 'CRITICAL'
                WHEN :frs_val > 0.6 OR :fls_val > 0.5 THEN 'WARNING'
                ELSE 'INFO'
            END);
    
    RETURN alert_message;
END;
$$;

-- Helper function to calculate haversine distance (if not built-in)
CREATE OR REPLACE FUNCTION HAVERSINE(lat1 FLOAT, lon1 FLOAT, lat2 FLOAT, lon2 FLOAT)
RETURNS FLOAT
LANGUAGE SQL
AS
$$
    6371 * 2 * ASIN(SQRT(
        POWER(SIN(RADIANS(lat2 - lat1) / 2), 2) +
        COS(RADIANS(lat1)) * COS(RADIANS(lat2)) *
        POWER(SIN(RADIANS(lon2 - lon1) / 2), 2)
    ))
$$;
