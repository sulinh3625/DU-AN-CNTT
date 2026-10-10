# neumf_project — mã nguồn của đề tài

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu.

Kết quả chính theo **giao thức v2** (kế hoạch đăng ký trước: `audit/PREREG_v2.md`):

- **Mô hình đề tài NeuMF-F:** hai nhánh GMF-F và MLP-F hợp nhất sớm như NeuMF. Vector của khách và sản phẩm =
  embedding ID + phép chiếu của đặc trưng (thuộc tính và mô tả văn bản của sản phẩm, thông tin khách, doanh số và thời
  gian — tính theo thời điểm, không dùng thông tin tương lai).
- **Dữ liệu:** hai mẫu khách hàng không giao nhau của H&M — **mẫu phát triển** chỉ để tinh chỉnh (trên tập xác thực),
  **mẫu kiểm định** chỉ để đánh giá cuối (mở tập kiểm thử đúng một lần). Một sản phẩm là một mẫu (`product_code`, mọi màu
  gộp lại); tập ứng viên là các sản phẩm có dữ liệu huấn luyện trước mốc.
- **So sánh:** 14 mô hình, 5 seed, họ 10 so sánh có hiệu chỉnh Holm. Kết quả: `outputs/v2/final/ket_qua.txt`.

Phương pháp chi tiết: `pham_vi_du_an.md`. Mọi lệnh dưới đây chạy từ thư mục `neumf_project/`.

| Mục | Nội dung |
|---|---|
| 1 | Cài đặt |
| 2 | Dữ liệu |
| 3 | Chạy giao thức v2 |
| 4 | Kiểm thử |
| 5 | Demo |
| 6 | Cấu trúc thư mục |

---

## 1. Cài đặt

Python 3.11 trở lên (đã chạy với 3.12 và 3.13), RAM 16 GB. GPU NVIDIA không bắt buộc nhưng nhanh hơn nhiều.

```bash
python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

Có GPU: cài PyTorch bản CUDA **trước** `requirements.txt`, ví dụ
`pip install torch --index-url https://download.pytorch.org/whl/cu124`, rồi kiểm tra
`python -c "import torch; print(torch.cuda.is_available())"`. Cấu hình để `device: auto` nên tự dùng GPU nếu có.

## 2. Dữ liệu

Tải 3 file của cuộc thi Kaggle
[H&M Personalized Fashion Recommendations](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations/data)
(phải bấm *I Understand and Accept* ở trang Rules) vào `data/raw/hm/`:

| File | Dùng cho |
|---|---|
| `transactions_train.csv` (3,5 GB) | Lịch sử mua; doanh số theo ngày của toàn H&M (đặc trưng) |
| `articles.csv` | Thuộc tính và mô tả văn bản của sản phẩm (đặc trưng); tên, loại sản phẩm trên demo |
| `customers.csv` | Thuộc tính khách (đặc trưng); tuổi trong danh sách chọn khách của demo |

Không dùng bản `.xlsx`: Excel cắt ở 1.048.576 dòng. `customers.csv` đúng có 1.371.980 khách; bản chỉ có 1.048.575 dòng
là bản đã bị Excel cắt, cần tải lại (code báo lỗi nếu thiếu dòng).

Tải bằng Kaggle CLI (cần `~/.kaggle/kaggle.json`):

```bash
pip install kaggle
kaggle competitions download -c h-and-m-personalized-fashion-recommendations -f transactions_train.csv -p data/raw/hm
```

(làm tương tự với `articles.csv`, `customers.csv`). Sau đó tạo hai mẫu, đặc trưng và dữ liệu đã lọc — chạy một lần:

```bash
python run.py sample-hm     # mẫu phát triển (khối 0) → data/processed/hm/mau_phat_trien.csv
python run.py v2-data       # mẫu kiểm định (khối 2) → mau_kiem_dinh.csv; đặc trưng → catalog_v2.npz, daily_sales_v2.npz;
                            # dữ liệu đã lọc → outputs/data/<mẫu>.csv.gz + manifest.json (MD5)
```

Mẫu lấy theo băm `customer_id` với khoá cố định nên chạy lại luôn ra đúng cùng file (MD5 ghi trong
`audit/PREREG_v2.md` mục 1). Khối 1 đã bị mở trong lúc phát triển nên không dùng. Thư mục `data/` không được commit.

## 3. Chạy giao thức v2

