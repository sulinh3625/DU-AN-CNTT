# Chuẩn bị vấn đáp — Mô hình khuyến nghị lai trên dữ liệu H&M

File này giúp trả lời 17 góp ý của cô trong buổi họp. Mỗi câu có: **Trả lời** (ý chính, nói trong 1–2 phút) và
**Mở ở đâu** (mục trong báo cáo hoặc file trong repo). Cập nhật theo kết quả đánh giá cuối ngày 10/10/2026 (bản cuối
giao thức v2, mẫu kiểm định khối 2).

> **Quy tắc tránh nói sai**
> - Kết quả cuối trên mẫu B **đã có** (10/10/2026). Nói đúng như sau: NeuMF-F **tốt hơn có ý nghĩa** NeuMF chỉ ID, MLP-F,
>   BPR-MF, ItemKNN, UserKNN, MostPopular-Recent, Content; **ngang** GMF-F và LateFusion-F; **không thua** mô hình nào.
>   **Không nói "NeuMF-F tốt nhất"** — NeuMF-F đứng 2/14, LateFusion-F có NDCG@10 cao hơn một chút (không có ý nghĩa).
> - **Không nói đề tài xử lý được khởi đầu lạnh của sản phẩm**: bản cuối bỏ sản phẩm chưa có người mua khỏi đánh giá.
>   Cũng không nói NeuMF-F "học chấm sản phẩm mới nhờ bỏ ID ngẫu nhiên": tinh chỉnh chọn ρ = 0 cho NeuMF-F (và MLP-F);
>   chỉ GMF-F chọn ρ = 0,25.
> - Một **sản phẩm** trong đề tài là một **mẫu thiết kế** (`product_code`, gộp mọi màu), không phải một `article_id`.
> - Không so số của đề tài với số trong bài báo (khác dữ liệu, khác cách chia, khác cách đánh giá).
> - Không gọi MLP đứng riêng là "early fusion" (đó là mạng DNN thuần).
> - Số của giai đoạn phát triển (v1) và của khối 1 (04/10) chỉ nhắc khi được hỏi về lịch sử; không đặt cạnh số bản cuối.

---

## Phần A. Nắm nhanh đề tài trong 1 phút

- **Bài toán:** gợi ý Top-K sản phẩm thời trang cho từng khách hàng, dựa trên lịch sử mua (không có điểm đánh giá).
- **Dữ liệu:** H&M Personalized Fashion Recommendations — 31,8 triệu giao dịch (20/09/2018 → 22/09/2020), danh mục
  105.542 sản phẩm (theo màu), thông tin 1.371.980 khách hàng. Đề tài gộp các màu của cùng một mẫu thành **một sản phẩm**
  (`product_code`).
- **Mô hình đề tài — NeuMF-F:** giữ cấu trúc của NeuMF (nhánh MF + nhánh mạng nơ-ron sâu, hợp nhất ở lớp dự đoán), nhưng
  mỗi khách hàng/sản phẩm được biểu diễn bằng **mã ID + đặc trưng** (thuộc tính và mô tả sản phẩm, thông tin khách hàng,
  doanh số và thời gian) — tức có thêm thông tin ngoài lịch sử mua.
- **Cách đánh giá:** hai nhóm khách hàng khác nhau hoàn toàn. **Mẫu A** dùng để chọn cấu hình (tinh chỉnh). **Mẫu B**
  dùng để chấm điểm cuối cùng, chỉ một lần, theo kế hoạch đã ghi sẵn từ trước (`audit/PREREG_v2.md`).
- **So sánh với:** NeuMF chỉ dùng mã ID, từng nhánh đứng riêng, cách hợp nhất muộn, và 7 mô hình đối chứng (baseline).
- **Kết quả một câu:** đặc trưng giúp rõ (NeuMF-F hơn NeuMF chỉ ID 43,8%), NeuMF-F hơn cả 5 baseline trong họ so sánh,
  nhưng cách ghép hai nhánh không tạo khác biệt có ý nghĩa so với nhánh GMF-F đứng riêng hay hợp nhất muộn.

**Vài từ cần giải thích được:**

