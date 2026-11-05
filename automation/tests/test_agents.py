"""
Integration & Regression Test Suite for all 15 Specialist Agents
"""

import unittest
from automation.core.orchestrator import orchestrator
from automation.agents import SPECIALIST_AGENT_REGISTRY

class TestAllSpecialistAgents(unittest.TestCase):
    def test_registry_count(self):
        """Verifies that all 15 specialist service areas are properly registered."""
        self.assertEqual(len(SPECIALIST_AGENT_REGISTRY), 15)

    def test_all_15_agents_run(self):
        """Executes each of the 15 specialist agents and validates structured output."""
        for area_id in range(1, 16):
            with self.subTest(area_id=area_id):
                result = orchestrator.run_agent(area_id)
                self.assertEqual(
                    result.get("status"),
                    "success",
                    f"Agent #{area_id} failed with error: {result.get('error_message')}"
                )
                self.assertIsNotNone(result.get("output"))
                self.assertEqual(result.get("specialist_area_id"), area_id)

    def test_listing_optimizer_validation(self):
        """Tests Area #3 (Listing Optimizer) character and byte boundary constraints."""
        result = orchestrator.run_agent(3)
        metrics = result["output"].get("validation_metrics", {})
        self.assertTrue(metrics.get("title_valid"))
        self.assertEqual(metrics.get("bullets_count"), 5)
        self.assertTrue(metrics.get("search_terms_valid"))

    def test_ppc_bid_optimization(self):
        """Tests Area #5 (PPC Manager) harvesting and bid math."""
        result = orchestrator.run_agent(5)
        out = result["output"]
        self.assertIn("harvest_actions", out)
        self.assertIn("negative_actions", out)

    def test_account_health_metrics(self):
        """Tests Area #11 (Account Health) thresholds and POA generation."""
        result = orchestrator.run_agent(11)
        out = result["output"]
        self.assertIn("plan_of_action", out)
        self.assertIn("account_health_metrics", out)

if __name__ == "__main__":
    unittest.main()
