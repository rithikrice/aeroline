"""Unit tests for prescription logic."""

import pytest
from app.prescriptions.prescribe import (
    determine_action,
    generate_prescriptions,
    generate_alert_message,
    prescription_engine
)
from app.schemas import Action


class TestPrescriptionLogic:
    """Test prescription determination logic."""
    
    def test_determine_action_no_action(self):
        """Test NO_ACTION is recommended for low risk."""
        action, explanation = determine_action(
            frs=0.3,
            fls=0.3,
            otif_value=10000,
            expedite_cost=3000,
            downtime_cost_per_hour=1500,
            spare_available=True
        )
        
        assert action == Action.NO_ACTION
        assert "explanation" in locals() and explanation is not None
        assert explanation["frs"] == 0.3
        assert explanation["fls"] == 0.3
    
    def test_determine_action_reschedule(self):
        """Test RESCHEDULE for high compound risk."""
        action, explanation = determine_action(
            frs=0.75,
            fls=0.65,
            otif_value=10000,
            expedite_cost=8000,  # High expedite cost
            downtime_cost_per_hour=1500,
            spare_available=True
        )
        
        # Should recommend RESCHEDULE due to high compound risk
        # and expensive expedite
        assert action == Action.RESCHEDULE
        assert "High compound risk" in str(explanation["triggers"])
    
    def test_determine_action_expedite_critical_frs(self):
        """Test EXPEDITE for critical FRS with affordable cost."""
        action, explanation = determine_action(
            frs=0.85,  # Critical FRS
            fls=0.3,
            otif_value=10000,
            expedite_cost=2000,  # Less than 25% of OTIF
            downtime_cost_per_hour=1500,
            spare_available=True
        )
        
        assert action == Action.EXPEDITE
        assert "Critical FRS" in str(explanation["triggers"])
    
    def test_determine_action_expedite_positive_roi(self):
        """Test EXPEDITE when ROI is positive despite compound risk."""
        action, explanation = determine_action(
            frs=0.72,
            fls=0.62,
            otif_value=20000,
            expedite_cost=2000,  # Low cost relative to OTIF
            downtime_cost_per_hour=3000,
            spare_available=True
        )
        
        # Even with compound risk, low expedite cost should make it worthwhile
        assert action == Action.EXPEDITE
        assert "positive ROI" in explanation["decision_rationale"].lower() or \
               "expedite" in explanation["decision_rationale"].lower()
    
    def test_determine_action_pull_spares(self):
        """Test PULL_SPARES for high FLS."""
        action, explanation = determine_action(
            frs=0.4,
            fls=0.68,  # High FLS
            otif_value=10000,
            expedite_cost=3000,
            downtime_cost_per_hour=2000,
            spare_available=True
        )
        
        assert action == Action.PULL_SPARES
        assert "Critical FLS" in str(explanation["triggers"])
    
    def test_determine_action_no_spares_available(self):
        """Test behavior when spares are not available."""
        action, explanation = determine_action(
            frs=0.4,
            fls=0.68,  # High FLS but no spares
            otif_value=10000,
            expedite_cost=3000,
            downtime_cost_per_hour=2000,
            spare_available=False
        )
        
        # Should not recommend PULL_SPARES if not available
        assert action != Action.PULL_SPARES
    
    def test_determine_action_edge_cases(self):
        """Test edge cases in action determination."""
        # Test with zero risk scores
        action_zero, _ = determine_action(
            frs=0,
            fls=0,
            otif_value=10000,
            expedite_cost=3000,
            downtime_cost_per_hour=1500
        )
        assert action_zero == Action.NO_ACTION
        
        # Test with maximum risk scores
        action_max, _ = determine_action(
            frs=1.0,
            fls=1.0,
            otif_value=10000,
            expedite_cost=10000,  # Very expensive
            downtime_cost_per_hour=5000
        )
        assert action_max == Action.RESCHEDULE
        
        # Test with very high OTIF value
        action_high_otif, _ = determine_action(
            frs=0.8,
            fls=0.4,
            otif_value=100000,  # Very high value
            expedite_cost=3000,  # Now relatively cheap
            downtime_cost_per_hour=1500
        )
        assert action_high_otif == Action.EXPEDITE


