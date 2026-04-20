# Individual Report - Pham Quoc Dung (2A202600490)

## 1) Vai tro
- D13-T03: Tracing va metadata enrichment.

## 2) Phan viec da hoan thanh
- Tich hop tracing cho luong xu ly chinh (`agent.run`, `rag.retrieve`, `llm.generate`).
- Dam bao propagation `correlation_id` xuyen suot tu request -> span metadata -> logs.
- Cap nhat tuong thich Langfuse v3 client API va bo sung metadata de dieu tra su co.
- Cung cap bo evidence runtime tracing (trace list, waterfall, correlation proof).

## 3) Git evidence (commits chinh)
- https://github.com/jot2003/Lab13_C401_E3/commit/ae8f2bf
- https://github.com/jot2003/Lab13_C401_E3/commit/92d3fc8
- https://github.com/jot2003/Lab13_C401_E3/commit/e0904c7
- https://github.com/jot2003/Lab13_C401_E3/commit/1ef28e32da95406110bace00e86182e533b669a2

## 4) Anh huong den he thong
- Tang kha nang root-cause analysis theo flow Metrics -> Traces -> Logs.
- Dam bao moi request co the truy vet theo mot `correlation_id` duy nhat o nhieu tang.
- Giam rui ro "mat dau vet" khi demo incident runtime.

## 5) Van de gap phai va cach xu ly
- Khac biet API Langfuse giua version cu va v3 -> doi sang helper an toan va cap nhat cach update span/trace.
- Co nhung span thieu metadata correlation -> bo sung logic truyen correlation_id xuyen qua cac ham noi bo.

## 6) Cau hoi van dap co the tra loi
- Tai sao can propagation `correlation_id` cho tracing thay vi chi log?
- Khac nhau giua trace-level metadata va span-level metadata trong bai nay?
- Khi inject incident, dung trace de chung minh root cause nhu the nao?
