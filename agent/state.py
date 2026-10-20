from typing import TypedDict, Any

class IncidentState(TypedDict, total=False):
    incident_id: int
    title: str
    service_name: str
    severity: str
    description: str
    logs: str
    evidence: list[str]
    root_cause: str
    recommended_action: str
    risk_level: str
    approval_required: bool
    similar_incidents: list[dict[str, Any]]
