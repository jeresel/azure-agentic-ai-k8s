
import os
from datetime import datetime, timezone, timedelta

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException


def get_k8s_client():
    """
    Use the Pod ServiceAccount inside AKS.
    Use local kubeconfig during development.
    """
    if os.getenv("KUBERNETES_SERVICE_HOST"):
        config.load_incluster_config()
    else:
        config.load_kube_config()

    return client.CoreV1Api()


def get_pod_diagnostics(
    namespace: str,
    pod_name: str,
    minutes: int = 30,
) -> dict:
    """
    Collect read-only Kubernetes diagnostics
    for the requested time window.
    """
    if not 1 <= minutes <= 1440:
        return {"error": "minutes must be between 1 and 1440"}

    api = get_k8s_client()
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=minutes)

    try:
        pod = api.read_namespaced_pod(
            name=pod_name,
            namespace=namespace,
        )

        events = api.list_namespaced_event(
            namespace=namespace,
            field_selector=f"involvedObject.uid={pod.metadata.uid}",
        )

        containers = []

        for container in pod.status.container_statuses or []:
            state = container.state
            waiting = state.waiting if state else None
            terminated = state.terminated if state else None

            previous = (
                container.last_state.terminated
                if container.last_state
                else None
            )

            containers.append({
                "name": container.name,
                "ready": container.ready,
                "restart_count": container.restart_count,
                "waiting_reason": waiting.reason if waiting else None,
                "waiting_message": waiting.message if waiting else None,
                "terminated_reason": (
                    terminated.reason if terminated else None
                ),
                "terminated_exit_code": (
                    terminated.exit_code if terminated else None
                ),
                "last_termination_reason": (
                    previous.reason if previous else None
                ),
                "last_termination_exit_code": (
                    previous.exit_code if previous else None
                ),
                "last_termination_time": (
                    previous.finished_at.isoformat()
                    if previous and previous.finished_at
                    else None
                ),
            })

        event_details = []

        for event in events.items:
            event_time = (
                event.last_timestamp
                or event.event_time
                or event.first_timestamp
                or event.metadata.creation_timestamp
            )

            if event_time and event_time >= cutoff:
                event_details.append({
                    "reason": event.reason,
                    "message": event.message,
                    "type": event.type,
                    "count": event.count,
                    "timestamp": event_time.isoformat(),
                })

        logs = {}
        previous_logs = {}

        for container in pod.spec.containers:
            name = container.name

            try:
                logs[name] = api.read_namespaced_pod_log(
                    name=pod_name,
                    namespace=namespace,
                    container=name,
                    since_seconds=minutes * 60,
                    tail_lines=200,
                    timestamps=True,
                    _request_timeout=15,
                )
            except ApiException as exc:
                logs[name] = f"Logs unavailable: HTTP {exc.status}"

            try:
                previous_logs[name] = api.read_namespaced_pod_log(
                    name=pod_name,
                    namespace=namespace,
                    container=name,
                    previous=True,
                    since_seconds=minutes * 60,
                    tail_lines=100,
                    timestamps=True,
                    _request_timeout=15,
                )
            except ApiException:
                # Previous logs may not exist.
                previous_logs[name] = None

        return {
            "timestamp": now.isoformat(),
            "time_window_minutes": minutes,
            "namespace": namespace,
            "pod": pod_name,
            "phase": pod.status.phase,
            "node": pod.spec.node_name,
            "containers": containers,
            "events": event_details,
            "logs": logs,
            "previous_logs": previous_logs,
        }

    except ApiException as exc:
        return {
            "error": f"Kubernetes API error: HTTP {exc.status}",
            "namespace": namespace,
            "pod": pod_name,
        }
