# Chuẩn bị vấn đáp — Mô hình khuyến nghị lai trên dữ liệu H&M

File này giúp trả lời 17 góp ý của cô trong buổi họp. Mỗi câu có: **Trả lời** (ý chính, nói trong 1–2 phút) và
**Mở ở đâu** (mục trong báo cáo hoặc file trong repo). Cập nhật theo kết quả đánh giá cuối trên H&M ngày 10/10/2026
(mẫu kiểm định khối 2), kết quả kiểm chứng trên Amazon Beauty (10–11/10/2026) và bản báo cáo sửa theo góp ý họp 04/10
(13/10/2026: K = 15, Amazon, bảng ba nghiên cứu nền tảng, vẽ lại hình, mã giả, khách hàng mới, baseline ba nhóm và
phân tích bổ sung với mô hình lai truyền thống Hybrid-CBCF).

> **Quy tắc tránh nói sai**
> - Kết quả cuối trên mẫu kiểm định H&M **đã có** (10/10/2026). Nói đúng như sau: NeuMF-F **tốt hơn có ý nghĩa** NeuMF
>   chỉ ID, MLP-F, BPR-MF, ItemKNN, UserKNN, MostPopular-Recent, Content; **ngang** GMF-F và LateFusion-F; trên H&M
>   **không thua** mô hình nào. **Không nói "NeuMF-F tốt nhất"** — NeuMF-F đứng 2/14, LateFusion-F có NDCG@10 cao hơn
>   một chút (không có ý nghĩa).
> - **Trên Amazon Beauty, LateFusion-F tốt hơn NeuMF-F có ý nghĩa** (NeuMF-F thấp hơn 12,5%). Nói thẳng điều này; NeuMF-F
>   vẫn là mô hình đề xuất vì đã cố định trước khi xem kết quả (PREREG). Không nói "NeuMF-F không thua mô hình nào" mà
>   không nói rõ là trên H&M.
> - Amazon **không tinh chỉnh lại**: mọi mô hình dùng cấu hình chọn trên H&M. Hai so sánh có BPR-MF trên Amazon
>   (NeuMF-F +186,5%, NeuMF +72,9%) **không dùng làm bằng chứng** — BPR-MF trên Amazon kém cả ItemKNN, MostPopular-Recent.
> - **K = 15** được tính lại từ hạng đã lưu của lần đánh giá cuối — **không mở lại tập kiểm thử**, không chạy lại mô hình.
> - **Không nói đề tài xử lý được khởi đầu lạnh của sản phẩm**: bản cuối bỏ sản phẩm chưa có người mua khỏi đánh giá.
>   Cũng không nói NeuMF-F "học chấm sản phẩm mới nhờ bỏ ID ngẫu nhiên": tinh chỉnh chọn ρ = 0 cho NeuMF-F (và MLP-F);
>   chỉ GMF-F chọn ρ = 0,25. Khách hàng mới: hệ thống gợi ý sản phẩm phổ biến — **không đánh giá định lượng** nhóm này.
> - Một **sản phẩm** trong đề tài là một **mẫu thiết kế** (`product_code`, gộp mọi màu), không phải một `article_id`.
> - Không so số của đề tài với số trong bài báo (khác dữ liệu, khác cách chia, khác cách đánh giá). Bảng ba nghiên cứu
>   nền tảng (mục 2.6.1) chỉ để thấy **thiết lập khác nhau** và mức cải thiện tương đối mà mỗi bài tự báo cáo.
> - Không gọi MLP đứng riêng là "early fusion" (đó là mạng DNN thuần).
> - Số của giai đoạn phát triển ban đầu và của khối 1 (04/10) chỉ nhắc khi được hỏi về lịch sử; không đặt cạnh số bản
>   cuối.
> - **Hybrid-CBCF là phân tích bổ sung** sau đánh giá cuối: NeuMF-F tốt hơn nó có ý nghĩa trên cả hai bộ; Hybrid-CBCF
>   không khác biệt có ý nghĩa với UserKNN trên H&M nhưng tốt hơn trên Amazon. Không tính nó vào "14 mô hình" hay họ 10
>   so sánh.

---

## Phần A. Nắm nhanh đề tài trong 1 phút

- **Bài toán:** gợi ý Top-K sản phẩm thời trang cho từng khách hàng, dựa trên lịch sử mua (không có điểm đánh giá).
- **Dữ liệu:** H&M Personalized Fashion Recommendations — 31,8 triệu giao dịch (20/09/2018 → 22/09/2020), danh mục
  105.542 sản phẩm (theo màu), thông tin 1.371.980 khách hàng. Đề tài gộp các màu của cùng một mẫu thành **một sản phẩm**
  (`product_code`). Kiểm chứng thêm trên **Amazon Beauty** (đánh giá sản phẩm làm đẹp, bản 5-core năm 2014).
- **Mô hình đề xuất — NeuMF-F:** giữ cấu trúc của NeuMF (nhánh MF + nhánh mạng nơ-ron sâu, hợp nhất ở lớp dự đoán),
  nhưng mỗi khách hàng/sản phẩm được biểu diễn bằng **mã ID + đặc trưng** (thuộc tính và mô tả sản phẩm, thông tin khách
  hàng, doanh số và thời gian) — tức có thêm thông tin ngoài lịch sử mua.
- **Cách đánh giá:** hai nhóm khách hàng khác nhau hoàn toàn. **Mẫu phát triển** dùng để chọn cấu hình (tinh chỉnh).
  **Mẫu kiểm định** dùng để chấm điểm cuối cùng, chỉ một lần, theo kế hoạch đã ghi sẵn từ trước (`audit/PREREG_v2.md`).
