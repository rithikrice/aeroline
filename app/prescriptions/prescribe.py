"""Prescription logic for generating action recommendations."""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from app.config import config
from app.prescriptions.cost_model import cost_optimizer, calculate_roi
from app.schemas import Action

logger = logging.getLogger(__name__)


def determine_action(
    frs: float,
    fls: float,
    otif_value: float = None,
    expedite_cost: float = None,
    downtime_cost_per_hour: float = None,
    spare_available: bool = True
) -> Tuple[Action, Dict]:
    """
    Determine the recommended action based on risk scores and costs.
    
    Rules:
    - If (FRS>0.7 and FLS>0.6) → RESCHEDULE unless expedite ROI positive
    - If FRS>0.8 and expedite_cost < otif_value*0.25 → EXPEDITE
    - If FLS>0.65 and spare_available → PULL_SPARES
    - Else NO_ACTION
    
    Args:
        frs: Flight Risk Score (0-1)
        fls: Failure Likelihood Score (0-1)
        otif_value: OTIF value
        expedite_cost: Expedite cost
        downtime_cost_per_hour: Downtime cost per hour
        spare_available: Whether spare parts are available
        
    Returns:
        Tuple of (recommended_action, explanation_dict)
    """
    # Use defaults if not provided
    otif_value = otif_value or config.app.default_otif_value
    expedite_cost = expedite_cost or config.app.default_expedite_cost
    downtime_cost_per_hour = downtime_cost_per_hour or config.app.default_downtime_cost_per_hour
    
    # Get cost analysis for all actions
    cost_analysis = cost_optimizer.optimize_action_costs(
        frs, fls, otif_value, expedite_cost, downtime_cost_per_hour
    )
    
    # Initialize explanation
    explanation = {
        "frs": frs,
        "fls": fls,
        "risk_assessment": _assess_risk_level(frs, fls),
        "cost_analysis": cost_analysis,
        "triggers": [],
        "decision_rationale": ""
    }
    
    # Apply decision rules
    
    # Rule 1: High compound risk - consider RESCHEDULE unless EXPEDITE has positive ROI
    if frs > config.app.high_frs_threshold and fls > config.app.high_fls_threshold:
        explanation["triggers"].append(f"High compound risk: FRS={frs:.2f}, FLS={fls:.2f}")
        
        # Check if expedite ROI is positive and better than reschedule
        if "EXPEDITE" in cost_analysis:
            expedite_roi = cost_analysis["EXPEDITE"]["roi"]
            reschedule_roi = cost_analysis["RESCHEDULE"]["roi"]
            
            if expedite_roi > 0 and expedite_roi > reschedule_roi:
                explanation["decision_rationale"] = (
                    f"Despite high compound risk, EXPEDITE has positive ROI ({expedite_roi:.0f}) "
                    f"and outperforms RESCHEDULE ({reschedule_roi:.0f})"
                )
                return Action.EXPEDITE, explanation
        
        explanation["decision_rationale"] = (
            "High compound risk requires rescheduling to avoid cascading failures"
        )
        return Action.RESCHEDULE, explanation
    
    # Rule 2: Critical FRS with affordable expedite
    if frs > config.app.critical_frs_threshold and expedite_cost < otif_value * 0.25:
        explanation["triggers"].append(f"Critical FRS ({frs:.2f}) with affordable expedite")
        explanation["decision_rationale"] = (
            f"Critical flight risk requires expediting. Cost ({expedite_cost:.0f}) "
            f"is within 25% of OTIF value ({otif_value:.0f})"
        )
        return Action.EXPEDITE, explanation
    
    # Rule 3: High FLS with available spares
    if fls > config.app.critical_fls_threshold and spare_available:
        explanation["triggers"].append(f"Critical FLS ({fls:.2f}) with spare parts available")
        
        if "PULL_SPARES" in cost_analysis:
            spare_benefit = cost_analysis["PULL_SPARES"].get("spare_benefit", 0)
            explanation["decision_rationale"] = (
                f"High failure risk requires pulling spare parts. "
                f"Expected benefit: {spare_benefit:.0f}"
            )
            return Action.PULL_SPARES, explanation
    
    # Rule 4: ROI-based decision
    # Find action with highest ROI
    best_action = Action.NO_ACTION
    best_roi = cost_analysis.get("NO_ACTION", {}).get("roi", 0)
    
    for action_name, analysis in cost_analysis.items():
        if analysis["roi"] > best_roi:
            best_roi = analysis["roi"]
            best_action = Action(action_name)
    
    if best_action != Action.NO_ACTION:
        explanation["triggers"].append(f"ROI optimization selected {best_action.value}")
        explanation["decision_rationale"] = (
            f"{best_action.value} provides highest ROI ({best_roi:.0f})"
        )
    else:
        explanation["decision_rationale"] = (
            "Risk levels are acceptable and no intervention provides positive ROI"
        )
    
    return best_action, explanation


