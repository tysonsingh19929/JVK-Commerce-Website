"""
Specialist Area 10: Order & Customer Service Management Agent
Automates 'Request a Review' solicitation triggers, performs sentiment analysis on buyer messages,
drafts policy-compliant responses, and compiles Safe-T claim reimbursement evidence.
"""

from typing import Dict, Any, List
from ..core.base_agent import BaseAgent
from ..connectors.amazon_sp_api import AmazonSPAPIClient

class CustomerCareAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CustomerCareAgent",
            specialist_area_id=10,
            description="Manages customer communications under strict Amazon guidelines and automates review requests.",
            preferred_engine="hermes"
        )
        self.sp_client = AmazonSPAPIClient()

    def get_default_system_prompt(self) -> str:
        return (
            "You are the JVK Commerce Customer Experience & Policy Compliance Lead. "
            "You handle buyer communications under strict Amazon Communication Guidelines:\n"
            "- NEVER include external links, phone numbers, or email addresses.\n"
            "- NEVER incentivize positive reviews or request review modification.\n"
            "- Maintain an empathetic, professional, and resolution-oriented tone.\n"
            "- Identify opportunities to trigger the official 'Request a Review' Solicitations API.\n"
            "- Compile evidence for Safe-T claims when buyers return empty boxes or incorrect items. Return JSON."
        )

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        incoming_message = inputs.get("incoming_message", "Hello, my tumbler arrived with a chipped lid. Can I get a replacement?")
        order_id = inputs.get("order_id", "114-9876543-1234567")
        buyer_name = inputs.get("buyer_name", "Sarah M.")
        delivered_days_ago = int(inputs.get("delivered_days_ago", 6))

        # Check review solicitation eligibility (between 5 and 30 days post-delivery)
        solicitation_result = None
        if 5 <= delivered_days_ago <= 30:
            solicitation_result = self.sp_client.request_review(order_id)

        prompt = (
            f"Analyze and respond to this customer service inquiry for Order #{order_id}:\n"
            f"Buyer: {buyer_name}\n"
            f"Customer Message: '{incoming_message}'\n"
            f"Days since delivery: {delivered_days_ago}\n\n"
            "Provide:\n"
            "1. Sentiment Analysis (Positive, Neutral, Negative, Frustrated)\n"
            "2. Intent Classification (Damaged in Transit, Missing Part, How to Use, Return Request)\n"
            "3. Amazon Policy-Compliant Draft Response (Ready to send)\n"
            "4. Immediate resolution action (e.g. Free replacement order, partial refund, carrier claim)\n"
            "Return valid JSON."
        )

        llm_response = self.call_llm(prompt=prompt, engine_type="hermes")

        return {
            "order_id": order_id,
            "buyer_name": buyer_name,
            "solicitation_triggered": solicitation_result,
            "customer_service_resolution": llm_response.get("parsed_json") or llm_response.get("raw_content")
        }
