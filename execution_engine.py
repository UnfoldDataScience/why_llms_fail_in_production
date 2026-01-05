from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel, ValidationError

class ActionRequest(BaseModel):
    action: str
    parameters: Dict[str, Any]
    reasoning: str

class ExecutionResult(BaseModel):
    success: bool
    action_taken: Optional[str]
    message: str
    audit_entries: List[Dict[str, Any]]

class ExecutionEngine:
    ALLOWED_ACTIONS = {
        "approve_refund": {
            "required_params": ["order_id", "amount", "reason"],
            "max_amount": 1000.0,
            "allowed_reasons": ["defective_product", "wrong_item", "not_delivered", "cancelled_order"]
        },
        "reject_refund": {
            "required_params": ["order_id", "reason"],
            "allowed_reasons": ["outside_return_window", "item_used", "no_proof", "policy_violation"]
        },
        "escalate_refund": {
            "required_params": ["order_id", "amount", "reason"],
            "max_amount": 5000.0
        },
        "request_additional_info": {
            "required_params": ["order_id", "info_needed"]
        }
    }

    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []

    def _add_audit_entry(self, level: str, message: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        self.audit_log.append(entry)

    def _validate_action(self, action_request: ActionRequest) -> Tuple[bool, Optional[str]]:
        action = action_request.action.lower()
        
        if action not in self.ALLOWED_ACTIONS:
            return False, f"Action '{action}' is not in allowed actions list"
        
        action_config = self.ALLOWED_ACTIONS[action]
        params = action_request.parameters
        
        for required_param in action_config["required_params"]:
            if required_param not in params:
                return False, f"Missing required parameter: {required_param}"
        
        if "max_amount" in action_config:
            amount = params.get("amount", 0)
            if isinstance(amount, str):
                try:
                    amount = float(amount)
                except ValueError:
                    return False, f"Invalid amount format: {amount}"
            if amount > action_config["max_amount"]:
                return False, f"Amount {amount} exceeds maximum {action_config['max_amount']}"
        
        if "allowed_reasons" in action_config:
            reason = params.get("reason", "").lower()
            if reason not in [r.lower() for r in action_config["allowed_reasons"]]:
                return False, f"Reason '{reason}' not in allowed reasons: {action_config['allowed_reasons']}"
        
        return True, None

    def execute(self, action_request: ActionRequest) -> ExecutionResult:
        self.audit_log = []
        
        self._add_audit_entry("INFO", f"Received action request: {action_request.action}")
        self._add_audit_entry("INFO", f"Reasoning: {action_request.reasoning}")
        self._add_audit_entry("INFO", f"Parameters: {action_request.parameters}")
        
        is_valid, error_msg = self._validate_action(action_request)
        
        if not is_valid:
            self._add_audit_entry("ERROR", f"Validation failed: {error_msg}")
            return ExecutionResult(
                success=False,
                action_taken=None,
                message=f"Execution rejected: {error_msg}",
                audit_entries=self.audit_log.copy()
            )
        
        self._add_audit_entry("INFO", "Validation passed")
        
        action = action_request.action.lower()
        params = action_request.parameters
        
        if action == "approve_refund":
            order_id = params["order_id"]
            amount = params["amount"]
            reason = params["reason"]
            self._add_audit_entry("INFO", f"Executing: Approving refund for order {order_id}, amount ${amount}, reason: {reason}")
            result_message = f"Refund approved: Order {order_id}, Amount ${amount}, Reason: {reason}"
            action_taken = f"APPROVED_REFUND_{order_id}"
        
        elif action == "reject_refund":
            order_id = params["order_id"]
            reason = params["reason"]
            self._add_audit_entry("INFO", f"Executing: Rejecting refund for order {order_id}, reason: {reason}")
            result_message = f"Refund rejected: Order {order_id}, Reason: {reason}"
            action_taken = f"REJECTED_REFUND_{order_id}"
        
        elif action == "escalate_refund":
            order_id = params["order_id"]
            amount = params["amount"]
            reason = params["reason"]
            self._add_audit_entry("INFO", f"Executing: Escalating refund for order {order_id}, amount ${amount}, reason: {reason}")
            result_message = f"Refund escalated to manager: Order {order_id}, Amount ${amount}, Reason: {reason}"
            action_taken = f"ESCALATED_REFUND_{order_id}"
        
        elif action == "request_additional_info":
            order_id = params["order_id"]
            info_needed = params["info_needed"]
            self._add_audit_entry("INFO", f"Executing: Requesting additional info for order {order_id}, needed: {info_needed}")
            result_message = f"Additional information requested: Order {order_id}, Needed: {info_needed}"
            action_taken = f"REQUESTED_INFO_{order_id}"
        
        else:
            self._add_audit_entry("ERROR", f"Unknown action in execution: {action}")
            return ExecutionResult(
                success=False,
                action_taken=None,
                message="Unknown action",
                audit_entries=self.audit_log.copy()
            )
        
        self._add_audit_entry("SUCCESS", f"Action completed: {action_taken}")
        
        return ExecutionResult(
            success=True,
            action_taken=action_taken,
            message=result_message,
            audit_entries=self.audit_log.copy()
        )

