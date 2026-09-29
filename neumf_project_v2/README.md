# DACNTT — NeuMF Recommendation Project V2

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu (NeuMF).

Dữ liệu: **hm500k** — mẫu ~500k giao dịch H&M Personalized Fashion Recommendations, lấy theo khách hàng, trải đủ
2018-09-20 → 2020-09-22 (sau k-core 10: 7.519 users × 10.345 items). Mô hình: GMF, MLP, NeuMF-Scratch,
NeuMF-Pretrained; baseline Random, MostPopular, BPR-MF. Đánh giá Full Ranking, protocol chính chia theo một mốc
thời gian chung.

- **Lý thuyết, phạm vi, phương pháp, kết quả:** `pham_vi_du_an.md` — đọc trước khi sửa code.
- **Hướng dẫn chạy:** file này (máy local mục 2–6, Google Colab mục 7).
- **Demo web:** `demo/README.md`.

---

## 1. Cây thư mục

```text
neumf_project_v2/
├── configs/
│   ├── hm500k_global.yaml   # Protocol CHÍNH: một mốc thời gian chung (dùng cho tuning + đánh giá cuối)
│   ├── hm500k.yaml          # Protocol phụ: leave-one-out theo thời gian từng user (mặc định của run.py)
│   └── hm.yaml, hm_subset.yaml   # Cấu hình cũ (H&M đầy đủ / mẫu 300k), không dùng cho kết quả chính
├── data/
│   ├── raw/hm/              # transactions_train.csv (+ articles.csv, customers.csv chỉ cho demo) — tải từ Kaggle
│   └── processed/hm/        # hm500k_transactions.csv (sinh bởi scripts/00_sample_hm.py)
├── src/
│   ├── config.py
│   ├── data_pipeline/       # adapter H&M, preprocessing, k-core, splitting, negative sampling, dataset
│   ├── models/              # GMF, MLP, NeuMF (neumf.py), EarlyFusion
│   ├── baselines/           # Random, MostPopular, BPR-MF, ItemKNN (tự bỏ qua khi > 5.000 item)
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
│   ├── 08_hyperparam_sweep.py   # Sweep cũ (chỉ NeuMF-Scratch) — thay bằng 10_tune.py
│   ├── 09_full_report.py        # audit → sweep → final → multi-seed → evaluate
│   ├── 10_tune.py               # Tuning chỉ trên val → audit/tuning_log.csv, best_configs.json
│   ├── 11_final.py              # Đánh giá cuối trên TEST, 3 seed (có khoá test)
│   ├── 12_significance.py       # Wilcoxon + bootstrap CI + Holm → outputs/final/summary.csv, significance.csv
│   ├── 13_plot_final.py         # Biểu đồ kết quả cuối → outputs/figures/final_*.png
│   ├── 14_secondary.py          # Phân tích phụ trên test: head/tail, cold/warm, beyond-accuracy, Sampled-99, độ trễ
│   ├── 15_export_report.py      # Xuất bảng .tex + macro số liệu + hình sang Report DACNTT/
│   └── run_all.py               # 03 rồi 05
├── audit/                   # Bằng chứng thực nghiệm: PREREG.md, tuning_log.csv, best_configs.json, test_access_log.csv
├── notebooks/
│   ├── colab_final.ipynb    # Notebook Colab chạy lại kết quả cuối (mục 7)
│   └── colab_hm_subset.ipynb   # Notebook Colab cũ (run.py all trên mẫu 300k)
├── demo/                    # Web demo (xem demo/README.md)
├── outputs/
│   ├── final/               # Kết quả cuối (summary.csv, significance.csv, seed*/)
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
cd neumf_project_v2
python -m venv .venv
.venv\Scripts\activate            # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
```

Có GPU thì cài PyTorch bản CUDA **trước** rồi mới cài `requirements.txt`, ví dụ:
`pip install torch --index-url https://download.pytorch.org/whl/cu121`. Kiểm tra:
`python -c "import torch; print(torch.cuda.is_available())"`. Config để `device: auto` nên tự dùng GPU nếu có.

