"""Maintenance feature engineering for FLS (Failure Likelihood Score)."""

import math
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from scipy import stats


def calculate_ewma(values: List[float], alpha: float = 0.3) -> float:
    """
    Calculate Exponentially Weighted Moving Average.
    
    Args:
        values: List of values (most recent last)
        alpha: Smoothing factor (0 < alpha <= 1)
        
    Returns:
        EWMA value
    """
    if not values:
        return 0.0
    
    ewma = values[0]
    for value in values[1:]:
        ewma = alpha * value + (1 - alpha) * ewma
    
    return ewma


def calculate_zscore_features(
    df: pd.DataFrame,
    columns: List[str]
) -> pd.DataFrame:
    """
    Calculate z-scores for specified columns.
    
    Args:
        df: DataFrame with machine data
        columns: Columns to calculate z-scores for
        
    Returns:
        DataFrame with z-score columns added
    """
    for col in columns:
        if col in df.columns:
            mean_val = df[col].mean()
            std_val = df[col].std()
            
            if std_val > 0:
                df[f"{col}_zscore"] = (df[col] - mean_val) / std_val
            else:
                df[f"{col}_zscore"] = 0.0
    
    return df


def calculate_rolling_stats(
    df: pd.DataFrame,
    columns: List[str],
    window: int = 10
) -> pd.DataFrame:
    """
    Calculate rolling statistics for specified columns.
    
    Args:
        df: DataFrame with machine data
        columns: Columns to calculate rolling stats for
        window: Rolling window size
        
    Returns:
        DataFrame with rolling stat columns added
    """
    # Sort by machine_id and event_ts to ensure proper rolling
    df = df.sort_values(["machine_id", "event_ts"])
    
    for col in columns:
        if col in df.columns:
            # Rolling mean
            df[f"{col}_rolling_mean"] = df.groupby("machine_id")[col].transform(
                lambda x: x.rolling(window, min_periods=1).mean()
            )
            
            # Rolling std
            df[f"{col}_rolling_std"] = df.groupby("machine_id")[col].transform(
                lambda x: x.rolling(window, min_periods=1).std()
            )
            
            # EWMA
            df[f"{col}_ewma"] = df.groupby("machine_id")[col].transform(
                lambda x: x.ewm(alpha=0.3, adjust=False).mean()
            )
    
    return df


def sigmoid(x: float) -> float:
    """Sigmoid activation function."""
    return 1 / (1 + math.exp(-x))


def calculate_fls_heuristic(
    temp_deviation: float,
    tool_wear: float,
    speed_variance: float,
    torque_zscore: float,
    temp_weight: float = 0.4,
    wear_weight: float = 0.3,
    speed_weight: float = 0.2,
    torque_weight: float = 0.1
) -> float:
    """
    Calculate Failure Likelihood Score using heuristic approach.
    
    Args:
        temp_deviation: Temperature deviation (air + process temp z-scores)
        tool_wear: Tool wear value (normalized)
        speed_variance: Rotational speed variance
        torque_zscore: Torque z-score
        temp_weight: Weight for temperature deviation
        wear_weight: Weight for tool wear
        speed_weight: Weight for speed variance
        torque_weight: Weight for torque
        
    Returns:
        FLS score between 0 and 1
    """
    # Normalize features
    # Temperature deviation: already in z-score, cap at ±3
    temp_norm = max(-1, min(1, temp_deviation / 3))
    
    # Tool wear: normalize to [0, 1] range (assume max wear is 250)
    wear_norm = min(1, tool_wear / 250)
    
    # Speed variance: normalize (cap at 100)
    speed_norm = min(1, speed_variance / 100)
    
    # Torque z-score: cap at ±3
    torque_norm = max(-1, min(1, torque_zscore / 3))
    
    # Weighted sum
    weighted_sum = (
        temp_weight * abs(temp_norm) +
        wear_weight * wear_norm +
        speed_weight * speed_norm +
        torque_weight * abs(torque_norm)
    )
    
    # Apply sigmoid to get score between 0 and 1
    fls = sigmoid(2 * weighted_sum - 0.5)
    
    return fls