class TestPrescriptionGeneration:
    """Test prescription generation for multiple jobs."""
    
    def test_generate_prescriptions_basic(self):
        """Test basic prescription generation."""
        risk_data = [
            {
                "job_id": "JOB-001",
                "machine_id": "M-01",
                "callsign": "TEST01",
                "FRS": 0.75,
                "FLS": 0.62,
                "otif_value": 10000,
                "expedite_cost": 3000,
                "downtime_cost": 3000
            },
            {
                "job_id": "JOB-002",
                "machine_id": "M-02",
                "callsign": "TEST02",
                "FRS": 0.3,
                "FLS": 0.3,
                "otif_value": 8000,
                "expedite_cost": 2000,
                "downtime_cost": 2000
            }
        ]
        
        prescriptions = generate_prescriptions(risk_data, persist=False)
        
        assert len(prescriptions) == 2
        
        # Check first prescription (high risk)
        assert prescriptions[0]["job_id"] == "JOB-001"
        assert prescriptions[0]["action"] in ["EXPEDITE", "RESCHEDULE", "PULL_SPARES"]
        assert "explain_json" in prescriptions[0]
        
        # Check second prescription (low risk)
        assert prescriptions[1]["job_id"] == "JOB-002"
        assert prescriptions[1]["action"] == "NO_ACTION"
    
    def test_generate_prescriptions_empty(self):
        """Test prescription generation with empty data."""
        prescriptions = generate_prescriptions([], persist=False)
        assert prescriptions == []
    
    def test_generate_prescriptions_missing_fields(self):
        """Test prescription generation with missing fields uses defaults."""
        risk_data = [
            {
                "job_id": "JOB-003",
                "machine_id": "M-03",
                "callsign": "TEST03"
                # Missing FRS, FLS, costs - should use defaults
            }
        ]
        
        prescriptions = generate_prescriptions(risk_data, persist=False)
        
        assert len(prescriptions) == 1
        assert prescriptions[0]["frs"] == 0.5  # Default
        assert prescriptions[0]["fls"] == 0.5  # Default
        assert prescriptions[0]["action"] == "NO_ACTION"  # Low default risk


class TestAlertGeneration:
    """Test alert message generation."""
    
    def test_generate_alert_message_basic(self):
        """Test basic alert message generation."""
        prescription = {
            "job_id": "JOB-001",
            "frs": 0.75,
            "fls": 0.62,
            "action": "EXPEDITE",
            "explain_json": {
                "triggers": ["High FRS", "Moderate FLS"],
                "decision_rationale": "Expedite to avoid delays"
            }
        }
        
        message = generate_alert_message(prescription, use_cortex=False)
        
        assert "JOB-001" in message
        assert "FRS=0.75" in message
        assert "FLS=0.62" in message
        assert "EXPEDITE" in message
        assert "High FRS" in message
    
    def test_generate_alert_message_no_triggers(self):
        """Test alert message with no triggers."""
        prescription = {
            "job_id": "JOB-002",
            "frs": 0.3,
            "fls": 0.3,
            "action": "NO_ACTION",
            "explain_json": {
                "triggers": []
            }
        }
        
        message = generate_alert_message(prescription, use_cortex=False)
        
        assert "JOB-002" in message
        assert "NO_ACTION" in message
        assert "Normal parameters" in message


class TestPrescriptionEngine:
    """Test prescription engine functionality."""
    
    def test_whatif_analysis_basic(self):
        """Test basic what-if analysis."""
        engine = prescription_engine
        
        result = engine.what_if_analysis(
            frs=0.6,
            fls=0.5,
            expedite_cost=3000,
            downtime_cost=3000,
            otif_value=10000
        )
        
        assert "action" in result
        assert "roi" in result
        assert "explanation" in result
        assert "inputs" in result
        
        # Check inputs are preserved
        assert result["inputs"]["frs"] == 0.6
        assert result["inputs"]["fls"] == 0.5
    
    def test_whatif_analysis_scenarios(self):
        """Test what-if analysis with different scenarios."""
        engine = prescription_engine
        
        # Scenario 1: High risk, expensive expedite
        result1 = engine.what_if_analysis(
            frs=0.9,
            fls=0.8,
            expedite_cost=8000,
            downtime_cost=5000,
            otif_value=10000
        )
        assert result1["action"] == Action.RESCHEDULE
        
        # Scenario 2: High FRS, cheap expedite
        result2 = engine.what_if_analysis(
            frs=0.85,
            fls=0.3,
            expedite_cost=1000,
            downtime_cost=2000,
            otif_value=10000
        )
        assert result2["action"] == Action.EXPEDITE
        
        # Scenario 3: High FLS
        result3 = engine.what_if_analysis(
            frs=0.3,
            fls=0.75,
            expedite_cost=3000,
            downtime_cost=4000,
            otif_value=10000
        )
        assert result3["action"] == Action.PULL_SPARES
        
        # Scenario 4: Low risk
        result4 = engine.what_if_analysis(
            frs=0.2,
            fls=0.2,
            expedite_cost=3000,
            downtime_cost=2000,
            otif_value=10000
        )
        assert result4["action"] == Action.NO_ACTION
    
    def test_whatif_roi_calculation(self):
        """Test that what-if analysis calculates ROI correctly."""
        engine = prescription_engine
        
        result = engine.what_if_analysis(
            frs=0.5,
            fls=0.5,
            expedite_cost=3000,
            downtime_cost=2000,
            otif_value=10000
        )
        
        # ROI should be a reasonable number
        assert isinstance(result["roi"], (int, float))
        assert -10000 < result["roi"] < 10000  # Sanity check
        
        # Different actions should have different ROIs
        result_expedite = engine.what_if_analysis(
            frs=0.8,
            fls=0.3,
            expedite_cost=2000,
            downtime_cost=2000,
            otif_value=15000
        )
        
        if result_expedite["action"] == Action.EXPEDITE:
            # Expedite ROI should account for expedite cost
            assert result_expedite["roi"] < 15000  # Less than OTIF due to costs
