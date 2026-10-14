from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException
from pydantic import Field
from app.graph import graph
from pathlib import Path
from fastapi.responses import FileResponse
from kubernetes.client.exceptions import ApiException
from app.tools.kubernetes import get_k8s_client


app = FastAPI(
    title="Azure Agentic AI CloudOps Assistant",
    description=(
        "AI-powered Kubernetes troubleshooting API "
        "using LangGraph and Microsoft Foundry."
    ),
    version="0.1.0",
)


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

@app.get("/", include_in_schema=False)
def web_interface():
    return FileResponse(WEB_DIR / "index.html")

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="healthy",
        service="cloudops-ai-agent",
        version="0.1.0",
    )

class DiagnosticsRequest(BaseModel):
    namespace: str = Field(
        min_length=1,
        max_length=63,
        pattern=r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$",
    )
    pod: str = Field(
        min_length=1,
        max_length=253,
        pattern=r"^[a-z0-9]([-a-z0-9.]*[a-z0-9])?$",
    )


class DiagnosticsResponse(BaseModel):
    namespace: str
    pod: str
    analysis: str


@app.post("/api/diagnostics", response_model=DiagnosticsResponse)
def analyze_kubernetes_pod(request: DiagnosticsRequest):
    try:
        result = graph.invoke({
            "namespace": request.namespace,
            "pod": request.pod,
        })
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Kubernetes diagnostics workflow failed.",
        )

    analysis = result["analysis"]

    if analysis.startswith("Unable to collect diagnostics:"):
        raise HTTPException(
            status_code=404,
            detail="Pod not found or diagnostics unavailable.",
        )

    return DiagnosticsResponse(
        namespace=request.namespace,
        pod=request.pod,
        analysis=analysis,
    )


@app.get("/api/namespaces")
def list_kubernetes_namespaces():
    try:
        api = get_k8s_client()
        namespaces = api.list_namespace(
            _request_timeout=10
        )

        return {
            "namespaces": sorted(
                ns.metadata.name
                for ns in namespaces.items
            )
        }

    except (ApiException, Exception) as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve Kubernetes namespaces."
        ) from exc


@app.get("/api/pods")
def list_kubernetes_pods(namespace: str):
    try:
        api = get_k8s_client()
        pods = api.list_namespaced_pod(
            namespace=namespace,
            _request_timeout=10
        )

        return {
            "namespace": namespace,
            "pods": sorted(
                pod.metadata.name
                for pod in pods.items
            )
        }

    except ApiException as exc:
        if exc.status == 404:
            raise HTTPException(
                status_code=404,
                detail="Namespace not found."
            ) from exc

        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve Kubernetes pods."
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve Kubernetes pods."
        ) from exc
