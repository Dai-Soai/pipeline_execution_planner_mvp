from __future__ import annotations

from typing import Any

from pipeline_execution_planner.contract import (
    PlannedPipeline,
    PlanIssue,
    blocked_plan,
    ready_plan,
)
from pipeline_execution_planner.dependency_loader import (
    get_dependency_issues,
    get_dependency_report_status,
    get_execution_order,
)
from pipeline_execution_planner.validation_loader import (
    get_validation_issues,
    get_validation_report_status,
)


def issue_from_payload(payload: dict[str, Any], default_code: str) -> PlanIssue:
    return PlanIssue(
        code=str(payload.get("code", default_code)),
        message=str(payload.get("message", "Unknown issue.")),
        pipeline_id=payload.get("pipeline_id"),
    )


def build_execution_plan(
    dependency_report: dict[str, Any],
    validation_report: dict[str, Any],
):
    issues: list[PlanIssue] = []

    dependency_ok = get_dependency_report_status(dependency_report)
    validation_ok = get_validation_report_status(validation_report)

    if not dependency_ok:
        for issue in get_dependency_issues(dependency_report):
            issues.append(
                issue_from_payload(
                    issue,
                    default_code="dependency_failed",
                )
            )

    if not validation_ok:
        for issue in get_validation_issues(validation_report):
            issues.append(
                issue_from_payload(
                    issue,
                    default_code="validation_failed",
                )
            )

    execution_order = get_execution_order(dependency_report)

    if issues:
        return blocked_plan(
            pipelines=[
                PlannedPipeline(
                    pipeline_id=pipeline_id,
                    status="blocked",
                    reason="plan_blocked",
                )
                for pipeline_id in execution_order
            ],
            issues=issues,
        )

    return ready_plan(
        pipelines=[
            PlannedPipeline(
                pipeline_id=pipeline_id,
                status="ready",
            )
            for pipeline_id in execution_order
        ]
    )
