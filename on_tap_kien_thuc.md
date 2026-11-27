# Ôn tập kiến thức đề tài NeuMF-F — từ cơ bản đến nâng cao

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu.
**Nhóm:** Lê Minh Lý, Sử Thị Yến Linh. **GVHD:** TS. Hồ Thị Linh.

File gồm hai phần:

- **Phần A — Tóm tắt kiến thức** (cấp 1 → cấp 5): định nghĩa ngắn, công thức, con số thật của đề tài.
- **Phần B — Prompt** để dán vào một AI (ChatGPT, Claude, Gemini…) cùng với Phần A, nhờ viết thành tài liệu học chi tiết.

Mọi con số lấy từ kết quả đã lưu (`neumf_project/outputs/`) và báo cáo; giải thích dài hơn có ở `tong_hop.md` mục 15.

---

# PHẦN A — TÓM TẮT KIẾN THỨC

## Cấp 1 — Khái niệm nền

| Khái niệm | Tóm tắt |
|---|---|
| Hệ khuyến nghị | Từ dữ liệu quá khứ, đoán món mỗi người có khả năng mua/thích, đưa ra danh sách ngắn |
| Phản hồi tường minh (*explicit feedback*) | Người dùng tự chấm điểm (1–5 sao) |
| Phản hồi ngầm (*implicit feedback*) | Chỉ biết hành vi; đề tài: **mua = 1**. "Không mua" ≠ "không thích" (có thể chưa thấy) |
| Bài toán Top-K | Xếp hạng mọi sản phẩm ứng viên, lấy K món đầu (K = 10; thêm 15, 20) |
| Ma trận tương tác | Hàng = khách, cột = sản phẩm, ô = 1 nếu đã mua. Mẫu kiểm định H&M: 243.696 cặp / (7.994 × 6.749) ≈ **0,45%** ô khác 0 → rất **thưa** |
| *Cold start* | Khách/sản phẩm mới chưa có lịch sử; mô hình chỉ dùng ID bó tay, đặc trưng giúp xử lý |
| Mô hình / tham số | Hàm tính điểm; tham số (trọng số, embedding) do huấn luyện học ra |
| Siêu tham số | Người chọn trước khi huấn luyện: d, lr, số mẫu âm, dropout… |
| Tập huấn luyện / xác thực / kiểm thử | Học trọng số / chọn cấu hình và số epoch / kết luận cuối (mở đúng 1 lần) |

## Cấp 2 — Học máy cơ bản

| Khái niệm | Tóm tắt | Trong đề tài |
|---|---|---|
| **Epoch** | 1 lượt mô hình đi qua **toàn bộ** dữ liệu huấn luyện một lần | Tối đa 20 epoch |
| **Batch** | Gói nhỏ dữ liệu; mỗi batch → tính lỗi → cập nhật trọng số 1 lần | 512 mẫu/batch |
| Iteration | 1 lần cập nhật = 1 batch. Số iteration/epoch = số mẫu / batch | — |
| **Hàm mất mát** (*loss*) | Đo mô hình sai bao nhiêu; huấn luyện = làm nó nhỏ đi | BCE (cấp 3) |
| Gradient descent | Đi ngược hướng đạo hàm của loss để giảm loss | — |
| **Adam** | Biến thể gradient descent, tự điều chỉnh bước cho từng tham số | lr = 0,001 |
| Learning rate (lr) | Độ lớn mỗi bước cập nhật; lớn quá → nhảy lung tung, nhỏ quá → học chậm | 0,001 |
| Weight decay / regularization | Phạt trọng số lớn để chống học thuộc | 1e-6 (BPR-MF: 0,001) |
| **Overfitting** | Học thuộc dữ liệu huấn luyện, kém trên dữ liệu mới | Chặn bằng dừng sớm, dropout, weight decay |
| Underfitting | Học chưa đủ | — |
| **Dừng sớm** (*early stopping*) | Sau mỗi epoch chấm tập xác thực; không tăng sau *patience* epoch thì dừng, lấy epoch tốt nhất | Chấm NDCG@10, patience = 5 |
| Dropout | Khi huấn luyện tắt ngẫu nhiên một phần nơ-ron; khi chấm bật hết | NeuMF-F chọn 0 |
| **Seed** | Số khởi đầu cho bộ sinh ngẫu nhiên → chạy lại ra đúng kết quả | 5 seed: 42, 2024, 2025, 2026, 3407 |
| Trung bình ± độ lệch chuẩn | Kết quả qua 5 seed và mức dao động | Mô hình không ngẫu nhiên (Most Popular, Content, KNN, Hybrid-CBCF) có **± 0** — không phải thiếu số |

