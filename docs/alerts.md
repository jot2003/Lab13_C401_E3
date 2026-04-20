# Alert Rules and Runbooks

> **Owner:** Nguyen Thanh Nam (D13-T04)
> **Domain:** Tu van tuyen sinh Dai hoc
> **Last updated:** 2026-04-20
>
> Moi runbook tuong ung 1-1 voi alert trong `config/alert_rules.yaml`.
> Tat ca command duoi day da kiem tra cu phap voi `scripts/inject_incident.py`.

---

## Attack-to-Alert Mapping (Admissions Domain)

Bang nay giup on-call biet: khi team "pha data" theo kich ban nao,
metric nao se thay doi, alert nao se bat, va dieu tra o dau.

| Attack Type (Incident) | Metric Thay Doi | Alert Bat | Huong Dieu Tra |
|------------------------|-----------------|-----------|----------------|
| `rag_slow` - RAG latency spike | `latency_p95` tang manh | `high_latency_p95` | Mo Langfuse -> loc slow traces -> so sanh span RAG vs LLM |
| `tool_fail` - Vector store loi | `error_rate_pct` tang | `high_error_rate` | Loc log theo `error_type` -> kiem tra step nao fail trong trace |
| `cost_spike` - Token explosion | `avg_cost_usd` tang, `tokens_out` tang | `cost_budget_spike` | Phan tich traces -> so sanh `tokens_in`/`tokens_out` binh thuong vs bat thuong |
| `rag_slow` keo dai -> retrieval kem | `quality_avg` giam | `low_quality_score` | Kiem tra `retrieval_score` trong trace -> RAG tra ve chunk khong lien quan |

> **Cach inject incident de test alert:**
> ```bash
> # Bat incident
> python scripts/inject_incident.py --scenario rag_slow
> python scripts/inject_incident.py --scenario tool_fail
> python scripts/inject_incident.py --scenario cost_spike
>
> # Tat incident
> python scripts/inject_incident.py --scenario rag_slow --disable
> python scripts/inject_incident.py --scenario tool_fail --disable
> python scripts/inject_incident.py --scenario cost_spike --disable
> ```

---

## 1. High latency P95

- **Severity:** P2
- **Trigger:** `latency_p95 > 5000 for 30m`
- **SLO objective:** 3000ms | Alert fires khi vuot 5000ms lien tuc 30 phut
- **Domain impact:** Thi sinh hoi diem chuan / dieu kien xet tuyen phai cho lau,
  co the bo qua va nop ho so sai vi khong nhan duoc tu van kip thoi.

### First checks

1. Mo Langfuse -> filter traces theo `duration_ms > 5000` trong 1 gio gan nhat
2. So sanh thoi gian **RAG span** vs **LLM span** (buoc nao chiem phan lon thoi gian?)
3. Kiem tra va tat incident `rag_slow` neu dang bat:
   ```bash
   python scripts/inject_incident.py --scenario rag_slow --disable
   ```
4. Xem log JSON de loc request cham:
   ```bash
   python scripts/validate_logs.py
   ```
5. Xem metrics snapshot: `GET http://127.0.0.1:8000/metrics` -> kiem tra `latency_p95`

### Mitigation

- Tat incident: `python scripts/inject_incident.py --scenario rag_slow --disable`
- Rut ngan query truoc khi gui vao RAG (truncate cau hoi qua dai)
- Giam kich thuoc prompt (xoa lich su chat cu) de LLM xu ly nhanh hon
- Fallback sang retrieval source du phong neu vector store bi qua tai

### Escalation

- Neu `latency_p95 > 10000ms` lien tuc 1 gio -> leo thang len P1
- Notify: team-oncall + backend-lead

---

## 2. High error rate

- **Severity:** P1
- **Trigger:** `error_rate_pct > 5 for 5m`
- **SLO objective:** 2% | Alert fires khi vuot 5% lien tuc 5 phut
- **Domain impact:** Thi sinh nhan response loi khi hoi ve ma nganh, to hop xet
  tuyen, han nop ho so. Rui ro cao nhat trong domain: tu van sai = nop sai.

### First checks

1. Chay validate de xem tong quan loi:
   ```bash
   python scripts/validate_logs.py
   ```
2. Loc log theo `error_type` de phan loai nguon loi (LLM / tool / schema)
3. Kiem tra va tat incident `tool_fail` neu dang bat:
   ```bash
   python scripts/inject_incident.py --scenario tool_fail --disable
   ```