Mọi lệnh bên dưới chạy từ thư mục `neumf_project_v2/`.

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

## 5. Pipeline chính thức (tuning → test → kiểm định → biểu đồ)

Đây là đường tạo ra số liệu trong báo cáo (xem `pham_vi_du_an.md` mục 7–9).

### 5.1 Tuning (chỉ validation) — đã chạy xong, thường không cần chạy lại

```bash
python scripts/10_tune.py --model all          # hoặc: bpr | gmf | mlp | neumf_scratch | neumf_pretrained
```

Mặc định **ghi nối** vào `audit/tuning_log.csv` và ghi đè `best_configs.json` — là bằng chứng đã commit.
Muốn thử lại mà không đụng bằng chứng: thêm `--log-dir outputs/tuning_rerun`. Thời gian gốc: 1,9 giờ GPU.

### 5.2 Đánh giá cuối trên test (3 seed)

```bash
git status                       # working tree phải sạch, nếu không script từ chối chạy
python scripts/11_final.py --reason "Lý do chấm test"      # mặc định seed 42 2024 2025
```

Khoá test: script chỉ chạy khi `audit/PREREG.md` đã commit, có `--reason` và tree sạch. Mỗi seed ghi 1 dòng
vào `audit/test_access_log.csv` **trước** khi chấm. Chạy một lần cho cả 3 seed (sau seed đầu file log đã đổi
nên không chạy tách được). Chạy xong nên commit dòng log mới. Ra: `outputs/final/seed<N>/` (`results.json`,
`results_per_user.csv`, `topk.json`, checkpoint). Thời gian gốc: 65 phút trên RTX 3050.

### 5.3 Kiểm định và biểu đồ

```bash
python scripts/12_significance.py     # → outputs/final/summary.csv, significance.csv
python scripts/13_plot_final.py       # → outputs/figures/final_metrics.png, final_significance.png, final_val_vs_test.png
```

`13_plot_final.py` cần `outputs/final/seed*/results_per_user.csv` (chỉ có sau khi chạy 11).

### 5.4 Phân tích phụ và xuất sang báo cáo

```bash
python scripts/14_secondary.py --reason "Phân tích phụ trên test"   # nạp checkpoint của 11, không train lại
python scripts/15_export_report.py                                 # → ../Report DACNTT/content/tables/, media/figures/final/
```

`14_secondary.py` cần checkpoint trong `outputs/final/seed*/` và là một lần chấm test (ghi 1 dòng nhật ký); chỉ đòi
code/cấu hình không bị sửa (cho phép `outputs/` và `audit/test_access_log.csv`). Ra `outputs/final/{stratified,
beyond_accuracy,sampled99,latency}.csv` (khoảng 10–15 phút trên GPU).

`15_export_report.py` sinh bảng `.tex`, file macro `results_macros.tex` và chép hình `final_*.png` vào báo cáo. Chương 4,
5 và phần tóm tắt đọc số qua macro (`\Res{Pre}{NDCG10}`, `\Sig{PreBPR}{pholm}`…), nên chạy lại script rồi biên dịch là
số trong báo cáo tự cập nhật. Bảng/hình chưa có số liệu sẽ hiện khung "Chưa có số liệu" thay vì lỗi biên dịch.

## 6. Chạy nhanh bằng `run.py` (khám phá, protocol phụ, demo)

`run.py` chạy `03_run_experiment.py` với cấu hình mặc định (không phải cấu hình đã tune). Mặc định mọi bảng tính
trên **validation**; chấm test cần `--final --reason "..."` (cùng khoá test như trên).

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

Notebook chính: **`notebooks/colab_final.ipynb`** — chạy lại đúng pipeline mục 5.2–5.4 (dữ liệu → khám phá từng bước →
11_final 3 seed → kiểm định → biểu đồ → phân tích phụ → xuất bảng/hình cho báo cáo), dùng `best_configs.json` đã tune,
**không tune lại**.

Notebook **clone code từ GitHub** (`sulinh3625/DU-AN-CNTT`, nhánh `main`), nên mọi thay đổi ở máy local phải
**commit + push** trước khi chạy.

