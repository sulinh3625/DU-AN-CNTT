# Phạm vi và phương pháp

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu
**GVHD:** TS. Hồ Thị Linh — **Nhóm:** Lê Minh Lý, Sử Thị Yến Linh

Tài liệu tóm tắt bài toán, phạm vi và phương pháp của **giao thức v2** — giao thức cho kết quả chính của báo cáo.
Ràng buộc đầy đủ: kế hoạch đăng ký trước `audit/PREREG_v2.md`. Trình bày chi tiết: báo cáo Chương 2–3. Cách chạy:
`README.md`. Giao thức v1 chỉ còn là lịch sử phát triển (mục 10).

| Mục | Nội dung |
|---|---|
| 1 | Bài toán và câu hỏi nghiên cứu |
| 2 | Yêu cầu R1–R9 |
| 3 | Phạm vi |
| 4 | Dữ liệu |
| 5 | Mô hình |
| 6 | Đánh giá và kiểm định |
| 7 | Quy trình chống thiên lệch |
| 8 | Kết quả ở đâu |
| 9 | Hạn chế đã biết |
| 10 | Lịch sử: giao thức v1 |
| 11 | Tài liệu tham khảo chính |

---

## 1. Bài toán và câu hỏi nghiên cứu

Khuyến nghị Top-K sản phẩm thời trang từ **phản hồi ngầm**: chỉ biết khách đã mua gì ($y_{ui} = 1$), không có điểm
đánh giá. $y_{ui} = 0$ không có nghĩa là khách không thích — có thể chỉ là chưa thấy. Vì vậy bài toán là **xếp hạng**,
và khi huấn luyện cần lấy mẫu âm.

Tại một mốc thời gian, với mỗi khách, mô hình chấm điểm mọi sản phẩm trong tập ứng viên — **gồm cả sản phẩm mới** chưa
từng bán trước mốc — rồi xếp giảm dần và lấy K món đầu.

Câu hỏi nghiên cứu được trả lời bằng **họ 10 so sánh** đăng ký trước (mục 6.3):

| Câu hỏi | So sánh |
|---|---|
| Đặc trưng có cải thiện mô hình lai không? | NeuMF-F vs NeuMF |
| Mô hình lai có hơn từng nhánh đứng riêng không? | NeuMF-F vs GMF-F; NeuMF-F vs MLP-F |
| Hợp nhất sớm hay hợp nhất muộn? | NeuMF-F vs LateFusion-F |
| NeuMF-F so với các baseline đã tinh chỉnh | NeuMF-F vs BPR-MF, ItemKNN, UserKNN, MostPopular-Recent, Content |
| Mô hình lai chỉ dùng ID so với MF | NeuMF vs BPR-MF |

## 2. Yêu cầu R1–R9

| Mã | Yêu cầu |
|---|---|
| R1 | H&M Personalized Fashion Recommendations là bộ dữ liệu **chính và duy nhất** cho kết quả |
| R2 | **Lai MF + DNN có đặc trưng**: lõi là GMF + MLP hợp nhất sớm như NeuMF; được dùng thuộc tính và mô tả văn bản của sản phẩm (`articles.csv`), thuộc tính khách (`customers.csv`), doanh số theo ngày của toàn H&M. Không dùng ảnh, giá. NeuMF/GMF/MLP chỉ dùng ID giữ làm đối chứng |
| R3 | GMF + MLP → NeuMF theo He et al. (2017) |
| R4 | **Không dùng thông tin tương lai**: đặc trưng tại ngày t chỉ dùng dữ liệu trước t; k-core chỉ dùng cặp trước mốc kiểm thử; mẫu âm chỉ lấy trong sản phẩm đã ra mắt |
| R5 | Tinh chỉnh có hệ thống, mọi cấu hình ghi vào `audit/v2/tuning_log.csv` kèm mã băm mã nguồn |
| R6 | Precision@K, Recall@K, NDCG@K (giữ HR@K); **Full Ranking** trên tập ứng viên gồm cả sản phẩm mới; chỉ số theo nhóm sản phẩm cũ/mới |
| R7 | Triển khai được: demo web suy diễn bằng đúng mô hình của đánh giá cuối |
| R8 | Báo cáo khớp code và file kết quả (số liệu qua macro tự sinh) |
| R9 | Kết luận lấy trên **mẫu khách hàng độc lập** (mẫu B), mở tập kiểm thử đúng một lần theo kế hoạch đăng ký trước |

