# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: C401_E3
- [REPO_URL]: https://github.com/jot2003/Lab13_C401_E3
- [MEMBERS]:
  - Member A: Quach Gia Duoc (2A202600423) | Role: Logging & PII
  - Member B: Pham Quoc Dung (2A202600490) | Role: Tracing & Enrichment
  - Member C: Nguyen Thanh Nam (2A202600205) | Role: SLO & Alerts
  - Member D: Hoang Kim Tri Thanh (2A202600372) | Role: Dashboard & Evidence
  - Member E: Dang Dinh Tu Anh (2A202600019) | Role: Correlation Middleware & Demo

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: /100
- [TOTAL_TRACES_COUNT]: (>= 10 traces on Langfuse)
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: docs/evidence/03-json-logs-correlation-id.png
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: docs/evidence/04-pii-redaction.png
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: docs/evidence/02-trace-waterfall.png
- [TRACE_WATERFALL_EXPLANATION]: Span RAG (mock_rag) chiem phan lon thoi gian xu ly. Khi inject rag_slow, span nay tang len > 5000ms trong khi LLM span van binh thuong, xac nhan bottleneck nam o retrieval layer, khong phai LLM.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: docs/evidence/05-dashboard-6-panels.png
- [SLO_TABLE]:

| SLI | Metric Key | Target | Window | Alert Threshold |
|---|---|---:|---|---:|
| Latency P95 | latency_p95 | < 3000ms | 28d | > 5000ms for 30m |
| Error Rate | error_rate_pct | < 2% | 28d | > 5% for 5m |
| Cost Budget | avg_cost_usd | < $2.50/req | 28d | > 2x_baseline for 15m |
| Quality Score | quality_avg | >= 0.75 | 28d | < 0.5 for 10m |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: docs/evidence/06-alert-rules.png
- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md#2-high-error-rate

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: latency_p95 tang vuot 5000ms, quality_avg giam xuong duoi 0.6. Nguoi dung bao cao phan hoi cham va cau tra loi kem chinh xac hon binh thuong.
- [ROOT_CAUSE_PROVED_BY]: Langfuse trace cho thay RAG span chiem > 80% tong thoi gian xu ly. Log JSON co truong latency_ms > 5000 va correlation_id cho phep truy vet request cu the.
- [FIX_ACTION]: Tat incident toggle bang lenh: `python scripts/inject_incident.py --scenario rag_slow --disable`. Latency P95 giam ve muc binh thuong trong vong 2 phut.
- [PREVENTIVE_MEASURE]: Dat alert high_latency_p95 voi threshold 5000ms/30m. Them timeout cho RAG span. Monitor quality_avg song song voi latency de phat hien som khi retrieval bi degraded.

---

## 5. Individual Contributions & Evidence

### Quach Gia Duoc (2A202600423) - D13-T02
- [TASKS_COMPLETED]: Structured JSON logging dung schema, scrub PII (email, phone, credit card) trong log output, cap nhat logging_schema.json.
- [EVIDENCE_LINK]: Branch QuachGiaDuoc-2A202600423 | Commits: 90f5dae, 01fefd2, 38ec00a, dbc0f15

### Pham Quoc Dung (2A202600490) - D13-T03
- [TASKS_COMPLETED]: Gan tracing + metadata vao luong xu ly agent, dam bao >= 10 traces hien thi tren Langfuse voi day du span (RAG, LLM, tool).
- [EVIDENCE_LINK]: Branch PhamQuocDung-2A202600490 | Commit: ae8f2bf

### Nguyen Thanh Nam (2A202600205) - D13-T04
- [TASKS_COMPLETED]:
  1. Dinh nghia 4 SLO voi metric_key khop chinh xac voi app/metrics.py: latency_p95, error_rate_pct, avg_cost_usd, quality_avg
  2. Viet 4 alert rules (high_latency_p95/P2, high_error_rate/P1, cost_budget_spike/P2, low_quality_score/P2) voi severity, condition, owner, runbook link, rationale va domain_impact cho domain tuyen sinh
  3. Viet day du runbook cho ca 4 alert: trigger, first checks, mitigation, escalation voi command dung cu phap inject_incident.py
  4. Bo sung bang Attack-to-Alert Mapping cho domain tu van tuyen sinh dai hoc: anh xa rag_slow/tool_fail/cost_spike -> metric thay doi -> alert bat -> huong dieu tra
  5. Fix 3 loi sau peer review: loai bo --status (khong ton tai), sua cu phap --disable, xoa rag_failure (khong ton tai), dong nhat ten metric voi snapshot()
- [EVIDENCE_LINK]: Branch feature/day13-nam-slo-alerts | PR: https://github.com/jot2003/Lab13_C401_E3/compare/main...feature/day13-nam-slo-alerts | Commits: 797b721, 51d57d2, 392df10

### Hoang Kim Tri Thanh (2A202600372) - D13-T05 + D13-T00
- [TASKS_COMPLETED]: Chot metric cho dashboard 6 panels, bo bang chung evidence, dieu phoi merge gate, smoke test cuoi, chot report nop bai.
- [EVIDENCE_LINK]: Branch feature/day13-thanh-d13t05-d13t00 | Commit: d8248b8

### Dang Dinh Tu Anh (2A202600019) - D13-T01
- [TASKS_COMPLETED]: Implement correlation ID middleware, gan x-request-id vao moi request/response, clear context vars dung cach.
- [EVIDENCE_LINK]: Branch DangDinhTuAnh-2A202600019 | Commits: 30fcdc4, b10f1f2, 2956a0b

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: SLO avg_cost_usd co domain_context giai thich cach giam cost: truncate prompt, cache cau hoi tuyen sinh pho bien, route request don gian sang model re hon. Evidence: config/slo.yaml#avg_cost_usd.
- [BONUS_AUDIT_LOGS]: (Chua trien khai - optional)
- [BONUS_CUSTOM_METRIC]: Attack-to-Alert mapping trong docs/alerts.md bo sung mapping table giup on-call xac dinh nguyen nhan nhanh hon: 4 attack type -> 4 metric -> 4 alert -> huong dieu tra cu the.

