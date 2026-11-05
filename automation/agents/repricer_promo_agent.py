"""
Specialist Area 12: Promotions, Deals & Pricing Strategies Agent
Implements algorithmic dynamic repricing to capture Buy Box share, enforces minimum margin floors,
and schedules Prime Exclusive Discounts and Coupons.
"""

from typing import Dict, Any, List
from ..core.base_agent import BaseAgent
from ..connectors.amazon_sp_api import AmazonSPAPIClient

class RepricerPromoAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="RepricerPromoAgent",
            specialist_area_id=12,
            description="Optimizes Buy Box ownership with dynamic repricing algorithms and promotional strategies.",
            preferred_engine="hermes"  # Fast deterministic rule-execution
        )
        self.sp_client = AmazonSPAPIClient()

    def get_default_system_prompt(self) -> str:
        return (
            "You are the JVK Commerce Pricing Strategist & Promotional Architect. "
            "You maximize revenue and Buy Box ownership while strictly protecting profit margins. "
            "You calculate competitive prices (matching Buy Box winner or undercutting by $0.01 only when "
            "above minimum floor price). You design seasonal promotional stacks (Coupons + Prime Exclusive Discounts) "
            "and prevent Amazon listing suppression from off-Amazon price disparity. Return output as JSON."
        )

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        asin = inputs.get("asin", "B08EXAMPLE12")
        current_price = float(inputs.get("current_price", 24.99))
        min_floor_price = float(inputs.get("min_floor_price", 21.50))
        max_ceiling_price = float(inputs.get("max_ceiling_price", 29.99))
        promo_type = inputs.get("promo_type", "PRIME_EXCLUSIVE_DISCOUNT")  # 'COUPON', 'LIGHTNING_DEAL'

        pricing_data = self.sp_client.get_competitive_pricing([asin])
        comp_price_info = pricing_data.get("prices", [{}])[0]
        buy_box_price = comp_price_info.get("buy_box_price", current_price)
        lowest_offer = comp_price_info.get("lowest_offer", current_price)
        is_winner = comp_price_info.get("is_buy_box_winner", True)

        # Repricing algorithm
        recommended_price = current_price
        reason = "Maintaining current price."

        if not is_winner:
            target = lowest_offer - 0.01
            if target >= min_floor_price:
                recommended_price = round(target, 2)
                reason = f"Undercutting lowest offer by $0.01 to reclaim Buy Box while staying above floor (${min_floor_price:.2f})."
            else:
                recommended_price = min_floor_price
                reason = f"Held at minimum profit floor (${min_floor_price:.2f}) to protect margin."
        else:
            # If we own the Buy Box, can we optimize upwards slightly?
            if buy_box_price < max_ceiling_price and buy_box_price == lowest_offer:
                recommended_price = current_price
                reason = "Dominating Buy Box at optimal target price."

        prompt = (
            f"Review pricing and promotion strategy for ASIN {asin}.\n"
            f"Current Price: ${current_price:.2f}, Floor: ${min_floor_price:.2f}, Ceiling: ${max_ceiling_price:.2f}\n"
            f"Buy Box Price: ${buy_box_price:.2f}, Lowest Competitor: ${lowest_offer:.2f}, Is Winner: {is_winner}\n"
            f"Algorithmic Price: ${recommended_price:.2f} ({reason})\n"
            f"Requested Promo: {promo_type}\n\n"
            "Provide:\n"
            "1. Repricing decision validation\n"
            "2. Promotional configuration (e.g. 10% coupon vs Prime Exclusive Discount timing)\n"
            "3. Price elasticity & profit impact forecast\n"
            "Format as structured JSON."
        )

        llm_response = self.call_llm(prompt=prompt, engine_type="hermes")

        return {
            "asin": asin,
            "current_price": current_price,
            "recommended_price": recommended_price,
            "is_buy_box_winner": is_winner,
            "pricing_strategy": llm_response.get("parsed_json") or llm_response.get("raw_content")
        }
