from __future__ import annotations

import time
from collections import Counter
from statistics import mean
from threading import Lock

# ---------- Raw storage ----------
REQUEST_LATENCIES: list[int] = []
REQUEST_COSTS: list[float] = []
REQUEST_TOKENS_IN: list[int] = []
REQUEST_TOKENS_OUT: list[int] = []
ERRORS: Counter[str] = Counter()
GUARDRAIL_BREACHES: Counter[str] = Counter()
DATA_ATTACK_BY_TYPE: Counter[str] = Counter()
DATA_ATTACK_BY_ERROR: Counter[str] = Counter()
TRAFFIC: int = 0
QUALITY_SCORES: list[float] = []
DATA_ATTACK_INGESTIONS: int = 0
DATA_ATTACK_TOTAL_RECORDS: int = 0
DATA_ATTACK_INVALID_RECORDS: int = 0
DATA_ATTACK_LAST_SUMMARY: dict = {}

# ---------- Time-series (for dashboard panels) ----------
LATENCY_SERIES: list[dict] = []   # {"ts": epoch, "value": ms}
COST_SERIES: list[dict] = []      # {"ts": epoch, "value": usd}
TOKENS_SERIES: list[dict] = []    # {"ts": epoch, "tokens_in": n, "tokens_out": n}
ERROR_SERIES: list[dict] = []     # {"ts": epoch, "error_type": str}
QUALITY_SERIES: list[dict] = []   # {"ts": epoch, "value": float}
TRAFFIC_SERIES: list[dict] = []   # {"ts": epoch, "count": 1}

_lock = Lock()
MAX_SERIES_POINTS = 2000
MAX_SAMPLE_POINTS = 5000


def _prune_samples() -> None:
    if len(REQUEST_LATENCIES) > MAX_SAMPLE_POINTS:
        del REQUEST_LATENCIES[:-MAX_SAMPLE_POINTS]
    if len(REQUEST_COSTS) > MAX_SAMPLE_POINTS:
        del REQUEST_COSTS[:-MAX_SAMPLE_POINTS]
    if len(REQUEST_TOKENS_IN) > MAX_SAMPLE_POINTS:
        del REQUEST_TOKENS_IN[:-MAX_SAMPLE_POINTS]
    if len(REQUEST_TOKENS_OUT) > MAX_SAMPLE_POINTS:
        del REQUEST_TOKENS_OUT[:-MAX_SAMPLE_POINTS]
    if len(QUALITY_SCORES) > MAX_SAMPLE_POINTS:
        del QUALITY_SCORES[:-MAX_SAMPLE_POINTS]


def _prune_timeseries() -> None:
    if len(LATENCY_SERIES) > MAX_SERIES_POINTS:
        del LATENCY_SERIES[:-MAX_SERIES_POINTS]
    if len(COST_SERIES) > MAX_SERIES_POINTS:
        del COST_SERIES[:-MAX_SERIES_POINTS]
    if len(TOKENS_SERIES) > MAX_SERIES_POINTS:
        del TOKENS_SERIES[:-MAX_SERIES_POINTS]
    if len(ERROR_SERIES) > MAX_SERIES_POINTS:
        del ERROR_SERIES[:-MAX_SERIES_POINTS]
    if len(QUALITY_SERIES) > MAX_SERIES_POINTS:
        del QUALITY_SERIES[:-MAX_SERIES_POINTS]
    if len(TRAFFIC_SERIES) > MAX_SERIES_POINTS:
        del TRAFFIC_SERIES[:-MAX_SERIES_POINTS]


def record_request(latency_ms: int, cost_usd: float, tokens_in: int, tokens_out: int, quality_score: float) -> None:
    global TRAFFIC
    now = time.time()
    with _lock:
        TRAFFIC += 1
        REQUEST_LATENCIES.append(latency_ms)
        REQUEST_COSTS.append(cost_usd)
        REQUEST_TOKENS_IN.append(tokens_in)
        REQUEST_TOKENS_OUT.append(tokens_out)
        QUALITY_SCORES.append(quality_score)

        # Time-series for dashboard panels
        LATENCY_SERIES.append({"ts": now, "value": latency_ms})
        COST_SERIES.append({"ts": now, "value": cost_usd})
        TOKENS_SERIES.append({"ts": now, "tokens_in": tokens_in, "tokens_out": tokens_out})
        QUALITY_SERIES.append({"ts": now, "value": quality_score})
        TRAFFIC_SERIES.append({"ts": now, "count": 1})
        _prune_samples()
        _prune_timeseries()


def record_error(error_type: str) -> None:
    global TRAFFIC
    now = time.time()
    with _lock:
        # Count failed requests in total traffic as well.
        TRAFFIC += 1
        ERRORS[error_type] += 1
        ERROR_SERIES.append({"ts": now, "error_type": error_type})
        TRAFFIC_SERIES.append({"ts": now, "count": 1})
        _prune_timeseries()


def record_guardrail_breach(kind: str) -> None:
    with _lock:
        GUARDRAIL_BREACHES[kind] += 1