---

## 7. Individual Deep-Dive: Nguyen Thanh Nam (D13-T04 - SLO & Alerts)

> Phan nay danh rieng cho bao cao ca nhan cua Nguyen Thanh Nam theo yeu cau rubric B1 (Individual Report & Quality).

### 7.1 Nhiem vu duoc giao

Task **D13-T04**: Dinh nghia SLO, rule canh bao, va runbook xu ly su co cho he thong tu van tuyen sinh dai hoc.

**Files chinh:** `config/slo.yaml`, `config/alert_rules.yaml`, `docs/alerts.md`

**Branch:** `feature/day13-nam-slo-alerts`

### 7.2 Quyet dinh ky thuat va ly do

#### A. Chon 4 SLI va cach dinh nghia threshold

| SLI | Objective | Alert Threshold | Ly do chon gap |
|-----|-----------|----------------|----------------|
| latency_p95 | 3000ms | 5000ms (30m) | Gap 2x tranh false positive mua tuyen sinh traffic cao |
| error_rate_pct | 2% | 5% (5m) | 5 phut de phat hien nhanh, P1 vi sai thong tin = rui ro thi sinh |
| avg_cost_usd | $2.50 | 2x baseline (15m) | Cau hoi tuyen sinh dai (nhieu truong) gay token cao tu nhien |
| quality_avg | 0.75 | 0.5 (10m) | 0.5 la nguong nguoi dung cam nhan ro, 10 phut tranh alert nhieu |

**Nguyen tac dinh threshold:** `alert_threshold > SLO objective` de tranh canh bao khi he thong dang chay binh thuong nhung co bien dong nho (burn-rate buffer).

#### B. Tai sao high_error_rate la P1 trong khi cac alert khac la P2?

Trong domain tu van tuyen sinh, loi tra loi sai (sai ma nganh, sai to hop, sai han nop) co the gay hau qua truc tiep: thi sinh nop sai truong, mat co hoi xet tuyen. Do do `high_error_rate` duoc dat P1 va thoi gian kich hoat chi 5 phut (nhanh hon cac alert khac).

#### C. Metric key phai khop chinh xac voi app/metrics.py

Mot loi pho bien la dung ten metric tuy y. Toi da doi chieu truc tiep voi ham `snapshot()` trong `app/metrics.py`:

```
latency_p95   <- percentile(REQUEST_LATENCIES, 95)
error_rate_pct <- error_rate()
avg_cost_usd  <- mean(REQUEST_COSTS)
quality_avg   <- mean(QUALITY_SCORES)
```

Cac ten sai cu (hourly_cost_usd, quality_score_avg) da duoc fix sau peer review.

#### D. Bang Attack-to-Alert Mapping (dong gop rieng)

Toi bo sung bang nay vao dau `docs/alerts.md` de on-call biet ngay: khi team inject incident nao, metric nao thay doi, alert nao bat, va dieu tra o dau. Day la phan khong co trong template goc nhung rat can thiet cho demo incident response.

| Attack | Metric | Alert | Dieu tra |
|--------|--------|-------|---------|
| rag_slow | latency_p95 tang | high_latency_p95 | RAG span tren Langfuse |
| tool_fail | error_rate_pct tang | high_error_rate | error_type trong log |
| cost_spike | avg_cost_usd tang | cost_budget_spike | tokens_out trong traces |
| rag_slow keo dai | quality_avg giam | low_quality_score | retrieval_score trong trace |

### 7.3 Cac bug da fix (Peer Review)

Sau khi nhan feedback tu teammate, toi da fix 3 loi:

1. **Lenh khong ton tai:** `inject_incident.py --status` → Xoa bop, thay bang lenh co cu phap dung
2. **Cu phap sai:** `--disable rag_slow` → `--scenario rag_slow --disable` (dung voi argparse thuc te)
3. **Incident khong ton tai:** `rag_failure` → Xoa, chi giu 3 incident that: `rag_slow`, `tool_fail`, `cost_spike`
4. **Ten metric sai:** `hourly_cost_usd` → `avg_cost_usd`, `quality_score_avg` → `quality_avg`

Commit fix: `51d57d2`

### 7.4 Ket qua dat duoc (Definition of Done)

- [x] config/slo.yaml parse OK (4 SLI, metric_key khop metrics.py)
- [x] config/alert_rules.yaml co 4 alert rules, condition dung metric key thuc te
- [x] Command trong runbook chay dung cu phap (`--scenario X --disable`)
- [x] Khong con reference den incident khong ton tai
- [x] Bang Attack-to-Alert Mapping cho admissions domain
- [x] Moi alert co severity, condition, owner, runbook link, rationale, domain_impact
- [x] Moi runbook co: trigger, first checks, mitigation, escalation

### 7.5 Diem can phoi hop voi thanh vien khac

- **D13-T03 (Pham Quoc Dung):** Can trace co tag `retrieval_score` trong metadata de runbook #4 dieu tra duoc
- **D13-T05 (Hoang Kim Tri Thanh):** Sau khi dashboard xong, xac nhan `latency_p95` va `quality_avg` hien thi dung tren panel
- **D13-T01 (Dang Dinh Tu Anh):** `correlation_id` phai co trong moi log de on-call trace duoc tung request loi theo runbook #2
