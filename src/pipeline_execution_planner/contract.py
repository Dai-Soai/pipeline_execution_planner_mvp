from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

PlanStatus = Literal["ready", "blocked"]
PipelinePlanStatus = Literal["ready", "blocked"]


@dataclass(frozen=True)
class PlannedPipeline:
    """
    One pipeline in the execution plan.
    """

    pipeline_id: str
    status: PipelinePlanStatus = "ready"
    reason: str | None = None


@dataclass(frozen=True)
class PlanIssue:
    """
    One issue that affects execution planning.
    """

    code: str
    message: str
    pipeline_id: str | None = None


@dataclass(frozen=True)
class ExecutionPlan:
    """
    Final execution plan.
    """

    status: PlanStatus
    pipelines: list[PlannedPipeline] = field(default_factory=list)
    issues: list[PlanIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.status == "ready"

    @property
    def ready_pipelines(self) -> list[PlannedPipeline]:
        return [pipeline for pipeline in self.pipelines if pipeline.status == "ready"]

    @property
    def blocked_pipelines(self) -> list[PlannedPipeline]:
        return [pipeline for pipeline in self.pipelines if pipeline.status == "blocked"]

    @property
    def ready_count(self) -> int:
        return len(self.ready_pipelines)

    @property
    def blocked_count(self) -> int:
        return len(self.blocked_pipelines)

    @property
    def issue_count(self) -> int:
        return len(self.issues)


def ready_plan(pipelines: list[PlannedPipeline]) -> ExecutionPlan:
    return ExecutionPlan(
        status="ready",
        pipelines=pipelines,
    )


def blocked_plan(
    pipelines: list[PlannedPipeline],
    issues: list[PlanIssue],
) -> ExecutionPlan:
    return ExecutionPlan(
        status="blocked",
        pipelines=pipelines,
        issues=issues,
    )