def record_data_attack_summary(summary: dict) -> None:
    global DATA_ATTACK_INGESTIONS, DATA_ATTACK_TOTAL_RECORDS, DATA_ATTACK_INVALID_RECORDS, DATA_ATTACK_LAST_SUMMARY
    with _lock:
        DATA_ATTACK_INGESTIONS += 1
        total_records = int(summary.get("total_records", 0))
        invalid_records = int(summary.get("invalid_records", 0))
        DATA_ATTACK_TOTAL_RECORDS += total_records
        DATA_ATTACK_INVALID_RECORDS += invalid_records
        DATA_ATTACK_BY_TYPE.update(summary.get("by_attack_type", {}))
        DATA_ATTACK_BY_ERROR.update(summary.get("by_error_type", {}))
        DATA_ATTACK_LAST_SUMMARY = dict(summary)


def percentile(values: list[int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])


def error_rate() -> float:
    """Total errors / total requests as a percentage."""
    total_errors = sum(ERRORS.values())
    if TRAFFIC == 0:
        return 0.0
    return round((total_errors / TRAFFIC) * 100, 2)


def snapshot() -> dict:
    """Full metrics snapshot aligned with 6-panel dashboard spec."""
    with _lock:
        return {
            # Panel 1: Latency P50/P95/P99
            "traffic": TRAFFIC,
            "latency_p50": percentile(REQUEST_LATENCIES, 50),
            "latency_p95": percentile(REQUEST_LATENCIES, 95),
            "latency_p99": percentile(REQUEST_LATENCIES, 99),
            # Panel 2: Traffic / QPS
            "qps": round(TRAFFIC / max(1, (time.time() - TRAFFIC_SERIES[0]["ts"])), 2) if TRAFFIC_SERIES else 0.0,
            # Panel 3: Error rate + breakdown
            "error_rate_pct": error_rate(),
            "error_breakdown": dict(ERRORS),
            "guardrail_breaches": dict(GUARDRAIL_BREACHES),
            "data_attack_ingestions": DATA_ATTACK_INGESTIONS,
            "data_attack_total_records": DATA_ATTACK_TOTAL_RECORDS,
            "data_attack_invalid_records": DATA_ATTACK_INVALID_RECORDS,
            "data_attack_invalid_rate_pct": round((DATA_ATTACK_INVALID_RECORDS / DATA_ATTACK_TOTAL_RECORDS) * 100, 2)
            if DATA_ATTACK_TOTAL_RECORDS
            else 0.0,
            "data_attack_by_type": dict(DATA_ATTACK_BY_TYPE),
            "data_attack_by_error": dict(DATA_ATTACK_BY_ERROR),
            "data_attack_last_summary": dict(DATA_ATTACK_LAST_SUMMARY),
            # Panel 4: Cost over time
            "avg_cost_usd": round(mean(REQUEST_COSTS), 4) if REQUEST_COSTS else 0.0,
            "total_cost_usd": round(sum(REQUEST_COSTS), 4),
            # Panel 5: Tokens in/out
            "tokens_in_total": sum(REQUEST_TOKENS_IN),
            "tokens_out_total": sum(REQUEST_TOKENS_OUT),
            "avg_tokens_in": round(mean(REQUEST_TOKENS_IN), 1) if REQUEST_TOKENS_IN else 0,
            "avg_tokens_out": round(mean(REQUEST_TOKENS_OUT), 1) if REQUEST_TOKENS_OUT else 0,
            # Panel 6: Quality proxy
            "quality_avg": round(mean(QUALITY_SCORES), 4) if QUALITY_SCORES else 0.0,
            "quality_min": round(min(QUALITY_SCORES), 4) if QUALITY_SCORES else 0.0,
            "quality_max": round(max(QUALITY_SCORES), 4) if QUALITY_SCORES else 0.0,
        }


def timeseries_snapshot() -> dict:
    """Return time-series data for dashboard chart rendering."""
    with _lock:
        return {
            "latency": list(LATENCY_SERIES),
            "cost": list(COST_SERIES),
            "tokens": list(TOKENS_SERIES),
            "errors": list(ERROR_SERIES),
            "quality": list(QUALITY_SERIES),
            "traffic": list(TRAFFIC_SERIES),
        }


def reset() -> None:
    """Reset all metrics (useful for testing)."""
    global TRAFFIC, DATA_ATTACK_INGESTIONS, DATA_ATTACK_TOTAL_RECORDS, DATA_ATTACK_INVALID_RECORDS, DATA_ATTACK_LAST_SUMMARY
    with _lock:
        TRAFFIC = 0
        REQUEST_LATENCIES.clear()
        REQUEST_COSTS.clear()
        REQUEST_TOKENS_IN.clear()
        REQUEST_TOKENS_OUT.clear()
        ERRORS.clear()
        GUARDRAIL_BREACHES.clear()
        DATA_ATTACK_BY_TYPE.clear()
        DATA_ATTACK_BY_ERROR.clear()
        QUALITY_SCORES.clear()
        DATA_ATTACK_INGESTIONS = 0
        DATA_ATTACK_TOTAL_RECORDS = 0
        DATA_ATTACK_INVALID_RECORDS = 0
        DATA_ATTACK_LAST_SUMMARY = {}
        LATENCY_SERIES.clear()
        COST_SERIES.clear()
        TOKENS_SERIES.clear()
        ERROR_SERIES.clear()
        QUALITY_SERIES.clear()
        TRAFFIC_SERIES.clear()
