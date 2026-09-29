# Phạm Vi, Cơ Sở Lý Thuyết & Phương Pháp Luận — NeuMF V2

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu (NeuMF)
**GVHD:** TS. Hồ Thị Linh — **Nhóm:** Lê Minh Lý, Sử Thị Yến Linh

> Tài liệu tổng hợp **toàn bộ lý thuyết và quyết định phương pháp** của dự án: phạm vi, cơ sở lý thuyết mô hình,
> dữ liệu, cách chia, giao thức đánh giá, quy trình tuning/kiểm định, kết quả và hạn chế. Hướng dẫn cài đặt và chạy
> (máy local, Google Colab, demo) nằm trong `README.md`.
>
> Bằng chứng thực nghiệm ở `audit/`: `PREREG.md` (đăng ký trước — khoá test kiểm tra file này), `tuning_log.csv`
> (mọi cấu hình đã tune), `best_configs.json` (cấu hình tốt nhất trên val), `test_access_log.csv` (mỗi lần chấm test).
> Số liệu kết quả cuối: `outputs/final/`.

---

## 1. Bài Toán & Yêu Cầu Đề Tài

**Bài toán:** khuyến nghị Top-K sản phẩm cho khách hàng từ **phản hồi ngầm** (lịch sử mua), không có điểm đánh giá.
Với mỗi user $u$, mô hình chấm điểm $\hat{y}_{ui}$ cho mọi sản phẩm $i$ chưa mua, xếp hạng giảm dần và lấy K món đầu.

Yêu cầu (R1–R8, dùng để kiểm định dự án):

| Mã | Yêu cầu |
|---|---|
| R1 | H&M Personalized Fashion Recommendations là dataset **chính và duy nhất** cho kết quả |
| R2 | **Lọc cộng tác thuần**: chỉ học từ tương tác user–item (ID, số lần mua, thời điểm). Không dùng `articles.csv`, `customers.csv`, văn bản, ảnh, tuổi, danh mục làm đầu vào. "Lai" = MF + DNN theo NCF |
| R3 | GMF + MLP → NeuMF, có pre-training (He et al., 2017) |
| R4 | Mọi đặc trưng lịch sử mua (tần suất, recency, confidence) chỉ tính từ **train** |
| R5 | Huấn luyện & tinh chỉnh có hệ thống, toàn bộ trail ghi vào `tuning_log.csv` |
| R6 | Precision@K, Recall@K, NDCG@K (giữ HR@K); protocol chính là **Full Ranking** |
| R7 | Khả năng triển khai: API/demo, độ trễ đo thật; chưa đo thì không khẳng định |
| R8 | Báo cáo khớp code + file kết quả, không nhắc đề tài khác |

---

## 2. Phạm Vi

### ✅ Trong phạm vi

- Dữ liệu thật H&M, mẫu **hm500k** (~500k giao dịch lấy theo khách hàng, trải đủ 2018-09-20 → 2020-09-22)
- Gộp cặp user–item → lọc k-core (k = 10) → ánh xạ ID → phản hồi nhị phân
- Hai cách chia theo thời gian: **một mốc thời gian chung** (chính) và leave-one-out từng user (phụ), luôn kiểm tra không giao nhau
- Mô hình: GMF, MLP, NeuMF-Scratch, NeuMF-Pretrained (He et al., 2017)
- Baseline: Random, MostPopular, BPR-MF (được tune cùng ngân sách)
- Đánh giá Full Ranking (chính) + Sampled-99 (chỉ để đối chiếu protocol NCF gốc)
- Phân tích mô tả: long-tail (head/tail), cold/warm user, coverage, novelty, popularity bias (ARP, HRR)
- Tuning chỉ trên validation, khoá tập test, 3 seed, kiểm định paired theo user + hiệu chỉnh Holm
- Demo inference-only: FastAPI backend + HTML frontend (không train lại)

### ❌ Ngoài phạm vi

- Thông tin nội dung (thuộc tính/ảnh/mô tả sản phẩm, thông tin khách hàng). Các mô hình ContentBased,
  Hybrid-NeuMF-CBF, CategoryPopularity, AgeGroupPopularity đã gỡ khỏi code
- Mô hình đồ thị (LightGCN), mô hình chuỗi (SASRec): không thuộc họ MF + DNN, đã gỡ khỏi code
- iALS, MostPopular theo cửa sổ gần, CFNet/DeepCF, late fusion MF + NeuMF: đã thử trên validation rồi bỏ theo
  quyết định của nhóm (quá nhiều baseline) — xem mục 8.4
- ConvNCF: tích ngoài d×d + CNN cho từng cặp → Full Ranking ~23 triệu cặp mỗi lượt val, quá đắt
- ItemKNN: ma trận tương đồng dày O(items²), 10.345 item vượt ngưỡng an toàn 5.000
- Cold-start tuyệt đối (user/item chưa có giao dịch nào): CF thuần ID không chấm được. Demo có gợi ý rule-based cho khách mới, **gắn nhãn không phải mô hình**
- Hyperparameter search tự động (Optuna/AutoML); triển khai production

---

## 3. Cơ Sở Lý Thuyết

