# neumf_project — mã nguồn của đề tài

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu.

Kết quả chính theo **giao thức v2** (kế hoạch đăng ký trước: `audit/PREREG_v2.md`):

- **Mô hình đề tài NeuMF-F:** hai nhánh GMF-F và MLP-F hợp nhất sớm như NeuMF. Vector của khách và sản phẩm =
  embedding ID + phép chiếu của đặc trưng (thuộc tính và mô tả văn bản của sản phẩm, thông tin khách, doanh số và thời
  gian — tính theo thời điểm, không dùng thông tin tương lai).
- **Dữ liệu:** hai mẫu khách hàng không giao nhau của H&M — **A** chỉ để tinh chỉnh (trên tập xác thực), **B** chỉ để
  đánh giá cuối (mở tập kiểm thử đúng một lần). Tập ứng viên gồm cả sản phẩm mới.
- **So sánh:** 14 mô hình, 5 seed, họ 10 so sánh có hiệu chỉnh Holm.

Phương pháp chi tiết: `pham_vi_du_an.md`. Giao thức v1 (lịch sử phát triển): mục 7.

Mọi lệnh dưới đây chạy từ thư mục `neumf_project/`.

| Mục | Nội dung |
|---|---|
| 1 | Cài đặt |
| 2 | Dữ liệu |
| 3 | Chạy giao thức v2 |
| 4 | Kiểm thử |
| 5 | Demo |
| 6 | Cấu trúc thư mục |
| 7 | Giao thức v1 — lịch sử phát triển |

---

## 1. Cài đặt

Python 3.11 trở lên (đã chạy với 3.13), RAM 16 GB. GPU NVIDIA không bắt buộc nhưng nhanh hơn nhiều.

```bash
python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

Có GPU: cài PyTorch bản CUDA **trước** `requirements.txt`, ví dụ
`pip install torch --index-url https://download.pytorch.org/whl/cu121`, rồi kiểm tra
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

(làm tương tự với `articles.csv`, `customers.csv`). Sau đó tạo hai mẫu và đặc trưng — chạy một lần:

```bash
python run.py sample-hm     # mẫu A → data/processed/hm/hm500k_transactions.csv
python run.py v2-data       # mẫu B → hm500k_b_transactions.csv; đặc trưng → catalog_v2.npz, daily_sales_v2.npz
```

Mẫu lấy theo băm `customer_id` với khoá cố định nên chạy lại luôn ra đúng cùng file (mã MD5 ghi trong
`audit/PREREG_v2.md` mục 1). Thư mục `data/` không được commit.

## 3. Chạy giao thức v2

| Bước | Lệnh | Việc | Thời gian (CPU 4 nhân) |
|---|---|---|---|
| 1 | `python run.py v2-tune --resume` | Tinh chỉnh trên tập xác thực của mẫu A | khoảng 7 giờ |
| 2 | `python run.py v2-dry-run` | Tuỳ chọn: chạy thử trọn đường ống, không chấm test | khoảng 1 giờ |
| 3 | `python run.py v2-final --reason "..."` | Đánh giá cuối trên tập kiểm thử của mẫu B + xuất bảng, hình cho báo cáo | 12–17 giờ (GPU: 2–5 giờ) |
| 4 | `python run.py check-report` | Đối chiếu câu chữ báo cáo với số liệu | dưới 1 phút |

Chạy qua đêm một lệnh: `python run.py all` = `prepare` → bước 1 (`--resume`) → bước 2; thêm `--final --reason "..."`
để chạy luôn bước 3 ở cuối (khoá kiểm thử của bước 3 vẫn áp dụng). Bị ngắt thì chạy lại đúng lệnh đó: tinh chỉnh đi
tiếp từ cấu hình còn thiếu.

### 3.1 Tinh chỉnh — chỉ trên tập xác thực của mẫu A

- Mỗi mô hình có học thử 6 cấu hình (seed 42); mô hình một tham số thử đủ lưới. Lưới: `audit/PREREG_v2.md` mục 4.
- Mỗi cấu hình ghi một dòng `audit/v2/tuning_log.csv` kèm commit và **mã băm mã nguồn** (`code_hash`, tính trên
  `src/`, `scripts/v2_common.py`, `scripts/22_tune_v2.py`, `configs/v2.yaml`). Cấu hình tốt nhất ghi vào
  `audit/v2/best_configs.json`.
- Bị ngắt thì chạy lại đúng lệnh trên: cấu hình đã có được bỏ qua.
- **Không sửa các file trong mã băm cho tới khi đánh giá cuối xong** — đánh giá cuối từ chối chạy nếu mã băm khác lúc
  tinh chỉnh.
- Xong thì đưa bảng tinh chỉnh vào báo cáo: `python scripts/24_report_v2.py --tuning-only`.

### 3.2 Chạy thử (tuỳ chọn)

