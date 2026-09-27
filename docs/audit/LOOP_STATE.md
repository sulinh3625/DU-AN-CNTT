## Lượt hiện tại: 1 | Pha: 0 (xong) → 1
Prompt + quyết định người dùng: docs/audit/LOOP_PROMPT.md. Nhánh: loop/hm500k-audit (không push).

## Hạng mục
| ID | Mô tả | Trạng thái | Bằng chứng | Bị chặn bởi |
|---|---|---|---|---|
| P0 | Kiểm định R1–R8 + V3 → COMPLIANCE_MATRIX.md | DONE | docs/audit/COMPLIANCE_MATRIX.md | — |
| P1a | Thuần CF: gỡ content-based khỏi code (Q3=a) | DONE | commit 44ddbf7 (loop 0) | — |
| P1b | pytest: config chính không đọc metadata; confidence/popularity chỉ từ train | TODO | | — |
| P1c | Lưu checkpoint BPR-MF (F7) | TODO | | — |
| P1d | Xoá LightGCN/SASRec (F6, người dùng chọn xoá) | TODO | src/models/lightgcn.py, sasrec.py không được gọi | có thể bị chặn xoá |
| P2a | Split theo Q1 (mốc thời gian chung) + metric nhiều item đúng + unit test | DONE | src/data_pipeline/splitting.py global_temporal_split; tests/test_global_split.py | — |
| P2b | 03: metadata ghi config hash + git commit; log n_candidates; xuất results_per_user.csv | TODO | | — |
| P2c | Khoá test: đánh giá test chỉ qua --final + docs/audit/test_access_log.csv | TODO | | — |
| P2d | Test không rò rỉ thời gian (train < val < test theo first_timestamp) trên dữ liệu thật | TODO | | — |
| P3a | REFERENCES.md (đọc thật từng nguồn) | TODO | | — |
| P3b | CANDIDATES.md + đo 1 epoch/Full Ranking thử | TODO | | P3a |
| P3c | Baseline mạnh: MostPopular cửa sổ gần, iALS (implicit) | TODO | | — |
| P3d | PREREG.md commit trước mọi test | TODO | | P3a, P3b |
| P4a | Tuning chỉ val → tuning_log.csv (ngân sách như nhau) | TODO | | P2b, P2c, P3d |
| P4b | Multi-seed (3) + --final + kiểm định paired + Holm | TODO | | P4a |
| P4c | Đo độ trễ Top-K p50/p95 CPU (R7) | TODO | | — |
| P5a | Bảng .tex sinh từ kết quả; C4 \input | TODO | | P4b |
| P5b | Viết lại báo cáo bỏ DataCo, sửa P/R, hybrid/content, độ trễ | TODO | | P4b, P4c |
| P5c | Demo trỏ run được chọn | TODO | | P4b |

## Cần người dùng quyết định / làm
- Xoá file (agent bị hệ thống chặn): `neumf_project_v2/configs/{dataco,hm,hm_subset,hm_primary}.yaml`,
  `src/data_pipeline/adapters/dataco.py`, `scripts/07_compare_datasets.py`, `scripts/00_prepare_hm_cache.py`,
  `PLAN_swap_primary_dataset.md`, `docs/refactor_audit.md`, `data_pipeline_walkthrough.ipynb`, `outputs/archive/`,
  `Report DACNTT/chuong1.tex` (đề tài khác). Lệnh: `git rm -rf <các file trên>`.
- `Report DACNTT/Bao_Cao_Ly_Thuyet_Chuong_1_2_NeuMF.md`: bản nháp dùng DataCo + chữ "khóa luận" — xoá hay sửa?
- Lưu ý: toàn bộ outputs/experiments|checkpoints|tables|figures đã bị xoá trước loop (không phải agent) →
  các run hm500k_seed42, hm500k_global_seed42 cần chạy lại (sẽ chạy lại trong Pha 4 theo khoá test).
- Lệch bất biến: k-core = 10 (Q2) thay vì 5.

## Ngân sách đã dùng: 0 / 8 giờ GPU

## Nhật ký lượt (mới nhất ở trên)
- Lượt 1: Pha 0 — lập COMPLIANCE_MATRIX (R3 PASS; R1, R2, R4, R6 PARTIAL; R5, R7, R8 FAIL; V3 phần lớn FAIL);
  phát hiện `Report DACNTT/chuong1.tex` là đề tài khác. Kiểm chứng: `pytest tests -q` → 56 passed.
  Lượt sau: P1b (pytest thuần CF + chỉ-train).
- Lượt 0: commit điểm xuất phát 44ddbf7 (hm500k, split mốc thời gian chung, gỡ content-based).
