# Alert Rules and Runbooks

> **Owner:** Nguyen Thanh Nam (D13-T04)  
> **Last updated:** 2026-04-20  
> Moi runbook duoi day tuong ung voi mot alert trong `config/alert_rules.yaml`.

---

## 1. High latency P95

- **Severity:** P2
- **Trigger:** `latency_p95_ms > 5000 for 30m`
- **SLO objective:** 3000ms (alert ban o 5000ms - 2x budget)
- **Impact:** Tail latency vi pham SLO, nguoi dung cuoi bang trai nghiem cham ro ret

### First checks

1. Mo top slow traces trong 1 gio gan nhat tren Langfuse
2. So sanh thoi gian span RAG vs span LLM (buoc nao chiem nhieu thoi gian hon)
3. Kiem tra incident toggle `rag_slow` co dang bat khong:
   ```bash
   python scripts/inject_incident.py --scenario rag_slow --disable
   ```
   *(Neu lenh tren chay thanh cong thi toggle dang bat — da tat xong)*
4. Xem log JSON va loc theo `latency_ms > 5000`

### Mitigation

- Tat incident toggle: `python scripts/inject_incident.py --scenario rag_slow --disable`
- Rut ngan query truoc khi gui vao RAG (truncate long queries)
- Doi sang nguon retrieval du phong (fallback retrieval source)
- Giam kich thuoc prompt de LLM xu ly nhanh hon

---

## 2. High error rate

- **Severity:** P1
- **Trigger:** `error_rate_pct > 5 for 5m`
- **SLO objective:** 2% (alert ban o 5% - su co nghiem trong)
- **Impact:** Nguoi dung nhan duoc response that bai, anh huong truc tiep den trai nghiem

### First checks

1. Nhom log loi theo truong `error_type`:
   ```bash
   python scripts/validate_logs.py
   ```
   Hoac inject `tool_fail` de kiem tra: `python scripts/inject_incident.py --scenario tool_fail --disable`
2. Inspect failed traces tren Langfuse - xem step nao bi loi (LLM, tool, hay schema)
3. Xac dinh loi co phai do: LLM, tool call, hay schema validation
4. Kiem tra xem co deploy moi nao gan day khong (git log --oneline -10)

### Mitigation

- Rollback thay doi moi nhat neu loi bat dau sau deploy
- Disable tool dang bi loi trong `app/agent.py`
- Retry voi fallback model hoac tat tinh nang dang gap su co
- Escalate len P0 neu error rate vuot 20% va khong giam

---

## 3. Cost budget spike

- **Severity:** P2
- **Trigger:** `avg_cost_usd > 2x_baseline for 15m`
- **SLO objective:** $2.50/request (alert khi gio vuot 2x baseline)
- **Impact:** Toc do dot ngan sach vuot ke hoach, co the anh huong tai chinh

### First checks

1. Phan chia traces theo `feature` va `model` tag tren Langfuse
2. So sanh `tokens_in` / `tokens_out` giua cac request binh thuong va bat thuong
3. Kiem tra va tat incident toggle `cost_spike`:
   ```bash
   python scripts/inject_incident.py --scenario cost_spike --disable
   ```
   *(Neu lenh tren chay thanh cong thi toggle dang bat — da tat xong)*
4. Xem metrics endpoint: `GET /metrics` va kiem tra truong `avg_cost_usd` va `total_cost_usd`

### Mitigation

- Tat incident toggle: `python scripts/inject_incident.py --scenario cost_spike --disable`
- Rut ngan prompt (shorten prompts) de giam tokens_in
- Route cac request don gian sang mo hinh re hon
- Ap dung prompt cache cho cac query lap lai

---

## 4. Low quality score

- **Severity:** P2
- **Trigger:** `quality_avg < 0.5 for 10m`
- **SLO objective:** 0.75 (alert ban o 0.5 - nguoi dung da cam nhan ro su xuong cap)
- **Impact:** Nguoi dung nhan duoc response kem chat luong, sai lech hoac khong lien quan

### First checks

1. Mo traces tren Langfuse, loc theo tag `quality_avg < 0.5`
2. Kiem tra RAG co dang tra ve chunks lien quan khong:
   - Xem `retrieval_score` trong trace metadata
   - So sanh noi dung chunk vs noi dung cau hoi
3. Kiem tra va tat incident toggle `rag_slow` (incident anh huong chat luong):
   ```bash
   python scripts/inject_incident.py --scenario rag_slow --disable
   ```
   *(Cac incident co the gay anh huong: `rag_slow`, `tool_fail`)*
4. Xem log JSON va loc theo `quality_avg`:
   ```bash
   python scripts/validate_logs.py
   ```

### Mitigation

- Tat incident toggle neu do nguyen nhan thu cong: `python scripts/inject_incident.py --scenario rag_slow --disable`
- Dieu chinh similarity threshold trong `app/mock_rag.py` de lay chunk chinh xac hon
- Fallback sang LLM truc tiep (khong qua RAG) neu retrieval dang bi degraded
- Re-rank ket qua retrieval: uu tien chunk co diem so tuong dong cao nhat
