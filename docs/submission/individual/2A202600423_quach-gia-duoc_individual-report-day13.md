# Individual Report - Quach Gia Duoc (2A202600423)

## 1) Vai trò
- D13-T02: Logging schema + PII scrubbing.

## 2) Phạm vi task đã làm
- Mở rộng bộ nhận diện PII trong app/pii.py cho các nhóm dữ liệu: email, số điện thoại Việt Nam, CCCD, số thẻ, hộ chiếu.
- Bổ sung test cho PII scrubbing trong tests/test_pii.py để kiểm tra đầy đủ các mẫu dữ liệu nhạy cảm.
- Bật processor scrub PII trong pipeline logging và xử lý scrub đệ quy cho payload lồng nhau tại app/logging_config.py.
- Chuẩn hóa logging schema trong config/logging_schema.json để siết chặt ràng buộc trường log.
- Bổ sung bind context cho log API tại app/main.py để có đủ user_id_hash, session_id, feature, model, env.
- Phối hợp kiểm thử tích hợp bằng cách đồng bộ commit middleware từ nhánh D13-T01 vào nhánh cá nhân để xác minh luồng correlation + enrichment khi chạy validate end-to-end.

## 3) Git evidence (commit chính)
- https://github.com/jot2003/Lab13_C401_E3/commit/90f5dae
- https://github.com/jot2003/Lab13_C401_E3/commit/dbc0f15
- https://github.com/jot2003/Lab13_C401_E3/commit/01fefd2
- https://github.com/jot2003/Lab13_C401_E3/commit/38ec00a
- https://github.com/jot2003/Lab13_C401_E3/commit/5bb3f37

## 4) Ảnh hưởng đến hệ thống
- Log đầu vào/đầu ra API được làm sạch PII, giảm rủi ro lộ dữ liệu nhạy cảm trong logs.
- Log schema chặt chẽ hơn, giúp kiểm tra tự động ổn định hơn khi đánh giá chất lượng observability.
- Context log API đầy đủ hơn, hỗ trợ truy vết theo người dùng, phiên làm việc, tính năng và model.
- Trong lần kiểm thử bàn giao trên nhánh cá nhân, validate_logs đạt 100/100 cho 4 tiêu chí: schema, correlation, enrichment, PII.

## 5) Vấn đề gặp phải và cách xử lý
- Ban đầu validate_logs chưa đạt do thiếu correlation và thiếu enrichment context.
- Cách xử lý:
  - Phối hợp lấy phần middleware correlation từ nhánh D13-T01 để bỏ blocker kỹ thuật.
  - Hoàn thiện bind context ở app/main.py để đáp ứng tiêu chí enrichment.
  - Chạy lại pytest và validate_logs đến khi đạt đầy đủ.

## 6) Câu hỏi vấn đáp có thể trả lời
- PII scrubbing đang diễn ra ở đâu trong pipeline logging và vì sao cần xử lý đệ quy payload?
- Vì sao cần vừa có correlation_id vừa có các trường enrichment như session_id, feature, model?
- Logging schema siết chặt giúp ích gì cho kiểm thử tự động và cho vận hành thực tế?
