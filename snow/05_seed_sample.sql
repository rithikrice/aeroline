-- Seed sample data for AeroLine

USE DATABASE AEROLINE_DB;
USE SCHEMA PUBLIC;

-- Clear existing sample data (optional - comment out if you want to keep existing)
TRUNCATE TABLE FLIGHTS_RAW;
TRUNCATE TABLE MACHINES_RAW;
TRUNCATE TABLE JOBS;

-- Insert sample machine data (50 records across 5 machines)
INSERT INTO MACHINES_RAW (machine_id, type, air_temp, process_temp, rotational_speed, torque, tool_wear, failure_label, event_ts)
VALUES
    -- Machine M-01 (Low performance type)
    ('M-01', 'L', 298.1, 308.9, 1380, 48.5, 15, 0, DATEADD('minute', -240, CURRENT_TIMESTAMP())),
    ('M-01', 'L', 298.3, 309.1, 1375, 48.2, 18, 0, DATEADD('minute', -235, CURRENT_TIMESTAMP())),
    ('M-01', 'L', 298.5, 309.4, 1385, 49.1, 21, 0, DATEADD('minute', -230, CURRENT_TIMESTAMP())),
    ('M-01', 'L', 298.8, 309.8, 1390, 49.5, 24, 0, DATEADD('minute', -225, CURRENT_TIMESTAMP())),
    ('M-01', 'L', 299.2, 310.3, 1378, 48.8, 27, 0, DATEADD('minute', -220, CURRENT_TIMESTAMP())),
    ('M-01', 'L', 299.5, 310.7, 1382, 49.2, 30, 0, DATEADD('minute', -215, CURRENT_TIMESTAMP())),
    ('M-01', 'L', 299.8, 311.1, 1388, 49.7, 33, 0, DATEADD('minute', -210, CURRENT_TIMESTAMP())),
    ('M-01', 'L', 300.1, 311.5, 1376, 48.6, 36, 0, DATEADD('minute', -205, CURRENT_TIMESTAMP())),
    ('M-01', 'L', 300.4, 311.9, 1384, 49.3, 39, 0, DATEADD('minute', -200, CURRENT_TIMESTAMP())),
    ('M-01', 'L', 300.7, 312.3, 1379, 48.9, 42, 0, DATEADD('minute', -195, CURRENT_TIMESTAMP())),
    
    -- Machine M-02 (Medium performance type - showing degradation)
    ('M-02', 'M', 300.5, 311.8, 1450, 51.2, 125, 0, DATEADD('minute', -240, CURRENT_TIMESTAMP())),
    ('M-02', 'M', 300.8, 312.2, 1455, 51.8, 130, 0, DATEADD('minute', -235, CURRENT_TIMESTAMP())),
    ('M-02', 'M', 301.1, 312.6, 1448, 52.3, 135, 0, DATEADD('minute', -230, CURRENT_TIMESTAMP())),
    ('M-02', 'M', 301.5, 313.1, 1462, 52.9, 140, 0, DATEADD('minute', -225, CURRENT_TIMESTAMP())),
    ('M-02', 'M', 301.9, 313.6, 1458, 53.5, 145, 0, DATEADD('minute', -220, CURRENT_TIMESTAMP())),
    ('M-02', 'M', 302.3, 314.2, 1465, 54.1, 150, 1, DATEADD('minute', -215, CURRENT_TIMESTAMP())),
    ('M-02', 'M', 302.8, 314.8, 1470, 54.8, 155, 1, DATEADD('minute', -210, CURRENT_TIMESTAMP())),
    ('M-02', 'M', 303.2, 315.4, 1468, 55.4, 160, 1, DATEADD('minute', -205, CURRENT_TIMESTAMP())),
    ('M-02', 'M', 303.7, 316.0, 1475, 56.1, 165, 1, DATEADD('minute', -200, CURRENT_TIMESTAMP())),
    ('M-02', 'M', 304.2, 316.7, 1472, 56.8, 170, 1, DATEADD('minute', -195, CURRENT_TIMESTAMP())),
    
    -- Machine M-03 (High performance type)
    ('M-03', 'H', 297.8, 308.5, 1580, 45.2, 8, 0, DATEADD('minute', -240, CURRENT_TIMESTAMP())),
    ('M-03', 'H', 298.0, 308.8, 1585, 45.6, 10, 0, DATEADD('minute', -235, CURRENT_TIMESTAMP())),
    ('M-03', 'H', 298.2, 309.1, 1590, 46.0, 12, 0, DATEADD('minute', -230, CURRENT_TIMESTAMP())),
    ('M-03', 'H', 298.4, 309.4, 1588, 46.4, 14, 0, DATEADD('minute', -225, CURRENT_TIMESTAMP())),
    ('M-03', 'H', 298.6, 309.7, 1592, 46.8, 16, 0, DATEADD('minute', -220, CURRENT_TIMESTAMP())),
    ('M-03', 'H', 298.8, 310.0, 1595, 47.2, 18, 0, DATEADD('minute', -215, CURRENT_TIMESTAMP())),
    ('M-03', 'H', 299.0, 310.3, 1587, 47.6, 20, 0, DATEADD('minute', -210, CURRENT_TIMESTAMP())),
    ('M-03', 'H', 299.2, 310.6, 1591, 48.0, 22, 0, DATEADD('minute', -205, CURRENT_TIMESTAMP())),
    ('M-03', 'H', 299.4, 310.9, 1589, 48.4, 24, 0, DATEADD('minute', -200, CURRENT_TIMESTAMP())),
    ('M-03', 'H', 299.6, 311.2, 1593, 48.8, 26, 0, DATEADD('minute', -195, CURRENT_TIMESTAMP())),
    
    -- Machine M-04 (Medium type - normal operation)
    ('M-04', 'M', 299.0, 310.2, 1500, 50.5, 45, 0, DATEADD('minute', -240, CURRENT_TIMESTAMP())),
    ('M-04', 'M', 299.2, 310.5, 1505, 50.8, 48, 0, DATEADD('minute', -235, CURRENT_TIMESTAMP())),
    ('M-04', 'M', 299.4, 310.8, 1498, 51.1, 51, 0, DATEADD('minute', -230, CURRENT_TIMESTAMP())),
    ('M-04', 'M', 299.6, 311.1, 1502, 51.4, 54, 0, DATEADD('minute', -225, CURRENT_TIMESTAMP())),
    ('M-04', 'M', 299.8, 311.4, 1508, 51.7, 57, 0, DATEADD('minute', -220, CURRENT_TIMESTAMP())),
    ('M-04', 'M', 300.0, 311.7, 1495, 52.0, 60, 0, DATEADD('minute', -215, CURRENT_TIMESTAMP())),
    ('M-04', 'M', 300.2, 312.0, 1503, 52.3, 63, 0, DATEADD('minute', -210, CURRENT_TIMESTAMP())),
    ('M-04', 'M', 300.4, 312.3, 1499, 52.6, 66, 0, DATEADD('minute', -205, CURRENT_TIMESTAMP())),
    ('M-04', 'M', 300.6, 312.6, 1506, 52.9, 69, 0, DATEADD('minute', -200, CURRENT_TIMESTAMP())),
    ('M-04', 'M', 300.8, 312.9, 1501, 53.2, 72, 0, DATEADD('minute', -195, CURRENT_TIMESTAMP())),
    
    -- Machine M-05 (Low type - showing high wear)
    ('M-05', 'L', 301.0, 312.5, 1350, 55.0, 180, 0, DATEADD('minute', -240, CURRENT_TIMESTAMP())),
    ('M-05', 'L', 301.3, 312.9, 1355, 55.5, 185, 0, DATEADD('minute', -235, CURRENT_TIMESTAMP())),
    ('M-05', 'L', 301.6, 313.3, 1348, 56.0, 190, 0, DATEADD('minute', -230, CURRENT_TIMESTAMP())),
    ('M-05', 'L', 301.9, 313.7, 1352, 56.5, 195, 0, DATEADD('minute', -225, CURRENT_TIMESTAMP())),
    ('M-05', 'L', 302.2, 314.1, 1358, 57.0, 200, 1, DATEADD('minute', -220, CURRENT_TIMESTAMP())),
    ('M-05', 'L', 302.5, 314.5, 1345, 57.5, 205, 1, DATEADD('minute', -215, CURRENT_TIMESTAMP())),
    ('M-05', 'L', 302.8, 314.9, 1353, 58.0, 210, 1, DATEADD('minute', -210, CURRENT_TIMESTAMP())),
    ('M-05', 'L', 303.1, 315.3, 1349, 58.5, 215, 1, DATEADD('minute', -205, CURRENT_TIMESTAMP())),
    ('M-05', 'L', 303.4, 315.7, 1356, 59.0, 220, 1, DATEADD('minute', -200, CURRENT_TIMESTAMP())),
    ('M-05', 'L', 303.7, 316.1, 1351, 59.5, 225, 1, DATEADD('minute', -195, CURRENT_TIMESTAMP()));

