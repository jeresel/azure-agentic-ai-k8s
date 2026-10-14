# Azure Agentic AI CloudOps Assistant

**AI-Powered Kubernetes Diagnostics | LangGraph | Microsoft Foundry | Azure AKS**

An AI-powered CloudOps Assistant designed to investigate Kubernetes workloads, collect real-time diagnostic information, and provide AI-assisted root cause analysis using **LangGraph and Microsoft Foundry GPT-4.1-mini**.

The application provides a web-based interface where engineers can dynamically select an AKS namespace and pod, collect Kubernetes diagnostics, and request AI-generated troubleshooting insights.

This repository contains the Python application, FastAPI backend, LangGraph workflow, web interface, and Kubernetes deployment manifests.

Azure infrastructure is managed separately using Terraform in the `azure-agentic-ai-infra` repository.

---

## 1. Architecture

```text
                 CloudOps Web GUI
                  (HTML / JS)
                       |
                       v
                 FastAPI Backend
                       |
          +------------+------------+
          |                         |
          v                         v
   Kubernetes Discovery       Diagnostics API
   /api/namespaces            /api/diagnostics
   /api/pods                        |
          |                         v
          |                   LangGraph Agent
          |                         |
          |               +---------+---------+
          |               |                   |
          v               v                   v
       Azure AKS     Kubernetes SDK      Diagnostics
       Read-only      Pod Status         Processing
       RBAC           Events / Logs      Redaction
                          |                   |
                          +---------+---------+
                                    |
                                    v
                            Microsoft Foundry
                              GPT-4.1-mini
                                    |
                                    v
                            AI Root Cause Analysis
                                    |
                                    v
                              CloudOps Web GUI
```

### Workflow

1. The web application retrieves available Kubernetes namespaces through the FastAPI backend.
2. Selecting a namespace dynamically populates the available pods.
3. The user selects a pod and initiates an analysis.
4. LangGraph invokes the Kubernetes diagnostic collection tool.
5. The Kubernetes Python SDK retrieves pod status, container information, recent events, and logs.
6. Diagnostic information is filtered and redacted before being submitted to Microsoft Foundry.
7. GPT-4.1-mini generates troubleshooting insights based on the collected evidence.
8. The analysis is returned to the web interface.

The workflow is designed for **read-only investigation**, without automatically modifying Kubernetes resources.

---

## 2. Technology Stack

| Component | Technology |
|---|---|
| Cloud Platform | Microsoft Azure |
| Container Orchestration | Azure Kubernetes Service (AKS) |
| AI Platform | Microsoft Foundry |
| Large Language Model | GPT-4.1-mini |
| Agent Orchestration | LangGraph |
| Backend Framework | FastAPI |
| Frontend | HTML, CSS, JavaScript |
| Application Language | Python |
| Kubernetes Integration | Kubernetes Python SDK |
| Authentication | Microsoft Entra ID / Azure Identity |
| Kubernetes Security | Read-only RBAC |
| Containerization | Docker |
| Container Registry | Azure Container Registry (ACR) |
| Kubernetes Configuration | Kustomize and YAML |
| Infrastructure as Code | Terraform (separate repository) |

---

## 3. Repository Structure

```text
azure-agentic-ai-k8s/
├── agent/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   └── kubernetes.py
│   │   ├── web/
│   │   │   └── index.html
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── graph.py
│   │   ├── llm.py
│   │   ├── diagnostics.py
│   │   └── security.py
│   ├── tests/
│   │   ├── __init__.py
│   │   └── validate_cloudops_workflow.py
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   └── test_foundry.py
├── k8s/
│   ├── base/
│   │   ├── namespace.yaml
│   │   ├── serviceaccount.yaml
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── kustomization.yaml
│   └── overlays/
│       └── dev/
│           └── kustomization.yaml
└── README.md
```

Additional Kubernetes manifests provide read-only ClusterRole and ClusterRoleBinding permissions and optional observability components.

---

## 4. Features

