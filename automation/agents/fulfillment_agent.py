"""
Specialist Area 9: FBA, FBM & Seller Flex Management Agent
Automates Send-to-Amazon inbound shipment workflows, box content packaging configurations,
FBM carrier rate shopping, and Seller Flex SLA dispatch monitoring.
"""

from typing import Dict, Any, List
from ..core.base_agent import BaseAgent
from ..connectors.amazon_sp_api import AmazonSPAPIClient

class FulfillmentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="FulfillmentAgent",
            specialist_area_id=9,
            description="Coordinates FBA inbound logistics, FBM carrier selection, and Seller Flex SLAs.",
            preferred_engine="hermes"  # Hermes 3 for strict logistics schemas
        )
        self.sp_client = AmazonSPAPIClient()

    def get_default_system_prompt(self) -> str:
        return (
            "You are the JVK Commerce Logistics & Fulfillment Operations Director. "
            "You manage multi-channel fulfillment operations: Amazon FBA Inbound (Send to Amazon API v2024-03-20), "
            "Merchant Fulfilled Network (FBM) carrier rate-shopping via Buy Shipping API, and Seller Flex warehouse "
            "dispatch cutoffs. Ensure 100% On-Time Dispatch SLA and zero carton label non-compliance fees. Format as JSON."
        )

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        fulfillment_mode = inputs.get("fulfillment_mode", "FBA_INBOUND")  # 'FBA_INBOUND', 'FBM', 'SELLER_FLEX'
        shipment_items = inputs.get("items", [
            {"sku": "TUMBLER-32OZ-BLK", "quantity": 500, "units_per_box": 25, "boxes": 20, "weight_lbs_per_box": 22.5},
            {"sku": "TUMBLER-32OZ-BLU", "quantity": 250, "units_per_box": 25, "boxes": 10, "weight_lbs_per_box": 22.5}
        ])
        origin_address = inputs.get("origin_address", {
            "name": "JVK Central Warehouse",
            "city": "Dallas",
            "state": "TX",
            "postal_code": "75201",
            "country_code": "US"
        })

        total_units = sum(item["quantity"] for item in shipment_items)
        total_boxes = sum(item["boxes"] for item in shipment_items)
        total_weight = sum(item["boxes"] * item["weight_lbs_per_box"] for item in shipment_items)

        prompt = (
            f"Generate a Send-to-Amazon Inbound Logistics Plan for {fulfillment_mode}.\n"
            f"Origin: {origin_address}\n"
            f"Total Units: {total_units} across {total_boxes} cartons ({total_weight} lbs total).\n"
            f"Items: {shipment_items}\n\n"
            "Include:\n"
            "1. Box Content Information strategy (2D Barcode vs Feed)\n"
            "2. Amazon Partnered Carrier (UPS/FedEx SPD vs LTL Freight) cost-efficiency recommendation\n"
            "3. Palletization layout (standard 48x40 inch wood GMA pallets, max 72 inch height)\n"
            "4. Seller Flex dispatch schedule and daily cutoff checklist\n"
            "Output as clean JSON."
        )

        llm_response = self.call_llm(prompt=prompt, engine_type="hermes")

        return {
            "fulfillment_mode": fulfillment_mode,
            "total_units": total_units,
            "total_boxes": total_boxes,
            "total_weight_lbs": total_weight,
            "inbound_plan": llm_response.get("parsed_json") or llm_response.get("raw_content")
        }
