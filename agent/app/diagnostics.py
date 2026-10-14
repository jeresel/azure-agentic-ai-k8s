
import json

from app.security import redact_sensitive_data


def filter_logs(logs: dict, max_lines: int = 50) -> dict:
    """
    Remove routine health checks and limit logs
    before sending them to the LLM.
    """
    filtered = {}

    for container, content in logs.items():
        if not content:
            continue

        lines = content.splitlines()

        meaningful_lines = [
            line for line in lines
            if not (
                "GET /health" in line
                and "200 OK" in line
            )
        ]

        filtered[container] = meaningful_lines[-max_lines:]

    return filtered


def prepare_diagnostics(diagnostics: dict) -> str:
    """
    Prepare sanitized Kubernetes diagnostics
    for Microsoft Foundry AI analysis.
    """

    containers = []

    for container in diagnostics.get("containers", [])[:10]:
        containers.append({
            key: container.get(key)
            for key in (
                "name",
                "ready",
                "restart_count",
                "waiting_reason",
                "waiting_message",
                "terminated_reason",
                "terminated_exit_code",
                "last_termination_reason",
                "last_termination_exit_code",
                "last_termination_time",
            )
        })

    events = []

    for event in diagnostics.get("events", [])[-20:]:
        events.append({
            "reason": event.get("reason"),
            "message": event.get("message"),
            "type": event.get("type"),
            "timestamp": event.get("timestamp"),
        })

    filtered = {
        "timestamp": diagnostics.get("timestamp"),
        "time_window_minutes": diagnostics.get(
            "time_window_minutes", 30
        ),
        "namespace": diagnostics.get("namespace"),
        "pod": diagnostics.get("pod"),
        "phase": diagnostics.get("phase"),
        "node": diagnostics.get("node"),
        "containers": containers,
        "events": events,
        "logs": filter_logs(
            diagnostics.get("logs", {})
        ),
        "previous_logs": filter_logs(
            diagnostics.get("previous_logs", {})
        ),
    }

    return redact_sensitive_data(
        json.dumps(filtered, indent=2, default=str)
    )
