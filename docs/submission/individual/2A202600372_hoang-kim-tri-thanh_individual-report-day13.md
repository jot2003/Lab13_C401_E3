# Individual Report - Hoang Kim Tri Thanh (2A202600372)

## 1) Vai tro
- D13-T05: Metrics + Dashboard + Evidence.
- D13-T00: Release gate + final report integration.

## 2) Phan viec da hoan thanh
- Hoan thien dashboard Streamlit tieng Viet, bo cuc 2 tang quan sat (Runtime Incident + Data Attack JSONL).
- Bo sung guardrails max-scope runtime cho latency/error/cost/quality va hien thi trang thai breach tren UI.
- Tich hop pipeline ingest admissions JSONL vao metrics homepage (`data_attack_*` counters).
- Chot bo evidence + release checklist + blueprint report de dap ung rubric 60/40.

## 3) Git evidence (commits chinh)
- https://github.com/jot2003/Lab13_C401_E3/commit/d8248b8
- https://github.com/jot2003/Lab13_C401_E3/commit/e630190
- https://github.com/jot2003/Lab13_C401_E3/commit/14c84c4
- https://github.com/jot2003/Lab13_C401_E3/commit/ad74213
- https://github.com/jot2003/Lab13_C401_E3/commit/601eab8

## 4) Anh huong den he thong
- Tang kha nang demo va giai thich su co: metrics/traces/logs dong bo, co guardrails va scope status ro rang.
- Dam bao data attack khong con la kenh rieng le: JSONL ingest duoc phan anh truc tiep tren trang chu metrics.
- Hoan thien readiness nop bai: evidence map + release gate pass.

## 5) Van de gap phai va cach xu ly
- Error rate co luc vuot 100% do mau so traffic khong tinh loi -> sua `record_error()` de tang traffic cho request fail.
- UI ban dau tach data attack khoi metrics tong -> bo sung endpoint ingest + counters `data_attack_*`.
- Demo de bi vo luong khi API fail -> thay `st.stop()` bang degraded-state handling.

## 6) Cau hoi van dap co the tra loi
- Vi sao can correlation_id va no di qua nhung thanh phan nao?
- Tai sao can tach 2 tang observability (runtime incident vs data attack)?
- Max-scope guardrail dang enforce theo request hay system-level, va doc o dau?
