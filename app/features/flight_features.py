"""Flight feature engineering for FRS (Flight Risk Score)."""

import math
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth.
    
    Args:
        lat1, lon1: Latitude and longitude of first point
        lat2, lon2: Latitude and longitude of second point
        
    Returns:
        Distance in kilometers
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def calculate_eta_drift(
    current_lat: float,
    current_lon: float,
    dest_lat: float,
    dest_lon: float,
    current_velocity: float,
    scheduled_arrival_time: float,
    current_time: float
) -> float:
    """
    Calculate ETA drift in minutes.
    
    Args:
        current_lat, current_lon: Current position
        dest_lat, dest_lon: Destination position
        current_velocity: Current speed in m/s
        scheduled_arrival_time: Scheduled arrival timestamp
        current_time: Current timestamp
        
    Returns:
        ETA drift in minutes (positive = late, negative = early)
    """
    # Calculate remaining distance
    remaining_distance_km = haversine_distance(
        current_lat, current_lon, dest_lat, dest_lon
    )
    
    # Convert to meters
    remaining_distance_m = remaining_distance_km * 1000
    
    # Calculate ETA based on current velocity (handle zero velocity)
    if current_velocity > 0:
        eta_seconds = remaining_distance_m / current_velocity
    else:
        # Use default cruise speed if velocity is zero
        eta_seconds = remaining_distance_m / 250  # 250 m/s default
    
    # Calculate actual arrival time
    actual_arrival_time = current_time + eta_seconds
    
    # Calculate drift in minutes
    drift_seconds = actual_arrival_time - scheduled_arrival_time
    drift_minutes = drift_seconds / 60
    
    return drift_minutes


def calculate_route_deviation(
    current_lat: float,
    current_lon: float,
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float
) -> float:
    """
    Calculate deviation from great-circle route in kilometers.
    
    Args:
        current_lat, current_lon: Current position
        origin_lat, origin_lon: Origin position
        dest_lat, dest_lon: Destination position
        
    Returns:
        Route deviation in kilometers
    """
    # For simplicity, calculate perpendicular distance to great circle
    # This is a simplified approximation
    
    # Distance from origin to current
    dist_origin_current = haversine_distance(
        origin_lat, origin_lon, current_lat, current_lon
    )
    
    # Distance from current to destination
    dist_current_dest = haversine_distance(
        current_lat, current_lon, dest_lat, dest_lon
    )
    
    # Distance from origin to destination
    dist_origin_dest = haversine_distance(
        origin_lat, origin_lon, dest_lat, dest_lon
    )
    
    # Use triangle inequality to estimate deviation
    # If on perfect route, dist_origin_current + dist_current_dest = dist_origin_dest
    deviation = abs(
        (dist_origin_current + dist_current_dest) - dist_origin_dest
    )
    
    return deviation


def calculate_speed_zscore(
    velocity: float,
    route_velocities: List[float]
) -> float:
    """
    Calculate z-score of current velocity relative to route average.
    
    Args:
        velocity: Current velocity in m/s
        route_velocities: Historical velocities for this route
        
    Returns:
        Z-score of velocity
    """
    if not route_velocities or len(route_velocities) < 2:
        # Not enough data, return 0 (normal)
        return 0.0
    
    mean_velocity = np.mean(route_velocities)
    std_velocity = np.std(route_velocities)
    
    if std_velocity == 0:
        return 0.0
    
    z_score = (velocity - mean_velocity) / std_velocity
    return z_score


def sigmoid(x: float) -> float:
    """Sigmoid activation function."""
    return 1 / (1 + math.exp(-x))


def calculate_frs(
    eta_drift_min: float,
    route_dev_km: float,
    speed_zscore: float,
    eta_weight: float = 0.6,
    route_weight: float = 0.3,
    speed_weight: float = 0.1
) -> float:
    """
    Calculate Flight Risk Score (FRS).
    
    Args:
        eta_drift_min: ETA drift in minutes
        route_dev_km: Route deviation in kilometers
        speed_zscore: Speed z-score
        eta_weight: Weight for ETA drift (default 0.6)
        route_weight: Weight for route deviation (default 0.3)
        speed_weight: Weight for speed z-score (default 0.1)
        
    Returns:
        FRS score between 0 and 1
    """
    # Normalize features
    # ETA drift: normalize to [-1, 1] range (cap at ±60 minutes)
    eta_norm = max(-1, min(1, eta_drift_min / 60))
    
    # Route deviation: normalize to [0, 1] range (cap at 100 km)
    route_norm = min(1, route_dev_km / 100)
    
    # Speed z-score: already normalized, cap at ±3
    speed_norm = max(-1, min(1, speed_zscore / 3))
    
    # Weighted sum
    weighted_sum = (
        eta_weight * abs(eta_norm) +
        route_weight * route_norm +
        speed_weight * abs(speed_norm)
    )
    
    # Apply sigmoid to get score between 0 and 1
    # Multiply by 2 and subtract 1 to center around 0.5
    frs = sigmoid(2 * weighted_sum - 1)
    
    return frs


def compute_flight_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute flight features for a DataFrame of flight data.
    
    Args:
        df: DataFrame with flight data
        
    Returns:
        DataFrame with added feature columns
    """
    # Add stub destination coordinates (normally would come from flight plan)
    # For demo, assume flights heading to major hubs
    df["dest_lat"] = 37.6213  # SFO
    df["dest_lon"] = -122.3790
    
    # Add stub origin coordinates
    df["origin_lat"] = df["lat"] - 5  # Assume started 5 degrees south
    df["origin_lon"] = df["lon"] - 5  # Assume started 5 degrees west
    
    # Add stub scheduled arrival time (2 hours from snapshot)
    df["scheduled_arrival"] = df["snapshot_ts"] + pd.Timedelta(hours=2)
    
    # Calculate ETA drift
    df["eta_drift_min"] = df.apply(
        lambda row: calculate_eta_drift(
            row["lat"], row["lon"],
            row["dest_lat"], row["dest_lon"],
            row["velocity"] if pd.notna(row["velocity"]) else 250,
            row["scheduled_arrival"].timestamp(),
            row["snapshot_ts"].timestamp()
        ),
        axis=1
    )
    
    # Calculate route deviation
    df["route_dev_km"] = df.apply(
        lambda row: calculate_route_deviation(
            row["lat"], row["lon"],
            row["origin_lat"], row["origin_lon"],
            row["dest_lat"], row["dest_lon"]
        ),
        axis=1
    )
    
    # Calculate speed z-score (using group statistics for demo)
    df["speed_zscore"] = 0.0
    if "velocity" in df.columns and not df["velocity"].isna().all():
        mean_velocity = df["velocity"].mean()
        std_velocity = df["velocity"].std()
        if std_velocity > 0:
            df["speed_zscore"] = (df["velocity"] - mean_velocity) / std_velocity
    
    # Calculate FRS
    df["FRS"] = df.apply(
        lambda row: calculate_frs(
            row["eta_drift_min"],
            row["route_dev_km"],
            row["speed_zscore"]
        ),
        axis=1
    )
    
    return df
