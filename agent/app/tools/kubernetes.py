import os
from datetime import datetime, timezone

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException


def get_k8s_client():
    """
    Use the Pod ServiceAccount when running inside AKS.
    Use the local kubeconfig during development.
    """
    if os.getenv("KUBERNETES_SERVICE_HOST"):
        config.load_incluster_config()
    else:
        config.load_kube_config()

    return client.CoreV1Api()


def get_pod_diagnostics(namespace: str, pod_name: str) -> dict:
    """
    Collect read-only diagnostic information for a Kubernetes pod.
    """
    api = get_k8s_client()

    try:
        pod = api.read_namespaced_pod(
            name=pod_name,
            namespace=namespace,
        )

        # Select only events associated with this pod's UID.
        events = api.list_namespaced_event(
            namespace=namespace,
            field_selector=f"involvedObject.uid={pod.metadata.uid}",
        )

        containers = []
        for container in pod.status.container_statuses or []:
            state = container.state
            waiting = state.waiting if state else None
            terminated = state.terminated if state else None

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
                    container.last_state.terminated.reason
                    if container.last_state
                    and container.last_state.terminated
                    else None
                ),
            })

        event_details = [
            {
                "reason": event.reason,
                "message": event.message,
                "type": event.type,
                "count": event.count,
            }
            for event in events.items
        ]

        logs = {}

        for container in pod.spec.containers:
            try:
                logs[container.name] = api.read_namespaced_pod_log(
                    name=pod_name,
                    namespace=namespace,
                    container=container.name,
                    tail_lines=50,
                    timestamps=True,
                    _request_timeout=15,
                )
            except ApiException as exc:
                logs[container.name] = (
                    f"Logs unavailable: HTTP {exc.status}"
                )

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "namespace": namespace,
            "pod": pod_name,
            "phase": pod.status.phase,
            "node": pod.spec.node_name,
            "containers": containers,
            "events": event_details,
            "logs": logs,
        }

    except ApiException as exc:
        return {
            "error": f"Kubernetes API error: HTTP {exc.status}",
            "namespace": namespace,
            "pod": pod_name,
        }