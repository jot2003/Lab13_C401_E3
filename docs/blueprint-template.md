# Day 13 Observability Lab Report

## 1. Team Metadata
- Group: C401_E3
- Repo: https://github.com/jot2003/Lab13_C401_E3
- Members:
  - Member A: Dang Dinh Tu Anh (2A202600019) | Role: Correlation Middleware
  - Member B: Quach Gia Duoc (2A202600423) | Role: Logging & PII
  - Member C: Pham Quoc Dung (2A202600490) | Role: Tracing & Enrichment
  - Member D: Nguyen Thanh Nam (2A202600205) | Role: SLO & Alerts
  - Member E: Hoang Kim Tri Thanh (2A202600372) | Role: Metrics, Dashboard, Demo & Report

---

## 2. Group Performance
- Validate logs score: 100/100
- Total traces: 74
- PII leaks found: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- Correlation proof screenshot: `docs/evidence/03-correlation-proof.png`
- PII redaction screenshot: `docs/evidence/04-pii-redaction.png`
- Trace waterfall screenshot: `docs/evidence/02-trace-waterfall.png`
- Trace explanation: Span `agent.run` thể hiện rõ chuỗi `rag.retrieve -> llm.generate`; cùng một `correlation_id` được nối xuyên qua response header, trace metadata và JSON logs nên truy vết root cause từ dashboard sang traces/logs được đảm bảo.

### 3.2 Dashboard & SLOs
- Dashboard screenshot (6 panels): `docs/evidence/05-dashboard-6-panels.png`
- SLO table:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 1098ms |
| Error Rate | < 2% | 28d | 0.00% (baseline, incident off) |
| Cost Budget | < $2.5/day | 1d | 0.0016 USD/request (avg baseline) |

### 3.3 Alerts & Runbook
- Alert rules screenshot: `docs/evidence/06-alert-rules.png`
- Sample runbook link: `docs/alerts.md#2-high-error-rate`

---

## 4. Incident Response (Group)
- Scenario: `cost_spike` + `tool_fail` (combined stress case)
- Symptoms observed: `avg_cost_usd` và `tokens_out` tăng mạnh khi bật `cost_spike`; khi bật thêm `tool_fail` thì `error_rate_pct` tăng, dashboard hiển thị `system_scope_breaches`.
- Root cause evidence: Trace IDs trong `docs/evidence/04-attack-case-notes.txt` + log event `request_scope_breach` + `/metrics` snapshot.
- Fix action: Bổ sung guardrail max-scope runtime, tách 2 tầng observability (runtime incident vs data attack JSONL), và ingest JSONL vào metrics homepage.
- Preventive measure: Giữ ngưỡng guardrail qua env `LIMIT_*`, theo dõi `guardrail_breaches`, chạy định kỳ ingestion attack dataset để kiểm thử hợp đồng dữ liệu.

---

## 5. Individual Contributions & Evidence

### Dang Dinh Tu Anh (2A202600019)
- Tasks completed: Hoàn thiện `CorrelationIdMiddleware`, thêm kiểm thử middleware, và dựng data contract admissions (schema + clean/attack datasets).
- Evidence links:
  - https://github.com/jot2003/Lab13_C401_E3/commit/c21a6a1
  - https://github.com/jot2003/Lab13_C401_E3/commit/a5a2e99
  - https://github.com/jot2003/Lab13_C401_E3/commit/9acd041

### Quach Gia Duoc (2A202600423)
- Tasks completed: Chuẩn hóa logging schema, mở rộng regex + coverage cho PII scrubber, enrich log context cho API.
- Evidence links:
  - https://github.com/jot2003/Lab13_C401_E3/commit/01fefd2
  - https://github.com/jot2003/Lab13_C401_E3/commit/38ec00a
  - https://github.com/jot2003/Lab13_C401_E3/commit/5bb3f37

### Pham Quoc Dung (2A202600490)
- Tasks completed:
  - Hoàn thành D13-T03 tracing pipeline: instrument spans trong `app/tracing.py`, `app/agent.py`, `app/main.py`.
  - Sửa propagation `correlation_id` xuyên suốt các spans và metadata để truy vết nhất quán từ response header -> trace -> JSON logs.
  - Nâng cấp tương thích Langfuse v3 API và chuẩn hóa metadata tracing (`feature`, `session_id`, `request_id`) để lọc theo domain use-case.
  - Xác minh đầu ra tracing với tối thiểu 10 traces (thực tế 74 traces) và bàn giao bộ evidence phục vụ demo/incident debug.
- Evidence links:
  - https://github.com/jot2003/Lab13_C401_E3/commit/ae8f2bf
  - https://github.com/jot2003/Lab13_C401_E3/commit/92d3fc8
  - https://github.com/jot2003/Lab13_C401_E3/commit/e0904c7
  - docs/evidence/01-langfuse-trace-list.png
  - docs/evidence/02-trace-waterfall.png
  - docs/evidence/03-correlation-proof.png
  - docs/evidence/tracing-summary.json

### Nguyen Thanh Nam (2A202600205)
- Tasks completed: Thiết kế SLO/alerts theo domain tuyển sinh, đồng bộ metric key, cập nhật runbook và mapping attack-to-alert.
- Evidence links:
  - https://github.com/jot2003/Lab13_C401_E3/commit/797b721
  - https://github.com/jot2003/Lab13_C401_E3/commit/51d57d2
  - https://github.com/jot2003/Lab13_C401_E3/commit/392df10

### Hoang Kim Tri Thanh (2A202600372)
- Tasks completed: Dẫn dắt D13-T05/T00, hoàn thiện dashboard Streamlit tiếng Việt, tối ưu metrics/error_rate, thêm guardrails max-scope, tích hợp ingest JSONL vào homepage metrics, và chốt evidence + release gate.
- Evidence links:
  - https://github.com/jot2003/Lab13_C401_E3/commit/d8248b8
  - https://github.com/jot2003/Lab13_C401_E3/commit/14c84c4
  - https://github.com/jot2003/Lab13_C401_E3/commit/ad74213

---

## 6. Bonus Items (Optional)
- Cost optimization: Có guardrail giới hạn cost per-request và system-level max scope để phát hiện cost spike sớm; evidence: commit `14c84c4`.
- Audit logs: Chưa tách riêng `data/audit.jsonl` trong bản nộp hiện tại.
- Custom metric: Bổ sung metric data attack (`data_attack_invalid_rate_pct`, breakdown theo `attack_type`/`error_type`) và guardrail breach counters; evidence: commit `ad74213`.