- **So sánh với:** NeuMF chỉ dùng mã ID, từng nhánh đứng riêng, cách hợp nhất muộn, và 7 mô hình đối chứng (baseline).
- **Kết quả một câu:** đặc trưng giúp rõ (NeuMF-F hơn NeuMF chỉ ID 43,8% trên H&M, 65,7% trên Amazon), NeuMF-F hơn cả 5
  baseline trong họ so sánh trên cả hai bộ dữ liệu, nhưng cách ghép hai nhánh không tạo lợi thế: ngang GMF-F đứng riêng ở
  cả hai bộ, ngang hợp nhất muộn trên H&M và **thua** hợp nhất muộn trên Amazon.

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
| Mẫu phát triển (tinh chỉnh) | Khối 0: 500.269 giao dịch của 21.599 khách | báo cáo mục 3.2.2 |
| Mẫu kiểm định (đánh giá cuối) | Khối 2: 500.164 giao dịch của 21.351 khách, **không có khách nào chung** với mẫu phát triển | mục 3.2.2 |
| Gộp theo mẫu thiết kế | Trước mốc kiểm thử: mẫu phát triển 55.971 → 27.370 sản phẩm, 401.293 → 359.181 cặp; mẫu kiểm định 55.683 → 27.291 sản phẩm, 398.653 → 356.740 cặp | mục 3.2.3 |
| Sau lọc 10-core | Mẫu phát triển: 8.039 khách, 6.801 sản phẩm, 245.644 cặp. Mẫu kiểm định: 7.994 khách, 6.749 sản phẩm, 243.696 cặp | mục 3.2.3, Bảng 3.3 |
| Mốc thời gian | Xác thực: 01/07–28/07/2020 (4 tuần). Kiểm thử: 29/07–22/09/2020 (8 tuần) | mục 3.2.4 |
| Mẫu phát triển ở giai đoạn xác thực | 2.569 khách được đánh giá, 8.636 cặp đúng, trung bình 6.762 ứng viên mỗi khách | Bảng 3.3 |
| Số mô hình, số lần chạy | 14 mô hình; 5 seed; họ 10 so sánh có hiệu chỉnh Holm | mục 3.6, 4.2 |
| Kết quả tinh chỉnh (tập xác thực của mẫu phát triển, NDCG@10) | LateFusion-F 0,03556 · NeuMF-F 0,03337 · MLP-F 0,03212 · GMF-F 0,03162 · GMF 0,02857 · UserKNN 0,02753 · MLP 0,02742 · NeuMF 0,02696 · BPR-MF 0,02636 · ItemKNN 0,02599 · MostPopular-Recent 0,02334 · Most Popular 0,02174 · Content 0,00459 | mục 4.3 |
| Tập kiểm thử mẫu kiểm định | 3.165 khách; 10.285 cặp đúng; trung bình 6.710 ứng viên mỗi khách | mục 4.1 |
| Kết quả cuối H&M (NDCG@10, 5 seed) | **LateFusion-F 0,04093** · **NeuMF-F 0,04003** · GMF-F 0,03902 · MLP-F 0,03480 · UserKNN 0,03114 · ItemKNN 0,02860 · NeuMF 0,02783 · MostPopular-Recent 0,02760 · GMF 0,02695 · BPR-MF 0,02661 · MLP 0,02373 · Most Popular 0,02184 · Content 0,00506 · Random 0,00098 | mục 4.4.1; `outputs/v2/final/ket_qua.txt` |
| Theo K (H&M, NeuMF-F) | NDCG@5/10/15/20 = 0,03120 / 0,04003 / 0,04644 / 0,05166; HR@15 = 0,19406. Ở mọi K và mọi độ đo, thứ tự đầu luôn là LateFusion-F, NeuMF-F, GMF-F, MLP-F | mục 4.4.2, Bảng 4.5–4.6 |
| 10 so sánh H&M | NeuMF-F tốt hơn 7 (NeuMF +43,8%, MLP-F +15,0%, BPR-MF +50,4%, ItemKNN +39,9%, UserKNN +28,5%, MostPopular-Recent +45,0%, Content +691,5%); ngang 2 (GMF-F +2,6%, LateFusion-F −2,2%). NeuMF vs BPR-MF: ngang (+4,6%, p Holm 0,059) | mục 4.4.3 |
| Ablation H&M (seed 42) | Bỏ thời gian **−42,3%**, bỏ thông tin khách −10,3% (cả hai khoảng tin cậy không chứa 0); bỏ thuộc tính −3,7%, văn bản −2,7% (khoảng tin cậy chứa 0) | mục 4.4.5 |
| Lần chạy H&M | 10/10/2026, GPU RTX 3050, 7,5 giờ cho 5 seed; seed 42 chạy lại một lần (lần đầu dừng giữa chừng) | mục 4.1 |
| Amazon Beauty — dữ liệu | Bản 5-core: 198.502 đánh giá, 22.363 khách, 12.101 sản phẩm. Lọc 5-core trước 01/01/2014: 10.681 khách, 6.069 sản phẩm, 94.009 cặp. Kiểm thử 01/01–23/07/2014: 2.644 khách, 6.107 cặp đúng, 6.058 ứng viên mỗi khách | mục 3.2.6, Bảng 3.6 |
| Amazon — kết quả (NDCG@10, 5 seed) | **LateFusion-F 0,03747** · GMF-F 0,03298 · NeuMF-F 0,03277 · MLP-F 0,03065 · UserKNN 0,02506 · ItemKNN 0,02333 · NeuMF 0,01978 · GMF 0,01627 · MostPopular-Recent 0,01401 · MLP 0,01271 · BPR-MF 0,01144 · Content 0,00945 · Most Popular 0,00872 | mục 4.5.1 |
| Amazon — 10 so sánh | NeuMF-F tốt hơn NeuMF +65,7% và cả 5 baseline (từ +30,8% với UserKNN); ngang GMF-F (−0,6%) và MLP-F (+6,9%, p Holm ≈ 0,05 nhưng CI chứa 0); **LateFusion-F tốt hơn NeuMF-F** (NeuMF-F −12,5%) | mục 4.5.2, Bảng 4.15–4.16 |
| Amazon — ablation | Bỏ thời gian −31,6%, bỏ thuộc tính −14,4% (CI không chứa 0); bỏ văn bản −9,8%, bỏ thông tin khách +1,3% (CI chứa 0) | mục 4.5.3 |
| Hybrid-CBCF (bổ sung, 13/10) | H&M: NDCG@10 0,03183, hạng 5/15; NeuMF-F tốt hơn +25,8%; so với UserKNN +2,2% (không khác biệt có ý nghĩa). Amazon: 0,02664, hạng 5/15; NeuMF-F tốt hơn +23,0%; so với UserKNN +6,3% (Hybrid-CBCF tốt hơn) | mục 4.4.4, 4.5.1 (Bảng 4.8, 4.14) |

Số tinh chỉnh chỉ dùng để **chọn cấu hình**; kết luận chỉ lấy từ tập kiểm thử của mẫu kiểm định (và được kiểm chứng
trên Amazon).

---

## Phần C. Trả lời 17 góp ý

### 1. Kết quả có cao bất thường, có rò rỉ dữ liệu không?

**1a. Kết quả có cao bất thường không?**
Không. Bài toán khó nên điểm tuyệt đối thấp:
- mỗi khách chỉ có vài món đúng (trung bình khoảng 3) giữa khoảng 6,7 nghìn sản phẩm ứng viên;
- chỉ tính món **khách chưa từng mua**, và dự đoán cho 8 tuần sau.

