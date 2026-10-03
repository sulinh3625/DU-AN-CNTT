# Chuẩn bị vấn đáp — Mô hình khuyến nghị lai trên dữ liệu H&M

File này giúp trả lời 17 góp ý của cô trong buổi họp. Mỗi câu có: **Trả lời** (ý chính, nói trong 1–2 phút) và
**Mở ở đâu** (mục trong báo cáo hoặc file trong repo).

> **Quy tắc tránh nói sai**
> - Kết quả cuối trên mẫu B **chưa có** (chờ chạy đánh giá cuối). Trước khi có số: chỉ nói phương pháp, không đoán kết
>   quả, không nói "NeuMF-F tốt hơn".
> - Không so số của đề tài với số trong bài báo (khác dữ liệu, khác cách chia, khác cách đánh giá).
> - Không gọi MLP đứng riêng là "early fusion" (đó là mạng DNN thuần).
> - Số của giai đoạn phát triển (v1) chỉ nhắc khi được hỏi về lịch sử; số v1 và số v2 không đặt cạnh nhau.

---

## Phần A. Nắm nhanh đề tài trong 1 phút

- **Bài toán:** gợi ý Top-K sản phẩm thời trang cho từng khách hàng, dựa trên lịch sử mua (không có điểm đánh giá).
- **Dữ liệu:** H&M Personalized Fashion Recommendations — 31,8 triệu giao dịch (20/09/2018 → 22/09/2020), danh mục
  105.542 sản phẩm, thông tin 1.371.980 khách hàng.
- **Mô hình đề tài — NeuMF-F:** giữ cấu trúc của NeuMF (nhánh MF + nhánh mạng nơ-ron sâu, hợp nhất ở lớp dự đoán), nhưng
  mỗi khách hàng/sản phẩm được biểu diễn bằng **mã ID + đặc trưng** (thuộc tính và mô tả sản phẩm, thông tin khách hàng,
  doanh số và thời gian). Nhờ có đặc trưng, mô hình chấm điểm được cả **sản phẩm mới** chưa ai mua.
- **Cách đánh giá:** hai nhóm khách hàng khác nhau hoàn toàn. **Mẫu A** dùng để chọn cấu hình (tinh chỉnh). **Mẫu B**
  dùng để chấm điểm cuối cùng, chỉ một lần, theo kế hoạch đã ghi sẵn từ trước (`audit/PREREG_v2.md`).
- **So sánh với:** NeuMF chỉ dùng mã ID, từng nhánh đứng riêng, cách hợp nhất muộn, và 7 mô hình đối chứng (baseline).

**Vài từ cần giải thích được:**

| Từ | Nghĩa đơn giản |
|---|---|
| Embedding ID | Vector học được cho mỗi mã khách/mã sản phẩm từ lịch sử mua |
| Đặc trưng | Thông tin mô tả: loại, màu, nhóm hàng, mô tả chữ, doanh số gần đây, tuổi khách… |
| Sản phẩm cũ / mới | Cũ: đã có người mua trong dữ liệu huấn luyện. Mới: chưa từng bán trước thời điểm dự đoán |
| Early fusion (hợp nhất sớm) | Nối biểu diễn của các nguồn rồi cho **một** mô hình dự đoán — NeuMF, NeuMF-F |
| Late fusion (hợp nhất muộn) | Mỗi mô hình dự đoán riêng, rồi trộn điểm — LateFusion-F |
| NDCG@10 | Điểm chất lượng của 10 gợi ý đầu: món đúng càng ở trên càng được nhiều điểm (0 → 1) |

---

## Phần B. Số liệu cần nhớ (chỉ những số đã chắc chắn)

