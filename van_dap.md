# Chuẩn bị vấn đáp — Mô hình khuyến nghị lai NeuMF trên dữ liệu H&M

Tài liệu trả lời 17 điểm góp ý của giảng viên trong buổi họp. Mỗi mục gồm:

- **Hỏi** — câu hỏi dự kiến;
- **Trả lời** — ý chính để nói (1–2 phút);
- **Bằng chứng** — file trong repo hoặc mục trong báo cáo để mở ra khi cần;
- **Phải thừa nhận** — điểm yếu, nói thẳng, không né.

Số liệu lấy từ `neumf_project/outputs/final/` (lần chấm test 29/09/2026, sau khi huấn luyện lại trên train ∪ val) và
`neumf_project/audit/`. Số hình, bảng, mục theo bản `Report DACNTT/main.pdf` hiện tại.

> **Trước khi vấn đáp:** toàn bộ số liệu sẽ được chạy lại một lần trên commit cuối (`python run.py final`, đăng ký
> trước ở PREREG mục 8, ngày 02/10/2026), kèm phần mở rộng late fusion + ItemKNN/UserKNN (PREREG mục 9). Chạy xong,
> `python run.py check-report` liệt kê dòng nào trong file này còn ghi số cũ. Chạy trên đúng máy RTX 3050 đã dùng
> ngày 29/09 thì số của 7 mô hình chính kỳ vọng **trùng hoàn toàn**.

> **Thông điệp xuyên suốt:** dữ liệu đúng → đánh giá đúng → rồi mới so sánh mô hình. Đề tài đã làm theo đúng thứ tự
> này: chia theo thời gian, không đưa nhãn test vào huấn luyện, khoá tập test, cùng ngân sách tinh chỉnh cho mọi mô
> hình. Kết quả: mô hình lai NeuMF **không** tốt hơn có ý nghĩa thống kê so với MF đã tinh chỉnh — và đề tài báo cáo
> đúng như vậy.

---

## Phương án đã chốt — đối chiếu luận án của GVHD, đề cương và tài liệu gốc

Nguồn đối chiếu:

- **Luận án của GVHD:** Hồ Thị Linh (2023), *Multi-Source Integration for Recommendation Systems*, luận án tiến sĩ,
  ĐH Tôn Đức Thắng (`tai_lieu/10. Hồ Thị Linh - Toàn văn LATS.pdf`). Số trang dưới đây là số trang in trong luận án.
- **Đề cương sơ bộ và đề cương chi tiết** — đã xóa khỏi `tai_lieu/`; nội dung đề cương được trích dẫn trực tiếp trong
  báo cáo và trong file này.
- **Tài liệu gốc** mà luận án trích: K. Liu et al. (2018), Atrey et al. (2010), Burke (2002). Ba nguồn này và chính luận
  án đã được thêm vào danh mục tài liệu tham khảo của báo cáo.

**Cách dùng:** khi vấn đáp, dùng đúng thuật ngữ trong cột "Đề tài dùng". Báo cáo đã được sửa cho thống nhất với cột này.

| Vấn đề | Luận án GVHD | Đề tài dùng |
|---|---|---|
| Early fusion | Mục 1.1.2.2 (tr. 15) và 5.3 (tr. 103): nối đặc trưng/biểu diễn của các view rồi **một** mô hình dự đoán, p = h([v₁; …; v_m]). Chương 4: vector MF từ Utility Matrix + vector BERT/TF-IDF → nối → MLP | **NeuMF** (cả Scratch và Pretrained): nối vector nhánh MF (GMF, p ⊙ q) với vector nhánh DNN (MLP) → lớp dự đoán chung, học chung |
| Late fusion | Mục 1.1.2.2 (tr. 16): mỗi view một mô hình dự đoán riêng, gộp đầu ra bằng F (trung bình, bỏ phiếu, mô hình học), p = F(h₁(v₁), …, h_m(v_m)). Chương 3: gộp điểm của content-based, UserKNN, ItemKNN bằng max/min/trung bình hoặc MLP | **Late Fusion GMF + MLP**: w·minmax(GMF) + (1−w)·minmax(MLP), hai mô hình huấn luyện riêng, w chọn trên val (w = 0,1); thêm biến thể BPR-MF + MLP (w = 0,3). Báo cáo mục 2.3.4 (công thức 2.15, Hình 2.2) và mục 4.5. Mô hình B (iALS + NeuMF-Scratch, chỉ có số validation) trộn MF với *chính mô hình lai NeuMF* — **không** được gọi là late fusion MF + DNN |
| Không phải fusion | — | **MLP đứng riêng** = mô hình DNN thuần (đối chứng bỏ nhánh MF). Lớp `EarlyFusionModel` trong code trùng MLP, không gọi là early fusion |
| "Mô hình lai" | Tr. 11, theo Burke (2002): kết hợp nhiều kỹ thuật gợi ý; 7 kiểu (weighted, switching, mixed, feature combination, feature augmentation, cascade, meta-level). Chương 3 gọi "hybrid" là **gộp điểm của nhiều mô hình riêng** (tức late fusion) | Chữ "lai" của đề tài dựa vào **tên đề tài** và **NeuMF của He et al. (2017)**: kết hợp MF với DNN trong một mô hình (đề cương sơ bộ: "mô hình lai Matrix Factorization và Deep Neural Network (NeuMF)"). **Không** viện dẫn Burke cho NeuMF; nghĩa "hybrid" của Burke và chương 3 tương ứng với phía late fusion |
| Ma trận user–item | "Utility Matrix" (tr. 1, 36–37); MF phân rã R ≈ P·Qᵀ, r̂ = p_u · q_i (tr. 37) | "Ma trận tương tác (Utility Matrix)" |
| Lọc cộng tác | Tr. 10, 55–58: memory-based (UserKNN — Algorithm 3, ItemKNN — Algorithm 4) và model-based (MF) | Mô hình chính là model-based; memory-based có **UserKNN, ItemKNN** (bản thưa top-k, báo cáo mục 2.1.2, công thức 2.2–2.3) làm baseline mở rộng; demo hiện "10 khách tương đồng nhất" theo UserKNN (Hình 3.4) — mục 3 dưới đây |
| Độ đo | Mục 2.1.2 (tr. 34–36): MAE/RMSE/NMAE cho rating; Precision/Recall/F1; top-N: Hit rate (leave-one-out, top 10) và ARHR. **Không có NDCG** | Dữ liệu là phản hồi ẩn, không có rating → không dùng MAE/RMSE. Dùng HR@K (= hit rate), Precision/Recall@K (đúng định nghĩa tp/fp/fn), NDCG@K (cùng tinh thần ARHR — mục 6) |
| Chia dữ liệu | Ngẫu nhiên 80/20, lấy 20% train làm validation (tr. 63, 86); hit rate theo leave-one-out (tr. 36) | Mốc thời gian chung (chặt hơn, không rò rỉ tương lai); leave-one-out giữ làm giao thức phụ |
| Transformer, BERT (gợi ý ở buổi họp) | Chương 5: Transformer encoder hợp nhất nhiều view theo kiểu early fusion (không phải mô hình chuỗi); BERT trích vector từ review/mô tả sản phẩm | Ngoài phạm vi CF thuần. H&M có mô tả sản phẩm (`articles.csv`) nên đây là hướng mở rộng tự nhiên, đã ghi ở báo cáo mục 2.4.2 và 5.3 (mục 10 dưới đây) |

**Lệch so với đề cương — phải nói được nếu bị hỏi:**

