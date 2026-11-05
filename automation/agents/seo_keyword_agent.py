"""
Specialist Area 4: SEO & Keyword Research Agent
Performs reverse-ASIN competitor keyword gap analysis, search volume clustering,
and backend indexation auditing.
"""

from typing import Dict, Any, List
from ..core.base_agent import BaseAgent
from ..connectors.keepa_connector import KeepaClient

class SEOKeywordAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="SEOKeywordAgent",
            specialist_area_id=4,
            description="Analyzes competitor search terms, clusters keywords by volume, and identifies indexation gaps.",
            preferred_engine="quant"  # Prefers DeepSeek-R1 / Quant engine for clustering & scoring
        )
        self.keepa = KeepaClient()

    def get_default_system_prompt(self) -> str:
        return (
            "You are the JVK Commerce Master of Amazon SEO & Keyword Research. "
            "You analyze search volumes, calculate keyword opportunity scores, identify competitor gaps, "
            "and cluster keywords into High-Intent Commercial, Long-Tail, and Brand Defense groups. "
            "Always return clean, structured JSON data."
        )

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        target_asin = inputs.get("target_asin", "B08EXAMPLE12")
        competitor_asins = inputs.get("competitor_asins", ["B08COMP001", "B08COMP002", "B08COMP003"])
        seed_keywords = inputs.get("seed_keywords", ["tumbler 32oz", "travel mug", "insulated cup"])

        # Fetch Keepa data for target ASIN
        keepa_data = self.keepa.get_product_data(target_asin)

        prompt = (
            f"Perform an in-depth Amazon SEO & Keyword Gap Analysis for ASIN {target_asin}.\n"
            f"Competitor ASINs: {', '.join(competitor_asins)}\n"
            f"Seed Keywords: {', '.join(seed_keywords)}\n\n"
            "Generate:\n"
            "1. Top 5 High-Volume Root Keywords (estimated search volume & opportunity score 1-100)\n"
            "2. Top 5 Long-Tail Conversion Keywords (high conversion intent, lower competition)\n"
            "3. Competitor Keyword Gap (keywords top competitors rank for that target ASIN misses)\n"
            "4. Search Query Performance (SQP) recommendation\n"
            "Return valid JSON format."
        )

        llm_response = self.call_llm(prompt=prompt, engine_type="quant")

        return {
            "target_asin": target_asin,
            "competitor_asins": competitor_asins,
            "sales_rank": keepa_data.get("stats", {}).get("current_sales_rank"),
            "keyword_clusters": llm_response.get("parsed_json") or llm_response.get("raw_content")
        }
