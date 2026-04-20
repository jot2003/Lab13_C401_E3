# Evidence Collection Sheet

> **Owner**: D13-T05 (Metrics + Dashboard + Evidence)
> Collect all items below before submission. Each item maps to a rubric criterion.

---

## Required Screenshots

| # | Evidence Item | Rubric Section | Status |
|---|---|---|---|
| 1 | Langfuse trace list with ≥ 10 traces | A1 – Logging & Tracing (10 pts) | ☐ |
| 2 | One full trace waterfall (with span details) | A1 – Logging & Tracing | ☐ |
| 3 | JSON logs showing `correlation_id` field | A1 – Logging & Tracing | ☐ |
| 4 | Log line with PII redaction (e.g. email → `***`) | A1 – Alerts & PII (10 pts) | ☐ |
| 5 | Dashboard with all 6 panels visible | A1 – Dashboard & SLO (10 pts) | ☐ |
| 6 | Alert rules config with runbook link | A1 – Alerts & PII | ☐ |

## Optional Screenshots (Bonus)

| # | Evidence Item | Bonus Points |
|---|---|---|
| 7 | Incident before / after fix | +3 pts |
| 8 | Cost comparison before / after optimization | +3 pts |
| 9 | Auto-instrumentation proof | +2 pts |
| 10 | Audit logs (`data/audit.jsonl`) | +2 pts |

---

## Evidence File Naming Convention

Place screenshots in `docs/evidence/` with names:
```
01-langfuse-trace-list.png
02-trace-waterfall.png
03-json-logs-correlation-id.png
04-pii-redaction.png
05-dashboard-6-panels.png
06-alert-rules.png
07-incident-before-after.png   (optional)
08-cost-optimization.png       (optional)
```

---

## Validation Outputs (paste results here)

### validate_logs.py
```
[Paste output of: python scripts/validate_logs.py]
Score: __/100
```

### Langfuse Trace Count
```
Total traces: __  (must be ≥ 10)
```

### Dashboard Panel Count
```
Panels visible: __/6
```

---

## D13-T00 Release Gate Checklist

> **All items must pass before final submission.**

| # | Gate | Command / Check | Pass? |
|---|---|---|---|
| 1 | `validate_logs.py` passes ≥ 80/100 | `python scripts/validate_logs.py` | ☐ |
| 2 | ≥ 10 traces on Langfuse | Check Langfuse dashboard | ☐ |
| 3 | Dashboard shows all 6 panels | Screenshot in `docs/evidence/05-dashboard-6-panels.png` | ☐ |
| 4 | Evidence collection complete | All required screenshots (1–6) present | ☐ |
| 5 | Blueprint report filled | `docs/blueprint-template.md` has all member names + sections | ☐ |
| 6 | No PII leaks in logs | `grep -c "email\|phone\|ssn" data/logs.jsonl` returns 0 | ☐ |
| 7 | All TODOs resolved | `grep -r "TODO" app/` returns 0 critical items | ☐ |

**Sign-off**: __________________ Date: __________
