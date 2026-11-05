"""
Specialist Area 11: Account Health & Performance Monitoring Agent
Monitors critical health metrics (ODR < 1%, LDR < 4%, VTR > 95%), detects policy violations,
and generates formal, 3-part Plan of Action (POA) appeals for Seller Performance teams.
"""

from typing import Dict, Any, List
from ..core.base_agent import BaseAgent
from ..connectors.amazon_sp_api import AmazonSPAPIClient

class AccountHealthAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="AccountHealthAgent",
            specialist_area_id=11,
            description="Monitors account health metrics, flags policy risks, and drafts formal Plan of Action (POA) appeals.",
            preferred_engine="frontier"  # Claude 3.7 for authoritative, legalistic appeal writing
        )
        self.sp_client = AmazonSPAPIClient()

    def get_default_system_prompt(self) -> str:
        return (
            "You are the JVK Commerce Account Health & Seller Performance Defense Lead. "
            "You protect marketplace accounts against suspensions and resolve policy warnings. "
            "When drafting a Plan of Action (POA), you strictly adhere to Amazon's 3-part structure:\n"
            "1. The Root Cause of the issue (honest, objective, detailed identification of failure points)\n"
            "2. Immediate Corrective Actions taken (remedies enacted for existing affected orders/listings)\n"
            "3. Preventive Measures implemented (systemic, long-term operational changes to guarantee zero recurrence)\n"
            "Write in an authoritative, humble, and evidence-backed tone. Return output as JSON."
        )

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        health_data = self.sp_client.get_account_health()
        violation_type = inputs.get("violation_type", "Late Dispatch Rate (LDR) Exceeded")
        incident_context = inputs.get("incident_context", "Carrier courier truck failed to collect packages during severe regional snowstorm on Jan 14.")

        # Metric compliance checks
        odr = health_data.get("order_defect_rate", 0.0)
        ldr = health_data.get("late_dispatch_rate", 0.0)
        vtr = health_data.get("valid_tracking_rate", 100.0)

        compliance_alerts = []
        if odr >= 1.0:
            compliance_alerts.append(f"CRITICAL: Order Defect Rate is {odr}% (Target < 1.0%)")
        if ldr >= 4.0:
            compliance_alerts.append(f"WARNING: Late Dispatch Rate is {ldr}% (Target < 4.0%)")
        if vtr < 95.0:
            compliance_alerts.append(f"WARNING: Valid Tracking Rate is {vtr}% (Target > 95.0%)")

        prompt = (
            f"Draft a formal Amazon Seller Performance Plan of Action (POA) for:\n"
            f"Issue: {violation_type}\n"
            f"Context: {incident_context}\n"
            f"Current Metrics: ODR={odr}%, LDR={ldr}%, VTR={vtr}%\n\n"
            "Provide:\n"
            "1. Root Cause Statement\n"
            "2. Immediate Actions Taken\n"
            "3. Long-Term Preventive Measures\n"
            "4. Account Health Risk Level Assessment (Low, Medium, Severe)\n"
            "Format as structured JSON."
        )

        llm_response = self.call_llm(prompt=prompt, engine_type="frontier")

        return {
            "account_health_metrics": health_data,
            "compliance_alerts": compliance_alerts,
            "incident_addressed": violation_type,
            "plan_of_action": llm_response.get("parsed_json") or llm_response.get("raw_content")
        }