| Nội dung | Giá trị | Mở ở đâu |
|---|---|---|
| Mẫu A (tinh chỉnh) | 500.269 giao dịch của 21.599 khách | báo cáo mục 3.2.2 |
| Mẫu B (đánh giá cuối) | 500.125 giao dịch của 21.030 khách, **không có khách nào chung** với A | mục 3.2.2 |
| Mốc thời gian | Xác thực: 01/07–28/07/2020 (4 tuần). Kiểm thử: 29/07–22/09/2020 (8 tuần) | mục 3.2.4 |
| Sản phẩm mới | Ở mẫu A, 27% cặp mua lần đầu trong 8 tuần cuối là sản phẩm chưa từng bán trước 29/07/2020 | mục 3.2.4 |
| Mẫu A sau lọc (giai đoạn xác thực) | 7.134 khách; 19.228 sản phẩm (9.596 có mã ID, còn lại là sản phẩm mới); 2.229 khách được đánh giá, 7.074 cặp đúng (930 cặp là sản phẩm mới) | Bảng quy mô dữ liệu, mục 3.2.4 |
| Số mô hình, số lần chạy | 14 mô hình; 5 seed; họ 10 so sánh có hiệu chỉnh Holm | mục 3.6, 4.2 |
| Kết quả tinh chỉnh (tập xác thực của A, NDCG@10) | UserKNN 0,01216 · ItemKNN 0,01094 · BPR-MF 0,00934 · GMF 0,00845 · MostPopular-Recent 0,00830 · MLP 0,00797 · Most Popular 0,00734 · Content 0,00499. NeuMF, GMF-F, MLP-F, NeuMF-F, LateFusion-F: đang chạy | mục 4.3 |
| Kết quả cuối trên mẫu B | **Chưa có** — điền sau khi chạy đánh giá cuối | mục 4.4 |

Số tinh chỉnh chỉ dùng để **chọn cấu hình**, không dùng để kết luận mô hình nào tốt hơn.

---

## Phần C. Trả lời 17 góp ý

### 1. Kết quả có cao bất thường, có rò rỉ dữ liệu không?

**1a. Kết quả có cao bất thường không?**
Không. Bài toán rất khó nên điểm tuyệt đối thấp:
- mỗi khách chỉ có vài món đúng giữa khoảng 17–19 nghìn sản phẩm ứng viên;
- chỉ tính món **khách chưa từng mua**, và dự đoán cho 8 tuần sau.

Ở giai đoạn phát triển, NDCG@10 cao nhất chỉ khoảng 0,01. Điều cần xem là chênh lệch giữa các mô hình có ý nghĩa thống kê hay không, không phải độ lớn tuyệt đối.

**1b. Train/test chia thế nào?**
Chia theo **thời gian**, cùng một mốc cho mọi khách:
- trước 01/07/2020 để huấn luyện, 01/07–28/07 để xác thực (chọn cấu hình, chọn số epoch);
- từ 29/07 đến 22/09 để kiểm thử;
- trước khi chấm kiểm thử, mô hình được huấn luyện lại trên mọi dữ liệu trước 29/07.

Món khách đã mua trước mốc không được tính là món đúng. Mở ở đâu: mục 3.2.4.

**1c. Dữ liệu test có lọt vào huấn luyện không?**
Không. Có năm lớp bảo vệ:
1. Mỗi cặp (khách, sản phẩm) chỉ có một ngày mua đầu, nên không thể vừa ở tập huấn luyện vừa là món đúng.
2. Bước lọc dữ liệu (k-core) chỉ dùng dữ liệu trước mốc kiểm thử.
3. Đặc trưng tại ngày t chỉ dùng dữ liệu **trước** ngày t (ví dụ doanh số chỉ tính đến ngày t−1).
4. Mẫu B gồm khách khác hẳn mẫu A; tập kiểm thử của B chỉ mở một lần.
5. Chương trình chấm cuối có "khoá": từ chối chạy nếu kế hoạch chưa lưu, mã nguồn bị sửa hoặc khác lúc tinh chỉnh; mỗi lần chấm ghi nhật ký.

Có test tự động kiểm tra các điều trên. Mở ở đâu: mục 3.2.3–3.2.5, 3.6; `neumf_project/tests/test_v2.py`.

**1d. Có huấn luyện lại trước khi chấm không?**
Có. Với mỗi seed:
1. Huấn luyện trên dữ liệu trước 01/07, dừng sớm theo tập xác thực để biết số epoch tốt nhất.
2. Huấn luyện lại từ đầu trên mọi dữ liệu trước 29/07, đúng số epoch đó.
3. Chấm kiểm thử.

Tập kiểm thử không bao giờ dùng để dừng hay chọn mô hình. Mở ở đâu: mục 3.6.

