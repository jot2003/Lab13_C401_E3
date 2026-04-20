from __future__ import annotations

import os
from dataclasses import dataclass


def _float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class GuardrailLimits:
    latency_p95_max_ms: float
    error_rate_pct_max: float
    avg_cost_usd_max: float
    quality_avg_min: float
    request_cost_usd_max: float
    request_tokens_in_max: int
    request_tokens_out_max: int


def load_limits() -> GuardrailLimits:
    return GuardrailLimits(
        latency_p95_max_ms=_float_env("LIMIT_LATENCY_P95_MAX_MS", 5000.0),
        error_rate_pct_max=_float_env("LIMIT_ERROR_RATE_PCT_MAX", 5.0),
        avg_cost_usd_max=_float_env("LIMIT_AVG_COST_USD_MAX", 2.5),
        quality_avg_min=_float_env("LIMIT_QUALITY_AVG_MIN", 0.5),
        request_cost_usd_max=_float_env("LIMIT_REQUEST_COST_USD_MAX", 0.02),
        request_tokens_in_max=_int_env("LIMIT_REQUEST_TOKENS_IN_MAX", 1200),
        request_tokens_out_max=_int_env("LIMIT_REQUEST_TOKENS_OUT_MAX", 700),
    )


def evaluate_request_scope(tokens_in: int, tokens_out: int, cost_usd: float) -> list[str]:
    limits = load_limits()
    breaches: list[str] = []
    if cost_usd > limits.request_cost_usd_max:
        breaches.append("request_cost_usd_max")
    if tokens_in > limits.request_tokens_in_max:
        breaches.append("request_tokens_in_max")
    if tokens_out > limits.request_tokens_out_max:
        breaches.append("request_tokens_out_max")
    return breaches


def evaluate_system_scope(metrics_snapshot: dict) -> list[str]:
    limits = load_limits()
    breaches: list[str] = []
    if float(metrics_snapshot.get("latency_p95", 0.0)) > limits.latency_p95_max_ms:
        breaches.append("latency_p95_max_ms")
    if float(metrics_snapshot.get("error_rate_pct", 0.0)) > limits.error_rate_pct_max:
        breaches.append("error_rate_pct_max")
    if float(metrics_snapshot.get("avg_cost_usd", 0.0)) > limits.avg_cost_usd_max:
        breaches.append("avg_cost_usd_max")
    if float(metrics_snapshot.get("quality_avg", 0.0)) < limits.quality_avg_min:
        breaches.append("quality_avg_min")
    return breaches
