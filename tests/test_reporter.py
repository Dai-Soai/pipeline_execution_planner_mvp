import json

from pipeline_execution_planner.contract import (
    ExecutionPlan,
    PlannedPipeline,
    PlanIssue,
)
from pipeline_execution_planner.reporter import (
    build_plan_report,
    write_plan_report,
)


def test_build_plan_report_ready():
    plan = ExecutionPlan(
        status="ready",
        pipelines=[
            PlannedPipeline("database"),
            PlannedPipeline("prepare"),
        ],
    )

    report = build_plan_report(plan)

    assert report["event_type"] == "pipeline_execution_plan"
    assert report["status"] == "ready"
    assert report["ok"] is True
    assert report["ready_count"] == 2
    assert report["blocked_count"] == 0
    assert report["ready_pipelines"] == ["database", "prepare"]
    assert report["execution_order"] == ["database", "prepare"]


def test_build_plan_report_blocked():
    plan = ExecutionPlan(
        status="blocked",
        pipelines=[
            PlannedPipeline("database"),
            PlannedPipeline(
                "workflow",
                status="blocked",
                reason="plan_blocked",
            ),
        ],
        issues=[
            PlanIssue(
                code="file_not_found",
                message="File not found.",
                pipeline_id="workflow",
            )
        ],
    )

    report = build_plan_report(plan)

    assert report["status"] == "blocked"
    assert report["ok"] is False
    assert report["ready_count"] == 1
    assert report["blocked_count"] == 1
    assert report["blocked_pipelines"][0]["pipeline_id"] == "workflow"
    assert report["issues"][0]["code"] == "file_not_found"


def test_write_plan_report(tmp_path):
    plan = ExecutionPlan(
        status="ready",
        pipelines=[
            PlannedPipeline("database"),
        ],
    )

    output = tmp_path / "execution.plan.json"

    write_plan_report(plan, output)

    assert output.exists()

    report = json.loads(output.read_text(encoding="utf-8"))

    assert report["event_type"] == "pipeline_execution_plan"
    assert report["status"] == "ready"
    assert report["execution_order"] == ["database"]
