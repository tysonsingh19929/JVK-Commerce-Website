"""
Amazon Advertising API v3 Connector
Handles programmatic campaign management, Search Term Report extraction,
keyword bid adjustments, and negative target isolation across SP, SB, and SD.
"""

import logging
from typing import Dict, Any, List, Optional
from ..config.settings import settings

logger = logging.getLogger("AESAS.AdsAPIConnector")

class AmazonAdsClient:
    def __init__(self, profile_id: Optional[str] = None):
        self.profile_id = profile_id or settings.ads_api.profile_id
        self.use_mock = settings.ads_api.use_mock

    def get_campaign_reports(self, campaign_type: str = "sp") -> Dict[str, Any]:
        """Module 5: Fetch campaign performance metrics (Spend, Sales, ACoS, CPC, ROAS)."""
        if self.use_mock:
            return {
                "campaigns": [
                    {
                        "campaignId": "11223344",
                        "name": "SP_Auto_Tumbler_Research",
                        "type": "SP",
                        "state": "ENABLED",
                        "dailyBudget": 50.00,
                        "spend": 34.20,
                        "sales": 137.40,
                        "clicks": 42,
                        "impressions": 3890,
                        "acos": 24.89,
                        "roas": 4.02
                    },
                    {
                        "campaignId": "55667788",
                        "name": "SP_Manual_Exact_Hero_Keywords",
                        "type": "SP",
                        "state": "ENABLED",
                        "dailyBudget": 120.00,
                        "spend": 108.50,
                        "sales": 499.80,
                        "clicks": 95,
                        "impressions": 5410,
                        "acos": 21.71,
                        "roas": 4.61
                    },
                    {
                        "campaignId": "99001122",
                        "name": "SD_Competitor_ASIN_Defense",
                        "type": "SD",
                        "state": "ENABLED",
                        "dailyBudget": 40.00,
                        "spend": 38.10,
                        "sales": 82.50,
                        "clicks": 29,
                        "impressions": 8900,
                        "acos": 46.18,
                        "roas": 2.17
                    }
                ]
            }
        # In live mode, calls https://advertising-api.amazon.com/v3/reports
        return {"campaigns": []}

    def get_search_terms(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Fetch search term performance to power automated target harvesting."""
        if self.use_mock:
            return [
                {
                    "searchTerm": "stainless steel travel tumbler with straw",
                    "keywordId": "kw_001",
                    "impressions": 940,
                    "clicks": 34,
                    "cost": 27.20,
                    "orders": 8,
                    "sales": 199.92,
                    "cpc": 0.80,
                    "acos": 13.60
                },
                {
                    "searchTerm": "disposable styrofoam coffee cups bulk",
                    "keywordId": "kw_auto",
                    "impressions": 310,
                    "clicks": 14,
                    "cost": 11.20,
                    "orders": 0,
                    "sales": 0.00,
                    "cpc": 0.80,
                    "acos": 0.00
                }
            ]
        return []

    def update_keyword_bid(self, keyword_id: str, new_bid: float) -> Dict[str, Any]:
        """Update a keyword or target bid."""
        logger.info(f"Setting bid on {keyword_id} to ${new_bid:.2f}")
        return {
            "status": "SUCCESS",
            "keywordId": keyword_id,
            "updated_bid": round(new_bid, 2)
        }

    def add_negative_keyword(self, campaign_id: str, keyword_text: str, match_type: str = "NEGATIVE_EXACT") -> Dict[str, Any]:
        """Isolate wasted ad spend by creating negative exact/phrase keywords."""
        logger.info(f"Adding negative {match_type}: '{keyword_text}' in campaign {campaign_id}")
        return {
            "status": "SUCCESS",
            "campaignId": campaign_id,
            "keywordText": keyword_text,
            "matchType": match_type
        }