| Đề cương hứa | Thực tế | Cách trả lời |
|---|---|---|
| Dữ liệu DataCo (ghi là "nguồn tham khảo đề xuất") | H&M | Dữ liệu giao dịch thật, rất thưa, có thời gian; lý do ở báo cáo mục 1.1.1 |
| Chia leave-one-out | Mốc thời gian chung; leave-one-out chỉ làm giao thức phụ | Leave-one-out rò rỉ tương lai (báo cáo mục 3.2.5, Meng et al. 2020) |
| Baseline Item-based CF, ALS | ItemKNN bản dày cũ không chạy (ma trận 10.345 × 10.345 vượt bộ nhớ) → đã viết lại bản thưa top-k, thêm UserKNN; tune trên val (ItemKNN 0,01217, UserKNN 0,01340 — **cao hơn** NeuMF-Scratch 0,01107) và chấm test trong lần chạy lại (PREREG mục 9, báo cáo mục 4.5). iALS chỉ có số validation (bị loại trước khi chấm test) | **Thừa nhận** bổ sung sau khi đã xem test: đăng ký trước khi chấm, họ kiểm định riêng, báo cáo là kết quả mở rộng |
| Ablation: bỏ GMF, bỏ MLP, số chiều embedding, số lớp MLP, tỉ lệ negative | Có: bỏ từng nhánh (GMF, MLP), số chiều embedding và tỉ lệ negative (qua tinh chỉnh). **Chưa có:** số lớp MLP | Đã ghi hạn chế ở báo cáo mục 4.4.3 và 5.2 |
| K = 5/10/20 | K = 5, 10; K = 20 bổ sung (Bảng 4.3) | NDCG@10 là chỉ số chính đã đăng ký trước; K = 20 tính lại từ hạng đã lưu, chỉ mô tả |
| Cold-start: đo nhóm ít tương tác; thử thêm đặc trưng Category/Department | Có đo cold/warm và head/tail; **chưa** thử đặc trưng nội dung | Ngoài phạm vi CF thuần; hướng phát triển ở mục 5.3 |
| Biến thể phản hồi có trọng số (theo doanh thu) | Chưa làm (code có chế độ `weighted_confidence` nhưng chưa báo cáo) | Hướng mở rộng |
| Demo FastAPI + Streamlit + Docker | FastAPI + giao diện HTML, dùng đúng mô hình của đánh giá cuối; Docker chưa kiểm tra đầy đủ | Chức năng tương đương; Docker đã ghi ở mục 5.3, 5.4 |
| Báo cáo 6 chương | 5 chương | Chương "cài đặt và thực nghiệm" và chương "kết quả và đánh giá" được gộp thành Chương 4 |
| Kỳ vọng NeuMF tốt hơn các thành phần | Kết quả âm (0/8 so sánh có ý nghĩa) | Đề cương sơ bộ (mục 6) đã dự liệu: "không tự ý chỉnh sửa số liệu… phân tích nguyên nhân khách quan cũng là một đóng góp học thuật" |

---

## 0. Số liệu cần thuộc

| Nội dung | Giá trị |
|---|---|
| Dữ liệu gốc | H&M Personalized Fashion Recommendations: 31,8 triệu giao dịch, 20/09/2018 → 22/09/2020 |
| Mẫu hm500k | 500.269 giao dịch của 21.599 khách (lấy theo khách hàng, giữ trọn lịch sử) |
| Sau gộp cặp + k-core 10 | 7.519 user × 10.345 item, 220.292 cặp, mật độ 0,283% |
| Chia theo mốc thời gian | train < 01/07/2020 ≤ val < 29/07/2020 ≤ test (đến 22/09/2020) |
| Train / Val / Test | 201.801 / 7.057 / 9.229 cặp; test có 2.996 user, trung bình 3,08 món đúng mỗi user |
| Dữ liệu huấn luyện lại trước khi chấm test | train ∪ val: 209.212 cặp, 7.515 user, 10.216 item (= tập ứng viên khi chấm test) |
| Mô hình | Random, Most Popular, BPR-MF (baseline); GMF (chỉ MF), MLP (chỉ DNN); NeuMF-Scratch, NeuMF-Pretrained (lai MF + DNN, early fusion) |
| Tinh chỉnh | 6 cấu hình mỗi mô hình, chỉ trên validation; 57 cấu hình chính (1,9 giờ GPU) + 34 cấu hình mở rộng (ItemKNN, UserKNN 6 mỗi mô hình; late fusion quét 11 giá trị w mỗi biến thể) |
| Mở rộng trên validation (NDCG@10) | UserKNN 0,01340 · ItemKNN 0,01217 · NeuMF-Scratch 0,01107 · Late Fusion GMF + MLP 0,01005 · BPR-MF + MLP 0,00972 |
| NDCG@10 trên test (TB 3 seed) | BPR-MF 0,01007 · NeuMF-Pretrained 0,00957 · MLP 0,00931 · Most Popular 0,00917 · NeuMF-Scratch 0,00910 · GMF 0,00907 · Random 0,00065 |
| HR@10 trên test | BPR-MF 4,65% · NeuMF-Pretrained 4,35% · Most Popular 4,34% · Random 0,31% |
| Kiểm định | 0/8 so sánh đạt "tốt hơn"; gần ngưỡng nhất: NeuMF-Pretrained vs GMF, p = 0,043 trước hiệu chỉnh, p Holm = 0,342 |
| Sampled-99 (chỉ đối chiếu) | NDCG@10 ≈ 0,15, HR@10 ≈ 0,26 — cao gấp 15–17 lần Full Ranking |
| Độ trễ trên CPU | NeuMF-Pretrained p50 1,1 ms, p95 1,6 ms; BPR-MF 0,6 / 0,8 ms (≈ 10.182 ứng viên mỗi yêu cầu) |

---

## 1. "Kết quả cao bất thường" và rò rỉ dữ liệu

### 1.1 Kết quả hiện tại có cao bất thường không?

**Trả lời:** Không. NDCG@10 cao nhất chỉ 0,01007 (BPR-MF), HR@10 = 4,65%. Mức này hợp lý với bài toán khó: mỗi user
test có khoảng 3 món đúng giữa khoảng 10.200 ứng viên, chỉ tính món *mới* (chưa từng mua), dự đoán cho 8 tuần sau.
Chọn ngẫu nhiên kỳ vọng HR@10 ≈ 10 × 3,08 / 10.216 ≈ 0,30% — khớp số đo của Random (0,31%). Các mô hình học được cao
hơn ngẫu nhiên khoảng 15 lần, không phải hàng trăm lần.

Nếu số "cao" thầy/cô thấy trước đây là:

- **Sampled-99** — xếp 1 món đúng giữa 100 ứng viên (giao thức của bài NCF gốc): NDCG@10 ≈ 0,15, HR@10 ≈ 0,26
  (Bảng 4.7). Đề tài chỉ dùng để đối chiếu, không dùng để kết luận.
- **Lát cắt 100k dòng cũ** — chỉ 3 ngày dữ liệu, 1.743 user × 1.080 item, NDCG@10 khoảng 0,04. Phương án này đã bỏ
  (`neumf_project/pham_vi_du_an.md` mục 4.4).

**Bằng chứng:** Bảng 4.2, 4.7; `outputs/final/summary.csv`, `outputs/final/sampled99.csv`.

### 1.2 Train/Test được chia thế nào?

**Trả lời:** Chia theo **một mốc thời gian chung** cho mọi user — không chia ngẫu nhiên, không chia riêng từng user.
Mỗi cặp (user, item) được xếp theo ngày mua *đầu tiên*: train < 01/07/2020 ≤ val < 29/07/2020 ≤ test (đến
22/09/2020). Val chỉ giữ user/item đã có trong train; test chỉ giữ user/item đã có trong train ∪ val (mô hình thuần ID
không chấm điểm được thực thể chưa từng thấy). Một user có thể có nhiều món đúng; món đã mua trước đó không tính là
đích.

**Bằng chứng:** `src/data_pipeline/splitting.py` (`global_temporal_split`), `configs/hm500k_global.yaml`, Bảng 3.3
(mục 3.2.5).

### 1.3 Dữ liệu test có xuất hiện trong training không?

**Trả lời:** Không. Có ba lớp kiểm tra:

