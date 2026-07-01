from pipeline_execution_planner.contract import (
    ExecutionPlan,
    PlannedPipeline,
    PlanIssue,
    blocked_plan,
    ready_plan,
)


def test_planned_pipeline_contract():
    pipeline = PlannedPipeline(
        pipeline_id="database",
        status="ready",
    )

    assert pipeline.pipeline_id == "database"
    assert pipeline.status == "ready"
    assert pipeline.reason is None


def test_plan_issue_contract():
    issue = PlanIssue(
        code="validation_failed",
        message="Validation failed.",
        pipeline_id="workflow",
    )

    assert issue.code == "validation_failed"
    assert issue.message == "Validation failed."
    assert issue.pipeline_id == "workflow"


def test_ready_execution_plan_contract():
    plan = ExecutionPlan(
        status="ready",
        pipelines=[
            PlannedPipeline("database"),
            PlannedPipeline("prepare"),
        ],
    )

    assert plan.ok is True
    assert plan.ready_count == 2
    assert plan.blocked_count == 0
    assert plan.issue_count == 0


def test_blocked_execution_plan_contract():
    plan = ExecutionPlan(
        status="blocked",
        pipelines=[
            PlannedPipeline("workflow", status="blocked", reason="validation_failed"),
        ],
        issues=[
            PlanIssue(
                code="validation_failed",
                message="Validation failed.",
                pipeline_id="workflow",
            )
        ],
    )

    assert plan.ok is False
    assert plan.ready_count == 0
    assert plan.blocked_count == 1
    assert plan.issue_count == 1


def test_ready_plan_helper():
    plan = ready_plan(
        [
            PlannedPipeline("database"),
            PlannedPipeline("prepare"),
        ]
    )

    assert plan.ok is True
    assert plan.ready_count == 2


def test_blocked_plan_helper():
    plan = blocked_plan(
        pipelines=[
            PlannedPipeline(
                "workflow",
                status="blocked",
                reason="dependency_failed",
            )
        ],
        issues=[
            PlanIssue(
                code="dependency_failed",
                message="Dependency analysis failed.",
                pipeline_id="workflow",
            )
        ],
    )

    assert plan.ok is False
    assert plan.blocked_count == 1
    assert plan.issues[0].code == "dependency_failed"
