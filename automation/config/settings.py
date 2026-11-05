"""
Settings and Environment Configuration for AESAS (Autonomous E-Commerce Specialist Automation System)
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class LLMSettings:
    # Primary Specialist / Tool Calling Engine: Hermes 3
    hermes_provider: str = os.getenv("HERMES_PROVIDER", "mock")  # 'ollama', 'vllm', 'openrouter', 'mock'
    hermes_model: str = os.getenv("HERMES_MODEL", "hermes3:8b")
    hermes_api_base: str = os.getenv("HERMES_API_BASE", "http://localhost:11434/v1")
    hermes_api_key: str = os.getenv("HERMES_API_KEY", "")

    # Frontier Creative & Complex Reasoning Engine: Claude / GPT-4o
    frontier_provider: str = os.getenv("FRONTIER_PROVIDER", "mock")  # 'anthropic', 'openai', 'openrouter', 'mock'
    frontier_model: str = os.getenv("FRONTIER_MODEL", "claude-3-7-sonnet-20250219")
    frontier_api_key: str = os.getenv("ANTHROPIC_API_KEY", os.getenv("OPENAI_API_KEY", ""))

    # Algorithmic & Quantitative Engine: DeepSeek-R1 / o3-mini
    quant_provider: str = os.getenv("QUANT_PROVIDER", "mock")  # 'deepseek', 'openai', 'openrouter', 'mock'
    quant_model: str = os.getenv("QUANT_MODEL", "deepseek-reasoner")
    quant_api_key: str = os.getenv("DEEPSEEK_API_KEY", os.getenv("OPENAI_API_KEY", ""))

    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "4096"))

@dataclass
class AmazonSPAPISettings:
    client_id: str = os.getenv("SP_API_CLIENT_ID", "mock_client_id")
    client_secret: str = os.getenv("SP_API_CLIENT_SECRET", "mock_client_secret")
    refresh_token: str = os.getenv("SP_API_REFRESH_TOKEN", "mock_refresh_token")
    aws_access_key: str = os.getenv("SP_API_AWS_ACCESS_KEY", "mock_access_key")
    aws_secret_key: str = os.getenv("SP_API_AWS_SECRET_KEY", "mock_secret_key")
    role_arn: str = os.getenv("SP_API_ROLE_ARN", "arn:aws:iam::123456789012:role/SPAPIRole")
    use_mock: bool = os.getenv("SP_API_USE_MOCK", "true").lower() in ("true", "1", "yes")

@dataclass
class AmazonAdsSettings:
    client_id: str = os.getenv("ADS_CLIENT_ID", "mock_ads_client_id")
    client_secret: str = os.getenv("ADS_CLIENT_SECRET", "mock_ads_client_secret")
    refresh_token: str = os.getenv("ADS_REFRESH_TOKEN", "mock_ads_refresh_token")
    profile_id: str = os.getenv("ADS_PROFILE_ID", "mock_profile_id")
    use_mock: bool = os.getenv("ADS_USE_MOCK", "true").lower() in ("true", "1", "yes")

@dataclass
class KeepaSettings:
    api_key: str = os.getenv("KEEPA_API_KEY", "mock_keepa_key")
    use_mock: bool = os.getenv("KEEPA_USE_MOCK", "true").lower() in ("true", "1", "yes")

@dataclass
class SystemSettings:
    llm: LLMSettings = field(default_factory=LLMSettings)
    sp_api: AmazonSPAPISettings = field(default_factory=AmazonSPAPISettings)
    ads_api: AmazonAdsSettings = field(default_factory=AmazonAdsSettings)
    keepa: KeepaSettings = field(default_factory=KeepaSettings)
    default_marketplace: str = os.getenv("DEFAULT_MARKETPLACE", "US")
    output_dir: str = os.getenv("OUTPUT_DIR", "automation/data")

# Singleton settings instance
settings = SystemSettings()