1. `assert_disjoint_splits`: train ∩ val = train ∩ test = val ∩ test = ∅ ở cấp cặp (user, item), chạy mỗi lần chia.
2. Test tự động trên dữ liệu thật (`tests/test_no_leakage_real_data.py`): ngày lớn nhất của train nhỏ hơn mốc val,
   ngày lớn nhất của val nhỏ hơn mốc test; user/item của val thuộc train, của test thuộc train ∪ val.
3. **Khoá tập test:** chỉ `scripts/11_final.py`, `scripts/14_secondary.py` và `scripts/17_extension.py` được chấm
   test. Script từ chối chạy nếu `audit/PREREG.md` chưa commit, thiếu `--reason` hoặc code có thay đổi chưa commit
   (17 còn đòi PREREG có mục 9); mỗi lần chấm ghi một dòng vào `audit/test_access_log.csv`. Mọi lựa chọn siêu tham số
   chỉ dựa trên validation (`audit/tuning_log.csv`: 91 dòng = 57 chính + 34 mở rộng, toàn bộ là số validation).

### 1.4 Preprocessing có dùng thông tin của toàn dataset không?

**Trả lời:** Có **một** chỗ, và đã ghi là hạn chế: **lọc k-core** (giữ user/item có ít nhất 10 cặp) chạy trên toàn bộ
mẫu hm500k trước khi chia. Vì vậy việc một user/item có được giữ lại hay không phụ thuộc cả vào tương tác trong giai
đoạn val/test. Đây là rò rỉ ở khâu *chọn tập dữ liệu*, không đưa nhãn test vào huấn luyện, và tác động như nhau lên mọi
mô hình. Ánh xạ ID cũng làm trên toàn mẫu nhưng không mang thống kê nào.

Mọi thống kê khác chỉ tính trên dữ liệu huấn luyện của bước tương ứng (train khi chấm val, train ∪ val khi chấm test):
độ phổ biến của Most Popular, tập negative, nhóm head/tail, nhóm cold/warm, trọng số confidence.

**Bằng chứng:** `src/data_pipeline/preprocessing.py` (`build_interactions`: gộp → k-core → re-index, trước khi chia);
các test `tests/test_pure_cf.py::test_popularity_statistics_in_03_use_train_df`,
`tests/test_pure_cf.py::test_confidence_weight_scale_fitted_on_train_only`,
`tests/test_evaluation.py::test_head_fraction_uses_train_only_counts`; báo cáo mục 4.6, ý (v).

**Phải thừa nhận:** muốn loại hẳn rò rỉ này thì phải chạy k-core chỉ trên dữ liệu trước mốc test. Việc đó làm thay đổi
tập dữ liệu nên chưa làm.

### 1.5 Model có được train lại trên toàn bộ dữ liệu trước khi test không?

**Trả lời:** Có — trên **toàn bộ dữ liệu trước mốc test** (train ∪ val, mọi cặp trước 29/07/2020), **không** gồm test.
Quy trình cho mỗi seed:

1. Train trên train, early stopping theo NDCG@10 trên val → lấy số epoch tốt nhất.
2. Train lại từ đầu trên train ∪ val đúng số epoch đó.
3. Chấm test.

Most Popular và BPR-MF cũng được khớp trên train ∪ val. Test không bao giờ được dùng để dừng sớm hay chọn mô hình.
Lý do train lại: nếu bỏ trống 4 tuần sát kỳ dự đoán, NDCG@10 (đo trên validation) của Most Popular và BPR-MF giảm
khoảng 17–19%.

**Phải thừa nhận:** bước train lại được thêm **sau** lần chấm test đầu tiên (27/09). Việc này đã được ghi là lệch kế
hoạch (PREREG mục 8; báo cáo mục 3.6 và phần tóm tắt). Lần chấm đầu cho cùng kết luận: BPR-MF cao nhất, 0/8 so sánh có
ý nghĩa. Sau đó còn một lần chạy lại toàn bộ trên commit cuối (đăng ký trước ngày 02/10, cùng cấu hình — để mọi số
truy vết về một commit; kỳ vọng ra đúng cùng số vì huấn luyện ở chế độ GPU tất định).

**Bằng chứng:** `scripts/11_final.py`; `outputs/final/seed*/results.json` (trường `best_epoch`, `refit_train_time_s`);
`audit/test_access_log.csv` (trước lần chạy lại có 7 dòng: 3 seed ngày 27/09, 3 seed ngày 29/09, 1 lần phân tích phụ;
lần chạy lại thêm 5 dòng: 3 seed, phần mở rộng, phân tích phụ).

### 1.6 Positive/negative samples được tạo thế nào?

**Trả lời:**

- **Positive:** mỗi cặp (user, item) đã mua trong dữ liệu huấn luyện, nhãn 1. Mua nhiều lần vẫn tính một cặp.
- **Negative khi huấn luyện:** với mỗi positive, lấy ngẫu nhiên đều `neg_ratio` món (4 hoặc 8 tuỳ cấu hình tốt nhất)
  trong số món user **chưa mua trong dữ liệu huấn luyện**, lấy lại mới mỗi epoch. Bộ lấy mẫu không bao giờ đọc val/test.
  BPR-MF lấy cặp (món đã mua i, món chưa mua j).
- Một negative có thể là món user sẽ mua trong tương lai. Đó là bản chất của phản hồi ẩn ("chưa mua" ≠ "không thích"),
  không phải rò rỉ, vì bộ lấy mẫu không nhìn vào dữ liệu test.
- **Khi đánh giá:** không lấy mẫu negative. Ứng viên = mọi món trong dữ liệu huấn luyện trừ món user đã mua; món đúng
  luôn nằm trong ứng viên (Full Ranking).

**Bằng chứng:** `src/data_pipeline/negative_sampling.py`, `src/data_pipeline/dataset.py` (`TrainDataset.resample`);
các test `tests/test_data_pipeline.py::test_negative_sampler_never_returns_positive`,
`tests/test_data_pipeline.py::test_train_dataset_never_labels_positive_as_negative`,
`tests/test_evaluation.py::test_full_ranking_excludes_seen_and_keeps_positive`.

### 1.7 Trường hợp lấy lần mua cuối làm test (leave-one-out)

**Trả lời:** Đề tài có giao thức phụ leave-one-out (`configs/hm500k.yaml`) và tách **trước khi train**: sắp lịch sử
từng user theo thời gian, món cuối → test, món áp chót → val, phần còn lại → train. Mô hình không bao giờ thấy món cuối.

Nhưng ngay cả khi tách đúng, leave-one-out vẫn rò rỉ **tương lai của người khác**: trên hm500k, trung bình 11,2% tương
tác trong train xảy ra *sau* ngày của món test của user đó, và 60,9% user có món val và món test mua cùng một ngày. Vì
vậy leave-one-out chỉ dùng để đối chiếu với bài NCF gốc, không dùng để chọn mô hình. Giao thức chính là mốc thời gian
chung (Meng et al., 2020).

**Bằng chứng:** `src/data_pipeline/splitting.py` (`temporal_leave_one_out`); các test
`tests/test_data_pipeline.py::test_temporal_loo_and_no_overlap`,
`tests/test_no_leakage_real_data.py::test_loo_split_is_temporal_per_user`; báo cáo mục 3.2.5.

---

## 2. Bộ test chuẩn chung cho mọi mô hình

**Hỏi:** Các mô hình có được đánh giá trên cùng điều kiện không?

**Trả lời:** Có. Một bộ test cố định cho cả 7 mô hình:

- cùng 9.229 cặp đúng của 2.996 user;
- cùng tập ứng viên (10.216 món, trừ món user đã mua);
- cùng quy tắc phá hoà điểm tất định (seed 2026);
- cùng 3 seed (42, 2024, 2025);
- cùng ngân sách tinh chỉnh (6 cấu hình mỗi mô hình).

Kết quả từng user được lưu ở `outputs/final/seed*/results_per_user.csv`, nhờ đó làm được kiểm định theo cặp (cùng một
user, hai mô hình).

