# Phạm Vi & Phương Pháp Luận — NeuMF V2

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu (NeuMF)
**GVHD:** TS. Hồ Thị Linh — **Nhóm:** Lê Minh Lý, Sử Thị Yến Linh

> Đây là tài liệu phạm vi và phương pháp luận **chính thức của V2**. Mọi quyết định thiết kế pipeline/evaluation ghi ở đây đã được cài đặt trong `src/`. Không còn file nào khác trong `docs/` cần đọc.

---

## 1. Phạm Vi Thực Nghiệm

### ✅ Trong phạm vi

- Xử lý dữ liệu thật: DataCo Supply Chain (chính) và H&M Fashion (đối chứng)
- Lọc k-core (k=5), ánh xạ ID, binary implicit feedback
- Phân chia Leave-One-Out kết hợp kiểm tra Disjoint bắt buộc
- Kiến trúc: GMF, MLP, EarlyFusion, NeuMF (from-scratch & pre-trained) — He et al. (2017)
- Baselines: Random, MostPopular, CategoryPopularity, ItemKNN, BPR-MF
- Content-based trên H&M (dùng đủ 3 file `transactions_train.csv` + `articles.csv` + `customers.csv`):
  ContentBased (one-hot thuộc tính sản phẩm + TF-IDF `prod_name`/`detail_desc`, hồ sơ user có trọng số thời gian),
  CategoryPopularity (`product_type_name`), AgeGroupPopularity (nhóm tuổi từ `customers.csv`)
- Hybrid-NeuMF-CBF: lai ghép muộn `alpha·NeuMF + (1-alpha)·CBF`, alpha chọn trên validation
- Mô hình bổ sung: LightGCN, SASRec (đã cài đặt, dùng để so sánh)
- Đánh giá Full Ranking (chính) + Sampled-99 (đối chiếu protocol NCF gốc)
- Phân tích phân tầng: Long-tail (head/tail items), Cold-start (cold/warm users)
- Cold-start tuyệt đối trên H&M: user bị k-core loại (1–4 giao dịch) — chỉ phương pháp nội dung/độ phổ biến chấm được
- Beyond-accuracy: Catalog Coverage, Novelty, Popularity Bias (ARP, HRR)
- Multi-seed + kiểm định Wilcoxon (hạ tầng đã có, chưa chạy đủ — xem mục 4)
- Demo inference-only: FastAPI backend + HTML frontend (không train lại)

### ❌ Ngoài phạm vi

- Đặc trưng hình ảnh sản phẩm (văn bản mô tả đã dùng trong ContentBased)
- Mô hình hoá chuỗi thời gian / session-based (SASRec chỉ là baseline so sánh)
- Cold-start tuyệt đối cho CF thuần ID (giới hạn lý thuyết) — trên H&M được xử lý bằng Content-based
- Cold-start item mới hoàn toàn (item chưa có giao dịch nào không nằm trong catalog đánh giá)
- Hyperparameter search tự động (Optuna/AutoML)
- Triển khai production (Docker đóng gói chưa hoàn chỉnh — xem mục 4)

---

## 2. Quyết Định Pipeline Dữ Liệu

### 2.1 Thứ tự: Aggregate → k-core (không đảo ngược)

K-core đếm degree theo số **item/user khác nhau**, không phải số transaction.
Mua lại cùng sản phẩm nhiều lần vẫn là 1 cạnh User-Item.
V1 đã làm sai thứ tự này → số liệu V1 và V2 không so sánh được trực tiếp.

| k | Users | Items | Unique interactions | Density |
|--:|--:|--:|--:|--:|
| 3 | 11.943 | 100 | 92.230 | 7,72% |
| **5** | **10.799** | **100** | **88.088** | **8,16%** |
| 10 | 2.736 | 97 | 29.749 | 11,21% |

Dùng k=5. Raw: 180.519 dòng → 10.799 users, 100 items, 88.088 unique interactions.

### 2.2 Leave-One-Out Split

```
Test      : item cuối cùng (theo thời gian) của mỗi user
Validation: item áp chót
Train     : tất cả trước đó
Assert    : train∩val = train∩test = val∩test = ∅  (cấp (user, item))
```

Assert Disjoint là bắt buộc — V1 không có kiểm tra này.

### 2.3 Negative Sampling

- **Train**: 4 negatives/positive; pool loại toàn bộ **train positives** (không dùng future labels).
- **Eval (Sampled-99)**: loại toàn bộ known positives để tránh false negative.
- **Eval (Full Ranking)**: loại train+val positives, giữ test positive trong candidates.

### 2.4 Feedback

Binary implicit feedback là mặc định (mua = 1, chưa mua = 0).
Weighted confidence (dùng giá trị đơn hàng) chỉ là ablation phụ, không phải luận điểm chính.

---

## 3. Giao Thức Đánh Giá

### 3.1 Primary: Full Ranking

- Với mỗi user trong test: loại seen items (train+val), score toàn bộ candidates còn lại.
- Metrics: **HR@K**, **NDCG@K** với K ∈ {1, 5, 10, 20}.
- Early stopping theo **NDCG@10**.
- Tie-breaking: deterministic (dùng hash seed), không random.
- Batched inference: flatten toàn bộ (user, candidate) pairs → batch lớn → hiệu quả.

