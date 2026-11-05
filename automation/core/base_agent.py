"""
Base Agent Class for all 15 Specialist E-commerce Modules
Provides standardized execution lifecycle, logging, tool registration, and structured metrics.
"""

import json
import logging
import os
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from .llm_router import router
from ..config.settings import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

class BaseAgent(ABC):
    def __init__(
        self,
        name: str,
        specialist_area_id: int,
        description: str,
        preferred_engine: str = "hermes",  # 'hermes', 'frontier', 'quant'
        system_prompt: Optional[str] = None
    ):
        self.name = name
        self.specialist_area_id = specialist_area_id
        self.description = description
        self.preferred_engine = preferred_engine
        self.system_prompt = system_prompt or self.get_default_system_prompt()
        self.logger = logging.getLogger(f"AESAS.{self.name}")
        self.tools: Dict[str, Any] = {}

    @abstractmethod
    def get_default_system_prompt(self) -> str:
        """Returns the specialized system prompt for this agent."""
        pass

    @abstractmethod
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Core execution logic implemented by each specialist agent."""
        pass

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the agent workflow with timing, audit logging, and exception resilience.
        """
        start_time = time.time()
        self.logger.info(f"Starting execution for Specialist Area #{self.specialist_area_id}: {self.name}")

        try:
            result = self.execute(inputs)
            duration = round(time.time() - start_time, 2)
            self.logger.info(f"Completed {self.name} successfully in {duration}s")

            wrapped_result = {
                "agent_name": self.name,
                "specialist_area_id": self.specialist_area_id,
                "status": "success",
                "duration_seconds": duration,
                "engine_used": self.preferred_engine,
                "output": result
            }

            self._persist_audit_log(wrapped_result)
            return wrapped_result

        except Exception as e:
            duration = round(time.time() - start_time, 2)
            self.logger.error(f"Execution failed in {self.name} after {duration}s: {e}", exc_info=True)
            return {
                "agent_name": self.name,
                "specialist_area_id": self.specialist_area_id,
                "status": "error",
                "error_message": str(e),
                "duration_seconds": duration,
                "engine_used": self.preferred_engine,
                "output": None
            }

    def call_llm(
        self,
        prompt: str,
        engine_type: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Calls the configured intelligence engine with the agent's system prompt."""
        engine = engine_type or self.preferred_engine
        return router.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            engine_type=engine,
            json_schema=json_schema,
            tools=tools
        )

    def register_tool(self, name: str, func: Any):
        """Registers a Python function as an executable tool for the agent."""
        self.tools[name] = func
        self.logger.debug(f"Registered tool: {name}")

    def _persist_audit_log(self, data: Dict[str, Any]):
        """Saves execution logs to the output directory for traceability."""
        try:
            out_dir = settings.output_dir
            os.makedirs(out_dir, exist_ok=True)
            log_path = os.path.join(out_dir, f"audit_{self.name.lower().replace(' ', '_')}.json")
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as err:
            self.logger.warning(f"Could not save audit log: {err}")
