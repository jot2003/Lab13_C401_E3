from app import metrics
from app.metrics import percentile


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100


def test_error_rate_is_bounded_to_total_requests() -> None:
    metrics.reset()
    metrics.record_error("RuntimeError")
    metrics.record_error("TimeoutError")
    assert metrics.error_rate() == 100.0


def test_error_rate_mixed_success_and_failure() -> None:
    metrics.reset()
    metrics.record_request(latency_ms=100, cost_usd=0.001, tokens_in=10, tokens_out=20, quality_score=0.9)
    metrics.record_error("RuntimeError")
    assert metrics.error_rate() == 50.0


def test_series_are_pruned_to_max_points() -> None:
    metrics.reset()
    for _ in range(metrics.MAX_SERIES_POINTS + 25):
        metrics.record_request(latency_ms=120, cost_usd=0.01, tokens_in=10, tokens_out=15, quality_score=0.8)
    series = metrics.timeseries_snapshot()
    assert len(series["latency"]) == metrics.MAX_SERIES_POINTS
    assert len(series["traffic"]) == metrics.MAX_SERIES_POINTS


def test_data_attack_summary_updates_snapshot() -> None:
    metrics.reset()
    metrics.record_data_attack_summary(
        {
            "total_records": 10,
            "invalid_records": 4,
            "by_attack_type": {"MISSING_REQUIRED": 3, "WRONG_TYPE": 7},
            "by_error_type": {"required": 2, "type": 2},
        }
    )
    snap = metrics.snapshot()
    assert snap["data_attack_ingestions"] == 1
    assert snap["data_attack_total_records"] == 10
    assert snap["data_attack_invalid_records"] == 4
    assert snap["data_attack_invalid_rate_pct"] == 40.0