Trên tập kiểm thử của mẫu kiểm định, NDCG@10 cao nhất là 0,0409 (LateFusion-F); HR@10 cao nhất 15,8% — tức khoảng 1/6
số khách có ít nhất một món đúng trong 10 gợi ý. Điều cần xem là chênh lệch giữa các mô hình có ý nghĩa thống kê hay
không, không phải độ lớn tuyệt đối.

**1b. Train/test chia thế nào?**
Chia theo **thời gian**, cùng một mốc cho mọi khách:
- trước 01/07/2020 để huấn luyện, 01/07–28/07 để xác thực (chọn cấu hình, chọn số epoch);
- từ 29/07 đến 22/09 để kiểm thử;
- trước khi chấm kiểm thử, mô hình được huấn luyện lại trên mọi dữ liệu trước 29/07.

Món khách đã mua trước mốc không được tính là món đúng. Mở ở đâu: mục 3.2.4.

**1c. Dữ liệu test có lọt vào huấn luyện không?**
Không. Có sáu lớp bảo vệ:
1. Mỗi cặp (khách, sản phẩm) chỉ có một ngày mua đầu, nên không thể vừa ở tập huấn luyện vừa là món đúng.
2. Bước lọc dữ liệu (k-core) chỉ dùng dữ liệu trước mốc kiểm thử (Thuật toán 3.1).
3. Đặc trưng tại ngày t chỉ dùng dữ liệu **trước** ngày t (ví dụ doanh số chỉ tính đến ngày t−1).
4. Mẫu kiểm định gồm khách khác hẳn mẫu phát triển; tập kiểm thử của mẫu kiểm định chỉ mở một lần.
5. Dữ liệu đã lọc ghi ra file có mã MD5; mọi mô hình đọc đúng cùng file.
6. Chương trình chấm cuối có "khoá": từ chối chạy nếu kế hoạch chưa lưu, mã nguồn bị sửa hoặc khác lúc tinh chỉnh; mỗi lần chấm ghi nhật ký.

Có test tự động kiểm tra các điều trên. Mở ở đâu: mục 3.2.3–3.2.5, 3.6 (Hình 3.3); `neumf_project/tests/test_v2.py`.

**1d. Có huấn luyện lại trước khi chấm không?**
Có. Với mỗi seed (Thuật toán 3.3):
1. Huấn luyện trên dữ liệu trước 01/07, dừng sớm theo tập xác thực để biết số epoch tốt nhất.
2. Huấn luyện lại từ đầu trên mọi dữ liệu trước 29/07, đúng số epoch đó.
3. Chấm kiểm thử.

Tập kiểm thử không bao giờ dùng để dừng hay chọn mô hình. Mở ở đâu: mục 3.5.1, 3.6.

**1e. Mẫu dương, mẫu âm tạo thế nào?**
- Mẫu dương: cặp (khách, sản phẩm) đã mua.
- Mẫu âm: với mỗi lượt mua, lấy ngẫu nhiên 4 hoặc 8 sản phẩm khách chưa mua. Với mô hình có đặc trưng, chỉ lấy trong sản phẩm **đã ra mắt** tính đến ngày mua (sản phẩm chưa bán thì khách không thể mua). Lấy lại mới mỗi epoch (Thuật toán 3.2).
- Khi đánh giá thì không lấy mẫu: xếp hạng toàn bộ sản phẩm ứng viên (Thuật toán 3.4).

Mở ở đâu: mục 3.4.1.

**1f. Sao không chia leave-one-out (lấy món mua cuối làm test)?**
Vì cách đó để lọt thông tin tương lai: dữ liệu huấn luyện chứa lượt mua của người khác xảy ra **sau** thời điểm cần dự đoán. Đo trên mẫu phát triển: trung bình 11,2% tương tác huấn luyện xảy ra sau ngày của món test; 60,9% khách có món xác thực và món test mua cùng ngày. Mở ở đâu: mục 3.2.4 (Meng et al., 2020).

### 2. Có bộ test chuẩn chung cho mọi mô hình không?

Có. Cả 14 mô hình được chấm trên **cùng** tập kiểm thử của mẫu kiểm định (3.165 khách, 10.285 cặp đúng):
- cùng file dữ liệu đã lọc (kiểm MD5), cùng tập ứng viên (sản phẩm đã có người mua trước mốc), cùng cách phá hoà điểm;
- cùng 5 seed, cùng ngân sách tinh chỉnh (6 cấu hình mỗi mô hình).

Kết quả của từng khách được lưu lại (kể cả hạng của từng món đúng) nên so sánh được theo cặp (cùng một khách, hai mô
hình) và tính lại được chỉ số ở K bất kỳ. Trên Amazon cũng vậy: 14 mô hình, cùng tập kiểm thử. Mở ở đâu: mục 3.6, 4.1.

### 3. Top-K là gì? Top-K người dùng tương đồng xác định thế nào?

- **Top-K trong kết quả** là Top-K **sản phẩm**: chấm điểm mọi món khách chưa mua, sắp giảm dần, lấy K món đầu (Hình 2.1,
  3.2 vẽ đủ chuỗi σ → điểm → sắp xếp → Top-K; Thuật toán 3.7).
- **Top-K người dùng tương đồng** thuộc cách lọc cộng tác dựa trên láng giềng — mô hình **UserKNN**, đúng như Algorithm 3 trong luận án của cô:
  1. tính độ tương đồng cosine giữa hai khách theo các món mua chung;
  2. giữ k khách giống nhất (k = 200, chọn trên tập xác thực);
  3. điểm của một món = tổng độ tương đồng của các láng giềng đã mua món đó.
- **ItemKNN** làm tương tự theo sản phẩm (Algorithm 4).
- Cả hai là baseline chính thức. Kết quả: **UserKNN là baseline mạnh nhất** (0,03114, hạng 5/14, hơn BPR-MF); NeuMF-F
  hơn UserKNN 28,5% (có ý nghĩa). ItemKNN 0,02860 (hạng 6). Trên Amazon, UserKNN cũng là baseline mạnh nhất (0,02506).
- Demo có màn hình "10 khách tương đồng nhất" cho từng khách.

Mở ở đâu: mục 2.1.2 (công thức 2.1–2.3), 3.8.

### 4. Lọc cộng tác hoạt động thế nào? Có phải lấy món người khác mua để gợi ý trực tiếp?

