"""Cost model for ROI calculation."""

import math
from typing import Dict, Tuple
from app.config import config


def calculate_penalty(frs: float, fls: float, lambda_val: float = 1.0, alpha: float = 0.7, beta: float = 0.3) -> float:
    """
    Calculate risk penalty based on FRS and FLS.
    
    Args:
        frs: Flight Risk Score (0-1)
        fls: Failure Likelihood Score (0-1)
        lambda_val: Overall penalty weight
        alpha: FRS weight
        beta: FLS weight
        
    Returns:
        Risk penalty value
    """
    # Ensure scores are within bounds
    frs = max(0, min(1, frs))
    fls = max(0, min(1, fls))
    
    # Calculate weighted penalty
    penalty = lambda_val * (alpha * frs + beta * fls)
    
    # Scale penalty based on risk levels
    # Higher combined risk = exponentially higher penalty
    combined_risk = (frs + fls) / 2
    if combined_risk > 0.7:
        # Exponential penalty for high risk
        penalty *= math.exp(combined_risk - 0.7)
    
    return penalty


def calculate_roi(
    otif_value: float,
    expedite_cost: float,
    downtime_cost: float,
    frs: float,
    fls: float,
    lambda_val: float = None,
    alpha: float = None,
    beta: float = None
) -> float:
    """
    Calculate Return on Investment (ROI).
    
    Formula: ROI = otif_value - expedite_cost - downtime_cost - λ*(α*FRS + β*FLS)
    
    Args:
        otif_value: Value of on-time in-full delivery
        expedite_cost: Cost of expediting shipment
        downtime_cost: Cost of machine downtime
        frs: Flight Risk Score (0-1)
        fls: Failure Likelihood Score (0-1)
        lambda_val: Penalty weight (uses config default if None)
        alpha: FRS weight (uses config default if None)
        beta: FLS weight (uses config default if None)
        
    Returns:
        ROI value
    """
    # Use config defaults if not provided
    if lambda_val is None:
        lambda_val = config.app.frs_lambda
    if alpha is None:
        alpha = config.app.frs_alpha
    if beta is None:
        beta = config.app.fls_beta
    
    # Calculate penalty
    penalty = calculate_penalty(frs, fls, lambda_val, alpha, beta)
    
    # Scale penalty to cost magnitude
    # Penalty should be proportional to the potential costs
    penalty_cost = penalty * (otif_value * 0.5)  # Max penalty is 50% of OTIF value
    
    # Calculate ROI
    roi = otif_value - expedite_cost - downtime_cost - penalty_cost
    
    return roi


def estimate_downtime_hours(frs: float, fls: float, base_hours: float = 2.0) -> float:
    """
    Estimate potential downtime hours based on risk scores.
    
    Args:
        frs: Flight Risk Score (0-1)
        fls: Failure Likelihood Score (0-1)
        base_hours: Base downtime estimate
        
    Returns:
        Estimated downtime hours
    """
    # Higher FRS = longer delay
    delay_multiplier = 1 + (frs * 2)  # Up to 3x base for high FRS
    
    # Higher FLS = longer repair time
    repair_multiplier = 1 + (fls * 1.5)  # Up to 2.5x base for high FLS
    
    # Combined effect
    total_hours = base_hours * max(delay_multiplier, repair_multiplier)
    
    # Add interaction effect for compound risk
    if frs > 0.7 and fls > 0.6:
        total_hours *= 1.5  # Additional 50% for compound risk
    
    return total_hours


def calculate_expedite_feasibility(
    frs: float,
    current_expedite_cost: float,
    otif_value: float
) -> Tuple[bool, float]:
    """
    Determine if expediting is feasible and cost-effective.
    
    Args:
        frs: Flight Risk Score
        current_expedite_cost: Current expedite cost
        otif_value: OTIF value
        
    Returns:
        Tuple of (is_feasible, adjusted_cost)
    """
    # Higher FRS = higher expedite cost (supply/demand)
    cost_multiplier = 1 + (frs * 0.5)  # Up to 50% premium for high risk
    adjusted_cost = current_expedite_cost * cost_multiplier
    
    # Feasible if cost is less than 40% of OTIF value
    is_feasible = adjusted_cost < (otif_value * 0.4)
    
    return is_feasible, adjusted_cost