## 3. Phạm vi

**Trong phạm vi**

- Dữ liệu H&M: hai mẫu khách hàng không giao nhau, khoảng 500 nghìn giao dịch mỗi mẫu.
- Đặc trưng sản phẩm (thuộc tính, mô tả văn bản), khách hàng (thuộc tính) và thời gian (doanh số, tuổi sản phẩm, khoảng
  cách lần mua) — tính theo thời điểm.
- Khởi đầu lạnh của **sản phẩm**: sản phẩm mới nằm trong tập ứng viên và được đánh giá riêng theo nhóm cũ/mới.
- 14 mô hình cùng ngân sách tinh chỉnh; 5 seed; kiểm định có hiệu chỉnh Holm; ablation 5 thành phần của NeuMF-F.
- Demo web suy diễn bằng đúng mô hình của đánh giá cuối.

**Ngoài phạm vi**

- Khởi đầu lạnh của **khách hàng** (chưa có lịch sử mua): demo dùng gợi ý theo luật, gắn nhãn rõ là không phải mô hình.
- Ảnh và giá sản phẩm; biểu diễn mô tả bằng mô hình ngôn ngữ (BERT, Transformer) — đề tài dùng TF-IDF + SVD.
- Mô hình chuỗi (SASRec), mô hình đồ thị (LightGCN), tự mã hoá biến phân (Mult-VAE) — hướng phát triển (báo cáo mục 5.3).
- Toàn bộ H&M: Full Ranking trên toàn bộ danh mục vượt khả năng máy của nhóm (mục 4.1).
- Tìm siêu tham số tự động; triển khai production.

## 4. Dữ liệu

### 4.1 Nguồn và lý do lấy mẫu

Cuộc thi Kaggle H&M Personalized Fashion Recommendations:

| File | Nội dung | Dùng |
|---|---|---|
| `transactions_train.csv` | 31.788.324 giao dịch, 20/09/2018 → 22/09/2020 | `customer_id`, `article_id`, `t_dat` (ngày mua) |
| `articles.csv` | 105.542 sản phẩm | 11 thuộc tính danh mục, tên và mô tả |
| `customers.csv` | 1.371.980 khách | tuổi, trạng thái hội viên, tần suất nhận tin, FN, Active |

Không dùng giá, kênh bán, mã bưu chính; ảnh chỉ hiển thị trên demo. `article_id` đọc dạng chuỗi và `zfill(10)` để giữ
số 0 đầu.

Full Ranking phải chấm **mọi** sản phẩm ứng viên cho mỗi khách. Trên toàn bộ H&M, ngay cả với k = 10 vẫn còn 633.130
khách × 80.265 sản phẩm — hàng chục tỷ cặp cho mỗi mô hình — vượt khả năng máy của nhóm (RAM 16 GB). Vì vậy đề tài lấy
mẫu **theo khách hàng** và giữ trọn lịch sử hai năm của khách được chọn; lấy theo dòng sẽ cắt vụn lịch sử từng khách.

### 4.2 Hai mẫu khách hàng

| | Mẫu phát triển A | Mẫu kiểm định B |
|---|---|---|
| File (`data/processed/hm/`) | `hm500k_transactions.csv` | `hm500k_b_transactions.csv` |
| Nhóm băm `customer_id` (trên 100.000) | [0, 1597) | [1597, 3160) |
| Giao dịch | 500.269 | 500.125 |
| Khách | 21.599 | 21.030 |
| Dùng cho | Tinh chỉnh — chỉ trên tập xác thực | Đánh giá cuối — mở tập kiểm thử đúng một lần |

