"""
Specialist Area 8: Inventory & FBA Forecasting Agent
Calculates Reorder Points (ROP), Economic Order Quantity (EOQ),
Days of Supply (DOS), and monitors Aged Inventory Surcharge risks.
"""

from typing import Dict, Any, List
from ..core.base_agent import BaseAgent
from ..connectors.amazon_sp_api import AmazonSPAPIClient

class InventoryForecasterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="InventoryForecasterAgent",
            specialist_area_id=8,
            description="Forecats FBA stock replenishment, calculates ROP and safety stock, and prevents aged inventory fees.",
            preferred_engine="quant"  # DeepSeek-R1 for statistical forecasting
        )
        self.sp_client = AmazonSPAPIClient()

    def get_default_system_prompt(self) -> str:
        return (
            "You are the JVK Commerce Supply Chain & FBA Inventory Forecasting Scientist. "
            "You analyze sales velocity, lead times, and seasonal spikes. "
            "You calculate:\n"
            "- Reorder Point (ROP) = (Average Daily Sales * Supplier Lead Time) + Safety Stock\n"
            "- Safety Stock = Z-score * std_dev_sales * sqrt(Lead Time)\n"
            "- Days of Supply (DOS) = Fulfillable Units / Daily Sales Velocity\n"
            "Flag any ASIN with DOS < 15 days as HIGH STOCKOUT RISK, and DOS > 180 days as AGED SURCHARGE RISK. "
            "Return output as structured JSON."
        )

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        supplier_lead_time_days = int(inputs.get("lead_time_days", 30))
        safety_buffer_days = int(inputs.get("safety_buffer_days", 14))

        inventory_data = self.sp_client.get_inventory_summaries()
        summaries = inventory_data.get("inventorySummaries", [])

        analyzed_skus = []
        for item in summaries:
            fulfillable = item.get("fulfillableQuantity", 0)
            inbound = item.get("inboundWorkingQuantity", 0)
            # Simulated daily sales velocity based on stock level
            est_daily_sales = max(5, int(fulfillable / max(1, item.get("estimatedDaysOfSupply", 14))))
            days_of_supply = round(fulfillable / est_daily_sales, 1)

            # ROP calculation
            rop = (est_daily_sales * supplier_lead_time_days) + (est_daily_sales * safety_buffer_days)
            needs_reorder = (fulfillable + inbound) <= rop
            suggested_reorder_qty = max(0, rop * 2 - (fulfillable + inbound)) if needs_reorder else 0

            analyzed_skus.append({
                "sku": item.get("sellerSku"),
                "asin": item.get("asin"),
                "fulfillable": fulfillable,
                "inbound": inbound,
                "daily_sales_velocity": est_daily_sales,
                "days_of_supply": days_of_supply,
                "reorder_point": rop,
                "reorder_recommended": needs_reorder,
                "suggested_units_to_order": suggested_reorder_qty,
                "urgency": "CRITICAL" if days_of_supply < 7 else ("WARNING" if days_of_supply < 15 else "HEALTHY")
            })

        prompt = (
            f"Review supply chain forecast for {len(analyzed_skus)} SKUs with lead time={supplier_lead_time_days} days.\n"
            f"SKU Analysis Data: {analyzed_skus}\n\n"
            "Generate:\n"
            "1. Executive Inventory Health Summary\n"
            "2. Prioritized Purchase Order recommendations with unit volumes\n"
            "3. Storage utilization & FBA capacity limit recommendations\n"
            "Format as JSON."
        )

        llm_response = self.call_llm(prompt=prompt, engine_type="quant")

        return {
            "supplier_lead_time_days": supplier_lead_time_days,
            "skus_evaluated": len(analyzed_skus),
            "sku_forecasts": analyzed_skus,
            "executive_recommendation": llm_response.get("parsed_json") or llm_response.get("raw_content")
        }