**1e. Mẫu dương, mẫu âm tạo thế nào?**
- Mẫu dương: cặp (khách, sản phẩm) đã mua.
- Mẫu âm: với mỗi lượt mua, lấy ngẫu nhiên 4 hoặc 8 sản phẩm khách chưa mua. Với mô hình có đặc trưng, chỉ lấy trong sản phẩm **đã ra mắt** tính đến ngày mua (sản phẩm chưa bán thì khách không thể mua). Lấy lại mới mỗi epoch.
- Khi đánh giá thì không lấy mẫu: xếp hạng toàn bộ sản phẩm ứng viên.

Mở ở đâu: mục 3.4.1.

**1f. Sao không chia leave-one-out (lấy món mua cuối làm test)?**
Vì cách đó để lọt thông tin tương lai: dữ liệu huấn luyện chứa lượt mua của người khác xảy ra **sau** thời điểm cần dự đoán. Đo trên mẫu A: trung bình 11,2% tương tác huấn luyện xảy ra sau ngày của món test; 60,9% khách có món xác thực và món test mua cùng ngày. Mở ở đâu: mục 3.2.4 (Meng et al., 2020).

### 2. Có bộ test chuẩn chung cho mọi mô hình không?

Có. Cả 14 mô hình được chấm trên **cùng** tập kiểm thử của mẫu B:
- cùng tập ứng viên (sản phẩm cũ + sản phẩm mới), cùng cách phá hoà điểm;
- cùng 5 seed, cùng ngân sách tinh chỉnh (6 cấu hình mỗi mô hình).

Kết quả của từng khách được lưu lại nên so sánh được theo cặp (cùng một khách, hai mô hình). Mở ở đâu: mục 3.6, 4.1.

### 3. Top-K là gì? Top-K người dùng tương đồng xác định thế nào?

- **Top-K trong kết quả** là Top-K **sản phẩm**: chấm điểm mọi món khách chưa mua, sắp giảm dần, lấy K món đầu.
- **Top-K người dùng tương đồng** thuộc cách lọc cộng tác dựa trên láng giềng — mô hình **UserKNN**, đúng như Algorithm 3 trong luận án của cô:
  1. tính độ tương đồng cosine giữa hai khách theo các món mua chung;
  2. giữ k khách giống nhất (k = 200, chọn trên tập xác thực);
  3. điểm của một món = tổng độ tương đồng của các láng giềng đã mua món đó.
- **ItemKNN** làm tương tự theo sản phẩm (Algorithm 4).
- Cả hai là baseline chính thức.
- Demo có màn hình "10 khách tương đồng nhất" cho từng khách.

Mở ở đâu: mục 2.1.2 (công thức 2.1–2.3), 3.7.

### 4. Lọc cộng tác hoạt động thế nào? Có phải lấy món người khác mua để gợi ý trực tiếp?

Không hẳn. Có hai cách:
- **Dựa trên láng giềng (UserKNN):** tìm khách giống mình → lấy các món họ đã mua mà mình chưa mua → xếp theo độ giống.
- **Dựa trên mô hình (MF, NeuMF, NeuMF-F):** học một vector cho mỗi khách và mỗi sản phẩm từ toàn bộ lịch sử; khách mua giống nhau sẽ có vector gần nhau; điểm của một món tính từ hai vector.

NeuMF-F cộng thêm đặc trưng vào vector, nên chấm được cả món chưa ai mua. Mở ở đâu: mục 2.1.2, 3.3.1.

### 5. Khởi đầu lạnh (Cold Start)?

- **Sản phẩm mới — đề tài xử lý:**
  - sản phẩm chưa từng bán vẫn nằm trong danh sách ứng viên;
  - NeuMF-F chấm chúng bằng đặc trưng (thuộc tính, mô tả, thời gian) vì chúng chưa có vector ID;
  - khi huấn luyện, mã ID sản phẩm bị **bỏ ngẫu nhiên** để mô hình học cách chấm khi thiếu ID (ý tưởng của DropoutNet);
  - báo cáo có điểm riêng cho nhóm sản phẩm mới. Các mô hình chỉ dùng mã ID có điểm 0 ở nhóm này vì không chấm được.