**Hàm kích hoạt và lớp:**

- Lớp tuyến tính: $\mathbf{h} = W\mathbf{x} + \mathbf{b}$
- ReLU: $\max(0, z)$ — tạo phi tuyến
- Sigmoid: $\sigma(z) = \dfrac{1}{1 + e^{-z}} \in (0,1)$ — xác suất "sẽ mua"
- **Logit** = $z$ trước sigmoid. Đề tài **xếp hạng theo logit** vì sigmoid float32 bão hoà thành 1,0 → nhiều món bằng
  điểm giả.

## Cấp 3 — Hệ khuyến nghị: từ cổ điển đến học sâu

### 3.1 Mô hình đơn giản

| Mô hình | Cách tính điểm | Cấu hình chọn |
|---|---|---|
| Random | Ngẫu nhiên (cận dưới) | — |
| Most Popular | Số lượt mua trong tập huấn luyện; ai cũng nhận cùng danh sách | — |
| MostPopular-Recent | Số giao dịch trong W ngày trước mốc | W = 28 ngày |
| Content | Hồ sơ khách = trung bình vector nội dung các món đã mua, món mới nặng hơn; điểm = cosine | Chu kỳ bán rã 30 ngày |

### 3.2 Lọc cộng tác láng giềng

$$\cos(\mathbf{a},\mathbf{b}) = \frac{\mathbf{a}\cdot\mathbf{b}}{\lVert\mathbf{a}\rVert\lVert\mathbf{b}\rVert + h}$$

- h = hệ số co (*shrink*): hạ điểm cặp có quá ít khách chung.
- **ItemKNN**: sản phẩm = vector 0/1 theo khách đã mua; giữ k láng giềng; điểm(u, i) = tổng tương đồng giữa i và các món
  u đã mua. Chọn k = 100, h = 50.
- **UserKNN**: tương tự theo khách. Chọn k = 200, h = 0.
- Ví dụ: áo A được khách {1,2,3} mua, áo B được {2,3,4} → cos = 2/(√3·√3) = 0,67.

### 3.3 Embedding và nhân tử hoá ma trận (MF)

- **Embedding**: bảng tra, mỗi ID ↔ một vector d số thực **học được**.
- **MF**: $\hat{y}_{ui} = \mathbf{p}_u^\top \mathbf{q}_i$ (tích vô hướng vector khách và sản phẩm).
- **BPR-MF** (Rendle et al., 2009): học thứ tự "món đã mua i > món chưa mua j":

$$L_{\text{BPR}} = -\sum_{(u,i,j)} \ln\sigma(\hat{y}_{ui} - \hat{y}_{uj}) + \lambda\lVert\Theta\rVert^2$$

  Chọn d = 128, lr = 0,03, λ = 0,001, 20 epoch.

### 3.4 Khung NCF (He et al., 2017)

| Mô hình | Công thức tương tác | Ý nghĩa |
|---|---|---|
| **GMF** | $\phi^G = \mathbf{p}_u \odot \mathbf{q}_i$ (nhân từng phần tử) → lớp tuyến tính | MF tổng quát, mỗi chiều có trọng số |
| **MLP** | $\phi^M = \text{MLP}([\mathbf{p}_u;\mathbf{q}_i])$, tháp 64 → 32 → 16 → 8, ReLU | Tương tác phi tuyến |
| **NeuMF** | $\hat{y} = \sigma\big(\mathbf{h}^\top[\phi^G;\phi^M]\big)$ | Kết hợp tuyến tính + phi tuyến (hợp nhất sớm) |

Ví dụ ⊙: [1, 2, 3] ⊙ [4, 0, −1] = [4, 0, −3]; cộng lại = tích vô hướng = 1.

### 3.5 Huấn luyện mô hình nơ-ron

- **BCE** (*binary cross-entropy*, `nn.BCEWithLogitsLoss`):

$$L = -\big[y\ln\sigma(z) + (1-y)\ln(1-\sigma(z))\big]$$

  Món đã mua, σ(z) = 0,9 → L ≈ 0,105; σ(z) = 0,1 → L ≈ 2,30.