### 3.1 Hệ khuyến nghị và phản hồi ngầm

- **Content-based** dựa vào thuộc tính sản phẩm; **lọc cộng tác (CF)** dựa vào hành vi của nhiều user: user có lịch sử
  giống nhau sẽ thích sản phẩm giống nhau. Đề tài chỉ dùng CF.
- **Phản hồi ngầm (implicit feedback):** chỉ biết user *đã mua* ($y_{ui} = 1$). $y_{ui} = 0$ **không** có nghĩa là
  không thích — có thể chưa thấy. Vì vậy bài toán là **xếp hạng** (one-class), không phải dự đoán điểm, và cần
  **negative sampling** khi huấn luyện.
- Ma trận tương tác $R \in \{0,1\}^{|U| \times |I|}$ rất thưa (hm500k sau k-core: mật độ 0,283%).

### 3.2 Nhân tử hoá ma trận (MF)

Mỗi user có vector ẩn $\mathbf{p}_u \in \mathbb{R}^d$, mỗi item có $\mathbf{q}_i \in \mathbb{R}^d$; điểm là tích vô hướng:

$$\hat{y}_{ui} = \mathbf{p}_u^\top \mathbf{q}_i = \sum_{k=1}^{d} p_{uk}\, q_{ik}$$

Hạn chế (He et al., 2017): tương tác giữa các nhân tử ẩn là **tuyến tính** với trọng số bằng nhau → có thể không đủ
biểu diễn quan hệ phức tạp. Ngược lại, Rendle et al. (2020) chỉ ra MF tích vô hướng **được tune kỹ** vẫn thắng
NeuMF trên chính dữ liệu của bài NCF — lý do đề tài bắt buộc tune baseline cùng ngân sách.

### 3.3 BPR-MF (baseline)

Bayesian Personalized Ranking (Rendle et al., 2009) tối ưu thứ tự theo cặp: item đã mua $i$ phải xếp trên item chưa mua $j$.

$$\mathcal{L}_{BPR} = -\sum_{(u,i,j)} \ln \sigma\!\left(\hat{y}_{ui} - \hat{y}_{uj}\right) + \lambda \left(\lVert\mathbf{p}_u\rVert^2 + \lVert\mathbf{q}_i\rVert^2 + \lVert\mathbf{q}_j\rVert^2\right)$$

Cài đặt (`src/baselines/classical.py::BPRMFBaseline`): SGD từng mẫu bằng NumPy, $j$ lấy đều từ item user chưa mua
trong train; cập nhật $\mathbf{p}_u \mathrel{+}= \eta\,[\sigma(-x)(\mathbf{q}_i - \mathbf{q}_j) - \lambda \mathbf{p}_u]$ (tương tự cho $\mathbf{q}_i, \mathbf{q}_j$), với $x = \mathbf{p}_u^\top(\mathbf{q}_i - \mathbf{q}_j)$.

### 3.4 Các baseline không học

- **Random:** điểm ngẫu nhiên — cận dưới.
- **MostPopular:** điểm = số user đã mua item **trong train**; mọi user nhận cùng một danh sách (trừ item đã mua).
  Là baseline mạnh trên dữ liệu thời trang vì độ phổ biến lệch mạnh.

### 3.5 Neural Collaborative Filtering (He et al., 2017)

Khung NCF: embedding user/item → các tầng nơ-ron → lớp output $\hat{y}_{ui} = \sigma(\mathbf{h}^\top \phi(\cdot))$.
Mã nguồn: `src/models/neumf.py`.

**GMF (Generalized Matrix Factorization)** — tổng quát hoá MF bằng tích từng phần tử và trọng số học được:

$$\phi^{GMF} = \mathbf{p}_u^G \odot \mathbf{q}_i^G, \qquad \hat{y}_{ui} = \sigma\!\left(\mathbf{h}^\top (\mathbf{p}_u^G \odot \mathbf{q}_i^G)\right)$$

Khi $\mathbf{h} = \mathbf{1}$ thì GMF trở về MF.

**MLP** — nối hai embedding rồi qua tháp nơ-ron để học tương tác **phi tuyến**:

$$\mathbf{z}_1 = [\mathbf{p}_u^M ; \mathbf{q}_i^M], \quad \mathbf{z}_{l+1} = \mathrm{ReLU}(W_l \mathbf{z}_l + \mathbf{b}_l), \quad \hat{y}_{ui} = \sigma(\mathbf{h}^\top \mathbf{z}_L)$$

Tháp theo NCF: mỗi tầng giảm một nửa, `[64, 32, 16, 8]` với embedding 32 (tầng đầu = 2 × embedding_dim); dropout sau mỗi ReLU.

**NeuMF** — lai MF + DNN: GMF và MLP có **embedding riêng** (4 bảng), ghép vector ẩn cuối rồi qua một lớp output:

$$\hat{y}_{ui} = \sigma\!\left(\mathbf{h}^\top \left[\, \mathbf{p}_u^G \odot \mathbf{q}_i^G \;;\; \mathbf{z}_L^{M} \,\right]\right)$$

