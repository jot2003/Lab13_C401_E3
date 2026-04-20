# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: C401_E3
- [REPO_URL]: https://github.com/jot2003/Lab13_C401_E3
- [MEMBERS]:
  - Member A: Dang Dinh Tu Anh (2A202600019) | Role: Correlation Middleware
  - Member B: Quach Gia Duoc (2A202600423) | Role: Logging & PII
  - Member C: Pham Quoc Dung (2A202600490) | Role: Tracing & Enrichment
  - Member D: Nguyen Thanh Nam (2A202600205) | Role: SLO & Alerts
  - Member E: Hoang Kim Tri Thanh (2A202600372) | Role: Metrics, Dashboard, Demo & Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 74
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: `docs/evidence/03-correlation-proof.png`
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: `docs/evidence/04-pii-redaction.png`
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: `docs/evidence/02-trace-waterfall.png`
- [TRACE_WATERFALL_EXPLANATION]: Span `agent.run` thể hiện rõ chuỗi `rag.retrieve -> llm.generate`; cùng một `correlation_id` được nối xuyên qua response header, trace metadata và JSON logs nên truy vết root cause từ dashboard sang traces/logs được đảm bảo.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: `docs/evidence/05-dashboard-6-panels.png`
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 1098ms |
| Error Rate | < 2% | 28d | 0.00% (baseline, incident off) |
| Cost Budget | < $2.5/day | 1d | 0.0016 USD/request (avg baseline) |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: `docs/evidence/06-alert-rules.png`
- [SAMPLE_RUNBOOK_LINK]: `docs/alerts.md#2-high-error-rate`

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: `cost_spike` + `tool_fail` (combined stress case)
- [SYMPTOMS_OBSERVED]: `avg_cost_usd` và `tokens_out` tăng mạnh khi bật `cost_spike`; khi bật thêm `tool_fail` thì `error_rate_pct` tăng, dashboard hiển thị `system_scope_breaches`.
- [ROOT_CAUSE_PROVED_BY]: Trace IDs trong `docs/evidence/04-attack-case-notes.txt` + log event `request_scope_breach` + `/metrics` snapshot.
- [FIX_ACTION]: Bổ sung guardrail max-scope runtime, tách 2 tầng observability (runtime incident vs data attack JSONL), và ingest JSONL vào metrics homepage.
- [PREVENTIVE_MEASURE]: Giữ ngưỡng guardrail qua env `LIMIT_*`, theo dõi `guardrail_breaches`, chạy định kỳ ingestion attack dataset để kiểm thử hợp đồng dữ liệu.

---

## 5. Individual Contributions & Evidence

### Dang Dinh Tu Anh (2A202600019)
- [TASKS_COMPLETED]: Hoàn thiện `CorrelationIdMiddleware`, thêm kiểm thử middleware, và dựng data contract admissions (schema + clean/attack datasets).
- [EVIDENCE_LINK]:
  - https://github.com/jot2003/Lab13_C401_E3/commit/c21a6a1
  - https://github.com/jot2003/Lab13_C401_E3/commit/a5a2e99
  - https://github.com/jot2003/Lab13_C401_E3/commit/9acd041

### Quach Gia Duoc (2A202600423)
- [TASKS_COMPLETED]: Chuẩn hóa logging schema, mở rộng regex + coverage cho PII scrubber, enrich log context cho API.
- [EVIDENCE_LINK]:
  - https://github.com/jot2003/Lab13_C401_E3/commit/01fefd2
  - https://github.com/jot2003/Lab13_C401_E3/commit/38ec00a
  - https://github.com/jot2003/Lab13_C401_E3/commit/5bb3f37

### Pham Quoc Dung (2A202600490)
- [TASKS_COMPLETED]: Tích hợp Langfuse v3, propagate correlation_id xuyên suốt spans, bổ sung metadata tracing và runtime evidence.
- [EVIDENCE_LINK]:
  - https://github.com/jot2003/Lab13_C401_E3/commit/ae8f2bf
  - https://github.com/jot2003/Lab13_C401_E3/commit/92d3fc8
  - https://github.com/jot2003/Lab13_C401_E3/commit/e0904c7

### Nguyen Thanh Nam (2A202600205)
- [TASKS_COMPLETED]: Thiết kế SLO/alerts theo domain tuyển sinh, đồng bộ metric key, cập nhật runbook và mapping attack-to-alert.
- [EVIDENCE_LINK]:
  - https://github.com/jot2003/Lab13_C401_E3/commit/797b721
  - https://github.com/jot2003/Lab13_C401_E3/commit/51d57d2
  - https://github.com/jot2003/Lab13_C401_E3/commit/392df10

### Hoang Kim Tri Thanh (2A202600372)
- [TASKS_COMPLETED]: Dẫn dắt D13-T05/T00, hoàn thiện dashboard Streamlit tiếng Việt, tối ưu metrics/error_rate, thêm guardrails max-scope, tích hợp ingest JSONL vào homepage metrics, và chốt evidence + release gate.
- [EVIDENCE_LINK]:
  - https://github.com/jot2003/Lab13_C401_E3/commit/d8248b8
  - https://github.com/jot2003/Lab13_C401_E3/commit/14c84c4
  - https://github.com/jot2003/Lab13_C401_E3/commit/ad74213

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: Có guardrail giới hạn cost per-request và system-level max scope để phát hiện cost spike sớm; evidence: commit `14c84c4`.
- [BONUS_AUDIT_LOGS]: Chưa tách riêng `data/audit.jsonl` trong bản nộp hiện tại.
- [BONUS_CUSTOM_METRIC]: Bổ sung metric data attack (`data_attack_invalid_rate_pct`, breakdown theo `attack_type`/`error_type`) và guardrail breach counters; evidence: commit `ad74213`.