| Từ | Nghĩa đơn giản |
|---|---|
| Embedding ID | Vector học được cho mỗi mã khách/mã sản phẩm từ lịch sử mua |
| Đặc trưng | Thông tin mô tả: loại, nhóm hàng, mô tả chữ, doanh số gần đây, tuổi khách… |
| Mẫu thiết kế (`product_code`) | Mã của một mẫu sản phẩm; các màu của cùng mẫu có `article_id` khác nhau nhưng chung `product_code` (= `article_id` bỏ 3 chữ số cuối) |
| Early fusion (hợp nhất sớm) | Nối biểu diễn của các nguồn rồi cho **một** mô hình dự đoán — NeuMF, NeuMF-F |
| Late fusion (hợp nhất muộn) | Mỗi mô hình dự đoán riêng, rồi trộn điểm — LateFusion-F |
| NDCG@10 | Điểm chất lượng của 10 gợi ý đầu: món đúng càng ở trên càng được nhiều điểm (0 → 1) |

---

## Phần B. Số liệu cần nhớ (chỉ những số đã chắc chắn)

| Nội dung | Giá trị | Mở ở đâu |
|---|---|---|
| Mẫu A (tinh chỉnh) | Khối 0: 500.269 giao dịch của 21.599 khách | báo cáo mục 3.2.2 |
| Mẫu B (đánh giá cuối) | Khối 2: 500.164 giao dịch của 21.351 khách, **không có khách nào chung** với A | mục 3.2.2 |
| Gộp theo mẫu thiết kế | Trước mốc kiểm thử: mẫu A 55.971 → 27.370 sản phẩm, 401.293 → 359.181 cặp; mẫu B 55.683 → 27.291 sản phẩm, 398.653 → 356.740 cặp | mục 3.2.3 |
| Sau lọc 10-core | Mẫu A: 8.039 khách, 6.801 sản phẩm, 245.644 cặp. Mẫu B: 7.994 khách, 6.749 sản phẩm, 243.696 cặp | mục 3.2.3, Bảng quy mô dữ liệu |
| Mốc thời gian | Xác thực: 01/07–28/07/2020 (4 tuần). Kiểm thử: 29/07–22/09/2020 (8 tuần) | mục 3.2.4 |
| Mẫu A ở giai đoạn xác thực | 2.569 khách được đánh giá, 8.636 cặp đúng, trung bình 6.762 ứng viên mỗi khách | Bảng quy mô dữ liệu |
| Số mô hình, số lần chạy | 14 mô hình; 5 seed; họ 10 so sánh có hiệu chỉnh Holm | mục 3.6, 4.2 |
| Kết quả tinh chỉnh (tập xác thực của A, NDCG@10) | LateFusion-F 0,03556 · NeuMF-F 0,03337 · MLP-F 0,03212 · GMF-F 0,03162 · GMF 0,02857 · UserKNN 0,02753 · MLP 0,02742 · NeuMF 0,02696 · BPR-MF 0,02636 · ItemKNN 0,02599 · MostPopular-Recent 0,02334 · Most Popular 0,02174 · Content 0,00459 | mục 4.3 |
| Tập kiểm thử mẫu B | 3.165 khách; 10.285 cặp đúng; trung bình 6.710 ứng viên mỗi khách | mục 4.1 |
| Kết quả cuối (test B, NDCG@10, 5 seed) | **LateFusion-F 0,04093** · **NeuMF-F 0,04003** · GMF-F 0,03902 · MLP-F 0,03480 · UserKNN 0,03114 · ItemKNN 0,02860 · NeuMF 0,02783 · MostPopular-Recent 0,02760 · GMF 0,02695 · BPR-MF 0,02661 · MLP 0,02373 · Most Popular 0,02184 · Content 0,00506 · Random 0,00098 | mục 4.4.1; `outputs/v2/final/ket_qua.txt` |
| 10 so sánh | NeuMF-F tốt hơn 7 (NeuMF +43,8%, MLP-F +15,0%, BPR-MF +50,4%, ItemKNN +39,9%, UserKNN +28,5%, MostPopular-Recent +45,0%, Content +691,5%); ngang 2 (GMF-F +2,6%, LateFusion-F −2,2%). NeuMF vs BPR-MF: ngang (+4,6%, p Holm 0,059) | mục 4.4.2 |
| Ablation (seed 42) | Bỏ thời gian **−42,3%**, bỏ thông tin khách −10,3% (cả hai khoảng tin cậy không chứa 0); bỏ thuộc tính −3,7%, văn bản −2,7% (khoảng tin cậy chứa 0) | mục 4.4.3 |
| Lần chạy | 10/10/2026, GPU RTX 3050, 7,5 giờ cho 5 seed; seed 42 chạy lại một lần (lần đầu dừng giữa chừng) | mục 4.1 |

Số tinh chỉnh chỉ dùng để **chọn cấu hình**; kết luận chỉ lấy từ test của mẫu B.

---

## Phần C. Trả lời 17 góp ý