| Bước | Lệnh | Việc | Thời gian |
|---|---|---|---|
| 1 | `python run.py v2-tune --resume` | Tinh chỉnh trên tập xác thực của mẫu phát triển | khoảng 7 giờ (CPU 4 nhân) |
| 2 | `python run.py v2-dry-run` | Tuỳ chọn: chạy thử trọn đường ống, không chấm test | khoảng 1 giờ |
| 3 | `python run.py v2-final --reason "..."` | Đánh giá cuối trên tập kiểm thử của mẫu kiểm định + xuất bảng, hình cho báo cáo | khoảng 7,5 giờ (RTX 3050 Laptop) |
| 4 | `python run.py check-report` | Đối chiếu câu chữ báo cáo với số liệu | dưới 1 phút |

Chạy qua đêm một lệnh: `python run.py all` = `prepare` → bước 1 (`--resume`) → bước 2; thêm `--final --reason "..."`
để chạy luôn bước 3 ở cuối (khoá kiểm thử của bước 3 vẫn áp dụng). Bị ngắt thì chạy lại đúng lệnh đó: tinh chỉnh đi
tiếp từ cấu hình còn thiếu.

### 3.1 Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển

- Mỗi mô hình có học thử 6 cấu hình (seed 42); mô hình một tham số thử đủ lưới. Lưới: `audit/PREREG_v2.md` mục 4.
- Mỗi cấu hình ghi một dòng `audit/v2/tuning_log.csv` kèm commit và **mã băm mã nguồn** (`code_hash`, tính trên
  `src/`, `scripts/v2_common.py`, `scripts/22_tune_v2.py`, `scripts/02_prepare_data.py`, `configs/v2.yaml`). Cấu hình
  tốt nhất ghi vào `audit/v2/best_configs.json`.
- Bị ngắt thì chạy lại đúng lệnh trên: cấu hình đã có được bỏ qua.
- Xong thì đưa bảng tinh chỉnh vào báo cáo: `python scripts/24_report_v2.py --tuning-only`.

### 3.2 Chạy thử (tuỳ chọn)

`python run.py v2-dry-run` chạy trọn đường ống đánh giá cuối nhưng trên tập xác thực của mẫu phát triển, mỗi mạng nơ-ron
1 epoch — không mở tập kiểm thử nào. Kết quả ở `outputs/v2/dry_run/` (không commit).

### 3.3 Đánh giá cuối — mở tập kiểm thử đúng một lần

**Đã chạy ngày 10/10/2026** (commit `e4e4f25`, `code_hash` `0f1ea1eec5a86c31`; seed 42 chạy lại theo
`audit/PREREG_v2.md` mục 10). Kết quả: `outputs/v2/final/` — đọc nhanh ở `ket_qua.txt`.

```bash
git status       # mọi thay đổi (kể cả audit/PREREG_v2.md, audit/v2/) phải đã commit
python run.py v2-final --reason "Đánh giá cuối v2 theo PREREG_v2"
```

Lệnh chạy hai script:

1. `scripts/23_final_v2.py` — 5 seed (42, 2024, 2025, 2026, 3407). Mỗi seed: mạng nơ-ron chọn số epoch trên tập xác thực
   của mẫu kiểm định, huấn luyện lại từ đầu trên mọi cặp trước 29/07/2020, rồi chấm tập kiểm thử. Seed 42 thêm ablation
   của NeuMF-F (bỏ biến thể trùng NeuMF-F), top-20 và checkpoint cho demo. Ra: `outputs/v2/final/seed*/`; thư mục này còn
   kết quả của dữ liệu khác thì script dừng.
2. `scripts/24_report_v2.py` — trung bình ± độ lệch chuẩn, kiểm định (Wilcoxon + bootstrap + Holm, 10 so sánh), ablation,
   độ phủ. Ra: `outputs/v2/final/*.csv`, `ket_qua.txt`, hình, bảng `.tex` và macro số liệu trong `../Report DACNTT/`.

**Khoá kiểm thử.** `23_final_v2.py` từ chối chạy nếu:

- `audit/PREREG_v2.md` chưa commit, hoặc thiếu `--reason`;
- có file đã theo dõi bị sửa mà chưa commit (trừ `outputs/` và `audit/test_access_log.csv`), hoặc có file mã nguồn chưa
  theo dõi trong `src/`, `scripts/`, `configs/`;
- tinh chỉnh chưa đủ mô hình, hoặc mã băm mã nguồn khác lúc tinh chỉnh;
- seed đã từng mở tập kiểm thử.

Mỗi seed ghi một dòng `audit/test_access_log.csv` **trước** khi chấm. Bị ngắt giữa chừng: chạy tiếp các seed còn thiếu
bằng `--seeds ...`. Seed đang chạy dở đã mở tập kiểm thử, nên chạy lại seed đó cần `--allow-rerun` và phải ghi vào
`audit/PREREG_v2.md` mục 10 (lệch kế hoạch).

