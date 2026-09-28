# DACNTT — NeuMF Recommendation Project V2

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu.

Phiên bản V2 refactor pipeline để tránh data leakage, chuẩn hóa đánh giá full-ranking. Dự án thực nghiệm trên bộ dữ liệu **H&M Personalized Fashion Recommendations** (catalog lớn, cực thưa). Chi tiết phương pháp luận và số liệu đầy đủ nằm trong `Report DACNTT/main.pdf` (Chương 3, 4).

## Cây thư mục chính thức

```text
neumf_project_v2/
├── configs/
│   ├── hm.yaml           # Config H&M quy mô ĐẦY ĐỦ (đọc data/processed/hm/*.parquet)
│   └── hm_subset.yaml    # Config H&M mẫu ~300k dòng theo khách, trải 2 năm — dùng để có số liệu trong báo cáo
├── data/
│   ├── raw/hm/                   # Đặt file CSV gốc tại đây
│   ├── processed/hm/             # Mẫu hm300k (00_sample_hm.py) và cache Parquet (00_prepare_hm_cache.py)
│   └── splits/hm/
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
│   ├── 00_sample_hm.py           # Lấy mẫu ~300k dòng theo khách hàng, trải toàn bộ 2 năm (cho hm_subset)
│   ├── 00_prepare_hm_cache.py    # Tiền xử lý 1 lần: CSV H&M gốc (31,8 triệu dòng) -> Parquet (cho hm)
│   ├── 01_data_audit.py          # Audit k-core, mật độ, kiểm tra Disjoint — chạy trước khi train
│   ├── 02_preprocess.py          # Sinh splits (dùng khi cần splits độc lập với run_all)
│   ├── 03_run_experiment.py      # Huấn luyện toàn bộ mô hình (GMF/MLP/EarlyFusion/NeuMF) + baselines
│   ├── 04_multi_seed.py          # Lặp lại 03 trên nhiều seed (mặc định 42, 2024, 2025, 2026, 3407)
│   ├── 05_evaluate.py            # Đánh giá + xuất 11 biểu đồ + bảng kết quả từ 1 run_tag
│   ├── 06_aggregate_seeds.py     # Tổng hợp mean±std và kiểm định Wilcoxon từ nhiều seed
│   └── run_all.py                # Chạy trọn gói: 03 rồi 05 cho một config, một lệnh duy nhất
├── run.py                         # CLI tổng hợp: all/audit/train/evaluate/multi-seed/aggregate/demo (python run.py -h)
├── demo/                          # Giao diện thực nghiệm (xem mục "Chạy demo" bên dưới)
│   ├── backend/main.py           # FastAPI — suy diễn trên checkpoint đã huấn luyện
│   └── frontend/index.html       # Giao diện web tĩnh
├── outputs/{data_audit,checkpoints,experiments,tables,figures}/
│   └── archive/legacy_v1/         # Kết quả bản V1 cũ, giữ lại để đối chiếu
├── tests/
├── colab_final.ipynb              # Chạy pipeline trên Google Colab (code từ GitHub, dữ liệu + kết quả trên Drive)
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

Nếu cần CUDA, cài PyTorch theo đúng bản CUDA của máy trước khi cài phần còn lại. `configs/hm_subset.yaml` đặt `device: auto`: dùng GPU nếu có, không thì CPU. `seed_everything` bật chế độ tất định cho CUDA nên chạy lại cùng seed trên cùng máy cho cùng kết quả; GPU và CPU cho số khác nhau ở các mô hình có dropout, nên mọi số liệu báo cáo phải chạy trên cùng một thiết bị.

## 2. Đặt dữ liệu thô

```text
data/raw/hm/transactions_train.csv
```

Sau đó lấy mẫu một lần (~1,5 phút, đọc theo lô nên ít RAM):

```bash
python scripts/00_sample_hm.py
```

Script chọn ngẫu nhiên (seed 42) các khách hàng và giữ **toàn bộ lịch sử** của họ cho tới khi đủ ~300.000 dòng, ghi ra `data/processed/hm/hm300k_transactions.csv` với cột/ID gốc. Không lấy ngẫu nhiên theo *dòng*: 300k dòng rải trên 1,36 triệu khách thì mỗi khách chỉ còn ~0,2 giao dịch và lọc k-core=5 xoá sạch dữ liệu. Script cũng in thống kê trùng lặp (dòng trùng hệt nhau = mua nhiều đơn vị, được gộp ở bước tiền xử lý).

## 3. Huấn luyện H&M (một lệnh)

```bash
python run.py all --dataset hm_subset --run-tag hm_<tag_của_bạn>
```

`run.py` ở gốc dự án gom tất cả lệnh trong `scripts/` lại một chỗ — `all` tự động: audit → huấn luyện GMF → MLP → EarlyFusion → NeuMF-Scratch → NeuMF-Pretrained → baselines (Random, MostPopular, BPR-MF) → gọi `05_evaluate.py` xuất bảng (`outputs/tables/<run_tag>/`) và 11 biểu đồ (`outputs/figures/<run_tag>/`).

`--dataset` nhận `hm_subset` (mặc định) / `hm`. Xem toàn bộ lệnh sẵn có:

```bash
python run.py -h              # danh sách lệnh: all, audit, preprocess, train, evaluate,
                               # multi-seed, aggregate, prepare-hm-cache, demo