**Đã có trên bộ test này:** Baseline (Random, Most Popular), MF (BPR-MF, GMF), DL (MLP), Hybrid early fusion
(NeuMF-Scratch, NeuMF-Pretrained). **Mở rộng** (cùng bộ test, chấm trong lần chạy lại): late fusion GMF + MLP và BPR-MF +
MLP (dùng đúng GMF, MLP, BPR-MF đã huấn luyện lại của từng seed), ItemKNN, UserKNN — Bảng 4.9–4.10, mục 4.5.

**Phải thừa nhận:** bốn mô hình mở rộng được thêm **sau** khi đã xem test (đăng ký trước khi chấm, họ 7 so sánh với
Holm riêng, không thay kết luận chính); phép trộn điểm iALS + NeuMF chỉ có số trên validation (mục 12–13).

---

## 3. Top-K người dùng tương đồng và Top-K sản phẩm khuyến nghị

**Hỏi:** Top-K trong kết quả là Top-K gì? 10 user tương đồng nhất của user A được xác định thế nào?

**Trả lời:**

- Mọi chỉ số @K trong báo cáo (K = 5, 10) là **Top-K sản phẩm khuyến nghị**: chấm điểm mọi món A chưa mua, sắp giảm
  dần, lấy K món đầu.
- Các mô hình của đề tài (BPR-MF, GMF, MLP, NeuMF) là **CF dựa trên mô hình** (model-based), **không có bước tìm Top-K
  láng giềng**. Độ tương đồng giữa các user nằm ngầm trong vector ẩn: hai user mua nhiều món giống nhau sẽ được huấn
  luyện để chấm cao cùng các món đó, nên vector của họ gần nhau và danh sách gợi ý giống nhau.
- Top-K láng giềng thuộc về **CF dựa trên bộ nhớ** (UserKNN/ItemKNN) — đúng như Algorithm 3 (UserKNN) và Algorithm 4
  (ItemKNN) trong luận án của cô (tr. 58). Đề tài **đã cài đặt cả hai** (`src/baselines/neighborhood.py`, báo cáo mục
  2.1.2, công thức 2.2–2.3):
  - Độ tương đồng cosine trên vector mua nhị phân, có hệ số co: sim(a, b) = |món chung| / (√(|món của a| · |món của b|)
    + shrink).
  - Mỗi user giữ k láng giềng gần nhất (ma trận thưa); k và shrink chọn trên validation: **UserKNN k = 200, shrink = 0**.
  - Điểm của món i cho A = tổng độ tương đồng của các láng giềng đã mua i; xếp hạng → Top-K sản phẩm.
- **Minh hoạ trực tiếp "10 user tương đồng nhất của A"**: demo, màn hình Admin, thẻ cuối (Hình 3.4 trong báo cáo;
  API `GET /api/users/{id}/neighbors`) — mỗi láng giềng có độ tương đồng, số món mua chung, ví dụ món chung và láng
  giềng đó đã mua sản phẩm đích (test) nào của A, tức là vì sao UserKNN gợi ý món đó.
- Trên validation, UserKNN đạt NDCG@10 = 0,01340 — **cao nhất** trong mọi mô hình đã tinh chỉnh (NeuMF-Scratch 0,01107);
  số test có trong lần chạy lại (báo cáo mục 4.5).

**Phải thừa nhận:** UserKNN/ItemKNN được thêm sau khi đã xem test của 7 mô hình chính (bản ItemKNN dày cũ không chạy
được vì ma trận 10.345 × 10.345), nên kết quả của chúng là kết quả mở rộng với họ kiểm định riêng. Nếu chúng tốt hơn
NeuMF trên test, đó là thêm một bằng chứng cho kết luận "baseline đơn giản được tune tốt không thua mô hình học sâu"
(Ferrari Dacrema et al., 2019).

---

## 4. Collaborative Filtering hoạt động thế nào

**Hỏi:** Có phải lấy sản phẩm người khác đã mua để đề xuất trực tiếp không?

**Trả lời:** Không. Có hai cách, cùng đi tới Top-K món A chưa mua:

| Bước | CF dựa trên bộ nhớ (UserKNN) | CF dựa trên mô hình (đề tài) |
|---|---|---|
| 1 | Tìm các user có lịch sử mua giống A (độ tương đồng từ món mua chung) | Học vector ẩn cho mọi user và item từ toàn bộ lịch sử mua |
| 2 | Lấy các món láng giềng đã mua mà A chưa mua | Ứng viên = mọi món A chưa mua |
| 3 | Dự đoán mức thích = tổng có trọng số theo độ tương đồng | Dự đoán ŷ(A, i) bằng mô hình (tích vô hướng, MLP hoặc NeuMF) |
| 4 | Xếp hạng → Top-K | Xếp hạng → Top-K |

Với mô hình, "user tương đồng" và "món họ đã mua" được mã hoá vào vector: món i được chấm cao cho A khi vector của i khớp
vector của A, mà vector của A được kéo về phía các món những user giống A đã mua.

**Lịch sử thay đổi thì sao?** Với UserKNN, tập láng giềng đổi ngay khi lịch sử đổi. Với mô hình của đề tài, vector user
chỉ cập nhật khi **huấn luyện lại**. Chính vì vậy, trước khi chấm test mô hình được huấn luyện lại trên train ∪ val để
dùng lịch sử mới nhất.

---

## 5. Cold Start

**Hỏi:** User mới chưa có lịch sử thì sao?

**Trả lời:**

- **Phạm vi:** mô hình chính chỉ áp dụng cho user/item đã có lịch sử (sau k-core 10, mỗi user có ít nhất 10 món khác
  nhau trong toàn bộ dữ liệu). Cold-start tuyệt đối nằm ngoài phạm vi, đã ghi rõ ở mục 1.2.1, 4.6 và 5.2 của báo cáo.
  Đề tài **không** khẳng định đã giải quyết cold-start.
- **Demo:** khách mới nhận gợi ý theo luật — lọc theo lựa chọn của khách (khu vực mua sắm, nhóm tuổi…) rồi xếp theo độ
  phổ biến — và giao diện ghi rõ "không phải mô hình NeuMF". Đúng hướng thầy/cô gợi ý: dùng sản phẩm phổ biến trước,
  cá nhân hoá sau.
- **Thực nghiệm cold-start tương đối:** ở nhóm 20% user ít tương tác nhất (555 user test), Most Popular đạt NDCG@10 cao
  nhất (0,01053), cao hơn mọi mô hình cá nhân hoá. Đây là bằng chứng cho chiến lược "người ít lịch sử thì dùng độ phổ
  biến" (phân tích mô tả, chưa kiểm định).

**Bằng chứng:** `neumf_project/demo/backend/onboarding.py`, `onboarding_config.yaml`; Bảng 4.5.

---

## 6. NDCG và các chỉ số

### 6.1 Công thức (relevance nhị phân, một user có thể nhiều món đúng)

Ký hiệu: T_u là tập món đúng của user u trong test; r là hạng (bắt đầu từ 1) của một món đúng trong danh sách xếp hạng
toàn bộ ứng viên; hits_u là số món đúng nằm trong top-K.

| Chỉ số | Công thức cho một user | Ý nghĩa |
|---|---|---|
| HR@K | 1 nếu hits_u ≥ 1, ngược lại 0 | Có ít nhất một món đúng trong K gợi ý không |
| Precision@K | hits_u / K | Bao nhiêu phần trong K gợi ý là đúng |
| Recall@K | hits_u / (số món trong T_u) | Tìm lại được bao nhiêu phần món user thực sự mua |
| NDCG@K | DCG@K / IDCG@K | Món đúng càng ở trên càng được nhiều điểm; chuẩn hoá về [0, 1] |