Hai đoạn nhóm băm không chồng nhau nên **không có khách chung**. Lấy mẫu bằng hàm băm với khoá cố định nên chạy lại luôn
ra đúng cùng file (MD5 ghi trong `audit/PREREG_v2.md` mục 1). Mẫu A cũng là mẫu của giao thức v1, nên tập kiểm thử của
A đã bị xem nhiều lần — đó là lý do cần mẫu B.

### 4.3 Tiền xử lý

1. **Gộp** giao dịch lặp thành cặp (khách, sản phẩm) duy nhất, giữ **ngày mua đầu** (mẫu A: 500.269 giao dịch →
   429.964 cặp).
2. **Lọc 10-core** lặp tới hội tụ, **chỉ trên các cặp có ngày mua đầu trước mốc kiểm thử 29/07/2020** — việc chọn khách
   và sản phẩm không dùng thông tin của giai đoạn kiểm thử. Chọn k = 10 thay vì 5 vì giới hạn RAM: ở k = 5, danh mục mẫu
   A còn 23.067 sản phẩm và Full Ranking ước tính cần khoảng 10,7 GB RAM. Hệ quả: dữ liệu thiên về khách mua nhiều.
3. **Phản hồi nhị phân**: mua = 1.

### 4.4 Giai đoạn đánh giá, sản phẩm mới và tập ứng viên

| | Giai đoạn xác thực | Giai đoạn kiểm thử |
|---|---|---|
| Mốc τ | 01/07/2020 | 29/07/2020 |
| Cửa sổ sản phẩm đúng | 01/07 – 28/07/2020 (4 tuần) | 29/07 – 22/09/2020 (8 tuần) |
| Dữ liệu huấn luyện | Cặp đã lọc có ngày mua đầu trước τ | Như vậy — nên gồm cả cửa sổ xác thực |
| Dùng cho | Chọn cấu hình (mẫu A); chọn số epoch (mẫu B) | Kết luận (chỉ mẫu B) |

- **Sản phẩm cũ:** có ít nhất một cặp huấn luyện, nên có embedding ID.
- **Sản phẩm mới:** có trong danh mục nhưng chưa từng bán trên toàn H&M trước τ. **Giả định:** doanh nghiệp biết trước
  danh mục sắp bán (có thuộc tính, mô tả) nhưng không biết sản phẩm nào sẽ bán được. Trong mẫu A, 27% cặp mua lần đầu
  trong cửa sổ kiểm thử là sản phẩm mới — bỏ chúng đi (như v1) là đánh giá một bài toán dễ hơn thực tế.
- **Tập ứng viên** của một khách = sản phẩm cũ ∪ sản phẩm mới, trừ món khách đã mua trước τ.
- **Sản phẩm đúng** = món khách mua lần đầu trong cửa sổ và thuộc tập ứng viên. Một khách có thể có nhiều sản phẩm
  đúng; chỉ khách có dữ liệu huấn luyện mới được đánh giá. Món đã mua trước τ không bao giờ là sản phẩm đúng — mô hình
  dự đoán món **mới đối với khách**.
- Mẫu A ở giai đoạn xác thực: 7.134 khách, 19.228 sản phẩm (9.596 có ID); 2.229 khách được đánh giá với 7.074 cặp
  đúng, trong đó 930 cặp là sản phẩm mới.
- Mẫu B ở giai đoạn kiểm thử (`outputs/v2/final/data.json`): 7.038 khách, 19.109 sản phẩm (9.478 có ID, 7.372
  sản phẩm mới); 2.991 khách được đánh giá với 12.206 cặp đúng, trong đó 6.080 cặp (49,8%) là sản phẩm mới; trung bình
  16.814 sản phẩm ứng viên mỗi khách.

**Không chia leave-one-out** (cách của He et al., 2017): cách này để lọt thông tin tương lai (Meng et al., 2020). Đo
trên mẫu A ở giai đoạn phát triển, tính trung bình theo người dùng: 11,2% tương tác trong tập huấn luyện xảy ra sau ngày
mua sản phẩm kiểm thử của người dùng đó; 60,9% người dùng có sản phẩm xác thực và sản phẩm kiểm thử mua cùng một ngày.

### 4.5 Đặc trưng theo thời điểm

