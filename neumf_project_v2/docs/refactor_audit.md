# Refactor Audit — NeuMF V2 → H&M Full (STEP 1)

Ngày audit: 2026-09-25 · Phạm vi: `neumf_project_v2/` · Trạng thái: **chỉ audit, chưa sửa code**.
Căn cứ: "MASTER INSTRUCTION — NEUMF V2 REFACTOR & FULL H&M TRAINING PIPELINE" (gọi tắt: *spec*, số mục §N).
Môi trường chạy: tiền xử lý có thể chạy local (Windows, 15,7 GB RAM, CPU, không CUDA); **huấn luyện chạy trên Google Colab GPU**.

---

## 1. Hiện trạng repository

```text
neumf_project_v2/
├── configs/        dataco.yaml · hm.yaml · hm_subset.yaml · hm_primary.yaml (mới, chưa commit)
├── src/
│   ├── config.py                     dataclass config loader (YAML → ProjectConfig)
│   ├── data_pipeline/
│   │   ├── adapters/{base,dataco,hm}.py   đọc raw → events chuẩn hoá (pandas)
│   │   ├── preprocessing.py          aggregate unique (user,item) → k-core → reindex (pandas)
│   │   ├── kcore.py                  iterative k-core (pandas, lặp đến hội tụ)
│   │   ├── splitting.py              temporal LOO theo last_timestamp + assert_disjoint_splits
│   │   ├── negative_sampling.py      positive sets = list[set]; sample theo từng user (Python loop)
│   │   ├── dataset.py                TrainDataset: resample negatives mỗi epoch (Python loop)
│   │   ├── side_features.py          articles/customers → item/user idx
│   │   └── audit.py                  k-core sensitivity + split overlap
│   ├── models/{neumf,early_fusion,lightgcn,sasrec}.py
│   ├── baselines/{classical,content_based,hybrid}.py
│   ├── training/trainer.py           train_one_model (BCEWithLogits, early stopping theo val)
│   ├── evaluation/{full_ranking,sampled_ranking,metrics,ranking_utils,long_tail,cold_start,beyond_accuracy,statistics}.py
│   └── utils/{seed,io}.py
├── scripts/00…09 + common.py + run_all.py      pipeline từng bước
├── run.py                                      CLI tổng (all/audit/preprocess/train/evaluate/multi-seed/aggregate/compare/demo)
├── tests/            34 test (pass) · demo/tests: 6 pass + 2 skip
├── demo/             FastAPI + frontend (mới mở rộng, chưa commit)
├── outputs/          experiments|tables|figures|checkpoints: dataco_20260918_verify, dataco_v2_full, dataco_v2_sasrec, hm_cbf_v1, sweep_hm
└── data/raw/hm/{transactions_train,articles,customers}.csv · data/processed/hm/*.parquet (cache int32)
```

Ghi chú phát hiện ngoài lề:
- `data/processed/dataco/` đang chứa **bản sao file H&M** (`transactions_train.csv` 3,5 GB, `articles.csv`, `customers.csv`, `.xlsx`). Không được code nào dùng. Không xoá — chờ người dùng xác nhận.
- `configs/hm_primary.yaml` + `PLAN_swap_primary_dataset.md` là kế hoạch trước đó (lọc 1 năm cuối bằng `start_date`, cold_fraction…) — **mâu thuẫn với spec** (spec: H&M FULL, DuckDB, fixed candidates). Đánh dấu deprecated, không xoá.
- `LightGCN`/`SASRec` có class trong `src/models/` và có kết quả cũ (`dataco_v2_full`, `dataco_v2_sasrec`) nhưng **không script nào gọi tới** (phần nối vào runner đã mất, không có trong lịch sử git). Cần nối lại.
- Quy mô H&M Full sau k-core (README ghi ~889K users × 90K items) **chưa được đo thực tế**: `outputs/data_audit/hm` chỉ là audit lát cắt 100K dòng. Số thật sẽ có ở STEP 3.

---

## 2. Đối chiếu từng thành phần với spec

