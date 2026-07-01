from pathlib import Path

import pytest

from pipeline_execution_planner.dependency_loader import (
    DependencyReportLoadError,
    get_dependency_issues,
    get_dependency_report_status,
    get_execution_order,
    load_dependency_report,
    load_json_file,
)


def test_load_json_file(tmp_path: Path):
    report = tmp_path / "dependency.report.json"
    report.write_text(
        """
{
  "ok": true,
  "execution_order": ["database", "prepare"]
}
""",
        encoding="utf-8",
    )

    payload = load_json_file(report)

    assert payload["ok"] is True
    assert payload["execution_order"] == ["database", "prepare"]


def test_load_missing_json_file():
    with pytest.raises(DependencyReportLoadError, match="Dependency report not found"):
        load_json_file("missing.report.json")


def test_load_invalid_json_file(tmp_path: Path):
    report = tmp_path / "bad.report.json"
    report.write_text("{bad json", encoding="utf-8")

    with pytest.raises(
        DependencyReportLoadError, match="Invalid dependency report JSON"
    ):
        load_json_file(report)


def test_get_dependency_report_status():
    assert get_dependency_report_status({"ok": True}) is True
    assert get_dependency_report_status({"ok": False}) is False


def test_get_execution_order():
    payload = {"execution_order": ["database", "prepare", "workflow"]}

    assert get_execution_order(payload) == ["database", "prepare", "workflow"]


def test_get_execution_order_rejects_invalid_type():
    with pytest.raises(
        DependencyReportLoadError, match="execution_order must be a list"
    ):
        get_execution_order({"execution_order": "database"})


def test_get_execution_order_rejects_invalid_item():
    with pytest.raises(
        DependencyReportLoadError,
        match="execution_order items must be non-empty strings",
    ):
        get_execution_order({"execution_order": ["database", ""]})


def test_get_dependency_issues():
    issues = get_dependency_issues(
        {
            "issues": [
                {
                    "code": "missing_dependency",
                    "message": "Missing dependency: database",
                }
            ]
        }
    )

    assert len(issues) == 1
    assert issues[0]["code"] == "missing_dependency"


def test_get_dependency_issues_rejects_invalid_type():
    with pytest.raises(DependencyReportLoadError, match="issues must be a list"):
        get_dependency_issues({"issues": "bad"})


def test_load_dependency_report_sample():
    payload = load_dependency_report("examples/dependency.report.sample.json")

    assert payload["event_type"] == "pipeline_dependency_analysis"
    assert payload["ok"] is True
    assert get_execution_order(payload) == ["database", "prepare", "workflow"]