| Nhóm | Đặc trưng | Mã hoá |
|---|---|---|
| Sản phẩm — thuộc tính | 11 thuộc tính danh mục: loại, nhóm sản phẩm, hoạ tiết, nhóm màu, độ đậm màu, màu chủ đạo, bộ phận, chỉ mục, nhóm chỉ mục, khu, nhóm may mặc | Embedding 8 chiều mỗi thuộc tính (88 chiều) |
| Sản phẩm — văn bản | Tên và mô tả chi tiết | TF-IDF (từ đơn và cặp từ) → SVD 64 chiều → chuẩn hoá L2 |
| Sản phẩm — thời gian tại t | Doanh số toàn H&M trong 7, 28, 91 ngày trước t; tuổi sản phẩm; cờ "chưa từng bán trước t" | log(1 + x)/10; cờ 0/1 (5 chiều) |
| Khách — tĩnh | Nhóm tuổi, trạng thái hội viên, tần suất nhận tin, FN, Active | Embedding 8 chiều mỗi thuộc tính (40 chiều) |
| Khách — thời gian tại t | Số ngày từ lần mua gần nhất; số cặp đã mua | log(1 + x)/10 (2 chiều) |

- Đặc trưng tại ngày t chỉ dùng dữ liệu **trước** t. Khi huấn luyện, mỗi cặp dương mang chính ngày mua đầu của nó; khi
  đánh giá, t = τ. Có test tự động kiểm tra điều này.
- Doanh số lấy trên toàn bộ giao dịch H&M (dữ liệu doanh nghiệp có tại thời điểm dự đoán), không chỉ trong mẫu.
- TF-IDF và SVD khớp trên toàn bộ danh mục — phù hợp giả định "biết trước danh mục"; phép khớp không dùng dữ liệu mua.
- Code: `scripts/21_build_features.py`, `src/data_pipeline/features.py`.

## 5. Mô hình

### 5.1 NeuMF-F — mô hình đề tài (`src/models/hybrid_features.py`)

Mỗi nhánh b ∈ {G (GMF), M (MLP)} có embedding ID $P^b$, $Q^b$ và hai phép chiếu tuyến tính $W^b_U$, $W^b_I$ (không hệ
số chệch). Vector của khách u và sản phẩm i tại ngày t:

$$p^b_u(t) = P^b_u + W^b_U\, x_u(t), \qquad q^b_i(t) = m_i\, Q^b_i + W^b_I\, x_i(t)$$

- $x_u(t)$, $x_i(t)$: vector đặc trưng của khách và sản phẩm (mục 4.5). Embedding thuộc tính dùng chung cho hai nhánh;
  phép chiếu riêng từng nhánh.
- $m_i = 1$ với sản phẩm cũ, $m_i = 0$ với sản phẩm mới — khi đó vector chỉ còn phần đặc trưng, nhờ vậy NeuMF-F chấm
  được sản phẩm chưa từng bán. Khi huấn luyện, $m_i$ bị đặt về 0 ngẫu nhiên với xác suất ρ ∈ {0; 0,25; 0,5} (**bỏ ID
  ngẫu nhiên**, ý tưởng từ DropoutNet) để mô hình học cách chấm khi thiếu ID. ρ là siêu tham số: tinh chỉnh chọn ρ = 0
  cho NeuMF-F (không dùng) và ρ = 0,5 cho MLP-F.
- **Nhánh GMF-F:** $\phi^G = p^G_u \odot q^G_i$ (nhân từng phần tử — tương tác tuyến tính).
- **Nhánh MLP-F:** nối $[p^M_u ; q^M_i]$ rồi qua tháp [2d → d → d/2 → d/4], ReLU, dropout (tương tác phi tuyến).
- **Hợp nhất sớm:** $\hat{y}_{ui} = \sigma\big(h^\top [\phi^G ; \phi^M_L]\big)$. Khi xếp hạng dùng logit (trước sigmoid)
  vì sigmoid float32 bão hoà tạo điểm bằng nhau giả.
- **Huấn luyện:** binary cross-entropy với mẫu âm lấy lại mỗi epoch, chỉ trong các sản phẩm đã ra mắt tại ngày t của cặp
  dương, trừ món khách đã mua; Adam, batch 512, tối đa 20 epoch, dừng sớm sau 5 epoch không cải thiện NDCG@10 xác thực.

