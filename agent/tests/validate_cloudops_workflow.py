
from app.graph import graph
from unittest.mock import patch

# Simulated Kubernetes pod failure
mock_diagnostics = {
    "namespace": "cloudops-ai",
    "pod": "nginx-test",
    "phase": "Running",
    "containers": [
        {
            "name": "nginx",
            "ready": False,
            "restart_count": 5,
            "waiting_reason": "CrashLoopBackOff",
            "terminated_reason": "OOMKilled",
            "exit_code": 137,
        }
    ],
    "events": [
        {
            "reason": "BackOff",
            "message": "Back-off restarting failed container nginx",
        }
    ],
    "logs": "Container terminated after exceeding memory limit.",
}

# Replace only the Kubernetes diagnostic call.
# LangGraph and the Foundry model call remain real.
with patch(
    "app.graph.get_pod_diagnostics",
    return_value=mock_diagnostics,
):
    result = graph.invoke(
        {
            "namespace": "cloudops-ai",
            "pod": "nginx-test",
        }
    )

print("\n=== Kubernetes Diagnostics ===")
print(result["diagnostics"])

print("\n=== AI Root Cause Analysis ===")
print(result["analysis"])
