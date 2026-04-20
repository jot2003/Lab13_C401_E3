# Individual Report - Dang Dinh Tu Anh (2A202600019)

## 1) Ho ten + MSSV + vai tro
- Ho ten: Dang Dinh Tu Anh
- MSSV: 2A202600019
- Vai tro: D13-T02 — Correlation ID Middleware + Data Contract (Admissions Domain)

## 2) Pham vi task da lam

### T02-A: CorrelationIdMiddleware
- Implement `app/middleware.py`: moi request duoc gan `correlation_id` doc lap.
  - Neu request gui `x-request-id` header -> giu nguyen ID do.
  - Neu khong co header -> tu sinh ID dang `req-<8hex>`.
  - Bind `correlation_id` vao structlog contextvars de moi dong log trong request deu co ID.
  - Tra ve `x-request-id` va `x-response-time-ms` trong response header.
  - `clear_contextvars()` o dau moi request de chong leak context giua cac request dong thoi.
- Viet `tests/test_middleware.py` voi 3 case:
  - Case 1: custom header -> response echo dung ID, `bind_contextvars` duoc goi dung ID.
  - Case 2: khong header -> ID dang `req-[0-9a-f]{8}`, khop voi response header.
  - Case 3: 2 request lien tiep -> 2 ID doc lap (chong leak).
- Verify runtime: app thuc chay, gui 3 request, check log `data/logs.jsonl` co `correlation_id` khop header.
- Ket qua `validate_logs.py`: 23 unique correlation IDs, score 100/100.

### T02-B: Data Contract + Dataset — Admissions Domain
- Tao `data/admissions_schema.json` (JSON Schema draft-07, 20 fields):
  - Conditional validation `if/then/else` theo `phuong_thuc_xet_tuyen`:
    - DGNL: `diem_xet_tuyen` 0–1200, `diem_chuan` 400–1200.
    - IELTS/Chung_chi_quoc_te: 0–9, buoc 0.5.
    - THPTQG/Hoc_ba/Uu_tien: 0–30, `diem_chuan` 15–30.
  - `additionalProperties: false` de chong field la.
- Tao `data/admissions_clean.jsonl` (35 records):
  - Da dang: THPTQG, DGNL, IELTS, Hoc_ba, Chung_chi_quoc_te, Uu_tien.
  - Cover cac truong hop: hoc bong toan phan (NghiDinh 116), hoc phi = 0, hoc phi cao (RMIT ~95tr).
  - Cac tinh/thanh khac nhau, nhieu nganh: Y, CNTT, Luat, Ngoai thuong, Su pham, Kien truc.
- Tao `data/admissions_attack.jsonl` (20 records, 8 attack pattern):
  - MISSING_REQUIRED, WRONG_TYPE, ENUM_VIOLATION, OUTLIER_VALUE.
  - PII_LEAK (email, CCCD, so tai khoan ngan hang), INJECTION (prompt + SQL), FORMAT_ERROR, ADDITIONAL_PROPERTIES.
- Viet `docs/admissions-data-contract.md`: schema reference, expected behavior theo tung attack type, edge cases.
- Fix blocker: schema cu set `diem_xet_tuyen` max=30 trong khi 4 record DGNL co diem 780–900 -> them conditional validation.
- Normalize 11 `ma_truong` tu prefix co dau Unicode (DHSP, DHYD...) ve ASCII-only.
- Ket qua: 35/35 clean records pass jsonschema validation.

## 3) Git evidence (commits chinh)
- `b10f1f2` — implement middleware.py (CorrelationIdMiddleware core logic)
  https://github.com/jot2003/Lab13_C401_E3/commit/b10f1f2
- `c21a6a1` — test middleware (3 unit tests + verify runtime)
  https://github.com/jot2003/Lab13_C401_E3/commit/c21a6a1
- `a5a2e99` — feat(data): add admissions domain data contract and test datasets
  https://github.com/jot2003/Lab13_C401_E3/commit/a5a2e99
- `9acd041` — fix(schema): add conditional score validation per xet_tuyen method
  https://github.com/jot2003/Lab13_C401_E3/commit/9acd041

## 4) Anh huong den he thong
- **Correlation propagation**: moi dong log trong mot request deu co cung `correlation_id`. Team co the filter log theo ID de trace toan bo lifecycle (request_received -> response_sent).
- **No context leak**: `clear_contextvars()` dau moi request dam bao ID khong bi reuse sai giua cac request dong thoi hoac lien tiep.
- **Data attack pipeline**: 20 record attack cung cap input de quan sat `validation_error_count`, `pii_scrub_count`, `outlier_count` tang tren dashboard khi ingest data xau.
- **Schema gate**: conditional validation ngan data DGNL bi reject nham (blocker truoc do lam load_test fail), giup pipeline on dinh.

## 5) Van de gap phai va cach xu ly
- **validate_logs fail "less than 2 unique IDs"**: app dang chay process cu truoc merge, endpoint `/metrics/timeseries` moi chua co -> restart uvicorn, seed traffic bang load_test, pass 100/100.
- **Schema blocker DGNL**: `diem_xet_tuyen` max=30 reject toan bo record DGNL (diem 780–900) -> dung `if/then/else` JSON Schema draft-07, giu 1 field thay vi tach doi.
- **ma_truong regex fail**: 11 ma truong dung chu `D` co dau Unicode khong match `^[A-Z]{2,8}$` ASCII -> normalize bang script Python, sua trong data.
- **Test log verification**: `/health` endpoint khong emit log nen khong the check `correlation_id` bang doc file -> patch `app.middleware.bind_contextvars` truc tiep thay vi doc file.

## 6) Cau hoi van dap co the tra loi
- Tai sao `clear_contextvars()` phai goi o dau request chu khong phai cuoi? (tranh truong hop request bi exception, context khong duoc clean, leak sang request ke tiep)
- `structlog.contextvars.bind_contextvars` vs `logger.bind`: scope khac nhau the nao trong async context?
- JSON Schema `if/then/else` hoat dong the nao khi field trigger (`phuong_thuc_xet_tuyen`) bi thieu?
- Tai sao PII test dung `patch("app.middleware.bind_contextvars")` thay vi doc log file?
- DGNL diem thang 1200 va THPTQG thang 30 cung 1 field: trade-off so voi cach tach `diem_thpt` / `diem_dgnl` rieng?
