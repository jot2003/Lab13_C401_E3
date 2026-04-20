from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from jsonschema import Draft7Validator
from structlog.contextvars import bind_contextvars

from .agent import LabAgent
from .guardrails import evaluate_request_scope, evaluate_system_scope, load_limits
from .incidents import disable, enable, status
from .logging_config import configure_logging, get_logger
from .metrics import record_data_attack_summary, record_error, record_guardrail_breach, snapshot, timeseries_snapshot
from .middleware import CorrelationIdMiddleware
from .pii import hash_user_id, summarize_text
from .schemas import ChatRequest, ChatResponse
from .tracing import tracing_enabled

configure_logging()
log = get_logger()
app = FastAPI(title="Day 13 Observability Lab")
app.add_middleware(CorrelationIdMiddleware)
agent = LabAgent()
ADMISSIONS_SCHEMA_PATH = Path("data/admissions_schema.json")
ADMISSIONS_DATASETS = {
    "clean": Path("data/admissions_clean.jsonl"),
    "attack": Path("data/admissions_attack.jsonl"),
}


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def _analyze_admissions_dataset(dataset: str) -> dict:
    if dataset not in ADMISSIONS_DATASETS:
        raise HTTPException(status_code=404, detail=f"Unknown dataset: {dataset}")
    if not ADMISSIONS_SCHEMA_PATH.exists():
        raise HTTPException(status_code=500, detail=f"Schema not found: {ADMISSIONS_SCHEMA_PATH}")

    schema = json.loads(ADMISSIONS_SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft7Validator(schema)
    path = ADMISSIONS_DATASETS[dataset]
    rows = _load_jsonl(path)
    if not rows:
        raise HTTPException(status_code=400, detail=f"Dataset not found or empty: {path}")

    by_attack = Counter()
    by_error = Counter()
    invalid_records = 0
    sample_errors: list[dict] = []
    for idx, row in enumerate(rows, 1):
        working = dict(row)
        attack_type = working.get("_attack_type", "UNKNOWN")
        by_attack[attack_type] += 1
        if dataset == "attack":
            # Ignore metadata keys so validation focuses on domain fields.
            working.pop("_attack_type", None)
            working.pop("_attack_desc", None)

        errors = sorted(validator.iter_errors(working), key=lambda e: e.path)
        if not errors:
            continue
        invalid_records += 1
        first = errors[0]
        by_error[first.validator] += 1
        if len(sample_errors) < 12:
            sample_errors.append(
                {
                    "dong": idx,
                    "attack_type": attack_type,
                    "loi_dau_tien": first.message,
                    "truong": ".".join(str(part) for part in first.absolute_path) or "(root)",
                }
            )

    summary = {
        "dataset": dataset,
        "dataset_path": str(path),
        "total_records": len(rows),
        "invalid_records": invalid_records,
        "valid_records": len(rows) - invalid_records,
        "invalid_rate_pct": round((invalid_records / len(rows)) * 100, 2) if rows else 0.0,
        "by_attack_type": dict(by_attack),
        "by_error_type": dict(by_error),
        "sample_errors": sample_errors,
    }
    return summary


@app.on_event("startup")
async def startup() -> None:
    log.info(
        "app_started",
        service=os.getenv("APP_NAME", "day13-observability-lab"),
        env=os.getenv("APP_ENV", "dev"),
        payload={"tracing_enabled": tracing_enabled()},
    )


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "tracing_enabled": tracing_enabled(), "incidents": status()}


@app.get("/metrics")
async def metrics() -> dict:
    data = snapshot()
    data["scope_limits"] = load_limits().__dict__
    data["system_scope_breaches"] = evaluate_system_scope(data)
    return data


@app.get("/metrics/timeseries")
async def metrics_timeseries() -> dict:
    return timeseries_snapshot()


@app.post("/ingest/admissions/{dataset}")
async def ingest_admissions_dataset(dataset: str, request: Request) -> dict:
    summary = _analyze_admissions_dataset(dataset)
    record_data_attack_summary(summary)
    log.info(
        "data_attack_ingested",
        service="api",
        payload={
            "dataset": dataset,
            "invalid_records": summary["invalid_records"],
            "total_records": summary["total_records"],
        },
        correlation_id=request.state.correlation_id,
    )
    return summary


@app.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    bind_contextvars(
        user_id_hash=hash_user_id(body.user_id),
        session_id=body.session_id,
        feature=body.feature,
        model=agent.model,
        env=os.getenv("APP_ENV", "dev"),
    )
    
    log.info(
        "request_received",
        service="api",
        payload={"message_preview": summarize_text(body.message)},
    )
    try:
        result = agent.run(
            user_id=body.user_id,
            feature=body.feature,
            session_id=body.session_id,
            message=body.message,
            correlation_id=request.state.correlation_id,
        )
        log.info(
            "response_sent",
            service="api",
            latency_ms=result.latency_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            payload={"answer_preview": summarize_text(result.answer)},
        )
        guardrail_breaches = evaluate_request_scope(
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
        )
        if guardrail_breaches:
            for breach in guardrail_breaches:
                record_guardrail_breach(breach)
            log.warning(
                "request_scope_breach",
                service="api",
                payload={
                    "breaches": guardrail_breaches,
                    "tokens_in": result.tokens_in,
                    "tokens_out": result.tokens_out,
                    "cost_usd": result.cost_usd,
                },
            )
        return ChatResponse(
            answer=result.answer,
            correlation_id=request.state.correlation_id,
            latency_ms=result.latency_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            quality_score=result.quality_score,
            guardrail_breaches=guardrail_breaches,
        )
    except Exception as exc:  # pragma: no cover
        error_type = type(exc).__name__
        record_error(error_type)
        log.error(
            "request_failed",
            service="api",
            error_type=error_type,
            payload={"detail": str(exc), "message_preview": summarize_text(body.message)},
        )
        raise HTTPException(status_code=500, detail=error_type) from exc


@app.post("/incidents/{name}/enable")
async def enable_incident(name: str) -> JSONResponse:
    try:
        enable(name)
        log.warning("incident_enabled", service="control", payload={"name": name})
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/incidents/{name}/disable")
async def disable_incident(name: str) -> JSONResponse:
    try:
        disable(name)
        log.warning("incident_disabled", service="control", payload={"name": name})
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
