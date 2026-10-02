# DACNTT — NeuMF Recommendation Project

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu (NeuMF).

Dữ liệu: **hm500k** — mẫu ~500k giao dịch H&M Personalized Fashion Recommendations, lấy theo khách hàng, trải đủ
2018-09-20 → 2020-09-22 (sau k-core 10: 7.519 users × 10.345 items). Mô hình: GMF, MLP, NeuMF-Scratch,
NeuMF-Pretrained; baseline Random, MostPopular, BPR-MF; phần mở rộng (PREREG mục 9) late fusion GMF + MLP,
BPR-MF + MLP, ItemKNN, UserKNN. Đánh giá Full Ranking, protocol chính chia theo một mốc thời gian chung.

**Chạy lại toàn bộ số liệu báo cáo:** `python run.py preflight` rồi `python run.py final --reason "..."` (mục 5.2).

- **Lý thuyết, phạm vi, phương pháp, kết quả:** `pham_vi_du_an.md` — đọc trước khi sửa code.
- **Hướng dẫn chạy:** file này (máy local mục 2–6, Google Colab mục 7).
- **Demo web:** `demo/README.md`.

---

## 1. Cây thư mục

```text
neumf_project/
├── configs/
│   ├── hm500k_global.yaml   # Protocol CHÍNH: một mốc thời gian chung (dùng cho tuning + đánh giá cuối)
│   └── hm500k.yaml          # Protocol phụ: leave-one-out theo thời gian từng user (mặc định của run.py)
├── data/
│   ├── raw/hm/              # transactions_train.csv (+ articles.csv, customers.csv chỉ cho demo) — tải từ Kaggle
│   └── processed/hm/        # hm500k_transactions.csv (sinh bởi scripts/00_sample_hm.py)
├── src/
│   ├── config.py
│   ├── data_pipeline/       # adapter H&M, preprocessing, k-core, splitting, negative sampling, dataset
│   ├── models/              # GMF, MLP, NeuMF (neumf.py — early fusion), late fusion (late_fusion.py), EarlyFusionModel (trùng MLP, không dùng)
│   ├── baselines/           # Random, MostPopular, BPR-MF (classical.py); ItemKNN, UserKNN thưa top-K (neighborhood.py)
│   ├── training/            # trainer.py — vòng lặp huấn luyện, early stopping
│   ├── evaluation/          # full_ranking, sampled_ranking, metrics, long_tail, cold_start, beyond_accuracy, statistics
│   └── utils/
├── scripts/
│   ├── 00_sample_hm.py          # Tạo hm500k từ transactions_train.csv gốc (chạy 1 lần)
│   ├── 01_data_audit.py         # Audit k-core, mật độ, kiểm tra split không giao nhau
│   ├── 02_preprocess.py         # Sinh splits thủ công
│   ├── 03_run_experiment.py     # Train toàn bộ mô hình + baselines (mặc định chấm trên VALIDATION)
│   ├── 04_multi_seed.py         # Lặp lại 03 trên nhiều seed
│   ├── 05_evaluate.py           # Bảng + biểu đồ cho một run
│   ├── 06_aggregate_seeds.py    # mean ± std + Wilcoxon qua các seed
│   ├── 10_tune.py               # Tuning chỉ trên val → audit/tuning_log.csv, best_configs.json
│   ├── 11_final.py              # Đánh giá cuối trên TEST, 3 seed (có khoá test)
│   ├── 12_significance.py       # Wilcoxon + bootstrap CI + Holm → outputs/final/summary.csv, significance.csv
│   ├── 13_plot_final.py         # Biểu đồ kết quả cuối → outputs/figures/final_*.png
│   ├── 14_secondary.py          # Phân tích phụ trên test: head/tail, cold/warm, beyond-accuracy, Sampled-99, độ trễ
│   ├── 15_export_report.py      # Xuất bảng .tex + macro số liệu + hình sang Report DACNTT/
│   ├── 16_extra_k.py            # Chỉ số @20 tính lại từ hạng đã lưu (mô tả; không chấm lại mô hình)
│   ├── 17_extension.py          # Mở rộng PREREG mục 9 trên TEST: late fusion GMF+MLP, BPR-MF+MLP, ItemKNN, UserKNN
│   ├── 18_preflight.py          # Kiểm tra sẵn sàng trước khi chạy lại (tree sạch, PREREG, dữ liệu, tái lập tuning)
│   ├── 19_check_report.py       # Đối chiếu sau khi chạy: tái lập, câu chữ báo cáo, số chép tay trong tài liệu
│   └── run_all.py               # 03 rồi 05
├── audit/                   # Bằng chứng thực nghiệm: PREREG.md, tuning_log.csv, best_configs.json, test_access_log.csv,
│                            #   final_2909_*.csv (bản lưu kết quả lần chấm 29/09 để đối chiếu tái lập)
├── notebooks/
│   └── colab_final.ipynb    # Notebook Colab chạy lại kết quả cuối (mục 7)
├── demo/                    # Web demo (xem demo/README.md)
├── outputs/
│   ├── final/               # Kết quả cuối (summary.csv, significance.csv, seed*/ kèm checkpoint, extension/)
│   └── {checkpoints,experiments,tables,figures,data_audit,tuning}/
├── tests/
├── run.py                   # CLI tổng hợp (python run.py -h)
└── pham_vi_du_an.md
```