`python run.py v2-dry-run` chạy trọn đường ống đánh giá cuối nhưng trên tập xác thực của mẫu A, mỗi mạng nơ-ron 1 epoch
— không mở tập kiểm thử nào. Kết quả ở `outputs/v2/dry_run/` (không commit).

### 3.3 Đánh giá cuối trên mẫu B — mở tập kiểm thử đúng một lần

```bash
git status       # mọi thay đổi (kể cả audit/PREREG_v2.md, audit/v2/) phải đã commit
python run.py v2-final --reason "Đánh giá cuối v2 theo PREREG_v2"
```

Lệnh chạy hai script:

1. `scripts/23_final_v2.py` — 5 seed (42, 2024, 2025, 2026, 3407). Mỗi seed: mạng nơ-ron chọn số epoch trên tập xác thực
   của B, huấn luyện lại từ đầu trên mọi cặp trước 29/07/2020, rồi chấm tập kiểm thử (tập ứng viên đầy đủ, và thêm bản
   "chỉ sản phẩm cũ"). Seed 42 thêm 5 ablation của NeuMF-F, top-20 và checkpoint cho demo.
   Ra: `outputs/v2/final/seed*/`.
2. `scripts/24_report_v2.py` — trung bình ± độ lệch chuẩn, kiểm định (Wilcoxon + bootstrap + Holm, 10 so sánh), nhóm
   sản phẩm cũ/mới, ablation, độ phủ. Ra: `outputs/v2/final/*.csv`, hình, bảng `.tex` và macro số liệu trong
   `../Report DACNTT/`.

**Khoá kiểm thử.** `23_final_v2.py` từ chối chạy nếu:

- `audit/PREREG_v2.md` chưa commit, hoặc thiếu `--reason`;
- có file đã theo dõi bị sửa mà chưa commit (trừ `outputs/` và `audit/test_access_log.csv`), hoặc có file mã nguồn chưa
  theo dõi trong `src/`, `scripts/`, `configs/`;
- tinh chỉnh chưa đủ mô hình, hoặc mã băm mã nguồn khác lúc tinh chỉnh;
- seed đã từng mở tập kiểm thử.

Mỗi seed ghi một dòng `audit/test_access_log.csv` **trước** khi chấm. Bị ngắt giữa chừng: chạy tiếp các seed còn thiếu
bằng `--seeds ...`. Seed đang chạy dở đã mở tập kiểm thử, nên chạy lại seed đó cần `--allow-rerun` và phải ghi vào
`audit/PREREG_v2.md` mục 10 (lệch kế hoạch).

**Chạy trên máy khác.** Mạng nơ-ron trên GPU có thể lệch nhẹ ở chữ số cuối so với CPU; máy đã chạy được ghi tự động
trong `results.json`.

- *Máy có GPU* (vd. RTX 3050 của thành viên khác): pull code đã commit; chép `data/raw/hm/` và `data/processed/hm/`
  (không có trong git); chạy lệnh trên; rồi commit `outputs/v2/`, `audit/test_access_log.csv` và `Report DACNTT/`.
- *Google Colab (GPU T4):* `notebooks/colab_v2.ipynb`. Notebook clone code từ GitHub (`sulinh3625/DU-AN-CNTT`, nhánh
  `main`) nên phải **commit + push trước**. Mở trên Colab bằng `File → Upload notebook` (chọn file trong repo) hoặc
  `File → Open notebook → GitHub`; chọn `Runtime → Change runtime type → T4 GPU`; thêm secret `GITHUB_TOKEN` nếu repo
  private và `KAGGLE_USERNAME`, `KAGGLE_KEY` để tải dữ liệu lần đầu. Notebook tự chuẩn bị dữ liệu (lưu lên Drive),
  kiểm tra khoá kiểm thử trước khi chạy, ghi bản sao nhật ký lên Drive và đóng gói kết quả; bảng chép kết quả về repo
  nằm ở cuối notebook.

### 3.4 Sau khi chạy

1. `python run.py check-report`: báo câu nhận xét bằng chữ trong báo cáo không còn đúng với số liệu, dòng tài liệu còn
   ghi số cũ, macro/bảng/hình còn thiếu.
2. Viết phần thảo luận Chương 4–5 theo `outputs/v2/final/significance.csv` và `summary.csv`. Số liệu trong báo cáo đọc
   qua macro nên tự cập nhật.
3. Chụp ảnh demo (mục 5), biên dịch báo cáo (`../Report DACNTT/compile.bat`), commit.

Cần tính lại bảng/hình mà không chấm lại: `python run.py v2-report`.

## 4. Kiểm thử

```bash
pytest -q              # tests/ — test cần dữ liệu thật tự bỏ qua nếu chưa có
pytest demo/tests -q   # demo — test chế độ v2 bỏ qua cho tới khi có outputs/v2/final/
```

## 5. Demo

```bash
python run.py demo     # http://localhost:8000
```

Mặc định dùng đúng các mô hình của đánh giá cuối v2 khi đã có `outputs/v2/final/seed42/`. Chi tiết: `demo/README.md`.

