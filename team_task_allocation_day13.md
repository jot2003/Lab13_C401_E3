# Day13 - Phan cong nhiem vu nhom (tap trung Observability)

## Muc tieu
- Chia viec ro nguoi, ro file, ro dau ra de tranh conflict.
- Moi su co phai truy ra duoc owner thong qua log, trace, metrics.
- Dam bao hoan thanh dung tieu chi cham: TODO, >=10 traces, dashboard 6 panels, alerts + report.

## Thanh vien
1. Hoang Kim Tri Thanh (2A202600372)
2. Dang Dinh Tu Anh (2A202600019)
3. Quach Gia Duoc (2A202600423)
4. Pham Quoc Dung (2A202600490)
5. Nguyen Thanh Nam (2A202600205)
6. (Neu co) Thanh vien thu 6: cap nhat ten tai day

## Nguyen tac lam viec
1. Moi nguoi uu tien sua file trong scope cua minh.
2. Neu can sua file owner khac: ping owner truoc, thong nhat cach sua roi moi commit.
3. Moi commit mot y chinh, message ro muc tieu thay doi.
4. Truoc khi ban giao: chay lai `python scripts/validate_logs.py` va gui evidence.

## Phan cong theo task_id

| Task ID | Thanh vien | Branch de xuat | File chinh | Cong viec chinh | Dau ra bat buoc |
|---|---|---|---|---|---|
| D13-T01 | Dang Dinh Tu Anh | feature/day13-tuanh-correlation | `app/middleware.py` | Correlation ID cho moi request, gan vao response header, clear context vars dung cach | Log co `correlation_id`, response co `x-request-id` |
| D13-T02 | Quach Gia Duoc | feature/day13-duoc-logging-pii | `app/logging_config.py`, `app/pii.py`, `config/logging_schema.json` | Structured log dung schema, scrub PII day du | Log khong lo PII, schema pass |
| D13-T03 | Pham Quoc Dung | feature/day13-dung-tracing | `app/tracing.py`, `app/agent.py` | Gan tracing + metadata de theo doi luong xu ly | Langfuse co >=10 traces doc duoc |
| D13-T04 | Nguyen Thanh Nam | feature/day13-nam-slo-alerts | `config/slo.yaml`, `config/alert_rules.yaml`, `docs/alerts.md` | Dinh nghia SLO, rule canh bao, runbook xu ly su co | It nhat 3 alert rules + runbook link |
| D13-T05 | Hoang Kim Tri Thanh | feature/day13-thanh-dashboard-evidence | `app/metrics.py`, `docs/dashboard-spec.md`, `docs/grading-evidence.md` | Chot metric cho dashboard 6 panels va bo bang chung | Dashboard du 6 panel + bo screenshot day du |
| D13-T00 | Hoang Kim Tri Thanh | chore/day13-thanh-release-gate | `README.md`, `docs/blueprint-template.md`, file tong hop | Dieu phoi merge gate, smoke test cuoi, chot report nop bai | Validate pass, demo on dinh, report khop artifact |

## Quy uoc khi co loi
- Loi middleware/request id -> `D13-T01`
- Loi schema log/PII -> `D13-T02`
- Loi trace/missing span -> `D13-T03`
- Loi SLO/alert config -> `D13-T04`
- Loi metrics/dashboard evidence -> `D13-T05`
- Loi tich hop cuoi/trinh dien -> `D13-T00`

## Lenh chay chung ca nhom
```bash
python scripts/load_test.py --concurrency 5
python scripts/validate_logs.py
python scripts/inject_incident.py --scenario rag_slow
```

## Thu tu merge de it vo luong
1. `D13-T01` (middleware correlation)
2. `D13-T02` (logging + PII)
3. `D13-T03` (tracing)
4. `D13-T05` (metrics + dashboard evidence)
5. `D13-T04` (SLO + alerts + runbook)
6. `D13-T00` (release gate + report chot)
