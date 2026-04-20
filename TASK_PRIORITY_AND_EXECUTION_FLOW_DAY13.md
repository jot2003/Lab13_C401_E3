# Day13 - Thu tu uu tien task va execution flow

File nay tra loi 3 cau hoi:
- Viec nao lam truoc de khong gay tac nghen?
- Ai can xong truoc de nguoi sau tiep tuc?
- Quy trinh tu kickoff den merge/push nhu the nao?

---

## 1) Ban do task va owner
- `D13-T00` - Integration/release gate - Hoang Kim Tri Thanh
- `D13-T01` - Correlation middleware - Dang Dinh Tu Anh
- `D13-T02` - Logging schema + PII - Quach Gia Duoc
- `D13-T03` - Tracing + metadata - Pham Quoc Dung
- `D13-T04` - SLO + alerts + runbook - Nguyen Thanh Nam
- `D13-T05` - Metrics + dashboard + evidence - Hoang Kim Tri Thanh

---

## 2) Thu tu uu tien bat buoc (critical path)

## P0 - Phai xong truoc
1. `D13-T01` (Correlation ID middleware)
2. `D13-T02` (Structured log + PII scrub)
3. `D13-T03` (Tracing tren luong da co context)
4. `D13-T05` (Metrics + dashboard evidence)
5. `D13-T04` (SLO/alerts chot theo metric that)
6. `D13-T00` (Release gate va demo check cuoi)

Giai thich ngan:
- Khong co correlation ID -> kho noi trace va log.
- Log chua dung schema/PII chua scrub -> evidence khong dat.
- Chua co trace that -> kho debug incident.
- SLO/alerts phai dua tren metric da xac thuc.

## P1 - Co the song song tung phan
- `D13-T04` co the viet khung runbook som, nhung chot threshold sau khi co dashboard.
- `D13-T05` co the dung khung panel truoc, nhung du lieu cuoi phai lay tu run that.

## P2 - Hoan thien
- Chuan hoa wording report.
- Chup hinh dep va de doc hon cho giang vien.

---

## 3) Dependency ro rang (ai xong truoc ai)
- `D13-T01` xong co ban roi `D13-T02` moi xac nhan schema context day du.
- `D13-T01` + `D13-T02` xong roi `D13-T03` moi debug trace nhanh va dung.
- `D13-T03` + luong run on dinh roi `D13-T05` moi thu metric dashboard kha tin.
- `D13-T05` xong panel/metric roi `D13-T04` moi chot SLO va alert threshold hop ly.
- Tat ca xong roi `D13-T00` moi gate merge va push.

---

## 4) SOP cho buoi lam (tu bat dau den nop)

## Buoc 0 - Kickoff 15 phut
1. Chot owner theo `team_task_allocation_day13.md`.
2. Moi nguoi checkout branch rieng.
3. Chot kenh bao loi nhanh (group chat + mau bug message).

## Buoc 1 - Lam theo critical path
1. `D13-T01`: middleware correlation ID.
2. `D13-T02`: log schema + PII scrub.
3. `D13-T03`: tracing voi metadata.
4. `D13-T05`: metrics + dashboard + evidence.
5. `D13-T04`: SLO + alert rules + runbook.

## Buoc 2 - Self-check theo nhom
```bash
python scripts/load_test.py --concurrency 5
python scripts/validate_logs.py
python scripts/inject_incident.py --scenario rag_slow
```

Yeu cau dat:
- Validate logs pass.
- Co >=10 traces tren Langfuse.
- Dashboard du 6 panels.
- Alerts trigger dung nguong da khai bao.

## Buoc 3 - Triage loi dung owner
1. Lay `correlation_id` tu request gap loi.
2. So trace de tim step cham/loi.
3. So log JSON de xac dinh goc.
4. Assign theo task:
   - Middleware -> `D13-T01`
   - Logging/PII -> `D13-T02`
   - Tracing -> `D13-T03`
   - Metrics/dashboard -> `D13-T05`
   - SLO/alerts -> `D13-T04`

## Buoc 4 - Merge tuan tu va release gate
1. Merge `D13-T01`
2. Merge `D13-T02`
3. Merge `D13-T03`
4. Merge `D13-T05`
5. Merge `D13-T04`
6. Merge `D13-T00` (chot)

Moi lan merge:
- Rebase nhanh theo main moi nhat.
- Chay smoke test toi thieu.
- Khong keo file ngoai scope.

---

## 5) Timeline goi y (4 gio)
- 00:00-00:30: kickoff + baseline run.
- 00:30-01:30: `D13-T01`, `D13-T02`.
- 01:30-02:20: `D13-T03` + gui request dat >=10 traces.
- 02:20-03:10: `D13-T05` dashboard/evidence.
- 03:10-03:40: `D13-T04` SLO/alerts/runbook.
- 03:40-04:00: `D13-T00` merge gate + demo rehearsal.

Neu tre gio:
- Giu nguyen P0.
- Cat polish P2, khong cat evidence.

---

## 6) Definition of Done cho ca nhom
Chi xem la xong Day13 khi du:
- Hoan thanh tat ca TODO code.
- `scripts/validate_logs.py` dat yeu cau.
- Langfuse co toi thieu 10 traces.
- Dashboard du 6 panels.
- Alert rules + runbook co the dung de xu ly incident.
- Blueprint/report khop artifact that.
