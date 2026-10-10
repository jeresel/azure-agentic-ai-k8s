import argparse
import json

from app.tools.kubernetes import get_pod_diagnostics


def main():
    parser = argparse.ArgumentParser(
        description="Azure Agentic AI CloudOps Assistant"
    )

    parser.add_argument(
        "--namespace",
        required=True,
        help="Kubernetes namespace",
    )

    parser.add_argument(
        "--pod",
        required=True,
        help="Kubernetes pod name",
    )

    args = parser.parse_args()

    print(
        f"Collecting diagnostics for "
        f"{args.namespace}/{args.pod}...",
        flush=True,
    )

    diagnostics = get_pod_diagnostics(
        namespace=args.namespace,
        pod_name=args.pod,
    )

    print(json.dumps(diagnostics, indent=2))


if __name__ == "__main__":
    main()