- DCG@K = Σ 1 / log₂(r + 1), lấy tổng trên các món đúng có r ≤ K.
- IDCG@K = Σ 1 / log₂(j + 1) với j = 1 … min(số món đúng, K) — DCG khi mọi món đúng đứng đầu danh sách.

**Ví dụ tính tay (nên thuộc):** user có 3 món đúng nằm ở hạng 2, 7 và 40; K = 10.

- hits = 2 → HR@10 = 1; Precision@10 = 2/10 = 0,2; Recall@10 = 2/3 ≈ 0,667.
- DCG@10 = 1/log₂3 + 1/log₂8 = 0,631 + 0,333 = 0,964.
- IDCG@10 = 1/log₂2 + 1/log₂3 + 1/log₂4 = 1 + 0,631 + 0,5 = 2,131.
- NDCG@10 = 0,964 / 2,131 ≈ 0,453.

### 6.2 Code, xếp hạng, K, cách tổng hợp

- **Công thức:** `src/evaluation/metrics.py` (`multi_ranking_metrics`). Có test tính tay
  `tests/test_global_split.py::test_multi_metrics_two_relevant_items` (hạng 1 và 4, K = 3 → NDCG = 1 / (1 + 1/log₂3)),
  và test mô hình hoàn hảo cho NDCG = 1 (`tests/test_evaluation.py::test_perfect_model_hr_ndcg_one`).
- **Xếp hạng:** chấm điểm mọi ứng viên bằng **logit** (không qua sigmoid, vì sigmoid float32 bão hoà sẽ tạo điểm hoà
  giả). Hoà điểm được phá bằng một khoá tất định (seed 2026), giống nhau cho mọi mô hình —
  `src/evaluation/ranking_utils.py`, `src/evaluation/full_ranking.py`.
- **K:** K ∈ {5, 10}; chỉ số chính là **NDCG@10**, đã đăng ký trước trong PREREG.
- **Tổng hợp:** trong một seed, lấy trung bình theo user (mỗi user trọng số như nhau); sau đó báo trung bình ± độ lệch
  chuẩn qua 3 seed. Kiểm định dùng NDCG@10 của từng user lấy trung bình qua 3 seed.

### 6.3 Con số đang nói gì? (ví dụ BPR-MF)

- **NDCG@10 = 0,01007:** điểm chất lượng xếp hạng trên thang 0–1 (1 = mọi món đúng nằm đầu danh sách). Đây **không**
  phải "độ chính xác 1%". Cao gấp khoảng 15 lần Random (0,00065).
- **HR@10 = 4,65%:** cứ 100 khách thì khoảng 4–5 khách có ít nhất một món họ thực sự mua trong 8 tuần sau nằm trong 10
  gợi ý; chọn ngẫu nhiên chỉ được khoảng 0,3 khách.
- **Recall@10 = 1,53%:** 1,5% số món (mới) khách thực sự mua nằm trong top-10.
- **Precision@10 = 0,52%:** trung bình 10 gợi ý có khoảng 0,05 món đúng.
- **Vì sao số thấp:** khoảng 10.200 ứng viên, chỉ đếm món *mới*, khoảng dự đoán 8 tuần, thời trang thay đổi theo mùa.
  Điều cần quan tâm là **chênh lệch giữa các mô hình có ý nghĩa thống kê hay không**, không phải độ lớn tuyệt đối.

### 6.4 Nối với các độ đo trong luận án của cô

Luận án của cô (mục 2.1.2, tr. 34–36) dùng MAE/RMSE cho dự đoán rating, Precision/Recall/F1, và với top-N thì dùng
**Hit rate** (leave-one-out, top 10) và **ARHR** (average reciprocal hit rate); luận án không dùng NDCG.

- Dữ liệu H&M chỉ có lượt mua, **không có điểm rating**, nên MAE/RMSE không áp dụng được; bài toán là xếp hạng top-N.
- **HR@K** của đề tài chính là hit rate của luận án, mở rộng cho trường hợp một user có nhiều món đúng (trúng nếu có ít nhất
  một món).
- **Precision@K, Recall@K** dùng đúng định nghĩa tp/(tp+fp) và tp/(tp+fn) của luận án (tr. 35), với tp là số món đúng
  trong top-K.
- **NDCG@K cùng tinh thần với ARHR:** cả hai thưởng nhiều hơn khi món đúng nằm cao trong danh sách. ARHR chiết khấu theo 1/r,
  NDCG chiết khấu theo 1/log₂(r + 1) (giảm chậm hơn), và NDCG chia cho IDCG để đưa về [0, 1] khi user có nhiều món đúng.
- Lưu ý: "Precision" ở chương 3 của luận án là tỉ lệ dự đoán rating sai lệch ≤ 0,5 hoặc ≤ 1 so với thực tế — khác
  Precision@K của bài toán xếp hạng, không được đặt hai con số cạnh nhau.

---

## 7. Trình bày kết quả theo chuẩn học thuật

**Hỏi:** NDCG@10 có nhân 100 không? Các bài báo thường trình bày thế nào?

**Trả lời:**

- Các bài nền tảng (NCF — He et al., 2017; Rendle et al., 2020) ghi HR@10, NDCG@10 dạng **số thập phân** trong [0, 1].
  Một số bài khác ghi dạng % nhưng **ghi rõ đơn vị ở tiêu đề cột**.
- Báo cáo dùng số thập phân 5 chữ số, trung bình ± độ lệch chuẩn qua seed, in đậm giá trị cao nhất mỗi cột, kèm một bảng
  kiểm định riêng (Bảng 4.2, 4.4; phần mở rộng Bảng 4.9, 4.10).
- NDCG không phải tỉ lệ phần trăm. Nếu muốn nhân 100 thì phải ghi "NDCG@10 (×100)". HR, Recall, Precision là tỉ lệ nên
  có thể ghi % (HR@10 = 4,65%).
- **Khoảng giá trị phụ thuộc giao thức:**
  - Bài NCF gốc dùng leave-one-out + lấy mẫu âm nên HR@10 ≈ 0,7 trên MovieLens.
  - Với Full Ranking trên dữ liệu thương mại điện tử thưa, NDCG thường chỉ vài phần trăm. Ví dụ LightGCN (2020) báo
    NDCG@20 ≈ 0,03 trên Amazon-Book và ≈ 0,15 trên Gowalla — kiểm tra lại số trong bài gốc trước khi trích.
  - Chính đề tài cho thấy điều này: cùng mô hình, Sampled-99 cho NDCG@10 ≈ 0,15, Full Ranking chỉ ≈ 0,01 (Bảng 4.7).
- Vì vậy không đặt số của đề tài cạnh số của các bài dùng giao thức khác, cũng không so với điểm Kaggle H&M (MAP@12,
  cửa sổ 7 ngày, có dùng metadata).

**Bằng chứng:** Bảng 4.2, 4.4, 4.7; Krichene & Rendle (2020).

---

## 8. Vai trò của Matrix Factorization

**Trả lời:**

- Ma trận tương tác R có 7.519 × 10.345 ≈ 77,8 triệu ô, chỉ 220.292 ô bằng 1 (0,283%) — rất thưa.
- MF phân rã R ≈ P · Qᵀ:
  - P (7.519 × d): vector ẩn của user — sở thích.
  - Q (10.345 × d): vector ẩn của item — đặc tính.
  - d = 32 hoặc 64, nhỏ hơn rất nhiều so với số item. Điểm dự đoán ŷ_ui = p_u · q_i.
- Lợi ích:
  1. Nén ma trận thưa thành biểu diễn dày, ít chiều. BPR-MF với d = 32 chỉ có (7.519 + 10.345) × 32 ≈ 0,57 triệu tham
     số, so với 77,8 triệu ô.
  2. Suy ra điểm cho các ô trống nhờ thông tin dùng chung qua các vector.
  3. Tạo **biểu diễn** để đưa vào mạng sâu.
