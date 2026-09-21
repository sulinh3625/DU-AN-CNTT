# DACNTT — NeuMF Recommendation Project V2

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu.

Phiên bản V2 refactor pipeline để tránh data leakage, chuẩn hóa đánh giá full-ranking. Dự án thực nghiệm trên **hai bộ dữ liệu độc lập**: DataCo Supply Chain (chính, catalog nhỏ/dày đặc) và H&M Personalized Fashion Recommendations (đối chứng, catalog lớn/cực thưa). Chi tiết phương pháp luận và số liệu đầy đủ nằm trong `Report DACNTT/main.pdf` (Chương 3, 4).

## Cây thư mục chính thức

```text
neumf_project_v2/
├── configs/
│   ├── dataco.yaml       # Config DataCo (dùng cho run.py / scripts/run_all.py)
│   ├── hm.yaml           # Config H&M quy mô ĐẦY ĐỦ (đọc data/processed/hm/*.parquet)
│   └── hm_subset.yaml    # Config H&M lát cắt thực nghiệm (đọc raw CSV trực tiếp) — dùng để có số liệu trong báo cáo
├── data/
│   ├── raw/{dataco,hm}/          # Đặt file CSV gốc tại đây (xem README riêng từng thư mục)
│   ├── processed/hm/             # Cache Parquet của H&M, sinh bởi scripts/00_prepare_hm_cache.py
│   └── splits/{dataco,hm}/
├── docs/                          # METHODOLOGY_V2, IMPLEMENTATION_STATUS (đang dùng)
│   └── archive/                   # MIGRATION_V1_TO_V2, legacy_v1_pham_vi_du_an (tài liệu lịch sử V1)
├── src/
│   ├── config.py
│   ├── data_pipeline/            # Xử lý dữ liệu: adapters, preprocessing, k-core, splitting, negative sampling, dataset, audit
│   │                              # (đặt tên khác với data/ ở trên — data/ chỉ chứa FILE dữ liệu thô/đã xử lý, không phải code)
│   ├── models/                   # GMF / MLP / NeuMF / EarlyFusion
│   ├── baselines/                # ItemKNN, BPR-MF
│   ├── training/                 # Vòng lặp huấn luyện
│   ├── evaluation/                # Metrics, full/sampled ranking, long-tail, beyond-accuracy, kiểm định thống kê
│   └── utils/                    # seed, io
├── scripts/
│   ├── 00_prepare_hm_cache.py    # Tiền xử lý 1 lần: CSV H&M gốc (31,8 triệu dòng) -> Parquet gọn nhẹ
│   ├── 01_data_audit.py          # Audit k-core, mật độ, kiểm tra Disjoint — chạy trước khi train
│   ├── 02_preprocess.py          # Sinh splits (dùng khi cần splits độc lập với run_all)
│   ├── 03_run_experiment.py      # Huấn luyện toàn bộ mô hình (GMF/MLP/EarlyFusion/NeuMF) + baselines
│   ├── 04_multi_seed.py          # Lặp lại 03 trên nhiều seed (mặc định 42, 2024, 2025, 2026, 3407)
│   ├── 05_evaluate.py            # Đánh giá + xuất 11 biểu đồ + bảng kết quả từ 1 run_tag
│   ├── 06_aggregate_seeds.py     # Tổng hợp mean±std và kiểm định Wilcoxon từ nhiều seed
│   ├── 07_compare_datasets.py    # Biểu đồ so sánh DataCo vs H&M (dùng trong báo cáo, Hình 4.1)
│   └── run_all.py                # Chạy trọn gói: 03 rồi 05 cho một config, một lệnh duy nhất
├── run.py                         # CLI tổng hợp: all/audit/train/evaluate/multi-seed/aggregate/compare/demo (python run.py -h)
├── demo/                          # Giao diện thực nghiệm (xem mục "Chạy demo" bên dưới)
│   ├── backend/main.py           # FastAPI — suy diễn trên checkpoint đã huấn luyện
│   └── frontend/index.html       # Giao diện web tĩnh
├── outputs/{data_audit,checkpoints,experiments,tables,figures}/
│   └── archive/legacy_v1/         # Kết quả bản V1 cũ, giữ lại để đối chiếu
├── tests/
├── requirements.txt
└── pytest.ini
```

## 1. Cài đặt

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

Nếu cần CUDA, cài PyTorch theo đúng bản CUDA của máy trước khi cài phần còn lại. Thực nghiệm gốc của báo cáo chạy hoàn toàn trên CPU (không có GPU), xem cấu hình máy ở mục 4.1 báo cáo.

## 2. Đặt dữ liệu thô

```text
data/raw/dataco/DataCoSupplyChainDataset.csv
data/raw/hm/transactions_train.csv   (+ articles.csv, customers.csv — xem data/raw/hm/README.md)
```

## 3. Huấn luyện DataCo (một lệnh)

```bash
python run.py all --dataset dataco --run-tag dataco_<tag_của_bạn>
```