- **Mẫu âm** (*negative sampling*): mỗi cặp đã mua rút **8** món chưa mua (y = 0), chỉ trong món **đã ra mắt** tại ngày
  mua; rút lại mỗi epoch.
- Cấu hình chọn của NeuMF-F: d = 32, lr = 0,001, 8 mẫu âm, weight decay 1e-6, dropout 0, ρ = 0.

## Cấp 4 — Mô hình đề xuất NeuMF-F và đặc trưng

### 4.1 Công thức

$$\mathbf{p}_u = \mathbf{e}^{\text{ID}}_u + W_U\,\mathbf{x}_u(t), \qquad \mathbf{q}_i = m_i\,\mathbf{e}^{\text{ID}}_i + W_I\,\mathbf{x}_i(t)$$

- Giữ nguyên NeuMF, nhưng vector khách/sản phẩm = embedding ID **cộng** đặc trưng đã chiếu về d = 32 chiều.
- Mỗi nhánh GMF, MLP có $W_U$, $W_I$ riêng; embedding thuộc tính dùng chung.
- $m_i$: **bỏ ID ngẫu nhiên** (ý tưởng DropoutNet) — khi huấn luyện đặt $m_i = 0$ với xác suất ρ để mô hình học cả từ
  đặc trưng. NeuMF-F chọn ρ = 0; GMF-F chọn 0,25.
- Đặc trưng tại ngày t **chỉ dùng dữ liệu trước t** (không lộ tương lai).

### 4.2 Vector đặc trưng sản phẩm $\mathbf{x}_i$

$$d_I = n_{\text{thuộc tính}} \times 8 + 64 + 5$$

| Phần | Cách tạo | H&M | Amazon Beauty |
|---|---|---|---|
| Thuộc tính danh mục | Mỗi thuộc tính một embedding **8 chiều** (`cat_dim = 8`), nối lại | 11 × 8 = **88** | 5 × 8 = **40** |
| Văn bản | TF-IDF → SVD → chuẩn hoá L2 | **64** | **64** |
| Thời gian tại t | Bán trong 7, 28, 91 ngày trước t; tuổi sản phẩm; cờ "chưa từng bán" | **5** | **5** |
| **Tổng** | | **157** | **109** |

- 11 thuộc tính H&M: loại sản phẩm, nhóm sản phẩm, hoạ tiết, nhóm màu, độ đậm màu, màu chủ đạo, bộ phận, mã chỉ mục,
  nhóm chỉ mục, khu, nhóm may mặc.
- 5 thuộc tính Amazon: thương hiệu, danh mục cấp 1, 2, 3, nhóm giá (8 nhóm, 0 = không có giá).
- Số đếm thời gian mã hoá $\log(1+x)/10$; cờ 0/1. Amazon dùng số đánh giá thay doanh số.

### 4.3 Vector đặc trưng khách $\mathbf{x}_u$

- H&M: 5 thuộc tính × 8 (nhóm tuổi, trạng thái hội viên, tần suất nhận tin, FN, Active) + 2 đặc trưng thời gian (số ngày
  từ lần mua gần nhất, số cặp đã mua) = **42 chiều**.
- Amazon: không có thông tin khách → chỉ **2 chiều** thời gian.

### 4.4 Văn bản: TF-IDF và SVD

- **TF-IDF**: mỗi chiều là một từ/cụm 2 từ; cao khi từ xuất hiện nhiều trong mô tả này (TF) nhưng hiếm ở mô tả khác
  (IDF ≈ log(N / số mô tả chứa từ)). Bỏ từ dừng; tối đa 30.000 từ; từ phải có ở ≥ 3 sản phẩm.
- **SVD cắt cụt** (ý tưởng LSA): nén ~30.000 chiều thưa xuống **64 chiều** giữ thông tin lớn nhất.
- **Chuẩn hoá L2**: chia cho độ dài để mọi vector dài 1.
- Tính **một lần** trên toàn danh mục, không học trong huấn luyện.

### 4.5 Hợp nhất sớm và muộn

| | Hợp nhất sớm (*early fusion*) | Hợp nhất muộn (*late fusion*) |
|---|---|---|
| Cách làm | Nối biểu diễn hai nhánh, **một** mô hình học chung | Hai mô hình học **riêng**, trộn **điểm** |
| Mô hình | NeuMF, NeuMF-F | LateFusion-F |

