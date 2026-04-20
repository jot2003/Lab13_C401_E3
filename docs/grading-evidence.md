# Evidence Collection Sheet

> **Owner**: D13-T05 (Metrics + Dashboard + Evidence)
> Collect all items below before submission. Each item maps to a rubric criterion.

---

## Required Screenshots

| # | Evidence Item | Rubric Section | Status |
|---|---|---|---|
| 1 | Langfuse trace list with ≥ 10 traces (`docs/evidence/01-langfuse-trace-list.png`) | A1 – Logging & Tracing (10 pts) | ☑ |
| 2 | One full trace waterfall (with span details) (`docs/evidence/02-trace-waterfall.png`) | A1 – Logging & Tracing | ☑ |
| 3 | Correlation proof image (response header -> trace metadata -> JSON logs) (`docs/evidence/03-correlation-proof.png`) | A1 – Logging & Tracing | ☑ |
| 4 | Log line with PII redaction (e.g. email -> `***`) (`docs/evidence/04-pii-redaction.png`) | A1 – Alerts & PII (10 pts) | ☑ |
| 5 | Dashboard with all 6 panels visible (`docs/evidence/05-dashboard-6-panels.png`) | A1 – Dashboard & SLO (10 pts) | ☑ |
| 6 | Alert rules config with runbook link (screenshot) (`docs/evidence/06-alert-rules.png`) | A1 – Alerts & PII | ☑ |

## Optional Screenshots (Bonus)

| # | Evidence Item | Bonus Points | Status |
|---|---|---|---|
| 7 | Incident before / after fix (`docs/evidence/04-attack-case-notes.png`) | +3 pts | ☑ |
| 8 | Cost comparison before / after optimization | +3 pts | ☐ |
| 9 | Auto-instrumentation proof | +2 pts | ☐ |
| 10 | Audit logs (`data/audit.jsonl`) | +2 pts | ☐ |

---

## Evidence File Naming Convention

Place screenshots in `docs/evidence/` with names:
```
01-langfuse-trace-list.png
02-trace-waterfall.png
03-correlation-proof.png
04-attack-case-notes.png
04-attack-case-notes.txt
tracing-summary.json
```

Pending files for full D13-T05 closure:
```
04-pii-redaction.png
05-dashboard-6-panels.png
06-alert-rules.png
```
Status: done (all files present in `docs/evidence/`).

---

## Validation Outputs (paste results here)

### validate_logs.py
```
python scripts/validate_logs.py
Total log records analyzed: 217
Records with missing required fields: 0
Records with missing enrichment (context): 0
Unique correlation IDs found: 112
Potential PII leaks detected: 0
Estimated Score: 100/100
```

### Langfuse Trace Count
```
Total traces: 74  (must be ≥ 10)
```

### Dashboard Panel Count
```
Panels visible: 6/6 (`docs/evidence/05-dashboard-6-panels.png`)
```

### D13-T03 Correlation + Attack Evidence (Runtime)
```
proof.request_id_sent: req-proof-38cffd91
proof.response_header_x_request_id: req-proof-38cffd91
proof.trace_id: f0c7e48e370845f8a2f2fea820ea92fd
proof.trace_metadata_correlation_id: req-proof-38cffd91

rag_slow.attack_trace_id: 9225c08e60fb28a6d07f87de10a4eba9
rag_slow.recover_trace_id: c7dafbd44e13aba8475de89b586122b9
cost_spike.attack_trace_id: f8a46f222dbaa9184668fce222efad12
cost_spike.recover_trace_id: 3ec6d73de68ff1b483cd5cf2f052b41e
```

---

## D13-T00 Release Gate Checklist

> **All items must pass before final submission.**

| # | Gate | Command / Check | Pass? |
|---|---|---|---|
| 1 | `validate_logs.py` passes ≥ 80/100 | `python scripts/validate_logs.py` | ☑ |
| 2 | ≥ 10 traces on Langfuse | Checked via Langfuse API/dashboard (`totalItems=74`) | ☑ |
| 3 | Dashboard shows all 6 panels | Screenshot in `docs/evidence/05-dashboard-6-panels.png` | ☑ |
| 4 | Evidence collection complete | All required screenshots (1–6) present | ☑ |
| 5 | Blueprint report filled | `docs/blueprint-template.md` has all member names + sections | ☑ |
| 6 | No PII leaks in logs | `validate_logs.py` reports leaks=0 (raw token grep-like count=14) | ☑ |
| 7 | All TODOs resolved | TODO scan in `app/` returned 0 | ☑ |

**Sign-off**: Hoang Kim Tri Thanh (D13-T00/D13-T05) Date: 2026-04-20
