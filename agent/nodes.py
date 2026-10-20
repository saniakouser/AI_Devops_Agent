from agent.tools import get_logs
from rag.retrieval import search_incidents

def collect_evidence(state: dict) -> dict:
    logs = get_logs(state.get("logs", ""))
    evidence = []
    if logs:
        evidence.append("Incident logs were supplied by the caller.")
    else:
        evidence.append("No logs supplied; root-cause confidence is limited.")
    evidence.append("Service metrics are not connected (demo stub).")
    return {"evidence": evidence, "logs": logs}

def analyze_root_cause(state: dict) -> dict:
    logs = (state.get("logs") or "").lower()
    description = (state.get("description") or "").lower()
    combined = logs + "\n" + description
    if "oomkilled" in combined or "out of memory" in combined or "memoryerror" in combined:
        cause = "Possible memory exhaustion (OOM); confirm with memory metrics and container events."
        action = "Review memory usage and recent changes; consider scaling only after approval."
        risk = "high"
    elif "imagepullbackoff" in combined or "image pull" in combined:
        cause = "Container image could not be pulled; check image name, tag, registry access, and image-pull secret."
        action = "Validate image reference and registry credentials, then redeploy through the normal pipeline."
        risk = "medium"
    elif "modulenotfounderror" in combined or "module not found" in combined or "npm err!" in combined:
        cause = "Likely dependency or build packaging failure."
        action = "Check dependency manifest, lockfile, build environment, and CI logs; rerun tests before redeploy."
        risk = "low"
    elif "connection refused" in combined:
        cause = "A dependency or service endpoint refused the connection; the target may be down or misconfigured."
        action = "Verify target health, port, DNS, network policy, and recent deployment changes."
        risk = "medium"
    elif "permission denied" in combined:
        cause = "Likely filesystem, identity, or authorization permission issue."
        action = "Inspect the failing identity and minimum required permissions; do not grant broad privileges."
        risk = "medium"
    elif "500" in combined or "internal server error" in combined:
        cause = "Application is returning HTTP 500 errors; logs provided are insufficient to prove a specific cause."
        action = "Correlate stack traces with deployment history and dependency health before taking action."
        risk = "medium"
    else:
        cause = "Insufficient evidence to determine a reliable root cause."
        action = "Collect timestamped application logs, metrics, recent deployment details, and dependency status."
        risk = "low"
    return {"root_cause": cause, "recommended_action": action, "risk_level": risk,
            "approval_required": risk in {"high", "critical"}}

def retrieve_history(state: dict) -> dict:
    query = " ".join([state.get("title", ""), state.get("description", ""), state.get("logs", "")])
    return {"similar_incidents": search_incidents(query, limit=3)}
