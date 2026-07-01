from pathlib import Path

from pipeline_execution_planner.cli import main


def test_cli_help(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["pipeline-planner"])

    exit_code = main()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Build RADAR Services pipeline execution plans" in captured.out


def test_cli_plan_ready(tmp_path: Path, monkeypatch, capsys):
    dependency_report = tmp_path / "dependency.report.json"
    validation_report = tmp_path / "validation.report.json"

    dependency_report.write_text(
        """
{
  "ok": true,
  "execution_order": ["database", "prepare", "workflow"],
  "issues": []
}
""",
        encoding="utf-8",
    )

    validation_report.write_text(
        """
{
  "ok": true,
  "error_count": 0,
  "issues": []
}
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "pipeline-planner",
            "plan",
            "--dependency-report",
            str(dependency_report),
            "--validation-report",
            str(validation_report),
        ],
    )

    exit_code = main()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Execution plan status: ready" in captured.out
    assert "Ready pipelines: 3" in captured.out
    assert "- database" in captured.out
    assert "- prepare" in captured.out
    assert "- workflow" in captured.out


def test_cli_plan_blocked(tmp_path: Path, monkeypatch, capsys):
    dependency_report = tmp_path / "dependency.report.json"
    validation_report = tmp_path / "validation.report.json"

    dependency_report.write_text(
        """
{
  "ok": true,
  "execution_order": ["database", "prepare", "workflow"],
  "issues": []
}
""",
        encoding="utf-8",
    )

    validation_report.write_text(
        """
{
  "ok": false,
  "error_count": 1,
  "issues": [
    {
      "code": "file_not_found",
      "message": "File not found.",
      "pipeline_id": "workflow"
    }
  ]
}
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "pipeline-planner",
            "plan",
            "--dependency-report",
            str(dependency_report),
            "--validation-report",
            str(validation_report),
        ],
    )

    exit_code = main()
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Execution plan status: blocked" in captured.out
    assert "Ready pipelines: 2" in captured.out
    assert "Blocked pipelines: 1" in captured.out
    assert "file_not_found" in captured.out


def test_cli_plan_missing_report(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        [
            "pipeline-planner",
            "plan",
            "--dependency-report",
            "missing.dependency.json",
            "--validation-report",
            "missing.validation.json",
        ],
    )

    exit_code = main()
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Execution planning failed to start" in captured.err


def test_cli_plan_report_json(tmp_path: Path, monkeypatch, capsys):
    dependency_report = tmp_path / "dependency.report.json"
    validation_report = tmp_path / "validation.report.json"
    plan_report = tmp_path / "execution.plan.json"

    dependency_report.write_text(
        """
{
  "ok": true,
  "execution_order": ["database", "prepare", "workflow"],
  "issues": []
}
""",
        encoding="utf-8",
    )

    validation_report.write_text(
        """
{
  "ok": true,
  "error_count": 0,
  "issues": []
}
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "pipeline-planner",
            "plan",
            "--dependency-report",
            str(dependency_report),
            "--validation-report",
            str(validation_report),
            "--report-json",
            str(plan_report),
        ],
    )

    exit_code = main()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Execution plan report written:" in captured.out
    assert plan_report.exists()