def calculate_spare_parts_benefit(
    fls: float,
    downtime_cost_per_hour: float,
    spare_setup_hours: float = 0.5
) -> float:
    """
    Calculate benefit of pulling spare parts.
    
    Args:
        fls: Failure Likelihood Score
        downtime_cost_per_hour: Cost per hour of downtime
        spare_setup_hours: Time to set up spare parts
        
    Returns:
        Net benefit of using spares
    """
    # Probability of failure
    failure_prob = fls
    
    # Expected downtime without spares (hours)
    expected_downtime_without = estimate_downtime_hours(0, fls, base_hours=4)
    
    # Downtime with spares (just setup time)
    downtime_with_spares = spare_setup_hours
    
    # Calculate expected benefit
    saved_hours = (expected_downtime_without - downtime_with_spares) * failure_prob
    benefit = saved_hours * downtime_cost_per_hour
    
    return benefit


class CostOptimizer:
    """Optimizer for cost-based decision making."""
    
    def __init__(self):
        """Initialize cost optimizer with config values."""
        self.default_otif = config.app.default_otif_value
        self.default_expedite = config.app.default_expedite_cost
        self.default_downtime_per_hour = config.app.default_downtime_cost_per_hour
    
    def optimize_action_costs(
        self,
        frs: float,
        fls: float,
        otif_value: float = None,
        expedite_cost: float = None,
        downtime_cost_per_hour: float = None
    ) -> Dict:
        """
        Optimize costs for different action scenarios.
        
        Args:
            frs: Flight Risk Score
            fls: Failure Likelihood Score
            otif_value: OTIF value (uses default if None)
            expedite_cost: Expedite cost (uses default if None)
            downtime_cost_per_hour: Downtime cost per hour (uses default if None)
            
        Returns:
            Dictionary with cost analysis for each action
        """
        # Use defaults if not provided
        otif_value = otif_value or self.default_otif
        expedite_cost = expedite_cost or self.default_expedite
        downtime_cost_per_hour = downtime_cost_per_hour or self.default_downtime_per_hour
        
        # Estimate downtime
        downtime_hours = estimate_downtime_hours(frs, fls)
        downtime_cost = downtime_hours * downtime_cost_per_hour
        
        # Calculate ROI for each action
        actions = {}
        
        # No Action
        actions["NO_ACTION"] = {
            "roi": calculate_roi(otif_value, 0, downtime_cost, frs, fls),
            "costs": {
                "expedite": 0,
                "downtime": downtime_cost,
                "risk_penalty": calculate_penalty(frs, fls) * otif_value * 0.5
            }
        }
        
        # Expedite
        feasible, adjusted_expedite = calculate_expedite_feasibility(frs, expedite_cost, otif_value)
        if feasible:
            # Expediting reduces FRS impact
            reduced_frs = frs * 0.3  # 70% reduction in flight risk
            reduced_downtime = estimate_downtime_hours(reduced_frs, fls) * downtime_cost_per_hour
            
            actions["EXPEDITE"] = {
                "roi": calculate_roi(otif_value, adjusted_expedite, reduced_downtime, reduced_frs, fls),
                "costs": {
                    "expedite": adjusted_expedite,
                    "downtime": reduced_downtime,
                    "risk_penalty": calculate_penalty(reduced_frs, fls) * otif_value * 0.5
                }
            }
        
        # Pull Spares
        spare_benefit = calculate_spare_parts_benefit(fls, downtime_cost_per_hour)
        if spare_benefit > 0:
            # Using spares reduces FLS impact
            reduced_fls = fls * 0.4  # 60% reduction in failure impact
            spare_downtime = 0.5 * downtime_cost_per_hour  # Just setup time
            
            actions["PULL_SPARES"] = {
                "roi": calculate_roi(otif_value, 0, spare_downtime, frs, reduced_fls),
                "costs": {
                    "expedite": 0,
                    "downtime": spare_downtime,
                    "risk_penalty": calculate_penalty(frs, reduced_fls) * otif_value * 0.5
                },
                "spare_benefit": spare_benefit
            }
        
        # Reschedule
        # Rescheduling avoids most costs but may have OTIF impact
        reschedule_otif = otif_value * 0.7  # 30% OTIF penalty for rescheduling
        actions["RESCHEDULE"] = {
            "roi": calculate_roi(reschedule_otif, 0, 0, frs * 0.1, fls * 0.1),
            "costs": {
                "expedite": 0,
                "downtime": 0,
                "risk_penalty": calculate_penalty(frs * 0.1, fls * 0.1) * reschedule_otif * 0.5,
                "otif_impact": otif_value * 0.3
            }
        }
        
        return actions


# Global optimizer instance
cost_optimizer = CostOptimizer()
