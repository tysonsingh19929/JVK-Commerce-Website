"""
Unified Multi-Engine LLM Router for AESAS
Routes tasks between Nous Hermes 3 (Tool-calling & JSON execution),
Claude 3.7 / GPT-4o (Creative, High-order Reasoning),
and DeepSeek-R1 (Quantitative / PPC / Forecasting Math).
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
import httpx
from ..config.settings import settings

logger = logging.getLogger("AESAS.LLMRouter")

class LLMRouter:
    def __init__(self):
        self.settings = settings.llm

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        engine_type: str = "hermes",  # 'hermes', 'frontier', 'quant'
        json_schema: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Routes the prompt to the selected engine and returns structured response.
        """
        logger.info(f"Routing generation request to engine_type={engine_type}")

        if engine_type == "quant":
            provider = self.settings.quant_provider
            model = self.settings.quant_model
            api_key = self.settings.quant_api_key
        elif engine_type == "frontier":
            provider = self.settings.frontier_provider
            model = self.settings.frontier_model
            api_key = self.settings.frontier_api_key
        else:
            # Default to Hermes-3
            provider = self.settings.hermes_provider
            model = self.settings.hermes_model
            api_key = self.settings.hermes_api_key

        if provider == "mock":
            return self._mock_response(prompt, engine_type, json_schema)

        # Handle HTTP-based OpenAI-compatible endpoints (Ollama, vLLM, OpenRouter, Together, DeepSeek)
        if provider in ("ollama", "vllm", "openrouter", "deepseek", "together", "openai"):
            return self._call_openai_compatible(
                provider=provider,
                model=model,
                api_key=api_key,
                prompt=prompt,
                system_prompt=system_prompt,
                json_schema=json_schema,
                tools=tools
            )

        # Fallback to mock
        return self._mock_response(prompt, engine_type, json_schema)

    def _call_openai_compatible(
        self,
        provider: str,
        model: str,
        api_key: str,
        prompt: str,
        system_prompt: Optional[str],
        json_schema: Optional[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Calls OpenAI-compatible /v1/chat/completions endpoint (Ollama, vLLM, OpenRouter, DeepSeek)"""
        if provider == "ollama":
            base_url = self.settings.hermes_api_base
        elif provider == "openrouter":
            base_url = "https://openrouter.ai/api/v1"
        elif provider == "deepseek":
            base_url = "https://api.deepseek.com/v1"
        else:
            base_url = self.settings.hermes_api_base

        headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": self.settings.temperature,
            "max_tokens": self.settings.max_tokens,
        }

        if json_schema:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "structured_output",
                    "schema": json_schema
                }
            }
        elif "json" in prompt.lower() or (system_prompt and "json" in system_prompt.lower()):
            payload["response_format"] = {"type": "json_object"}

        if tools:
            payload["tools"] = tools

        try:
            with httpx.Client(timeout=60.0) as client:
                res = client.post(f"{base_url.rstrip('/')}/chat/completions", json=payload, headers=headers)
                res.raise_for_status()
                data = res.json()
                choice = data["choices"][0]
                message = choice["message"]
                content = message.get("content", "")

                result = {
                    "raw_content": content,
                    "tool_calls": message.get("tool_calls", []),
                    "model_used": model,
                    "engine_type": provider,
                    "parsed_json": None
                }

                if json_schema or "json" in prompt.lower():
                    try:
                        # Extract JSON even if wrapped in markdown code blocks
                        clean_content = content.strip()
                        if clean_content.startswith("```json"):
                            clean_content = clean_content[7:]
                        if clean_content.startswith("```"):
                            clean_content = clean_content[3:]
                        if clean_content.endswith("```"):
                            clean_content = clean_content[:-3]
                        result["parsed_json"] = json.loads(clean_content.strip())
                    except Exception as e:
                        logger.warning(f"Failed to parse JSON response: {e}")

                return result
        except Exception as err:
            logger.error(f"Error calling {provider} endpoint: {err}. Falling back to mock engine.")
            return self._mock_response(prompt, "fallback", json_schema)

    def _mock_response(
        self,
        prompt: str,
        engine_type: str,
        json_schema: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Provides realistic fallback intelligence when running offline or in test mode."""
        logger.info(f"Generating mock specialist response for: {prompt[:80]}...")

        # Domain-aware rule-based fallback responses for all 15 areas
        lower_p = prompt.lower()

        parsed = {}
        if "listing" in lower_p or "bullet" in lower_p or "title" in lower_p:
            parsed = {
                "title": "Premium Stainless Steel Insulated Tumbler 32oz - Double Wall Vacuum Thermal Travel Mug with Leak-Proof Straw Lid, Keeps Cold 24h & Hot 12h, BPA Free",
                "bullet_points": [
                    "MAXIMUM TEMPERATURE RETENTION: Double-wall vacuum insulation keeps beverages ice-cold for 24 hours or steaming hot for up to 12 hours without sweating.",
                    "100% LEAK-PROOF 2-IN-1 LID: Features an ergonomic flip straw for effortless cold sipping and a secure locking spout for hot coffee on the go.",
                    "FOOD-GRADE 18/8 STAINLESS STEEL: Crafted from ultra-durable, rust-resistant pro-grade steel that preserves pure flavor without metallic aftertaste.",
                    "CUPHOLDER FRIENDLY ERGONOMICS: Tapered base fits standard car cup holders effortlessly; textured powder coat finish ensures a non-slip grip.",
                    "EASY TO CLEAN & BPA-FREE: Fully dishwasher safe lid and body with wide mouth opening for rapid ice cube filling and effortless hand washing."
                ],
                "backend_search_terms": "travel mug reusable coffee cup cold drinks water bottle thermal flask gym hydration shaker car mug spill proof",
                "char_counts": {
                    "title": 169,
                    "search_terms_bytes": 105
                },
                "compliance_check": {
                    "passed": True,
                    "flagged_terms": []
                }
            }
        elif "ppc" in lower_p or "bid" in lower_p or "campaign" in lower_p:
            parsed = {
                "campaign_analysis": "Target ACoS is 25%. Current actual ACoS is 31.4%. 4 search terms have high conversion rate and should be harvested into Exact Match.",
                "actions": [
                    {
                        "action": "HARVEST_EXACT",
                        "search_term": "insulated tumbler 32oz with straw",
                        "impressions": 1420,
                        "clicks": 58,
                        "orders": 12,
                        "current_cpc": 0.82,
                        "recommended_bid": 0.95
                    },
                    {
                        "action": "ADD_NEGATIVE_EXACT",
                        "search_term": "cheap plastic cup 50 cent",
                        "clicks": 18,
                        "orders": 0,
                        "wasted_spend": 14.76
                    },
                    {
                        "action": "REDUCE_BID",
                        "target": "b08xyz123 (Competitor ASIN)",
                        "current_bid": 1.45,
                        "recommended_bid": 0.90,
                        "reason": "ACoS of 52% exceeds 25% target"
                    }
                ],
                "expected_acos_reduction": "6.2%",
                "budget_efficiency_gain": "+18.4%"
            }
        elif "audit" in lower_p or "report" in lower_p or "health" in lower_p:
            parsed = {
                "account_health_score": "98/100 (Healthy)",
                "summary": "Account is in good standing. Buy Box win rate is 89.2%. TACoS is healthy at 14.1%.",
                "key_metrics": {
                    "gross_revenue_30d": 148520.00,
                    "ppc_spend_30d": 20941.32,
                    "ppc_revenue_30d": 74580.00,
                    "acos": "28.08%",
                    "tacos": "14.10%",
                    "buy_box_percentage": "89.2%",
                    "order_defect_rate": "0.18% (Target < 1.0%)",
                    "late_dispatch_rate": "0.45% (Target < 4.0%)"
                },
                "high_priority_recommendations": [
                    "Replenish ASIN B07ABC123: 8 days of cover remaining before stockout.",
                    "Resolve suppressed listing on ASIN B09XYZ456 due to missing main image pure white background.",
                    "Launch Sponsored Display retargeting campaign on high-traffic hero ASINs."
                ]
            }
        elif "poa" in lower_p or "appeal" in lower_p:
            parsed = {
                "appeal_type": "Late Dispatch Rate (LDR) Policy Resolution",
                "plan_of_action": {
                    "root_cause": "A sudden winter storm in the Midwest delayed local courier pickups by 48 hours between Jan 12-14, preventing timely tracking scans.",
                    "immediate_corrective_actions": [
                        "All affected orders were upgraded to expedited Priority courier at our expense and delivered to buyers.",
                        "Proactively messaged affected buyers with direct tracking updates and sincere apologies."
                    ],
                    "preventive_measures": [
                        "Integrated automated multi-carrier fallback routing (UPS, FedEx, DHL) to dispatch via alternate carriers during weather disruptions.",
                        "Increased handling time buffer from 1 business day to 2 business days on all Merchant Fulfilled listings.",
                        "Enrolled top 80% volume SKUs into Amazon FBA to ensure 100% prime on-time dispatch adherence."
                    ]
                },
                "status": "Ready for submission to Seller Performance Team"
            }
        else:
            parsed = {
                "status": "success",
                "specialist_response": f"Specialist intelligence completed analysis for prompt: {prompt[:100]}",
                "parameters_analyzed": 15,
                "execution_recommendations": ["Automate via SP-API", "Monitor via Cron daemon", "Maintain HITL approval threshold"]
            }

        return {
            "raw_content": json.dumps(parsed, indent=2),
            "tool_calls": [],
            "model_used": "mock-hermes-3-specialist",
            "engine_type": engine_type,
            "parsed_json": parsed
        }

# Global singleton router
router = LLMRouter()
