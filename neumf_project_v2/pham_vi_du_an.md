# Phạm Vi & Phương Pháp Luận — NeuMF V2

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu (NeuMF)
**GVHD:** TS. Hồ Thị Linh — **Nhóm:** Lê Minh Lý, Sử Thị Yến Linh

> Đây là tài liệu phạm vi và phương pháp luận **chính thức của V2**. Mọi quyết định thiết kế pipeline/evaluation ghi ở đây đã được cài đặt trong `src/`. Không còn file nào khác trong `docs/` cần đọc.

---

## 1. Phạm Vi Thực Nghiệm

### ✅ Trong phạm vi

- Dữ liệu thật: H&M Personalized Fashion Recommendations, mẫu **hm500k** (~500k giao dịch lấy theo khách hàng,
  trải đủ 2018-09-20 → 2020-09-22)
- Lọc k-core (k=10), ánh xạ ID, binary implicit feedback
- Phân chia Leave-One-Out kết hợp kiểm tra Disjoint bắt buộc
- Kiến trúc: GMF, MLP, EarlyFusion, NeuMF (from-scratch & pre-trained) — He et al. (2017)
- Baselines truyền thống: Random, MostPopular, BPR-MF
- Mọi mô hình chỉ học từ ma trận tương tác user–sản phẩm (lọc cộng tác thuần)
- Đánh giá Full Ranking (chính) + Sampled-99 (đối chiếu protocol NCF gốc)
- Phân tích phân tầng: Long-tail (head/tail items), Cold-start (cold/warm users)
- Beyond-accuracy: Catalog Coverage, Novelty, Popularity Bias (ARP, HRR)
- Multi-seed + kiểm định Wilcoxon (hạ tầng đã có, chưa chạy đủ — xem mục 4)
- Hai cách chia: leave-one-out theo thời gian từng user (chính) và một mốc thời gian chung (kiểm chứng)
- Demo inference-only: FastAPI backend + HTML frontend (không train lại)

### ❌ Ngoài phạm vi

- Thông tin nội dung: thuộc tính/ảnh/mô tả sản phẩm, thông tin khách hàng (các mô hình ContentBased,
  Hybrid-NeuMF-CBF, CategoryPopularity, AgeGroupPopularity đã gỡ khỏi code)
- Mô hình đồ thị (LightGCN) và mô hình chuỗi (SASRec): không thuộc họ MF + DNN, đã gỡ khỏi code
- Cold-start tuyệt đối (user/item mới hoàn toàn) — CF thuần ID không chấm được
- Cold-start item mới hoàn toàn (item chưa có giao dịch nào không nằm trong catalog đánh giá)
- Hyperparameter search tự động (Optuna/AutoML)
- Triển khai production (Docker đóng gói chưa hoàn chỉnh — xem mục 4)

---

## 2. Quyết Định Pipeline Dữ Liệu

### 2.1 Thứ tự: Aggregate → k-core (không đảo ngược)

K-core đếm degree theo số **item/user khác nhau**, không phải số transaction.
Mua lại cùng sản phẩm nhiều lần vẫn là 1 cạnh User-Item.
V1 đã làm sai thứ tự này → số liệu V1 và V2 không so sánh được trực tiếp.

Mẫu hm500k: 500.269 dòng, 21.599 khách, 429.964 cặp user-item duy nhất trước k-core.

| k | Users | Items | Unique interactions | Density | RAM ước tính cho full ranking |
|--:|--:|--:|--:|--:|--:|
| 5 | 12.900 | 23.067 | 340.267 | 0,114% | ~10,7 GB (vượt máy 16 GB) |
| **10** | **7.519** | **10.345** | **220.292** | **0,283%** | **~2,8 GB** |

Dùng k=10 (RAM đỉnh đo thực tế khi train một seed: 4,1 GB). k=10 thiên về khách mua nhiều — ghi là hạn chế.

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
- Metrics: **HR@K**, **NDCG@K** với K ∈ {5, 10}.
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
| Beyond-accuracy | Coverage, Novelty, ARP (Avg. Recommendation Popularity), HRR (Head Rec. Rate) |

Popularity của items tính **chỉ từ train set** (không dùng val/test để tránh leakage định nghĩa).

---

## Tiến Độ (cập nhật 27/09/2026)