**Early / late fusion** theo luận án của GVHD (Hồ Thị Linh, 2023): *early fusion* nối biểu diễn của các view rồi dùng
**một** mô hình dự đoán — NeuMF và NeuMF-F thuộc loại này; *late fusion* cho mỗi view một mô hình riêng rồi gộp điểm —
LateFusion-F. MLP-F đứng riêng là mô hình DNN thuần, không phải hợp nhất MF + DNN.

### 5.2 Mô hình đối chứng

| Nhóm | Mô hình | Ghi chú |
|---|---|---|
| Cận dưới | Random | Điểm ngẫu nhiên |
| Phổ biến | Most Popular | Số cặp trong tập huấn luyện của mẫu; sản phẩm mới xếp cuối |
| | MostPopular-Recent | Số giao dịch toàn H&M trong W ngày trước mốc |
| Nội dung | Content | Hồ sơ khách = trung bình có trọng số theo độ mới của vector nội dung sản phẩm đã mua; cosine |
| Láng giềng | ItemKNN, UserKNN | Cosine trên vector mua nhị phân, hệ số co, top-k láng giềng |
| MF | BPR-MF | MF tối ưu thứ hạng theo cặp (Rendle et al., 2009), chỉ dùng ID |
| Chỉ dùng ID | GMF, MLP, NeuMF | Kiến trúc NCF gốc (He et al., 2017) |
| Có đặc trưng | GMF-F, MLP-F | NeuMF-F chỉ giữ một nhánh |
| Hợp nhất muộn | LateFusion-F | w · minmax(GMF-F) + (1 − w) · minmax(MLP-F), hai mô hình huấn luyện riêng |

Mô hình chỉ dùng ID (Most Popular, ItemKNN, UserKNN, BPR-MF, GMF, MLP, NeuMF) cho sản phẩm mới điểm −∞, tức xếp cuối
danh sách — đúng giới hạn của lọc cộng tác thuần mà giao thức muốn đo.

**Ablation NeuMF-F** (cùng siêu tham số, tắt một thành phần): bỏ vector văn bản, bỏ đặc trưng thời gian, bỏ thông tin
khách, bỏ thuộc tính sản phẩm, bỏ cơ chế bỏ ID ngẫu nhiên (ρ = 0). Chỉ seed 42, chỉ mô tả. Vì NeuMF-F đã chọn ρ = 0,
 biến thể cuối trùng hệt bản đầy đủ và không mang thông tin.

## 6. Đánh giá và kiểm định

### 6.1 Full Ranking và độ đo

- Chấm toàn bộ tập ứng viên của từng khách (giai đoạn xác thực của mẫu A: trung bình khoảng 19 nghìn sản phẩm). Hoà
  điểm phá bằng khoá giả ngẫu nhiên tất định (seed 2026). Trung bình theo khách.
- **Độ đo chính: NDCG@10** trên tập kiểm thử của mẫu B. Độ đo phụ: Recall@10, HR@10, Precision@10, NDCG@5, NDCG@20.
- **Theo nhóm sản phẩm:** NDCG@10 riêng cho sản phẩm đúng cũ và mới; hạng lấy trong cùng danh sách xếp hạng đầy đủ.
- **Độ nhạy "chỉ sản phẩm cũ":** cùng các mô hình đã huấn luyện, chấm lại với ứng viên và sản phẩm đúng chỉ gồm sản
  phẩm cũ (gần với giao thức v1).
- **Mô tả thêm** (seed 42): độ phủ danh mục của top-10, tỉ lệ sản phẩm mới trong top-10, thời gian huấn luyện.

Với $T_u$ là tập sản phẩm đúng của khách u, $\text{hits}_u$ là số sản phẩm đúng trong top-K, $r$ là hạng (từ 1):

