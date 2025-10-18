"""FLS (Failure Likelihood Score) model implementation."""

import logging
from typing import Dict, List, Optional
import pandas as pd
import pickle
import os

from app.features.maintenance_features import (
    compute_maintenance_features,
    train_fls_model
)
from app.config import config

logger = logging.getLogger(__name__)


class FLSModel:
    """Failure Likelihood Score model for predicting machine failures."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize FLS model.
        
        Args:
            model_path: Optional path to saved model
        """
        self.model = None
        self.model_path = model_path or "models/fls_model.pkl"
        
        # Try to load existing model
        self._load_model()
    
    def _load_model(self) -> None:
        """Load saved model if available."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    self.model = pickle.load(f)
                logger.info(f"Loaded FLS model from {self.model_path}")
            except Exception as e:
                logger.warning(f"Failed to load model: {e}")
                self.model = None
    
    def _save_model(self) -> None:
        """Save trained model to disk."""
        if self.model is not None:
            try:
                os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
                with open(self.model_path, "wb") as f:
                    pickle.dump(self.model, f)
                logger.info(f"Saved FLS model to {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to save model: {e}")
    
    def train(self, training_data: pd.DataFrame) -> bool:
        """
        Train FLS model on historical data.
        
        Args:
            training_data: DataFrame with machine data and failure labels
            
        Returns:
            True if training successful, False otherwise
        """
        try:
            self.model = train_fls_model(training_data)
            
            if self.model is not None:
                self._save_model()
                logger.info("FLS model trained successfully")
                return True
            else:
                logger.warning("FLS model training failed, using heuristic approach")
                return False
                
        except Exception as e:
            logger.error(f"Error training FLS model: {e}")
            return False
    
    def predict(self, machine_data: pd.DataFrame) -> pd.DataFrame:
        """
        Predict FLS scores for machine data.
        
        Args:
            machine_data: DataFrame with machine information
            
        Returns:
            DataFrame with FLS scores and features
        """
        try:
            # Compute features and FLS
            result_df = compute_maintenance_features(machine_data, self.model)
            
            # Ensure FLS is within bounds
            result_df["FLS"] = result_df["FLS"].clip(0, 1)
            
            logger.info(f"Computed FLS for {len(result_df)} machines")
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error computing FLS: {e}")
            # Return original data with default FLS
            machine_data["FLS"] = 0.5
            return machine_data
    
    def predict_single(self, machine_record: Dict) -> float:
        """
        Predict FLS for a single machine record.
        
        Args:
            machine_record: Dictionary with machine information
            
        Returns:
            FLS score between 0 and 1
        """
        df = pd.DataFrame([machine_record])
        result = self.predict(df)
        
        if not result.empty and "FLS" in result.columns:
            return float(result.iloc[0]["FLS"])
        
        return 0.5  # Default neutral score
    
    def get_risk_level(self, fls: float) -> str:
        """
        Get risk level description for FLS score.
        
        Args:
            fls: FLS score between 0 and 1
            
        Returns:
            Risk level description
        """
        if fls >= config.app.critical_fls_threshold:
            return "CRITICAL"
        elif fls >= config.app.high_fls_threshold:
            return "HIGH"
        elif fls >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def explain_score(self, machine_record: Dict) -> Dict:
        """
        Provide explanation for FLS score.
        
        Args:
            machine_record: Machine record with computed features
            
        Returns:
            Dictionary with score explanation
        """
        fls = machine_record.get("FLS", 0.5)
        
        explanation = {
            "score": fls,
            "risk_level": self.get_risk_level(fls),
            "contributing_factors": [],
            "model_type": "ML" if self.model is not None else "Heuristic"
        }
        
        # Check temperature anomalies
        air_temp_z = machine_record.get("air_temp_zscore", 0)
        process_temp_z = machine_record.get("process_temp_zscore", 0)
        
        if abs(air_temp_z) > 2 or abs(process_temp_z) > 2:
            explanation["contributing_factors"].append({
                "factor": "Temperature Anomaly",
                "value": f"Air: {air_temp_z:.2f}σ, Process: {process_temp_z:.2f}σ",
                "impact": "HIGH" if max(abs(air_temp_z), abs(process_temp_z)) > 3 else "MEDIUM"
            })
        
        # Check tool wear
        tool_wear = machine_record.get("tool_wear", 0)
        if tool_wear > 150:
            explanation["contributing_factors"].append({
                "factor": "Tool Wear",
                "value": f"{tool_wear:.0f} units",
                "impact": "HIGH" if tool_wear > 200 else "MEDIUM"
            })
        
        # Check torque anomaly
        torque_z = machine_record.get("torque_zscore", 0)
        if abs(torque_z) > 2:
            explanation["contributing_factors"].append({
                "factor": "Torque Anomaly",
                "value": f"{torque_z:.2f} std dev",
                "impact": "HIGH" if abs(torque_z) > 3 else "MEDIUM"
            })
        
        # Check speed variance
        speed_var = machine_record.get("rotational_speed_rolling_std", 0)
        if speed_var > 50:
            explanation["contributing_factors"].append({
                "factor": "Speed Instability",
                "value": f"Variance: {speed_var:.1f}",
                "impact": "HIGH" if speed_var > 100 else "MEDIUM"
            })
        
        if not explanation["contributing_factors"]:
            explanation["contributing_factors"].append({
                "factor": "Normal Operations",
                "value": "All parameters within normal range",
                "impact": "LOW"
            })
        
        return explanation


# Global model instance
fls_model = FLSModel()