- **Khách hàng mới (chưa mua gì) — ngoài phạm vi:** demo dùng gợi ý theo luật (lọc theo lựa chọn của khách rồi xếp theo độ phổ biến) và ghi rõ "không phải mô hình học".

Mở ở đâu: mục 2.1.4, 2.4.1, 3.3.1, 4.4.3.

### 6. NDCG và các chỉ số

**Công thức** (một khách có thể có nhiều món đúng; r là hạng của món đúng, bắt đầu từ 1):

| Chỉ số | Cách tính cho một khách | Ý nghĩa |
|---|---|---|
| HR@K | 1 nếu có ít nhất một món đúng trong top-K, ngược lại 0 | Có trúng không |
| Precision@K | số món đúng trong top-K / K | Bao nhiêu phần gợi ý là đúng |
| Recall@K | số món đúng trong top-K / tổng số món đúng | Tìm lại được bao nhiêu phần |
| NDCG@K | DCG@K / IDCG@K | Món đúng càng ở trên càng nhiều điểm, chuẩn hoá về 0–1 |

- DCG@K = tổng của 1/log₂(r + 1) trên các món đúng có r ≤ K.
- IDCG@K = DCG khi mọi món đúng đứng đầu danh sách.

**Ví dụ tính tay (nên thuộc).** Một khách có 3 món đúng ở hạng 2, 7 và 40; K = 10:
- HR@10 = 1; Precision@10 = 2/10 = 0,2; Recall@10 = 2/3 ≈ 0,667.
- DCG = 1/log₂3 + 1/log₂8 = 0,631 + 0,333 = 0,964.
- IDCG = 1 + 0,631 + 0,5 = 2,131.
- NDCG@10 = 0,964 / 2,131 ≈ 0,453.

**Cách tính trong đề tài:**
- Chỉ số chính: **NDCG@10** (đăng ký trước); phụ: Recall@10, HR@10, Precision@10, NDCG@5, NDCG@20.
- Lấy trung bình theo khách, rồi trung bình ± độ lệch chuẩn qua 5 seed.
- Có thêm NDCG@10 riêng cho nhóm **sản phẩm cũ** và **sản phẩm mới**.

**Nối với luận án của cô:**
- Luận án dùng MAE/RMSE (cho dự đoán điểm đánh giá), Precision/Recall, Hit rate và ARHR.
- H&M không có điểm đánh giá nên không dùng MAE/RMSE.
- HR@K chính là hit rate. NDCG cùng tinh thần ARHR: cả hai thưởng món đúng nằm cao; NDCG chiết khấu theo 1/log₂(r+1) và chuẩn hoá về 0–1.

Mở ở đâu: mục 2.5 (công thức 2.19–2.21); `neumf_project/src/evaluation/metrics.py`.

### 7. Trình bày kết quả theo chuẩn học thuật?

- Số thập phân (NDCG không nhân 100), 5 chữ số, dạng trung bình ± độ lệch chuẩn qua 5 seed, in đậm giá trị cao nhất mỗi cột.
- Có bảng kiểm định riêng: chênh lệch, khoảng tin cậy 95%, p sau hiệu chỉnh Holm, kết luận.
- Mọi bảng, hình, con số được chương trình **tự sinh** từ file kết quả, không gõ tay.
- Không đặt số của đề tài cạnh số trong bài báo, vì khác dữ liệu và cách đánh giá.

Mở ở đâu: mục 4.4; `neumf_project/scripts/24_report_v2.py`.

### 8. Vai trò của Matrix Factorization (MF)?

- Ma trận khách × sản phẩm rất thưa (mật độ khoảng 0,3% sau lọc).
- MF nén ma trận này thành hai bảng vector nhỏ: P (khách) và Q (sản phẩm); điểm dự đoán = tích vô hướng p_u · q_i. Nhờ vậy suy ra được điểm cho những ô chưa có dữ liệu.
- Trong đề tài:
  - **BPR-MF** là baseline MF;
  - **GMF** là MF dạng mạng nơ-ron (có trọng số riêng cho từng chiều);
  - trong NeuMF-F, nhánh **GMF-F** là MF trên vector có đặc trưng, nên còn học được tương tác giữa thuộc tính khách và thuộc tính sản phẩm.