Không hẳn. Có hai cách:
- **Dựa trên láng giềng (UserKNN):** tìm khách giống mình → lấy các món họ đã mua mà mình chưa mua → xếp theo độ giống.
- **Dựa trên mô hình (MF, NeuMF, NeuMF-F):** học một vector cho mỗi khách và mỗi sản phẩm từ toàn bộ lịch sử; khách mua giống nhau sẽ có vector gần nhau; điểm của một món tính từ hai vector.

NeuMF-F cộng thêm đặc trưng vào vector, nên vector có thêm thông tin ngoài lịch sử mua (loại hàng, xu hướng bán gần đây,
nhóm khách). Mở ở đâu: mục 2.1.2, 3.3.1.

### 5. Khởi đầu lạnh (Cold Start)?

- **Khách hàng mới (chưa mua gì) — gợi ý sản phẩm phổ biến:** mô hình chỉ có vector cho khách đã có trong dữ liệu đã học.
  Khách mới, hoặc mua quá ít để qua lọc 10-core, được gợi ý **các sản phẩm phổ biến nhất** (Most Popular, tính trên dữ
  liệu trước mốc); khi khách đã có lịch sử mua, hệ thống dùng mô hình đề xuất NeuMF-F. Hệ thống **luôn có gợi ý**, không
  báo lỗi. Demo làm đúng như vậy: nhập một mã khách không có trong dữ liệu → danh sách "Gợi ý phổ biến". Phần đánh giá
  định lượng chỉ đo khách đã có lịch sử, nên chất lượng gợi ý cho khách mới không được đo riêng.
- **Sản phẩm mới — đã thử, rồi đưa ra ngoài phạm vi theo góp ý:**
  - bản đầu của kế hoạch (khối 1, 04/10) đưa sản phẩm chưa từng bán vào tập ứng viên; NDCG@10 trên nhóm này của
    **mọi** mô hình đều dưới 0,002 — gần như không gợi ý đúng được;
  - theo góp ý của cô, bản cuối coi một sản phẩm là một mẫu thiết kế và bỏ sản phẩm chưa có người mua khỏi tập ứng viên
    lẫn đáp án. Khởi đầu lạnh của sản phẩm vì vậy **nằm ngoài phạm vi** kết quả cuối — ghi là hạn chế và hướng phát triển;
  - thiết kế có tuỳ chọn **bỏ ID ngẫu nhiên** khi huấn luyện (ý tưởng DropoutNet), nhưng tinh chỉnh chọn ρ = 0 cho NeuMF-F
    và MLP-F (GMF-F chọn 0,25); trong bản cuối nó chỉ là một siêu tham số điều chuẩn.

Mở ở đâu: mục 2.1.4, 2.4.1, 3.2.4, **3.7** (Thuật toán 3.7), 4.6, 4.7.

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
- Báo cáo đủ bốn chỉ số ở **K = 5, 10, 15, 20** (Bảng 4.5–4.6 cho H&M, 4.12–4.13 cho Amazon). K = 15 tính lại từ hạng
  của từng món đúng đã lưu ở lần đánh giá cuối — không chạy lại mô hình, không mở lại tập kiểm thử; cách tính lại cho
  đúng từng số @5, @10, @20 của lần đánh giá đó.
- Lấy trung bình theo khách, rồi trung bình ± độ lệch chuẩn qua 5 seed.
- Mô tả thêm: độ phủ của top-10 (bao nhiêu phần danh mục được gợi ý cho ít nhất một khách).

**Nối với luận án của cô:**
- Luận án dùng MAE/RMSE (cho dự đoán điểm đánh giá), Precision/Recall, Hit rate và ARHR.
- H&M không có điểm đánh giá nên không dùng MAE/RMSE.
- HR@K chính là hit rate. NDCG cùng tinh thần ARHR: cả hai thưởng món đúng nằm cao; NDCG chiết khấu theo 1/log₂(r+1) và chuẩn hoá về 0–1.

Mở ở đâu: mục 2.5 (công thức 2.19–2.21), 4.4.2; `neumf_project/src/evaluation/metrics.py`.

### 7. Trình bày kết quả theo chuẩn học thuật?

- Số thập phân (NDCG không nhân 100), 5 chữ số, dạng trung bình ± độ lệch chuẩn qua 5 seed, in đậm giá trị cao nhất mỗi cột.
- Có bảng kiểm định riêng: chênh lệch, khoảng tin cậy 95%, p sau hiệu chỉnh Holm, kết luận.
- Mọi bảng, hình, con số được chương trình **tự sinh** từ file kết quả, không gõ tay; 58 câu nhận xét bằng chữ trong báo
  cáo (cả phần Amazon và phần theo K) được chương trình đối chiếu lại với số liệu (`python run.py check-report`).
- Không đặt số của đề tài cạnh số trong bài báo để so hơn kém, vì khác dữ liệu và cách đánh giá.

Mở ở đâu: mục 4.4, 4.5; `neumf_project/scripts/24_report_v2.py`, `19_check_report.py`.

### 8. Vai trò của Matrix Factorization (MF)?

- Ma trận khách × sản phẩm rất thưa (mật độ khoảng 0,45% sau khi gộp theo mẫu và lọc 10-core).
- MF nén ma trận này thành hai bảng vector nhỏ: P (khách) và Q (sản phẩm); điểm dự đoán = tích vô hướng p_u · q_i. Nhờ vậy suy ra được điểm cho những ô chưa có dữ liệu.
- Trong đề tài:
  - **BPR-MF** là baseline MF;
  - **GMF** là MF dạng mạng nơ-ron (có trọng số riêng cho từng chiều);
  - trong NeuMF-F, nhánh **GMF-F** là MF trên vector có đặc trưng, nên còn học được tương tác giữa thuộc tính khách và
    thuộc tính sản phẩm. Kết quả: GMF-F đứng riêng đã ngang NeuMF-F trên cả H&M lẫn Amazon — nhánh MF có đặc trưng là
    phần mạnh nhất của mô hình.

Mở ở đâu: mục 2.2, 3.3.2.

### 9. Có thực sự xây mô hình lai không?

Có — **NeuMF-F**:
1. Mỗi nhánh (GMF và MLP) có vector khách = vector ID + chiếu của đặc trưng khách; vector sản phẩm = vector ID + chiếu của đặc trưng sản phẩm.
2. Nhánh GMF-F nhân từng phần tử hai vector (tuyến tính); nhánh MLP-F nối hai vector rồi qua 3 tầng ẩn (phi tuyến).
3. Hai kết quả được nối lại, qua một lớp dự đoán chung → điểm.

Hình 3.2 vẽ đủ kích thước: với d = 32, mỗi bảng Embedding có 32 cột, đặc trưng sản phẩm 157 chiều và khách 42 chiều được
chiếu về 32 chiều, tháp MLP 64 → 32 → 16 → 8, vector hợp nhất 40 chiều.