- Trong đề tài:
  - BPR-MF: MF tối ưu thứ tự xếp hạng theo cặp.
  - GMF: MF tổng quát — p_u ⊙ q_i rồi qua một lớp có trọng số học được; khi trọng số bằng 1 thì đúng là MF.
  - Ở NeuMF-Pretrained, vector ẩn do GMF học được chép vào nhánh GMF của NeuMF. Đây chính là bước "dùng latent vector
    của MF để kết hợp với Deep Learning".

**Bằng chứng:** báo cáo mục 2.2, 2.3; `src/baselines/classical.py` (`BPRMFBaseline`), `src/models/neumf.py` (`GMF`).

---

## 9. Mô hình Hybrid đã thực sự được xây dựng

**Hỏi:** Có thực sự xây mô hình lai không, hay chỉ chạy MF?

**Trả lời:** Có. Mô hình lai là **NeuMF** (He et al., 2017):

- Nhánh MF (GMF): φ_GMF = p_u^G ⊙ q_i^G.
- Nhánh DNN (MLP): nối [p_u^M ; q_i^M] → tháp [2d → d → d/2 → d/4], ReLU, dropout.
- Hợp nhất: ŷ_ui = σ(hᵀ [φ_GMF ; z_MLP]). Hai nhánh có bảng embedding riêng.
- Hai biến thể:
  - **NeuMF-Scratch:** khởi tạo ngẫu nhiên.
  - **NeuMF-Pretrained:** huấn luyện GMF và MLP trước, chép embedding và trọng số sang NeuMF, khởi tạo
    h = [α·h_GMF ; (1−α)·h_MLP] rồi fine-tune. α tốt nhất = 0,3.
- Cả hai được tinh chỉnh cùng ngân sách, chạy 3 seed, kiểm định với các baseline và với từng nhánh.

**Kết quả (phải nói thẳng):** mô hình lai **không** tốt hơn có ý nghĩa. NeuMF-Pretrained so với GMF +5,5%, so với MLP
+2,7%, so với BPR-MF −5,0%; cả 8 so sánh có p Holm ≥ 0,34. Kết luận này nhất quán với Rendle et al. (2020) và Ferrari
Dacrema et al. (2019). Giá trị của đề tài là một quy trình đo đáng tin cậy và một câu trả lời có bằng chứng cho câu hỏi
"lai có giúp trên dữ liệu thời trang thưa không".

**Bằng chứng:** `src/models/neumf.py` (`NeuMF.forward`, `NeuMF.load_pretrained`); Hình 2.1; Bảng 4.2, 4.4; mục 4.4.3.

---

## 10. Các mô hình Deep Learning khác (Transformer, Temporal, BERT)

**Hỏi:** Đã thử Transformer, Temporal Fusion, BERT chưa?

**Trả lời:** Chưa, và có chủ đích. Trước hết cần hiểu đúng ý của cô — theo luận án của cô:

- **Transformer** (chương 5) được dùng làm **mô hình hợp nhất nhiều view theo kiểu early fusion**: nối vector MF (từ
  Utility Matrix) với vector văn bản, cắt thành chuỗi token rồi đưa vào Transformer encoder để dự đoán. Đây không phải
  mô hình chuỗi hành vi — đúng như ghi chú ở buổi họp "có thể thử nếu không tập trung mạnh vào yếu tố thời gian".
- **BERT** (chương 4–5) dùng để **tạo vector từ văn bản** (review, mô tả sản phẩm) rồi nối với vector MF trước khi đưa vào
  mô hình dự đoán.

Vì sao đề tài chưa làm:

- Cả hai hướng đều cần **nguồn nội dung** (văn bản sản phẩm), trong khi đề tài giới hạn ở lọc cộng tác thuần (MF + DNN
  trên dữ liệu tương tác) theo đúng tên đề tài và đề cương. Đề cương chi tiết đặt đặc trưng nội dung và gợi ý theo
  chuỗi/phiên ở phần hướng phát triển.
- Nhánh DNN của đề tài là MLP, đúng đề cương và kiến trúc NCF. Một mô hình DL khác đã được thử trên validation là
  DeepCF/CFNet (NDCG@10 = 0,01169), nhưng bị loại khỏi phạm vi trước khi chấm test.

**Hướng mở rộng đúng ý cô (đã ghi ở báo cáo mục 5.3):** H&M có sẵn mô tả sản phẩm (`detail_desc` trong `articles.csv`).
Có thể làm early fusion vector ẩn của MF với vector BERT của mô tả sản phẩm (như chương 4 luận án), rồi thay MLP bằng
Transformer encoder (như chương 5), đánh giá bằng cùng giao thức không thiên lệch. Mô hình chuỗi (SASRec, BERT4Rec) là
một hướng khác, dành cho yếu tố thời gian (mục 11).

Thầy/cô đã ghi rõ phần này **không bắt buộc**; mô hình cuối phải được chọn dựa trên thực nghiệm.

---

## 11. Có dùng yếu tố thời gian không?

**Trả lời:**

- Dữ liệu **có** timestamp (`t_dat`, theo ngày).
- Thời gian được dùng để **chia dữ liệu** (mốc chung, chống rò rỉ) và để quyết định **huấn luyện lại trên dữ liệu mới
  nhất**: bỏ trống 4 tuần gần nhất làm NDCG@10 giảm 17–19% trên validation, tức sở thích có trôi theo thời gian.
- Thời gian **không** phải đặc trưng đầu vào của mô hình. Thử nghiệm đơn giản với độ phổ biến theo cửa sổ gần
  (MostPopular-Recent, trên validation): cửa sổ 7 / 14 / 28 / 56 ngày cho NDCG@10 lần lượt 0,0053 / 0,0057 / 0,0068 /
  0,0085. Cửa sổ càng ngắn càng kém, tức xu hướng ngắn hạn đơn thuần chưa đủ giải thích hành vi mua.
- Timestamp chỉ theo ngày, không có giờ; nhiều món được mua cùng giỏ trong cùng một ngày, nên thứ tự trong ngày không
  xác định. Điều này hạn chế giá trị của mô hình chuỗi chi tiết.
- Kết luận: không cố đưa Temporal Fusion vào; gợi ý theo thời gian là hướng mở rộng.

**Bằng chứng:** `audit/tuning_log.csv` (4 dòng `popularity_recent`); `audit/PREREG.md` mục 8.

---

## 12–13. Early Fusion và Late Fusion

**Thuật ngữ đã chốt** theo luận án của cô (mục 1.1.2.2, 5.3) và các nguồn gốc (K. Liu et al. 2018; Atrey et al. 2010).
Báo cáo mục 2.3.4 đã viết lại theo đúng định nghĩa này, kèm **Hình 2.2** so sánh hai cách hợp nhất:

| Kiểu hợp nhất | Định nghĩa | Trong đề tài | Có số test? |
|---|---|---|---|
| **Early fusion** | Nối vector của các view → **một** mô hình dự đoán: p = h([v₁; …; v_m]) | **NeuMF** (Scratch, Pretrained): nối vector nhánh MF (GMF, p ⊙ q) với vector cuối nhánh DNN (MLP) → lớp dự đoán chung, học chung từ đầu đến cuối | Có (3 seed) |
| **Late fusion** | Mỗi view một mô hình dự đoán riêng → gộp đầu ra: p = F(h₁(v₁), …, h_m(v_m)); với tổng có trọng số là kiểu lai *weighted* (Burke, 2002) | **Late Fusion GMF + MLP**: w·minmax(điểm GMF) + (1−w)·minmax(điểm MLP), min–max trên tập ứng viên của từng user, hai mô hình huấn luyện riêng, w = 0,1 chọn trên val (công thức 2.15). Biến thể **BPR-MF + MLP** (w = 0,3) | Có — phần mở rộng, chấm trong lần chạy lại (mục 4.5) |
| Trộn điểm MF + mô hình lai | Không phải late fusion MF + DNN (một thành phần đã là mô hình lai) | **Mô hình B**: w·minmax(điểm iALS) + (1−w)·minmax(điểm NeuMF-Scratch) | Chỉ validation |
| Không phải fusion | — | **MLP đứng riêng** (nối embedding user–item ở đầu vào) = DNN thuần. Lớp `EarlyFusionModel` trong code trùng hệt MLP (có test chứng minh) | Có (dưới tên MLP) |

