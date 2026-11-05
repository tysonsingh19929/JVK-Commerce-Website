"""
Specialist Area 2: Marketplace Account Management Agent
Performs 24/7 continuous account monitoring, automated case log tracking,
operational triage, and cross-channel sync.
"""

from typing import Dict, Any, List
from ..core.base_agent import BaseAgent
from ..connectors.amazon_sp_api import AmazonSPAPIClient
from ..connectors.headless_browser import HeadlessBrowserClient

class MarketplaceAccountManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MarketplaceAccountManagerAgent",
            specialist_area_id=2,
            description="Manages day-to-day marketplace account operations, case log triage, and status monitoring.",
            preferred_engine="hermes"
        )
        self.sp_client = AmazonSPAPIClient()
        self.browser_client = HeadlessBrowserClient()

    def get_default_system_prompt(self) -> str:
        return (
            "You are the JVK Commerce Specialist for Marketplace Account Management. "
            "You oversee daily operations across global marketplaces (Amazon, Walmart, eBay, Noon, TikTok Shop). "
            "Your tasks include reviewing active case logs, prioritizing support responses, flagging suppressed "
            "listings, and coordinating actions across specialist teams. Provide actionable, concise JSON summaries."
        )

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        case_ids: List[str] = inputs.get("case_ids", ["14285701", "14285992"])

        cases_status = []
        for cid in case_ids:
            case_data = self.browser_client.inspect_case_log(cid)
            cases_status.append(case_data)

        participations = self.sp_client.get_marketplace_participations()

        prompt = (
            f"Review daily operations for {len(cases_status)} active support cases and global marketplace status.\n"
            f"Case details: {cases_status}\n"
            "Generate:\n"
            "1. Triage priority level (HIGH, MEDIUM, LOW) for each case\n"
            "2. Recommended immediate reply or document upload\n"
            "3. Operational daily checklist for account manager\n"
            "Format as structured JSON."
        )

        llm_response = self.call_llm(prompt=prompt, engine_type="hermes")

        return {
            "monitored_marketplaces": len(participations.get("payload", [])),
            "cases_reviewed": cases_status,
            "daily_triage": llm_response.get("parsed_json") or llm_response.get("raw_content")
        }