-- Insert sample flight data (100 records for various flights)
INSERT INTO FLIGHTS_RAW (snapshot_ts, icao24, callsign, origin_country, time_position, last_contact, lon, lat, baro_altitude, on_ground, velocity, true_track, vertical_rate, geo_altitude, squawk, spi, position_source)
VALUES
    -- Flight AI1234 (India to USA - showing delay)
    (DATEADD('minute', -120, CURRENT_TIMESTAMP()), '39a123', 'AI1234', 'India', 1694440800, 1694440815, 77.59, 12.97, 10500, false, 205, 70, 1.2, 10600, '1234', false, 0),
    (DATEADD('minute', -115, CURRENT_TIMESTAMP()), '39a123', 'AI1234', 'India', 1694441100, 1694441115, 78.12, 13.25, 10700, false, 210, 72, 1.5, 10800, '1234', false, 0),
    (DATEADD('minute', -110, CURRENT_TIMESTAMP()), '39a123', 'AI1234', 'India', 1694441400, 1694441415, 78.65, 13.53, 10900, false, 215, 74, 1.8, 11000, '1234', false, 0),
    (DATEADD('minute', -105, CURRENT_TIMESTAMP()), '39a123', 'AI1234', 'India', 1694441700, 1694441715, 79.18, 13.81, 11100, false, 180, 76, -0.5, 11200, '1234', false, 0),
    (DATEADD('minute', -100, CURRENT_TIMESTAMP()), '39a123', 'AI1234', 'India', 1694442000, 1694442015, 79.71, 14.09, 11000, false, 175, 78, -0.8, 11100, '1234', false, 0),
    
    -- Flight LH760 (Germany to USA - on schedule)
    (DATEADD('minute', -120, CURRENT_TIMESTAMP()), '3c4b56', 'LH760', 'Germany', 1694441400, 1694441410, 8.57, 50.03, 11000, false, 240, 280, 0, 11100, '2345', false, 0),
    (DATEADD('minute', -115, CURRENT_TIMESTAMP()), '3c4b56', 'LH760', 'Germany', 1694441700, 1694441710, 7.95, 50.15, 11000, false, 245, 280, 0, 11100, '2345', false, 0),
    (DATEADD('minute', -110, CURRENT_TIMESTAMP()), '3c4b56', 'LH760', 'Germany', 1694442000, 1694442010, 7.33, 50.27, 11000, false, 250, 280, 0, 11100, '2345', false, 0),
    (DATEADD('minute', -105, CURRENT_TIMESTAMP()), '3c4b56', 'LH760', 'Germany', 1694442300, 1694442310, 6.71, 50.39, 11000, false, 248, 280, 0, 11100, '2345', false, 0),
    (DATEADD('minute', -100, CURRENT_TIMESTAMP()), '3c4b56', 'LH760', 'Germany', 1694442600, 1694442610, 6.09, 50.51, 11000, false, 252, 280, 0, 11100, '2345', false, 0),
    
    -- Flight UA850 (USA domestic - severe delay)
    (DATEADD('minute', -120, CURRENT_TIMESTAMP()), '4b1805', 'UA850', 'United States', 1694442000, 1694442015, -122.38, 37.62, 8500, false, 150, 90, -2.0, 8600, '3456', false, 0),
    (DATEADD('minute', -115, CURRENT_TIMESTAMP()), '4b1805', 'UA850', 'United States', 1694442300, 1694442315, -122.15, 37.64, 8300, false, 145, 92, -2.5, 8400, '3456', false, 0),
    (DATEADD('minute', -110, CURRENT_TIMESTAMP()), '4b1805', 'UA850', 'United States', 1694442600, 1694442615, -121.92, 37.66, 8100, false, 140, 94, -3.0, 8200, '3456', false, 0),
    (DATEADD('minute', -105, CURRENT_TIMESTAMP()), '4b1805', 'UA850', 'United States', 1694442900, 1694442915, -121.69, 37.68, 7900, false, 135, 96, -3.5, 8000, '3456', false, 0),
    (DATEADD('minute', -100, CURRENT_TIMESTAMP()), '4b1805', 'UA850', 'United States', 1694443200, 1694443215, -121.46, 37.70, 7700, false, 130, 98, -4.0, 7800, '3456', false, 0),
    
    -- Flight BA248 (UK to USA - normal)
    (DATEADD('minute', -120, CURRENT_TIMESTAMP()), '405b9a', 'BA248', 'United Kingdom', 1694442300, 1694442315, -0.46, 51.47, 10800, false, 230, 270, 0.5, 10900, '4567', false, 0),
    (DATEADD('minute', -115, CURRENT_TIMESTAMP()), '405b9a', 'BA248', 'United Kingdom', 1694442600, 1694442615, -1.08, 51.45, 10900, false, 235, 270, 0.8, 11000, '4567', false, 0),
    (DATEADD('minute', -110, CURRENT_TIMESTAMP()), '405b9a', 'BA248', 'United Kingdom', 1694442900, 1694442915, -1.70, 51.43, 11000, false, 240, 270, 1.0, 11100, '4567', false, 0),
    (DATEADD('minute', -105, CURRENT_TIMESTAMP()), '405b9a', 'BA248', 'United Kingdom', 1694443200, 1694443215, -2.32, 51.41, 11100, false, 238, 270, 0.5, 11200, '4567', false, 0),
    (DATEADD('minute', -100, CURRENT_TIMESTAMP()), '405b9a', 'BA248', 'United Kingdom', 1694443500, 1694443515, -2.94, 51.39, 11200, false, 242, 270, 0.3, 11300, '4567', false, 0),
    
    -- Flight EK201 (UAE to USA - critical delay)
    (DATEADD('minute', -120, CURRENT_TIMESTAMP()), '896542', 'EK201', 'United Arab Emirates', 1694443000, 1694443015, 55.36, 25.25, 9500, false, 120, 320, -1.5, 9600, '5678', false, 0),
    (DATEADD('minute', -115, CURRENT_TIMESTAMP()), '896542', 'EK201', 'United Arab Emirates', 1694443300, 1694443315, 55.12, 25.48, 9300, false, 115, 322, -2.0, 9400, '5678', false, 0),
    (DATEADD('minute', -110, CURRENT_TIMESTAMP()), '896542', 'EK201', 'United Arab Emirates', 1694443600, 1694443615, 54.88, 25.71, 9100, false, 110, 324, -2.5, 9200, '5678', false, 0),
    (DATEADD('minute', -105, CURRENT_TIMESTAMP()), '896542', 'EK201', 'United Arab Emirates', 1694443900, 1694443915, 54.64, 25.94, 8900, false, 105, 326, -3.0, 9000, '5678', false, 0),
    (DATEADD('minute', -100, CURRENT_TIMESTAMP()), '896542', 'EK201', 'United Arab Emirates', 1694444200, 1694444215, 54.40, 26.17, 8700, false, 100, 328, -3.5, 8800, '5678', false, 0);

