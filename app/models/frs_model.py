"""FRS (Flight Risk Score) model implementation."""

import logging
from typing import Dict, List, Optional
import pandas as pd

from app.features.flight_features import compute_flight_features
from app.config import config

logger = logging.getLogger(__name__)


class FRSModel:
    """Flight Risk Score model for predicting air freight delays."""
    
    def __init__(self):
        """Initialize FRS model with configured weights."""
        self.eta_weight = config.app.frs_eta_weight
        self.route_weight = config.app.frs_route_weight
        self.speed_weight = config.app.frs_speed_weight
        
    def predict(self, flight_data: pd.DataFrame) -> pd.DataFrame:
        """
        Predict FRS scores for flight data.
        
        Args:
            flight_data: DataFrame with flight information
            
        Returns:
            DataFrame with FRS scores and features
        """
        try:
            # Compute features and FRS
            result_df = compute_flight_features(flight_data)
            
            # Ensure FRS is within bounds
            result_df["FRS"] = result_df["FRS"].clip(0, 1)
            
            logger.info(f"Computed FRS for {len(result_df)} flights")
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error computing FRS: {e}")
            # Return original data with default FRS
            flight_data["FRS"] = 0.5
            return flight_data
    
    def predict_single(self, flight_record: Dict) -> float:
        """
        Predict FRS for a single flight record.
        
        Args:
            flight_record: Dictionary with flight information
            
        Returns:
            FRS score between 0 and 1
        """
        df = pd.DataFrame([flight_record])
        result = self.predict(df)
        
        if not result.empty and "FRS" in result.columns:
            return float(result.iloc[0]["FRS"])
        
        return 0.5  # Default neutral score
    
    def get_risk_level(self, frs: float) -> str:
        """
        Get risk level description for FRS score.
        
        Args:
            frs: FRS score between 0 and 1
            
        Returns:
            Risk level description
        """
        if frs >= config.app.critical_frs_threshold:
            return "CRITICAL"
        elif frs >= config.app.high_frs_threshold:
            return "HIGH"
        elif frs >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def explain_score(self, flight_record: Dict) -> Dict:
        """
        Provide explanation for FRS score.
        
        Args:
            flight_record: Flight record with computed features
            
        Returns:
            Dictionary with score explanation
        """
        frs = flight_record.get("FRS", 0.5)
        
        explanation = {
            "score": frs,
            "risk_level": self.get_risk_level(frs),
            "contributing_factors": []
        }
        
        # Check ETA drift
        eta_drift = flight_record.get("eta_drift_min", 0)
        if abs(eta_drift) > 30:
            explanation["contributing_factors"].append({
                "factor": "ETA Drift",
                "value": f"{eta_drift:.1f} minutes",
                "impact": "HIGH" if abs(eta_drift) > 60 else "MEDIUM"
            })
        
        # Check route deviation
        route_dev = flight_record.get("route_dev_km", 0)
        if route_dev > 50:
            explanation["contributing_factors"].append({
                "factor": "Route Deviation",
                "value": f"{route_dev:.1f} km",
                "impact": "HIGH" if route_dev > 100 else "MEDIUM"
            })
        
        # Check speed anomaly
        speed_z = flight_record.get("speed_zscore", 0)
        if abs(speed_z) > 2:
            explanation["contributing_factors"].append({
                "factor": "Speed Anomaly",
                "value": f"{speed_z:.2f} std dev",
                "impact": "HIGH" if abs(speed_z) > 3 else "MEDIUM"
            })
        
        if not explanation["contributing_factors"]:
            explanation["contributing_factors"].append({
                "factor": "Normal Operations",
                "value": "All parameters within normal range",
                "impact": "LOW"
            })
        
        return explanation


# Global model instance
frs_model = FRSModel()
