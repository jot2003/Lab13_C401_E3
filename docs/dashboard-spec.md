# Dashboard Spec — 6-Panel Observability Dashboard

> **Owner**: D13-T05 (Metrics + Dashboard + Evidence)
> **Data source**: `GET /metrics` and `GET /metrics/timeseries`

---

## Quality Bar (applies to ALL panels)

| Setting | Value |
|---|---|
| Default time range | 1 hour |
| Auto-refresh interval | 15–30 seconds |
| Threshold / SLO lines | Visible on every numeric panel |
| Units | Clearly labeled (ms, %, USD, count) |
| Max panels on main view | 6–8 |

---

## Panel Definitions

### Panel 1 — Latency P50 / P95 / P99
- **Type**: Line chart (time-series)
- **Metrics**: `latency_p50`, `latency_p95`, `latency_p99` (from `/metrics`)
- **Time-series source**: `latency` array from `/metrics/timeseries`
- **Unit**: milliseconds (ms)
- **SLO line**: P95 < 3 000 ms (red dashed)
- **Color scheme**: P50 = green, P95 = orange, P99 = red

### Panel 2 — Traffic (Request Count / QPS)
- **Type**: Bar chart or area chart (time-series)
- **Metrics**: `traffic` (total), `qps` (computed)
- **Time-series source**: `traffic` array from `/metrics/timeseries`
- **Unit**: requests / requests per second
- **Note**: Show cumulative count as big number + QPS trend line

### Panel 3 — Error Rate with Breakdown
- **Type**: Stacked bar chart + big-number gauge
- **Metrics**: `error_rate_pct`, `error_breakdown`
- **Time-series source**: `errors` array from `/metrics/timeseries`
- **Unit**: percentage (%)
- **SLO line**: Error rate < 2 % (red dashed)
- **Breakdown**: Color-code by `error_type`

### Panel 4 — Cost Over Time
- **Type**: Area chart + cumulative big number
- **Metrics**: `avg_cost_usd`, `total_cost_usd`
- **Time-series source**: `cost` array from `/metrics/timeseries`
- **Unit**: USD ($)
- **SLO line**: Daily budget < $2.50 (yellow dashed)

### Panel 5 — Tokens In / Out
- **Type**: Dual-axis bar chart (time-series)
- **Metrics**: `tokens_in_total`, `tokens_out_total`, `avg_tokens_in`, `avg_tokens_out`
- **Time-series source**: `tokens` array from `/metrics/timeseries`
- **Unit**: token count
- **Note**: Show in vs. out as separate colored bars

### Panel 6 — Quality Proxy
- **Type**: Line chart + gauge
- **Metrics**: `quality_avg`, `quality_min`, `quality_max`
- **Time-series source**: `quality` array from `/metrics/timeseries`
- **Unit**: score (0.0–1.0)
- **SLO line**: Avg quality > 0.7 (green dashed)
- **Note**: Can be heuristic similarity, thumbs-up rate, or regenerate rate

---

## How to Build (step-by-step)

1. Start the app: `uvicorn app.main:app --reload`
2. Generate traffic: `python scripts/load_test.py --concurrency 5`
3. Open `/metrics` in browser to verify data is flowing.
4. Import data into your dashboard tool (Grafana, Streamlit, or spreadsheet).
5. Create each panel per spec above.
6. Add SLO threshold lines.
7. Set auto-refresh to 15 s.
8. Screenshot all 6 panels for `docs/grading-evidence.md`.