Ba so sánh trả lời trực tiếp "lai có tác dụng không":
- **NeuMF-F với NeuMF chỉ dùng ID:** đặc trưng có giúp không.
- **NeuMF-F với GMF-F, MLP-F:** hợp nhất có hơn từng nhánh không.
- **NeuMF-F với LateFusion-F:** hợp nhất sớm hay muộn tốt hơn.

Kết quả:
- **Đặc trưng giúp rõ:** NeuMF-F hơn NeuMF chỉ ID **43,8%** trên H&M và **65,7%** trên Amazon (đều có ý nghĩa).
- **Lai hơn nhánh DNN trên H&M** (MLP-F, +15,0%, có ý nghĩa) nhưng không còn có ý nghĩa trên Amazon (+6,9%);
  **không hơn nhánh MF** (GMF-F) ở cả hai bộ.
- **Hợp nhất sớm và muộn:** ngang nhau trên H&M (LateFusion-F cao hơn 2,2%, p Holm 0,735); trên Amazon LateFusion-F
  **tốt hơn** NeuMF-F có ý nghĩa (12,5%).

Mở ở đâu: mục 3.3 (Hình 3.2, công thức 3.6–3.9), 4.4.3, 4.5.2; `neumf_project/src/models/hybrid_features.py`.

### 10. Đã thử Transformer, Temporal, BERT chưa?

- **Đã dùng mô tả văn bản của sản phẩm:**
  - biểu diễn bằng TF-IDF rồi giảm còn 64 chiều (SVD);
  - nối vào vector của mô hình — cùng tinh thần chương 4 luận án của cô (vector MF + vector văn bản);
  - cách này nhẹ, chạy được trên máy không có GPU.
  - Ablation: bỏ vector văn bản làm NDCG@10 giảm 2,7% (H&M) và 9,8% (Amazon), khoảng tin cậy đều chứa 0 — chưa khẳng định được.
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

Kết quả ablation: bỏ đặc trưng thời gian làm NDCG@10 của NeuMF-F giảm **42,3%** trên H&M và **31,6%** trên Amazon — thành
phần đóng góp lớn nhất ở cả hai bộ (khoảng tin cậy không chứa 0). Bản thân MostPopular-Recent cũng là baseline khá mạnh
trên H&M: 0,02760 trên test, hơn Most Popular (0,02184) và ngang NeuMF (0,02783), BPR-MF (0,02661); NeuMF-F hơn nó 45,0%
(có ý nghĩa) — tức mô hình học được nhiều hơn xu hướng bán chung. Mở ở đâu: mục 3.2.5, 4.2, 4.4.4, 4.5.3.

### 12–13. Early fusion và Late fusion

Định nghĩa theo luận án của cô (mục 1.1.2.2):

| Kiểu | Định nghĩa | Trong đề tài |
|---|---|---|
| **Early fusion** | Nối biểu diễn của các nguồn → **một** mô hình dự đoán | **NeuMF-F** (và NeuMF): nối vector nhánh GMF với vector nhánh MLP → một lớp dự đoán chung, huấn luyện chung. Đặc trưng cũng được đưa vào ngay từ vector |
| **Late fusion** | Mỗi nguồn một mô hình riêng → trộn kết quả | **LateFusion-F**: w × điểm GMF-F + (1 − w) × điểm MLP-F (điểm chuẩn hoá về 0–1), hai mô hình huấn luyện riêng, w = 0,4 chọn trên tập xác thực (Thuật toán 3.5) |
| Không phải fusion | — | **MLP đứng riêng** chỉ là mạng DNN thuần |

So sánh NeuMF-F với LateFusion-F (cùng hai thành phần) nằm sẵn trong 10 so sánh đã đăng ký trước. **Kết quả:** trên H&M
**không khác biệt có ý nghĩa** — LateFusion-F 0,04093, NeuMF-F 0,04003 (thấp hơn 2,2%, p Holm 0,735); trên Amazon
**LateFusion-F tốt hơn có ý nghĩa** — 0,03747 so với 0,03277 (NeuMF-F thấp hơn 12,5%). Tức là trong hai cách ghép, hợp
nhất muộn không kém ở bộ nào đã thử. Mở ở đâu: mục 2.3.4 (Hình 2.2, công thức 2.13–2.15), 3.3.5, 4.4.3, 4.5.2.

### 14. Baseline gồm những gì? Lai có tốt hơn trước khi lai không?

Theo góp ý họp 04/10, baseline được xếp thành **ba nhóm** (báo cáo mục 4.2; cách xếp do nhóm đề xuất, chờ cô xác nhận):

| Nhóm | Mô hình | Trả lời câu hỏi |
|---|---|---|
| Mô hình đơn lẻ | GMF, MLP (chỉ mã ID); GMF-F, MLP-F (có đặc trưng) — từng nhánh của mô hình lai đứng riêng | Lai có hơn từng nhánh không |
| Học máy truyền thống | Content, ItemKNN, UserKNN, BPR-MF; **Hybrid-CBCF** — mô hình lai truyền thống (bổ sung) | Lai học sâu có hơn cách làm truyền thống, kể cả lai truyền thống, không |
| Chuyên biệt cho gợi ý | Most Popular, MostPopular-Recent; NeuMF (NCF gốc); LateFusion-F (hợp nhất muộn) | Có hơn xu hướng phổ biến, NCF gốc và hợp nhất muộn không |

Mô hình đề xuất: **NeuMF-F** (early fusion). Random là cận dưới.

- "Lai có tốt hơn trước khi lai" = so sánh NeuMF-F với GMF-F và MLP-F. **Kết quả H&M:** hơn MLP-F (+15,0%), ngang GMF-F
  (+2,6%, không có ý nghĩa). Với baseline: hơn cả 5 baseline trong họ so sánh (BPR-MF, ItemKNN, UserKNN,
  MostPopular-Recent, Content) trên cả H&M lẫn Amazon.
- Chỉ nói "A tốt hơn B" khi **đủ cả ba** điều kiện: p sau hiệu chỉnh Holm < 0,05; khoảng tin cậy 95% không chứa 0; chênh lệch ≥ 5%. Tiêu chí này cố định từ trước khi chấm.
- **Mô hình lai truyền thống Hybrid-CBCF** (theo chương 3 luận án của cô): ba mô hình đơn lẻ — Content (lọc nội dung),
  UserKNN, ItemKNN (lọc cộng tác) — chấm riêng; điểm mỗi mô hình chuẩn hoá về 0–1 trên tập ứng viên của khách; rồi kết
  hợp bằng bỏ phiếu (trung bình, max, min) hoặc tổng có trọng số. Trên tập xác thực của mẫu phát triển, tổng có trọng
  số tốt nhất (NDCG@10 0,02815, so với trung bình 0,02634 và UserKNN đứng riêng 0,02753); trọng số Content 0,12,
  UserKNN 0,60, ItemKNN 0,28 — lọc cộng tác là chính.
