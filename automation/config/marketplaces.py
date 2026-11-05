"""
Marketplace IDs, Endpoint URLs, and Region Configurations for Global E-commerce
Supported Marketplaces: Amazon (NA, EU, FE, ME), Walmart, eBay, Noon, TikTok Shop.
"""

from typing import Dict, Any

AMAZON_MARKETPLACES: Dict[str, Dict[str, Any]] = {
    # North America
    "US": {
        "name": "United States",
        "id": "ATVPDKIKX0DER",
        "region": "na",
        "endpoint": "https://sellingpartnerapi-na.amazon.com",
        "currency": "USD",
        "domain": "amazon.com"
    },
    "CA": {
        "name": "Canada",
        "id": "A2EUQ1WTGCTBG2",
        "region": "na",
        "endpoint": "https://sellingpartnerapi-na.amazon.com",
        "currency": "CAD",
        "domain": "amazon.ca"
    },
    "MX": {
        "name": "Mexico",
        "id": "A1AM78C64UM0Y8",
        "region": "na",
        "endpoint": "https://sellingpartnerapi-na.amazon.com",
        "currency": "MXN",
        "domain": "amazon.com.mx"
    },
    # Europe
    "UK": {
        "name": "United Kingdom",
        "id": "A1F83G8C2ARO7P",
        "region": "eu",
        "endpoint": "https://sellingpartnerapi-eu.amazon.com",
        "currency": "GBP",
        "domain": "amazon.co.uk"
    },
    "DE": {
        "name": "Germany",
        "id": "A1PA6795UKMFR9",
        "region": "eu",
        "endpoint": "https://sellingpartnerapi-eu.amazon.com",
        "currency": "EUR",
        "domain": "amazon.de"
    },
    "FR": {
        "name": "France",
        "id": "A13V1IB3VIYZZH",
        "region": "eu",
        "endpoint": "https://sellingpartnerapi-eu.amazon.com",
        "currency": "EUR",
        "domain": "amazon.fr"
    },
    "IT": {
        "name": "Italy",
        "id": "APJ6JRA9NG5V4",
        "region": "eu",
        "endpoint": "https://sellingpartnerapi-eu.amazon.com",
        "currency": "EUR",
        "domain": "amazon.it"
    },
    "ES": {
        "name": "Spain",
        "id": "A1RKKUPIHCS9HS",
        "region": "eu",
        "endpoint": "https://sellingpartnerapi-eu.amazon.com",
        "currency": "EUR",
        "domain": "amazon.es"
    },
    # Middle East
    "AE": {
        "name": "United Arab Emirates",
        "id": "A2VIGQ35RCS4UG",
        "region": "eu",
        "endpoint": "https://sellingpartnerapi-eu.amazon.com",
        "currency": "AED",
        "domain": "amazon.ae"
    },
    "SA": {
        "name": "Saudi Arabia",
        "id": "A17E79C6D8DWNP",
        "region": "eu",
        "endpoint": "https://sellingpartnerapi-eu.amazon.com",
        "currency": "SAR",
        "domain": "amazon.sa"
    },
    # Far East & Australia
    "AU": {
        "name": "Australia",
        "id": "A39IBJ37TRP1C6",
        "region": "fe",
        "endpoint": "https://sellingpartnerapi-fe.amazon.com",
        "currency": "AUD",
        "domain": "amazon.com.au"
    },
    "JP": {
        "name": "Japan",
        "id": "A1VC38T7YXB528",
        "region": "fe",
        "endpoint": "https://sellingpartnerapi-fe.amazon.com",
        "currency": "JPY",
        "domain": "amazon.co.jp"
    }
}

AMAZON_AWS_REGIONS = {
    "na": "us-east-1",
    "eu": "eu-west-1",
    "fe": "us-west-2"
}

OTHER_MARKETPLACES = {
    "WALMART_US": {
        "name": "Walmart US",
        "api_endpoint": "https://marketplace.walmartapis.com/v3",
        "currency": "USD"
    },
    "NOON_UAE": {
        "name": "Noon UAE",
        "api_endpoint": "https://api.noon.partners",
        "currency": "AED"
    },
    "NOON_KSA": {
        "name": "Noon KSA",
        "api_endpoint": "https://api.noon.partners",
        "currency": "SAR"
    },
    "TIKTOK_SHOP_US": {
        "name": "TikTok Shop US",
        "api_endpoint": "https://open-api.tiktokglobalshop.com",
        "currency": "USD"
    },
    "EBAY_US": {
        "name": "eBay US",
        "api_endpoint": "https://api.ebay.com",
        "currency": "USD"
    }
}
