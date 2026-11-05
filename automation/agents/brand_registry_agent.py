"""
Specialist Area 15: Brand Registry & Account Support Agent
Monitors brand trademark integrity, detects unauthorized catalog hijackers,
generates Report a Violation (RAV) filings, and manages Project Zero/Transparency workflows.
"""

from typing import Dict, Any, List
from ..core.base_agent import BaseAgent
from ..connectors.keepa_connector import KeepaClient

class BrandRegistryAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="BrandRegistryAgent",
            specialist_area_id=15,
            description="Protects brand trademarks, removes unauthorized hijackers, and files Report a Violation (RAV) claims.",
            preferred_engine="frontier"  # Claude 3.7 for legalistic IP dispute drafting
        )
        self.keepa = KeepaClient()

    def get_default_system_prompt(self) -> str:
        return (
            "You are the JVK Commerce Brand Protection & Intellectual Property Counsel. "
            "You safeguard brand assets under Amazon Brand Registry policies. "
            "You track unauthorized Buy Box hijackers selling counterfeit or parallel imports, "
            "structure Report a Violation (RAV) complaints with exact USPTO trademark registration numbers, "
            "and deploy Transparency 2D serial barcode verification. Write with precise legal phrasing. Return JSON."
        )

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        brand_name = inputs.get("brand_name", "JVK Hydration")
        trademark_number = inputs.get("trademark_number", "USPTO-97812345")
        target_asin = inputs.get("target_asin", "B08EXAMPLE12")

        keepa_data = self.keepa.get_product_data(target_asin)
        alerts = keepa_data.get("alerts", [])

        prompt = (
            f"Review brand protection status and generate a Report a Violation (RAV) / Cease & Desist package.\n"
            f"Brand Name: {brand_name}\n"
            f"Registered Trademark: {trademark_number}\n"
            f"Protected ASIN: {target_asin}\n"
            f"Recent Seller Alerts: {alerts}\n\n"
            "Include:\n"
            "1. Hijacker Threat Level Assessment\n"
            "2. Formal Cease & Desist (C&D) Notice to unauthorized seller\n"
            "3. Amazon Brand Registry RAV Submission Template (IP Infringement category, legal representation)\n"
            "4. Transparency Serial Number Enrollment Plan to permanently block unauthorized stock\n"
            "Return valid JSON."
        )

        llm_response = self.call_llm(prompt=prompt, engine_type="frontier")

        return {
            "brand_name": brand_name,
            "trademark_number": trademark_number,
            "target_asin": target_asin,
            "detected_threats": alerts,
            "brand_protection_plan": llm_response.get("parsed_json") or llm_response.get("raw_content")
        }