- **Vì sao học trọng số theo cặp?** Luận án học trọng số trên điểm đánh giá (rating); dữ liệu của đề tài chỉ có mua /
  không mua. Nếu chạy hồi quy logistic thường trên từng cặp (khách, sản phẩm), trọng số học ra âm và mô hình hỏng
  (NDCG@10 ≈ 0,0005), vì gộp mọi khách thì khác biệt giữa các khách lấn át thứ tự trong danh sách của từng khách. Học
  theo cặp (món đúng so với món không đúng **của cùng một khách**) là đúng mục tiêu xếp hạng — cùng tiêu chí với BPR.
- **Vì sao thêm sau khi đã chấm tập kiểm thử, có thiên lệch không?** Mô hình được thêm theo góp ý của cô, sau đánh giá
  cuối, nên làm như một **phân tích bổ sung**: kế hoạch riêng `PREREG_bosung.md` commit trước khi chấm; cách kết hợp chọn
  trên tập xác thực, không nhìn tập kiểm thử; tập kiểm thử mở thêm đúng một lần cho mô hình này; hai so sánh bổ sung
  (NeuMF-F vs Hybrid-CBCF, Hybrid-CBCF vs UserKNN) hiệu chỉnh Holm riêng; họ 10 so sánh và kết luận cũ giữ nguyên. Điều
  phải nói thẳng: lúc thêm, nhóm đã biết kết quả kiểm thử của ba thành phần.
- **Kết quả trên tập kiểm thử** (chấm một lần mỗi bộ, 13/10/2026):
  - H&M: Hybrid-CBCF đạt NDCG@10 0,03183, hạng 5/15, ngay sau bốn mô hình có đặc trưng. NeuMF-F hơn nó **+25,8%, có ý
    nghĩa**. So với UserKNN, Hybrid-CBCF chỉ hơn +2,2%, **không khác biệt có ý nghĩa** — trọng số dồn vào UserKNN, còn
    Content đứng riêng rất yếu.
  - Amazon (dùng nguyên trọng số chọn trên H&M): 0,02664, hạng 5/15. NeuMF-F hơn **+23,0%, có ý nghĩa**; Hybrid-CBCF hơn
    UserKNN **+6,3%, có ý nghĩa**. Có thể vì Content trên Amazon không quá yếu (hơn 1/3 NDCG@10 của UserKNN, so với
    khoảng 1/6 trên H&M) — nhận định, chưa kiểm chứng.
  - Câu trả lời ngắn: ghép điểm các kỹ thuật truyền thống giúp ít; thêm đặc trưng vào mô hình lai học sâu giúp nhiều hơn
    hẳn.

Mở ở đâu: mục 2.1.1, 3.6 (Thuật toán 3.6), 4.2 (Bảng 4.1), 4.3 (Bảng 4.3), 4.4.4 (Bảng 4.8), 4.5.1 (Bảng 4.14), 4.8.

### 15. Sơ đồ kiến trúc

- **Hình 2.1** — kiến trúc NeuMF, có kích thước từng ma trận và từng tầng, nối tới σ → điểm → sắp xếp → Top-K.
- **Hình 2.2** — hợp nhất sớm (NeuMF, NeuMF-F) so với hợp nhất muộn (LateFusion-F).
- **Hình 3.1** — đường ống: dữ liệu → tiền xử lý → đặc trưng → huấn luyện → lưu mô hình → suy diễn Top-K (không có ô
  đánh giá).
- **Hình 3.2** — kiến trúc NeuMF-F, có kích thước ma trận (d = 32: tháp 64 → 32 → 16 → 8), nối tới Top-K.
- **Hình 3.3** — quy trình đánh giá riêng: tinh chỉnh trên mẫu phát triển → đăng ký trước, khoá test → huấn luyện lại →
  Full Ranking trên mẫu kiểm định → kiểm định họ 10 so sánh.
- **Hình 3.4** — kiến trúc ba tầng của demo.
- **Thuật toán 3.1–3.7** — mã giả: chuẩn bị dữ liệu (gộp product_code, k-core lặp), lấy mẫu âm, huấn luyện có dừng sớm
  và huấn luyện lại, Full Ranking, chọn w của LateFusion-F, chọn cách kết hợp của mô hình lai truyền thống, suy diễn
  Top-K có xử lý khách mới.

Luồng cô gợi ý (dữ liệu → tiền xử lý → chia → ma trận → MF → vector → DL → hợp nhất → điểm → xếp hạng → Top-K) được Hình
3.1, 3.2 và 2.1 thể hiện đủ.

### 16. Mô hình "variational" nhắc trong buổi họp

- Chưa triển khai; **cần hỏi lại cô tên mô hình**, không tự khẳng định.
- Khả năng cao là Mult-VAE (Liang và cộng sự, 2018), đã trình bày lý thuyết ở mục 2.4.4.
- Tập kiểm thử của mẫu kiểm định **đã mở** (10/10). Nếu cô yêu cầu, chỉ thêm được dưới dạng **thăm dò sau kiểm thử**:
  tinh chỉnh trên mẫu phát triển như mọi mô hình, chấm trên mẫu kiểm định, nhưng ghi rõ là lệch kế hoạch (PREREG_v2 mục
  10) và không đưa vào họ 10 so sánh.

### 17. Lộ trình 10 bước — đã làm đến đâu?

| # | Bước | Trạng thái |
|---|---|---|
| 1 | Sửa cách chia Train/Test | Xong — chia theo thời gian; một sản phẩm = một mẫu thiết kế |
| 2 | Kiểm tra rò rỉ dữ liệu | Xong — có test tự động |
| 3 | Bộ test chuẩn | Xong — mẫu kiểm định độc lập (khối 2), file dữ liệu kiểm MD5, khoá test |
| 4 | Chạy lại Baseline/MF | Xong — tinh chỉnh trên mẫu phát triển, chấm trên mẫu kiểm định (BPR-MF 0,02661) |
| 5 | Mô hình Deep Learning | Xong — MLP, MLP-F |
| 6 | Xây mô hình lai | Xong — NeuMF-F (0,04003, hơn NeuMF chỉ ID 43,8%) |
| 7 | Thử Fusion | Xong — Early (NeuMF-F) và Late (LateFusion-F); ngang nhau trên H&M, Late tốt hơn trên Amazon |
| 8 | Bảng NDCG/HR/Recall/Precision | Xong — tự sinh từ kết quả 5 seed, ở K = 5, 10, 15, 20 |
| 9 | Vẽ kiến trúc | Xong — Hình 2.1, 3.1, 3.2, 3.3 (vẽ lại theo góp ý 04/10), mã giả Thuật toán 3.1–3.7 |
| 10 | Phân tích kết quả | Xong — kiểm định, ablation, độ phủ, ổn định giữa hai mẫu, kiểm chứng Amazon, phần thảo luận Chương 4 |