Mở ở đâu: mục 2.2, 3.3.2.

### 9. Có thực sự xây mô hình lai không?

Có — **NeuMF-F**:
1. Mỗi nhánh (GMF và MLP) có vector khách = vector ID + chiếu của đặc trưng khách; vector sản phẩm = vector ID + chiếu của đặc trưng sản phẩm. Sản phẩm mới chưa có ID nên chỉ dùng phần đặc trưng.
2. Nhánh GMF-F nhân từng phần tử hai vector (tuyến tính); nhánh MLP-F nối hai vector rồi qua 3 tầng ẩn (phi tuyến).
3. Hai kết quả được nối lại, qua một lớp dự đoán chung → điểm.

Ba so sánh trả lời trực tiếp "lai có tác dụng không":
- **NeuMF-F với NeuMF chỉ dùng ID:** đặc trưng có giúp không.
- **NeuMF-F với GMF-F, MLP-F:** hợp nhất có hơn từng nhánh không.
- **NeuMF-F với LateFusion-F:** hợp nhất sớm hay muộn tốt hơn.

Kết quả: chờ đánh giá cuối. Mở ở đâu: mục 3.3 (Hình 3.2, công thức 3.7–3.10); `neumf_project/src/models/hybrid_features.py`.

### 10. Đã thử Transformer, Temporal, BERT chưa?

- **Đã dùng mô tả văn bản của sản phẩm:**
  - biểu diễn bằng TF-IDF rồi giảm còn 64 chiều (SVD);
  - nối vào vector của mô hình — cùng tinh thần chương 4 luận án của cô (vector MF + vector văn bản);
  - cách này nhẹ, chạy được trên máy không có GPU.
- **BERT** (thay TF-IDF) và **Transformer** (làm mô hình hợp nhất như chương 5 luận án): là hướng phát triển, vì chi phí tính toán lớn. Cô đã ghi phần này không bắt buộc.
- **Temporal Fusion Transformer** là mô hình dự báo chuỗi thời gian, không phải mô hình gợi ý Top-K.
- Mô hình theo chuỗi (SASRec, BERT4Rec) cần thứ tự mua chi tiết, mà H&M chỉ ghi ngày và nhiều món mua cùng giỏ.

Mở ở đâu: mục 2.4.1, 2.4.2, 5.3.

### 11. Có dùng yếu tố thời gian không?

Có, theo ba cách:
1. **Chia dữ liệu theo thời gian** (mục 1b).
2. **Làm đặc trưng đầu vào**, tính theo thời điểm:
   - sản phẩm: doanh số toàn H&M trong 7, 28, 91 ngày trước, tuổi sản phẩm;
   - khách: số ngày từ lần mua gần nhất, số món đã mua.
3. **Baseline MostPopular-Recent** (bán chạy trong W ngày gần nhất). Trên tập xác thực, cửa sổ 14 ngày tốt nhất (0,00830).

Phần ablation "bỏ đặc trưng thời gian" đo xem thời gian đóng góp bao nhiêu. Mở ở đâu: mục 3.2.5, 4.2, 4.4.4.

### 12–13. Early fusion và Late fusion

Định nghĩa theo luận án của cô (mục 1.1.2.2):

| Kiểu | Định nghĩa | Trong đề tài |
|---|---|---|
| **Early fusion** | Nối biểu diễn của các nguồn → **một** mô hình dự đoán | **NeuMF-F** (và NeuMF): nối vector nhánh GMF với vector nhánh MLP → một lớp dự đoán chung, huấn luyện chung. Đặc trưng cũng được đưa vào ngay từ vector |
| **Late fusion** | Mỗi nguồn một mô hình riêng → trộn kết quả | **LateFusion-F**: w × điểm GMF-F + (1 − w) × điểm MLP-F (điểm chuẩn hoá về 0–1), hai mô hình huấn luyện riêng, w chọn trên tập xác thực |
| Không phải fusion | — | **MLP đứng riêng** chỉ là mạng DNN thuần |