## 6. Cấu trúc thư mục

```text
neumf_project/
├── configs/      v2.yaml (giao thức v2); hm500k_global.yaml, hm500k.yaml (giao thức v1)
├── data/         raw/hm/ (3 file Kaggle), processed/hm/ (mẫu A, mẫu B, đặc trưng) — không commit
├── src/
│   ├── data_pipeline/   đọc dữ liệu, gộp cặp, k-core, chia dữ liệu, mẫu âm;
│   │                    v2: features.py (đặc trưng), protocol_v2.py (giai đoạn, sản phẩm mới), feature_dataset.py
│   ├── models/          neumf.py (GMF, MLP, NeuMF), late_fusion.py;
│   │                    v2: hybrid_features.py (NeuMF-F, GMF-F, MLP-F, MostPopular-Recent, Content)
│   ├── baselines/       Random, Most Popular, BPR-MF, ItemKNN, UserKNN
│   ├── training/        vòng lặp huấn luyện, dừng sớm
│   └── evaluation/      xếp hạng toàn bộ, độ đo, kiểm định; v2.py (chỉ số theo nhóm sản phẩm cũ/mới)
├── scripts/      xem bảng dưới
├── audit/        bằng chứng thực nghiệm đã commit (bảng dưới)
├── outputs/      v2/ (kết quả v2: tuning/, final/), final/ (kết quả v1), các thư mục khác của v1
├── notebooks/    colab_v2.ipynb (đánh giá cuối v2), colab_final.ipynb (v1)
├── demo/         web demo
├── tests/
└── run.py        lệnh tắt — python run.py -h
```

Script của giao thức v2:

| Script | Việc |
|---|---|
| `00_sample_hm.py` | Lấy mẫu A; `--holdout`: mẫu B (khách khác hẳn A) |
| `21_build_features.py` | Danh mục sản phẩm (thuộc tính + vector văn bản), doanh số theo ngày của toàn H&M |
| `22_tune_v2.py` | Tinh chỉnh trên tập xác thực của A → `audit/v2/` |
| `23_final_v2.py` | Đánh giá cuối trên tập kiểm thử của B (có khoá kiểm thử); `--dry-run`: chạy thử trên tập xác thực của A |
| `24_report_v2.py` | Kiểm định, bảng, hình, macro LaTeX → `../Report DACNTT/`; `--tuning-only`: chỉ bảng tinh chỉnh |
| `v2_common.py` | Nạp dữ liệu, dựng, huấn luyện, chấm mô hình — dùng chung cho 22, 23 và demo |
| `19_check_report.py` | Đối chiếu câu chữ báo cáo và tài liệu với số liệu |

Các script `01`–`18`, `20` thuộc giao thức v1 (mục 7).

`audit/` gồm: `PREREG_v2.md` (kế hoạch v2), `v2/tuning_log.csv`, `v2/best_configs.json`, `v2/data_dev.json` (tinh chỉnh
v2), `test_access_log.csv` (mọi lần chấm tập kiểm thử của cả hai giao thức); v1: `PREREG.md`, `tuning_log.csv`,
`best_configs.json`. Code đọc/ghi trực tiếp các file này — không sửa tay, trừ khi chép nhật ký từ Colab về.

## 7. Giao thức v1 — lịch sử phát triển

Giai đoạn phát triển dùng mẫu A với các mô hình chỉ dùng ID (GMF, MLP, NeuMF-Scratch, NeuMF-Pretrained, BPR-MF,
Most Popular, Random; mở rộng: late fusion, ItemKNN, UserKNN), một mốc thời gian chung và tập ứng viên **không** có sản
phẩm mới. Kế hoạch: `audit/PREREG.md`; kết quả: `outputs/final/`; báo cáo mục 4.5. Lý do thay bằng v2:
`audit/PREREG_v2.md` mục 0.

Không cần chạy lại v1; `run.py` không còn lệnh v1. Chuỗi tái lập giữ lại để đối chiếu, chạy tay đúng thứ tự — **các
bước có `--reason` chấm tập kiểm thử của mẫu A và ghi vào `audit/test_access_log.csv`**:

```bash
python scripts/18_preflight.py                  # kiểm tra sẵn sàng (không chấm test)
python scripts/20_ablation.py --resume          # ablation trên validation (không chấm test)
python scripts/11_final.py --reason "..."
python scripts/12_significance.py
python scripts/17_extension.py --reason "... — mở rộng PREREG mục 9"
python scripts/16_extra_k.py
python scripts/13_plot_final.py
python scripts/14_secondary.py --reason "... — phân tích phụ"
python scripts/15_export_report.py
python scripts/19_check_report.py
```

Bản Colab của chuỗi này: `notebooks/colab_final.ipynb`. Các script khám phá (`03_run_experiment.py`, `04_multi_seed.py`,
`05_evaluate.py`, `06_aggregate_seeds.py`) chạy cấu hình mặc định và chỉ cho bảng trên tập xác thực, không ra số liệu
báo cáo.