---

## Phần D. Câu hỏi khó nên chuẩn bị

**"Vì sao đổi cách làm gần cuối dự án? Kết quả cũ thế nào?"**
Có hai lần đổi:
1. **Giai đoạn phát triển ban đầu → quy trình hiện tại (cuối tháng 9):** giai đoạn đầu (chỉ dùng mã ID) cho thấy NeuMF
   chỉ dùng mã ID **không** tốt hơn MF đã tinh chỉnh (BPR-MF cao nhất; 0/8 so sánh có ý nghĩa; tiền huấn luyện không
   giúp); lọc k-core dùng cả dữ liệu giai đoạn test; tập kiểm thử cũ đã bị xem nhiều lần. Quy trình hiện tại thêm đặc
   trưng, sửa cách lọc và lấy kết luận trên khách hàng mới hoàn toàn.
2. **Bản đầu → bản cuối của kế hoạch (09/10):** bản đầu tính theo từng màu, có sản phẩm mới và đánh giá trên khối 1 (mở
   04/10). Theo góp ý của cô, bản cuối gộp theo mẫu thiết kế, bỏ sản phẩm chưa có người mua, ghi dữ liệu ra file kiểm
   MD5 và đánh giá trên khối 2.

Kết quả của hai giai đoạn trước vẫn được báo cáo trung thực ở mục 4.6, không trộn với bản cuối.

**"Việc đã xem kết quả trước đó có làm lệch kết luận không?"**
Có ảnh hưởng ở mức thiết kế: biết mô hình chỉ dùng mã ID không hơn MF nên bổ sung đặc trưng; bản cuối được quyết định
**sau khi xem kết quả khối 1**. Vì vậy khối 1 bị loại, kết luận chỉ lấy trên khối 2 — dữ liệu chưa ai xem; kế hoạch bản
cuối được lưu (commit) sau khi tinh chỉnh lại trên mẫu phát triển và **trước** khi dựng tập kiểm thử của khối 2; độ đo
chính, họ 10 so sánh và tiêu chí kết luận giữ nguyên từ bản 03/10.

**"Kết quả khối 1 khác bản cuối (khối 1: LateFusion-F tốt hơn NeuMF-F có ý nghĩa) — tin cái nào?"**
Bản cuối. Khối 1 khác dữ liệu (theo màu, có sản phẩm mới) và đã được dùng để ra quyết định (đổi thiết kế), nên không còn
là ước lượng không thiên lệch. Điểm chung của cả hai: ba vị trí đầu đều là LateFusion-F, GMF-F và NeuMF-F (thứ tự khác
nhau), và NeuMF chỉ dùng ID không hơn BPR-MF có ý nghĩa. Trên Amazon, LateFusion-F cũng tốt hơn NeuMF-F có ý nghĩa — nên
nhận định an toàn là: hợp nhất muộn không kém hợp nhất sớm ở bất kỳ dữ liệu nào đã thử.

**"Seed 42 chạy lại — vậy có vi phạm 'mở tập kiểm thử một lần' không?"**
Lần chạy đầu dừng giữa chừng ở seed 42, sau khi đã chấm Random và 5 mô hình tất định (Most Popular, MostPopular-Recent,
Content, ItemKNN, UserKNN), trước khi lưu bất kỳ kết quả nào. Seed 42 được chạy lại với cùng mã nguồn, cấu hình và dữ
liệu; việc này ghi ở mục lệch kế hoạch (PREREG_v2 mục 10) và trong nhật ký truy cập (`v2_kiemdinh_seed42_rerun`). Không
quyết định nào được đưa ra sau khi thấy các số trên màn hình — cấu hình đã cố định, và 5 mô hình tất định cho cùng kết
quả ở lần chạy lại. Các seed khác mở tập kiểm thử đúng một lần.

**"LateFusion-F cao nhất (và trên Amazon còn tốt hơn có ý nghĩa) — sao không lấy LateFusion-F làm mô hình chính?"**
- Mô hình chính phải cố định **trước** khi xem test (PREREG_v2 mục 8, PREREG_amazon mục 8): đề tài là mô hình lai hợp
  nhất sớm MF + DNN có đặc trưng, nên NeuMF-F được chọn từ đầu, không theo kết quả. Đổi mô hình chính sau khi thấy test
  là chọn theo kết quả — đúng điều giao thức muốn tránh.
- Báo cáo nói thẳng kết quả: trên H&M hai cách hợp nhất ngang nhau (chênh 2,2%, p Holm 0,735); trên Amazon hợp nhất muộn
  tốt hơn có ý nghĩa (12,5%). Đây là câu trả lời cho câu hỏi của cô về early/late fusion: với cùng hai thành phần có đặc
  trưng, trộn điểm của hai mô hình huấn luyện riêng không kém — và có thể tốt hơn — ghép vector rồi học chung.
- Một nhận định (chưa kiểm chứng): trên Amazon hai nhánh GMF-F và MLP-F gợi ý những tập sản phẩm rất khác nhau (độ phủ
  32,1% so với 5,4%), trộn điểm tận dụng được sự khác nhau đó; cũng có thể cấu hình chọn trên H&M hợp với LateFusion-F hơn.

**"Amazon dùng lại siêu tham số của H&M, không tinh chỉnh — vậy có công bằng không?"**
- Đây là quyết định ghi trong kế hoạch **trước khi chạy** bất kỳ mô hình nào trên Amazon (PREREG_amazon mục 4): mục đích
  là kiểm tra kết luận có còn đúng khi đổi dữ liệu mà **không** được chỉnh lại theo dữ liệu mới. Chỉ số epoch được chọn
  trên tập xác thực Amazon.
- Hệ quả: mô hình nào có cấu hình không hợp với Amazon sẽ bị thiệt — rõ nhất là BPR-MF (0,01144, kém cả ItemKNN và
  MostPopular-Recent). Vì vậy hai so sánh có BPR-MF trên Amazon không dùng làm bằng chứng; báo cáo ghi rõ ở Bảng 4.16.