Embedding riêng cho phép hai nhánh có số chiều khác nhau (`gmf_dim`), linh hoạt hơn chia sẻ embedding.

**Pre-training (NeuMF-Pretrained):** huấn luyện GMF và MLP riêng tới hội tụ, chép embedding + tầng MLP sang NeuMF,
khởi tạo lớp output bằng $\mathbf{h} \leftarrow [\alpha\,\mathbf{h}^{GMF} ; (1-\alpha)\,\mathbf{h}^{MLP}]$ (bài gốc α = 0,5),
rồi fine-tune. **NeuMF-Scratch** khởi tạo ngẫu nhiên (embedding ~ N(0; 0,01), Xavier cho tầng tuyến tính).
Khác bài gốc: dự án fine-tune bằng **Adam** chứ không SGD, vì SGD lr 0,01 làm NeuMF không hội tụ trên dữ liệu này.

**EarlyFusion** (`src/models/early_fusion.py`): nối embedding rồi qua tháp MLP — **trùng hệt kiến trúc MLP**
(kiểm chứng: cùng seed cho val NDCG@10 bằng nhau 0,00770 = 0,00770;
`tests/test_tuning.py::test_early_fusion_is_architecturally_identical_to_mlp`). Vì vậy trong báo cáo, MLP chính là
ablation "early fusion / chỉ DNN"; EarlyFusion không được tune hay kiểm định riêng.

### 3.6 Hàm mất mát và negative sampling

Coi mỗi cặp là bài toán phân loại nhị phân, dùng **binary cross-entropy** trên logit (`BCEWithLogitsLoss`):

$$\mathcal{L} = -\sum_{(u,i) \in \mathcal{Y}^+ \cup \mathcal{Y}^-} y_{ui} \log \hat{y}_{ui} + (1 - y_{ui}) \log (1 - \hat{y}_{ui})$$

- Mỗi positive đi kèm **4 negative** (He et al.: tốt nhất khoảng 3–6; tuning thử {4, 8}), lấy lại **mỗi epoch**
  (`src/data_pipeline/dataset.py::TrainDataset`).
- Pool negative loại toàn bộ **train positives** — không dùng nhãn val/test (tránh rò rỉ tương lai).
- Khi xếp hạng, dùng **logit** chứ không qua sigmoid: sigmoid float32 bão hoà sẽ tạo điểm bằng nhau giả.

### 3.7 Tối ưu và early stopping

Adam, batch 512, tối đa 20 epoch; sau mỗi epoch chấm **NDCG@10 trên validation** (Full Ranking), giữ trạng thái tốt nhất,
dừng khi không cải thiện sau `patience` epoch (config mặc định 7; tuning và đánh giá cuối dùng 5 theo PREREG).
Mô hình neural đạt đỉnh rất sớm (epoch 1–9) — dữ liệu thưa nên quá khớp nhanh.

---

## 4. Dữ Liệu

### 4.1 Nguồn

Cuộc thi Kaggle **H&M Personalized Fashion Recommendations**: `transactions_train.csv` (31,8 triệu dòng, 2018-09-20 →
2020-09-22), `articles.csv`, `customers.csv`. Mô hình **chỉ đọc transactions** (có test khẳng định adapter chỉ mở file
này — `tests/test_pure_cf.py`). `articles.csv`/`customers.csv` chỉ dùng ở demo để hiển thị tên sản phẩm và gợi ý
rule-based cho khách mới.

Lưu ý đọc dữ liệu: `article_id` phải đọc dạng chuỗi + `zfill(10)` để giữ số 0 đầu; không dùng bản `.xlsx` (Excel cắt
ở 1.048.576 dòng).

### 4.2 Lấy mẫu hm500k

`scripts/00_sample_hm.py`: lấy mẫu **theo khách hàng** (hash `customer_id` với khoá cố định) — giữ **toàn bộ lịch sử**
của các khách được chọn, trải đủ 2 năm, tới khi đạt ~500k dòng. Tất định: chạy lại luôn ra cùng một file.
Đọc theo chunk, RAM ~0,5 GB. Kết quả: 500.269 dòng, 21.599 khách, ~1,6% dữ liệu gốc.

Lý do lấy mẫu theo khách (không theo dòng): lấy theo dòng sẽ cắt vụn lịch sử từng user, làm hỏng cả k-core lẫn cách chia theo thời gian.

### 4.3 Tiền xử lý: Aggregate → k-core (không đảo ngược)

1. **Gộp** giao dịch lặp thành cặp (user, item) duy nhất, giữ `first_timestamp`, `last_timestamp`, `interaction_count`.
   Mua lại cùng sản phẩm nhiều lần vẫn là 1 cạnh. hm500k: 500.269 dòng → 429.964 cặp.
2. **Iterative k-core:** loại lặp user và item có ít hơn k cặp **khác nhau** cho tới khi hội tụ (loại item có thể làm
   user rớt dưới k và ngược lại). Đếm theo cặp, không theo số giao dịch — V1 làm ngược thứ tự nên số V1 và V2 không so được.
