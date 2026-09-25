# DACNTT — NeuMF Recommendation Project V2

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu.

Phiên bản V2 refactor pipeline để tránh data leakage, chuẩn hóa đánh giá full-ranking. Dự án thực nghiệm trên **hai bộ dữ liệu độc lập**: DataCo Supply Chain (chính) và H&M Personalized Fashion Recommendations (đối chứng). Chi tiết phương pháp luận và số liệu đầy đủ trong `Report DACNTT/main.pdf`.

Xem `pham_vi_du_an.md` để hiểu quyết định thiết kế pipeline/evaluation trước khi sửa code.

---

## Cây thư mục

```text
neumf_project_v2/
├── configs/
│   ├── dataco.yaml          # Config DataCo
│   ├── hm.yaml              # Config H&M quy mô đầy đủ (89 vạn users — chỉ audit được, chưa train Full Ranking)
│   └── hm_subset.yaml       # Config H&M lát cắt 100K dòng — đây là config dùng trong báo cáo
├── data/
│   ├── raw/{dataco,hm}/     # Đặt file CSV gốc tại đây
│   ├── processed/hm/        # Cache Parquet H&M (sinh bởi scripts/00_prepare_hm_cache.py)
│   └── splits/{dataco,hm}/
├── src/
│   ├── config.py
│   ├── data_pipeline/       # adapters, preprocessing, k-core, splitting, negative sampling, dataset, audit
│   ├── models/              # GMF, MLP, NeuMF, EarlyFusion
│   ├── baselines/           # ItemKNN, BPR-MF, classical, content_based (CBF), hybrid
│   ├── training/            # trainer.py — vòng lặp huấn luyện, early stopping
│   ├── evaluation/          # full_ranking, sampled_ranking, metrics, long_tail, cold_start, beyond_accuracy
│   └── utils/               # seed, io
├── scripts/
│   ├── 00_prepare_hm_cache.py   # Nén CSV H&M 31,8M dòng → Parquet (chạy 1 lần)
│   ├── 01_data_audit.py         # Audit k-core, mật độ, kiểm tra Disjoint
│   ├── 02_preprocess.py         # Sinh splits thủ công
│   ├── 03_run_experiment.py     # Train toàn bộ mô hình + baselines
│   ├── 04_multi_seed.py         # Lặp lại 03 trên nhiều seed
│   ├── 05_evaluate.py           # Đánh giá + xuất bảng + 11 biểu đồ
│   ├── 06_aggregate_seeds.py    # Tổng hợp mean±std + kiểm định Wilcoxon
│   ├── 07_compare_datasets.py   # Biểu đồ so sánh DataCo vs H&M (Hình 4.1 báo cáo)
│   └── run_all.py               # Chạy 03 rồi 05 một lệnh duy nhất
├── demo/
│   ├── backend/main.py      # FastAPI — inference-only trên checkpoint đã train
│   └── frontend/index.html  # Giao diện web tĩnh
├── outputs/
│   ├── checkpoints/         # Model weights (.pt) theo run_tag
│   ├── experiments/         # results.json, CSV kết quả, history theo run_tag
│   ├── figures/             # Biểu đồ PNG
│   ├── tables/              # Bảng CSV tổng hợp
│   └── data_audit/          # Kết quả audit
├── tests/
│   ├── test_data_pipeline.py
│   ├── test_evaluation.py
│   └── test_models.py
├── run.py                   # CLI tổng hợp (python run.py -h)
├── pham_vi_du_an.md         # Phạm vi + phương pháp luận V2 — đọc trước khi sửa pipeline/eval
├── data_pipeline_walkthrough.ipynb  # Walkthrough pipeline từng bước
├── pipeline.drawio.xml      # Sơ đồ kiến trúc pipeline (mở bằng draw.io)
├── requirements.txt
├── pytest.ini
├── Dockerfile
└── docker-compose.yml
```

---

## 1. Cài đặt

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

> Thực nghiệm gốc chạy hoàn toàn trên CPU. Nếu có GPU, cài PyTorch bản CUDA trước rồi mới cài `requirements.txt`.

---

## 2. Đặt dữ liệu thô

```text
data/raw/dataco/DataCoSupplyChainDataset.csv
data/raw/hm/transactions_train.csv   (+ articles.csv, customers.csv)
```

---

## 3. Chạy DataCo (một lệnh)

```bash
python run.py all --dataset dataco --run-tag dataco_<tag>
```

Tự động chạy: audit → train GMF → MLP → EarlyFusion → NeuMF-Scratch → NeuMF-Pretrained → baselines → evaluate.
Kết quả: `outputs/tables/<run_tag>/` và `outputs/figures/<run_tag>/`. Mất ~10–15 phút trên CPU.

```bash
python run.py -h              # xem tất cả lệnh: all, audit, train, evaluate, multi-seed, aggregate, compare, demo
python run.py <lệnh> -h       # xem tham số của từng lệnh
```

---

## 4. Chạy H&M

H&M gốc có 31,8 triệu dòng — cần cache Parquet trước:

```bash
# Bước 1 — chạy 1 lần duy nhất (~2 phút)
python scripts/00_prepare_hm_cache.py

# Bước 2 — train trên lát cắt 100K dòng (đúng quy mô dùng trong báo cáo, ~4 phút gồm cả CBF/Hybrid/cold-start)
python run.py all --dataset hm_subset --run-tag hm_<tag>
```

Config H&M dùng đủ 3 file: `transactions_train.csv` (tương tác), `articles.csv` (thuộc tính sản phẩm →
ContentBased, CategoryPopularity, Hybrid-NeuMF-CBF) và `customers.csv` (nhóm tuổi → AgeGroupPopularity).
Ngoài các bảng chung, run H&M sinh thêm `cold_start_results.csv` (cold vs warm) và
`strict_cold_start_results.csv` (user bị k-core loại — CF thuần ID không chấm được), hình 12–13.
Tắt/bật trong YAML: `baselines.enabled` (`content_based`, `category_popularity`, `age_popularity`),
`hybrid.enabled`, `evaluation.strict_cold_start`.

> `configs/hm.yaml` (toàn bộ 889K users × 90K items) chỉ audit được, không thể chạy Full Ranking trên CPU — xem hạn chế mục 5.3 báo cáo.

---

## 5. Multi-seed & kiểm định thống kê

```bash
python run.py multi-seed --dataset dataco --seeds 42 2024 2025 2026 3407
python run.py aggregate  --dataset dataco --seeds 42 2024 2025 2026 3407
```

Mỗi seed ~10–15 phút. `aggregate` xuất bảng mean±std và p-value Wilcoxon. Hạ tầng đã sẵn sàng nhưng chưa chạy đủ 5 seed trong báo cáo hiện tại (ghi là hạn chế ở mục 5.2).

---

## 6. So sánh DataCo vs H&M

```bash
python scripts/07_compare_datasets.py
```

Sinh `outputs/figures/comparison/dataco_vs_hm_comparison.png` (Hình 4.1 báo cáo). Script đọc `results_primary.csv` từ 2 run tag — sửa hằng số `dataco_dir` / `hm_dir` trong file nếu dùng run tag khác.

---

## 7. Chạy demo

```bash
python -m uvicorn demo.backend.main:app --port 8000 --host 127.0.0.1
```

Mở trình duyệt tại **http://localhost:8000**. Yêu cầu đã train xong ít nhất 1 lần (bước 3 hoặc 4). Demo tự động chọn run_tag mới nhất — train run mới xong gọi `POST /api/reload/{dataset}` để cập nhật ngay, không cần restart.

---

## 8. Test

```bash
pytest -q
```
