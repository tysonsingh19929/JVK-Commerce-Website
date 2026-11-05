"""
Specialist Area 6: A+ Content & Brand Store Management Agent
Designs modular Premium and Standard A+ layouts, cross-sell comparison tables,
and generates generative image briefs (Flux/Midjourney) for visual assets.
"""

from typing import Dict, Any, List
from ..core.base_agent import BaseAgent

class APlusContentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="APlusContentAgent",
            specialist_area_id=6,
            description="Designs high-converting A+ Content layouts, comparison tables, and visual asset generation prompts.",
            preferred_engine="frontier"  # Claude 3.7 for creative design & visual briefs
        )

    def get_default_system_prompt(self) -> str:
        return (
            "You are the JVK Commerce Creative Director for Amazon A+ Content & Brand Stores. "
            "You design modular A+ pages that elevate brand prestige and drive conversion (+5% to +10%). "
            "You structure modules (Brand Story, Header Banners, Technical Specs, 4-Image Feature Grid, "
            "Comparison Table) and produce precise visual prompts for generative image models (Midjourney/Flux). "
            "Ensure compliance with Amazon A+ guidelines (no guarantees, no pricing references). Return JSON."
        )

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        brand_name = inputs.get("brand_name", "JVK Hydration")
        product_line = inputs.get("product_line", "Insulated Travel Tumblers & Water Bottles")
        models_to_compare = inputs.get("models_to_compare", ["32oz Tumbler", "40oz Travel Mug", "24oz Sports Flask"])

        prompt = (
            f"Design an A+ Content architecture and Brand Store wireframe for {brand_name} ({product_line}).\n"
            f"Comparison Models: {', '.join(models_to_compare)}\n\n"
            "Include:\n"
            "1. Recommended 5-Module A+ Layout (Module types, headline copy, paragraph text)\n"
            "2. Comparison Table Matrix (4 attributes across the 3 models)\n"
            "3. Visual Generation Prompts (3 detailed image generation prompts for hero banners and lifestyle shots with lighting, angle, and aspect ratio)\n"
            "4. Brand Store 3-page navigation structure\n"
            "Output as clean JSON."
        )

        llm_response = self.call_llm(prompt=prompt, engine_type="frontier")

        return {
            "brand": brand_name,
            "product_line": product_line,
            "modules_planned": 5,
            "aplus_design_blueprint": llm_response.get("parsed_json") or llm_response.get("raw_content")
        }
