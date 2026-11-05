"""
Specialist Area 1: Seller Central & Vendor Central Account Setup Agent
Automates verification workflows, entity creation, tax/VAT configuration,
shipping template setup, and Vendor Central onboarding validations.
"""

from typing import Dict, Any
from ..core.base_agent import BaseAgent
from ..connectors.amazon_sp_api import AmazonSPAPIClient

class AccountSetupAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="AccountSetupAgent",
            specialist_area_id=1,
            description="Automates Seller & Vendor Central account onboarding, tax, and regional configuration.",
            preferred_engine="hermes"
        )
        self.sp_client = AmazonSPAPIClient()

    def get_default_system_prompt(self) -> str:
        return (
            "You are the JVK Commerce Specialist for Seller Central & Vendor Central Account Setup. "
            "Your role is to validate merchant tax documentation (EIN, W-8BEN, VAT/IOSS, GST), "
            "configure multi-country shipping templates, verify deposit methods, and structure "
            "Vendor Central Direct Fulfillment (DF) handshakes. Ensure 100% compliance with "
            "Amazon marketplace onboarding policies and provide structured JSON outputs."
        )

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        entity_name = inputs.get("entity_name", "Global Enterprise Corp")
        tax_id = inputs.get("tax_id", "XX-XXXXXXX")
        target_marketplaces = inputs.get("target_marketplaces", ["US", "CA", "UK", "DE", "AE"])

        participations = self.sp_client.get_marketplace_participations()

        prompt = (
            f"Generate a comprehensive account setup blueprint for legal entity '{entity_name}'.\n"
            f"Tax ID: {tax_id}\n"
            f"Target Marketplaces: {', '.join(target_marketplaces)}\n"
            "Include:\n"
            "1. Tax compliance checklist (W-8BEN / UK VAT / EU IOSS / UAE TRN)\n"
            "2. Default automated shipping templates (transit days, delivery regions)\n"
            "3. User permissions & IAM Role delegation structure for SP-API\n"
            "4. Vendor Central Direct Fulfillment EDI handshake readiness\n"
            "Return output as a valid JSON object."
        )

        llm_response = self.call_llm(prompt=prompt, engine_type="hermes")

        return {
            "entity_name": entity_name,
            "target_marketplaces": target_marketplaces,
            "participations_detected": participations.get("payload", []),
            "setup_plan": llm_response.get("parsed_json") or llm_response.get("raw_content")
        }