3. **Re-index** user/item thành số nguyên liên tục 0..N−1.
4. **Phản hồi nhị phân** (mua = 1). Trọng số confidence theo số lần mua chỉ là tuỳ chọn ablation, scale fit trên train.

| k | Users | Items | Cặp duy nhất | Mật độ | RAM ước tính cho Full Ranking |
|--:|--:|--:|--:|--:|--:|
| 5 | 12.900 | 23.067 | 340.267 | 0,114% | ~10,7 GB (vượt máy 16 GB) |
| **10** | **7.519** | **10.345** | **220.292** | **0,283%** | **~2,8 GB** |

Chọn **k = 10** (lệch khỏi chuẩn k = 5 vì RAM; RAM đỉnh đo thực tế khi train một seed 4,1 GB). Hệ quả: dữ liệu thiên
về khách mua nhiều — ghi là hạn chế.

### 4.4 Các phương án dữ liệu đã thử và bỏ

Trước khi chốt hm500k, dự án đã thử ba phương án khác. Code của chúng đã gỡ khỏi repo (notebook `colab_hm_subset.ipynb`,
`configs/hm.yaml`, `configs/hm_subset.yaml`, `scripts/00_prepare_hm_cache.py`, `scripts/00_sample_hm300k.py`);
số liệu đo được giữ lại dưới đây vì là lý do cho các quyết định ở mục 4.2–4.3.

**(a) Toàn bộ H&M + cache Parquet** (`hm.yaml`). Đọc thẳng CSV 31,8 triệu dòng tốn nhiều; cache một lần sang Parquet
(đọc theo lô 2 triệu dòng, mã hoá `customer_id`/`article_id` thành int32, hạ kiểu số, ghi streaming) giảm đáng kể:

| Tiêu chí | CSV gốc | Cache Parquet |
|---|---|---|
| Kích thước | 3.488 MB | 323 MB (≈ 10,8 lần nhỏ hơn) |
| Thời gian nạp lại | ≈ 33 giây | ≈ 1,8 giây |
| RAM khi nạp | ≈ 7.851 MB | ≈ 890 MB |

Nhưng nạp nhanh không giải quyết được chi phí đánh giá. Độ nhạy k-core trên **toàn bộ** dữ liệu:

| k | Users | Items | Tương tác | Mật độ |
|--:|--:|--:|--:|--:|
| 3 | 1.074.388 | 96.264 | 26.873.935 | 0,0260% |
| 5 | 889.062 | 90.690 | 26.215.294 | 0,0325% |
| 10 | 633.130 | 80.265 | 24.426.258 | 0,0481% |

Ở k = 5, Full Ranking cần ≈ 889.062 × 90.690 ≈ 8,06·10¹⁰ cặp điểm cho **mỗi** mô hình → không khả thi với GPU 4 GB,
RAM 16 GB. Bỏ.

**(b) Lát cắt 100.000 dòng đầu tệp** (bản báo cáo cũ). Tệp gốc sắp theo ngày nên 100k dòng đầu chỉ phủ **3 ngày**
(20–22/09/2018): sau k = 5 còn 1.743 user × 1.080 item (8.200 cặp train); k = 10 thì sụp về 0. Không có chiều thời
gian, catalog quá nhỏ và mọi kết luận chỉ đúng cho 3 ngày. Bỏ.

**(c) Lấy mẫu ngẫu nhiên theo dòng.** 300k dòng rải trên 1,36 triệu khách → trung bình ≈ 0,2 giao dịch/khách; đã đo:
lấy ngẫu nhiên theo dòng hay cách đều theo dòng đều còn **0 tương tác sau k-core = 5**. Đây là lý do mọi mẫu về sau
đều lấy **theo khách hàng**, giữ trọn lịch sử.

**(d) hm_subset ≈ 300k dòng theo khách, k = 5, leave-one-out** (`hm_subset.yaml`, chạy bằng `run.py all` với cấu hình
mặc định, 1 seed). Đúng hướng lấy mẫu nhưng chưa tinh chỉnh, chưa khoá test, protocol leave-one-out rò rỉ tương lai
(mục 5.2). Được thay bằng hm500k + chia theo mốc thời gian chung + quy trình ở mục 7–8.

---

## 5. Chia Dữ Liệu

### 5.1 Protocol chính — một mốc thời gian chung (`configs/hm500k_global.yaml`)

Mỗi cặp (user, item) xếp theo **lần mua đầu tiên**:

```
train < 2020-07-01 ≤ val < 2020-07-29 ≤ test   (test đến 2020-09-22)
```

- Val/test chỉ giữ user và item đã xuất hiện trong train (CF thuần ID không chấm được user/item mới).
- Mỗi user có thể có **nhiều item đúng** → cần Recall/Precision thật, không chỉ HR.
- Item user đã mua trước đó không là đích: chỉ dự đoán món **mới** với user.
- Kích thước: train 201.801 cặp (7.506 user, 10.145 item); val 7.057 cặp / 2.275 user; test 8.493 cặp / 2.893 user
  (trung bình 2,94 item đúng mỗi user test).

