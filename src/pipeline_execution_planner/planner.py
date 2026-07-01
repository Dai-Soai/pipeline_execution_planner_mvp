from __future__ import annotations

from typing import Any

from pipeline_execution_planner.contract import (
    PlanIssue,
    PlannedPipeline,
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


def collect_blocked_pipeline_ids(issues: list[PlanIssue]) -> set[str]:
    blocked: set[str] = set()

    for issue in issues:
        if issue.pipeline_id:
            blocked.add(issue.pipeline_id)

    return blocked


def build_planned_pipelines(
    execution_order: list[str],
    blocked_ids: set[str],
) -> list[PlannedPipeline]:
    pipelines: list[PlannedPipeline] = []

    for pipeline_id in execution_order:
        if pipeline_id in blocked_ids:
            pipelines.append(
                PlannedPipeline(
                    pipeline_id=pipeline_id,
                    status="blocked",
                    reason="plan_blocked",
                )
            )
        else:
            pipelines.append(
                PlannedPipeline(
                    pipeline_id=pipeline_id,
                    status="ready",
                )
            )

    return pipelines


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
        blocked_ids = collect_blocked_pipeline_ids(issues)

        if not blocked_ids:
            blocked_ids = set(execution_order)

        return blocked_plan(
            pipelines=build_planned_pipelines(
                execution_order=execution_order,
                blocked_ids=blocked_ids,
            ),
            issues=issues,
        )

    return ready_plan(
        pipelines=build_planned_pipelines(
            execution_order=execution_order,
            blocked_ids=set(),
        )
    )