`audit/` là bằng chứng đã commit — code đọc/ghi trực tiếp các file này, không sửa tay (trừ khi chép log từ Colab về, mục 7.4).

---

## 2. Cài đặt trên máy local

Yêu cầu: Python 3.11+ (đã chạy với 3.13), ~16 GB RAM. GPU NVIDIA không bắt buộc nhưng nhanh hơn nhiều
(kết quả gốc chạy trên RTX 3050 Laptop 4 GB).

```bash
cd neumf_project
python -m venv .venv
.venv\Scripts\activate            # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
```

Có GPU thì cài PyTorch bản CUDA **trước** rồi mới cài `requirements.txt`, ví dụ:
`pip install torch --index-url https://download.pytorch.org/whl/cu121`. Kiểm tra:
`python -c "import torch; print(torch.cuda.is_available())"`. Config để `device: auto` nên tự dùng GPU nếu có.

Mọi lệnh bên dưới chạy từ thư mục `neumf_project/`.

## 3. Dữ liệu

Tải 3 file của cuộc thi Kaggle
[H&M Personalized Fashion Recommendations](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations/data)
(phải bấm *I Understand and Accept* ở trang Rules) và đặt vào `data/raw/hm/`:

| File | Dùng cho |
|---|---|
| `transactions_train.csv` (3,5 GB) | Bắt buộc — mô hình chỉ học từ file này |
| `articles.csv` | Chỉ demo (tên/loại sản phẩm) |
| `customers.csv` | Chỉ demo (lọc tuổi cho khách mới) |

Hoặc dùng Kaggle CLI (cần `~/.kaggle/kaggle.json`):

```bash
pip install kaggle
kaggle competitions download -c h-and-m-personalized-fashion-recommendations -f transactions_train.csv -p data/raw/hm
```

Không dùng bản `.xlsx` (Excel cắt ở 1.048.576 dòng). Sau đó tạo mẫu hm500k:

```bash
python run.py sample-hm      # ~1 phút, RAM ~0,5 GB → data/processed/hm/hm500k_transactions.csv
```

Mẫu lấy theo hash `customer_id` nên chạy lại luôn ra đúng cùng một file.

## 4. Kiểm tra

```bash
pytest -q                 # tests/ — cần có hm500k cho các test chạy trên dữ liệu thật
pytest demo/tests -q      # cần đã có run hm500k và file offline của demo
```

## 5. Pipeline chính thức (tuning → test → kiểm định → báo cáo)

Đây là đường tạo ra số liệu trong báo cáo (xem `pham_vi_du_an.md` mục 7–9, `audit/PREREG.md`).

### 5.1 Tuning (chỉ validation) — đã chạy xong, thường không cần chạy lại

```bash
python scripts/10_tune.py --model all          # 5 mô hình chính: bpr | gmf | mlp | neumf_scratch | neumf_pretrained
python scripts/10_tune.py --model extension    # 4 mô hình mở rộng: itemknn | userknn | late_gmf_mlp | late_bpr_mlp
```

Mặc định **ghi nối** vào `audit/tuning_log.csv` và ghi đè `best_configs.json` — là bằng chứng đã commit.
Muốn thử lại mà không đụng bằng chứng: thêm `--log-dir outputs/tuning_rerun`. Thời gian gốc: 1,9 giờ GPU (chính) +
khoảng 3 phút (mở rộng). Late fusion cần checkpoint train-only của GMF, MLP, BPR-MF trong `outputs/tuning/` (đã commit);
nếu mất, script huấn luyện lại đúng cấu hình đó và ghi số val của bản dựng lại vào `audit/rebuilt_checkpoints.json`.

### 5.2 Chạy lại toàn bộ số liệu báo cáo — một lệnh

