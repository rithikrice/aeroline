-- Create warehouse, database, and schema for AeroLine

-- Create warehouse
CREATE WAREHOUSE IF NOT EXISTS AEROLINE_WH
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Warehouse for AeroLine risk orchestrator';

-- Create database
CREATE DATABASE IF NOT EXISTS AEROLINE_DB
    COMMENT = 'Database for AeroLine air-to-floor risk orchestration';

-- Use the database
USE DATABASE AEROLINE_DB;

-- Create schema
CREATE SCHEMA IF NOT EXISTS PUBLIC
    COMMENT = 'Main schema for AeroLine tables and procedures';

-- Use the schema
USE SCHEMA PUBLIC;

-- Grant permissions (adjust roles as needed)
GRANT USAGE ON WAREHOUSE AEROLINE_WH TO ROLE DEVELOPER;
GRANT ALL ON DATABASE AEROLINE_DB TO ROLE DEVELOPER;
GRANT ALL ON SCHEMA AEROLINE_DB.PUBLIC TO ROLE DEVELOPER;
