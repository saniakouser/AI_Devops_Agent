from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

Severity = Literal["low", "medium", "high", "critical"]

class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    service_name: str = Field(min_length=1, max_length=100)
    severity: Severity = "medium"
    description: str = Field(min_length=1)
    logs: str = Field(default="", max_length=50000)

class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    service_name: str
    severity: str
    status: str
    description: str
    logs: str
    root_cause: str | None
    recommended_action: str | None
    created_at: datetime

class InvestigationResponse(BaseModel):
    incident_id: int
    root_cause: str
    recommended_action: str
    risk_level: str
    approval_required: bool
    evidence: list[str]
    similar_incidents: list[dict]
    status: str
