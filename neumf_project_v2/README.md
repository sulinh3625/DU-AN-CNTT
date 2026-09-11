# DACNTT — NeuMF Recommendation Project V2

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu.

Phiên bản V2 refactor pipeline để tránh data leakage, chuẩn hóa đánh giá full-ranking, hỗ trợ DataCo làm dataset chính và H&M làm scalability benchmark về sau.

## Cây thư mục chính thức

```text
neumf_project_v2/
├── configs/
│   ├── dataco.yaml
│   └── hm.yaml
├── data/
│   ├── raw/
│   │   ├── dataco/
│   │   └── hm/
│   ├── processed/
│   │   ├── dataco/
│   │   └── hm/
│   └── splits/
│       ├── dataco/
│       └── hm/
├── docs/
│   ├── METHODOLOGY_V2.md
│   ├── MIGRATION_V1_TO_V2.md
│   └── legacy_v1_pham_vi_du_an.md
├── src/
│   ├── config.py
│   ├── data/
│   │   ├── adapters/
│   │   │   ├── base.py
│   │   │   ├── dataco.py
│   │   │   └── hm.py
│   │   ├── preprocessing.py
│   │   ├── kcore.py
│   │   ├── splitting.py
│   │   ├── negative_sampling.py
│   │   ├── dataset.py
│   │   └── audit.py
│   ├── models/
│   │   └── neumf.py
│   ├── baselines/
│   │   └── classical.py
│   ├── training/
│   │   └── trainer.py
│   ├── evaluation/
│   │   ├── metrics.py
│   │   ├── ranking_utils.py
│   │   ├── full_ranking.py
│   │   ├── sampled_ranking.py
│   │   ├── long_tail.py
│   │   ├── beyond_accuracy.py
│   │   └── statistics.py
│   └── utils/
│       ├── seed.py
│       └── io.py
├── scripts/
│   ├── 01_data_audit.py
│   ├── 02_preprocess.py
│   ├── 03_run_experiment.py
│   └── 04_multi_seed.py
├── tests/
├── outputs/
│   ├── data_audit/
│   ├── checkpoints/
│   ├── experiments/
│   ├── tables/
│   ├── figures/
│   └── legacy_v1/
├── notebooks/
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

Nếu cần CUDA, cài PyTorch theo đúng bản CUDA của máy trước khi cài phần còn lại.

## 2. Đặt DataCo

```text
data/raw/dataco/DataCoSupplyChainDataset.csv
```

## 3. Audit dữ liệu — phải chạy trước training

```bash
python scripts/01_data_audit.py --config configs/dataco.yaml
```

Kiểm tra đặc biệt:

```text
train_val_overlap  = 0
train_test_overlap = 0
val_test_overlap   = 0
```

Kết quả lưu ở `outputs/data_audit/dataco/`.

## 4. Sinh splits

```bash
python scripts/02_preprocess.py --config configs/dataco.yaml
```

## 5. Chạy core experiment

```bash
python scripts/03_run_experiment.py --config configs/dataco.yaml
```

Kết quả gồm:

- `results_primary.csv`: full-ranking theo config.
- `results_sampled_99.csv`: protocol 99 negative để đối chiếu.
- `results_long_tail.csv`.
- histories và metadata/checkpoints.

## 6. Multi-seed

```bash
python scripts/04_multi_seed.py --config configs/dataco.yaml --seeds 42 2024 2025 2026 3407
```

## 7. H&M

Chỉ triển khai sau khi DataCo V2 đã pass audit và evaluator.