### 1. Kết quả có cao bất thường, có rò rỉ dữ liệu không?

**1a. Kết quả có cao bất thường không?**
Không. Bài toán khó nên điểm tuyệt đối thấp:
- mỗi khách chỉ có vài món đúng (trung bình khoảng 3) giữa khoảng 6,7 nghìn sản phẩm ứng viên;
- chỉ tính món **khách chưa từng mua**, và dự đoán cho 8 tuần sau.

Trên test mẫu B, NDCG@10 cao nhất là 0,0409 (LateFusion-F); HR@10 cao nhất 15,8% — tức khoảng 1/6 số khách có ít nhất
một món đúng trong 10 gợi ý. Điều cần xem là chênh lệch giữa các mô hình có ý nghĩa thống kê hay không, không phải độ
lớn tuyệt đối.

**1b. Train/test chia thế nào?**
Chia theo **thời gian**, cùng một mốc cho mọi khách:
- trước 01/07/2020 để huấn luyện, 01/07–28/07 để xác thực (chọn cấu hình, chọn số epoch);
- từ 29/07 đến 22/09 để kiểm thử;
- trước khi chấm kiểm thử, mô hình được huấn luyện lại trên mọi dữ liệu trước 29/07.

Món khách đã mua trước mốc không được tính là món đúng. Mở ở đâu: mục 3.2.4.

**1c. Dữ liệu test có lọt vào huấn luyện không?**
Không. Có sáu lớp bảo vệ:
1. Mỗi cặp (khách, sản phẩm) chỉ có một ngày mua đầu, nên không thể vừa ở tập huấn luyện vừa là món đúng.
2. Bước lọc dữ liệu (k-core) chỉ dùng dữ liệu trước mốc kiểm thử.
3. Đặc trưng tại ngày t chỉ dùng dữ liệu **trước** ngày t (ví dụ doanh số chỉ tính đến ngày t−1).
4. Mẫu B gồm khách khác hẳn mẫu A; tập kiểm thử của B chỉ mở một lần.
5. Dữ liệu đã lọc ghi ra file có mã MD5; mọi mô hình đọc đúng cùng file.
6. Chương trình chấm cuối có "khoá": từ chối chạy nếu kế hoạch chưa lưu, mã nguồn bị sửa hoặc khác lúc tinh chỉnh; mỗi lần chấm ghi nhật ký.

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

Có. Cả 14 mô hình được chấm trên **cùng** tập kiểm thử của mẫu B (3.165 khách, 10.285 cặp đúng):
- cùng file dữ liệu đã lọc (kiểm MD5), cùng tập ứng viên (sản phẩm đã có người mua trước mốc), cùng cách phá hoà điểm;
- cùng 5 seed, cùng ngân sách tinh chỉnh (6 cấu hình mỗi mô hình).

Kết quả của từng khách được lưu lại nên so sánh được theo cặp (cùng một khách, hai mô hình). Mở ở đâu: mục 3.6, 4.1.

### 3. Top-K là gì? Top-K người dùng tương đồng xác định thế nào?

- **Top-K trong kết quả** là Top-K **sản phẩm**: chấm điểm mọi món khách chưa mua, sắp giảm dần, lấy K món đầu.
- **Top-K người dùng tương đồng** thuộc cách lọc cộng tác dựa trên láng giềng — mô hình **UserKNN**, đúng như Algorithm 3 trong luận án của cô:
  1. tính độ tương đồng cosine giữa hai khách theo các món mua chung;
  2. giữ k khách giống nhất (k = 200, chọn trên tập xác thực);
  3. điểm của một món = tổng độ tương đồng của các láng giềng đã mua món đó.
- **ItemKNN** làm tương tự theo sản phẩm (Algorithm 4).
- Cả hai là baseline chính thức. Kết quả: **UserKNN là baseline mạnh nhất** (0,03114, hạng 5/14, hơn BPR-MF); NeuMF-F
  hơn UserKNN 28,5% (có ý nghĩa). ItemKNN 0,02860 (hạng 6).
- Demo có màn hình "10 khách tương đồng nhất" cho từng khách.

Mở ở đâu: mục 2.1.2 (công thức 2.1–2.3), 3.7.

### 4. Lọc cộng tác hoạt động thế nào? Có phải lấy món người khác mua để gợi ý trực tiếp?

Không hẳn. Có hai cách:
- **Dựa trên láng giềng (UserKNN):** tìm khách giống mình → lấy các món họ đã mua mà mình chưa mua → xếp theo độ giống.
- **Dựa trên mô hình (MF, NeuMF, NeuMF-F):** học một vector cho mỗi khách và mỗi sản phẩm từ toàn bộ lịch sử; khách mua giống nhau sẽ có vector gần nhau; điểm của một món tính từ hai vector.

