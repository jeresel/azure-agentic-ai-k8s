
import argparse

from app.graph import graph


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
        f"Analyzing AKS pod: {args.namespace}/{args.pod}",
        flush=True,
    )

    result = graph.invoke({
        "namespace": args.namespace,
        "pod": args.pod,
    })

    print("\n=== AI CloudOps Incident Analysis ===\n")
    print(result["analysis"])


if __name__ == "__main__":
    main()