```bash
git status                                     # mọi thay đổi phải được commit trước (khoá test)
python run.py preflight                        # kiểm tra sẵn sàng, không chấm test (3–4 phút)
python run.py final --reason "Chạy lại toàn bộ trên commit cuối (PREREG mục 8, 02/10/2026)"
```

`run.py final` chạy tuần tự (dừng ngay nếu một bước lỗi):

| Bước | Script | Việc | Chấm test? | Thời gian (RTX 3050) |
|---|---|---|---|---|
| 18 | `18_preflight.py` | tree sạch, PREREG đã commit và có mục 9, đủ cấu hình, dữ liệu khớp gốc, tuning mở rộng chạy lại ra đúng cùng số | không | 3–4 phút |
| 11 | `11_final.py` | 3 seed: chọn epoch trên val → train lại trên train ∪ val → chấm test | có (3 dòng log) | ~1,5 giờ |
| 12 | `12_significance.py` | mean ± std, Wilcoxon + bootstrap + Holm (họ 8 so sánh) | không | < 1 phút |
| 17 | `17_extension.py` | late fusion (dùng đúng GMF/MLP/BPR-MF của bước 11), ItemKNN, UserKNN; họ 7 so sánh riêng | có (1 dòng log) | 5–10 phút |
| 16 | `16_extra_k.py` | chỉ số @20 từ hạng đã lưu (cả mô hình mở rộng) | không | < 1 phút |
| 13 | `13_plot_final.py` | biểu đồ `outputs/figures/final_*.png` | không | < 1 phút |
| 14 | `14_secondary.py` | head/tail, cold/warm, beyond-accuracy, Sampled-99, độ trễ CPU | có (1 dòng log) | 10–15 phút |
| 15 | `15_export_report.py` | bảng `.tex`, macro số liệu (kể cả câu kết luận tự sinh), hình → `../Report DACNTT/` | không | < 1 phút |
| 19 | `19_check_report.py` | so số mới với bản đã commit, kiểm tra 33 khẳng định bằng chữ trong báo cáo, liệt kê dòng tài liệu còn ghi số cũ, macro/bảng còn thiếu | không | < 1 phút |

- **Máy chạy:** kết quả 29/09 chạy trên máy có **GPU RTX 3050 Laptop** (`outputs/final/final.log`). Huấn luyện ở chế độ
  GPU tất định (`src/utils/seed.py`, từ 28/09), nên chạy lại **trên chính máy đó** với cùng phiên bản thư viện kỳ vọng
  ra đúng cùng số cho 7 mô hình chính — `19_check_report.py` in "trùng khớp" hoặc độ lệch. Máy khác (Colab T4) thì
  Random, MostPopular, ItemKNN, UserKNN vẫn trùng, BPR-MF gần như trùng, GMF/MLP/NeuMF có thể lệch nhẹ. Máy không có GPU
  NVIDIA (PyTorch bản CPU) chạy được nhưng chậm hơn nhiều.
- **Khoá test:** 11 đòi tree sạch; 14 và 17 chỉ cho phép `outputs/` và `audit/test_access_log.csv` thay đổi (do bước
  trước vừa ghi). Chạy một lệnh cho cả chuỗi (sau bước 11 tree đã đổi nên không chạy lại 11 riêng được nếu chưa commit).
- **Chỉ chạy phần mở rộng** trên checkpoint đã có (không chạy lại 11): `python run.py extension --reason "..."`
  (18 → 17 → 16 → 15 → 19).

### 5.3 Sau khi chạy

1. Đọc kết quả `19_check_report.py` (chạy lại bất cứ lúc nào: `python run.py check-report`):
   - mục 2 `[SAI]`: câu nhận xét bằng chữ trong báo cáo không còn đúng với số mới → sửa câu ở `tệp:dòng` được in ra;
   - mục 3: dòng trong `van_dap.md`, `pham_vi_du_an.md`, README, notebook còn ghi số cũ → sửa;
   - mục 4: macro/bảng còn thiếu (bình thường phải hết sau bước 15).
2. Biên dịch báo cáo: `../Report DACNTT/compile.bat`. Số liệu trong Chương 4, 5 và tóm tắt đọc qua macro
   (`\Res{Pre}{NDCG10}`, `\Esig{all}{summary}`...) nên tự cập nhật; câu kết luận của phần mở rộng sinh từ
   `outputs/final/extension/significance.csv`.
3. (Tuỳ chọn) chụp lại Hình 3.3–3.4 nếu số trên demo đổi: `python run.py demo`, mở
   `http://127.0.0.1:8000/?user=<customer_id>&compare=1&a=NeuMF-Pretrained&b=BPR-MF#admin`.
