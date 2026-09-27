# Compliance matrix (kiểm định ở commit 44ddbf7, nhánh loop/hm500k-audit, 27/09/2026)

Đường dẫn code tương đối với `neumf_project_v2/`; báo cáo với `Report DACNTT/`.

| Mã | Trạng thái | Bằng chứng | Việc cần làm |
|---|---|---|---|
| R1 H&M duy nhất | PARTIAL | Code: config mặc định `configs/hm500k.yaml`, `configs/hm500k_global.yaml`; `scripts/common.py` chỉ còn HMAdapter. Còn sót: `configs/dataco.yaml`, `src/data_pipeline/adapters/dataco.py`, `scripts/07_compare_datasets.py`, `outputs/archive/legacy_v1/` (DataCo). Báo cáo: DataCo xuất hiện C1 8, C2 13, C3 30, C4 28, C5 2, abstract 1, abstract_english 1, phuluc_nguon 2 lần. | Người dùng xoá file DataCo (bị chặn với agent). Pha 5 viết lại báo cáo theo H&M. |
| R2 thuần CF | PARTIAL | Đường huấn luyện/đánh giá (`scripts/03_run_experiment.py`, `src/`) không còn đọc articles/customers (loop 0 gỡ content_based.py, hybrid.py, side_features.py). Chỉ demo đọc: `demo/backend/data_context.py:33-34,138,154` — dùng hiển thị tên sản phẩm + onboarding rule-based, KHÔNG đi vào điểm số mô hình (`demo/backend/inference.py` chỉ dùng checkpoint / train counts). Còn sót config vi phạm: `configs/hm_subset.yaml:49,66,71-72`, `configs/hm.yaml:50,70,75-76` (không nạp được nữa vì `src/config.py` đã bỏ các mục đó). Báo cáo còn mô tả hybrid/content (grep C1–C5). | Người dùng xoá config cũ. Pha 1: pytest khẳng định config chính không đọc metadata. Pha 5 sửa báo cáo. |
| R3 NeuMF có pre-training | PASS | `src/models/neumf.py:7 GMF, :27 MLP, :60 NeuMF, :98 load_pretrained`; `scripts/03_run_experiment.py:208` gọi `load_pretrained(gmf, mlp, alpha=cfg.model.pretrain_alpha)`. | — |
| R4 đặc trưng lịch sử mua chỉ từ train | PARTIAL | `src/data_pipeline/preprocessing.py:90-91` scale confidence fit trên train; mặc định `feedback.mode: binary` (không dùng tần suất/recency). Chưa có test khẳng định. | Pha 1: test confidence/popularity chỉ dùng train_df. |
| R5 tuning_log.csv | FAIL | Không có `tuning_log` ở bất kỳ file .py nào (grep rỗng). `scripts/08_hyperparam_sweep.py` chỉ sweep NeuMF-Scratch, không ghi trail chung. | Pha 4: trail tuning_log.csv (config hash, commit, val metrics, thời gian) cho mọi mô hình. |
| R6 P/R/NDCG/HR, Full Ranking chính | PARTIAL | Metric nhiều item đúng: `src/evaluation/metrics.py multi_ranking_metrics` + `tests/test_global_split.py` (tính tay). `configs/hm500k_global.yaml`: full_ranking + include_redundant_metrics true. Còn sót `configs/hm_primary.yaml:47 primary: sampled`. Báo cáo C2:298, C3:54 mô tả P/R như độ đo độc lập nhưng số liệu cũ là LOO (P=HR/K, R=HR). | Người dùng xoá hm_primary.yaml. Pha 5 sửa C2/C3 theo Q1 (global). |
| R7 triển khai đo được | FAIL | Có demo FastAPI (`demo/backend/routes.py`) nhưng không có số đo độ trễ nào trong code/kết quả. | Pha 4: đo p50/p95 Top-K trên CPU, ghi cấu hình máy. |
| R8 báo cáo khớp code, không đề tài khác | FAIL | `Report DACNTT/chuong1.tex` (349 dòng, không được main.tex \include) là nội dung đề tài KHÁC (tồn kho, học tăng cường: dòng 26, 78-182). `Bao_Cao_Ly_Thuyet_Chuong_1_2_NeuMF.md` dùng DataCo + "khóa luận". Báo cáo C1–C5 dựa trên DataCo và hm_subset 100k. | Người dùng xoá chuong1.tex (+ quyết định file .md). Pha 5 viết lại. |

## Checklist V3

| Mục | Trạng thái | Bằng chứng | Việc cần làm |
|---|---|---|---|
| results_per_user.csv từ pipeline chính | FAIL | 03 không xuất; chỉ có ở `demo/scripts/build_offline_artifacts.py` (LOO) và script tạm ngoài repo. | Pha 2: 03 xuất results_per_user.csv (user, model, rank từng test item, metric). |
| multi-seed | PARTIAL | Có `scripts/04_multi_seed.py`, `06_aggregate_seeds.py`; chưa chạy. Mọi output đã bị xoá khỏi `outputs/` (không phải do agent). | Pha 4: 3 seed (Q4). |
| n_candidates mỗi user | FAIL | Không log trong 03 (grep rỗng). | Pha 2. |
| tuning_log.csv | FAIL | xem R5. | Pha 4. |
| config hash + git commit mỗi run | FAIL | metadata.json không có (grep `config_hash|git_commit` rỗng). | Pha 2: ghi vào metadata.json. |
| kiểm định paired per-user | FAIL | Không có trong pipeline; chỉ có script tạm ngoài repo. | Pha 4: script kiểm định + Holm. |
| khoá test (--final, test_access_log.csv) | FAIL | 03 luôn đánh giá test trong cùng lần chạy (grep `--final` rỗng). | Pha 2: tách đánh giá test sau cờ --final + log. |

## Truy vết R2 (config → script → model/scorer)
- `run.py train/all` → `scripts/03_run_experiment.py --config configs/hm500k*.yaml` → `build_adapter` (HMAdapter, chỉ transactions) → `build_interactions` → split → models GMF/MLP/EarlyFusion/NeuMF (`src/models/`) + baselines Random/MostPopular/BPR-MF/ItemKNN (`src/baselines/classical.py`). Không import module đọc metadata.
- `demo/backend/data_context.py` đọc articles (hiển thị) + customers (tuổi cho onboarding rule-based, `demo/backend/onboarding.py`) — ngoài đường điểm số mô hình.

## Grep đề tài/dự án khác (khóa luận, KLTN, tồn kho, inventory, reinforcement, MARL)
Kết quả ≠ 0: `Report DACNTT/chuong1.tex` (nhiều dòng), `Report DACNTT/Bao_Cao_Ly_Thuyet_Chuong_1_2_NeuMF.md:12,71,72,182` ("khóa luận"). Code, README, demo: 0.
