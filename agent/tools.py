"""Safe, local evidence-collection tools. No production infrastructure is touched."""
def get_logs(log_text: str) -> str:
    return (log_text or "")[-12000:]

def get_service_status(service_name: str) -> dict:
    # Demo stub. Replace with an authenticated monitoring/Kubernetes adapter later.
    return {"service": service_name, "status": "unknown", "source": "demo_stub"}

def get_metrics(service_name: str) -> dict:
    # Demo stub; intentionally does not claim to query real metrics.
    return {"service": service_name, "cpu_percent": None, "memory_percent": None, "source": "demo_stub"}
