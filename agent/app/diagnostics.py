
import json

from app.security import redact_sensitive_data


def prepare_diagnostics(diagnostics: dict) -> str:
    """Prepare a limited, sanitized Kubernetes diagnostic payload."""

    containers = []

    for container in diagnostics.get("containers", [])[:10]:
        containers.append({
            key: container[key]
            for key in (
                "name",
                "ready",
                "restart_count",
                "waiting_reason",
                "terminated_reason",
                "exit_code",
            )
            if key in container
        })

    events = []

    for event in diagnostics.get("events", [])[-10:]:
        if isinstance(event, dict):
            events.append({
                key: event[key]
                for key in ("reason", "message")
                if key in event
            })

    raw_logs = diagnostics.get("logs", "")

    if not isinstance(raw_logs, str):
        raw_logs = json.dumps(raw_logs, default=str)

    filtered = {
        "namespace": diagnostics.get("namespace"),
        "pod": diagnostics.get("pod"),
        "phase": diagnostics.get("phase"),
        "containers": containers,
        "events": events,
        "logs": raw_logs[-2000:],
    }

    return redact_sensitive_data(
        json.dumps(filtered, indent=2, default=str)
    )
