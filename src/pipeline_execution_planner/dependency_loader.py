from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class DependencyReportLoadError(Exception):
    """Raised when dependency report cannot be loaded."""


def load_json_file(path: str | Path) -> dict[str, Any]:
    report_path = Path(path)

    if not report_path.exists():
        raise DependencyReportLoadError(f"Dependency report not found: {report_path}")

    if not report_path.is_file():
        raise DependencyReportLoadError(
            f"Dependency report path is not a file: {report_path}"
        )

    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DependencyReportLoadError(
            f"Invalid dependency report JSON: {report_path}"
        ) from exc

    if not isinstance(payload, dict):
        raise DependencyReportLoadError(
            f"Dependency report root must be an object: {report_path}"
        )

    return payload


def get_dependency_report_status(payload: dict[str, Any]) -> bool:
    return payload.get("ok") is True


def get_execution_order(payload: dict[str, Any]) -> list[str]:
    execution_order = payload.get("execution_order", [])

    if not isinstance(execution_order, list):
        raise DependencyReportLoadError("execution_order must be a list")

    result: list[str] = []

    for item in execution_order:
        if not isinstance(item, str) or not item.strip():
            raise DependencyReportLoadError(
                "execution_order items must be non-empty strings"
            )
        result.append(item)

    return result


def get_dependency_issues(payload: dict[str, Any]) -> list[dict[str, Any]]:
    issues = payload.get("issues", [])

    if not isinstance(issues, list):
        raise DependencyReportLoadError("issues must be a list")

    return issues


def load_dependency_report(path: str | Path) -> dict[str, Any]:
    return load_json_file(path)
