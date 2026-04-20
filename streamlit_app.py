from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
LOG_PATH = Path(os.getenv("LOG_PATH", "data/logs.jsonl"))
DEFAULT_TIMEOUT = 15.0
SLO_THRESHOLDS = {
    "latency_p95": 3000.0,
    "error_rate_pct": 2.0,
    "avg_cost_usd": 2.5,
    "quality_avg_min": 0.75,
}

st.set_page_config(
    page_title="Bảng Điều Khiển Quan Sát Tuyển Sinh",
    page_icon="🎓",
    layout="wide",
)


def api_get(path: str) -> dict[str, Any]:
    with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
        response = client.get(f"{API_BASE_URL}{path}")
        response.raise_for_status()
        return response.json()


def api_post(path: str) -> dict[str, Any]:
    with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
        response = client.post(f"{API_BASE_URL}{path}")
        response.raise_for_status()
        return response.json()


def api_post_json(path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
        response = client.post(f"{API_BASE_URL}{path}", json=payload or {})
        response.raise_for_status()
        return response.json()


def run_load_test(concurrency: int) -> tuple[bool, str]:
    env = os.environ.copy()
    env["API_BASE_URL"] = API_BASE_URL
    command = [sys.executable, "scripts/load_test.py", "--concurrency", str(concurrency)]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, env=env)
        return True, result.stdout[-3000:]
    except subprocess.CalledProcessError as exc:
        return False, (exc.stdout + "\n" + exc.stderr)[-3000:]


