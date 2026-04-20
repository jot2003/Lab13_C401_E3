# Data Contract — Trợ lý Tư vấn Tuyển sinh Đại học

## Mục đích

Dataset này dùng để test hệ thống observability (alert/metric/log/trace) thông qua việc nhập dữ liệu hợp lệ và cố tình phá vỡ các rule validation.

---

## Schema tóm tắt

Source of truth: [`data/admissions_schema.json`](../data/admissions_schema.json) (JSON Schema draft-07)

| Field | Type | Required | Rule |
|---|---|---|---|
| `record_id` | string | ✅ | Pattern `ADM-YYYYMMDD-XXXX` |
| `ho_ten` | string | ✅ | 2–100 ký tự |
| `nam_sinh` | integer | ✅ | 1990–2008 |
| `gioi_tinh` | enum | ✅ | `Nam` / `Nu` / `Khac` |
| `tinh_thanh` | string | ✅ | 2–50 ký tự |
| `truong_thpt` | string | ✅ | 5–150 ký tự |
| `ma_truong` | string | ✅ | Pattern `[A-Z]{2,8}` |
| `ten_truong` | string | ✅ | 5–200 ký tự |
| `ma_nganh` | string | ✅ | Pattern 7 chữ số |
| `ten_nganh` | string | ✅ | 3–150 ký tự |
| `phuong_thuc_xet_tuyen` | enum | ✅ | `THPTQG` / `Hoc_ba` / `DGNL` / `IELTS` / `Chung_chi_quoc_te` / `Uu_tien` |
| `to_hop_xet_tuyen` | enum | ✅ | A00/A01/B00/B08/C00/C01/D01/D07/D14/D15/D90/N00/R00 |
| `diem_xet_tuyen` | number | ✅ | 0–30 (THPTQG); dùng thang gốc nếu DGNL |
| `diem_chuan_du_kien` | number | ✅ | 15–30 |
| `hoc_phi_vnd` | number | ✅ | 0–100,000,000 VNĐ |
| `hoc_bong_phan_tram` | integer | ✅ | 0–100 |
| `deadline_nop_ho_so` | string (date) | ✅ | Format `YYYY-MM-DD` |
| `ielts_score` | number / null | ❌ | 0–9, bội số 0.5 |
| `ghi_chu` | string | ❌ | Tối đa 500 ký tự. **Không chứa PII.** |
| `created_at` | string (datetime) | ✅ | Format `YYYY-MM-DDTHH:MM:SSZ` |

`additionalProperties: false` — mọi field ngoài danh sách trên đều bị reject.

---

## Attack Patterns đã cover

### 1. `MISSING_REQUIRED` — Thiếu field bắt buộc
**Records:** ATK-0001, ATK-0002, ATK-0003

Các biến thể: thiếu `ma_nganh`+`ten_nganh`; thiếu `ho_ten`; thiếu `hoc_phi_vnd`+`deadline_nop_ho_so`.

**Expected behavior:** Hệ thống reject với lỗi validation, log event `validation_error` với danh sách field thiếu. Không được xử lý tiếp.

---

### 2. `WRONG_TYPE` — Sai kiểu dữ liệu
**Records:** ATK-0004, ATK-0005, ATK-0006

Các biến thể: `diem_xet_tuyen` là string; `nam_sinh` là string; `hoc_phi_vnd` là string; `hoc_bong_phan_tram` là float.

**Expected behavior:** Parser raise type error trước khi vào business logic. Metric `parse_error_count` tăng. Log có `error_type=TYPE_MISMATCH`.

---

### 3. `ENUM_VIOLATION` — Giá trị ngoài danh sách cho phép
**Records:** ATK-0007, ATK-0008, ATK-0009

Các biến thể: `gioi_tinh="Male"`; `phuong_thuc_xet_tuyen="SAT"`; `to_hop_xet_tuyen="Z99"`.

**Expected behavior:** Reject với `enum_violation`. Không gây crash — chỉ log warning và trả 422.

---

### 4. `OUTLIER_VALUE` — Giá trị hợp lệ về type nhưng phi thực tế
**Records:** ATK-0010, ATK-0011, ATK-0012, ATK-0013

Các biến thể:
- `diem_xet_tuyen=35.5` (vượt max 30)
- `hoc_phi_vnd=-5000000` (âm)
- `deadline_nop_ho_so="2019-01-01"` (quá khứ xa 5 năm)
- `nam_sinh=1985` (ngoài range)
- `hoc_bong_phan_tram=150` (> 100%)
- `diem_xet_tuyen=-3.5` (âm)

**Expected behavior:** Range validation trigger alert nếu outlier rate > threshold. Log `outlier_detected` với field và giá trị thực tế.

