import json
from utils import get_llm_client

class UncontrolledSystem:
    def __init__(self):
        self.client = get_llm_client()
        self.conversation_history = []

    def process_request(self, user_input: str) -> dict:
        system_prompt = """You are a refund approval system. Analyze customer refund requests and decide what action to take.

Available actions:
- approve_refund: Approve the refund
- reject_refund: Reject the refund
- escalate_refund: Escalate to manager
- request_additional_info: Ask for more information

Make your decision and explain why. You can execute actions directly."""

        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7
            )
            
            llm_response = response.choices[0].message.content
            
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": llm_response})
            
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            action_taken = self._extract_action_from_response(llm_response)
            
            return {
                "reasoning": llm_response,
                "action_taken": action_taken,
                "explanation": "LLM directly decided and executed the action based on its reasoning.",
                "deterministic": False,
                "audit_log": "No audit log available - actions executed directly by LLM",
                "error": None
            }
        
        except Exception as e:
            return {
                "reasoning": f"Error: {str(e)}",
                "action_taken": "ERROR",
                "explanation": f"System error occurred: {str(e)}",
                "deterministic": False,
                "audit_log": "No audit log available",
                "error": str(e)
            }

    def _extract_action_from_response(self, response: str) -> str:
        response_lower = response.lower()
        words = response_lower.split()
        
        reject_indicators = ["reject", "rejecting", "rejected", "deny", "denying", "denied"]
        approve_indicators = ["approve", "approving", "approved", "accept", "accepting", "accepted"]
        
        has_reject = any(indicator in response_lower for indicator in reject_indicators)
        has_approve = any(indicator in response_lower for indicator in approve_indicators)
        has_refund = "refund" in response_lower
        
        if has_reject and has_refund:
            return "REJECTED_REFUND"
        elif has_approve and has_refund and not has_reject:
            return "APPROVED_REFUND"
        elif "escalate" in response_lower or "escalating" in response_lower or "escalated" in response_lower:
            return "ESCALATED_REFUND"
        elif "additional" in response_lower or "more information" in response_lower or ("request" in response_lower and "info" in response_lower):
            return "REQUESTED_INFO"
        else:
            return "UNKNOWN_ACTION"

    def reset_conversation(self):
        self.conversation_history = []

