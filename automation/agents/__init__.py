"""
Export all 15 Specialist E-commerce Agents
"""

from .account_setup_agent import AccountSetupAgent
from .account_manager_agent import MarketplaceAccountManagerAgent
from .listing_optimizer_agent import ListingOptimizerAgent
from .seo_keyword_agent import SEOKeywordAgent
from .ppc_manager_agent import PPCManagerAgent
from .aplus_content_agent import APlusContentAgent
from .catalog_variation_agent import CatalogVariationAgent
from .inventory_forecaster_agent import InventoryForecasterAgent
from .fulfillment_agent import FulfillmentAgent
from .customer_care_agent import CustomerCareAgent
from .account_health_agent import AccountHealthAgent
from .repricer_promo_agent import RepricerPromoAgent
from .growth_expansion_agent import GrowthExpansionAgent
from .audit_reporting_agent import MarketplaceAuditsReportingAgent
from .brand_registry_agent import BrandRegistryAgent

SPECIALIST_AGENT_REGISTRY = {
    1: AccountSetupAgent,
    2: MarketplaceAccountManagerAgent,
    3: ListingOptimizerAgent,
    4: SEOKeywordAgent,
    5: PPCManagerAgent,
    6: APlusContentAgent,
    7: CatalogVariationAgent,
    8: InventoryForecasterAgent,
    9: FulfillmentAgent,
    10: CustomerCareAgent,
    11: AccountHealthAgent,
    12: RepricerPromoAgent,
    13: GrowthExpansionAgent,
    14: MarketplaceAuditsReportingAgent,
    15: BrandRegistryAgent,
}

__all__ = [
    "AccountSetupAgent",
    "MarketplaceAccountManagerAgent",
    "ListingOptimizerAgent",
    "SEOKeywordAgent",
    "PPCManagerAgent",
    "APlusContentAgent",
    "CatalogVariationAgent",
    "InventoryForecasterAgent",
    "FulfillmentAgent",
    "CustomerCareAgent",
    "AccountHealthAgent",
    "RepricerPromoAgent",
    "GrowthExpansionAgent",
    "MarketplaceAuditsReportingAgent",
    "BrandRegistryAgent",
    "SPECIALIST_AGENT_REGISTRY",
]
