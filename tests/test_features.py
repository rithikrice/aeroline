"""Unit tests for feature engineering functions."""

import pytest
import numpy as np
import pandas as pd
from app.features.flight_features import (
    haversine_distance,
    calculate_eta_drift,
    calculate_route_deviation,
    calculate_speed_zscore,
    calculate_frs,
    compute_flight_features
)
from app.features.maintenance_features import (
    calculate_ewma,
    calculate_zscore_features,
    calculate_fls_heuristic,
    compute_maintenance_features
)


class TestFlightFeatures:
    """Test flight feature engineering functions."""
    
    def test_haversine_distance(self):
        """Test haversine distance calculation."""
        # Test known distance: San Francisco to Los Angeles (~559 km)
        dist = haversine_distance(37.7749, -122.4194, 34.0522, -118.2437)
        assert dist == pytest.approx(559, rel=0.1)  # Within 10%
        
        # Test zero distance
        dist_zero = haversine_distance(0, 0, 0, 0)
        assert dist_zero == pytest.approx(0, abs=0.001)
        
        # Test antipodal points (opposite sides of Earth)
        dist_antipodal = haversine_distance(0, 0, 0, 180)
        assert dist_antipodal == pytest.approx(20015, rel=0.1)  # Half Earth circumference
    
    def test_calculate_eta_drift(self):
        """Test ETA drift calculation."""
        # Test on-time scenario
        drift = calculate_eta_drift(
            current_lat=37.0,
            current_lon=-122.0,
            dest_lat=37.6213,
            dest_lon=-122.3790,
            current_velocity=250,  # m/s
            scheduled_arrival_time=1000000 + 300,  # 5 minutes from now
            current_time=1000000
        )
        
        # Should be close to on-time (small drift)
        assert abs(drift) < 60  # Less than 60 minutes drift
        
        # Test delayed scenario (very slow speed)
        drift_delayed = calculate_eta_drift(
            current_lat=35.0,
            current_lon=-120.0,
            dest_lat=37.6213,
            dest_lon=-122.3790,
            current_velocity=50,  # Very slow
            scheduled_arrival_time=1000000 + 3600,  # 1 hour from now
            current_time=1000000
        )
        
        # Should show significant delay
        assert drift_delayed > 60  # More than 60 minutes late
    
    def test_calculate_route_deviation(self):
        """Test route deviation calculation."""
        # Test on-route scenario (point on direct path)
        deviation = calculate_route_deviation(
            current_lat=36.0,
            current_lon=-121.0,
            origin_lat=35.0,
            origin_lon=-120.0,
            dest_lat=37.0,
            dest_lon=-122.0
        )
        
        # Should have some deviation (simplified calculation)
        assert deviation >= 0
        
        # Test off-route scenario
        deviation_off = calculate_route_deviation(
            current_lat=38.0,  # Way off north
            current_lon=-125.0,  # Way off west
            origin_lat=35.0,
            origin_lon=-120.0,
            dest_lat=37.0,
            dest_lon=-122.0
        )
        
        # Should have larger deviation
        assert deviation_off > deviation
    
    def test_calculate_speed_zscore(self):
        """Test speed z-score calculation."""
        # Test with normal distribution
        velocities = [200, 210, 205, 195, 200, 205, 210, 195, 200, 205]
        current = 205
        
        z_score = calculate_speed_zscore(current, velocities)
        
        # Should be close to 0 (within 1 std dev)
        assert abs(z_score) < 1
        
        # Test with outlier
        z_score_outlier = calculate_speed_zscore(250, velocities)
        assert z_score_outlier > 2  # More than 2 std devs
        
        # Test with insufficient data
        z_score_insufficient = calculate_speed_zscore(200, [200])
        assert z_score_insufficient == 0
    
    def test_calculate_frs(self):
        """Test FRS calculation."""
        # Test normal risk
        frs = calculate_frs(
            eta_drift_min=10,  # 10 minutes late
            route_dev_km=20,   # 20 km off route
            speed_zscore=0.5   # Half std dev
        )
        
        # Should be moderate risk
        assert 0.3 < frs < 0.7
        
        # Test high risk
        frs_high = calculate_frs(
            eta_drift_min=90,   # 90 minutes late
            route_dev_km=150,  # 150 km off route
            speed_zscore=3     # 3 std devs
        )
        
        # Should be high risk
        assert frs_high > 0.7
        
        # Test low risk
        frs_low = calculate_frs(
            eta_drift_min=0,
            route_dev_km=0,
            speed_zscore=0
        )
        
        # Should be low risk
        assert frs_low < 0.5
    
    def test_compute_flight_features(self):
        """Test complete flight feature computation."""
        # Create sample flight data
        df = pd.DataFrame({
            "snapshot_ts": pd.date_range("2024-01-01", periods=3, freq="5min"),
            "icao24": ["abc123"] * 3,
            "callsign": ["TEST01"] * 3,
            "lat": [35.0, 36.0, 37.0],
            "lon": [-120.0, -121.0, -122.0],
            "velocity": [200, 210, 205]
        })
        
        # Compute features
        result = compute_flight_features(df)
        
        # Check that all feature columns are added
        assert "eta_drift_min" in result.columns
        assert "route_dev_km" in result.columns
        assert "speed_zscore" in result.columns
        assert "FRS" in result.columns
        
        # Check FRS is within bounds
        assert all(0 <= frs <= 1 for frs in result["FRS"])


