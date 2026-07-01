from __future__ import annotations

import argparse
import sys

from pipeline_execution_planner.dependency_loader import (
    DependencyReportLoadError,
    load_dependency_report,
)
from pipeline_execution_planner.planner import build_execution_plan
from pipeline_execution_planner.validation_loader import (
    ValidationReportLoadError,
    load_validation_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pipeline-planner",
        description="Build RADAR Services pipeline execution plans.",
    )

    subparsers = parser.add_subparsers(dest="command")

    plan_parser = subparsers.add_parser(
        "plan",
        help="Build an execution plan from validation and dependency reports.",
    )
    plan_parser.add_argument(
        "--dependency-report",
        required=True,
        help="Dependency analysis report JSON.",
    )
    plan_parser.add_argument(
        "--validation-report",
        required=True,
        help="Validation report JSON.",
    )

    return parser


def print_execution_plan(plan) -> None:
    print(f"Execution plan status: {plan.status}")
    print(f"Ready pipelines: {plan.ready_count}")
    print(f"Blocked pipelines: {plan.blocked_count}")
    print(f"Issues: {plan.issue_count}")

    if plan.ready_pipelines:
        print("Ready:")
        for pipeline in plan.ready_pipelines:
            print(f"- {pipeline.pipeline_id}")

    if plan.blocked_pipelines:
        print("Blocked:")
        for pipeline in plan.blocked_pipelines:
            print(f"- {pipeline.pipeline_id}: {pipeline.reason}")

    if plan.issues:
        print("Issues:")
        for issue in plan.issues:
            suffix = f" ({issue.pipeline_id})" if issue.pipeline_id else ""
            print(f"- {issue.code}: {issue.message}{suffix}")


def run_plan_command(args: argparse.Namespace) -> int:
    try:
        dependency_report = load_dependency_report(args.dependency_report)
        validation_report = load_validation_report(args.validation_report)
    except (DependencyReportLoadError, ValidationReportLoadError) as exc:
        print(f"Execution planning failed to start: {exc}", file=sys.stderr)
        return 1

    plan = build_execution_plan(
        dependency_report=dependency_report,
        validation_report=validation_report,
    )

    print_execution_plan(plan)

    return 0 if plan.ok else 1


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "plan":
        return run_plan_command(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