- Kết luận về đặc trưng vẫn đúng dù không tinh chỉnh — đó là điểm vững nhất.

**"K = 15 lấy ở đâu ra, có chạy lại không?"**
Không chạy lại. Lần đánh giá cuối đã lưu **hạng của từng món đúng** cho từng khách, từng mô hình, từng seed
(`per_user.csv.gz`, cột `ranks`). Từ hạng đó tính được mọi chỉ số ở K bất kỳ bằng đúng hàm đã dùng khi chấm; chương
trình còn kiểm tra rằng tính lại @5, @10, @20 cho đúng y các số đã báo cáo (lệch 0). Mở ở đâu: mục 4.4.2, Thuật toán 3.4.

**"Ba nghiên cứu nền tảng là gì, số liệu của họ so với đề tài thế nào?"**
He et al. (2017) — NCF/NeuMF; Rendle et al. (2020) — MF tinh chỉnh kỹ so với NeuMF; luận án của cô (2023) — Early/Late
Fusion đa nguồn. Bảng 2.2 ghi cho từng bài: dữ liệu, độ đo, cách chia, kích thước tập ứng viên và số liệu của bài gốc.
Hai bài NCF xếp hạng trên 101 ứng viên (HR@10 khoảng 0,7–0,9), luận án dự đoán điểm đánh giá (RMSE, MAE), còn đề tài xếp
hạng trên khoảng 6–7 nghìn ứng viên — nên số tuyệt đối không so được; chỉ đọc chiều và mức cải thiện tương đối mà mỗi bài
tự báo cáo. Ba bài được chọn là đề xuất của nhóm, **cô có thể đổi**.

**"Vì sao hợp nhất sớm không hơn nhánh GMF-F đứng riêng?"** (nói rõ là nhận định, chưa kiểm chứng)
GMF-F đứng riêng đã ngang NeuMF-F trên cả hai bộ (+2,6% H&M, −0,6% Amazon, đều không có ý nghĩa), trong khi MLP-F kém hơn
rõ trên H&M (NeuMF-F hơn MLP-F 15,0%). Phần lớn lợi ích nằm ở **đặc trưng** — nhất là đặc trưng thời gian — đưa vào nhánh
MF, chứ không ở việc thêm nhánh phi tuyến.

**"Thứ hạng có ổn định giữa lúc tinh chỉnh (mẫu phát triển) và test (mẫu kiểm định) không?"**
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
trước mốc kiểm thử, mẫu phát triển giảm từ 55.971 xuống 27.370 sản phẩm. Đổi lại, gợi ý ở mức mẫu thiết kế, không ở mức
màu — đã ghi là hạn chế.

**"Vì sao lọc k-core = 10, vì sao chỉ lấy mẫu 500 nghìn giao dịch?"**
Do bộ nhớ máy (16 GB RAM):
- chấm điểm toàn bộ sản phẩm cho mọi khách ở quy mô đầy đủ là hàng chục tỷ phép tính;
- khảo sát ở giai đoạn phát triển: với k = 5, ước tính cần khoảng 10,7 GB RAM.

Hệ quả: dữ liệu thiên về khách mua nhiều — đã ghi là hạn chế. Amazon dùng k = 5 (bằng bản 5-core gốc). Mở ở đâu: mục
3.2.1, 3.2.3, 5.2.

**"Có bị quá khớp (overfitting) không, xử lý thế nào?"**
- Dừng sớm theo NDCG@10 trên tập xác thực (dừng sau 5 epoch không cải thiện).
- Dropout trong tầng ẩn.
- Điều chuẩn L2 (weight decay).
- Bỏ ID ngẫu nhiên là một siêu tham số được tinh chỉnh (ρ ∈ {0; 0,25; 0,5}); NeuMF-F và MLP-F chọn 0, GMF-F chọn 0,25.

Khi huấn luyện lại, dừng đúng số epoch đã chọn. Mở ở đâu: mục 3.3.3, 3.5.1 (Thuật toán 3.3).

**"Vì sao 5 seed? Kiểm định thế nào?"**
- Kiểm định theo từng khách hàng (hàng nghìn khách), không theo seed. Mỗi khách lấy điểm trung bình qua 5 seed rồi so hai mô hình bằng Wilcoxon, kèm khoảng tin cậy bootstrap và hiệu chỉnh Holm cho 10 so sánh.
- Nếu kiểm định theo seed thì với 5 seed, p nhỏ nhất cũng chỉ 0,0625, không bao giờ dưới 0,05.

**"Demo dùng mô hình nào? Khách không có trong dữ liệu thì sao?"**
Đúng các mô hình của đánh giá cuối (seed 42), chỉ suy diễn, không huấn luyện lại; chọn được H&M hoặc Amazon Beauty. Mỗi
sản phẩm hiển thị theo mẫu thiết kế (tên và ảnh của màu đầu tiên, kèm số màu). Số trên demo được test tự động đối chiếu
với file kết quả theo từng khách. **Luôn có gợi ý:** khách đã có lịch sử nhận gợi ý của mô hình (khách không mua món mới
nào sau mốc thì chỉ có gợi ý, không có chỉ số); khách mới nhận danh sách "Gợi ý phổ biến" (Most Popular) thay vì báo lỗi.

**"Có gì khác so với đề cương?"**

| Đề cương | Thực tế | Lý do |
|---|---|---|
| Chia leave-one-out | Chia theo thời gian | Leave-one-out lọt thông tin tương lai (câu 1f) |
| Sản phẩm theo `article_id` | Sản phẩm theo mẫu thiết kế (`product_code`) | Theo góp ý của cô |
| Baseline ALS | BPR-MF | Cùng nhóm MF cho phản hồi ẩn; iALS chỉ thử ở giai đoạn phát triển |
| Thử đặc trưng Category/Department | **Đã dùng** (11 thuộc tính sản phẩm) | — |
| K = 5/10/20 | Có đủ, thêm K = 15 | K = 15 tính lại từ hạng đã lưu, theo góp ý 04/10 |
| Một bộ dữ liệu | Thêm kiểm chứng trên Amazon Beauty | Theo góp ý 04/10: dữ liệu đối chứng có bài báo |
| Biểu đồ hội tụ (TensorBoard/W&B) | Ghi ra file CSV, vẽ bằng matplotlib | Cùng thông tin, truy vết được trong repo |
| Demo FastAPI + Streamlit | FastAPI + giao diện HTML | Chức năng tương đương |
| Báo cáo 6 chương | 5 chương | Gộp cài đặt và kết quả vào Chương 4 |
