"""
Specialist Area 5: PPC Campaign Management Agent (SP, SB & SD)
Performs automated bid optimization using Target ACoS & Conversion Rate elasticity,
automates target harvesting (Search Term -> Exact Match), and negates non-converting spend.
"""

from typing import Dict, Any, List
from ..core.base_agent import BaseAgent
from ..connectors.amazon_ads_api import AmazonAdsClient

class PPCManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="PPCManagerAgent",
            specialist_area_id=5,
            description="Manages Sponsored Products, Brands & Display, bid math, target harvesting, and negative isolation.",
            preferred_engine="quant"  # DeepSeek-R1 for mathematical bid calculations
        )
        self.ads_client = AmazonAdsClient()

    def get_default_system_prompt(self) -> str:
        return (
            "You are the JVK Commerce Elite PPC Advertising Strategist. "
            "You optimize Amazon Sponsored Products, Sponsored Brands, and Sponsored Display campaigns. "
            "You apply rigorous mathematical bid calculations:\n"
            "Optimal Bid = Target ACoS * Average Order Value (AOV) * Conversion Rate (CR).\n"
            "You identify search terms with > 2 orders to harvest into Exact match, and queries with "
            "> 10 clicks and 0 orders to isolate as Negative Exact. Return structured JSON."
        )

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        target_acos = float(inputs.get("target_acos", 0.25))  # 25% Target ACoS
        campaign_type = inputs.get("campaign_type", "SP")
        aov = float(inputs.get("aov", 28.50))  # Average Order Value $28.50

        # Fetch campaign performance & search terms
        reports = self.ads_client.get_campaign_reports(campaign_type.lower())
        campaigns = reports.get("campaigns", [])
        search_terms = self.ads_client.get_search_terms(campaign_id="11223344")

        # Mathematical bid analysis
        harvest_actions = []
        negative_actions = []
        bid_adjustments = []

        for st in search_terms:
            clicks = st["clicks"]
            orders = st["orders"]
            term = st["searchTerm"]
            cost = st["cost"]

            if orders >= 2:
                # Harvest into exact
                cr = orders / clicks if clicks > 0 else 0.05
                calculated_optimal_bid = round(target_acos * aov * cr, 2)
                harvest_actions.append({
                    "action": "HARVEST_TO_EXACT",
                    "term": term,
                    "orders": orders,
                    "clicks": clicks,
                    "current_cpc": st["cpc"],
                    "calculated_optimal_bid": calculated_optimal_bid
                })
            elif clicks >= 10 and orders == 0:
                # Add negative exact
                negative_actions.append({
                    "action": "ADD_NEGATIVE_EXACT",
                    "term": term,
                    "wasted_spend": cost,
                    "clicks": clicks
                })

        prompt = (
            f"Review PPC performance for target ACoS={target_acos*100}%, AOV=${aov:.2f}.\n"
            f"Harvest candidates: {harvest_actions}\n"
            f"Negative candidates: {negative_actions}\n"
            f"Active campaigns: {campaigns}\n\n"
            "Generate an optimization summary with:\n"
            "1. Projected ad spend savings\n"
            "2. High-value harvest recommendations\n"
            "3. Sponsored Display / Sponsored Brands strategy adjustment\n"
            "Return JSON."
        )

        llm_response = self.call_llm(prompt=prompt, engine_type="quant")

        return {
            "target_acos": f"{target_acos*100}%",
            "campaigns_evaluated": len(campaigns),
            "harvest_actions": harvest_actions,
            "negative_actions": negative_actions,
            "optimization_plan": llm_response.get("parsed_json") or llm_response.get("raw_content")
        }