So sánh NeuMF-F với LateFusion-F (cùng hai thành phần) nằm sẵn trong 10 so sánh đã đăng ký trước. Mở ở đâu: mục 2.3.4 (Hình 2.2, công thức 2.13–2.15), 3.3.5.

### 14. Baseline gồm những gì? Lai có tốt hơn trước khi lai không?

| Nhóm | Mô hình |
|---|---|
| Đơn giản | Random, Most Popular, MostPopular-Recent |
| Theo nội dung | Content (gợi ý món giống món khách đã mua, theo mô tả và thuộc tính) |
| Láng giềng | ItemKNN, UserKNN |
| MF | BPR-MF |
| Chỉ dùng mã ID | GMF, MLP, NeuMF |
| Thành phần có đặc trưng | GMF-F, MLP-F |
| Mô hình đề tài | **NeuMF-F** (early fusion) |
| Hợp nhất muộn | LateFusion-F |

- "Lai có tốt hơn trước khi lai" = so sánh NeuMF-F với GMF-F và MLP-F.
- Chỉ nói "A tốt hơn B" khi **đủ cả ba** điều kiện: p sau hiệu chỉnh Holm < 0,05; khoảng tin cậy 95% không chứa 0; chênh lệch ≥ 5%. Tiêu chí này cố định từ trước khi chấm.

Mở ở đâu: mục 3.6, 4.2.

### 15. Sơ đồ kiến trúc

- **Hình 2.1** — kiến trúc NeuMF.
- **Hình 2.2** — hợp nhất sớm (NeuMF, NeuMF-F) so với hợp nhất muộn (LateFusion-F).
- **Hình 3.1** — luồng toàn hệ thống: dữ liệu → tiền xử lý và đặc trưng → giai đoạn đánh giá → mô hình → tinh chỉnh (mẫu A) → đánh giá cuối (mẫu B).
- **Hình 3.2** — kiến trúc NeuMF-F.
- **Hình 3.3** — kiến trúc ba tầng của demo.

Luồng cô gợi ý (dữ liệu → tiền xử lý → chia → ma trận → MF → vector → DL → hợp nhất → điểm → xếp hạng → Top-K) được Hình 3.1, 3.2 và 2.2 thể hiện đủ.

### 16. Mô hình "variational" nhắc trong buổi họp

- Chưa triển khai; **cần hỏi lại cô tên mô hình**, không tự khẳng định.
- Khả năng cao là Mult-VAE (Liang và cộng sự, 2018), đã trình bày lý thuyết ở mục 2.4.4.
- Nếu cô yêu cầu: vẫn thêm được **trước khi** chạy đánh giá cuối (tập kiểm thử của mẫu B chưa mở), tinh chỉnh trên mẫu A như mọi mô hình khác và ghi vào kế hoạch.

### 17. Lộ trình 10 bước — đã làm đến đâu?

| # | Bước | Trạng thái |
|---|---|---|
| 1 | Sửa cách chia Train/Test | Xong — chia theo thời gian, có sản phẩm mới |
| 2 | Kiểm tra rò rỉ dữ liệu | Xong — có test tự động |
| 3 | Bộ test chuẩn | Xong — mẫu B độc lập, khoá test |
| 4 | Chạy lại Baseline/MF | Xong phần tinh chỉnh |
| 5 | Mô hình Deep Learning | MLP, MLP-F |
| 6 | Xây mô hình lai | NeuMF-F |
| 7 | Thử Fusion | Early (NeuMF-F) và Late (LateFusion-F) |
| 8 | Bảng NDCG/HR/Recall/Precision | Chương trình tự sinh — chờ đánh giá cuối |
| 9 | Vẽ kiến trúc | Hình 3.1, 3.2 |
| 10 | Phân tích kết quả | Theo nhóm sản phẩm cũ/mới, ablation, độ phủ — chờ đánh giá cuối |

---

## Phần D. Câu hỏi khó nên chuẩn bị

**"Vì sao đổi cách làm gần cuối dự án? Kết quả cũ thế nào?"**
Giai đoạn phát triển (v1) cho thấy:
- NeuMF chỉ dùng mã ID **không** tốt hơn MF đã tinh chỉnh (BPR-MF cao nhất; 0/8 so sánh có ý nghĩa; tiền huấn luyện không giúp);
- sản phẩm mới bị bỏ khỏi đánh giá;
- tập kiểm thử cũ đã bị xem nhiều lần.