`run.py` ở gốc dự án gom tất cả lệnh trong `scripts/` lại một chỗ — `all` tự động: audit → huấn luyện GMF → MLP → EarlyFusion → NeuMF-Scratch → NeuMF-Pretrained → baselines (ItemKNN, BPR-MF) → gọi `05_evaluate.py` xuất bảng (`outputs/tables/<run_tag>/`) và 11 biểu đồ (`outputs/figures/<run_tag>/`). Mất khoảng 10–15 phút trên CPU phổ thông.

`--dataset` nhận `dataco` / `hm` / `hm_subset`. Xem toàn bộ lệnh sẵn có:

```bash
python run.py -h              # danh sách lệnh: all, audit, preprocess, train, evaluate,
                               # multi-seed, aggregate, compare, prepare-hm-cache, demo
python run.py <lệnh> -h       # chi tiết tham số từng lệnh
```

Muốn chạy tay từng bước hoặc gọi thẳng script gốc thì dùng `scripts/01_data_audit.py`, `scripts/run_all.py`, ... — `run.py` chỉ gọi lại các script này, không có logic riêng.

## 4. Huấn luyện H&M

H&M gốc có **31,8 triệu dòng** — quá nặng để đọc lại mỗi lần chạy. Quy trình 2 bước:

```bash
# Bước 1 (chạy 1 lần duy nhất, ~2 phút): nén CSV gốc thành cache Parquet nhẹ
python scripts/00_prepare_hm_cache.py

# Bước 2: audit + train trên lát cắt thực nghiệm (nhanh, ~1-2 phút — đúng cấu hình đã dùng trong báo cáo)
python run.py all --dataset hm_subset --run-tag hm_<tag_của_bạn>
```

> `configs/hm_subset.yaml` đọc trực tiếp `transactions_train.csv` (100.000 dòng đầu) — đây là quy mô thực tế dùng để tạo số liệu trong báo cáo (mục 3.3.3). `configs/hm.yaml` trỏ tới cache Parquet ở quy mô **toàn bộ** (889.062 người dùng, 90.690 sản phẩm sau lọc) — audit chạy được (`01_data_audit.py --config configs/hm.yaml`), nhưng **huấn luyện + đánh giá Full Ranking ở quy mô này chưa khả thi** trên CPU phổ thông (ước tính hàng chục tỷ phép tính, xem mục 3.3.3/5.3 báo cáo) — cần chuyển sang giao thức Sampled-99 trước khi chạy, đây là hướng phát triển đã ghi trong báo cáo.

## 5. Multi-seed & kiểm định thống kê (tuỳ chọn)

```bash
python run.py multi-seed --dataset dataco --seeds 42 2024 2025 2026 3407
python run.py aggregate --dataset dataco --seeds 42 2024 2025 2026 3407
```

Mỗi seed chạy lại toàn bộ bước 3 (~10-15 phút/seed trên DataCo) — hạ tầng đã sẵn sàng nhưng chưa được chạy đủ 5 seed trong báo cáo hiện tại (ghi rõ là hạn chế ở mục 5.2).

## 6. So sánh trực quan DataCo vs H&M

```bash
python scripts/07_compare_datasets.py
```

Sinh `outputs/figures/comparison/dataco_vs_hm_comparison.png` (dùng trong báo cáo, Hình 4.1) từ `results_primary.csv` của hai run tag `dataco_20260918_verify` / `hm_20260918_verify` — sửa hằng số `dataco_dir`/`hm_dir` trong script nếu bạn dùng run tag khác.

## 7. Chạy demo (giao diện thực nghiệm)

Demo nạp checkpoint đã huấn luyện ở bước 3/4 để suy diễn (inference-only, không huấn luyện lại), thiết kế theo mục 3.7 báo cáo.

```bash
# fastapi/uvicorn/pyarrow đã có trong requirements.txt
python -m uvicorn demo.backend.main:app --port 8000 --host 127.0.0.1
```

Mở trình duyệt tại **http://localhost:8000**. Lần đầu chọn mỗi bộ dữ liệu sẽ mất vài giây (server tái tạo pipeline tiền xử lý để suy ra đúng ánh xạ ID ↔ checkpoint); các lần sau tức thời vì đã cache trong bộ nhớ tiến trình.

Yêu cầu trước khi chạy: đã train xong ít nhất 1 lần cho mỗi bộ dữ liệu (mục 3-4). **Demo tự động dùng run_tag mới nhất** khớp tiền tố `dataco_`/`hm_` trong `outputs/experiments/` (ưu tiên run đã hoàn chỉnh, có checkpoint đầy đủ) — train ra run_tag mới rồi gọi `POST /api/reload/{dataset}` (hoặc khởi động lại server) để demo dùng ngay dữ liệu mới nhất, không cần sửa code. Chi tiết kiến trúc/API xem `demo/README.md` và mục 3.7 báo cáo.

## 8. Test

```bash
pytest -q
```