NeuMF-F cộng thêm đặc trưng vào vector, nên vector có thêm thông tin ngoài lịch sử mua (loại hàng, xu hướng bán gần đây,
nhóm khách). Mở ở đâu: mục 2.1.2, 3.3.1.

### 5. Khởi đầu lạnh (Cold Start)?

- **Sản phẩm mới — đã thử, rồi đưa ra ngoài phạm vi theo góp ý:**
  - bản v2 đầu (khối 1, 04/10) đưa sản phẩm chưa từng bán vào tập ứng viên; NDCG@10 trên nhóm này của **mọi** mô hình
    đều dưới 0,002 — gần như không gợi ý đúng được;
  - theo góp ý của cô, bản cuối coi một sản phẩm là một mẫu thiết kế và bỏ sản phẩm chưa có người mua khỏi tập ứng viên
    lẫn đáp án. Khởi đầu lạnh của sản phẩm vì vậy **nằm ngoài phạm vi** kết quả cuối — ghi là hạn chế và hướng phát triển;
  - thiết kế có tuỳ chọn **bỏ ID ngẫu nhiên** khi huấn luyện (ý tưởng DropoutNet), nhưng tinh chỉnh chọn ρ = 0 cho NeuMF-F
    và MLP-F (GMF-F chọn 0,25); trong bản cuối nó chỉ là một siêu tham số điều chuẩn.
- **Khách hàng mới (chưa mua gì) — ngoài phạm vi:** mọi khách được đánh giá đều có lịch sử trước mốc. Demo chỉ phục vụ khách
  có trong dữ liệu; nhập mã khách không có thì hệ thống báo lỗi thay vì gợi ý bừa.

Mở ở đâu: mục 2.1.4, 2.4.1, 3.2.4, 4.5, 4.6.

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
- Mô tả thêm: độ phủ của top-10 (bao nhiêu phần danh mục được gợi ý cho ít nhất một khách).

**Nối với luận án của cô:**
- Luận án dùng MAE/RMSE (cho dự đoán điểm đánh giá), Precision/Recall, Hit rate và ARHR.
- H&M không có điểm đánh giá nên không dùng MAE/RMSE.
- HR@K chính là hit rate. NDCG cùng tinh thần ARHR: cả hai thưởng món đúng nằm cao; NDCG chiết khấu theo 1/log₂(r+1) và chuẩn hoá về 0–1.

Mở ở đâu: mục 2.5 (công thức 2.19–2.21); `neumf_project/src/evaluation/metrics.py`.

### 7. Trình bày kết quả theo chuẩn học thuật?

- Số thập phân (NDCG không nhân 100), 5 chữ số, dạng trung bình ± độ lệch chuẩn qua 5 seed, in đậm giá trị cao nhất mỗi cột.
- Có bảng kiểm định riêng: chênh lệch, khoảng tin cậy 95%, p sau hiệu chỉnh Holm, kết luận.
- Mọi bảng, hình, con số được chương trình **tự sinh** từ file kết quả, không gõ tay; 31 câu nhận xét bằng chữ trong báo
  cáo được chương trình đối chiếu lại với số liệu.
- Không đặt số của đề tài cạnh số trong bài báo, vì khác dữ liệu và cách đánh giá.

Mở ở đâu: mục 4.4; `neumf_project/scripts/24_report_v2.py`, `19_check_report.py`.

### 8. Vai trò của Matrix Factorization (MF)?

- Ma trận khách × sản phẩm rất thưa (mật độ khoảng 0,45% sau khi gộp theo mẫu và lọc 10-core).
- MF nén ma trận này thành hai bảng vector nhỏ: P (khách) và Q (sản phẩm); điểm dự đoán = tích vô hướng p_u · q_i. Nhờ vậy suy ra được điểm cho những ô chưa có dữ liệu.
- Trong đề tài:
  - **BPR-MF** là baseline MF;
  - **GMF** là MF dạng mạng nơ-ron (có trọng số riêng cho từng chiều);
  - trong NeuMF-F, nhánh **GMF-F** là MF trên vector có đặc trưng, nên còn học được tương tác giữa thuộc tính khách và
    thuộc tính sản phẩm. Kết quả: GMF-F đứng riêng đã ngang NeuMF-F — nhánh MF có đặc trưng là phần mạnh nhất của mô hình.

Mở ở đâu: mục 2.2, 3.3.2.

### 9. Có thực sự xây mô hình lai không?

