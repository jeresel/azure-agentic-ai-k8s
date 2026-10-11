import json
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from app.tools.kubernetes import get_pod_diagnostics
from app.llm import analyze_pod_diagnostics
from app.diagnostics import prepare_diagnostics

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

    # Avoid sending failed diagnostic requests to the LLM
    if "error" in diagnostics:
        return {
            "analysis": (
                "Unable to collect diagnostics: "
                f"{diagnostics['error']}"
            )
        }

    # Convert Kubernetes diagnostic data into text
    diagnostic_text = prepare_diagnostics(diagnostics)

    # Analyze diagnostics using Azure Foundry GPT-4.1-mini
    try:
        analysis = analyze_pod_diagnostics(diagnostic_text)
    except Exception as exc:
        analysis = (
            "AI analysis unavailable. "
            f"Error type: {type(exc).__name__}. "
            "Check Foundry connectivity, authentication, "
            "deployment configuration, and logs."
        )

    return {"analysis": analysis}


builder = StateGraph(CloudOpsState)

builder.add_node("collect_diagnostics", collect_diagnostics)
builder.add_node("analyze_diagnostics", analyze_diagnostics)
builder.add_edge(START, "collect_diagnostics")
builder.add_edge("collect_diagnostics", "analyze_diagnostics")
builder.add_edge("analyze_diagnostics", END)
graph = builder.compile()