$$s_{\text{LF}} = w\cdot\text{minmax}(s_{\text{GMF-F}}) + (1-w)\cdot\text{minmax}(s_{\text{MLP-F}}),\quad w = 0{,}4$$

$$\text{minmax}(s) = \frac{s - \min}{\max - \min}\ \text{(trên tập ứng viên của từng khách)}$$

GMF-F, MLP-F = NeuMF-F chỉ giữ một nhánh.

### 4.6 Hybrid-CBCF — mô hình lai truyền thống (bổ sung)

- Theo chương 3 luận án của GVHD: Content + UserKNN + ItemKNN, chuẩn hoá min–max, kết hợp điểm.
- Thử bỏ phiếu (trung bình, max, min) và **tổng có trọng số học theo cặp** (hồi quy logistic trên hiệu đặc trưng món đúng
  − món sai, 50 món sai/món đúng — tiêu chí BPR với hàm tuyến tính) → chọn tổng có trọng số.
- Trọng số: Content 0,12; UserKNN 0,60; ItemKNN 0,28. Tất định → chấm 1 lần dùng cho cả 5 seed.

## Cấp 5 — Dữ liệu, đánh giá, thống kê, quy trình (nâng cao)

### 5.1 Dữ liệu H&M

| Bước | Nội dung | Số liệu |
|---|---|---|
| Gốc (Kaggle) | 20/09/2018 → 22/09/2020 | 31.788.324 giao dịch; 105.542 sản phẩm (theo màu); 1.371.980 khách |
| Lấy mẫu **theo khách** | Băm `customer_id` vào 100.000 nhóm, chia khối ~500.000 giao dịch, giữ trọn lịch sử | Mẫu phát triển (khối 0) và mẫu kiểm định (khối 2), **không chung khách** |
| Gộp theo mẫu thiết kế | `product_code` = `article_id // 1000`; mọi màu = 1 sản phẩm | — |
| Gộp cặp | Giao dịch lặp → 1 cặp (khách, sản phẩm), giữ **ngày mua đầu** | — |
| Lọc **10-core** lặp | Bỏ khách < 10 món, sản phẩm < 10 khách, lặp tới khi ổn định; chỉ trên dữ liệu **trước mốc kiểm thử** | Mẫu kiểm định: 7.994 khách, 6.749 sản phẩm, 243.696 cặp |
| Ghi file + MD5 | `outputs/data/*.csv.gz`; mọi mô hình đọc cùng file | — |

- Lý do lấy mẫu: Full Ranking toàn H&M cần hàng chục tỷ cặp/mô hình, vượt RAM 16 GB.
- Lý do k = 10 (không phải 5): giới hạn RAM.

### 5.2 Chia theo thời gian

| | Xác thực | Kiểm thử |
|---|---|---|
| Mốc τ | 01/07/2020 | 29/07/2020 |
| Cửa sổ món đúng | 01/07–28/07/2020 (4 tuần) | 29/07–22/09/2020 (8 tuần) |
| Dùng cho | Chọn cấu hình (mẫu phát triển), chọn số epoch (mẫu kiểm định) | Kết luận (mẫu kiểm định), mở 1 lần |

- **Món đúng** = món khách mua **lần đầu** trong cửa sổ; món đã mua trước τ không bao giờ là món đúng.
- **Tập ứng viên** = sản phẩm có người mua trước τ, trừ món khách đã mua (~6.700 món/khách H&M).
- **Không dùng leave-one-out** (giấu món cuối của mỗi khách) vì lọt tương lai: 11,2% cặp huấn luyện xảy ra sau món kiểm
  thử của chính khách đó (Meng et al., 2020).
- **Rò rỉ dữ liệu** (*data leakage*) bị chặn bởi: k-core trước τ, đặc trưng theo thời điểm, mẫu âm trong món đã ra mắt,
  có test tự động.

### 5.3 Amazon Beauty (dữ liệu đối chứng)

- Amazon review 2014 (McAuley et al., 2015), Beauty 5-core: 198.502 đánh giá, 22.363 khách, 12.101 sản phẩm.
- Chia theo thời gian: xác thực 01/10–31/12/2013; kiểm thử 01/01–23/07/2014. k-core = 5 trước 01/01/2014: 10.681 khách,
  6.069 sản phẩm, 94.009 cặp; 2.644 khách được đánh giá.
- **Không tinh chỉnh lại**: dùng nguyên cấu hình chọn trên H&M, chỉ chọn số epoch trên xác thực Amazon.

