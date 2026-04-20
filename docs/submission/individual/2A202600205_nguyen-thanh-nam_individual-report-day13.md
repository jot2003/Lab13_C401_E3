# Individual Report - Nguyen Thanh Nam (2A202600205)

## 1) Vai tro
- D13-T04: SLO, Alert rules va Runbook incident.

## 2) Phan viec da hoan thanh
- Dinh nghia bo SLO theo domain tu van tuyen sinh trong `config/slo.yaml` (latency, error rate, cost, quality).
- Xay dung va chuan hoa alert rules trong `config/alert_rules.yaml` voi severity, condition, owner, runbook link.
- Cap nhat `docs/alerts.md` theo huong runbook thuc thi duoc, bo sung attack-to-alert mapping.
- Dong bo ten metric key giua SLO/alerts va metric snapshot cua he thong.

## 3) Git evidence (commits chinh)
- https://github.com/jot2003/Lab13_C401_E3/commit/797b721
- https://github.com/jot2003/Lab13_C401_E3/commit/51d57d2
- https://github.com/jot2003/Lab13_C401_E3/commit/392df10
- https://github.com/jot2003/Lab13_C401_E3/commit/71a7342

## 4) Anh huong den he thong
- Dat duoc baseline quan sat theo SLO ro rang cho demo va danh gia chat luong dich vu.
- Alert + runbook giup doi nhom chuan hoa thao tac xu ly su co thay vi debug tu do.
- Co lien ket giua data attack va canh bao, giup demo "phat hien -> chan doan -> hanh dong" mach lac.

## 5) Van de gap phai va cach xu ly
- Lech ten metric giua alert config va API snapshot -> doi metric key cho dong bo.
- Co command incident trong runbook chua dung endpoint that -> cap nhat lai syntax script inject incident.

## 6) Cau hoi van dap co the tra loi
- Vi sao nguong SLO va alert threshold khong dat giong nhau?
- Alert `avg_cost_usd > 2x_baseline` nen giai thich baseline theo cach nao de tranh mo ho?
- Khi nao xep severity P1/P2 trong bo alert cua domain tuyen sinh?