### ✅ Đã xong
| Hạng mục | Kết quả / vị trí |
|---|---|
| Pipeline V2 (aggregate → k-core → LOO, Full Ranking) | `src/data_pipeline`, `src/evaluation` |
| Dữ liệu mặc định hm500k (tái lập được) | `python run.py sample-hm`, `configs/hm500k.yaml` |
| Cold-start tương đối (20% user ít tương tác nhất) | `src/evaluation/cold_start.py` |
| Chia theo mốc thời gian chung + metric nhiều item đúng | `configs/hm500k_global.yaml`, `src/data_pipeline/splitting.py` |
| Run hm500k seed 42 (leave-one-out và mốc thời gian chung) | `outputs/*/hm500k_seed42`, `outputs/*/hm500k_global_seed42` |
| Demo khớp kết quả run (sai lệch ≤ 1e-6) | `demo/` |
| Test | `pytest -q` + `pytest demo/tests -q` |

Kết quả seed 42 (NDCG@10, Full Ranking, 1 seed — chưa đủ để kết luận):

| Mô hình | Leave-one-out | Mốc thời gian chung |
|---|---|---|
| MostPopular | 0,0063 | 0,0100 |
| BPR-MF | 0,0068 | 0,0106 |
| GMF | 0,0076 | 0,0089 |
| MLP | 0,0066 | 0,0114 |
| EarlyFusion | 0,0064 | 0,0094 |
| NeuMF-Scratch | 0,0072 | 0,0098 |
| NeuMF-Pretrained | **0,0086** | 0,0104 |

Bootstrap theo user — leave-one-out: NeuMF-Pretrained hơn MostPopular và MLP có ý nghĩa, hơn GMF thì chưa
(p ≈ 0,07). Mốc thời gian chung: chỉ MLP hơn GMF chắc chắn; NeuMF-Pretrained không khác MostPopular (p ≈ 0,64).
Thứ hạng đổi theo cách chia (đúng như Meng et al. 2020) → cần multi-seed trên cả hai cách chia.

### ⏳ Chưa làm
| Hạng mục | Ghi chú |
|---|---|
| Multi-seed (≥ 6 seed) cho cả hai cách chia + Wilcoxon | `python run.py multi-seed [--config configs/hm500k_global.yaml]` rồi `aggregate` |
| Cập nhật báo cáo LaTeX (`Report DACNTT`) theo hm500k | C3 (dữ liệu, phương pháp), C4 (bảng + hình), C5/C6 |
| BPR-MF chưa lưu checkpoint | Demo chưa chấm được BPR-MF |

---

## 4. Hạn Chế Đã Biết

| Hạn chế | Trạng thái |
|---|---|
| Multi-seed chưa chạy đủ | Script `04_multi_seed.py` + `06_aggregate_seeds.py` đã cài, chưa chạy đủ 5 seeds |
| H&M chỉ dùng mẫu | ~1,6% khách (500k/31,8M dòng) — lấy mẫu theo khách hàng, giữ đủ lịch sử mua |
| Full Ranking trên H&M full | Không khả thi trên CPU — cần Sampled-99 ở quy mô đầy đủ |
| Leave-one-out rò rỉ tương lai | Trung bình 11,2% tương tác train xảy ra sau ngày của test item; 60,9% user có val/test cùng ngày → có thêm cách chia mốc thời gian chung để kiểm chứng |
| k-core lọc trên toàn bộ dữ liệu | Kể cả giai đoạn val/test (rò rỉ nhỏ, áp dụng như nhau cho mọi mô hình) |
| Dự đoán trong cùng giỏ hàng | Timestamp H&M theo ngày: item test có thể mua cùng ngày với item trong hồ sơ — áp dụng như nhau cho mọi mô hình |
| Docker chưa kiểm tra đầy đủ | `Dockerfile` có, chưa confirm build + đo latency thực |

---

## 5. Siêu Tham Số Chính Thức (V2)

| Nhóm | Tham số | Giá trị |
|---|---|---|
| Dữ liệu | k-core | 10 |
| | Negative ratio (train) | 4 |
| Mô hình | Embedding dim | 32 |
| | MLP layers | [64, 32, 16, 8] |
| | Dropout | 0,2 |
| Huấn luyện | Batch size | 512 |
| | Optimizer | Adam, lr=1e-3 (pretrain và fine-tune) |
| | Weight decay | 1e-6 |
| | Max epochs | 20 |
| | Patience | 7 |
| Đánh giá | K values | 5, 10 |

Tham số đầy đủ trong `configs/hm500k.yaml`.