### 5.4 Độ đo (trung bình theo khách)

$T_u$ = tập món đúng của khách u, $\text{hits}_u$ = số món đúng trong top-K, $r_i$ = hạng (từ 1):

| Độ đo | Công thức |
|---|---|
| HR@K | $\mathbb{1}[\text{hits}_u \ge 1]$ |
| Precision@K | $\text{hits}_u / K$ |
| Recall@K | $\text{hits}_u / \lvert T_u\rvert$ |
| **NDCG@K** (độ đo chính) | $\dfrac{\text{DCG}}{\text{IDCG}} = \dfrac{\sum_{i\in T_u, r_i\le K} 1/\log_2(r_i+1)}{\sum_{j=1}^{\min(\lvert T_u\rvert,K)} 1/\log_2(j+1)}$ |
| Độ phủ@10 (*coverage*) | Số sản phẩm khác nhau xuất hiện trong top-10 của ít nhất một khách / số ứng viên |

**Ví dụ tính tay** — khách KH0261: 2 món đúng, NeuMF-F xếp hạng 3 và 6.

- DCG = 1/log₂4 + 1/log₂7 = 0,500 + 0,356 = 0,856
- IDCG = 1/log₂2 + 1/log₂3 = 1 + 0,631 = 1,631
- **NDCG@10 ≈ 0,525**; HR@10 = 1; Recall@10 = 2/2 = 1; Precision@10 = 2/10 = 0,2.
- NeuMF xếp món gần nhất ở hạng 164 → NDCG@10 = 0.
- NDCG@10 trung bình chỉ ~0,04 vì đa số khách không có món đúng nào lọt top-10 trong ~6.700 ứng viên; Random = 0,001.

**Full Ranking vs Sampled Ranking:** Full chấm **mọi** ứng viên; Sampled chỉ trộn món đúng với ~100 món ngẫu nhiên — rẻ
hơn nhưng có thể đảo thứ hạng mô hình (Krichene & Rendle, 2020) → đề tài dùng Full.

### 5.5 Quy trình chống thiên lệch

1. **Đăng ký trước** (`audit/PREREG_v2.md`): mô hình, lưới, seed, độ đo, 10 cặp so sánh, tiêu chí — commit **trước** khi
   mở tập kiểm thử.
2. **Tinh chỉnh** chỉ trên xác thực của mẫu phát triển: 6 cấu hình/mô hình (cùng ngân sách), 76 cấu hình, 4,7 giờ.
3. **Đánh giá cuối**: mỗi seed, mạng nơ-ron chọn số epoch trên xác thực của mẫu kiểm định → **huấn luyện lại từ đầu** trên
   mọi cặp trước τ → chấm kiểm thử.
4. **Khoá kiểm thử**: script từ chối chạy nếu kế hoạch chưa commit hoặc mã đang sửa dở; mỗi lần mở tập kiểm thử ghi nhật
   ký `audit/test_access_log.csv`.
5. **So sánh công bằng**: cùng file dữ liệu (MD5), cùng tập ứng viên, cùng ngân sách tinh chỉnh.
6. **Không gõ tay số**: số trong báo cáo sinh tự động từ file kết quả.

### 5.6 Kiểm định thống kê

- **Chênh lệch tương đối** = (A − B) / B. Ví dụ NeuMF-F vs NeuMF: (0,04003 − 0,02783) / 0,02783 ≈ **+43,8%**.
- **Ghép cặp theo khách**: $d_u$ = NDCG@10(A) − NDCG@10(B) của từng khách (mỗi bên trung bình 5 seed).
- **Wilcoxon signed-rank**: bỏ $d_u = 0$, xếp hạng $|d_u|$, so tổng hạng phía dương và âm; không giả định phân phối
  chuẩn → **p-value** = xác suất thấy chênh lệch này nếu hai mô hình thật ra ngang nhau.
- **Bootstrap 95%**: rút có hoàn lại khách 10.000 lần, mỗi lần tính trung bình $d_u$, lấy phân vị 2,5% và 97,5%.
- **Holm** (so sánh bội, 10 phép): xếp p tăng dần, nhân $p_{(k)}$ với $(m - k + 1)$, giữ đơn điệu. Ví dụ m = 10: p nhỏ
  nhất 0,003 × 10 = 0,03 < 0,05 → có ý nghĩa; p = 0,02 đứng thứ 3 × 8 = 0,16 → không.