**Nếu bị hỏi sâu:** lớp đầu ra của NeuMF tuyến tính, nên điểm của NeuMF bằng tổng đóng góp của hai nhánh. Với
NeuMF-Pretrained, lúc khởi tạo h = [α·h_GMF ; (1−α)·h_MLP], nên logit ban đầu đúng bằng α·logit(GMF) + (1−α)·logit(MLP)
— giống trộn điểm. Điểm khác với late fusion: sau đó toàn bộ mạng được tinh chỉnh **chung**, hai nhánh không còn là hai
mô hình độc lập. Late fusion thì giữ nguyên hai mô hình, chỉ trộn điểm đã chuẩn hoá. Báo cáo viết ở mục 3.3.5 và 2.3.4.

**Kết quả trên validation** (phần dưới Bảng 4.1): Late Fusion GMF + MLP với w = 0,1 đạt NDCG@10 = 0,01005, cao hơn cả
hai thành phần đứng riêng (w = 1 chỉ còn GMF: 0,00843; w = 0 chỉ còn MLP: 0,00922) nhưng **thấp hơn NeuMF-Scratch**
(0,01107). Late Fusion BPR-MF + MLP (w = 0,3) đạt 0,00972 so với 0,00911 của BPR-MF đứng riêng. (MLP thành phần là bản
huấn luyện lại ở chế độ GPU tất định nên val 0,00922 khác 0,00837 lúc tuning — PREREG mục 8.)

**Kết quả trên test:** báo cáo mục 4.5, Bảng 4.9 (11 mô hình) và Bảng 4.10 (họ 7 so sánh, Holm riêng). Câu kết luận
trong báo cáo được sinh tự động từ `outputs/final/extension/significance.csv` sau lần chạy lại — khi vấn đáp, đọc đúng
dòng "Late Fusion GMF + MLP vs NeuMF-Scratch" (late vs early fusion) và "vs GMF", "vs MLP" (sau lai vs trước lai).

**Kết quả của mô hình B trên validation** (trộn MF với mô hình lai, không phải late fusion MF + DNN): với w = 0,6, B đạt
NDCG@10 = 0,01260 — cao hơn NeuMF-Scratch đứng riêng (0,01107) 13,8% và iALS đứng riêng (0,01141) 10,5%, gợi ý NeuMF mang
tín hiệu **bổ sung** cho MF khi trộn ở mức điểm.

**Phải thừa nhận:**

- Late fusion (và ItemKNN, UserKNN) được thêm **sau** khi đã xem test của 7 mô hình chính. Đã đăng ký trước khi chấm
  (PREREG mục 9), kiểm định trong họ 7 so sánh riêng có Holm riêng, báo cáo là kết quả mở rộng, không thay kết luận chính.
- Trọng số w cố định, chọn trên validation; chưa thử trộn bằng mô hình học (như cách kết hợp bằng MLP trong luận án của
  cô) — đã ghi ở hướng phát triển (mục 5.3).
- Mô hình B bị loại khỏi phạm vi trước khi chấm test (lý do: quá nhiều mô hình), nên chỉ có số validation.

**Đã làm đúng cách bổ sung đã nêu ở buổi trước:** (1) dùng đúng hai thành phần của NeuMF là GMF và MLP, huấn luyện
riêng; thêm biến thể BPR-MF + MLP; (2) w chỉ chọn trên validation (quét 11 giá trị 0; 0,1; …; 1); (3) ghi vào PREREG
mục 9 **trước** khi chấm test, kèm kiểm tra tuning chạy lại ra đúng cùng số; (4) chấm test bằng `17_extension.py`,
dùng đúng GMF, MLP, BPR-MF đã huấn luyện lại của từng seed trong `outputs/final/seed*/` — không huấn luyện thêm.

**Bằng chứng:** `src/models/late_fusion.py`, `scripts/10_tune.py --model extension`, `scripts/17_extension.py`,
`audit/tuning_log.csv` (11 dòng mỗi biến thể late fusion, 11 dòng `fusion_b`), `audit/best_configs.json`,
`audit/PREREG.md` mục 8–9; `tests/test_extension.py`, `tests/test_tuning.py::test_early_fusion_is_architecturally_identical_to_mlp`.

---

## 14. Baseline và câu hỏi "lai có tốt hơn trước khi lai không?"

| Nhóm | Mô hình | Vai trò |
|---|---|---|
| Baseline đơn giản | Random, Most Popular | Cận dưới; Most Popular rất mạnh với dữ liệu thời trang |
| Matrix Factorization | BPR-MF (tune cùng ngân sách), GMF | MF thuần |
| Láng giềng (memory-based) | ItemKNN, UserKNN (bản thưa top-k) | Baseline của đề cương — phần mở rộng |
| Deep Learning | MLP | DNN thuần |
| MF + DL, early fusion | NeuMF-Scratch, NeuMF-Pretrained | Mô hình lai của đề tài |
| MF + DL, late fusion | Late Fusion GMF + MLP; BPR-MF + MLP | Phần mở rộng (họ so sánh riêng) |
| MF + mô hình lai (trộn điểm) | B: iALS + NeuMF-Scratch | Chỉ có số validation |

**Trả lời câu hỏi chính:** Ở mức biểu diễn (NeuMF): không. Trên test, NeuMF không vượt BPR-MF (NeuMF-Pretrained −5,0%,
NeuMF-Scratch −9,6%), không vượt Most Popular, và không vượt các nhánh GMF, MLP của chính nó. Có 0/8 so sánh đạt tiêu chí
"tốt hơn" — cần **đồng thời** p Holm < 0,05, khoảng tin cậy 95% không chứa 0 và chênh lệch ≥ 5%. Tiêu chí này được đăng
ký trước khi xem test. Ở mức điểm (late fusion): xem kết quả mở rộng, mục 12–13 ở trên.

**Vì sao vẫn có giá trị:**

- Đề tài đo đúng câu hỏi bằng một quy trình chống thiên lệch, và so sánh trực tiếp hai cách hợp nhất của **cùng** hai
  thành phần.
- Kết quả âm nhất quán với các nghiên cứu đối chứng uy tín (Rendle et al., 2020; Ferrari Dacrema et al., 2019).
- Đề tài chỉ ra các hướng có tín hiệu tích cực trên validation (trộn điểm MF với NeuMF, baseline láng giềng).

---

## 15. Sơ đồ kiến trúc

**Đã có trong báo cáo:**

- **Hình 2.1** — kiến trúc chi tiết NeuMF: hai nhánh GMF/MLP, embedding riêng, lớp hợp nhất.
- **Hình 2.2** — so sánh hợp nhất ở mức biểu diễn (NeuMF, một mô hình học chung) với hợp nhất ở mức điểm (Late Fusion
  GMF + MLP, hai mô hình huấn luyện riêng, min–max rồi trộn với trọng số w).
- **Hình 3.1** — luồng toàn hệ thống: dữ liệu H&M → tiền xử lý (gộp, k-core, re-index, ma trận nhị phân) → chia theo
  thời gian và negative sampling → GMF/MLP → NeuMF (và late fusion ở phần mở rộng) → huấn luyện và tinh chỉnh (chỉ
  validation) → huấn luyện lại trên train ∪ val → Full Ranking, kiểm định, phân tích phụ; nhánh baseline (cả ItemKNN,
  UserKNN) chạy song song.
- **Hình 3.2** — kiến trúc ba tầng của demo; **Hình 3.3–3.4** — màn hình demo và bảng 10 khách tương đồng (UserKNN).

