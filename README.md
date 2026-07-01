# Pipeline Execution Planner MVP

A minimal execution planner for RADAR Services automation pipelines.

## Status

MVP in progress.

## Purpose

Build execution plans from validation and dependency reports before orchestration.

## Target Flow

```text
validation.report.json
dependency.report.json
    ↓
pipeline-planner plan
    ↓
execution.plan.json
    ↓
pipeline orchestrator
```
