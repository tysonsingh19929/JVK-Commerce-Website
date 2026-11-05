"""
Specialist Area 3: Product Listing Creation & Optimisation Agent
Generates high-converting, policy-compliant Amazon listings with strict
character/byte limits (Title < 200 chars, Bullets < 5x 250 chars, Backend Search Terms < 249 bytes).
"""

from typing import Dict, Any, List
from ..core.base_agent import BaseAgent
from ..connectors.amazon_sp_api import AmazonSPAPIClient

class ListingOptimizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ListingOptimizerAgent",
            specialist_area_id=3,
            description="Creates and optimizes compliant, high-ranking product listings with byte & character constraints.",
            preferred_engine="frontier"  # Prefers Claude 3.7 / Frontier for copywriting
        )
        self.sp_client = AmazonSPAPIClient()

    def get_default_system_prompt(self) -> str:
        return (
            "You are the JVK Commerce Elite E-commerce Copywriter and Listing Optimization Specialist. "
            "You create compelling, SEO-rich product titles, five benefit-driven bullet points, and "
            "compliant backend search terms under strict Amazon rules:\n"
            "- Title: Under 200 characters, no subjective claims ('Best', 'Top #1'), capitalizes major words.\n"
            "- Bullet Points: Exactly 5 bullets, each starting with a capitalized benefit header.\n"
            "- Backend Search Terms: Under 249 bytes, space-separated, no punctuation, no repeated words, no competitor brand names.\n"
            "- Compliance: No prohibited medical, environmental (e.g. uncertified 'biodegradable'), or pesticide claims.\n"
            "Output must be structured JSON."
        )

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        product_name = inputs.get("product_name", "Stainless Steel Insulated Tumbler 32oz")
        brand_name = inputs.get("brand_name", "JVK Hydration")
        features = inputs.get("features", [
            "Double-wall vacuum insulation",
            "Keeps cold 24 hours, hot 12 hours",
            "2-in-1 leak-proof lid with flip straw",
            "18/8 food-grade stainless steel",
            "Fits standard car cup holders",
            "Dishwasher safe"
        ])
        target_keywords = inputs.get("target_keywords", [
            "insulated tumbler 32oz",
            "travel coffee mug with straw",
            "leak proof water bottle",
            "stainless steel thermal cup"
        ])

        prompt = (
            f"Generate an optimized Amazon product listing for:\n"
            f"Brand: {brand_name}\n"
            f"Product: {product_name}\n"
            f"Key Features: {', '.join(features)}\n"
            f"Primary Keywords to Index: {', '.join(target_keywords)}\n\n"
            "Produce structured JSON with fields:\n"
            "- title (string, max 200 chars)\n"
            "- bullet_points (array of exactly 5 strings)\n"
            "- backend_search_terms (string, space-separated, strictly <= 249 bytes)\n"
            "- compliance_check (object with 'passed' bool and 'flagged_terms' array)\n"
        )

        llm_response = self.call_llm(prompt=prompt, engine_type="frontier")
        parsed = llm_response.get("parsed_json") or {}

        title = parsed.get("title", f"{brand_name} {product_name}")
        search_terms = parsed.get("backend_search_terms", "")
        bullets = parsed.get("bullet_points", [])

        # Strict validation
        validation = {
            "title_char_count": len(title),
            "title_valid": len(title) <= 200,
            "bullets_count": len(bullets),
            "search_terms_bytes": len(search_terms.encode("utf-8")),
            "search_terms_valid": len(search_terms.encode("utf-8")) <= 249
        }

        return {
            "brand": brand_name,
            "product_name": product_name,
            "listing_content": parsed,
            "validation_metrics": validation,
            "engine_used": llm_response.get("model_used")
        }