### Implemented

**Kubernetes Diagnostics**

- Connect to AKS using the Kubernetes Python SDK.
- Retrieve pod status and container readiness.
- Identify container restarts and termination reasons.
- Retrieve recent Kubernetes events.
- Collect current and previous container logs when available.
- Support a configurable diagnostic collection window, defaulting to 30 minutes.

**AI Agent Workflow**

- LangGraph-based diagnostic workflow.
- Kubernetes diagnostic collection node.
- Diagnostic processing and filtering.
- Microsoft Foundry GPT-4.1-mini integration.
- AI-generated analysis based on collected Kubernetes information.
- Graceful error handling when AI inference is unavailable.

**CloudOps Web Interface**

- FastAPI backend with HTML/CSS/JavaScript frontend.
- Dynamic namespace dropdown populated from AKS.
- Dynamic pod dropdown based on the selected namespace.
- Pod analysis through the existing LangGraph workflow.
- AI analysis displayed directly in the browser.
- Loading states and API error handling.
- Dark-themed CloudOps dashboard.

**Security**

- Read-only Kubernetes RBAC.
- Microsoft Entra ID authentication for Microsoft Foundry.
- Diagnostic log filtering and sensitive-data redaction.
- No automatic destructive Kubernetes operations.

### Planned Enhancements

- Natural-language troubleshooting across multiple pods and workloads.
- Automated workload discovery without manually selecting a pod.
- Deployment-level and namespace-wide incident analysis.
- AI-assisted remediation recommendations with human approval.
- Historical incident analysis and trend detection.
- Improved error classification and structured incident reports.
- Production-grade monitoring, authentication, and access controls.

---

## 5. REST API

The application exposes the following endpoints:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | CloudOps web interface |
| GET | `/health` | Application health check |
| GET | `/api/namespaces` | List available Kubernetes namespaces |
| GET | `/api/pods?namespace=cloudops-ai` | List pods in the selected namespace |
| POST | `/api/diagnostics` | Run LangGraph-powered pod diagnostics |

### Example Diagnostic Request

```bash
curl -X POST http://localhost:8000/api/diagnostics \
  -H "Content-Type: application/json" \
  -d '{
    "namespace": "cloudops-ai",
    "pod": "cloudops-ai-agent-784f8b77f6-whdkt"
  }'
```

### Example Response Structure

```json
{
  "namespace": "cloudops-ai",
  "pod": "cloudops-ai-agent-784f8b77f6-whdkt",
  "analysis": "AI-generated Kubernetes diagnostic analysis"
}
```

---

## 6. Kubernetes Diagnostic Capabilities

The Kubernetes diagnostic collector retrieves the following information:

| Diagnostic | Description |
|---|---|
| Pod Phase | Running, Pending, Failed, etc. |
| Container Readiness | Container health and readiness |
| Restart Count | Number of container restarts |
| Termination Details | Termination reasons and exit codes |
| Kubernetes Events | Recent pod-related events |
| Current Logs | Container logs within the selected time window |
| Previous Logs | Previous container logs when available |
| Node Information | Kubernetes node hosting the pod |
| Collection Timestamp | Time when diagnostics were retrieved |

### Log Processing

Before diagnostic information is sent to the AI model, the application:

- Removes routine successful `/health` requests.
- Limits the number of log lines included.
- Filters and limits Kubernetes events.
- Includes relevant container termination details.
- Applies sensitive-data redaction.
- Produces a structured JSON diagnostic payload.

The current implementation defaults to a **30-minute investigation window**.

This filtering reduces unnecessary AI token consumption and improves the relevance of troubleshooting information.

---

## 7. Local Development

### Prerequisites

- Python 3.12 or later
- Azure CLI
- kubectl
- Access to the AKS cluster
- Microsoft Foundry inference permissions
- Kubernetes permissions to read namespaces, pods, logs, and events

### Clone the Repository

```bash
git clone https://github.com/jeresel/azure-agentic-ai-k8s.git

cd azure-agentic-ai-k8s/agent
```