def train_fls_model(df: pd.DataFrame) -> Optional[object]:
    """
    Train FLS model using available data.
    
    Args:
        df: DataFrame with machine data and failure labels
        
    Returns:
        Trained model or None if training fails
    """
    try:
        # Try to use XGBoost
        import xgboost as xgb
        
        # Prepare features
        feature_cols = [
            "air_temp", "process_temp", "rotational_speed",
            "torque", "tool_wear"
        ]
        
        # Add engineered features
        df = calculate_zscore_features(df, feature_cols)
        df = calculate_rolling_stats(df, feature_cols, window=5)
        
        # Select all feature columns
        all_features = []
        for col in feature_cols:
            all_features.extend([
                col,
                f"{col}_zscore",
                f"{col}_rolling_mean",
                f"{col}_rolling_std",
                f"{col}_ewma"
            ])
        
        # Filter to existing columns
        X_cols = [col for col in all_features if col in df.columns]
        
        if not X_cols or "failure_label" not in df.columns:
            return None
        
        X = df[X_cols].fillna(0)
        y = df["failure_label"]
        
        # Train XGBoost model
        model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            objective="binary:logistic",
            random_state=42
        )
        
        model.fit(X, y)
        return model
        
    except ImportError:
        # XGBoost not available, try scikit-learn
        try:
            from sklearn.ensemble import RandomForestClassifier
            
            # Similar feature preparation as above
            feature_cols = [
                "air_temp", "process_temp", "rotational_speed",
                "torque", "tool_wear"
            ]
            
            df = calculate_zscore_features(df, feature_cols)
            
            X_cols = [col for col in df.columns if col in feature_cols or "_zscore" in col]
            X_cols = [col for col in X_cols if col in df.columns]
            
            if not X_cols or "failure_label" not in df.columns:
                return None
            
            X = df[X_cols].fillna(0)
            y = df["failure_label"]
            
            # Train Random Forest model
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=5,
                random_state=42
            )
            
            model.fit(X, y)
            return model
            
        except ImportError:
            # No ML libraries available
            return None


def compute_maintenance_features(df: pd.DataFrame, model: Optional[object] = None) -> pd.DataFrame:
    """
    Compute maintenance features for a DataFrame of machine data.
    
    Args:
        df: DataFrame with machine data
        model: Optional trained model for FLS prediction
        
    Returns:
        DataFrame with added feature columns and FLS
    """
    # Calculate z-scores
    feature_cols = ["air_temp", "process_temp", "rotational_speed", "torque", "tool_wear"]
    df = calculate_zscore_features(df, feature_cols)
    
    # Calculate rolling statistics
    df = calculate_rolling_stats(df, feature_cols, window=10)
    
    # Calculate FLS
    if model is not None:
        # Use trained model for prediction
        try:
            # Prepare features for model
            all_features = []
            for col in feature_cols:
                for suffix in ["", "_zscore", "_rolling_mean", "_rolling_std", "_ewma"]:
                    feat_name = f"{col}{suffix}"
                    if feat_name in df.columns:
                        all_features.append(feat_name)
            
            if all_features:
                X = df[all_features].fillna(0)
                # Get probability of failure
                proba = model.predict_proba(X)
                df["FLS"] = proba[:, 1] if proba.shape[1] > 1 else proba[:, 0]
            else:
                # Fallback to heuristic
                df = _apply_heuristic_fls(df)
        except Exception:
            # Model prediction failed, use heuristic
            df = _apply_heuristic_fls(df)
    else:
        # No model available, use heuristic
        df = _apply_heuristic_fls(df)
    
    return df


def _apply_heuristic_fls(df: pd.DataFrame) -> pd.DataFrame:
    """Apply heuristic FLS calculation."""
    df["temp_deviation"] = (
        df.get("air_temp_zscore", 0) + df.get("process_temp_zscore", 0)
    ) / 2
    
    df["speed_variance"] = df.get("rotational_speed_rolling_std", 0)
    
    df["FLS"] = df.apply(
        lambda row: calculate_fls_heuristic(
            row.get("temp_deviation", 0),
            row.get("tool_wear", 0),
            row.get("speed_variance", 0),
            row.get("torque_zscore", 0)
        ),
        axis=1
    )
    
    return df