Luồng thầy/cô gợi ý (Interaction → Preprocessing → Split → User–Item Matrix → MF → vectors → DL → Fusion → Score →
Ranking → Top-K) được Hình 3.1, 2.1 và 2.2 phủ đủ.

---

## 16. Mô hình "variational" được nhắc trong buổi họp

Tên mô hình **chưa được xác nhận** — cần hỏi lại thầy/cô; không tự ghi là VAE.

Khả năng cao là **Mult-VAE** (Liang et al., 2018, *Variational Autoencoders for Collaborative Filtering*). Báo cáo mục
2.4.4 đã trình bày mô hình này (công thức 2.18): đầu vào là vector mua của cả một user, mã hoá thành phân phối ẩn Gauss,
giải mã ra phân phối đa thức trên toàn catalog, huấn luyện bằng ELBO có hệ số β. Hợp với Full Ranking vì chấm cả catalog
trong một lượt và không cần lấy mẫu âm. Đề tài **chưa cài đặt**; đã đưa vào hướng phát triển (mục 5.3). Nếu thầy/cô yêu
cầu thêm vào thực nghiệm: phải đăng ký trước như phần mở rộng (tune chỉ trên val, ghi PREREG, họ so sánh riêng), vì tập
test đã được xem.

---

## 17. Lộ trình 10 bước — trạng thái hiện tại

| # | Bước | Trạng thái | Bằng chứng |
|---|---|---|---|
| 1 | Sửa Train/Test split | Xong: mốc thời gian chung | `splitting.py`, Bảng 3.3 |
| 2 | Kiểm tra data leakage | Xong (còn rò rỉ nhỏ do k-core, đã ghi là hạn chế) | `tests/test_no_leakage_real_data.py`, mục 4.6 |
| 3 | Tạo bộ test chuẩn | Xong, có khoá test và nhật ký truy cập | `audit/PREREG.md`, `audit/test_access_log.csv` |
| 4 | Chạy lại Baseline/MF | Xong: Random, Most Popular, BPR-MF, GMF; mở rộng: ItemKNN, UserKNN | Bảng 4.2, 4.9 |
| 5 | Chọn ít nhất một mô hình DL | MLP; đã thử thêm CFNet trên validation | Bảng 4.1, `audit/tuning_log.csv` |
| 6 | Xây Hybrid | Xong: NeuMF-Scratch, NeuMF-Pretrained | `src/models/neumf.py`, Hình 2.1 |
| 7 | Thử Fusion | Early fusion (NeuMF): có số test; late fusion GMF + MLP và BPR-MF + MLP: đã tune trên val, chấm test trong lần chạy lại (mở rộng); trộn iALS + NeuMF: chỉ validation | Mục 12–13 ở trên, báo cáo mục 4.5 |
| 8 | Bảng NDCG/HR/Recall/Precision | Xong: mean ± std 3 seed, kèm kiểm định | Bảng 4.2, 4.4; mở rộng 4.9–4.10 |
| 9 | Vẽ kiến trúc | Có Hình 2.1, 2.2 (early vs late fusion), 3.1, 3.2 | Mục 15 ở trên |
| 10 | Phân tích kết quả | Xong: ablation, phân tầng, beyond-accuracy, Sampled-99, độ trễ, phần mở rộng | Chương 4 |

---

## 18. Câu hỏi khó khác nên chuẩn bị

- **"Tập test đã bị chấm mấy lần?"** — Hai đợt chính (27/09 và 29/09, mỗi đợt 3 seed) và một lần phân tích phụ, rồi một
  lần chạy lại toàn bộ trên commit cuối (3 seed + phần mở rộng + phân tích phụ). Mọi lần đều ghi trong
  `audit/test_access_log.csv` kèm commit và lý do; mỗi thay đổi đều đăng ký trước khi chạy (PREREG mục 8–9). Cấu hình,
  chỉ số, họ so sánh và tiêu chí của 7 mô hình chính không đổi qua các lần; kết luận không đổi. Đã công bố ở mục 3.6,
  4.1 (ý "Lần chấm") và phần tóm tắt.
- **"Vì sao phải chạy lại toàn bộ khi đã có số?"** — Kết quả 29/09 sinh ở một commit cũ; sau đó thư mục mã được đổi tên
  và thêm phần mở rộng. Chạy lại để mọi số liệu trong báo cáo truy vết về **một** commit. Không tune lại, không đổi cấu
  hình; huấn luyện ở chế độ GPU tất định nên trên cùng máy kỳ vọng ra đúng cùng số — đó cũng là một kiểm tra tái lập
  (`scripts/19_check_report.py` so số mới với số cũ).
- **"Nếu UserKNN/ItemKNN tốt hơn NeuMF thì đề tài còn ý nghĩa gì?"** — Đó chính là câu hỏi đề tài đặt ra: NeuMF có đáng độ
  phức tạp trên dữ liệu thời trang thưa không. Baseline láng giềng được tune tốt vượt mô hình học sâu là phát hiện đã
  được Ferrari Dacrema et al. (2019) ghi nhận trên nhiều bộ dữ liệu; đề tài kiểm chứng lại trên H&M bằng quy trình không
  thiên lệch và báo cáo đúng như vậy.
- **"Vì sao NeuMF-Scratch là mô hình lai được chọn, trong khi Pretrained tốt hơn trên test?"** — Theo quy tắc đăng ký
  trước, mô hình được chọn theo validation (Scratch 0,01107 > Pretrained 0,00913); test chỉ để báo cáo, không chọn lại.
  Thứ hạng đổi giữa val và test (Hình 4.3) cho thấy chênh lệch giữa các mô hình nhỏ hơn nhiễu.
- **"Vì sao k-core = 10 chứ không phải 5?"** — Do RAM: k = 5 cần khoảng 10,7 GB cho Full Ranking (vượt máy 16 GB), k =
  10 cần khoảng 2,8 GB. Hệ quả là dữ liệu thiên về khách mua nhiều — đã ghi là hạn chế.
- **"Vì sao dùng mẫu 500k mà không dùng toàn bộ 31,8 triệu dòng?"** — Full Ranking trên toàn bộ dữ liệu (889.062 user ×
  90.690 item ở k = 5) cần khoảng 8·10¹⁰ phép chấm điểm cho mỗi mô hình, không khả thi trên GPU 4 GB. Mẫu lấy theo khách
  hàng, giữ trọn lịch sử và tất định (chạy lại ra đúng cùng một file).
- **"Vì sao không chia leave-one-out như đề cương?"** — Leave-one-out rò rỉ tương lai (báo cáo mục 3.2.5): trên hm500k,
  trung bình 11,2% tương tác train xảy ra sau ngày của món test của user đó, và 60,9% user có món val và món test cùng
  ngày (Meng et al., 2020). Leave-one-out chỉ còn là run khám phá với cấu hình mặc định, không dùng để chọn hay so sánh
  mô hình.
- **"Timestamp chỉ theo ngày có gây rò rỉ không?"** — Một món test có thể được mua cùng ngày (cùng giỏ) với một món
  trong lịch sử. Ảnh hưởng này như nhau với mọi mô hình và đã ghi ở mục 4.6, ý (iv).
- **"Demo dùng mô hình nào?"** — Đúng các mô hình của đánh giá cuối (`outputs/final/seed42`, huấn luyện lại trên
  train ∪ val, cấu hình riêng của từng mô hình); sản phẩm đích là các món khách mua lần đầu trong giai đoạn test. Số
  trên demo khớp file per-user của Chương 4 (có test tự động `demo/tests/test_demo.py`). Đây là hiển thị lại kết quả đã
  chấm, không phải một lần chấm mới. Chế độ khám phá leave-one-out cũ vẫn giữ (`DEMO_MODE=explore`).
- **"3 seed có đủ không?"** — Kiểm định làm theo user (2.996 cặp quan sát), không theo seed. Với 3 seed, Wilcoxon theo
  seed không thể đạt p < 0,05 (p nhỏ nhất là 0,25).