| Thành phần | Hiện trạng | Đánh giá theo spec | Hành động |
|---|---|---|---|
| Đọc raw H&M | pandas `read_csv`; cache Parquet bằng pandas chunk (00) rồi **nạp toàn bộ vào pandas** | Vi phạm §5 ở quy mô full | THÊM pipeline DuckDB out-of-core |
| article_id | đọc `dtype=string` + `zfill(10)` | Đúng §8 | GIỮ, thêm test riêng cho đường DuckDB |
| Aggregate → k-core | Đúng thứ tự, 1 cặp = 1 cạnh (có test) | Đúng §7; thiếu `first/last_source_order` cho tie-break theo first | SỬA nhẹ (thêm cột), cài lại bằng SQL cho full |
| Iterative k-core | Lặp đến hội tụ, không có assert sau cùng | Thiếu assert `min degree ≥ k` (§9) | SỬA: thêm assert (cả pandas & DuckDB) |
| Temporal LOO | Sắp theo **last_timestamp** | **Sai §10** (primary phải là first_timestamp) | SỬA: `split_timestamp` configurable, mặc định `first_timestamp` |
| Disjoint check | `assert_disjoint_splits` raise AssertionError | Đúng §11 | GIỮ; đường full kiểm tra bằng SQL/NumPy |
| Same-day tie audit | Không có | Thiếu §12 | THÊM |
| Split versioning / metadata | `02_preprocess` ghi CSV + `meta.json` tối giản; runner tự split lại mỗi lần | Thiếu §13–14 | THÊM `data/splits/<version>/` Parquet + `split_metadata.json`, chặn overwrite |
| Train negatives | Dynamic mỗi epoch, loại train positives (đúng ngữ nghĩa) nhưng **Python loop từng positive + mask n_items** | Đúng §15 về ngữ nghĩa, **không chạy được ở quy mô full** | SỬA: rejection sampling vector hoá trên CSR train positives |
| Positive sets | `list[set]` cho mọi user | Quá tốn RAM ở full (Colab ~12,7 GB) | SỬA: CSR (indptr/indices, int32) |
| Sampled-99 | Sinh lại mỗi run, seed = `training.seed+2` → **phụ thuộc seed huấn luyện** | Vi phạm §16 (phải cố định 1 file, seed 2026, dùng chung mọi model) | THÊM candidates cố định Parquet |
| Full ranking | Flatten toàn bộ candidate của mọi record một lần | Không chunk được ở quy mô lớn (§18) | SỬA: user-batch × item-chunk |
| Sampled evaluator | Flatten B×100, forward theo batch | Cơ bản đúng §19, nhưng giữ toàn bộ record trong RAM | SỬA: tensor [N,100] cố định, forward theo batch trên GPU |
| Exact subset | Không có | Thiếu §17 | THÊM: tập user cố định lấy từ split full, `max_users` configurable |
| Metrics | HR/NDCG@K, Precision/Recall tuỳ chọn | Đúng §20 | GIỮ |
| GMF/MLP/NeuMF | 4 embedding độc lập, output logits, BCEWithLogits | Đúng §23 (có test) | GIỮ |
| **EarlyFusion** | **Giống hệt kiến trúc MLP** (1 bộ embedding, concat, MLP) | Vi phạm §22 | SỬA kiến trúc + test phân biệt |
| Pretraining | Scratch & Pretrained cùng `finetune_*`, cùng budget | Đúng §24 | GIỮ |
| Thời gian pretrained | Chỉ ghi thời gian fine-tune | Thiếu §25 | SỬA: 4 trường thời gian |
| BPR-MF | NumPy SGD từng mẫu (Python loop) | Không khả thi ở full; không dùng GPU | SỬA: cài lại **cùng mô hình BPR** bằng PyTorch (không phải model mới) |
| ItemKNN | Dense n_items² (có chặn 5.000 item) | §21 cho phép chỉ chạy exact subset/DataCo | SỬA: skip có ghi lý do thay vì crash |
| ContentBased | one-hot + TF-IDF, hồ sơ từ TRAIN, `recency_decay` chọn trên val | Đúng §26–27; `score_items` tính dot với **toàn catalog** mỗi user → chậm ở full | SỬA: chỉ chấm các candidate; thêm ablation Categorical/Text/All (§28) |
| Hybrid | min-max từng user, alpha grid trên val | Đúng §29; thiếu `alpha_validation_results.csv` | SỬA nhỏ |
| Cold/warm | "cold" = bottom 20% train users | **Sai thuật ngữ §30** | SỬA: `warm / low_activity / few_shot / zero_history` |
| Strict cold-start | user ngoài k-core, ≥2 item trong catalog, không giới hạn trên | Gần §30 (few_shot = 1–4 item) | SỬA: giới hạn 2–4 item + đổi tên few_shot |
| Zero-history | Không có | Thiếu §31 | THÊM đánh giá fallback (MostPopular/AgeGroup/…) |
| Long-tail | head = top 10% theo train | Đúng định nghĩa; thiếu các share §32 | SỬA: thêm bảng share |
| Beyond-accuracy | 4 metric, popularity từ train | Đúng §33 | GIỮ |
| LightGCN | Graph chỉ từ train ✔; propagate toàn đồ thị **mỗi batch** khi train | Đúng §35 về leakage; **chưa nối runner**; rất nặng ở full | SỬA: nối runner, batch lớn riêng cho LightGCN, benchmark |
| SASRec | Sequence từ train ✔ nhưng sắp theo last_timestamp; chưa nối runner | Sai §34 (phải first_timestamp, document "first-time discovery order") | SỬA |
| Trainer | Batching thủ công NumPy→tensor; không AMP; không log peak memory | Thiếu §38, §43 | SỬA: AMP tuỳ chọn, tensor trên device, efficiency log |
| Early stopping | Theo val NDCG@10, giữ best state | Đúng §40 | GIỮ |
| Multi-seed | `04` chạy lại toàn pipeline, tag `<name>_seed_<s>` | Chưa theo phase §41 / cấu trúc output §44 | SỬA |
| Statistics | mean/std + Wilcoxon | Thiếu absolute diff (có mean_diff), thiếu cặp Hybrid vs CBF… | SỬA nhỏ (§42) |
| Hyperparam search | `08` coordinate sweep chỉ NeuMF-Scratch | §36 cần 6–10 config/model, chọn theo val | SỬA/mở rộng |
| run_metadata | Thiếu device, versions, git commit, candidate seed… | Thiếu §45 | THÊM |
| CLI `run.py` | Có all/audit/preprocess/train/evaluate/multi-seed/aggregate | Thiếu `--model`, `--seed`, dataset `hm_full`, `hm_smoke` (§47, §49) | MỞ RỘNG (không tạo CLI mới) |

