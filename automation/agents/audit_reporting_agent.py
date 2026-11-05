"""
Specialist Area 14: Marketplace Audits & Reporting Agent
Conducts comprehensive 360-degree account audits, analyzes P&L unit economics,
compares TACoS vs ACoS, and computes Listing Quality Scores (LQS).
"""

from typing import Dict, Any, List
from ..core.base_agent import BaseAgent
from ..connectors.amazon_sp_api import AmazonSPAPIClient
from ..connectors.amazon_ads_api import AmazonAdsClient

class MarketplaceAuditsReportingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MarketplaceAuditsReportingAgent",
            specialist_area_id=14,
            description="Performs complete 360-degree account performance audits and generates executive P&L reports.",
            preferred_engine="quant"  # DeepSeek-R1 / Quant for financial balancing & metric audits
        )
        self.sp_client = AmazonSPAPIClient()
        self.ads_client = AmazonAdsClient()

    def get_default_system_prompt(self) -> str:
        return (
            "You are the JVK Commerce Senior Partner for Marketplace Audits & Executive Reporting. "
            "You deliver rigorous, boardroom-grade financial and operational audits for multi-million dollar brands. "
            "You calculate:\n"
            "- ACoS = Ad Spend / Ad Sales\n"
            "- TACoS = Ad Spend / Total Gross Sales (healthy benchmark: 10% - 15%)\n"
            "- Net Contribution Margin = Total Sales - COGS - Amazon Referral/FBA Fees - Ad Spend - Returns\n"
            "- Listing Quality Score (LQS) based on Title, 5 Bullets, Image Count (>=7), A+ presence, Reviews (>=4.3 stars).\n"
            "Format output as structured JSON."
        )

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        gross_sales = float(inputs.get("gross_sales_30d", 148520.00))
        ad_spend = float(inputs.get("ad_spend_30d", 20941.32))
        ad_sales = float(inputs.get("ad_sales_30d", 74580.00))
        cogs = float(inputs.get("cogs_30d", 37130.00))
        fba_fees = float(inputs.get("fba_fees_30d", 41585.60))
        refunds = float(inputs.get("refunds_30d", 4455.60))

        # Financial metrics
        acos = round((ad_spend / ad_sales) * 100, 2) if ad_sales > 0 else 0.0
        tacos = round((ad_spend / gross_sales) * 100, 2) if gross_sales > 0 else 0.0
        net_profit = round(gross_sales - refunds - cogs - fba_fees - ad_spend, 2)
        net_margin = round((net_profit / gross_sales) * 100, 2) if gross_sales > 0 else 0.0

        health = self.sp_client.get_account_health()

        financial_snapshot = {
            "gross_sales": gross_sales,
            "refunds": refunds,
            "ad_spend": ad_spend,
            "ad_sales": ad_sales,
            "fba_referral_fees": fba_fees,
            "cogs": cogs,
            "net_profit": net_profit,
            "net_margin_percent": f"{net_margin}%",
            "acos_percent": f"{acos}%",
            "tacos_percent": f"{tacos}%",
            "tacos_status": "HEALTHY" if tacos <= 15.0 else ("WARNING" if tacos <= 20.0 else "UNSUSTAINABLE")
        }

        prompt = (
            f"Generate an Executive 360-Degree Performance Audit Report.\n"
            f"Financial Snapshot: {financial_snapshot}\n"
            f"Account Health Signals: {health}\n\n"
            "Include:\n"
            "1. Executive Summary & Boardroom Narrative\n"
            "2. Advertising Efficiency Assessment (ACoS vs TACoS balance)\n"
            "3. Top 3 Revenue Leakage Drivers\n"
            "4. 90-Day Value Creation Roadmap (specific steps to boost net margin by 3-5%)\n"
            "Format as structured JSON."
        )

        llm_response = self.call_llm(prompt=prompt, engine_type="quant")

        return {
            "financial_kpis": financial_snapshot,
            "account_health": health,
            "audit_report": llm_response.get("parsed_json") or llm_response.get("raw_content")
        }