4. Commit kết quả (`outputs/final/`, `audit/test_access_log.csv`, `Report DACNTT/`) và tài liệu đã sửa.

### 5.4 Từng bước riêng lẻ (nếu cần)

```bash
python scripts/11_final.py --reason "..."       # mặc định seed 42 2024 2025
python scripts/12_significance.py               # → outputs/final/summary.csv, significance.csv
python scripts/17_extension.py --reason "..."   # → outputs/final/extension/
python scripts/16_extra_k.py                    # → outputs/final/extra_k20.csv
python scripts/13_plot_final.py                 # → outputs/figures/final_*.png
python scripts/14_secondary.py --reason "..."   # → outputs/final/{stratified,beyond_accuracy,sampled99,latency}.csv
python scripts/15_export_report.py              # → ../Report DACNTT/content/tables/, media/figures/final/
python scripts/19_check_report.py               # đối chiếu
```

Late fusion = w·minmax(điểm A) + (1−w)·minmax(điểm B), hai mô hình huấn luyện riêng (`src/models/late_fusion.py`),
min-max trên tập ứng viên của từng user. Bảng/hình chưa có số liệu sẽ hiện khung "Chưa có số liệu", macro chưa có
giá trị hiện "[chưa có]" thay vì lỗi biên dịch.

## 6. Chạy nhanh bằng `run.py` (khám phá, protocol phụ, demo)

`run.py all/train/multi-seed` chạy `03_run_experiment.py` với cấu hình mặc định (không phải cấu hình đã tune),
mọi bảng tính trên **validation** — dùng để khám phá, **không** ra số liệu báo cáo. `--final` chỉ còn cho protocol phụ
leave-one-out; protocol chính (`hm500k_global.yaml`) chấm test bằng `python run.py final --reason "..."` (mục 5).

```bash
python run.py -h
python run.py all                                          # audit → train → evaluate, run tag hm500k_seed42 (leave-one-out)
python run.py all --config configs/hm500k_global.yaml      # protocol chính → hm500k_global_seed42
python run.py evaluate --run-tag hm500k_seed42             # vẽ lại bảng + biểu đồ
python run.py multi-seed                                   # seed 42 2024 2025 2026 3407 7
python run.py aggregate                                    # → outputs/tables/hm500k_multiseed/
python run.py demo                                         # http://localhost:8000 (chi tiết: demo/README.md)
```

RAM đỉnh ~4,1 GB. Kết quả: `outputs/tables/<run_tag>/` (xem `evaluation_report.txt` trước) và
`outputs/figures/<run_tag>/`.

Quy ước tên:

| Thứ | Tên |
|---|---|
| Run | `<tên config>_seed<seed>`, vd. `hm500k_seed42` — chạy lại cùng config + seed sẽ ghi đè; muốn giữ thì truyền `--run-tag` khác |
| Bảng multi-seed | `outputs/tables/<tên config>_multiseed/` |

Demo bằng Docker (chỉ inference, dữ liệu và `outputs/` mount qua volume; chưa kiểm tra đầy đủ):
`docker compose up --build`.

---

## 7. Chạy trên Google Colab

Notebook chính: **`notebooks/colab_final.ipynb`** — chạy đúng chuỗi của `python run.py final` (mục 5.2: dữ liệu →
khám phá từng bước → kiểm tra sẵn sàng → 11_final 3 seed → kiểm định → mở rộng PREREG mục 9 → @20 → biểu đồ → phân
tích phụ → xuất bảng/hình cho báo cáo → đối chiếu câu chữ), dùng `best_configs.json` đã tune, **không tune lại**.

Notebook **clone code từ GitHub** (`sulinh3625/DU-AN-CNTT`, nhánh `main`), nên mọi thay đổi ở máy local phải
**commit + push** trước khi chạy.

### 7.1 Mở notebook từ máy local lên Colab

Chọn một trong hai cách:

- **Upload từ máy:** vào https://colab.research.google.com → `File → Upload notebook` → chọn
  `neumf_project/notebooks/colab_final.ipynb` trong repo local.
- **Mở từ GitHub:** `File → Open notebook → GitHub` → dán `https://github.com/sulinh3625/DU-AN-CNTT`
  → chọn `neumf_project/notebooks/colab_final.ipynb` (repo private thì tick *Include private repos* và đăng nhập GitHub).

### 7.2 Chuẩn bị (một lần)