---

### 5. `PII_LEAK` — Dữ liệu nhạy cảm thô trong các field text
**Records:** ATK-0014, ATK-0015, ATK-0016

Các biến thể:
- `ghi_chu` chứa email + SĐT (`nguyenvanA2006@gmail.com`, `0912345678`)
- `ho_ten` + `ghi_chu` chứa CCCD (`079206001234`)
- `ghi_chu` chứa số tài khoản ngân hàng + SĐT định dạng quốc tế

**Expected behavior:** PII scrubber phát hiện và redact trước khi ghi log. Metric `pii_scrub_count` tăng. Raw PII **không bao giờ** xuất hiện trong log file.

---

### 6. `INJECTION` — Prompt injection & SQL injection
**Records:** ATK-0017, ATK-0018

Các biến thể:
- `ghi_chu` chứa `"Ignore previous instructions..."` (prompt injection)
- `ho_ten` chứa `"'; DROP TABLE admissions; --"` (SQL injection)

**Expected behavior:** Field bị sanitize trước khi đưa vào LLM. Hệ thống không thay đổi behavior. Alert nếu injection pattern được phát hiện.

---

### 7. `FORMAT_ERROR` — Sai format ngày/ID
**Record:** ATK-0019

Các biến thể: `record_id="REC-123-INVALID"`; `deadline_nop_ho_so="30/04/2024"` (dd/MM/yyyy thay vì YYYY-MM-DD); `created_at="15-03-2024 08:30"`.

**Expected behavior:** Format validation fail sớm ở parsing layer. Log `format_error` với field và value thực tế.

---

### 8. `ADDITIONAL_PROPERTIES` — Field ngoài schema
**Record:** ATK-0020

Field lạ: `cccd_so`, `so_dien_thoai`, `mat_khau` — đồng thời là PII leak attempt.

**Expected behavior:** `additionalProperties: false` reject toàn bộ record. Log warning về unknown fields. PII trong field lạ vẫn phải bị scrub trước khi log.

---

## Expected Behavior tổng hợp khi hệ thống nhận data phá

| Attack Type | HTTP Status | Log Event | Metric tăng | Alert trigger |
|---|---|---|---|---|
| MISSING_REQUIRED | 422 | `validation_error` | `validation_error_count` | Nếu > 10/phút |
| WRONG_TYPE | 422 | `parse_error` | `parse_error_count` | Nếu > 5/phút |
| ENUM_VIOLATION | 422 | `enum_violation` | `validation_error_count` | Không |
| OUTLIER_VALUE | 422 | `outlier_detected` | `outlier_count` | Nếu > 5/phút |
| PII_LEAK | 200* | `pii_scrubbed` | `pii_scrub_count` | Mỗi lần |
| INJECTION | 200* | `injection_attempt` | `injection_count` | Mỗi lần |
| FORMAT_ERROR | 422 | `format_error` | `validation_error_count` | Không |
| ADDITIONAL_PROPS | 422 | `unknown_fields` | `validation_error_count` | Không |

*PII và injection: record có thể được accept nhưng nội dung đã sanitize.

---

## Edge Cases cần lưu ý

1. **DGNL điểm thang 1000:** Field `diem_xet_tuyen` dùng chung cho THPTQG (thang 30) và DGNL (thang 1200). Schema hiện tại max=30 sẽ reject DGNL scores — team cần xử lý conditional validation theo `phuong_thuc_xet_tuyen`.

2. **IELTS score với phuong_thuc khác:** Record xét THPTQG nhưng có `ielts_score` khác null là hợp lệ (IELTS bổ sung hồ sơ). Không nên reject.

3. **hoc_phi_vnd = 0:** Hợp lệ cho ngành Sư phạm (Nghị định 116) và trường quân sự. Không phải outlier.

4. **Encoding UTF-8:** Field `ho_ten`, `ten_nganh`, `ghi_chu` chứa tiếng Việt có dấu. Parser phải đảm bảo UTF-8.

5. **Injection trong field ngắn:** `ho_ten` có maxLength=100, đủ để chứa payload injection ngắn. Cần sanitize tất cả string field, không chỉ `ghi_chu`.

---

## Definition of Done

- [x] `admissions_schema.json` parse được, draft-07 compliant
- [x] `admissions_clean.jsonl` — 35 records, parse được, đa dạng case
- [x] `admissions_attack.jsonl` — 20 records, tối thiểu 5 loại lỗi khác nhau
- [x] Tối thiểu 1 case PII leak attempt (có 3 cases: email, CCCD, tài khoản ngân hàng)
- [x] Docs đủ schema + attack patterns + expected behavior