4. Inspect failed traces tren Langfuse: xem step nao fail (RAG, LLM, hay schema validation?)
5. Kiem tra git log xem co deploy moi gan day khong:
   ```bash
   git log --oneline -5
   ```

### Mitigation

- Tat incident: `python scripts/inject_incident.py --scenario tool_fail --disable`
- Rollback commit moi nhat neu loi bat dau sau deploy
- Disable tool dang bi loi trong `app/agent.py`
- Retry voi fallback model neu loi do LLM
- **Escalate ngay len P0** neu error rate > 20% va khong giam sau 10 phut

### Escalation

- Neu error rate > 20% sau 10 phut -> P0, notify toan team + product owner
- Log tat ca correlation_id cua request loi de audit sau

---

## 3. Cost budget spike

- **Severity:** P2
- **Trigger:** `avg_cost_usd > 2x_baseline for 15m`
- **SLO objective:** $2.50/request | Alert khi trung binh vuot 2x baseline 15 phut
- **Domain impact:** Cau hoi tuyen sinh thuong dai (hoi nhieu truong, nhieu nganh cung luc)
  lam tang token. Spike keo dai co the can kiet ngan sach truoc khi het mua tuyen sinh.

### First checks

1. Xem metrics hien tai:
   ```bash
   # GET endpoint
   # curl http://127.0.0.1:8000/metrics
   ```
   Kiem tra cac truong: `avg_cost_usd`, `total_cost_usd`, `avg_tokens_in`, `avg_tokens_out`
2. Mo Langfuse -> phan chia traces theo `feature` va `model` tag
3. So sanh `tokens_in` / `tokens_out` giua request binh thuong vs bat thuong
4. Kiem tra va tat incident `cost_spike`:
   ```bash
   python scripts/inject_incident.py --scenario cost_spike --disable
   ```

### Mitigation

- Tat incident: `python scripts/inject_incident.py --scenario cost_spike --disable`
- Rut ngan prompt: xoa lich su chat cu, giu toi da 3 turns
- Route request don gian sang mo hinh re hon
- Ap dung prompt cache cho cac cau hoi tuyen sinh pho bien (diem chuan, ma nganh)
- Dat gioi han `max_tokens_out` trong config neu chua co

### Escalation

- Neu `total_cost_usd` trong gio > 3x gia tri gio truoc -> leo thang cho finops-owner
- Tao bao cao chi phi theo feature de xac dinh nganh/truong nao gay cost cao nhat

---

## 4. Low quality score

- **Severity:** P2
- **Trigger:** `quality_avg < 0.5 for 10m`
- **SLO objective:** 0.75 | Alert khi trung binh xuong duoi 0.5 lien tuc 10 phut
- **Domain impact:** He thong tu van tra loi sai: sai nganh, sai to hop, sai diem chuan.
  Day la loi nguy hiem nhat vi thi sinh co the tin tuong va hanh dong theo.

### First checks

1. Mo Langfuse -> filter traces theo `quality_avg < 0.5`, xem noi dung response
2. Kiem tra retrieval co dang tra ve chunks lien quan khong:
   - Xem `retrieval_score` trong trace metadata
   - So sanh noi dung chunk voi noi dung cau hoi thi sinh
3. Kiem tra va tat incident `rag_slow` (RAG cham -> chunk kem lien quan):
   ```bash
   python scripts/inject_incident.py --scenario rag_slow --disable
   ```
   Incident co the anh huong: `rag_slow`, `tool_fail`
4. Chay validate de kiem tra toan bo log:
   ```bash
   python scripts/validate_logs.py
   ```
5. Xem metrics: `quality_avg`, `quality_min` tai `GET /metrics`

### Mitigation

- Tat incident lien quan: `python scripts/inject_incident.py --scenario rag_slow --disable`
- Dieu chinh similarity threshold trong `app/mock_rag.py` de lay chunk chinh xac hon
- Fallback sang LLM truc tiep (khong qua RAG) neu retrieval dang bi degraded
- Re-rank ket qua retrieval: uu tien chunk co diem so cao nhat
- Neu loi do data admissions bi sai -> thong bao team data de update vector store

### Escalation

- Neu `quality_min < 0.2` lien tuc -> co the he thong dang tra loi hoan toan sai
- Tam thoi disable tinh nang tu van cho den khi root cause duoc xac dinh
- Log tat ca cau hoi va tra loi kem chat luong de review thu cong
