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


st.title("Bảng Điều Khiển Quan Sát Hệ Thống Tuyển Sinh")
st.caption("Phát hiện -> Chẩn đoán -> Xử lý -> Xác nhận hồi phục cho trợ lý tư vấn tuyển sinh.")

with st.sidebar:
    st.subheader("Thông tin hệ thống")
    st.text_input("Địa chỉ API", value=API_BASE_URL, disabled=True)
    if st.button("Tải lại dữ liệu ngay", use_container_width=True):
        st.rerun()

tab_overview, tab_incident, tab_investigation, tab_evidence = st.tabs(
    ["Tổng quan", "Điều khiển sự cố", "Điều tra", "Checklist nộp bài"]
)

with tab_overview:
    st.subheader("Dashboard 6 biểu đồ")
    try:
        metrics = api_get("/metrics")
        ts = api_get("/metrics/timeseries")
    except Exception as exc:  # pragma: no cover - runtime UX fallback
        st.error(f"Không tải được metrics từ API: {exc}")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Độ trễ P95 (ms)", f"{metrics.get('latency_p95', 0):.0f}")
    col2.metric("Tỷ lệ lỗi (%)", f"{metrics.get('error_rate_pct', 0):.2f}")
    col3.metric("Lượt truy cập", f"{metrics.get('traffic', 0)}")
    col4.metric("Chất lượng trung bình", f"{metrics.get('quality_avg', 0):.2f}")

    st.markdown("### Biểu đồ 1: Độ trễ P50/P95/P99")
    latency_series = to_timeseries(ts.get("latency", []), "value")
    if latency_series:
        st.line_chart(latency_series, x="time", y="value")
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
                "error_breakdown": metrics.get("error_breakdown", {}),
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
        st.write({"avg_cost_usd": metrics.get("avg_cost_usd"), "total_cost_usd": metrics.get("total_cost_usd")})

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
    st.write(
        {
            "quality_avg": metrics.get("quality_avg"),
            "quality_min": metrics.get("quality_min"),
            "quality_max": metrics.get("quality_max"),
        }
    )

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
    logs = load_logs()
    st.write(f"Số bản ghi log đã tải: {len(logs)}")

    correlation_filter = st.text_input("Lọc theo correlation_id")
    level_filter = st.selectbox("Lọc theo mức độ log", options=["all", "info", "warning", "error", "critical"])

    filtered = logs
    if correlation_filter.strip():
        filtered = [row for row in filtered if row.get("correlation_id") == correlation_filter.strip()]
    if level_filter != "all":
        filtered = [row for row in filtered if row.get("level") == level_filter]

    st.markdown("### Log gần đây")
    st.json(filtered[-30:])

    st.markdown("### Dữ liệu metrics thô")
    try:
        st.json(api_get("/metrics"))
    except Exception as exc:
        st.error(f"Không tải được /metrics: {exc}")

    st.markdown("### Tracing")
    st.info(
        "Mo Langfuse va loc theo correlation_id tu log ben tren. "
        "Quy trình để tìm lỗi: Metrics -> Traces -> Logs."
    )

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