| Độ đo | Công thức (trung bình theo khách) |
|---|---|
| HR@K | $\mathbb{1}[\text{hits}_u \ge 1]$ |
| Precision@K | $\text{hits}_u / K$ |
| Recall@K | $\text{hits}_u / \lvert T_u \rvert$ |
| NDCG@K | $\dfrac{\sum_{i \in T_u,\, r_i \le K} 1/\log_2(r_i + 1)}{\sum_{j=1}^{\min(\lvert T_u \rvert, K)} 1/\log_2(j + 1)}$ |

Công thức cài ở `src/evaluation/metrics.py`, có unit test tính tay.

### 6.2 Tinh chỉnh và đánh giá cuối

- **Tinh chỉnh** (`scripts/22_tune_v2.py`): chỉ trên tập xác thực của mẫu A, seed 42. Mỗi mô hình có học thử 6 cấu hình
  (cấu hình mặc định + 5 cấu hình rút ngẫu nhiên cố định từ lưới) — cùng ngân sách cho mọi mô hình; mô hình một tham số
  thử đủ lưới. Lưới: `audit/PREREG_v2.md` mục 4.
- **Đánh giá cuối** (`scripts/23_final_v2.py`): cấu hình tốt nhất của mẫu A, giữ nguyên; 5 seed (42, 2024, 2025, 2026,
  3407). Mạng nơ-ron chọn số epoch trên tập xác thực của B rồi huấn luyện lại từ đầu trên mọi cặp trước 29/07/2020;
  BPR-MF và các baseline không học khớp trên mọi cặp trước 29/07/2020; LateFusion-F trộn đúng GMF-F và MLP-F của cùng
  seed.

### 6.3 Kiểm định

- Với mỗi khách, lấy NDCG@10 trung bình qua 5 seed. So sánh từng cặp bằng **Wilcoxon signed-rank** ghép cặp theo khách
  và **khoảng tin cậy bootstrap 95%** của hiệu trung bình (10.000 lần, seed 0).
- **Họ 10 so sánh** cố định (mục 1), hiệu chỉnh **Holm** trên cả họ, α = 0,05.
- Chỉ viết "A tốt hơn B" khi **đồng thời**: p sau Holm < 0,05, khoảng tin cậy không chứa 0, chênh lệch tương đối
  NDCG@10 ≥ 5%. Ngược lại: "không khác biệt có ý nghĩa".
- Nhóm cũ/mới, ablation, "chỉ sản phẩm cũ": báo cáo trung bình và khoảng tin cậy, không kiểm định, không dùng để kết
  luận chính.

## 7. Quy trình chống thiên lệch

1. **Đăng ký trước:** mô hình, lưới, seed, độ đo, họ so sánh, tiêu chí nằm trong `audit/PREREG_v2.md`, commit trước đánh
   giá cuối. Lệch kế hoạch ghi ở mục 10 của file đó và trong báo cáo.
2. **Tách vai trò dữ liệu:** mọi quyết định dựa trên mẫu A; kết luận chỉ dựa trên tập kiểm thử của mẫu B — khách chưa
   từng được dùng cho quyết định nào.
3. **Khoá kiểm thử:** `23_final_v2.py` từ chối chạy khi kế hoạch chưa commit, có file đã theo dõi bị sửa mà chưa commit,
   hoặc mã băm mã nguồn khác lúc tinh chỉnh; mỗi lần mở tập kiểm thử ghi một dòng `audit/test_access_log.csv` trước khi chấm.
4. **Không dùng thông tin tương lai:** k-core trước mốc kiểm thử, đặc trưng theo thời điểm, mẫu âm trong sản phẩm đã ra
   mắt — có test tự động (`tests/test_v2.py`).
5. **So sánh công bằng:** cùng dữ liệu, cùng tập ứng viên, cùng quy tắc loại món đã mua, cùng ngân sách tinh chỉnh
   (theo khuyến nghị của Rendle et al., 2020 và Ferrari Dacrema et al., 2019).
6. **Không gõ tay số:** số trong báo cáo sinh tự động từ file kết quả qua macro; chưa có thì hiện "[chưa có]".
7. **Bài báo chỉ là cơ sở phương pháp:** không so số của đề tài với số công bố (khác dữ liệu, cách chia, giao thức), không
   đặt cạnh kết quả cuộc thi Kaggle (MAP@12, độ đo và giao thức khác).