def load_logs() -> list[dict[str, Any]]:
    if not LOG_PATH.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def to_timeseries(series: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for item in series:
        ts = item.get("ts")
        value = item.get(field)
        if ts is None or value is None:
            continue
        output.append(
            {
                "time": datetime.fromtimestamp(ts).strftime("%H:%M:%S"),
                field: value,
            }
        )
    return output


def fetch_observability_data() -> tuple[dict[str, Any] | None, dict[str, Any] | None, str | None]:
    try:
        metrics = api_get("/metrics")
        timeseries = api_get("/metrics/timeseries")
        return metrics, timeseries, None
    except Exception as exc:  # pragma: no cover - runtime UX fallback
        return None, None, str(exc)


def build_latency_percentile_series(latency_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    values: list[int] = []
    output: list[dict[str, Any]] = []
    for row in latency_rows:
        ts = row.get("ts")
        value = row.get("value")
        if ts is None or value is None:
            continue
        values.append(int(value))
        sorted_values = sorted(values)
        size = len(sorted_values)
        p50 = sorted_values[max(0, round(0.50 * size + 0.5) - 1)]
        p95 = sorted_values[max(0, round(0.95 * size + 0.5) - 1)]
        p99 = sorted_values[max(0, round(0.99 * size + 0.5) - 1)]
        output.append(
            {
                "time": datetime.fromtimestamp(ts).strftime("%H:%M:%S"),
                "p50": p50,
                "p95": p95,
                "p99": p99,
            }
        )
    return output


def render_breakdown(title: str, data: dict[str, int], x_key: str) -> None:
    st.markdown(title)
    if not data:
        st.info("Chưa có dữ liệu để phân loại.")
        return
    chart_rows = [{x_key: key, "count": val} for key, val in data.items()]
    st.bar_chart(chart_rows, x=x_key, y="count")
    st.write(data)


st.title("Bảng Điều Khiển Quan Sát Hệ Thống Tuyển Sinh")
st.caption("Phát hiện -> Chẩn đoán -> Xử lý -> Xác nhận hồi phục cho trợ lý tư vấn tuyển sinh.")

with st.sidebar:
    st.subheader("Thông tin hệ thống")
    st.text_input("Địa chỉ API", value=API_BASE_URL, disabled=True)
    refresh_mode = st.selectbox(
        "Tự động làm mới",
        options=["Tắt", "15 giây", "30 giây"],
        index=1,
        help="Dùng để dashboard tự cập nhật khi đang demo.",
    )
    refresh_seconds = {"Tắt": 0, "15 giây": 15, "30 giây": 30}[refresh_mode]
    if refresh_seconds > 0 and hasattr(st, "autorefresh"):
        st.autorefresh(interval=refresh_seconds * 1000, key="auto_refresh")
    st.caption(f"Cập nhật lần cuối: {datetime.now().strftime('%H:%M:%S')}")
    if st.button("Tải lại dữ liệu ngay", use_container_width=True):
        st.rerun()

tab_overview, tab_incident, tab_investigation, tab_evidence = st.tabs(
    ["Tổng quan", "Điều khiển sự cố", "Điều tra", "Checklist nộp bài"]
)

metrics, ts, metrics_error = fetch_observability_data()

with tab_overview:
    st.subheader("Dashboard 6 biểu đồ")
    st.info(
        "Tầng 1 - Runtime Incident Monitor: biểu đồ bên dưới phản ánh tác động realtime từ 3 sự cố "
        "`rag_slow`, `tool_fail`, `cost_spike`."
    )
    if metrics_error or metrics is None or ts is None:
        st.error(f"Không tải được metrics từ API: {metrics_error}")
        st.warning("Bạn vẫn có thể sang tab Điều khiển sự cố hoặc Điều tra để tiếp tục thao tác.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(
            "Độ trễ P95 (ms)",
            f"{metrics.get('latency_p95', 0):.0f}",
            delta=f"SLO <= {SLO_THRESHOLDS['latency_p95']:.0f}",
        )
        col2.metric(
            "Tỷ lệ lỗi (%)",
            f"{metrics.get('error_rate_pct', 0):.2f}",
            delta=f"SLO <= {SLO_THRESHOLDS['error_rate_pct']:.2f}",
        )
        col3.metric("Lượt truy cập", f"{metrics.get('traffic', 0)}")
        col4.metric(
            "Chất lượng trung bình",
            f"{metrics.get('quality_avg', 0):.2f}",
            delta=f"SLO >= {SLO_THRESHOLDS['quality_avg_min']:.2f}",
        )
        da1, da2, da3, da4 = st.columns(4)
        da1.metric("Số lần ingest JSONL", f"{metrics.get('data_attack_ingestions', 0)}")
        da2.metric("Tổng records JSONL", f"{metrics.get('data_attack_total_records', 0)}")
        da3.metric("Tổng records lỗi schema", f"{metrics.get('data_attack_invalid_records', 0)}")
        da4.metric("Tỷ lệ lỗi data attack (%)", f"{metrics.get('data_attack_invalid_rate_pct', 0):.2f}")

        st.markdown("### Biểu đồ 1: Độ trễ P50/P95/P99")
        percentile_series = build_latency_percentile_series(ts.get("latency", []))
        if percentile_series:
            st.line_chart(percentile_series, x="time", y=["p50", "p95", "p99"])
            st.caption(f"Ngưỡng SLO độ trễ P95: <= {SLO_THRESHOLDS['latency_p95']:.0f} ms")
        else:
            st.info("Chưa có dữ liệu độ trễ. Hãy tạo traffic bằng nút load test.")
        st.write(
            {
                "latency_p50": metrics.get("latency_p50"),
                "latency_p95": metrics.get("latency_p95"),
                "latency_p99": metrics.get("latency_p99"),
            }
        )

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Biểu đồ 2: Traffic / QPS")
            traffic_series = to_timeseries(ts.get("traffic", []), "count")
            if traffic_series:
                st.area_chart(traffic_series, x="time", y="count")
            st.write({"traffic": metrics.get("traffic"), "qps": metrics.get("qps")})

            st.markdown("### Biểu đồ 3: Tỷ lệ lỗi + Phân loại lỗi")
            st.write(
                {
                    "error_rate_pct": metrics.get("error_rate_pct"),
                    "error_rate_slo_max": SLO_THRESHOLDS["error_rate_pct"],
                    "error_breakdown": metrics.get("error_breakdown", {}),
                    "guardrail_breaches": metrics.get("guardrail_breaches", {}),
                }
            )
            error_rows = ts.get("errors", [])
            if error_rows:
                by_type: dict[str, int] = {}
                for row in error_rows:
                    key = row.get("error_type", "unknown")
                    by_type[key] = by_type.get(key, 0) + 1
                st.bar_chart([{"error_type": k, "count": v} for k, v in by_type.items()], x="error_type", y="count")

        with c2:
            st.markdown("### Biểu đồ 4: Chi phí theo thời gian")
            cost_series = to_timeseries(ts.get("cost", []), "value")
            if cost_series:
                st.line_chart(cost_series, x="time", y="value")
            st.write(
                {
                    "avg_cost_usd": metrics.get("avg_cost_usd"),
                    "total_cost_usd": metrics.get("total_cost_usd"),
                    "avg_cost_slo_max": SLO_THRESHOLDS["avg_cost_usd"],
                }
            )

            st.markdown("### Biểu đồ 5: Token vào / ra")
            token_rows = []
            for row in ts.get("tokens", []):
                token_rows.append(
                    {
                        "time": datetime.fromtimestamp(row["ts"]).strftime("%H:%M:%S"),
                        "tokens_in": row.get("tokens_in", 0),
                        "tokens_out": row.get("tokens_out", 0),
                    }
                )
            if token_rows:
                st.line_chart(token_rows, x="time", y=["tokens_in", "tokens_out"])
            st.write(
                {
                    "tokens_in_total": metrics.get("tokens_in_total"),
                    "tokens_out_total": metrics.get("tokens_out_total"),
                    "avg_tokens_in": metrics.get("avg_tokens_in"),
                    "avg_tokens_out": metrics.get("avg_tokens_out"),
                }
            )

        st.markdown("### Biểu đồ 6: Chỉ số chất lượng")
        quality_series = to_timeseries(ts.get("quality", []), "value")
        if quality_series:
            st.line_chart(quality_series, x="time", y="value")
            st.caption(f"Ngưỡng SLO chất lượng: >= {SLO_THRESHOLDS['quality_avg_min']:.2f}")
        st.write(
            {
                "quality_avg": metrics.get("quality_avg"),
                "quality_min": metrics.get("quality_min"),
                "quality_max": metrics.get("quality_max"),
            }
        )

        st.markdown("### Trạng thái max scope của hệ thống")
        st.write(
            {
                "scope_limits": metrics.get("scope_limits", {}),
                "system_scope_breaches": metrics.get("system_scope_breaches", []),
            }
        )
        if metrics.get("system_scope_breaches"):
            st.error("Hệ thống đang vượt max scope ở các chỉ số trên.")
        else:
            st.success("Tất cả chỉ số hệ thống đang trong max scope.")

with tab_incident:
    st.subheader("Điều khiển sự cố")
    try:
        health = api_get("/health")
        incidents = health.get("incidents", {})
        st.json(incidents)
    except Exception as exc:
        st.error(f"Không lấy được trạng thái sự cố: {exc}")
        incidents = {}

    col_a, col_b, col_c = st.columns(3)
    for col, incident in zip((col_a, col_b, col_c), ("rag_slow", "tool_fail", "cost_spike")):
        with col:
            st.markdown(f"#### {incident}")
            if st.button(f"Bật {incident}", key=f"enable_{incident}", use_container_width=True):
                try:
                    api_post(f"/incidents/{incident}/enable")
                    st.success(f"Đã bật {incident}")
                except Exception as exc:
                    st.error(str(exc))
            if st.button(f"Tắt {incident}", key=f"disable_{incident}", use_container_width=True):
                try:
                    api_post(f"/incidents/{incident}/disable")
                    st.success(f"Đã tắt {incident}")
                except Exception as exc:
                    st.error(str(exc))

    st.markdown("### Tạo traffic để test")
    concurrency = st.slider("Số lượng request đồng thời", min_value=1, max_value=20, value=5)
    if st.button("Chạy load test", use_container_width=True):
        ok, output = run_load_test(concurrency)
        if ok:
            st.success("Đã chạy load test xong")
            st.code(output or "(no output)")
        else:
            st.error("Load test thất bại")
            st.code(output or "(no output)")

with tab_investigation:
    st.subheader("Khu vực điều tra")
    st.info(
        "Tầng 2 - Data Attack Analyzer: khu này tách biệt với 3 sự cố runtime để tránh nhầm lẫn "
        "giữa lỗi vận hành và lỗi dữ liệu đầu vào."
    )
    runtime_view, data_attack_view = st.tabs(["Điều tra Runtime", "Điều tra Data Attack JSONL"])

    with runtime_view:
        logs = load_logs()
        st.write(f"Số bản ghi log đã tải: {len(logs)}")

        correlation_filter = st.text_input("Lọc theo correlation_id")
        level_filter = st.selectbox("Lọc theo mức độ log", options=["all", "info", "warning", "error", "critical"])
        max_rows = st.slider("Số dòng log hiển thị gần nhất", min_value=10, max_value=200, value=40, step=10)

        filtered = logs
        if correlation_filter.strip():
            filtered = [row for row in filtered if row.get("correlation_id") == correlation_filter.strip()]
        if level_filter != "all":
            filtered = [row for row in filtered if row.get("level") == level_filter]

        st.markdown("### Log gần đây")
        st.json(filtered[-max_rows:])

        st.markdown("### Dữ liệu metrics thô")
        if metrics is not None:
            st.json(metrics)
        else:
            st.error(f"Không tải được /metrics: {metrics_error}")

        st.markdown("### Tracing")
        st.info(
            "Mở Langfuse và lọc theo correlation_id từ log bên trên. "
            "Quy trình: Metrics -> Traces -> Logs."
        )

    with data_attack_view:
        st.markdown("### Phân tích tấn công dữ liệu admissions")
        st.caption(
            "Nhấn nút nạp để backend ingest JSONL vào metrics. Sau đó trang Tổng quan sẽ cập nhật "
            "các chỉ số data attack ngay."
        )
        col_left, col_right = st.columns(2)
        with col_left:
            if st.button("Nạp admissions_clean vào metrics", use_container_width=True):
                try:
                    summary = api_post_json("/ingest/admissions/clean")
                except Exception as exc:
                    st.error(f"Nạp admissions_clean thất bại: {exc}")
                else:
                    st.success("Đã nạp admissions_clean vào metrics")
                    st.write(
                        {
                            "total_records": summary["total_records"],
                            "valid_records": summary["valid_records"],
                            "invalid_records": summary["invalid_records"],
                            "invalid_rate_pct": summary["invalid_rate_pct"],
                        }
                    )
                    render_breakdown("#### Breakdown theo attack_type", summary["by_attack_type"], "attack_type")
                    render_breakdown("#### Breakdown theo schema_error_type", summary["by_error_type"], "error_type")
                    st.markdown("#### Ví dụ lỗi")
                    st.json(summary["sample_errors"])
                    st.info("Chuyển sang tab Tổng quan để thấy metric data attack vừa cập nhật.")
        with col_right:
            if st.button("Nạp admissions_attack vào metrics", use_container_width=True):
                try:
                    summary = api_post_json("/ingest/admissions/attack")
                except Exception as exc:
                    st.error(f"Nạp admissions_attack thất bại: {exc}")
                else:
                    st.warning("Đã nạp admissions_attack vào metrics")
                    st.write(
                        {
                            "total_records": summary["total_records"],
                            "valid_records": summary["valid_records"],
                            "invalid_records": summary["invalid_records"],
                            "invalid_rate_pct": summary["invalid_rate_pct"],
                        }
                    )
                    render_breakdown("#### Breakdown theo attack_type", summary["by_attack_type"], "attack_type")
                    render_breakdown("#### Breakdown theo schema_error_type", summary["by_error_type"], "error_type")
                    st.markdown("#### Ví dụ lỗi")
                    st.json(summary["sample_errors"])
                    st.info("Chuyển sang tab Tổng quan để thấy metric data attack vừa cập nhật.")

with tab_evidence:
    st.subheader("Checklist bằng chứng (sẵn sàng nộp bài)")
    checks = [
        "Danh sách trace Langfuse >= 10 trace",
        "1 ảnh waterfall trace đầy đủ",
        "Log JSON có correlation_id",
        "Có bằng chứng ẩn PII",
        "Dashboard đủ 6 biểu đồ",
        "Alert rules có runbook link",
        "Điểm validate_logs.py >= 80/100",
    ]
    for item in checks:
        st.checkbox(item, value=False)

    st.markdown("### Tên file ảnh khuyến nghị")
    st.code(
        "\n".join(
            [
                "docs/evidence/01-langfuse-trace-list.png",
                "docs/evidence/02-trace-waterfall.png",
                "docs/evidence/03-json-logs-correlation-id.png",
                "docs/evidence/04-pii-redaction.png",
                "docs/evidence/05-dashboard-6-panels.png",
                "docs/evidence/06-alert-rules.png",
            ]
        )
    )
