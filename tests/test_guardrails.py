from app.guardrails import evaluate_request_scope, evaluate_system_scope


def test_request_scope_breach_detected() -> None:
    breaches = evaluate_request_scope(tokens_in=2000, tokens_out=900, cost_usd=0.03)
    assert "request_tokens_in_max" in breaches
    assert "request_tokens_out_max" in breaches
    assert "request_cost_usd_max" in breaches


def test_system_scope_breach_detected() -> None:
    snapshot = {
        "latency_p95": 7000,
        "error_rate_pct": 12,
        "avg_cost_usd": 3.4,
        "quality_avg": 0.4,
    }
    breaches = evaluate_system_scope(snapshot)
    assert "latency_p95_max_ms" in breaches
    assert "error_rate_pct_max" in breaches
    assert "avg_cost_usd_max" in breaches
    assert "quality_avg_min" in breaches