- **Tiêu chí "A tốt hơn B"** — **đồng thời**: p sau Holm < 0,05; khoảng bootstrap không chứa 0; chênh lệch tương đối ≥ 5%.
  Thiếu một điều kiện → "không khác biệt có ý nghĩa" (demo ghi "ngang nhau").
- **Ablation** (bóc tách): tắt từng nhóm đặc trưng của NeuMF-F, đo NDCG giảm; chỉ seed 42, chỉ mô tả, không kiểm định.

### 5.7 Hệ thống và demo

```
1_sample.py → 3_features.py → 2_prepare.py → 4_tune.py → 5_final.py (+ 6_bosung.py) → 7_report.py → 8_check_report.py
 lấy mẫu      đặc trưng        k-core, MD5    tinh chỉnh  đánh giá cuối 5 seed          bảng, hình,     đối chiếu
                                                                                       macro LaTeX     câu chữ báo cáo
```

- Chạy qua `python run.py <lệnh>`; phần chung ở `scripts/common.py` và `src/` (mô hình: `src/models/hybrid_features.py`).
- **Demo**: backend FastAPI nạp checkpoint seed 42, chỉ **suy diễn** (không huấn luyện); frontend HTML/CSS/JS. Trung vị
  gợi ý top-10: 16,1 ms (H&M), 11,3 ms (Amazon) trên CPU. Khách mới nhận danh sách Most Popular.

## Kết quả chính (NDCG@10, trung bình 5 seed)

| Mô hình | H&M | Amazon Beauty |
|---|---|---|
| LateFusion-F | **0,04093** (hạng 1) | **0,03747** (hạng 1) |
| NeuMF-F (đề xuất) | 0,04003 (hạng 2) | 0,03277 (hạng 3) |
| GMF-F | 0,03902 | 0,03298 |
| MLP-F | 0,03480 | 0,03065 |
| Hybrid-CBCF (bổ sung) | 0,03183 | 0,02659 |
| UserKNN | 0,03114 | 0,02506 |
| ItemKNN | 0,02860 | 0,02333 |
| NeuMF | 0,02783 | 0,01978 |
| MostPopular-Recent | 0,02760 | 0,01401 |
| GMF | 0,02695 | 0,01627 |
| BPR-MF | 0,02661 | 0,01144 |
| MLP | 0,02373 | 0,01271 |
| Most Popular | 0,02184 | 0,00872 |
| Content | 0,00506 | 0,00945 |
| Random | 0,00098 | 0,00101 |

**Kết luận phải nói đúng:**

- H&M: NeuMF-F **tốt hơn có ý nghĩa 7/9** đối thủ trong họ so sánh; **ngang** GMF-F (+2,6%) và LateFusion-F (−2,2%).
- Đặc trưng là đóng góp chính: NeuMF-F hơn NeuMF chỉ dùng ID **+43,8%** (H&M), **+65,7%** (Amazon), đều có ý nghĩa.
- NeuMF-F hơn Hybrid-CBCF **+25,8%** (H&M), **+23,0%** (Amazon).
- Amazon: LateFusion-F **tốt hơn** NeuMF-F có ý nghĩa (NeuMF-F thấp hơn 12,5%).
- **Không gọi NeuMF-F là mô hình tốt nhất** — LateFusion-F cao nhất trên cả hai bộ.
- Ablation H&M: bỏ đặc trưng thời gian −42,3% (quan trọng nhất), bỏ thông tin khách −10,3%; bỏ thuộc tính −3,7% và bỏ văn
  bản −2,7% chưa khẳng định. Amazon: bỏ thời gian −31,6%, bỏ thuộc tính −14,4%.
- Thời gian huấn luyện/seed (H&M): NeuMF-F 15,2 phút; LateFusion-F 30,1 phút (tổng GMF-F + MLP-F).
- Độ phủ top-10 (H&M, seed 42): Most Popular 0,3%; UserKNN 5,7%; Hybrid-CBCF 10,8%; NeuMF-F 13,3%; ItemKNN 20,4%.

## Bảng thuật ngữ

