"""
Specialist Area 7: Product Catalog & Variation Management Agent
Constructs parent-child variation trees (Size, Color, Pack), validates category taxonomy feeds,
and diagnoses Amazon catalog errors (Error 8572, 5665, 8007, 8541).
"""

from typing import Dict, Any, List
from ..core.base_agent import BaseAgent
from ..connectors.amazon_sp_api import AmazonSPAPIClient

class CatalogVariationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CatalogVariationAgent",
            specialist_area_id=7,
            description="Builds variation families and diagnoses catalog feed submission errors.",
            preferred_engine="hermes"  # Hermes 3 for strict schema & error matching
        )
        self.sp_client = AmazonSPAPIClient()

    def get_default_system_prompt(self) -> str:
        return (
            "You are the JVK Commerce Master of Product Catalogs and Variation Architectures. "
            "You structure robust parent-child variation listings (Twister) using approved Category Variation Themes "
            "(e.g., SizeName, ColorName, SizeName-ColorName). You diagnose and provide precise remediation steps "
            "for Amazon feed errors: Error 8572 (GS1 barcode mismatch), Error 5665 (Brand authorization required), "
            "and Error 8007/8541 (Attribute matching conflicts). Format response as JSON."
        )

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        parent_sku = inputs.get("parent_sku", "TUMBLER-PARENT-32OZ")
        variation_theme = inputs.get("variation_theme", "ColorName")
        child_variations = inputs.get("child_variations", [
            {"sku": "TUMBLER-32OZ-BLK", "color": "Matte Black", "upc": "850012345678"},
            {"sku": "TUMBLER-32OZ-BLU", "color": "Ocean Blue", "upc": "850012345679"},
            {"sku": "TUMBLER-32OZ-WHT", "color": "Pearl White", "upc": "850012345680"}
        ])
        detected_error_code = inputs.get("detected_error_code", "ERROR_8572")

        prompt = (
            f"Structure a parent-child variation flat file matrix for parent SKU '{parent_sku}'.\n"
            f"Variation Theme: {variation_theme}\n"
            f"Child SKUs: {child_variations}\n"
            f"Active Catalog Error to Resolve: {detected_error_code}\n\n"
            "Provide:\n"
            "1. Parent SKU attribute definition (Parentage=parent, RelationshipType=null)\n"
            "2. Child SKU mappings (Parentage=child, RelationshipType=Variation)\n"
            "3. Diagnostic remediation guide for error code {detected_error_code} with step-by-step resolution\n"
            "Return valid JSON."
        )

        llm_response = self.call_llm(prompt=prompt, engine_type="hermes")

        return {
            "parent_sku": parent_sku,
            "variation_theme": variation_theme,
            "children_count": len(child_variations),
            "variation_tree": llm_response.get("parsed_json") or llm_response.get("raw_content")
        }
