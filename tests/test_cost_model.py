"""Unit tests for cost model and ROI calculations."""

import pytest
import math
from app.prescriptions.cost_model import (
    calculate_penalty,
    calculate_roi,
    estimate_downtime_hours,
    calculate_expedite_feasibility,
    calculate_spare_parts_benefit,
    cost_optimizer
)


class TestCostModel:
    """Test cost model functions."""
    
    def test_calculate_penalty_normal(self):
        """Test penalty calculation with normal risk scores."""
        penalty = calculate_penalty(0.5, 0.5)
        
        # With default weights: lambda=1.0, alpha=0.7, beta=0.3
        # penalty = 1.0 * (0.7 * 0.5 + 0.3 * 0.5) = 0.5
        assert penalty == pytest.approx(0.5, rel=0.01)
    
    def test_calculate_penalty_high_risk(self):
        """Test penalty calculation with high risk scores."""
        penalty = calculate_penalty(0.8, 0.8)
        
        # Combined risk = 0.8, which is > 0.7, so exponential penalty applies
        # Base penalty = 1.0 * (0.7 * 0.8 + 0.3 * 0.8) = 0.8
        # With exponential: 0.8 * exp(0.8 - 0.7) = 0.8 * exp(0.1)
        base_penalty = 0.8
        expected = base_penalty * math.exp(0.1)
        
        assert penalty == pytest.approx(expected, rel=0.01)
    
    def test_calculate_penalty_bounds(self):
        """Test penalty calculation respects bounds."""
        # Test with out-of-bounds inputs
        penalty_negative = calculate_penalty(-0.5, -0.5)
        assert penalty_negative == 0  # Should be clamped to 0
        
        penalty_high = calculate_penalty(1.5, 1.5)
        # Should be clamped to 1
        base = 1.0 * (0.7 * 1 + 0.3 * 1)
        expected = base * math.exp(1 - 0.7)
        assert penalty_high == pytest.approx(expected, rel=0.01)
    
    def test_calculate_roi_basic(self):
        """Test basic ROI calculation."""
        roi = calculate_roi(
            otif_value=10000,
            expedite_cost=3000,
            downtime_cost=2000,
            frs=0.5,
            fls=0.5
        )
        
        # ROI = 10000 - 3000 - 2000 - penalty_cost
        # penalty = 0.5 (from test above)
        # penalty_cost = 0.5 * (10000 * 0.5) = 2500
        expected = 10000 - 3000 - 2000 - 2500
        
        assert roi == pytest.approx(expected, rel=0.01)
    
    def test_calculate_roi_zero_risk(self):
        """Test ROI with zero risk scores."""
        roi = calculate_roi(
            otif_value=10000,
            expedite_cost=3000,
            downtime_cost=2000,
            frs=0,
            fls=0
        )
        
        # With zero risk, penalty should be 0
        expected = 10000 - 3000 - 2000
        assert roi == pytest.approx(expected, rel=0.01)
    
    def test_estimate_downtime_hours_normal(self):
        """Test downtime estimation with normal risk."""
        hours = estimate_downtime_hours(0.5, 0.5, base_hours=2.0)
        
        # delay_multiplier = 1 + (0.5 * 2) = 2
        # repair_multiplier = 1 + (0.5 * 1.5) = 1.75
        # total = 2 * max(2, 1.75) = 4
        assert hours == pytest.approx(4.0, rel=0.01)
    
    def test_estimate_downtime_hours_compound_risk(self):
        """Test downtime estimation with compound risk."""
        hours = estimate_downtime_hours(0.8, 0.7, base_hours=2.0)
        
        # High compound risk adds 50% multiplier
        # delay_multiplier = 1 + (0.8 * 2) = 2.6
        # repair_multiplier = 1 + (0.7 * 1.5) = 2.05
        # Before compound: 2 * max(2.6, 2.05) = 5.2
        # With compound: 5.2 * 1.5 = 7.8
        assert hours == pytest.approx(7.8, rel=0.01)
    
    def test_calculate_expedite_feasibility(self):
        """Test expedite feasibility calculation."""
        feasible, cost = calculate_expedite_feasibility(0.8, 3000, 10000)
        
        # cost_multiplier = 1 + (0.8 * 0.5) = 1.4
        # adjusted_cost = 3000 * 1.4 = 4200
        # feasible if 4200 < 10000 * 0.4 = 4000 -> False
        assert feasible is False
        assert cost == pytest.approx(4200, rel=0.01)
        
        # Test with lower FRS
        feasible2, cost2 = calculate_expedite_feasibility(0.3, 3000, 10000)
        # cost_multiplier = 1 + (0.3 * 0.5) = 1.15
        # adjusted_cost = 3000 * 1.15 = 3450
        # feasible if 3450 < 4000 -> True
        assert feasible2 is True
        assert cost2 == pytest.approx(3450, rel=0.01)
    
    def test_calculate_spare_parts_benefit(self):
        """Test spare parts benefit calculation."""
        benefit = calculate_spare_parts_benefit(0.7, 1500, spare_setup_hours=0.5)
        
        # failure_prob = 0.7
        # expected_downtime_without ≈ 4 * (1 + 0.7 * 1.5) = 8.2
        # downtime_with_spares = 0.5
        # saved_hours = (8.2 - 0.5) * 0.7 = 5.39
        # benefit = 5.39 * 1500 = 8085
        
        # Using the actual function logic:
        # expected_downtime_without = estimate_downtime_hours(0, 0.7, 4)
        # This gives: 4 * max(1, 1 + 0.7*1.5) = 4 * 2.05 = 8.2
        expected_saved = (8.2 - 0.5) * 0.7
        expected_benefit = expected_saved * 1500
        
        assert benefit == pytest.approx(expected_benefit, rel=0.1)


