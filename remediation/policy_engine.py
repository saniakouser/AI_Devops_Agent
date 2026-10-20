from dataclasses import dataclass

ALLOWED_ACTIONS = {"restart_service", "rollback_deployment", "scale_service"}

@dataclass
class PolicyDecision:
    allowed: bool
    approval_required: bool
    reason: str

def evaluate_action(action: str, severity: str, approved: bool = False) -> PolicyDecision:
    if action not in ALLOWED_ACTIONS:
        return PolicyDecision(False, False, "Action is not in the allowlist.")
    if action in {"rollback_deployment", "scale_service"}:
        if not approved:
            return PolicyDecision(False, True, "Human approval is required for this action.")
    if severity == "critical" and not approved:
        return PolicyDecision(False, True, "Critical incidents require human approval.")
    return PolicyDecision(True, False, "Allowed by demo policy.")