### Configure Python

```bash
python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

### Authenticate to Azure

```bash
az login
```

Configure the Microsoft Foundry endpoint and deployment:

```bash
export AZURE_OPENAI_ENDPOINT="https://<your-endpoint>.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT="gpt-4.1-mini"
```

Use the actual deployment name configured in Microsoft Foundry.

### Configure AKS Access

```bash
az aks get-credentials \
  --resource-group <resource-group> \
  --name aks-agentic-ai-dev
```

Verify connectivity:

```bash
kubectl config current-context

kubectl get pods -n cloudops-ai
```

---

## 8. Run the CloudOps Web Application

From the `agent/` directory:

```bash
python3 -m uvicorn app.api.main:app \
  --host 127.0.0.1 \
  --port 8000
```

Open the application:

**http://localhost:8000**

### Using the GUI

1. Open the CloudOps web interface.
2. Select the Kubernetes namespace from the dropdown.
3. Select a pod from the dynamically populated pod list.
4. Click **Analyze Pod**.
5. Review the AI-generated diagnostic analysis.

The application uses the active Kubernetes context to retrieve live diagnostic information.

---

## 9. Run Diagnostics from the CLI

The repository also supports command-line execution.

From the `agent/` directory:

```bash
python3 -m app.main \
  --namespace cloudops-ai \
  --pod cloudops-ai-agent-784f8b77f6-whdkt
```

The CLI invokes the LangGraph diagnostic workflow and prints the resulting analysis.

Pod names are deployment-specific and may change after a rollout.

---

## 10. Kubernetes Deployment

The application includes Docker and Kubernetes deployment configuration.

### Build the Container Image

From the `agent/` directory:

```bash
docker build -t azure-agentic-ai-cloudops:latest .
```

### Preview Kubernetes Resources

From the repository root:

```bash
kubectl kustomize k8s/overlays/dev
```

### Apply the Development Configuration

```bash
kubectl apply -k k8s/overlays/dev
```

The application has been exercised in an AKS environment. The latest GUI and diagnostic changes have been validated locally; a fresh container build and AKS rollout remain to be verified.

For AKS deployment, ensure that the container image, registry access, Kubernetes ServiceAccount, RBAC permissions, and Microsoft Foundry authentication are configured correctly.

---

## 11. Security Architecture

Security is a core design consideration for the CloudOps Assistant.

**Kubernetes Access**

- Read-only Kubernetes API permissions.
- Kubernetes ServiceAccount and ClusterRole-based access.
- No automatic pod deletion, restart, or deployment modification.

**Azure Authentication**

- Microsoft Entra ID-based authentication.
- Azure Identity integration for model inference.
- Designed to support passwordless workload authentication.

**AI Data Protection**

- Filter diagnostic information before model inference.
- Apply sensitive-data redaction to logs and events.
- Avoid embedding credentials in source code.
- Treat Kubernetes logs as untrusted input.
- Keep operational changes subject to human review.

The existing redaction controls provide a baseline but should not be considered a complete data-loss-prevention solution.

**Important:** Before exposing the web application beyond a trusted development environment, implement appropriate user authentication, authorization, network restrictions, and request controls.

---

## 12. Related Repository

**Azure Infrastructure — `azure-agentic-ai-infra`**

Contains Terraform-based Azure infrastructure provisioning, including AKS, Azure Container Registry, networking, Microsoft Foundry, model deployment, and Azure RBAC.

The application repository is intentionally separated from the infrastructure repository to support independent development and deployment lifecycles.

---

## 14. Project Goal

Build a secure, extensible, AI-powered CloudOps Assistant that combines Kubernetes observability, agent orchestration, and generative AI to help engineers investigate incidents faster and make informed operational decisions.

The long-term goal is to evolve the application from pod-level diagnostics into a broader **Agentic AI CloudOps platform** capable of intelligent investigation, incident correlation, and controlled remediation across cloud-native environments.