class TestMaintenanceFeatures:
    """Test maintenance feature engineering functions."""
    
    def test_calculate_ewma(self):
        """Test EWMA calculation."""
        values = [10, 12, 11, 13, 12]
        ewma = calculate_ewma(values, alpha=0.3)
        
        # Manual calculation:
        # ewma = 10
        # ewma = 0.3*12 + 0.7*10 = 10.6
        # ewma = 0.3*11 + 0.7*10.6 = 10.72
        # ewma = 0.3*13 + 0.7*10.72 = 11.404
        # ewma = 0.3*12 + 0.7*11.404 = 11.583
        
        assert ewma == pytest.approx(11.583, rel=0.01)
        
        # Test empty list
        ewma_empty = calculate_ewma([])
        assert ewma_empty == 0
        
        # Test single value
        ewma_single = calculate_ewma([5.0])
        assert ewma_single == 5.0
    
    def test_calculate_zscore_features(self):
        """Test z-score feature calculation."""
        df = pd.DataFrame({
            "temp": [298, 300, 302, 299, 301],
            "speed": [1400, 1450, 1425, 1475, 1425]
        })
        
        result = calculate_zscore_features(df, ["temp", "speed"])
        
        # Check z-score columns are added
        assert "temp_zscore" in result.columns
        assert "speed_zscore" in result.columns
        
        # Check z-scores have mean ~0 and std ~1
        assert abs(result["temp_zscore"].mean()) < 0.1
        assert abs(result["speed_zscore"].std() - 1) < 0.1
    
    def test_calculate_fls_heuristic(self):
        """Test FLS heuristic calculation."""
        # Test normal conditions
        fls = calculate_fls_heuristic(
            temp_deviation=0.5,
            tool_wear=50,
            speed_variance=20,
            torque_zscore=0.3
        )
        
        # Should be moderate risk
        assert 0.3 < fls < 0.7
        
        # Test high risk conditions
        fls_high = calculate_fls_heuristic(
            temp_deviation=3,
            tool_wear=200,
            speed_variance=100,
            torque_zscore=2.5
        )
        
        # Should be high risk
        assert fls_high > 0.6
        
        # Test low risk conditions
        fls_low = calculate_fls_heuristic(
            temp_deviation=0,
            tool_wear=10,
            speed_variance=5,
            torque_zscore=0
        )
        
        # Should be low risk
        assert fls_low < 0.5
    
    def test_compute_maintenance_features(self):
        """Test complete maintenance feature computation."""
        # Create sample machine data
        df = pd.DataFrame({
            "machine_id": ["M-01"] * 5,
            "event_ts": pd.date_range("2024-01-01", periods=5, freq="5min"),
            "air_temp": [298, 299, 300, 301, 302],
            "process_temp": [309, 310, 311, 312, 313],
            "rotational_speed": [1400, 1410, 1405, 1415, 1408],
            "torque": [48, 49, 50, 51, 52],
            "tool_wear": [10, 15, 20, 25, 30],
            "failure_label": [0, 0, 0, 0, 1]
        })
        
        # Compute features
        result = compute_maintenance_features(df, model=None)
        
        # Check that feature columns are added
        assert "air_temp_zscore" in result.columns
        assert "FLS" in result.columns
        
        # Check FLS is within bounds
        assert all(0 <= fls <= 1 for fls in result["FLS"])
        
        # Later values should have higher FLS (increasing wear and temp)
        assert result["FLS"].iloc[-1] >= result["FLS"].iloc[0]
    
    def test_features_with_missing_data(self):
        """Test feature computation with missing data."""
        # Create data with NaN values
        df = pd.DataFrame({
            "machine_id": ["M-01", "M-02"],
            "event_ts": pd.date_range("2024-01-01", periods=2, freq="5min"),
            "air_temp": [298, np.nan],
            "process_temp": [309, 310],
            "rotational_speed": [np.nan, 1400],
            "torque": [48, 49],
            "tool_wear": [10, 15],
            "failure_label": [0, 0]
        })
        
        # Should handle NaN gracefully
        result = compute_maintenance_features(df, model=None)
        
        # Check that FLS is still computed
        assert "FLS" in result.columns
        assert not result["FLS"].isna().all()  # At least some valid values