Có — **NeuMF-F**:
1. Mỗi nhánh (GMF và MLP) có vector khách = vector ID + chiếu của đặc trưng khách; vector sản phẩm = vector ID + chiếu của đặc trưng sản phẩm.
2. Nhánh GMF-F nhân từng phần tử hai vector (tuyến tính); nhánh MLP-F nối hai vector rồi qua 3 tầng ẩn (phi tuyến).
3. Hai kết quả được nối lại, qua một lớp dự đoán chung → điểm.

Ba so sánh trả lời trực tiếp "lai có tác dụng không":
- **NeuMF-F với NeuMF chỉ dùng ID:** đặc trưng có giúp không.
- **NeuMF-F với GMF-F, MLP-F:** hợp nhất có hơn từng nhánh không.
- **NeuMF-F với LateFusion-F:** hợp nhất sớm hay muộn tốt hơn.

Kết quả trên test mẫu B:
- **Đặc trưng giúp rõ:** NeuMF-F hơn NeuMF chỉ ID **43,8%** (có ý nghĩa).
- **Lai hơn nhánh DNN** (MLP-F, +15,0%, có ý nghĩa), **nhưng không hơn nhánh MF** (GMF-F, +2,6%, không có ý nghĩa).
- **Hợp nhất sớm và muộn ngang nhau:** LateFusion-F cao hơn NeuMF-F 2,2% nhưng không có ý nghĩa (p Holm 0,735).

Mở ở đâu: mục 3.3 (Hình 3.2, công thức 3.7–3.10), 4.4.2; `neumf_project/src/models/hybrid_features.py`.

### 10. Đã thử Transformer, Temporal, BERT chưa?

- **Đã dùng mô tả văn bản của sản phẩm:**
  - biểu diễn bằng TF-IDF rồi giảm còn 64 chiều (SVD);
  - nối vào vector của mô hình — cùng tinh thần chương 4 luận án của cô (vector MF + vector văn bản);
  - cách này nhẹ, chạy được trên máy không có GPU.
  - Ablation: bỏ vector văn bản làm NDCG@10 giảm 2,7%, khoảng tin cậy chứa 0 — đóng góp nhỏ, chưa khẳng định được.
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
3. **Baseline MostPopular-Recent** (bán chạy trong W ngày gần nhất). Trên tập xác thực, cửa sổ 28 ngày tốt nhất (0,02334).

Kết quả ablation: bỏ đặc trưng thời gian làm NDCG@10 của NeuMF-F giảm **42,3%** — thành phần đóng góp lớn nhất (khoảng
tin cậy không chứa 0). Bản thân MostPopular-Recent cũng là baseline khá mạnh: 0,02760 trên test, hơn Most Popular
(0,02184) và ngang NeuMF (0,02783), BPR-MF (0,02661); NeuMF-F hơn nó 45,0% (có ý nghĩa) — tức mô hình học được nhiều hơn xu hướng
bán chung. Mở ở đâu: mục 3.2.5, 4.2, 4.4.3.

### 12–13. Early fusion và Late fusion

Định nghĩa theo luận án của cô (mục 1.1.2.2):

| Kiểu | Định nghĩa | Trong đề tài |
|---|---|---|
| **Early fusion** | Nối biểu diễn của các nguồn → **một** mô hình dự đoán | **NeuMF-F** (và NeuMF): nối vector nhánh GMF với vector nhánh MLP → một lớp dự đoán chung, huấn luyện chung. Đặc trưng cũng được đưa vào ngay từ vector |
| **Late fusion** | Mỗi nguồn một mô hình riêng → trộn kết quả | **LateFusion-F**: w × điểm GMF-F + (1 − w) × điểm MLP-F (điểm chuẩn hoá về 0–1), hai mô hình huấn luyện riêng, w = 0,4 chọn trên tập xác thực |
| Không phải fusion | — | **MLP đứng riêng** chỉ là mạng DNN thuần |

So sánh NeuMF-F với LateFusion-F (cùng hai thành phần) nằm sẵn trong 10 so sánh đã đăng ký trước. **Kết quả: không khác
biệt có ý nghĩa** — LateFusion-F 0,04093, NeuMF-F 0,04003 (thấp hơn 2,2%, p Holm 0,735). LateFusion-F có NDCG@10 cao
nhất trong 14 mô hình, nhưng chênh lệch với NeuMF-F nằm trong dao động. Mở ở đâu: mục 2.3.4 (Hình 2.2, công thức
2.13–2.15), 3.3.5, 4.4.2.

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

