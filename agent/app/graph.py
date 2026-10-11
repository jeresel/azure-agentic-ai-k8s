from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from app.tools.kubernetes import get_pod_diagnostics


class CloudOpsState(TypedDict):
    namespace: str
    pod: str
    diagnostics: dict
    analysis: str


def collect_diagnostics(state: CloudOpsState) -> dict:
    diagnostics = get_pod_diagnostics(
        namespace=state["namespace"],
        pod_name=state["pod"],
    )

    return {"diagnostics": diagnostics}


def analyze_diagnostics(state: CloudOpsState) -> dict:
    diagnostics = state["diagnostics"]

    if "error" in diagnostics:
        analysis = f"Unable to collect diagnostics: {diagnostics['error']}"

    elif any(
        container.get("waiting_reason")
        or container.get("terminated_reason")
        or not container.get("ready")
        for container in diagnostics.get("containers", [])
    ):
        analysis = (
            "Potential pod issue detected. Review container state, "
            "restart counts, events and logs for the root cause."
        )

    else:
        analysis = (
            "Pod appears healthy based on its current container state. "
            "Review any warnings in logs for additional context."
        )

    return {"analysis": analysis}


builder = StateGraph(CloudOpsState)

builder.add_node("collect_diagnostics", collect_diagnostics)
builder.add_node("analyze_diagnostics", analyze_diagnostics)

builder.add_edge(START, "collect_diagnostics")
builder.add_edge("collect_diagnostics", "analyze_diagnostics")
builder.add_edge("analyze_diagnostics", END)

graph = builder.compile()