class TestCostOptimizer:
    """Test cost optimizer functionality."""
    
    def test_optimize_action_costs_no_action(self):
        """Test cost optimization for no action scenario."""
        optimizer = cost_optimizer
        
        results = optimizer.optimize_action_costs(
            frs=0.3,
            fls=0.3,
            otif_value=10000,
            expedite_cost=3000,
            downtime_cost_per_hour=1500
        )
        
        assert "NO_ACTION" in results
        assert "roi" in results["NO_ACTION"]
        assert "costs" in results["NO_ACTION"]
        
        # Check that NO_ACTION has zero expedite cost
        assert results["NO_ACTION"]["costs"]["expedite"] == 0
    
    def test_optimize_action_costs_expedite(self):
        """Test cost optimization includes expedite when feasible."""
        optimizer = cost_optimizer
        
        results = optimizer.optimize_action_costs(
            frs=0.6,
            fls=0.3,
            otif_value=15000,
            expedite_cost=2000,
            downtime_cost_per_hour=1500
        )
        
        assert "EXPEDITE" in results
        assert results["EXPEDITE"]["costs"]["expedite"] > 0
        
        # Expedite should reduce FRS impact
        expedite_roi = results["EXPEDITE"]["roi"]
        no_action_roi = results["NO_ACTION"]["roi"]
        
        # One of them should be positive or expedite should be better
        assert expedite_roi > no_action_roi or expedite_roi > 0
    
    def test_optimize_action_costs_pull_spares(self):
        """Test cost optimization includes spare parts option."""
        optimizer = cost_optimizer
        
        results = optimizer.optimize_action_costs(
            frs=0.3,
            fls=0.7,  # High FLS should trigger spares option
            otif_value=10000,
            expedite_cost=3000,
            downtime_cost_per_hour=2000
        )
        
        assert "PULL_SPARES" in results
        assert "spare_benefit" in results["PULL_SPARES"]
        assert results["PULL_SPARES"]["spare_benefit"] > 0
        
        # Spares should have lower downtime than no action
        spares_downtime = results["PULL_SPARES"]["costs"]["downtime"]
        no_action_downtime = results["NO_ACTION"]["costs"]["downtime"]
        assert spares_downtime < no_action_downtime
    
    def test_optimize_action_costs_reschedule(self):
        """Test cost optimization includes reschedule option."""
        optimizer = cost_optimizer
        
        results = optimizer.optimize_action_costs(
            frs=0.8,
            fls=0.8,
            otif_value=10000,
            expedite_cost=5000,
            downtime_cost_per_hour=2000
        )
        
        assert "RESCHEDULE" in results
        
        # Reschedule should have no expedite or downtime costs
        assert results["RESCHEDULE"]["costs"]["expedite"] == 0
        assert results["RESCHEDULE"]["costs"]["downtime"] == 0
        
        # But should have OTIF impact
        assert "otif_impact" in results["RESCHEDULE"]["costs"]
        assert results["RESCHEDULE"]["costs"]["otif_impact"] > 0
    
    def test_optimizer_consistency(self):
        """Test that optimizer produces consistent results."""
        optimizer = cost_optimizer
        
        # Run twice with same inputs
        results1 = optimizer.optimize_action_costs(0.5, 0.5)
        results2 = optimizer.optimize_action_costs(0.5, 0.5)
        
        # Should produce identical results
        assert results1.keys() == results2.keys()
        
        for action in results1:
            assert results1[action]["roi"] == pytest.approx(
                results2[action]["roi"], rel=0.001
            )