1. `Runtime → Change runtime type → T4 GPU`.
2. Secrets (biểu tượng 🔑 bên trái), bật *Notebook access* cho từng secret:
   - `GITHUB_TOKEN` — chỉ cần khi repo private (GitHub → Settings → Developer settings → Personal access token,
     quyền đọc repo).
   - `KAGGLE_USERNAME`, `KAGGLE_KEY` — để tải dữ liệu lần đầu (Kaggle → Settings → API → *Create New Token*).
     Thay thế: đặt `kaggle.json` vào `My Drive/neumf_colab/`.
3. Tài khoản Kaggle đã chấp nhận Rules của cuộc thi H&M.
4. (Tuỳ chọn, bỏ qua bước tải Kaggle) upload `data/processed/hm/hm500k_transactions.csv` từ máy local lên
   `My Drive/neumf_colab/hm500k_transactions.csv`.

### 7.3 Chạy

`Runtime → Run all`, hoặc chạy lần lượt từng ô:

| Ô | Việc | Ghi chú |
|---|---|---|
| 1 | Kiểm tra GPU | Báo "KHÔNG có GPU" thì đổi runtime |
| 2 | Mount Drive, cấu hình | Sửa `REASON` (ghi vào nhật ký test), `SEEDS`, `DRIVE_DIR` nếu cần |
| 3 | Clone repo + `pip install` | Nếu pip đổi phiên bản numpy/pandas: `Runtime → Restart session`, chạy lại ô 2 và `%cd /content/DU-AN-CNTT/neumf_project` |
| 4 | Dữ liệu hm500k | Dùng bản trên Drive nếu có; không thì tải Kaggle + lấy mẫu (10–20 phút) rồi lưu lên Drive |
| 5 | Khám phá pipeline từng bước | Kiểm tra khớp lần chạy gốc (201.801 cặp train, 10.145 item trong train) — lệch thì **dừng** |
| 6 | pytest + `18_preflight.py` | Báo **CHƯA SẴN SÀNG** (tree bẩn, PREREG thiếu mục 9, dữ liệu lệch, tuning mở rộng không tái lập) thì dừng |
| 7 | `11_final.py` 3 seed | 65 phút – 2 giờ; log ghi song song lên Drive. Giữ tab mở để Colab không ngắt |
| 8 | Kiểm định, `17_extension.py`, @20, biểu đồ | Báo lỗi nếu seed nào chưa chạy xong; phần mở rộng 5–10 phút, ghi 1 dòng nhật ký test |
| 9 | `14_secondary.py` | 10–15 phút; sửa `REASON_SECONDARY` ở ô 2 nếu muốn. Độ trễ đo trên CPU của Colab |
| 10 | `15_export_report.py`, `19_check_report.py` | Sinh bảng/macro/hình cho báo cáo trong bản clone; log đối chiếu lưu `check_report.log` lên Drive |
| 11 | Lưu Drive + tải zip về máy | `My Drive/neumf_colab/results_<thời điểm>/` (kèm checkpoint của `outputs/final/seed*/`) |
| 12 | Xem nhanh kết quả | Đối chiếu với số gốc ở cuối notebook |

### 7.4 Sau khi chạy

Giải nén zip và chép về repo (bảng này cũng có ở cuối mục 11 của notebook):

| Trong zip | Chép vào repo |
|---|---|
| `final/` | `neumf_project/outputs/final/` |
| `figures/final_*.png` | `neumf_project/outputs/figures/` |
| `test_access_log.csv` | `neumf_project/audit/test_access_log.csv` (ghi đè — đã gồm dòng cũ + dòng mới) |
| `report/` | `Report DACNTT/` (ghi đè `content/tables/`, `media/figures/final/`) |

Rồi làm như mục 5.3: `python run.py check-report` chỉ ra câu nhận xét bằng chữ nào trong báo cáo (Chương 1, 4, 5, tóm
tắt) không còn đúng với số mới và dòng tài liệu nào còn ghi số cũ; sửa, biên dịch lại báo cáo
(`Report DACNTT/compile.bat`) và commit. Câu kết luận của phần mở rộng và câu "Lần chấm" ở mục 4.1 tự sinh từ số liệu.

- Random và MostPopular phải ra giống hệt số gốc; BPR-MF gần như giống hệt; GMF/MLP/NeuMF trên GPU T4 có thể lệch
  nhẹ (cuDNN không tất định). Kết luận thống kê mới là thứ cần giữ.
- Colab ngắt giữa chừng: chạy lại từ ô 2 (mỗi lần chạy lại vẫn được ghi vào nhật ký test).

Các phương án dữ liệu cũ (toàn bộ H&M + cache Parquet, lát cắt 100k dòng, mẫu 300k) đã gỡ khỏi repo; lý do và số
liệu đo được ghi ở `pham_vi_du_an.md` mục 4.4.
