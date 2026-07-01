from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ValidationReportLoadError(Exception):
    """Raised when validation report cannot be loaded."""


def load_json_file(path: str | Path) -> dict[str, Any]:
    report_path = Path(path)

    if not report_path.exists():
        raise ValidationReportLoadError(f"Validation report not found: {report_path}")

    if not report_path.is_file():
        raise ValidationReportLoadError(
            f"Validation report path is not a file: {report_path}"
        )

    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationReportLoadError(
            f"Invalid validation report JSON: {report_path}"
        ) from exc

    if not isinstance(payload, dict):
        raise ValidationReportLoadError(
            f"Validation report root must be an object: {report_path}"
        )

    return payload


def get_validation_report_status(payload: dict[str, Any]) -> bool:
    return payload.get("ok") is True


def get_validation_issues(payload: dict[str, Any]) -> list[dict[str, Any]]:
    issues = payload.get("issues", [])

    if not isinstance(issues, list):
        raise ValidationReportLoadError("issues must be a list")

    return issues


def get_validation_error_count(payload: dict[str, Any]) -> int:
    error_count = payload.get("error_count", 0)

    if not isinstance(error_count, int):
        raise ValidationReportLoadError("error_count must be an integer")

    return error_count


def load_validation_report(path: str | Path) -> dict[str, Any]:
    return load_json_file(path)
