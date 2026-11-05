"""
Master Agent Swarm Orchestrator for AESAS
Coordinates, dispatches, and aggregates results from all 15 Specialist Agents.
"""

import logging
from typing import Dict, Any, List, Optional
from ..agents import SPECIALIST_AGENT_REGISTRY
from .base_agent import BaseAgent

logger = logging.getLogger("AESAS.Orchestrator")

class AgentSwarmOrchestrator:
    def __init__(self):
        self.agents: Dict[int, BaseAgent] = {}
        # Instantiate all 15 specialist agents
        for area_id, agent_cls in SPECIALIST_AGENT_REGISTRY.items():
            self.agents[area_id] = agent_cls()
        logger.info(f"Initialized AgentSwarmOrchestrator with {len(self.agents)} specialist agents.")

    def run_agent(self, specialist_area_id: int, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Runs a single specialist agent by ID (1 to 15)."""
        agent = self.agents.get(specialist_area_id)
        if not agent:
            raise ValueError(f"No agent registered for specialist area #{specialist_area_id}")
        return agent.run(inputs or {})

    def run_full_account_audit(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Runs an end-to-end full agency audit across all critical service modules:
        - Module 11: Account Health & Performance
        - Module 14: 360 Marketplace Audit & P&L
        - Module 5: PPC Optimization
        - Module 8: Inventory & FBA Forecasting
        - Module 3: Listing Optimization
        - Module 12: Buy Box Repricing
        - Module 15: Brand Protection
        """
        ctx = context or {}
        logger.info("Executing Complete 360-Degree Marketplace Agency Audit Swarm...")

        audit_sequence = [11, 14, 5, 8, 3, 12, 15]
        results = {}

        for area_id in audit_sequence:
            agent = self.agents[area_id]
            logger.info(f"Running Agent #{area_id}: {agent.name}")
            res = agent.run(ctx)
            results[agent.name] = res

        return {
            "orchestrator_status": "COMPLETED",
            "modules_executed": len(audit_sequence),
            "swarm_results": results
        }

    def list_specialists(self) -> List[Dict[str, Any]]:
        """Returns metadata for all 15 specialist service areas."""
        return [
            {
                "id": agent.specialist_area_id,
                "name": agent.name,
                "description": agent.description,
                "preferred_engine": agent.preferred_engine
            }
            for agent in self.agents.values()
        ]

# Global singleton orchestrator
orchestrator = AgentSwarmOrchestrator()