- "Lai có tốt hơn trước khi lai" = so sánh NeuMF-F với GMF-F và MLP-F. **Kết quả:** hơn MLP-F (+15,0%), ngang GMF-F
  (+2,6%, không có ý nghĩa). Với baseline: hơn cả 5 baseline trong họ so sánh (BPR-MF, ItemKNN, UserKNN,
  MostPopular-Recent, Content).
- Chỉ nói "A tốt hơn B" khi **đủ cả ba** điều kiện: p sau hiệu chỉnh Holm < 0,05; khoảng tin cậy 95% không chứa 0; chênh lệch ≥ 5%. Tiêu chí này cố định từ trước khi chấm.

Mở ở đâu: mục 3.6, 4.2.

### 15. Sơ đồ kiến trúc

- **Hình 2.1** — kiến trúc NeuMF.
- **Hình 2.2** — hợp nhất sớm (NeuMF, NeuMF-F) so với hợp nhất muộn (LateFusion-F).
- **Hình 3.1** — luồng toàn hệ thống: dữ liệu → tiền xử lý (gộp theo mẫu, lọc) và đặc trưng → giai đoạn đánh giá → mô hình → tinh chỉnh (mẫu A) → đánh giá cuối (mẫu B).
- **Hình 3.2** — kiến trúc NeuMF-F.
- **Hình 3.3** — kiến trúc ba tầng của demo.

Luồng cô gợi ý (dữ liệu → tiền xử lý → chia → ma trận → MF → vector → DL → hợp nhất → điểm → xếp hạng → Top-K) được Hình 3.1, 3.2 và 2.2 thể hiện đủ.

### 16. Mô hình "variational" nhắc trong buổi họp

- Chưa triển khai; **cần hỏi lại cô tên mô hình**, không tự khẳng định.
- Khả năng cao là Mult-VAE (Liang và cộng sự, 2018), đã trình bày lý thuyết ở mục 2.4.4.
- Tập kiểm thử của mẫu B **đã mở** (10/10). Nếu cô yêu cầu, chỉ thêm được dưới dạng **thăm dò sau kiểm thử**: tinh
  chỉnh trên mẫu A như mọi mô hình, chấm trên B, nhưng ghi rõ là lệch kế hoạch (PREREG_v2 mục 10) và không đưa vào họ 10
  so sánh.

### 17. Lộ trình 10 bước — đã làm đến đâu?

| # | Bước | Trạng thái |
|---|---|---|
| 1 | Sửa cách chia Train/Test | Xong — chia theo thời gian; một sản phẩm = một mẫu thiết kế |
| 2 | Kiểm tra rò rỉ dữ liệu | Xong — có test tự động |
| 3 | Bộ test chuẩn | Xong — mẫu B độc lập (khối 2), file dữ liệu kiểm MD5, khoá test |
| 4 | Chạy lại Baseline/MF | Xong — tinh chỉnh trên A, chấm trên B (BPR-MF 0,02661) |
| 5 | Mô hình Deep Learning | Xong — MLP, MLP-F |
| 6 | Xây mô hình lai | Xong — NeuMF-F (0,04003, hơn NeuMF chỉ ID 43,8%) |
| 7 | Thử Fusion | Xong — Early (NeuMF-F) và Late (LateFusion-F); không khác biệt có ý nghĩa |
| 8 | Bảng NDCG/HR/Recall/Precision | Xong — tự sinh từ kết quả 5 seed |
| 9 | Vẽ kiến trúc | Xong — Hình 3.1, 3.2 |
| 10 | Phân tích kết quả | Xong — kiểm định, ablation, độ phủ, ổn định giữa hai mẫu, phần thảo luận Chương 4 |

---

## Phần D. Câu hỏi khó nên chuẩn bị

**"Vì sao đổi cách làm gần cuối dự án? Kết quả cũ thế nào?"**
Có hai lần đổi:
1. **v1 → v2 (cuối tháng 9):** giai đoạn phát triển (v1) cho thấy NeuMF chỉ dùng mã ID **không** tốt hơn MF đã tinh chỉnh
   (BPR-MF cao nhất; 0/8 so sánh có ý nghĩa; tiền huấn luyện không giúp); lọc k-core dùng cả dữ liệu giai đoạn test; tập
   kiểm thử cũ đã bị xem nhiều lần. v2 thêm đặc trưng, sửa cách lọc và lấy kết luận trên khách hàng mới hoàn toàn.