| Tiếng Việt | Tiếng Anh |
|---|---|
| Phản hồi ngầm | Implicit feedback |
| Nhân tử hoá ma trận | Matrix factorization |
| Lọc cộng tác / dựa trên nội dung | Collaborative / content-based filtering |
| Vector nhúng | Embedding |
| Hợp nhất sớm / muộn | Early / late fusion |
| Mẫu âm | Negative sampling |
| Hàm mất mát | Loss function |
| Dừng sớm | Early stopping |
| Siêu tham số | Hyperparameter |
| Rò rỉ dữ liệu | Data leakage |
| Xếp hạng toàn bộ | Full ranking |
| Phân tích bóc tách | Ablation study |
| Đăng ký trước | Pre-registration |
| Khoảng tin cậy | Confidence interval |
| Độ phủ | Coverage |

---

# PHẦN B — PROMPT ĐỂ DÁN VÀO AI

Cách dùng: copy toàn bộ khối dưới đây, rồi dán **ngay sau nó** toàn bộ Phần A ở trên.

```text
Bạn là giảng viên học máy và hệ khuyến nghị, đang kèm hai sinh viên năm cuối ôn bảo vệ đồ án. Bên dưới là bản tóm tắt
đồ án của họ (Phần A). Hãy viết thành TÀI LIỆU HỌC CHI TIẾT bằng tiếng Việt có dấu, đi từ cơ bản đến nâng cao.

Yêu cầu nội dung:
1. Giữ đúng thứ tự Cấp 1 → Cấp 5, rồi Kết quả chính. Với MỖI khái niệm trong tóm tắt, viết đủ 5 ý:
   (a) Định nghĩa dễ hiểu, như giảng cho người mới học;
   (b) Trực giác / ví dụ đời thường (ví dụ trong mua sắm thời trang);
   (c) Công thức (giữ ký hiệu LaTeX như bản tóm tắt) và giải thích TỪNG ký hiệu;
   (d) Ví dụ tính tay bằng số nhỏ, trình bày từng bước;
   (e) Liên hệ cụ thể: khái niệm này được dùng thế nào và vì sao trong đồ án (dùng đúng con số đồ án đã cho).
2. Giải thích kỹ các chỗ hội đồng hay hỏi: vì sao vector sản phẩm 157 chiều (H&M) và 109 chiều (Amazon); epoch, batch,
   dừng sớm; vì sao "± 0" ở các mô hình không ngẫu nhiên; vì sao chia theo thời gian thay vì leave-one-out; vì sao Full
   Ranking; NDCG tính thế nào; Wilcoxon, bootstrap, Holm và tiêu chí "tốt hơn"; hợp nhất sớm khác hợp nhất muộn ra sao;
   vì sao NeuMF-F không đứng đầu mà đồ án vẫn có giá trị.
3. Cuối mỗi cấp: 5 câu hỏi tự kiểm tra kèm đáp án ngắn.
4. Cuối tài liệu: 20 câu hỏi hội đồng có thể hỏi, mỗi câu kèm câu trả lời mẫu 3–5 câu, bám đúng số liệu và kết luận.

Ràng buộc bắt buộc:
- CHỈ dùng số liệu, cấu hình, kết quả có trong bản tóm tắt. Không bịa thêm con số, tên mô hình, bài báo hay kết quả.
  Nếu cần ví dụ minh hoạ ngoài đồ án, ghi rõ "ví dụ minh hoạ" và dùng số nhỏ dễ tính.
- Không được viết NeuMF-F là mô hình tốt nhất: LateFusion-F cao nhất trên cả hai bộ dữ liệu; trên H&M NeuMF-F ngang
  GMF-F và LateFusion-F, trên Amazon LateFusion-F tốt hơn NeuMF-F có ý nghĩa.
- Thuật ngữ: tiếng Việt, kèm tiếng Anh in nghiêng ở lần xuất hiện đầu; riêng "cold start" giữ tiếng Anh. Dùng "lớp" cho
  mạng nơ-ron; dùng "hợp nhất sớm / hợp nhất muộn".
- Số thập phân viết theo kiểu Việt Nam (dấu phẩy: 0,04003; dấu chấm ngăn nghìn: 6.749).
- Trình bày Markdown: tiêu đề rõ ràng, bảng khi so sánh, công thức LaTeX ($...$ và $$...$$), câu ngắn, dễ đọc.
- Nếu tài liệu quá dài cho một lần trả lời, viết lần lượt từng cấp và dừng sau mỗi cấp để tôi gõ "tiếp".

PHẦN A — TÓM TẮT ĐỒ ÁN:
[dán Phần A vào đây]
```