-- Add more flight records to reach ~100
-- (Repeating patterns with variations for other flights)
INSERT INTO FLIGHTS_RAW (snapshot_ts, icao24, callsign, origin_country, lon, lat, baro_altitude, on_ground, velocity)
SELECT 
    DATEADD('minute', -seq.n, CURRENT_TIMESTAMP()) as snapshot_ts,
    CONCAT('abc', MOD(seq.n, 10)) as icao24,
    CONCAT('FL', LPAD(MOD(seq.n, 20), 3, '0')) as callsign,
    CASE MOD(seq.n, 5)
        WHEN 0 THEN 'United States'
        WHEN 1 THEN 'Germany'
        WHEN 2 THEN 'Japan'
        WHEN 3 THEN 'China'
        ELSE 'France'
    END as origin_country,
    -122.38 + (RANDOM() * 10 - 5) as lon,
    37.62 + (RANDOM() * 5 - 2.5) as lat,
    8000 + (RANDOM() * 4000) as baro_altitude,
    false as on_ground,
    200 + (RANDOM() * 100) as velocity
FROM (
    SELECT ROW_NUMBER() OVER (ORDER BY 1) as n 
    FROM TABLE(GENERATOR(ROWCOUNT => 75))
) seq;

-- Insert sample jobs (20 records)
INSERT INTO JOBS (job_id, machine_id, bom_item, inbound_flight_callsign, planned_start_ts, planned_end_ts)
VALUES
    ('JOB-001', 'M-01', 'PART-A-100', 'AI1234', DATEADD('hour', 2, CURRENT_TIMESTAMP()), DATEADD('hour', 6, CURRENT_TIMESTAMP())),
    ('JOB-002', 'M-02', 'PART-B-200', 'LH760', DATEADD('hour', 3, CURRENT_TIMESTAMP()), DATEADD('hour', 7, CURRENT_TIMESTAMP())),
    ('JOB-003', 'M-03', 'PART-C-300', 'UA850', DATEADD('hour', 4, CURRENT_TIMESTAMP()), DATEADD('hour', 8, CURRENT_TIMESTAMP())),
    ('JOB-004', 'M-04', 'PART-D-400', 'BA248', DATEADD('hour', 5, CURRENT_TIMESTAMP()), DATEADD('hour', 9, CURRENT_TIMESTAMP())),
    ('JOB-005', 'M-05', 'PART-E-500', 'EK201', DATEADD('hour', 6, CURRENT_TIMESTAMP()), DATEADD('hour', 10, CURRENT_TIMESTAMP())),
    ('JOB-006', 'M-01', 'PART-F-600', 'FL001', DATEADD('hour', 7, CURRENT_TIMESTAMP()), DATEADD('hour', 11, CURRENT_TIMESTAMP())),
    ('JOB-007', 'M-02', 'PART-G-700', 'FL002', DATEADD('hour', 8, CURRENT_TIMESTAMP()), DATEADD('hour', 12, CURRENT_TIMESTAMP())),
    ('JOB-008', 'M-03', 'PART-H-800', 'FL003', DATEADD('hour', 9, CURRENT_TIMESTAMP()), DATEADD('hour', 13, CURRENT_TIMESTAMP())),
    ('JOB-009', 'M-04', 'PART-I-900', 'FL004', DATEADD('hour', 10, CURRENT_TIMESTAMP()), DATEADD('hour', 14, CURRENT_TIMESTAMP())),
    ('JOB-010', 'M-05', 'PART-J-1000', 'FL005', DATEADD('hour', 11, CURRENT_TIMESTAMP()), DATEADD('hour', 15, CURRENT_TIMESTAMP())),
    ('JOB-011', 'M-01', 'PART-K-1100', 'FL006', DATEADD('hour', 12, CURRENT_TIMESTAMP()), DATEADD('hour', 16, CURRENT_TIMESTAMP())),
    ('JOB-012', 'M-02', 'PART-L-1200', 'FL007', DATEADD('hour', 13, CURRENT_TIMESTAMP()), DATEADD('hour', 17, CURRENT_TIMESTAMP())),
    ('JOB-013', 'M-03', 'PART-M-1300', 'FL008', DATEADD('hour', 14, CURRENT_TIMESTAMP()), DATEADD('hour', 18, CURRENT_TIMESTAMP())),
    ('JOB-014', 'M-04', 'PART-N-1400', 'FL009', DATEADD('hour', 15, CURRENT_TIMESTAMP()), DATEADD('hour', 19, CURRENT_TIMESTAMP())),
    ('JOB-015', 'M-05', 'PART-O-1500', 'FL010', DATEADD('hour', 16, CURRENT_TIMESTAMP()), DATEADD('hour', 20, CURRENT_TIMESTAMP())),
    ('JOB-016', 'M-01', 'PART-P-1600', 'FL011', DATEADD('hour', 17, CURRENT_TIMESTAMP()), DATEADD('hour', 21, CURRENT_TIMESTAMP())),
    ('JOB-017', 'M-02', 'PART-Q-1700', 'FL012', DATEADD('hour', 18, CURRENT_TIMESTAMP()), DATEADD('hour', 22, CURRENT_TIMESTAMP())),
    ('JOB-018', 'M-03', 'PART-R-1800', 'FL013', DATEADD('hour', 19, CURRENT_TIMESTAMP()), DATEADD('hour', 23, CURRENT_TIMESTAMP())),
    ('JOB-019', 'M-04', 'PART-S-1900', 'FL014', DATEADD('hour', 20, CURRENT_TIMESTAMP()), DATEADD('hour', 24, CURRENT_TIMESTAMP())),
    ('JOB-020', 'M-05', 'PART-T-2000', 'FL015', DATEADD('hour', 21, CURRENT_TIMESTAMP()), DATEADD('hour', 25, CURRENT_TIMESTAMP()));

-- Verify data was inserted
SELECT 'FLIGHTS_RAW' as table_name, COUNT(*) as row_count FROM FLIGHTS_RAW
UNION ALL
SELECT 'MACHINES_RAW', COUNT(*) FROM MACHINES_RAW
UNION ALL
SELECT 'JOBS', COUNT(*) FROM JOBS;