2. **Bản v2 đầu → bản cuối (09/10):** bản đầu tính theo từng màu, có sản phẩm mới và đánh giá trên khối 1 (mở 04/10).
   Theo góp ý của cô, bản cuối gộp theo mẫu thiết kế, bỏ sản phẩm chưa có người mua, ghi dữ liệu ra file kiểm MD5 và đánh
   giá trên khối 2.

Kết quả v1 và khối 1 vẫn được báo cáo trung thực ở mục 4.5, không trộn với bản cuối.

**"Việc đã xem kết quả trước đó có làm lệch kết luận không?"**
Có ảnh hưởng ở mức thiết kế: biết mô hình chỉ dùng mã ID không hơn MF nên bổ sung đặc trưng; bản cuối được quyết định
**sau khi xem kết quả khối 1**. Vì vậy khối 1 bị loại, kết luận chỉ lấy trên khối 2 — dữ liệu chưa ai xem; kế hoạch bản
cuối được lưu (commit) sau khi tinh chỉnh lại trên mẫu A và **trước** khi dựng tập kiểm thử của khối 2; độ đo chính, họ
10 so sánh và tiêu chí kết luận giữ nguyên từ bản 03/10.

**"Kết quả khối 1 khác bản cuối (khối 1: LateFusion-F tốt hơn NeuMF-F có ý nghĩa) — tin cái nào?"**
Bản cuối. Khối 1 khác dữ liệu (theo màu, có sản phẩm mới) và đã được dùng để ra quyết định (đổi thiết kế), nên không còn
là ước lượng không thiên lệch. Điểm chung của cả hai: ba vị trí đầu đều là LateFusion-F, GMF-F và NeuMF-F (thứ tự khác
nhau), và NeuMF chỉ dùng ID không hơn BPR-MF có ý nghĩa.

**"Seed 42 chạy lại — vậy có vi phạm 'mở tập kiểm thử một lần' không?"**
Lần chạy đầu dừng giữa chừng ở seed 42, sau khi đã chấm Random và 5 mô hình tất định (Most Popular, MostPopular-Recent,
Content, ItemKNN, UserKNN), trước khi lưu bất kỳ kết quả nào. Seed 42 được chạy lại với cùng mã nguồn, cấu hình và dữ
liệu; việc này ghi ở mục lệch kế hoạch (PREREG_v2 mục 10) và trong nhật ký truy cập (`v2_kiemdinh_seed42_rerun`). Không
quyết định nào được đưa ra sau khi thấy các số trên màn hình — cấu hình đã cố định, và 5 mô hình tất định cho cùng kết
quả ở lần chạy lại. Các seed khác mở tập kiểm thử đúng một lần.

**"LateFusion-F cao nhất — sao không lấy LateFusion-F làm mô hình chính?"**
- Mô hình chính phải cố định **trước** khi xem test (PREREG_v2 mục 8): đề tài là mô hình lai hợp nhất sớm MF + DNN có
  đặc trưng, nên NeuMF-F được chọn từ đầu, không theo kết quả. Đổi mô hình chính sau khi thấy test là chọn theo kết quả —
  đúng điều giao thức muốn tránh.
- Dữ liệu cũng không cho phép nói LateFusion-F tốt hơn: chênh 2,2%, p Holm 0,735.
- Kết quả vẫn trả lời câu hỏi của cô về early/late fusion: trên dữ liệu này, hai cách hợp nhất cho kết quả ngang nhau.

**"Vì sao hợp nhất sớm không hơn nhánh GMF-F đứng riêng?"** (nói rõ là nhận định, chưa kiểm chứng)
GMF-F đứng riêng đã ngang NeuMF-F (+2,6%, không có ý nghĩa), trong khi MLP-F kém hơn rõ (NeuMF-F hơn MLP-F 15,0%). Phần
lớn lợi ích nằm ở **đặc trưng** — nhất là đặc trưng thời gian — đưa vào nhánh MF, chứ không ở việc thêm nhánh phi tuyến;
điều này phù hợp với các tái đánh giá cho thấy thành phần MLP của NeuMF khó vượt tích vô hướng được tinh chỉnh tốt
(Rendle et al., 2020).

**"Thứ hạng có ổn định giữa lúc tinh chỉnh (mẫu A) và test (mẫu B) không?"**
Khá ổn định ở nhóm đầu: bốn mô hình có đặc trưng đứng đầu ở cả hai, LateFusion-F và NeuMF-F giữ hai vị trí đầu. Thay đổi
lớn nhất: GMF và MLP chỉ dùng ID tụt từ hạng 5 và 7 xuống 9 và 11 (hai mô hình duy nhất có NDCG@10 test thấp hơn lúc
tinh chỉnh); ItemKNN lên từ hạng 10 lên 6. Giá trị tuyệt đối hai bên không cùng thang (khác mẫu khách, cửa sổ kiểm thử dài
gấp đôi), nên chỉ so thứ hạng.

