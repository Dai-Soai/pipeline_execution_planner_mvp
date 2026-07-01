from pathlib import Path

import pytest

from pipeline_execution_planner.validation_loader import (
    ValidationReportLoadError,
    get_validation_error_count,
    get_validation_issues,
    get_validation_report_status,
    load_json_file,
    load_validation_report,
)


def test_load_json_file(tmp_path: Path):
    report = tmp_path / "validation.report.json"
    report.write_text(
        """
{
  "ok": true,
  "error_count": 0,
  "issues": []
}
""",
        encoding="utf-8",
    )

    payload = load_json_file(report)

    assert payload["ok"] is True
    assert payload["error_count"] == 0
    assert payload["issues"] == []


def test_load_missing_json_file():
    with pytest.raises(ValidationReportLoadError, match="Validation report not found"):
        load_json_file("missing.validation.json")


def test_load_invalid_json_file(tmp_path: Path):
    report = tmp_path / "bad.validation.json"
    report.write_text("{bad json", encoding="utf-8")

    with pytest.raises(
        ValidationReportLoadError, match="Invalid validation report JSON"
    ):
        load_json_file(report)


def test_get_validation_report_status():
    assert get_validation_report_status({"ok": True}) is True
    assert get_validation_report_status({"ok": False}) is False


def test_get_validation_issues():
    issues = get_validation_issues(
        {
            "issues": [
                {
                    "code": "file_not_found",
                    "message": "File not found.",
                    "field": "workflow.workflow_file",
                }
            ]
        }
    )

    assert len(issues) == 1
    assert issues[0]["code"] == "file_not_found"


def test_get_validation_issues_rejects_invalid_type():
    with pytest.raises(ValidationReportLoadError, match="issues must be a list"):
        get_validation_issues({"issues": "bad"})


def test_get_validation_error_count():
    assert get_validation_error_count({"error_count": 0}) == 0
    assert get_validation_error_count({"error_count": 2}) == 2


def test_get_validation_error_count_rejects_invalid_type():
    with pytest.raises(
        ValidationReportLoadError, match="error_count must be an integer"
    ):
        get_validation_error_count({"error_count": "2"})


def test_load_validation_report_sample():
    payload = load_validation_report("examples/validation.report.sample.json")

    assert payload["event_type"] == "pipeline_validation"
    assert payload["ok"] is True
    assert get_validation_error_count(payload) == 0
    assert get_validation_issues(payload) == []