python run.py <lệnh> -h       # chi tiết tham số từng lệnh
```

Muốn chạy tay từng bước hoặc gọi thẳng script gốc thì dùng `scripts/01_data_audit.py`, `scripts/run_all.py`, ... — `run.py` chỉ gọi lại các script này, không có logic riêng.

## 4. Hai quy mô dữ liệu H&M

> `configs/hm_subset.yaml` đọc mẫu `hm300k_transactions.csv` (300.003 dòng của 12.877 khách, 20/09/2018 → 22/09/2020; sau k-core=5 còn 7.402 khách × 15.216 sản phẩm) — đây là quy mô dùng để tạo số liệu trong báo cáo. `configs/hm.yaml` trỏ tới cache Parquet ở quy mô **toàn bộ** (889.062 người dùng, 90.690 sản phẩm sau lọc) — audit chạy được, nhưng **huấn luyện + đánh giá Full Ranking ở quy mô này chưa khả thi** trên CPU phổ thông (ước tính hàng chục tỷ phép tính, xem mục 3.3.3/5.3 báo cáo) — cần chuyển sang giao thức Sampled-99 trước khi chạy, đây là hướng phát triển đã ghi trong báo cáo.

H&M gốc có **31,8 triệu dòng** — quá nặng để đọc lại mỗi lần chạy, nên `hm.yaml` cần tạo cache Parquet một lần trước:

```bash
python scripts/00_prepare_hm_cache.py          # ~2 phút, chạy 1 lần
python run.py audit --dataset hm
```

## 5. Multi-seed & kiểm định thống kê (tuỳ chọn)

```bash
python run.py multi-seed --dataset hm_subset --seeds 42 2024 2025 2026 3407
python run.py aggregate --dataset hm_subset --seeds 42 2024 2025 2026 3407
```

Mỗi seed chạy lại toàn bộ bước 3.

## 6. Chạy demo (giao diện thực nghiệm)

Demo nạp checkpoint đã huấn luyện ở bước 3 để suy diễn (inference-only, không huấn luyện lại), thiết kế theo mục 3.7 báo cáo.

```bash
# fastapi/uvicorn/pyarrow đã có trong requirements.txt
python -m uvicorn demo.backend.main:app --port 8000 --host 127.0.0.1
```

Mở trình duyệt tại **http://localhost:8000**. Lần đầu mở sẽ mất vài giây (server tái tạo pipeline tiền xử lý để suy ra đúng ánh xạ ID ↔ checkpoint); các lần sau tức thời vì đã cache trong bộ nhớ tiến trình.

Yêu cầu trước khi chạy: đã train xong ít nhất 1 lần (mục 3). **Demo tự động dùng run_tag mới nhất** khớp tiền tố `hm_` trong `outputs/experiments/` (ưu tiên run đã hoàn chỉnh, có checkpoint đầy đủ) — train ra run_tag mới rồi gọi `POST /api/reload` (hoặc khởi động lại server) để demo dùng ngay dữ liệu mới nhất, không cần sửa code. Chi tiết kiến trúc/API xem `demo/README.md` và mục 3.7 báo cáo.

## 7. Test

```bash
pytest -q
```
