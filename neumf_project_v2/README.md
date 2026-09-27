# DACNTT — NeuMF Recommendation Project V2

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu.

Pipeline V2 tránh data leakage và đánh giá bằng full ranking. Dữ liệu thực nghiệm mặc định là
**hm500k**: mẫu khoảng 500k giao dịch H&M Personalized Fashion Recommendations, lấy theo khách hàng
và trải đủ 2018-09-20 → 2020-09-22 (21.599 khách; sau k-core 10: 7.519 users × 10.345 items,
220.292 tương tác).

Xem `pham_vi_du_an.md` để hiểu quyết định thiết kế pipeline/evaluation trước khi sửa code.

---

## Cây thư mục

```text
neumf_project_v2/
├── configs/
│   └── hm500k.yaml          # Config mặc định
├── data/
│   ├── raw/hm/              # transactions_train.csv (+ articles.csv, customers.csv chỉ cho demo) — tải từ Kaggle
│   └── processed/hm/        # hm500k_transactions.csv (sinh bởi scripts/00_sample_hm.py)
├── src/
│   ├── config.py
│   ├── data_pipeline/       # adapter H&M, preprocessing, k-core, splitting, negative sampling, side features
│   ├── models/              # GMF, MLP, NeuMF, EarlyFusion
│   ├── baselines/           # Random, MostPopular, BPR-MF, ItemKNN
│   ├── training/            # trainer.py — vòng lặp huấn luyện, early stopping
│   ├── evaluation/          # full_ranking, sampled_ranking, metrics, long_tail, cold_start, beyond_accuracy
│   └── utils/
├── scripts/
│   ├── 00_sample_hm.py          # Tạo hm500k từ transactions_train.csv gốc (chạy 1 lần)
│   ├── 01_data_audit.py         # Audit k-core, mật độ, kiểm tra split không giao nhau
│   ├── 02_preprocess.py         # Sinh splits thủ công
│   ├── 03_run_experiment.py     # Train toàn bộ mô hình + baselines
│   ├── 04_multi_seed.py         # Lặp lại 03 trên nhiều seed
│   ├── 05_evaluate.py           # Bảng + biểu đồ cho một run
│   ├── 06_aggregate_seeds.py    # mean ± std + kiểm định Wilcoxon qua các seed
│   ├── 08_hyperparam_sweep.py   # Sweep siêu tham số trên validation
│   ├── 09_full_report.py        # audit → sweep → final → multi-seed → evaluate
│   └── run_all.py               # 03 rồi 05
├── demo/                    # Web demo (xem demo/README.md)
├── outputs/{checkpoints,experiments,tables,figures,data_audit}/<run_tag>/
├── tests/
├── run.py                   # CLI tổng hợp (python run.py -h)
└── pham_vi_du_an.md
```

## Quy ước đặt tên

| Thứ | Tên |
|---|---|
| Config | `configs/<tên>.yaml` (mặc định `hm500k`) |
| Run | `<tên config>_seed<seed>`, vd. `hm500k_seed42` (mặc định của 03 và 04) |
| Bảng multi-seed | `outputs/tables/<tên config>_multiseed/` |
| Sweep | `outputs/tables/sweep_<tên config>/` |

Cùng config + cùng seed là cùng một thí nghiệm, nên chạy lại sẽ ghi đè run cũ cùng tên. Muốn giữ cả hai
thì truyền `--run-tag` khác.

---

## 1. Cài đặt

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Nếu có GPU, cài PyTorch bản CUDA trước rồi mới cài `requirements.txt`.

## 2. Dữ liệu

Đặt 3 file của cuộc thi Kaggle "H&M Personalized Fashion Recommendations" vào `data/raw/hm/`, rồi:

```bash
python run.py sample-hm      # ~1 phút, RAM ~0,5 GB → data/processed/hm/hm500k_transactions.csv
```

Mẫu lấy theo hash `customer_id` nên chạy lại luôn ra đúng cùng một file.
`customers.csv` đọc được cả bản gốc lẫn bản đã bị Excel lưu lại (phân cách `;`).

## 3. Train + đánh giá một seed

```bash
python run.py all                 # audit → train → evaluate, run tag hm500k_seed42
python run.py evaluate --run-tag hm500k_seed42
```

RAM đỉnh đo được ~4,1 GB trên máy 16 GB. Thời gian mỗi seed đo trước khi gỡ content-based là ~100 phút
(train 5 mô hình neural chỉ ~14 phút); đã gỡ nên sẽ nhanh hơn, chưa đo lại.

Kết quả: `outputs/tables/<run_tag>/` (xem `evaluation_report.txt` trước) và `outputs/figures/<run_tag>/`.

Mô hình trong bảng đánh giá (đúng phạm vi đề tài: mô hình lai MF + DNN chỉ học từ ma trận tương tác):

| Nhóm | Mô hình |
|---|---|
| Mô hình đề tài | NeuMF-Scratch, NeuMF-Pretrained (GMF + MLP ghép ở tầng cuối) |
| Ablation | GMF (chỉ MF), MLP (chỉ DNN), EarlyFusion (lai ghép sớm) |
| Baseline truyền thống | Random, MostPopular, BPR-MF |

Các mô hình dùng thuộc tính sản phẩm/khách hàng (ContentBased, Hybrid-NeuMF-CBF, CategoryPopularity,
AgeGroupPopularity) nằm ngoài phạm vi nên đã gỡ khỏi code. Run cũ vẫn còn số của chúng trong
`results.json` nên được ẩn khỏi bảng, biểu đồ, demo (`REPORT_HIDDEN_MODELS` trong `scripts/common.py`).

Hai cách chia dữ liệu:
- `configs/hm500k.yaml`: leave-one-out theo thời gian từng user (protocol của bài NeuMF gốc).
- `configs/hm500k_global.yaml`: một mốc thời gian chung (train < 2020-07-01 ≤ val < 2020-07-29 ≤ test),
  mỗi user test có thể có nhiều item đúng — dùng để kiểm chứng, vì leave-one-out rò rỉ tương lai.

## 4. Multi-seed & kiểm định

```bash
python run.py multi-seed          # seed 42 2024 2025 2026 3407 7 → hm500k_seed<N>
python run.py aggregate           # → outputs/tables/hm500k_multiseed/
```

Cần ≥ 6 seed: với 5 seed, p-value nhỏ nhất của Wilcoxon là 0,0625 nên không bao giờ đạt p < 0,05.

## 5. Demo

```bash
python run.py demo                # = python -m demo → http://localhost:8000
```

Demo tự dùng run `hm500k_seed*` mới nhất. Chi tiết trong `demo/README.md`.

## 6. Test

```bash
pytest -q                 # tests/
pytest demo/tests -q      # cần đã có run hm500k và file offline của demo
```