Lý do chọn làm chính (Meng et al., 2020): leave-one-out để **rò rỉ tương lai** — trung bình 11,2% tương tác train xảy ra
**sau** ngày của item test, 60,9% user có val/test cùng ngày. Mốc chung đảm bảo mô hình chỉ thấy quá khứ.

### 5.2 Protocol phụ — leave-one-out theo thời gian (`configs/hm500k.yaml`)

```
Test      : item cuối cùng (theo thời gian) của mỗi user
Validation: item áp chót
Train     : tất cả trước đó
```

Đúng protocol bài NCF gốc, dùng để đối chiếu, **không dùng để chọn mô hình**. Chạy thử seed 42 cho thấy thứ hạng
mô hình **đổi** giữa hai cách chia (ví dụ NeuMF-Pretrained đứng đầu ở LOO nhưng không khác MostPopular ở mốc chung)
— đúng như Meng et al. (2020) cảnh báo.

### 5.3 Kiểm tra bắt buộc

- `assert_disjoint_splits`: train ∩ val = train ∩ test = val ∩ test = ∅ ở cấp (user, item). V1 không có kiểm tra này.
- `tests/test_no_leakage_real_data.py` chạy trên hm500k thật: mốc chung chỉ có một dòng thời gian, user/item val/test ⊂ train;
  LOO thì val ≥ train và test ≥ val theo từng user.
- Mọi thống kê (popularity, head/tail, cold user, pool negative, confidence) **chỉ tính trên train**.

---

## 6. Giao Thức Đánh Giá

### 6.1 Full Ranking (chính)

Với mỗi user test: candidate = **toàn bộ item có trong train** (10.145 trên 10.345 item sau k-core), loại item user đã có trong train (khi chấm val)
hoặc train ∪ val (khi chấm test); item đúng vẫn nằm trong candidate. Chấm điểm mọi candidate, xếp hạng, lấy top-K.
Tie-break **tất định** (seed 2026). Số candidate thực tế mỗi user được ghi lại (min 9.863, max 10.144 ở val).

### 6.2 Sampled-99 (chỉ đối chiếu)

1 item đúng + 99 negative lấy mẫu (protocol He et al., 2017). Krichene & Rendle (2020) chứng minh metric lấy mẫu
**không nhất quán** với bản đầy đủ và có thể đảo ngược "A tốt hơn B" → không dùng để kết luận.

### 6.3 Độ đo

Với $T_u$ là tập item đúng của user $u$, $\text{hits}_u$ = số item đúng trong top-K, $r$ là hạng (bắt đầu từ 1):

| Độ đo | Công thức (trung bình theo user) |
|---|---|
| HR@K | $\mathbb{1}[\text{hits}_u \ge 1]$ |
| Precision@K | $\text{hits}_u / K$ |
| Recall@K | $\text{hits}_u / \lvert T_u \rvert$ |
| NDCG@K | $\dfrac{\sum_{i \in T_u,\, r_i \le K} 1/\log_2(r_i + 1)}{\sum_{j=1}^{\min(\lvert T_u \rvert, K)} 1/\log_2(j + 1)}$ |

Với leave-one-out ($\lvert T_u \rvert = 1$): NDCG@K = $1/\log_2(r+1)$ nếu $r \le K$; Recall = HR, Precision = HR/K.
K ∈ {5, 10}. **Metric chính: NDCG@10.** Công thức cài ở `src/evaluation/metrics.py`, có unit test tính tay.

### 6.4 Phân tích phân tầng và beyond-accuracy (mô tả, không kết luận)

| Phân tích | Định nghĩa |
|---|---|
| Long-tail | Top 10% item theo số tương tác train = head; còn lại = tail |
| Cold / warm user | 20% user ít tương tác train nhất = cold (cold-start **tương đối**, không phải user mới) |
| Catalog coverage | Tỉ lệ item xuất hiện trong ít nhất một danh sách top-K |
| Novelty | Trung bình $-\log_2 P(i)$ với $P(i)$ = tần suất item trong train (Vargas & Castells, 2011) |
| ARP | Average Recommendation Popularity — số tương tác train trung bình của item được gợi ý |
| HRR | Head Recommendation Rate — tỉ lệ item head trong danh sách gợi ý |

---

## 7. Quy Trình Thực Nghiệm Chống Thiên Lệch

Dựa trên Ferrari Dacrema et al. (2019) — code NCF gốc chọn số epoch theo **tập test**, baseline tune sơ sài — và
Rendle et al. (2020). Nguyên tắc:

1. **Khoá tập test.** Chọn mô hình/siêu tham số chỉ trên validation. Test chỉ chấm qua `scripts/11_final.py`
   (hoặc `run.py ... --final`), từ chối chạy nếu `audit/PREREG.md` chưa commit, thiếu `--reason`, hoặc
   working tree có file theo dõi bị sửa. Mỗi lần chấm ghi 1 dòng `audit/test_access_log.csv`
   (thời gian, git commit, config hash, lý do).
2. **Đăng ký trước (PREREG).** Metric, lưới tuning, số seed, họ so sánh, tiêu chí "tốt hơn" được commit **trước**
   lần chấm test đầu tiên. Mọi lệch kế hoạch ghi vào PREREG mục 8 và báo cáo.
