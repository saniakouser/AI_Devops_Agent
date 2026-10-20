"""Simulation-only remediation. Does not restart or modify any real service."""
from remediation.policy_engine import evaluate_action

def execute_remediation(action: str, service_name: str, severity: str, approved: bool = False) -> dict:
    decision = evaluate_action(action, severity, approved)
    if not decision.allowed:
        return {
            "executed": False,
            "simulation": True,
            "approval_required": decision.approval_required,
            "message": decision.reason,
            "action": action,
            "service": service_name,
        }
    return {
        "executed": True,
        "simulation": True,
        "approval_required": False,
        "message": "Simulated action only; no real infrastructure was changed.",
        "action": action,
        "service": service_name,
    }