v2 sửa các điểm đó và lấy kết luận trên khách hàng mới hoàn toàn. Kết quả v1 vẫn được báo cáo trung thực ở mục 4.5, không trộn với v2.

**"Việc đã xem kết quả v1 có làm lệch v2 không?"**
Có ảnh hưởng ở mức ý tưởng: biết mô hình chỉ dùng mã ID không hơn MF nên bổ sung đặc trưng. Vì vậy kết luận chỉ lấy trên mẫu B — dữ liệu chưa ai xem — với kế hoạch ghi sẵn từ trước.

**"Nếu NeuMF-F thua UserKNN thì sao?"**
Báo cáo đúng như vậy; quy tắc này đã ghi trong kế hoạch. Điểm theo nhóm sản phẩm cũ/mới và ablation cho biết NeuMF-F hơn hay thua ở đâu, thành phần nào đóng góp. Kết quả âm cũng là kết quả có giá trị.

**"Giả định biết trước danh mục sắp bán có hợp lý không?"**
Cửa hàng tự lên kế hoạch hàng hoá nên biết sản phẩm sắp bán (thuộc tính, mô tả), nhưng không biết món nào bán chạy. Đây là giả định, đã ghi rõ ở mục 4.6 và trong kế hoạch.

**"Vì sao lọc k-core = 10, vì sao chỉ lấy mẫu 500 nghìn giao dịch?"**
Do bộ nhớ máy (16 GB RAM):
- chấm điểm toàn bộ sản phẩm cho mọi khách ở quy mô đầy đủ là hàng chục tỷ phép tính;
- với k = 5, ước tính cần khoảng 10,7 GB RAM.

Hệ quả: dữ liệu thiên về khách mua nhiều — đã ghi là hạn chế. Mở ở đâu: mục 3.2.1, 3.2.3, 5.2.

**"Có bị quá khớp (overfitting) không, xử lý thế nào?"**
- Dừng sớm theo NDCG@10 trên tập xác thực (dừng sau 5 epoch không cải thiện).
- Dropout trong tầng ẩn.
- Điều chuẩn L2 (weight decay).
- Bỏ ID ngẫu nhiên cũng giúp mô hình không học thuộc theo mã.

Khi huấn luyện lại, dừng đúng số epoch đã chọn. Mở ở đâu: mục 3.3.3, 3.5.1.

**"Vì sao 5 seed? Kiểm định thế nào?"**
- Kiểm định theo từng khách hàng (hàng nghìn khách), không theo seed. Mỗi khách lấy điểm trung bình qua 5 seed rồi so hai mô hình bằng Wilcoxon, kèm khoảng tin cậy bootstrap và hiệu chỉnh Holm cho 10 so sánh.
- Nếu kiểm định theo seed thì với 5 seed, p nhỏ nhất cũng chỉ 0,0625, không bao giờ dưới 0,05.

**"Demo dùng mô hình nào?"**
Đúng các mô hình của đánh giá cuối (seed 42), chỉ suy diễn, không huấn luyện lại. Số trên demo khớp file kết quả (có test tự động). Khách mới dùng gợi ý theo luật, có ghi rõ.

**"Có gì khác so với đề cương?"**

| Đề cương | Thực tế | Lý do |
|---|---|---|
| Chia leave-one-out | Chia theo thời gian | Leave-one-out lọt thông tin tương lai (câu 1f) |
| Baseline ALS | BPR-MF | Cùng nhóm MF cho phản hồi ẩn; iALS chỉ thử ở giai đoạn phát triển |
| Thử đặc trưng Category/Department | **Đã dùng** (11 thuộc tính sản phẩm) | — |
| K = 5/10/20 | Có đủ | — |
| Biểu đồ hội tụ (TensorBoard/W&B) | Ghi ra file CSV, vẽ bằng matplotlib | Cùng thông tin, truy vết được trong repo |
| Demo FastAPI + Streamlit | FastAPI + giao diện HTML | Chức năng tương đương |
| Báo cáo 6 chương | 5 chương | Gộp cài đặt và kết quả vào Chương 4 |