def _assess_risk_level(frs: float, fls: float) -> Dict:
    """
    Assess overall risk level based on FRS and FLS.
    
    Args:
        frs: Flight Risk Score
        fls: Failure Likelihood Score
        
    Returns:
        Risk assessment dictionary
    """
    # Individual risk levels
    frs_level = "CRITICAL" if frs > 0.8 else "HIGH" if frs > 0.7 else "MEDIUM" if frs > 0.4 else "LOW"
    fls_level = "CRITICAL" if fls > 0.65 else "HIGH" if fls > 0.6 else "MEDIUM" if fls > 0.4 else "LOW"
    
    # Combined risk
    combined_score = (frs + fls) / 2
    if combined_score > 0.7:
        overall = "CRITICAL"
    elif combined_score > 0.5:
        overall = "HIGH"
    elif combined_score > 0.3:
        overall = "MEDIUM"
    else:
        overall = "LOW"
    
    return {
        "frs_level": frs_level,
        "fls_level": fls_level,
        "overall": overall,
        "combined_score": combined_score
    }


def generate_prescriptions(
    risk_data: List[Dict],
    persist: bool = False
) -> List[Dict]:
    """
    Generate prescriptions for a list of risk records.
    
    Args:
        risk_data: List of dictionaries with job/risk information
        persist: Whether to persist prescriptions to database
        
    Returns:
        List of prescription records
    """
    prescriptions = []
    
    for record in risk_data:
        # Extract required fields
        job_id = record.get("job_id", "")
        machine_id = record.get("machine_id", "")
        callsign = record.get("callsign", "")
        frs = record.get("FRS", 0.5)
        fls = record.get("FLS", 0.5)
        otif_value = record.get("otif_value", config.app.default_otif_value)
        expedite_cost = record.get("expedite_cost", config.app.default_expedite_cost)
        downtime_cost = record.get("downtime_cost", config.app.default_downtime_cost_per_hour * 2)
        
        # Determine action
        action, explanation = determine_action(
            frs, fls, otif_value, expedite_cost, downtime_cost / 2  # Convert back to per-hour
        )
        
        # Calculate final ROI
        roi = calculate_roi(
            otif_value, 
            expedite_cost if action == Action.EXPEDITE else 0,
            downtime_cost,
            frs,
            fls
        )
        
        # Create prescription record
        prescription = {
            "job_id": job_id,
            "machine_id": machine_id,
            "callsign": callsign,
            "frs": frs,
            "fls": fls,
            "otif_value": otif_value,
            "expedite_cost": expedite_cost,
            "downtime_cost": downtime_cost,
            "roi": roi,
            "action": action.value,
            "explain_json": explanation,
            "timestamp": datetime.utcnow()
        }
        
        prescriptions.append(prescription)
    
    if persist:
        # TODO: Persist to Snowflake RISK_JOIN table
        logger.info(f"Would persist {len(prescriptions)} prescriptions to database")
    
    return prescriptions


def generate_alert_message(prescription: Dict, use_cortex: bool = False) -> str:
    """
    Generate alert message for a prescription.
    
    Args:
        prescription: Prescription dictionary
        use_cortex: Whether to use Cortex for message generation
        
    Returns:
        Alert message string
    """
    if use_cortex:
        # TODO: Implement Cortex integration
        logger.info("Cortex integration not yet implemented, using template")
    
    # Template-based alert
    job_id = prescription.get("job_id", "Unknown")
    frs = prescription.get("frs", 0)
    fls = prescription.get("fls", 0)
    action = prescription.get("action", "NO_ACTION")
    
    # Get top contributing factors from explanation
    explain = prescription.get("explain_json", {})
    triggers = explain.get("triggers", [])
    top_features = ", ".join(triggers[:2]) if triggers else "Normal parameters"
    
    message = (
        f"Job {job_id}: FRS={frs:.2f}, FLS={fls:.2f} → {action}. "
        f"Triggers: {top_features}."
    )
    
    return message


class PrescriptionEngine:
    """Engine for generating and managing prescriptions."""
    
    def __init__(self):
        """Initialize prescription engine."""
        self.cost_optimizer = cost_optimizer
    
    def what_if_analysis(
        self,
        frs: float,
        fls: float,
        expedite_cost: float,
        downtime_cost: float,
        otif_value: float
    ) -> Dict:
        """
        Perform what-if analysis for given parameters.
        
        Args:
            frs: Flight Risk Score
            fls: Failure Likelihood Score
            expedite_cost: Expedite cost
            downtime_cost: Total downtime cost
            otif_value: OTIF value
            
        Returns:
            Analysis results with recommended action and ROI
        """
        # Convert total downtime cost to per-hour
        downtime_cost_per_hour = downtime_cost / 2  # Assume 2 hours default
        
        # Determine best action
        action, explanation = determine_action(
            frs, fls, otif_value, expedite_cost, downtime_cost_per_hour
        )
        
        # Calculate ROI for recommended action
        if action == Action.EXPEDITE:
            roi = calculate_roi(otif_value, expedite_cost, downtime_cost * 0.3, frs * 0.3, fls)
        elif action == Action.PULL_SPARES:
            roi = calculate_roi(otif_value, 0, downtime_cost * 0.25, frs, fls * 0.4)
        elif action == Action.RESCHEDULE:
            roi = calculate_roi(otif_value * 0.7, 0, 0, frs * 0.1, fls * 0.1)
        else:
            roi = calculate_roi(otif_value, 0, downtime_cost, frs, fls)
        
        return {
            "action": action,
            "roi": roi,
            "explanation": explanation,
            "inputs": {
                "frs": frs,
                "fls": fls,
                "expedite_cost": expedite_cost,
                "downtime_cost": downtime_cost,
                "otif_value": otif_value
            }
        }


# Global prescription engine instance
prescription_engine = PrescriptionEngine()