---

## 3. Danh sách file

### 3.1 Giữ nguyên
| File | Lý do |
|---|---|
| `src/models/neumf.py` | GMF/MLP/NeuMF đúng §23–24 (4 embedding, logits, load_pretrained) |
| `src/evaluation/metrics.py`, `ranking_utils.py` | Công thức đúng, tie-break deterministic |
| `src/evaluation/beyond_accuracy.py` | Đúng §33 |
| `src/data_pipeline/adapters/dataco.py`, `adapters/base.py` | DataCo là control, không đổi đọc dữ liệu |
| `src/utils/io.py`, `seed.py` | Dùng lại |
| `configs/dataco.yaml`, `configs/hm_subset.yaml`, `configs/hm.yaml` | Không overwrite (§37); chỉ thêm `role: control` cho DataCo (§50) |
| `outputs/**` hiện có | Không xoá kết quả cũ (§2) |
| `demo/**` | Ngoài phạm vi refactor; phụ thuộc đường hm_subset → giữ tương thích |

### 3.2 Sửa
| File | Thay đổi | Mục spec |
|---|---|---|
| `src/config.py` | Thêm `dataset.variant/role`, `preprocessing.*` (engine, memory_limit, threads, temp_dir, split_timestamp, split_version), `evaluation.large_scale.*`, `evaluation.exact_subset.*`, `training.amp/num_workers/…`; giữ tương thích YAML cũ | §37 |
| `src/data_pipeline/preprocessing.py` | Giữ `first/last_source_order`; tie-break theo first | §10, §12 |
| `src/data_pipeline/kcore.py` | Assert min degree ≥ k sau hội tụ | §9 |
| `src/data_pipeline/splitting.py` | `split_timestamp` (mặc định first), tie audit, raise khi overlap | §10–12 |
| `src/data_pipeline/negative_sampling.py`, `dataset.py` | CSR + rejection sampling vector hoá; giữ API cũ cho DataCo/test | §15 |
| `src/evaluation/full_ranking.py` | Evaluator chunked (user batch × item chunk) | §18 |
| `src/evaluation/sampled_ranking.py` | Đọc candidates cố định; evaluator [B,100] | §16, §19 |
| `src/evaluation/cold_start.py` | Đổi tên low_activity/few_shot/zero_history; few_shot 2–4 item | §30–31 |
| `src/evaluation/long_tail.py` | Thêm head/tail share | §32 |
| `src/evaluation/statistics.py` | absolute diff, relative improvement; bootstrap (tuỳ chọn) | §42 |
| `src/models/early_fusion.py` | Kiến trúc early fusion thật (xem §5.3) | §22 |
| `src/models/lightgcn.py` | Hỗ trợ batch lớn/propagate một lần mỗi step; ghi rõ train-only | §35 |
| `src/models/sasrec.py` | Sắp theo first_timestamp, docstring "first-time discovery order" | §34 |
| `src/baselines/classical.py` | BPR bằng PyTorch (cùng mô hình); ItemKNN skip có lý do | §21 |
| `src/baselines/content_based.py`, `hybrid.py` | Chấm theo candidate; ablation CBF; lưu alpha CSV | §26–29 |
| `src/training/trainer.py` | AMP tuỳ chọn, tensor trên device, peak memory, inference timing | §38–40, §43 |
| `scripts/03_run_experiment.py` | Nhánh hm_full đọc split versioned; nối LightGCN/SASRec; chọn model theo `--model`; output §44 | §21, §44 |
| `scripts/04_multi_seed.py`, `06_aggregate_seeds.py` | Phase seed + cấu trúc `outputs/hm_full/seed_*`; cặp so sánh §42 | §41–42 |
| `scripts/08_hyperparam_sweep.py` | Sweep nhỏ cho từng model, chọn theo val | §36 |
| `run.py`, `scripts/common.py` | Thêm `hm_full`, `hm_smoke`, `--model`, `--seed` | §47, §49 |
| `requirements.txt` | Thêm `duckdb` | §5 |
| `configs/dataco.yaml` | Thêm `role: control` (không đổi tham số) | §50 |