### 7.1 Mở notebook từ máy local lên Colab

Chọn một trong hai cách:

- **Upload từ máy:** vào https://colab.research.google.com → `File → Upload notebook` → chọn
  `neumf_project_v2/notebooks/colab_final.ipynb` trong repo local.
- **Mở từ GitHub:** `File → Open notebook → GitHub` → dán `https://github.com/sulinh3625/DU-AN-CNTT`
  → chọn `neumf_project_v2/notebooks/colab_final.ipynb` (repo private thì tick *Include private repos* và đăng nhập GitHub).

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
| 3 | Clone repo + `pip install` | Nếu pip đổi phiên bản numpy/pandas: `Runtime → Restart session`, chạy lại ô 2 và `%cd /content/DU-AN-CNTT/neumf_project_v2` |
| 4 | Dữ liệu hm500k | Dùng bản trên Drive nếu có; không thì tải Kaggle + lấy mẫu (10–20 phút) rồi lưu lên Drive |
| 5 | Khám phá pipeline từng bước | Kiểm tra khớp lần chạy gốc (201.801 cặp train, 10.145 item trong train) — lệch thì **dừng** |
| 6 | pytest + kiểm tra tree sạch | Tree bẩn thì 11_final từ chối chạy |
| 7 | `11_final.py` 3 seed | 65 phút – 2 giờ; log ghi song song lên Drive. Giữ tab mở để Colab không ngắt |
| 8 | Kiểm định + biểu đồ | Báo lỗi nếu seed nào chưa chạy xong |
| 9 | `14_secondary.py` | 10–15 phút; sửa `REASON_SECONDARY` ở ô 2 nếu muốn. Độ trễ đo trên CPU của Colab |
| 10 | `15_export_report.py` | Sinh bảng/macro/hình cho báo cáo trong bản clone |
| 11 | Lưu Drive + tải zip về máy | `My Drive/neumf_colab/results_<thời điểm>/` (không kèm checkpoint) |
| 12 | Xem nhanh kết quả | Đối chiếu với số gốc ở cuối notebook |

### 7.4 Sau khi chạy

Giải nén zip và chép về repo (bảng này cũng có ở cuối mục 11 của notebook):

| Trong zip | Chép vào repo |
|---|---|
| `final/` | `neumf_project_v2/outputs/final/` |
| `figures/final_*.png` | `neumf_project_v2/outputs/figures/` |
| `test_access_log.csv` | `neumf_project_v2/audit/test_access_log.csv` (ghi đè — đã gồm dòng cũ + dòng mới) |
| `report/` | `Report DACNTT/` (ghi đè `content/tables/`, `media/figures/final/`) |

Rồi commit và biên dịch lại báo cáo (`Report DACNTT/compile.bat`). Tìm `[TODO:` trong PDF: mục 4.4.4 cần 2–3 câu
nhận xét cho số liệu phân tích phụ (không viết trước được vì phụ thuộc kết quả).

- Nếu số so sánh "tốt hơn" trong bảng kiểm định khác 0/8, các câu kết luận chữ trong chương 4, 5 và tóm tắt phải sửa
  theo (số liệu trong câu thì tự cập nhật, nhưng câu "không so sánh nào có ý nghĩa" là chữ).
- Random và MostPopular phải ra giống hệt số gốc; BPR-MF gần như giống hệt; GMF/MLP/NeuMF trên GPU T4 có thể lệch
  nhẹ (cuDNN không tất định). Kết luận thống kê mới là thứ cần giữ.
- Colab ngắt giữa chừng: chạy lại từ ô 2 (mỗi lần chạy lại vẫn được ghi vào nhật ký test).

### 7.5 Notebook cũ `colab_hm_subset.ipynb`

Chạy `run.py all` trên mẫu ~300k (`configs/hm_subset.yaml`), đọc `transactions_train.csv` từ `My Drive/data/`,
lưu kết quả vào `My Drive/result/<thời điểm>/`. Không phải pipeline của kết quả chính — chỉ giữ để tham khảo.