3. **Truy vết.** Mỗi run lưu `config_hash` (sha256 config đã nạp), `git_commit`, `git_dirty`, `n_candidates`,
   và `results_per_user.csv` (hạng từng item đúng của từng user) để kiểm định paired.
4. **So sánh công bằng.** Cùng split, cùng pool candidate, cùng quy tắc loại item đã xem, **cùng ngân sách tuning**.
5. **Không bịa số.** Số trong báo cáo sinh từ file kết quả; chưa có thì ghi "chưa có". Không đặt số cạnh kết quả
   Kaggle H&M (MAP@12, 7 ngày, dùng metadata — khác protocol hoàn toàn).

---

## 8. Tuning, Đánh Giá Cuối & Kiểm Định

### 8.1 Ngân sách tuning (như nhau cho mọi mô hình)

Chỉ trên validation của protocol chính, seed 42. Mỗi mô hình **6 cấu hình** rút ngẫu nhiên cố định (numpy seed 0)
từ lưới, cấu hình mặc định luôn là một trong 6; neural tối đa 20 epoch, patience 5. Script: `scripts/10_tune.py`.

| Mô hình | Lưới |
|---|---|
| GMF / MLP / NeuMF-Scratch | lr {1e-3, 5e-4}, negative_ratio {4, 8}, embedding_dim {32, 64}, weight_decay {0, 1e-6}, dropout {0; 0,2} (không áp dụng GMF) |
| NeuMF-Pretrained | nạp GMF, MLP tốt nhất; fine-tune lr {1e-3, 5e-4, 1e-4}, α {0,3; 0,5; 0,7} (Adam) |
| BPR-MF | embedding_dim {32, 64, 128}, lr {0,01; 0,03; 0,05}, reg {0,001; 0,005; 0,01}, epochs {20, 40} |

Tổng thời gian tuning thực tế 1,90 giờ GPU (RTX 3050 Laptop 4 GB), 57 cấu hình (kể cả các mô hình bị bỏ sau đó).

### 8.2 Cấu hình tốt nhất trên validation (NDCG@10, seed 42)

| Mô hình | Cấu hình tốt nhất | Val NDCG@10 |
|---|---|---|
| NeuMF-Scratch | lr 5e-4, neg 4, d 64, wd 1e-6, dropout 0,2 | 0,01107 |
| NeuMF-Pretrained | GMF d64 + MLP d32; lr 1e-4, α 0,3, neg 8, wd 0 | 0,00913 |
| BPR-MF | d 32, lr 0,03, reg 0,005, 20 epoch | 0,00912 |
| GMF | lr 5e-4, neg 4, d 64, wd 0 | 0,00843 |
| MLP | lr 1e-3, neg 8, d 32, wd 0, dropout 0,2 | 0,00837 |

Nguồn: `audit/best_configs.json`. Số val của cấu hình tốt nhất lạc quan (chọn trên chính val). Pretrain không
giúp trên dữ liệu này (Pretrained < Scratch trên val).

**Mô hình lai được chọn theo val** (PREREG mục 7): **NeuMF-Scratch**.

### 8.3 Kiểm định (PREREG mục 6)

- Per-user NDCG@10 trung bình qua 3 seed → **Wilcoxon signed-rank** paired theo user + **paired bootstrap** CI 95%
  (10.000 lần, seed 0). Không dùng Wilcoxon theo seed: với n seed, p nhỏ nhất là $2/2^n$ (3 seed → 0,25; 5 seed → 0,0625), không bao giờ < 0,05.
- Họ 8 so sánh cố định, hiệu chỉnh **Holm** (α = 0,05): NeuMF-Pretrained vs {BPR-MF, MostPopular, GMF, MLP,
  NeuMF-Scratch}; NeuMF-Scratch vs {BPR-MF, GMF, MLP}.
- Chỉ viết "A tốt hơn B" khi **đồng thời**: p Holm < 0,05, CI bootstrap không chứa 0, chênh lệch tương đối ≥ 5%.
  Ngược lại: "không khác biệt có ý nghĩa". Nếu mô hình lai không vượt baseline MF đã tune, báo cáo đúng như vậy.

### 8.4 Lệch kế hoạch (đều trước mọi lần chấm test)

- EarlyFusion bỏ khỏi tuning/kiểm định vì trùng kiến trúc MLP (mục 3.5).
- NeuMF cho phép nhánh GMF và MLP khác số chiều (`gmf_dim`) để nạp được GMF/MLP tốt nhất.
- Bỏ iALS, MostPopular-Recent, CFNet, late fusion iALS + NeuMF (quyết định của nhóm). Kết quả val của chúng vẫn giữ
  trong `audit/tuning_log.csv` để minh bạch: fusion 0,01260, CFNet 0,01169, iALS 0,01141 — đều cao hơn
  NeuMF-Scratch 0,01107 trên val; không chạy test cho chúng.
- Đánh giá cuối chạy bằng `scripts/11_final.py` (thay `03 --final`) để mỗi mô hình dùng cấu hình tốt nhất riêng.

---

## 9. Kết Quả Cuối Trên Test