### 3.3 Thêm mới
| File | Nội dung |
|---|---|
| `configs/hm_full.yaml` | Config chính thức §37 |
| `configs/hm_smoke.yaml` | 100K dòng, 1–2 epoch, cùng code path với hm_full (§49) |
| `src/data_pipeline/duckdb_pipeline.py` | Scan CSV out-of-core → schema validation → aggregate → k-core (SQL lặp) → reindex → Parquet |
| `src/data_pipeline/split_store.py` | Ghi/đọc split versioned + `split_metadata.json`, chặn overwrite |
| `src/evaluation/candidates.py` | Sinh `sampled_99_seed2026.parquet` + exact subset user list |
| `src/utils/run_metadata.py` | device, CUDA, torch version, git commit, config snapshot |
| `scripts/10_preprocess_hm_full.py` (tên cuối cùng theo quy ước scripts) | Chạy DuckDB pipeline + split + candidates |
| `notebooks/colab_train_hm_full.ipynb` hoặc `docs/colab.md` | Hướng dẫn chạy trên Colab (mount Drive, cài deps, resume) |
| `tests/test_hm_full_pipeline.py`, `tests/test_fairness.py` | 18 nhóm test §46 |
| `docs/hm_full_migration_report.md`, `docs/report_update_plan.md` | Báo cáo §57, kế hoạch sửa LaTeX §52 |

### 3.4 Deprecated (giữ file, không dùng làm đường chính)
| File | Lý do |
|---|---|
| `configs/hm_primary.yaml`, `PLAN_swap_primary_dataset.md` | Thay bằng `hm_full.yaml` + spec này (lọc 1 năm ≠ FULL) |
| `scripts/00_prepare_hm_cache.py` + `data/processed/hm/*.parquet` | Thay bằng DuckDB pipeline; giữ vì `hm.yaml` và demo còn dùng |
| `scripts/02_preprocess.py` (CSV splits) | Thay bằng split store Parquet; giữ cho DataCo/hm_subset |
| `configs/hm.yaml` | Thay bằng `hm_full.yaml` |

---

## 4. Backward compatibility

1. **DataCo & hm_subset vẫn chạy bằng đường pandas cũ**, cùng CLI (`run.py all --dataset dataco|hm_subset`). Đường hm_full là nhánh mới, không thay thế.
2. **Thay đổi làm số liệu cũ không tái lập được** (đều do spec yêu cầu):
   - LOO theo `first_timestamp` thay vì `last_timestamp` → split DataCo/hm_subset đổi. Giữ `split_timestamp: last_timestamp` làm tuỳ chọn để tái lập kết quả cũ.
   - EarlyFusion đổi kiến trúc → kết quả EarlyFusion cũ không còn so sánh được.
   - Sampled-99 dùng candidate cố định seed 2026 thay vì seed huấn luyện + 2.
   - BPR cài lại bằng PyTorch → số BPR thay đổi nhẹ.
   - Kết quả cũ trong `outputs/` được giữ nguyên, đánh dấu "pre-refactor" trong migration report; DataCo sẽ chạy lại bằng code cuối (§50).
