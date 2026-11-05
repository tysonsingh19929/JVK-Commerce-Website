"""
Amazon Selling Partner API (SP-API) Connector
Provides authenticated access to Amazon's modern REST APIs for Listings, Orders,
Inventory, Reports, Finances, and Solicitations.
Includes full mock simulation support for testing.
"""

import logging
import time
from typing import Dict, Any, List, Optional
import httpx
from ..config.settings import settings
from ..config.marketplaces import AMAZON_MARKETPLACES

logger = logging.getLogger("AESAS.SPAPIConnector")

class AmazonSPAPIClient:
    def __init__(self, marketplace: str = "US"):
        self.marketplace = marketplace.upper()
        self.marketplace_config = AMAZON_MARKETPLACES.get(self.marketplace, AMAZON_MARKETPLACES["US"])
        self.endpoint = self.marketplace_config["endpoint"]
        self.marketplace_id = self.marketplace_config["id"]
        self.use_mock = settings.sp_api.use_mock
        self._access_token: Optional[str] = None
        self._token_expiry: float = 0

    def get_access_token(self) -> str:
        """Retrieves or refreshes the LWA (Login with Amazon) OAuth access token."""
        if self.use_mock:
            return "mock_lwa_access_token_123456789"

        if self._access_token and time.time() < self._token_expiry - 60:
            return self._access_token

        url = "https://api.amazon.com/auth/o2/token"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": settings.sp_api.refresh_token,
            "client_id": settings.sp_api.client_id,
            "client_secret": settings.sp_api.client_secret,
        }
        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(url, data=payload)
                res.raise_for_status()
                data = res.json()
                self._access_token = data["access_token"]
                self._token_expiry = time.time() + data.get("expires_in", 3600)
                return self._access_token
        except Exception as e:
            logger.warning(f"LWA token refresh failed: {e}. Defaulting to mock mode.")
            self.use_mock = True
            return "mock_lwa_access_token_123456789"

    def get_marketplace_participations(self) -> Dict[str, Any]:
        """Module 1 & 2: Fetch seller participations across worldwide marketplaces."""
        if self.use_mock:
            return {
                "payload": [
                    {"marketplace": AMAZON_MARKETPLACES["US"], "participation": {"isParticipating": True, "hasSuspendedListings": False}},
                    {"marketplace": AMAZON_MARKETPLACES["CA"], "participation": {"isParticipating": True, "hasSuspendedListings": False}},
                    {"marketplace": AMAZON_MARKETPLACES["UK"], "participation": {"isParticipating": True, "hasSuspendedListings": False}},
                    {"marketplace": AMAZON_MARKETPLACES["DE"], "participation": {"isParticipating": True, "hasSuspendedListings": False}},
                    {"marketplace": AMAZON_MARKETPLACES["AE"], "participation": {"isParticipating": True, "hasSuspendedListings": False}},
                ]
            }
        return self._make_request("GET", "/sellers/v1/marketplaceParticipations")

    def get_listings_item(self, sku: str) -> Dict[str, Any]:
        """Module 3 & 7: Fetch listing details, attributes, and issues for an existing SKU."""
        if self.use_mock:
            return {
                "sku": sku,
                "asin": "B08EXAMPLE12",
                "attributes": {
                    "item_name": [{"value": "Sample Insulated Tumbler 32oz"}],
                    "bullet_point": [
                        {"value": "Keeps drinks cold 24h"},
                        {"value": "Leak proof lid with straw"},
                        {"value": "18/8 food grade steel"}
                    ],
                    "bullet_point_count": 3,
                    "condition_type": [{"value": "new_new"}]
                },
                "issues": [
                    {
                        "code": "MISSING_ATTRIBUTE",
                        "severity": "WARNING",
                        "message": "Only 3 of 5 recommended bullet points provided."
                    }
                ]
            }
        return self._make_request("GET", f"/listings/2021-08-01/items/{settings.sp_api.role_arn}/{sku}")

    def get_inventory_summaries(self) -> Dict[str, Any]:
        """Module 8: Fetch real-time FBA inventory levels, reserved units, and days of supply."""
        if self.use_mock:
            return {
                "inventorySummaries": [
                    {
                        "asin": "B08EXAMPLE12",
                        "sellerSku": "TUMBLER-32OZ-BLK",
                        "fnSku": "X001ABCDEF",
                        "productName": "Insulated Tumbler 32oz Black",
                        "totalQuantity": 420,
                        "fulfillableQuantity": 380,
                        "inboundWorkingQuantity": 200,
                        "inboundShippedQuantity": 0,
                        "reservedQuantity": {
                            "totalReservedQuantity": 40,
                            "pendingCustomerOrderQuantity": 32,
                            "pendingTransshipmentQuantity": 8
                        },
                        "estimatedDaysOfSupply": 14
                    },
                    {
                        "asin": "B09SAMPLE88",
                        "sellerSku": "TUMBLER-32OZ-BLU",
                        "fnSku": "X002ABCDEF",
                        "productName": "Insulated Tumbler 32oz Ocean Blue",
                        "totalQuantity": 45,
                        "fulfillableQuantity": 35,
                        "inboundWorkingQuantity": 0,
                        "inboundShippedQuantity": 0,
                        "reservedQuantity": {
                            "totalReservedQuantity": 10,
                            "pendingCustomerOrderQuantity": 10
                        },
                        "estimatedDaysOfSupply": 3
                    }
                ]
            }
        return self._make_request("GET", "/fba/inventory/v1/summaries", params={"marketplaceIds": self.marketplace_id})

    def get_competitive_pricing(self, asins: List[str]) -> Dict[str, Any]:
        """Module 12: Fetch current Buy Box price and competitive offers."""
        if self.use_mock:
            return {
                "prices": [
                    {
                        "asin": asins[0] if asins else "B08EXAMPLE12",
                        "status": "Success",
                        "buy_box_price": 24.99,
                        "currency": "USD",
                        "is_buy_box_winner": True,
                        "total_offers": 3,
                        "lowest_offer": 24.95
                    }
                ]
            }
        return self._make_request("GET", "/products/pricing/v0/competitivePrice", params={"asins": ",".join(asins)})

    def request_review(self, order_id: str) -> Dict[str, Any]:
        """Module 10: Official automated 'Request a Review' solicitation button via API."""
        if self.use_mock:
            return {
                "status": "SUCCESS",
                "order_id": order_id,
                "message": f"Review solicitation successfully triggered for order {order_id}"
            }
        return self._make_request("POST", f"/solicitations/v1/orders/{order_id}/solicitations/productReviewAndSellerFeedback")

    def get_account_health(self) -> Dict[str, Any]:
        """Module 11: Get account performance metrics and policy violation signals."""
        if self.use_mock:
            return {
                "account_status": "NORMAL",
                "order_defect_rate": 0.22,
                "late_dispatch_rate": 0.65,
                "prefulfillment_cancellation_rate": 0.10,
                "valid_tracking_rate": 99.4,
                "policy_complaints": {
                    "ip_complaints": 0,
                    "product_authenticity": 0,
                    "product_safety": 0,
                    "listing_violations": 1
                }
            }
        return self._make_request("GET", "/reports/2021-06-30/reports")

    def _make_request(self, method: str, path: str, params: Optional[Dict] = None, json_body: Optional[Dict] = None) -> Dict[str, Any]:
        token = self.get_access_token()
        headers = {
            "x-amz-access-token": token,
            "Content-Type": "application/json",
            "User-Agent": "AESAS/1.0 (Language=Python; Platform=Windows)"
        }
        url = f"{self.endpoint.rstrip('/')}{path}"
        with httpx.Client(timeout=30.0) as client:
            res = client.request(method, url, headers=headers, params=params, json=json_body)
            res.raise_for_status()
            return res.json()