Protocol mốc thời gian chung, hm500k, 3 seed (42, 2024, 2025), commit `7805907`, 2.893 user test, 10.145 item trong train làm candidate.
Thời gian 64,8 phút trên RTX 3050. Số liệu: `outputs/final/summary.csv`, `outputs/final/significance.csv`.

### 9.1 Mean ± std qua 3 seed

| Mô hình | NDCG@10 | Recall@10 | HR@10 | Precision@10 | NDCG@5 |
|---|---|---|---|---|---|
| BPR-MF | **0,01062 ± 0,00009** | **0,01579 ± 0,00015** | **0,04666 ± 0,00035** | **0,00510 ± 0,00011** | **0,00811 ± 0,00045** |
| NeuMF-Pretrained | 0,01001 ± 0,00041 | 0,01443 ± 0,00081 | 0,04471 ± 0,00208 | 0,00487 ± 0,00016 | 0,00787 ± 0,00075 |
| MostPopular | 0,00998 ± 0,00000 | 0,01469 ± 0,00000 | 0,04666 ± 0,00000 | 0,00501 ± 0,00000 | 0,00799 ± 0,00000 |
| MLP | 0,00959 ± 0,00005 | 0,01382 ± 0,00074 | 0,04275 ± 0,00100 | 0,00479 ± 0,00016 | 0,00758 ± 0,00059 |
| NeuMF-Scratch | 0,00958 ± 0,00017 | 0,01404 ± 0,00072 | 0,03964 ± 0,00121 | 0,00425 ± 0,00027 | 0,00768 ± 0,00029 |
| GMF | 0,00945 ± 0,00080 | 0,01425 ± 0,00121 | 0,04252 ± 0,00419 | 0,00461 ± 0,00047 | 0,00704 ± 0,00061 |
| Random | 0,00063 ± 0,00004 | 0,00092 ± 0,00011 | 0,00300 ± 0,00040 | 0,00030 ± 0,00004 | 0,00046 ± 0,00016 |

### 9.2 Kiểm định paired theo user (NDCG@10, Holm trên 8 so sánh)

| A | B | Chênh tương đối | CI 95% bootstrap | p Wilcoxon | p Holm | Kết luận |
|---|---|---|---|---|---|---|
| NeuMF-Pretrained | BPR-MF | −5,8% | [−0,00172; 0,00055] | 0,021 | 0,168 | không khác biệt có ý nghĩa |
| NeuMF-Pretrained | MostPopular | +0,2% | [−0,00088; 0,00095] | 0,701 | 1,000 | không khác biệt có ý nghĩa |
| NeuMF-Pretrained | GMF | +5,9% | [−0,00005; 0,00119] | 0,112 | 0,787 | không khác biệt có ý nghĩa |
| NeuMF-Pretrained | MLP | +4,3% | [−0,00067; 0,00152] | 0,325 | 1,000 | không khác biệt có ý nghĩa |
| NeuMF-Pretrained | NeuMF-Scratch | +4,4% | [−0,00108; 0,00195] | 0,739 | 1,000 | không khác biệt có ý nghĩa |
| NeuMF-Scratch | BPR-MF | −9,8% | [−0,00278; 0,00070] | 0,227 | 1,000 | không khác biệt có ý nghĩa |
| NeuMF-Scratch | GMF | +1,4% | [−0,00138; 0,00164] | 0,539 | 1,000 | không khác biệt có ý nghĩa |
| NeuMF-Scratch | MLP | −0,1% | [−0,00184; 0,00181] | 0,721 | 1,000 | không khác biệt có ý nghĩa |

### 9.3 Kết luận

- **Không có so sánh nào đạt "tốt hơn"**: cả 8 đều có CI chứa 0 và p Holm ≥ 0,05.
- NeuMF (Scratch lẫn Pretrained) **không vượt** BPR-MF đã tune và ngang MostPopular — phù hợp với Rendle et al. (2020)
  và Ferrari Dacrema et al. (2019).
- Ghép GMF + MLP (NeuMF) không tốt hơn từng nhánh riêng một cách có ý nghĩa.
- Mô hình chọn theo val (NeuMF-Scratch) đứng dưới NeuMF-Pretrained trên test: thứ hạng val không giữ được trên test,
  chênh lệch giữa các mô hình nhỏ hơn nhiễu.
- Kết quả chỉ nói về mẫu hm500k và protocol này.

---

## 10. Demo (inference-only)

Web mô phỏng shop H&M (`demo/`), không train lại: nạp checkpoint, dựng lại pipeline theo config rồi **đối chiếu**
`metadata.json` của run (số users/items/interactions/split) — lệch thì báo lỗi thay vì nạp sai ID.

- **Khách hàng mới:** gợi ý rule-based (lọc theo lựa chọn + độ phổ biến train) — gắn nhãn **không phải mô hình NeuMF**.
- **Admin kiểm thử:** lịch sử mua, top-K từng mô hình, hạng item test, Hit@K/NDCG@K — chấm đúng protocol huấn luyện
  (`build_full_ranking_records`, `rank_positive`, cùng tie-break seed, xếp bằng logit). Trung bình per-user khớp
  kết quả run (sai lệch ≤ 1e-6).