## 8. Kết quả ở đâu

| Kết quả | File | Báo cáo |
|---|---|---|
| Tinh chỉnh (mẫu A, tập xác thực) — chỉ để chọn cấu hình | `audit/v2/tuning_log.csv`, `audit/v2/best_configs.json` | Mục 4.3 |
| Đánh giá cuối (mẫu B, tập kiểm thử) | `outputs/v2/final/` (`summary.csv`, `significance.csv`, `ablation.csv`, `beyond.csv`, `ket_qua.txt`) | Mục 4.4 |
| Lịch sử v1 | lịch sử git, commit `9799f1a` | Mục 4.5 |

**Tóm tắt kết quả đánh giá cuối** (test mẫu B, 04/10/2026, 5 seed, NDCG@10):

| Mô hình | NDCG@10 | Mô hình | NDCG@10 |
|---|---|---|---|
| LateFusion-F | 0,01753 | ItemKNN | 0,01027 |
| GMF-F | 0,01561 | Most Popular | 0,01004 |
| **NeuMF-F** | 0,01470 | MostPopular-Recent | 0,00995 |
| UserKNN | 0,01305 | MLP | 0,00985 |
| BPR-MF | 0,01206 | MLP-F | 0,00978 |
| NeuMF | 0,01071 | GMF | 0,00967 |
| Content | 0,00384 | Random | 0,00031 |

- Họ 10 so sánh: NeuMF-F **tốt hơn** NeuMF, MLP-F, BPR-MF, ItemKNN, MostPopular-Recent, Content; **không khác biệt có ý
  nghĩa** với GMF-F, UserKNN; **LateFusion-F tốt hơn** NeuMF-F. NeuMF vs BPR-MF: không khác biệt có ý nghĩa.
- Phần hơn của mô hình có đặc trưng nằm ở sản phẩm cũ; trên sản phẩm mới mọi mô hình đều rất thấp (cao nhất Content).
- Ablation: đặc trưng thời gian đóng góp nhiều nhất (bỏ đi −30%).

Bảng dạng chữ: `outputs/v2/final/ket_qua.txt`. Tình trạng thực hiện và đối chiếu 17 góp ý: `../tong_hop_thay_doi_v2.md`.

## 9. Hạn chế đã biết

| Hạn chế | Ghi chú |
|---|---|
| Quy mô dữ liệu | Hai mẫu, mỗi mẫu khoảng 1,5% khách của H&M |
| k-core = 10 | Chọn vì giới hạn RAM; dữ liệu thiên về khách mua nhiều |
| Giả định về danh mục | Sản phẩm mới trong tập ứng viên dựa trên giả định biết trước danh mục sắp bán |
| Thuộc tính khách | `customers.csv` không có mốc thời gian — coi là ít thay đổi |
| k-core ở giai đoạn xác thực | Lọc dùng mọi cặp trước mốc kiểm thử, nên tập khách/sản phẩm ở giai đoạn xác thực phụ thuộc một phần dữ liệu tháng 7/2020 — chỉ ảnh hưởng việc chọn cấu hình trên A, không ảnh hưởng tập kiểm thử của B |
| Một mẫu kiểm định | Khoảng 3 nghìn khách có sản phẩm đúng; một khung thời gian (07–09/2020); một bộ dữ liệu |
| Phạm vi đặc trưng | Chưa dùng ảnh, giá, chuỗi hành vi; văn bản chỉ TF-IDF + SVD |
| Ablation | Một seed, chỉ mô tả; biến thể "bỏ ID ngẫu nhiên" không mang thông tin vì NeuMF-F đã chọn ρ = 0 |
| Sản phẩm mới | Đưa được vào đánh giá nhưng NDCG@10 trên nhóm này của mọi mô hình rất thấp (≤ 0,0018) |
| Phần cứng | Mạng nơ-ron chạy trên CPU và GPU có thể lệch nhẹ ở chữ số cuối; máy chạy được ghi tự động trong kết quả |

## 10. Lịch sử: giao thức v1