**"Bỏ sản phẩm mới có làm bài toán dễ hơn, che đi điểm yếu không?"**
Có — kết quả cuối chỉ nói về gợi ý trong các sản phẩm đã có lịch sử bán, không nói về khởi đầu lạnh; đã ghi rõ là hạn
chế. Nhưng ở bản đầu (khối 1), khi đưa sản phẩm mới vào, NDCG@10 trên nhóm này của mọi mô hình đều dưới 0,002, nên ở quy
mô này khả năng gợi ý sản phẩm mới gần như không đo được. Thay đổi làm theo góp ý của cô và được quyết định trước khi mở
khối 2.

**"Vì sao gộp các màu thành một sản phẩm?"**
Theo góp ý của cô: các màu của cùng một mẫu (cùng `product_code`) được coi là một sản phẩm. Gộp làm dữ liệu bớt thưa —
trước mốc kiểm thử, mẫu A giảm từ 55.971 xuống 27.370 sản phẩm. Đổi lại, gợi ý ở mức mẫu thiết kế, không ở mức màu —
đã ghi là hạn chế.

**"Vì sao lọc k-core = 10, vì sao chỉ lấy mẫu 500 nghìn giao dịch?"**
Do bộ nhớ máy (16 GB RAM):
- chấm điểm toàn bộ sản phẩm cho mọi khách ở quy mô đầy đủ là hàng chục tỷ phép tính;
- khảo sát ở giai đoạn phát triển: với k = 5, ước tính cần khoảng 10,7 GB RAM.

Hệ quả: dữ liệu thiên về khách mua nhiều — đã ghi là hạn chế. Mở ở đâu: mục 3.2.1, 3.2.3, 5.2.

**"Có bị quá khớp (overfitting) không, xử lý thế nào?"**
- Dừng sớm theo NDCG@10 trên tập xác thực (dừng sau 5 epoch không cải thiện).
- Dropout trong tầng ẩn.
- Điều chuẩn L2 (weight decay).
- Bỏ ID ngẫu nhiên là một siêu tham số được tinh chỉnh (ρ ∈ {0; 0,25; 0,5}); NeuMF-F và MLP-F chọn 0, GMF-F chọn 0,25.

Khi huấn luyện lại, dừng đúng số epoch đã chọn. Mở ở đâu: mục 3.3.3, 3.5.1.

**"Vì sao 5 seed? Kiểm định thế nào?"**
- Kiểm định theo từng khách hàng (hàng nghìn khách), không theo seed. Mỗi khách lấy điểm trung bình qua 5 seed rồi so hai mô hình bằng Wilcoxon, kèm khoảng tin cậy bootstrap và hiệu chỉnh Holm cho 10 so sánh.
- Nếu kiểm định theo seed thì với 5 seed, p nhỏ nhất cũng chỉ 0,0625, không bao giờ dưới 0,05.

**"Demo dùng mô hình nào?"**
Đúng các mô hình của đánh giá cuối (seed 42), chỉ suy diễn, không huấn luyện lại. Mỗi sản phẩm hiển thị theo mẫu thiết kế
(tên và ảnh của màu đầu tiên, kèm số màu). Số trên demo được test tự động đối chiếu với file kết quả theo từng khách. Demo
chỉ phục vụ khách đã có lịch sử mua.

**"Có gì khác so với đề cương?"**

| Đề cương | Thực tế | Lý do |
|---|---|---|
| Chia leave-one-out | Chia theo thời gian | Leave-one-out lọt thông tin tương lai (câu 1f) |
| Sản phẩm theo `article_id` | Sản phẩm theo mẫu thiết kế (`product_code`) | Theo góp ý của cô |
| Baseline ALS | BPR-MF | Cùng nhóm MF cho phản hồi ẩn; iALS chỉ thử ở giai đoạn phát triển |
| Thử đặc trưng Category/Department | **Đã dùng** (11 thuộc tính sản phẩm) | — |
| K = 5/10/20 | Có đủ | — |
| Biểu đồ hội tụ (TensorBoard/W&B) | Ghi ra file CSV, vẽ bằng matplotlib | Cùng thông tin, truy vết được trong repo |
| Demo FastAPI + Streamlit | FastAPI + giao diện HTML | Chức năng tương đương |
| Báo cáo 6 chương | 5 chương | Gộp cài đặt và kết quả vào Chương 4 |