- **Dashboard:** chỉ đọc file kết quả đã chạy.

---

## 11. Siêu Tham Số Mặc Định (`configs/hm500k*.yaml`)

| Nhóm | Tham số | Giá trị |
|---|---|---|
| Dữ liệu | k-core | 10 |
| | Negative ratio (train) | 4 |
| Mô hình | Embedding dim | 32 |
| | MLP layers | [64, 32, 16, 8] |
| | Dropout | 0,2 |
| | Pretrain α | 0,5 |
| Huấn luyện | Batch size | 512 |
| | Optimizer | Adam, lr = 1e-3 (pretrain và fine-tune) |
| | Weight decay | 1e-6 |
| | Max epochs | 20 |
| | Patience | 7 (tuning/final: 5) |
| Đánh giá | K | 5, 10 |
| | Tie-break seed | 2026 |
| BPR-MF | d / epochs / lr / reg | 32 / 20 / 0,03 / 0,005 |

Đánh giá cuối không dùng mặc định mà dùng cấu hình tốt nhất trên val của từng mô hình (mục 8.2).

---

## 12. Hạn Chế Đã Biết

| Hạn chế | Ghi chú |
|---|---|
| Chỉ dùng mẫu H&M | ~1,6% dữ liệu (500k/31,8M dòng), lấy theo khách hàng, giữ đủ lịch sử |
| k-core = 10 | Thiên về khách mua nhiều; k = 5 vượt RAM 16 GB khi Full Ranking |
| Dữ liệu thưa | 201.801 cặp train, 7.519 user; mô hình neural quá khớp sau 1–9 epoch |
| Khoảng cách train–test | Test cách train 4 tuần (val nằm giữa, không đưa vào train) |
| k-core lọc trên toàn bộ dữ liệu | Kể cả giai đoạn val/test — rò rỉ nhỏ, áp dụng như nhau cho mọi mô hình |
| Timestamp theo ngày | Item test có thể mua cùng ngày (cùng giỏ) với item trong train — như nhau cho mọi mô hình |
| Leave-one-out rò rỉ tương lai | Lý do protocol chính là mốc thời gian chung (mục 5.1) |
| Full Ranking trên H&M đầy đủ | Không khả thi trên CPU/GPU 4 GB |
| ItemKNN không chạy | 10.345 item > ngưỡng ma trận dày 5.000 |
| GPU không tất định | cuDNN trên GPU khác có thể lệch nhẹ số GMF/MLP/NeuMF; kết luận thống kê mới là thứ cần giữ |
| Độ trễ Top-K (R7) | Đo bằng `scripts/14_secondary.py` (p50/p95 trên CPU, cùng lượt với phân tích phụ head/tail, cold/warm, beyond-accuracy, Sampled-99); chưa có số cho tới khi chạy notebook Colab |

---

## 13. Tài Liệu Tham Khảo Chính


- He, X., Liao, L., Zhang, H., Nie, L., Hu, X., & Chua, T.-S. (2017). Neural Collaborative Filtering. *WWW*. https://arxiv.org/abs/1708.05031 — code gốc: github.com/hexiangnan/neural_collaborative_filtering
- Rendle, S., Freudenthaler, C., Gantner, Z., & Schmidt-Thieme, L. (2009). BPR: Bayesian Personalized Ranking from Implicit Feedback. *UAI*.
- Rendle, S., Krichene, W., Zhang, L., & Anderson, J. (2020). Neural Collaborative Filtering vs. Matrix Factorization Revisited. *RecSys*. https://arxiv.org/abs/2005.09683
- Ferrari Dacrema, M., Cremonesi, P., & Jannach, D. (2019). Are We Really Making Much Progress? *RecSys*. https://arxiv.org/abs/1907.06902
- Krichene, W., & Rendle, S. (2020). On Sampled Metrics for Item Recommendation. *KDD*. https://dl.acm.org/doi/10.1145/3394486.3403226
- Meng, Z., McCreadie, R., Macdonald, C., & Ounis, I. (2020). Exploring Data Splitting Strategies for the Evaluation of Recommendation Models. *RecSys*.
- Rendle, S., Krichene, W., Zhang, L., & Koren, Y. (2022). Revisiting the Performance of iALS on Item Recommendation Benchmarks. *RecSys*. https://arxiv.org/abs/2110.14037
- Xue, H.-J., Dai, X., Zhang, J., Huang, S., & Chen, J. (2017). Deep Matrix Factorization Models for Recommender Systems. *IJCAI*.
- Deng, Z.-H., Huang, L., Wang, C.-D., Lai, J.-H., & Yu, P. S. (2019). DeepCF: A Unified Framework of Representation Learning and Matching Function Learning in Recommender System. *AAAI*. https://arxiv.org/abs/1901.04704
- Vargas, S., & Castells, P. (2011). Rank and Relevance in Novelty and Diversity Metrics for Recommender Systems. *RecSys*.
- RecBole — NeuMF: https://recbole.io/docs/user_guide/model/general/neumf.html
- Kaggle — H&M Personalized Fashion Recommendations: https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations
