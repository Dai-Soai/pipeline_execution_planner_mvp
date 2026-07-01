from pipeline_execution_planner.planner import (
    build_execution_plan,
    build_planned_pipelines,
    collect_blocked_pipeline_ids,
    issue_from_payload,
)


def make_dependency_report(ok=True):
    return {
        "ok": ok,
        "execution_order": [
            "database",
            "prepare",
            "workflow",
        ],
        "issues": (
            []
            if ok
            else [
                {
                    "code": "missing_dependency",
                    "message": "Missing dependency: database",
                }
            ]
        ),
    }


def make_validation_report(ok=True):
    return {
        "ok": ok,
        "issues": (
            []
            if ok
            else [
                {
                    "code": "file_not_found",
                    "message": "File not found.",
                    "field": "workflow.workflow_file",
                }
            ]
        ),
    }


def test_issue_from_payload():
    issue = issue_from_payload(
        {
            "code": "missing_dependency",
            "message": "Missing dependency.",
            "pipeline_id": "workflow",
        },
        default_code="dependency_failed",
    )

    assert issue.code == "missing_dependency"
    assert issue.message == "Missing dependency."
    assert issue.pipeline_id == "workflow"


def test_build_execution_plan_ready():
    plan = build_execution_plan(
        dependency_report=make_dependency_report(ok=True),
        validation_report=make_validation_report(ok=True),
    )

    assert plan.ok is True
    assert plan.status == "ready"
    assert plan.ready_count == 3
    assert plan.blocked_count == 0
    assert [pipeline.pipeline_id for pipeline in plan.pipelines] == [
        "database",
        "prepare",
        "workflow",
    ]


def test_build_execution_plan_blocked_by_dependency():
    plan = build_execution_plan(
        dependency_report=make_dependency_report(ok=False),
        validation_report=make_validation_report(ok=True),
    )

    assert plan.ok is False
    assert plan.status == "blocked"
    assert plan.blocked_count == 3
    assert plan.issue_count == 1
    assert plan.issues[0].code == "missing_dependency"


def test_build_execution_plan_blocked_by_validation():
    plan = build_execution_plan(
        dependency_report=make_dependency_report(ok=True),
        validation_report=make_validation_report(ok=False),
    )

    assert plan.ok is False
    assert plan.status == "blocked"
    assert plan.blocked_count == 3
    assert plan.issue_count == 1
    assert plan.issues[0].code == "file_not_found"


def test_build_execution_plan_blocked_by_both_reports():
    plan = build_execution_plan(
        dependency_report=make_dependency_report(ok=False),
        validation_report=make_validation_report(ok=False),
    )

    assert plan.ok is False
    assert plan.status == "blocked"
    assert plan.blocked_count == 3
    assert plan.issue_count == 2


def test_collect_blocked_pipeline_ids():
    issue = issue_from_payload(
        {
            "code": "validation_failed",
            "message": "Validation failed.",
            "pipeline_id": "workflow",
        },
        default_code="validation_failed",
    )

    assert collect_blocked_pipeline_ids([issue]) == {"workflow"}


def test_build_planned_pipelines_with_blocked_ids():
    pipelines = build_planned_pipelines(
        execution_order=["database", "prepare", "workflow"],
        blocked_ids={"workflow"},
    )

    assert pipelines[0].status == "ready"
    assert pipelines[1].status == "ready"
    assert pipelines[2].status == "blocked"
    assert pipelines[2].reason == "plan_blocked"


def test_build_execution_plan_partially_blocked_by_pipeline_id():
    dependency_report = {
        "ok": True,
        "execution_order": ["database", "prepare", "workflow"],
        "issues": [],
    }
    validation_report = {
        "ok": False,
        "issues": [
            {
                "code": "file_not_found",
                "message": "File not found.",
                "pipeline_id": "workflow",
            }
        ],
    }

    plan = build_execution_plan(
        dependency_report=dependency_report,
        validation_report=validation_report,
    )

    assert plan.ok is False
    assert plan.ready_count == 2
    assert plan.blocked_count == 1
    assert plan.blocked_pipelines[0].pipeline_id == "workflow"
