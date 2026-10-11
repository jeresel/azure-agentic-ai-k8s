# Azure Agentic AI CloudOps Assistant — Kubernetes & AI Agent

A Kubernetes-based AI CloudOps Assistant designed to investigate AKS workloads, collect diagnostic information, and provide AI-powered root cause analysis using LangGraph and Microsoft Foundry.

This repository contains the Kubernetes manifests and Python agent application. Azure infrastructure is provisioned separately using Terraform.

## Architecture

```text
CloudOps CLI / Application
          |
          v
    LangGraph Agent
          |
          +---- Kubernetes Python SDK
          |              |
          |              v
          |          Azure AKS
          |       (Read-only RBAC)
          |
          +---- Microsoft Foundry
                         |
                         v
                    GPT-4.1-mini
                         |
                         v
               Root Cause Analysis
```

The end-to-end integration between LangGraph and GPT-4.1-mini is currently under development.

## Technology Stack

| Component | Technology |
|---|---|
| Cloud Platform | Microsoft Azure |
| Container Orchestration | Azure Kubernetes Service (AKS) |
| AI Model | GPT-4.1-mini |
| AI Platform | Microsoft Foundry |
| Agent Orchestration | LangGraph |
| Application Language | Python |
| Kubernetes Integration | Kubernetes Python SDK |
| Authentication | Microsoft Entra ID |
| Kubernetes Configuration | Kustomize and YAML |
| Infrastructure Provisioning | Terraform (separate repository) |

## Repository Structure

```text
azure-agentic-ai-k8s/
├── agent/
│   ├── app/
│   │   ├── main.py
│   │   ├── graph.py
│   │   ├── llm.py
│   │   └── tools/
│   │       └── kubernetes.py
│   └── test_foundry.py
├── k8s/
│   ├── base/
│   │   ├── namespace.yaml
│   │   ├── serviceaccount.yaml
│   │   ├── clusterrole.yaml
│   │   ├── clusterrolebinding.yaml
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── kustomization.yaml
│   └── overlays/
│       └── dev/
│           └── kustomization.yaml
└── README.md
```

*Some application and deployment files are placeholders or under development.*

## Features

### Implemented

- Kubernetes namespace and ServiceAccount definitions
- Read-only ClusterRole and ClusterRoleBinding
- Declarative Kubernetes configuration using Kustomize
- Python Kubernetes diagnostics for pod status, events, and logs
- Initial LangGraph diagnostic workflow
- Successful GPT-4.1-mini inference test using Microsoft Entra ID

### Planned

- Integrate GPT-4.1-mini into the LangGraph diagnostic workflow
- Generate AI-powered root cause analysis and remediation recommendations
- Implement a FastAPI backend and web-based chat interface
- Containerize the application and push the image to Azure Container Registry
- Deploy the application to AKS using Kustomize
- Configure Azure Workload Identity for passwordless access to Azure services

## Local Development

### Prerequisites

- Python 3.12 or later
- Azure CLI
- kubectl
- Access to an AKS cluster
- Appropriate Azure RBAC permissions for Microsoft Foundry

### Configure Python

From the `agent/` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the Python dependencies required by the agent, including Kubernetes SDK, LangGraph, OpenAI SDK, and Azure Identity.

### Authenticate to Azure

```bash
az login
```

Set the model endpoint and deployment name:

```bash
export AZURE_OPENAI_ENDPOINT="https://foundry-agentic-ai-us2094b-dev.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT="gpt-4.1-mini"
```

### Test Foundry Connectivity

```bash
python3 test_foundry.py
```

### Test Kubernetes Diagnostics

Ensure your local Kubernetes context points to the intended AKS cluster.

```bash
kubectl config current-context
kubectl get pods -A
```

Then use the Python CLI to run the available pod diagnostic commands.

## Kubernetes Deployment

Kubernetes resources are maintained declaratively using Kustomize.

Preview the development overlay:

```bash
kubectl kustomize k8s/overlays/dev
```

Deployment of the AI agent application will be completed in a later phase. Application image references and workload identity configuration must be finalized before deployment.

## Security Design

- Kubernetes access is restricted using read-only RBAC.
- Microsoft Foundry inference uses Microsoft Entra ID authentication.
- Azure API keys and credentials are not stored in source code.
- Kubernetes changes are managed declaratively.
- Sensitive diagnostic information should be redacted before being sent to the AI model.
- Automated destructive Kubernetes operations are outside the initial project scope.

## Related Repository

**Azure Infrastructure:** `azure-agentic-ai-infra`

Contains Terraform modules for AKS, Azure Container Registry, networking, Microsoft Foundry, model deployment, and Azure RBAC.

## Project Goal

Build a secure, extensible AI-powered CloudOps Assistant that combines Kubernetes diagnostics, agent orchestration, and generative AI to support troubleshooting and operational decision-making.