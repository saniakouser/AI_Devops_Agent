from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import Base, engine, get_db
from app.models import Incident
from app.schemas import IncidentCreate, IncidentResponse, InvestigationResponse
from app.cache import cache_get, cache_set, cache_delete
from agent.graph import incident_graph
from remediation.executor import execute_remediation

Base.metadata.create_all(bind=engine)
app = FastAPI(title="AI DevOps Incident Resolution Agent", version="0.2.0")
DBSession = Annotated[Session, Depends(get_db)]

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "ai-devops-incident-agent"}

@app.get("/health/redis")
def redis_health():
    from app.cache import get_redis
    client = get_redis()
    if client is None:
        return {"status": "unavailable", "cache_enabled": False}
    try:
        return {"status": "healthy", "cache_enabled": True, "redis_version": client.info("server").get("redis_version")}
    except Exception:
        return {"status": "unavailable", "cache_enabled": False}

@app.post("/incidents", response_model=IncidentResponse, status_code=201)
def create_incident(payload: IncidentCreate, db: DBSession):
    incident = Incident(**payload.model_dump())
    db.add(incident)
    db.commit()
    db.refresh(incident)
    # Invalidate the list cache because a new incident was added.
    cache_delete("incidents:list")
    return incident

@app.get("/incidents", response_model=list[IncidentResponse])
def list_incidents(db: DBSession):
    cached = cache_get("incidents:list")
    if cached is not None:
        return cached
    incidents = db.query(Incident).order_by(Incident.id.desc()).all()
    result = [IncidentResponse.model_validate(item).model_dump(mode="json") for item in incidents]
    cache_set("incidents:list", result)
    return result

def find_incident(incident_id: int, db: Session) -> Incident:
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@app.get("/incidents/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, db: DBSession):
    key = f"incidents:{incident_id}"
    cached = cache_get(key)
    if cached is not None:
        return cached
    incident = find_incident(incident_id, db)
    result = IncidentResponse.model_validate(incident).model_dump(mode="json")
    cache_set(key, result)
    return result

@app.post("/incidents/{incident_id}/investigate", response_model=InvestigationResponse)
def investigate_incident(incident_id: int, db: DBSession):
    incident = find_incident(incident_id, db)
    state = incident_graph.invoke({
        "incident_id": incident.id,
        "title": incident.title,
        "service_name": incident.service_name,
        "severity": incident.severity,
        "description": incident.description,
        "logs": incident.logs,
    })
    incident.root_cause = state.get("root_cause", "Unknown")
    incident.recommended_action = state.get("recommended_action", "Collect more evidence.")
    incident.investigation = {
        "evidence": state.get("evidence", []),
        "risk_level": state.get("risk_level", "low"),
        "approval_required": state.get("approval_required", False),
        "similar_incidents": state.get("similar_incidents", []),
    }
    db.commit()
    db.refresh(incident)
    cache_delete("incidents:list", f"incidents:{incident.id}")
    return {
        "incident_id": incident.id,
        "root_cause": incident.root_cause,
        "recommended_action": incident.recommended_action,
        "risk_level": state.get("risk_level", "low"),
        "approval_required": state.get("approval_required", False),
        "evidence": state.get("evidence", []),
        "similar_incidents": state.get("similar_incidents", []),
        "status": incident.status,
    }

@app.post("/incidents/{incident_id}/remediate")
def remediate_incident(
    incident_id: int,
    action: str,
    approved: bool = False,
    db: Session = Depends(get_db),
):
    incident = find_incident(incident_id, db)
    return {
        "incident_id": incident.id,
        **execute_remediation(action, incident.service_name, incident.severity, approved),
    }

@app.post("/incidents/{incident_id}/verify")
def verify_incident(incident_id: int, db: DBSession):
    incident = find_incident(incident_id, db)
    return {
        "incident_id": incident.id,
        "verified": False,
        "message": "Verification adapter is not connected. Integrate real service health checks before resolving incidents.",
    }