### 3.2 Secondary: Sampled-99

- 1 positive + 99 sampled negatives — đúng protocol He et al. (2017).
- Dùng để đối chiếu với kết quả gốc NCF paper, không phải luận điểm chính.

### 3.3 Phân Tầng

| Phân tích | Định nghĩa |
|---|---|
| Long-tail | Top 10% items theo train interactions = head; phần còn lại = tail |
| Cold-start | Bottom 20% users theo train interactions = cold |
| Cold-start tuyệt đối (H&M) | User bị k-core loại, có >= 2 item thuộc catalog: item cuối = test, phần trước = hồ sơ; tối đa 5.000 user |
| Beyond-accuracy | Coverage, Novelty, ARP (Avg. Recommendation Popularity), HRR (Head Rec. Rate) |

Popularity của items tính **chỉ từ train set** (không dùng val/test để tránh leakage định nghĩa).

---

## Tiến Độ (cập nhật 25/09/2026)

### ✅ Đã xong
| Hạng mục | Kết quả / vị trí |
|---|---|
| Pipeline V2 (aggregate → k-core → LOO, Full Ranking) | `src/data_pipeline`, `src/evaluation` |
| DataCo: GMF, MLP, EarlyFusion, NeuMF, baselines, LightGCN, SASRec | `outputs/*/dataco_v2_full`, `dataco_v2_sasrec`, `dataco_20260918_verify` |
| H&M dùng đủ 3 file (transactions + articles + customers) | `configs/hm_subset.yaml`, `src/data_pipeline/side_features.py` |
| Content-based: ContentBased, CategoryPopularity, AgeGroupPopularity | `src/baselines/content_based.py` |
| Hybrid-NeuMF-CBF (alpha chọn trên validation, alpha = 0,2) | `src/baselines/hybrid.py` |
| Cold-start tương đối + tuyệt đối (5.000 user mới) | `src/evaluation/cold_start.py` |
| Run H&M chính thức (seed 42) | `outputs/*/hm_cbf_v1` — bảng + 13 hình |
| Hình so sánh DataCo vs H&M sinh lại từ `hm_cbf_v1` | `outputs/figures/comparison/` |
| Test | 34 test pass (`pytest -q`) |

Kết quả chính H&M (NDCG@10, Full Ranking): MostPopular 0,037 · NeuMF-Pretrained 0,041 ·
ContentBased 0,058 · **Hybrid 0,060 (+47% so với NeuMF)**. Long-tail: NeuMF 0 → ContentBased 0,056.
Cold-start tuyệt đối: ContentBased 0,118 vs MostPopular 0,042 (CF thuần ID không áp dụng được).

### ⏳ Chưa làm
| Hạng mục | Ghi chú |
|---|---|
| Multi-seed H&M + DataCo, kiểm định Wilcoxon | `python run.py multi-seed --dataset hm_subset` rồi `aggregate` (~4 phút/seed H&M) |
| Cập nhật báo cáo LaTeX (`Report DACNTT`) với CBF/Hybrid/cold-start | C3 (phương pháp), C4 (kết quả, bảng + hình 12–13), C5/C6 (thảo luận, kết luận); chép lại hình so sánh mới vào `media/figures/` |
| Chạy lại DataCo đầy đủ sau thay đổi code | Chỉ mới smoke test; kết quả DataCo cũ vẫn hợp lệ (logic CF không đổi) |
| Demo chưa hiển thị CBF/Hybrid | `demo/backend/main.py` chỉ nạp checkpoint các mô hình neural |

---

## 4. Hạn Chế Đã Biết

| Hạn chế | Trạng thái |
|---|---|
| Multi-seed chưa chạy đủ | Script `04_multi_seed.py` + `06_aggregate_seeds.py` đã cài, chưa chạy đủ 5 seeds |
| H&M chỉ ở quy mô lát cắt | 100.000 dòng đầu (~1.743 users), không phải 31,8M dòng gốc |
| Full Ranking trên H&M full | Không khả thi trên CPU — cần Sampled-99 ở quy mô đầy đủ |
| CBF/Hybrid chỉ dùng hồ sơ TRAIN | Giống CF (không thấy item validation) để so sánh công bằng |
| Dự đoán trong cùng giỏ hàng | Timestamp H&M theo ngày: item test có thể mua cùng ngày với item trong hồ sơ — áp dụng như nhau cho mọi mô hình |
| Docker chưa kiểm tra đầy đủ | `Dockerfile` có, chưa confirm build + đo latency thực |

---

## 5. Siêu Tham Số Chính Thức (V2)

| Nhóm | Tham số | Giá trị |
|---|---|---|
| Dữ liệu | k-core | 5 |
| | Negative ratio (train) | 4 |
| Mô hình | Embedding dim | 32 |
| | MLP layers | [64, 32, 16, 8] |
| | Dropout | 0,2 |
| Huấn luyện | Batch size | 256 |
| | Optimizer | Adam, lr=1e-3 |
| | Weight decay | 1e-6 |
| | Max epochs | 50 |
| | Patience | 10 |
| Đánh giá | K values | 1, 5, 10, 20 |

Tham số đầy đủ trong `configs/dataco.yaml` và `configs/hm_subset.yaml`.
