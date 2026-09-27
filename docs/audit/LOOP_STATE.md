## Lượt hiện tại: 8 | Pha: 3
Prompt + quyết định người dùng: docs/audit/LOOP_PROMPT.md. Nhánh: loop/hm500k-audit (không push).

## Hạng mục
| ID | Mô tả | Trạng thái | Bằng chứng | Bị chặn bởi |
|---|---|---|---|---|
| P0 | Kiểm định R1–R8 + V3 → COMPLIANCE_MATRIX.md | DONE | docs/audit/COMPLIANCE_MATRIX.md | — |
| P1a | Thuần CF: gỡ content-based khỏi code (Q3=a) | DONE | commit 44ddbf7 (loop 0) | — |
| P1b | pytest: config chính không đọc metadata; confidence/popularity chỉ từ train | DONE | neumf_project_v2/tests/test_pure_cf.py (7 test) | — |
| P1c | Lưu checkpoint BPR-MF (F7) | DONE | src/baselines/classical.py BPRMFBaseline.save/load; scripts/03_run_experiment.py lưu ckpt_dir/bpr.npz; demo nạp qua BPRMFBaseline.load; tests/test_models.py::test_bpr_checkpoint_roundtrip_and_demo_scoring_match | — |
| P1d | Xoá LightGCN/SASRec (F6, người dùng chọn xoá) | DONE | git rm src/models/lightgcn.py, sasrec.py (không file nào import); pham_vi_du_an.md cập nhật | — |
| P2a | Split theo Q1 (mốc thời gian chung) + metric nhiều item đúng + unit test | DONE | src/data_pipeline/splitting.py global_temporal_split; tests/test_global_split.py | — |
| P2b | 03: metadata ghi config hash + git commit; log n_candidates; xuất results_per_user.csv | DONE (smoke loop 6 OK) | src/utils/io.py run_provenance; src/evaluation/full_ranking.py per_user + _per_user_row; 03: metadata.provenance, n_candidates_test, results_per_user.csv; tests/test_evaluation.py (2 test mới) | — |
| P2c | Khoá test: đánh giá test chỉ qua --final + docs/audit/test_access_log.csv | DONE | 03 run(final=...): không --final → mọi bảng trên VALIDATION; --final cần PREREG.md đã commit + --reason, ghi test_access_log.csv trước khi đánh giá; cờ truyền qua run.py/run_all/04; 05 ghi 'Đánh giá trên'; tests/test_test_lock.py | — |
| P2d | Test không rò rỉ thời gian (train < val < test theo first_timestamp) trên dữ liệu thật | DONE | tests/test_no_leakage_real_data.py (global: 1 timeline + user/item val/test ⊂ train; LOO: val ≥ train, test ≥ val từng user) | — |
| P3a | REFERENCES.md (đọc thật từng nguồn) | DONE (DMF chỉ abstract; MS notebook một phần) | docs/audit/REFERENCES.md | — |
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

## Ngân sách đã dùng: 0,3 / 8 giờ GPU (smoke 18,5 phút)

## Nhật ký lượt (mới nhất ở trên)
- Lượt 8: P3a — đọc NCF (full text + README code gốc), Rendle 2020, Dacrema 2019, Krichene & Rendle 2020, Rendle 2022 iALS, DeepCF (full text + README), RecBole NeuMF; DMF chỉ đọc được abstract; MS ncf_deep_dive chỉ một phần. Hệ quả: baseline MF/BPR phải tune cùng ngân sách, thêm iALS; ItemKNN không chạy được (10.345 item > ngưỡng 5.000). Kiểm chứng: file REFERENCES.md có link + điều lấy được + áp dụng/không cho từng nguồn. Lượt sau: P3c (baseline iALS + MostPopular cửa sổ gần).
- Lượt 7: P2d — test rò rỉ thời gian trên dữ liệu thật hm500k (cả 2 cách chia). Kiểm chứng: `pytest tests -q` → 72 passed (2 test mới chạy thật trên hm500k, 9,6 s). Pha 2 xong. Lượt sau: P3a (REFERENCES.md, đọc thật từng nguồn).
- Lượt 6: P2c — khoá tập test (--final + PREREG + test_access_log.csv). Kiểm chứng: `pytest tests -q` → 70 passed; smoke 03 (configs/hm500k_global.yaml, 1 epoch, run smoke_p2c, 18,5 phút): evaluated_on=validation, provenance có config_hash/git_commit, n_candidates_eval min 9.863/max 10.144, results_per_user.csv 8 model × 2.275 user, trung bình per-user khớp results_primary (lệch 1e-16), không tạo test_access_log.csv. Lượt sau: P2d (test không rò rỉ thời gian trên dữ liệu thật).
- Lượt 5: P2b — provenance (config_hash sha256 của config đã nạp, git_commit, git_dirty) + n_candidates_test vào metadata.json; evaluate_* nhận per_user=list → 03 ghi results_per_user.csv (model, user, customer_id, n_candidates, n_positives, ranks, metric). Kiểm chứng: `pytest tests -q` → 66 passed; py_compile 03 OK. Chưa chạy 03 thật để tránh chạm test trước P2c. Lượt sau: P2c (--final + test_access_log.csv).
- Lượt 4: P1d — git rm src/models/lightgcn.py, sasrec.py (grep: không code nào dùng; chỉ docs/refactor_audit.md — file chờ người dùng xoá). Kiểm chứng: `pytest tests -q` → 64 passed. Pha 1 xong. Lượt sau: P2b (metadata config hash + git commit, n_candidates, results_per_user.csv trong 03).
- Lượt 3: P1c — 03 lưu bpr.npz; BPRMFBaseline.save/load; demo chấm BPR bằng Q @ P[u] (khớp score_items của 03). Kiểm chứng: `pytest tests -q` → 64 passed; py_compile 03 + demo OK. Chưa chạy 03 thật (chờ Pha 4). Lượt sau: P1d (xoá LightGCN/SASRec).
- Lượt 2: P1b — tests/test_pure_cf.py: config chính không có side_features/content/hybrid, baseline chỉ CF; code src/ + scripts 01–06 không nhắc articles/customers/side_features; adapter chỉ mở file transactions (monkeypatch pd.read_csv); scale confidence chỉ fit trên train; 03 tính popularity/head/cold/TrainDataset từ train_df. Kiểm chứng: `pytest tests -q` → 63 passed. Lượt sau: P1c (lưu checkpoint BPR-MF).
- Lượt 1: Pha 0 — lập COMPLIANCE_MATRIX (R3 PASS; R1, R2, R4, R6 PARTIAL; R5, R7, R8 FAIL; V3 phần lớn FAIL);
  phát hiện `Report DACNTT/chuong1.tex` là đề tài khác. Kiểm chứng: `pytest tests -q` → 56 passed.
  Lượt sau: P1b (pytest thuần CF + chỉ-train).
- Lượt 0: commit điểm xuất phát 44ddbf7 (hm500k, split mốc thời gian chung, gỡ content-based).
