from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, UTC
from pathlib import Path

from pipeline_execution_planner.contract import ExecutionPlan


def build_plan_report(plan: ExecutionPlan) -> dict:
    return {
        "event_type": "pipeline_execution_plan",
        "timestamp": datetime.now(UTC).isoformat(),
        "status": plan.status,
        "ok": plan.ok,
        "ready_count": plan.ready_count,
        "blocked_count": plan.blocked_count,
        "issue_count": plan.issue_count,
        "ready_pipelines": [pipeline.pipeline_id for pipeline in plan.ready_pipelines],
        "blocked_pipelines": [asdict(pipeline) for pipeline in plan.blocked_pipelines],
        "execution_order": [pipeline.pipeline_id for pipeline in plan.pipelines],
        "issues": [asdict(issue) for issue in plan.issues],
    }


def write_plan_report(
    plan: ExecutionPlan,
    output_file: Path,
) -> Path:
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = build_plan_report(plan)

    output_file.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    return output_file