Sau đánh giá cuối, mã v1 không dùng nữa đã được xoá khỏi `src/` nên mã băm hiện tại khác `0f1ea1eec5a86c31`; các hàm mà
v2 dùng giữ nguyên. Chạy lại `23_final_v2.py` vì vậy cần `--allow-code-change` (và ghi vào mục 10).

### 3.4 Sau khi chạy

1. `python run.py check-report`: báo câu nhận xét bằng chữ trong báo cáo không còn đúng với số liệu, dòng tài liệu còn
   ghi số cũ, macro/bảng/hình còn thiếu.
2. Viết phần thảo luận Chương 4–5 theo `outputs/v2/final/significance.csv` và `summary.csv`. Số liệu trong báo cáo đọc
   qua macro nên tự cập nhật.
3. Chụp ảnh demo (mục 5), biên dịch báo cáo (`../Report DACNTT/compile.bat`), commit.

Cần tính lại bảng/hình mà không chấm lại: `python run.py v2-report`.

## 4. Kiểm thử

```bash
pytest -q              # tests/ — không cần dữ liệu thật
pytest demo/tests -q   # demo — test nạp checkpoint bỏ qua cho tới khi có outputs/v2/final/seed42/
```

## 5. Demo

```bash
python run.py demo     # http://localhost:8000
```

Dùng đúng các mô hình của đánh giá cuối (`outputs/v2/final/seed42/`). Chi tiết: `demo/README.md`.

## 6. Cấu trúc thư mục

```text
neumf_project/
├── configs/      v2.yaml
├── data/         raw/hm/ (3 file Kaggle), processed/hm/ (hai mẫu, đặc trưng) — không commit
├── src/
│   ├── data_pipeline/   đọc dữ liệu (adapters/), gộp cặp, k-core, mẫu âm; features.py (đặc trưng, gộp theo
│   │                    product_code), protocol_v2.py (giai đoạn xác thực / kiểm thử), feature_dataset.py
│   ├── models/          neumf.py (GMF, MLP, NeuMF), late_fusion.py,
│   │                    hybrid_features.py (NeuMF-F, GMF-F, MLP-F, MostPopular-Recent, Content)
│   ├── baselines/       Random, Most Popular, BPR-MF, ItemKNN, UserKNN
│   ├── training/        vòng lặp huấn luyện, dừng sớm
│   └── evaluation/      xếp hạng toàn bộ, độ đo; v2.py (chấm theo giao thức v2)
├── scripts/      xem bảng dưới
├── audit/        bằng chứng thực nghiệm đã commit (bảng dưới)
├── outputs/      data/ (manifest dữ liệu đã lọc), v2/tuning/ (checkpoint tinh chỉnh), v2/final/ (kết quả cuối)
├── demo/         web demo
├── tests/
└── run.py        lệnh tắt — python run.py -h
```

| Script | Việc |
|---|---|
| `00_sample_hm.py` | Lấy mẫu khách theo khối: `--block 0` mẫu phát triển, `--block 2` mẫu kiểm định |
| `21_build_features.py` | Danh mục sản phẩm (thuộc tính + vector văn bản), doanh số theo ngày của toàn H&M |
| `02_prepare_data.py` | Gộp màu theo `product_code`, k-core trước mốc kiểm thử → `outputs/data/*.csv.gz` + MD5 |
| `22_tune_v2.py` | Tinh chỉnh trên tập xác thực của mẫu phát triển → `audit/v2/` |
| `23_final_v2.py` | Đánh giá cuối trên tập kiểm thử của mẫu kiểm định (có khoá kiểm thử); `--dry-run`: chạy thử |
| `24_report_v2.py` | Kiểm định, bảng, hình, macro LaTeX, `ket_qua.txt`; `--tuning-only`: chỉ bảng tinh chỉnh |
| `v2_common.py` | Nạp dữ liệu, dựng, huấn luyện, chấm mô hình — dùng chung cho 22, 23 và demo |
| `19_check_report.py` | Đối chiếu câu chữ báo cáo và tài liệu với số liệu |

`audit/` gồm: `PREREG_v2.md` (kế hoạch, bản cuối), `v2/tuning_log.csv`, `v2/best_configs.json`, `v2/data_dev.json`
(tinh chỉnh), `test_access_log.csv` (mọi lần chấm tập kiểm thử, kể cả của giai đoạn phát triển). Lịch sử:
`PREREG.md` (giao thức v1 — giai đoạn phát triển, báo cáo mục 4.5) và `PREREG_v2_cu.md` (bản v2 đầu, đánh giá trên
khối 1). Mã nguồn và kết quả của hai giai đoạn này nằm trong lịch sử git: commit `9799f1a` (tag cục bộ `truoc-don-dep`).
Code đọc/ghi trực tiếp các file trong `audit/` — không sửa tay.