Giai đoạn phát triển (tập kiểm thử của mẫu A được chấm các ngày 27/09, 29/09 và 02/10/2026) dùng:

- mẫu A, một mốc thời gian chung, tập ứng viên **không** có sản phẩm mới;
- mô hình chỉ dùng ID: GMF, MLP, NeuMF-Scratch, NeuMF-Pretrained (có pre-training), BPR-MF, Most Popular, Random;
  phần mở rộng thêm late fusion (GMF + MLP, BPR-MF + MLP), ItemKNN, UserKNN;
- 3 seed, họ 8 so sánh có hiệu chỉnh Holm.

Kết luận v1: BPR-MF có NDCG@10 cao nhất; không biến thể NeuMF nào tốt hơn BPR-MF có ý nghĩa (0/8 so sánh đạt tiêu
chí); pre-training không cho lợi ích có ý nghĩa.

v1 được thay bằng v2 vì bốn vấn đề (`audit/PREREG_v2.md` mục 0): tập kiểm thử của A đã xem nhiều lần; k-core dùng dữ liệu
giai đoạn kiểm thử; sản phẩm mới bị loại khỏi đánh giá; mô hình chỉ dùng ID không tận dụng thông tin sản phẩm, khách,
thời gian. **Không đặt số v1 cạnh số v2** — khác tập ứng viên và khác sản phẩm đúng.

Tài liệu v1: kế hoạch `audit/PREREG.md`, báo cáo mục 4.5; mã nguồn, kết quả và lệnh tái lập nằm trong lịch sử git
(commit `9799f1a`).

## 11. Tài liệu tham khảo chính

- He, X., Liao, L., Zhang, H., Nie, L., Hu, X., & Chua, T.-S. (2017). Neural Collaborative Filtering. *WWW*.
- Rendle, S., Freudenthaler, C., Gantner, Z., & Schmidt-Thieme, L. (2009). BPR: Bayesian Personalized Ranking from
  Implicit Feedback. *UAI*.
- Sarwar, B., Karypis, G., Konstan, J., & Riedl, J. (2001). Item-based Collaborative Filtering Recommendation
  Algorithms. *WWW*.
- Resnick, P., Iacovou, N., Suchak, M., Bergstrom, P., & Riedl, J. (1994). GroupLens: An Open Architecture for
  Collaborative Filtering of Netnews. *CSCW*.
- Volkovs, M., Yu, G., & Poutanen, T. (2017). DropoutNet: Addressing Cold Start in Recommender Systems. *NIPS*.
- Salton, G., & Buckley, C. (1988). Term-weighting Approaches in Automatic Text Retrieval. *Information Processing and
  Management*.
- Deerwester, S., Dumais, S. T., Furnas, G. W., Landauer, T. K., & Harshman, R. (1990). Indexing by Latent Semantic
  Analysis. *JASIS*.
- Hồ Thị Linh (2023). *Multi-Source Integration for Recommendation Systems*. Luận án tiến sĩ, Trường Đại học Tôn Đức
  Thắng.
- Rendle, S., Krichene, W., Zhang, L., & Anderson, J. (2020). Neural Collaborative Filtering vs. Matrix Factorization
  Revisited. *RecSys*.
- Ferrari Dacrema, M., Cremonesi, P., & Jannach, D. (2019). Are We Really Making Much Progress? A Worrying Analysis of
  Recent Neural Recommendation Approaches. *RecSys*.
- Meng, Z., McCreadie, R., Macdonald, C., & Ounis, I. (2020). Exploring Data Splitting Strategies for the Evaluation of
  Recommendation Models. *RecSys*.
- Krichene, W., & Rendle, S. (2020). On Sampled Metrics for Item Recommendation. *KDD*.
- Wilcoxon, F. (1945). Individual Comparisons by Ranking Methods. *Biometrics Bulletin*.
- Holm, S. (1979). A Simple Sequentially Rejective Multiple Test Procedure. *Scandinavian Journal of Statistics*.
- Efron, B., & Tibshirani, R. J. (1993). *An Introduction to the Bootstrap*. Chapman & Hall.
- Kaggle — H&M Personalized Fashion Recommendations:
  https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations
