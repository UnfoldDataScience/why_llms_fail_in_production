import json
from typing import Dict, Any
from utils import get_llm_client
from execution_engine import ExecutionEngine, ActionRequest

class GovernedSystem:
    def __init__(self):
        self.client = get_llm_client()
        self.execution_engine = ExecutionEngine()

    def process_request(self, user_input: str) -> dict:
        system_prompt = """You are a reasoning component in a governed refund approval system. Your role is ONLY to analyze the request and provide structured reasoning.

You must output a JSON object with this exact structure:
{
    "action": "approve_refund" | "reject_refund" | "escalate_refund" | "request_additional_info",
    "parameters": {
        "order_id": "string",
        "amount": number (if applicable),
        "reason": "string",
        "info_needed": "string" (if action is request_additional_info)
    },
    "reasoning": "Your detailed reasoning for this decision"
}

Available actions and their requirements:
- approve_refund: requires order_id, amount (max 1000), reason (defective_product, wrong_item, not_delivered, cancelled_order)
- reject_refund: requires order_id, reason (outside_return_window, item_used, no_proof, policy_violation)
- escalate_refund: requires order_id, amount (max 5000), reason
- request_additional_info: requires order_id, info_needed

You CANNOT execute actions. You only provide structured reasoning. The execution engine will validate and execute."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            llm_response = response.choices[0].message.content
            
            try:
                structured_output = json.loads(llm_response)
            except json.JSONDecodeError:
                return {
                    "reasoning": llm_response,
                    "action_taken": "ERROR",
                    "explanation": "LLM failed to produce valid JSON. Execution rejected.",
                    "deterministic": True,
                    "audit_log": "Validation failed: Invalid JSON structure",
                    "error": "JSON parsing error"
                }
            
            action = structured_output.get("action", "")
            parameters = structured_output.get("parameters", {})
            reasoning = structured_output.get("reasoning", "No reasoning provided")
            
            action_request = ActionRequest(
                action=action,
                parameters=parameters,
                reasoning=reasoning
            )
            
            execution_result = self.execution_engine.execute(action_request)
            
            audit_log_formatted = "\n".join([
                f"[{entry['timestamp']}] {entry['level']}: {entry['message']}"
                for entry in execution_result.audit_entries
            ])
            
            if execution_result.success:
                explanation = f"LLM provided reasoning. Execution engine validated and executed: {execution_result.message}"
            else:
                explanation = f"LLM provided reasoning. Execution engine rejected: {execution_result.message}"
            
            return {
                "reasoning": reasoning,
                "action_taken": execution_result.action_taken if execution_result.success else "REJECTED",
                "explanation": explanation,
                "deterministic": True,
                "audit_log": audit_log_formatted,
                "error": None
            }
        
        except Exception as e:
            return {
                "reasoning": f"Error: {str(e)}",
                "action_taken": "ERROR",
                "explanation": f"System error occurred: {str(e)}",
                "deterministic": True,
                "audit_log": f"Error: {str(e)}",
                "error": str(e)
            }

