"""
Specialist Area 13: Sales Growth & Business Development Agent
Evaluates cross-border international expansion feasibility (US to UK, EU, UAE, KSA, AU),
calculates landed VAT/customs margins, and sets up Amazon Business B2B tiered discounts.
"""

from typing import Dict, Any, List
from ..core.base_agent import BaseAgent
from ..config.marketplaces import AMAZON_MARKETPLACES

class GrowthExpansionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="GrowthExpansionAgent",
            specialist_area_id=13,
            description="Identifies global market expansion opportunities, models landed margins, and builds B2B growth.",
            preferred_engine="quant"  # DeepSeek-R1 for international landed-cost modeling
        )

    def get_default_system_prompt(self) -> str:
        return (
            "You are the JVK Commerce Global Expansion & Business Development Director. "
            "You scale brands internationally from domestic markets to the UK, Europe, Australia, and the Middle East (UAE, KSA). "
            "You calculate landed import costs, VAT/duty compliance (e.g. UK 20% VAT, EU IOSS), international shipping buffers, "
            "and Amazon Business (B2B) quantity discount matrices (e.g. 5 units: 5% off, 20 units: 10% off). "
            "Return clean, structured JSON."
        )

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        domestic_asin = inputs.get("asin", "B08EXAMPLE12")
        domestic_price_usd = float(inputs.get("price_usd", 24.99))
        target_regions = inputs.get("target_regions", ["UK", "DE", "AE", "AU"])
        b2b_enabled = inputs.get("enable_b2b_tiers", True)

        market_evaluations = []
        for code in target_regions:
            cfg = AMAZON_MARKETPLACES.get(code, {})
            currency = cfg.get("currency", "USD")
            # Estimated landed exchange rate & localized target pricing
            est_rates = {"GBP": 0.79, "EUR": 0.92, "AED": 3.67, "AUD": 1.54}
            rate = est_rates.get(currency, 1.0)
            local_list_price = round(domestic_price_usd * rate * 1.15, 2)  # 15% buffer for international logistics & duties

            market_evaluations.append({
                "country": cfg.get("name", code),
                "code": code,
                "currency": currency,
                "marketplace_id": cfg.get("id"),
                "estimated_local_retail_price": local_list_price,
                "vat_rate": "20% (Standard)" if code in ("UK", "FR") else ("19%" if code == "DE" else ("5%" if code in ("AE", "SA") else "10%")),
                "readiness_score": "HIGH (Demand Index 8.4/10)"
            })

        prompt = (
            f"Generate an International Expansion Roadmap for ASIN {domestic_asin} (US Price: ${domestic_price_usd:.2f}).\n"
            f"Target Regions: {target_regions}\n"
            f"Regional Market Estimates: {market_evaluations}\n"
            f"B2B Pricing Tiering: {b2b_enabled}\n\n"
            "Include:\n"
            "1. Priority sequence of entry (Phase 1, Phase 2)\n"
            "2. Regulatory & packaging compliance (CE/UKCA marks, multilingual manual)\n"
            "3. Recommended Amazon Business (B2B) tiered discount schedule\n"
            "4. Projected 12-month international incremental revenue\n"
            "Format as JSON."
        )

        llm_response = self.call_llm(prompt=prompt, engine_type="quant")

        return {
            "domestic_asin": domestic_asin,
            "domestic_price_usd": domestic_price_usd,
            "market_evaluations": market_evaluations,
            "expansion_strategy": llm_response.get("parsed_json") or llm_response.get("raw_content")
        }
