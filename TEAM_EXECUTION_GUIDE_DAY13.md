# Day13 Team Execution Guide - Cach lam de phoi hop khong vach

## 1) Muc tieu chung
- App log dung JSON schema, co correlation ID, khong lo PII.
- Co tracing de tim duoc duong di request tren Langfuse.
- Co metrics de lam dashboard 6 panels va dat nguong theo SLO.
- Co alert rules va runbook de debug incident nhanh.

## 2) Nhip lam viec de xuat (4 sprint trong 4 gio)
- Sprint 1 (0h-1h): Correlation ID + logging schema + PII.
- Sprint 2 (1h-2h): Tracing + metadata + smoke requests.
- Sprint 3 (2h-3h): Metrics + dashboard + incident injection.
- Sprint 4 (3h-4h): Alerts + runbook + evidence + demo rehearsal.

## 3) Checklist ca nhan truoc khi bao "xong"
- [ ] Chi sua file trong scope duoc giao.
- [ ] Tu chay lai flow lien quan phan minh.
- [ ] Co evidence that (log/trace/screenshot/metric) cho thay thay doi co tac dung that.
- [ ] Khong con ERROR cua phan minh trong run gan nhat.
- [ ] Commit message ro muc dich, de truy vet.

## 4) Definition of Done theo task

## `D13-T01` - Correlation Middleware
- Done khi:
  - Moi request co `x-request-id`.
  - `correlation_id` xuyen suot trong log.
  - Khong leak context qua request tiep theo.

## `D13-T02` - Logging + PII
- Done khi:
  - Log JSON co du field can thiet.
  - Email/phone/id nhay cam duoc redact.
  - `scripts/validate_logs.py` pass phan schema.

## `D13-T03` - Tracing
- Done khi:
  - Langfuse nhan du trace cho request that.
  - Co metadata de loc theo feature/model/session.
  - Nhom co it nhat 10 traces cho buoi demo.

## `D13-T04` - SLO + Alerts
- Done khi:
  - `config/slo.yaml` ro metric + muc tieu.
  - `config/alert_rules.yaml` co >=3 rules.
  - Moi alert co huong dan xu ly trong `docs/alerts.md`.

## `D13-T05` - Metrics + Dashboard + Evidence
- Done khi:
  - Du lieu metric du de ve 6 panels.
  - Dashboard co label, don vi, threshold ro rang.
  - Bo screenshot trong `docs/grading-evidence.md` day du.

## 5) Luong xu ly su co chung (rat de lam)
1. Xac dinh trieu chung: panel nao do den? alert nao vang?
2. Mo trace tren Langfuse: doan nao cham/loi?
3. Mo log JSON cung `correlation_id`: tim event goc.
4. Gan dung owner theo `task_id`.
5. Sua, chay lai test nho, cap nhat runbook/evidence.

## 6) Lenh tu check truoc ban giao
```bash
python scripts/load_test.py --concurrency 5
python scripts/validate_logs.py
python scripts/inject_incident.py --scenario rag_slow
```

Neu co thay doi lien quan endpoint, chay them request thu cong va chup 1 trace full waterfall.

## 7) Quy tac commit/PR de tranh mat diem
- Moi commit mot y, khong gom nhieu viec.
- Goi y prefix:
  - `feat(day13): ...`
  - `fix(day13): ...`
  - `docs(day13): ...`
  - `chore(day13): ...`
- Trong mo ta commit nen co `D13-Txx`.

## 8) Luu y de demo truot
- Khong demo bang "cam thay dung"; phai co log/trace/metric/evidence.
- Neu co `WARN` chap nhan tam, ghi ly do va rui ro trong runbook.
- Tranh sua phut cuoi tren nhanh release neu chua qua smoke test.