3. **results.json**: đổi khoá `cold_start` → `low_activity`, `cold_start_strict` → `few_shot`. `05_evaluate.py` sẽ đọc được cả khoá cũ để không vỡ các run cũ và demo.
4. **Demo** đọc `hm_subset` + `last_timestamp` cho phần hiển thị lịch sử → không ảnh hưởng vì cột vẫn còn.
5. **Tests**: không xoá test cũ; test nào kiểm tra hành vi đổi theo spec (vd. LOO theo last) sẽ được cập nhật tham số chứ không bỏ.

---

## 5. Quyết định kỹ thuật cần ghi nhận (không đổi spec)

### 5.1 Chạy trên Colab
- Tiền xử lý DuckDB có thể chạy **local** (6 GB limit, spill ra đĩa) hoặc Colab; output là Parquet nhỏ gọn (ước tính vài trăm MB) → đưa lên Google Drive.
- Huấn luyện trên Colab: RAM hệ thống ~12,7 GB → mọi cấu trúc per-user phải là mảng NumPy/CSR, không dùng `list[set]`.
- Colab hay ngắt phiên → mỗi model lưu checkpoint + kết quả riêng trong `outputs/hm_full/seed_<s>/`; runner **bỏ qua model đã xong** khi chạy lại (resume). Không đổi methodology.
- `num_workers` mặc định 2 trên Colab; 0 trên Windows (§38).

### 5.2 Tie-break same-day (§12)
Aggregate giữ `first_source_order` (thứ tự dòng trong CSV gốc, deterministic). Thứ tự LOO: `(first_timestamp, first_source_order, item_raw)`. Ghi `same_day_tie_users`, `same_day_tie_rate` vào metadata. Có sẵn hàm để chạy basket-split làm sensitivity sau này, không đổi protocol chính.

### 5.3 EarlyFusion mới (§22)
Hai bộ embedding (MF: `p_u, q_i`; deep: `u, i`) → **ghép ngay từ đầu** `[p_u ⊙ q_i ; u ; i]` → một mạng MLP chung → logit. NeuMF giữ late fusion (GMF và MLP là hai nhánh riêng, chỉ nối ở lớp cuối). Lớp MLP đầu của EarlyFusion có input `3·d` (cùng các lớp ẩn còn lại). Test: kiểm tra input dim và việc không có nhánh GMF riêng.

### 5.4 Few-shot (§30)
User không thuộc k-core, có **2–4 unique item nằm trong catalog k-core** (cần ≥2 để có hồ sơ + test). User bị loại do k-core lan truyền nhưng có ≥5 item trong catalog được đếm riêng trong metadata, không trộn vào few_shot.

### 5.5 Rủi ro hiệu năng cần benchmark ở Phase 2 (không quyết định trước)
- **LightGCN** full-graph propagation mỗi step: cần batch lớn (vd. 8192+) trên GPU; nếu vượt ngân sách Colab → chạy trên exact subset, ghi rõ lý do (§21 cho phép tương tự ItemKNN).
- **SASRec** BCE theo cặp (user,item): mỗi mẫu encode lại chuỗi → đắt ở full; tối ưu bằng encode user một lần/batch. Benchmark trước khi chốt.
- **Validation mỗi epoch** trên toàn bộ user × 100 candidate: khả thi với NeuMF trên GPU; với SASRec/LightGCN sẽ đo thực tế.

---

## 6. Kế hoạch thực hiện (theo §56)

| Step | Việc | Chạy test |
|---|---|---|
| 2 | Config (`hm_full.yaml`, `hm_smoke.yaml`, loader), paths, `requirements.txt` | pytest |
| 3 | DuckDB out-of-core preprocessing (schema validation, aggregate, k-core SQL + assert, reindex, Parquet) | pytest |
| 4 | Split first_timestamp + tie audit + versioning + metadata | pytest |
| 5 | Candidates cố định `sampled_99_seed2026.parquet` | pytest |
| 6 | Exact subset | pytest |
| 7–8 | Unit tests §46 + smoke test `hm_smoke` end-to-end | pytest + smoke |
| 9 | Audit/sửa model & fairness (EarlyFusion, BPR torch, timings, LightGCN/SASRec nối runner, terminology) | pytest + smoke |
| 10 | Tối ưu trainer/evaluator GPU (AMP, batching, efficiency log) | pytest + smoke |
| 11 | Toàn bộ test | pytest |
| 12 | `docs/hm_full_migration_report.md` + `docs/report_update_plan.md` + hướng dẫn Colab | — |

Không chạy preprocessing/training 31,8M dòng cho tới khi người dùng xác nhận (§48).
