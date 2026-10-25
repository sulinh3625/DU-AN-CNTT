# Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F

Tài liệu này để cả nhóm nắm toàn bộ đề tài và trả lời thống nhất trước hội đồng. Số mục, số bảng, số hình ghi theo
bản báo cáo hiện tại (104 trang, cập nhật 20/10/2026). Mọi số liệu ở đây khớp với báo cáo (kiểm bằng
`python run.py check-report`).

| Cần gì | Đọc phần |
|---|---|
| Mở đầu phần trình bày (3 phút) | Phần 1 |
| Hiểu toàn bộ đề tài theo từng chương | Phần 2 |
| Số liệu phải thuộc | Phần 3 |
| Cái gì nói trong báo cáo, cái gì chỉ nói khi được hỏi | Phần 4 |
| Câu hỏi hội đồng hay hỏi và cách trả lời | Phần 5 |
| Câu không được nói | Phần 6 |
| Kịch bản chạy demo | Phần 7 |
| Tra nhanh chương, mục, bảng, hình | Phần 8 |

---

## Phần 1. Thông điệp chính

### 1.1 Ba câu phải nói được ngay

1. Đề tài xây dựng **NeuMF-F**, mô hình lai giữa nhân tử hóa ma trận và mạng nơ-ron sâu, có bổ sung **đặc trưng sản
   phẩm, khách hàng và thời gian** vào cả hai nhánh.
2. NeuMF-F **vượt có ý nghĩa thống kê** các mô hình đối chứng được tinh chỉnh đầy đủ và một mô hình lai truyền thống,
   trên **hai bộ dữ liệu thuộc hai lĩnh vực** (thời trang H&M, mỹ phẩm Amazon Beauty).
3. Đề tài chỉ ra **phần cải thiện đến từ đâu**: chủ yếu từ biểu diễn có đặc trưng, trong đó **đặc trưng thời gian**
   quan trọng nhất. Kết quả được lấy theo một **quy trình đánh giá chặt chẽ** (chia theo thời gian, mẫu kiểm định độc
   lập, đăng ký trước, kiểm định thống kê).

### 1.2 Bốn đóng góp (dùng cho slide kết luận)

| # | Đóng góp | Bằng chứng |
|---|---|---|
| 1 | Mô hình lai có đặc trưng vượt các phương pháp đối chứng | H&M: NeuMF-F tốt hơn có ý nghĩa 7/10 so sánh, không thua so sánh nào; tốt hơn Hybrid-CBCF +25,8% |
| 2 | Kết quả tổng quát qua hai lĩnh vực | Amazon: NeuMF-F hơn NeuMF chỉ ID +65,7% và cả 5 mô hình đối chứng, **không tinh chỉnh lại** |
| 3 | Chỉ ra nguồn gốc cải thiện | NeuMF-F hơn NeuMF chỉ ID +43,8% (H&M); bỏ đặc trưng thời gian làm NDCG@10 giảm 42,3% (H&M), 31,6% (Amazon) |
| 4 | Quy trình đánh giá và hệ thống hoàn chỉnh | Sáu nguyên tắc đánh giá (mục 3.7.2), demo chạy được trên cả hai bộ dữ liệu, 14 mô hình |

### 1.3 Lời mở đầu gợi ý (khoảng 3 phút)

> Gợi ý sản phẩm thời trang khó vì dữ liệu rất thưa và xu hướng đổi nhanh. Nhân tử hóa ma trận chỉ học từ mã khách và mã
> sản phẩm, nên không dùng được những thông tin doanh nghiệp đã có như loại hàng, doanh số gần đây hay nhịp mua của
> khách. Nhóm xây dựng NeuMF-F: giữ hai nhánh MF và mạng nơ-ron của NeuMF, nhưng biểu diễn mỗi khách và mỗi sản phẩm
> bằng mã ID cộng với đặc trưng. Để kết luận đáng tin, nhóm chia dữ liệu theo thời gian, tinh chỉnh mọi mô hình với cùng
> ngân sách, và chấm điểm cuối trên một nhóm khách hàng hoàn toàn mới. Kết quả: NeuMF-F vượt có ý nghĩa các mô hình đối
> chứng trên H&M, và kết luận lặp lại trên Amazon Beauty dù không tinh chỉnh lại. Phân tích cho thấy đặc trưng thời
> gian đóng góp nhiều nhất. Cuối cùng, nhóm xin demo hệ thống trên một khách hàng cụ thể.

---

## Phần 2. Nắm toàn bộ đề tài

### 2.1 Bài toán và câu hỏi nghiên cứu (Chương 1)

- **Bài toán:** gợi ý Top-K sản phẩm cho từng khách từ lịch sử mua (phản hồi ẩn: mua / chưa mua, không có điểm đánh giá).
- **Ba câu hỏi nghiên cứu (mục 1.1.3)** — cả báo cáo xoay quanh ba câu này, nên phải nói được ngay:
  1. NeuMF-F có tốt hơn các mô hình đối chứng được tinh chỉnh đầy đủ không? → **Có**, trên cả hai bộ dữ liệu.
  2. Đặc trưng có giúp mô hình lai không, nhóm nào quan trọng nhất? → **Có**; đặc trưng thời gian quan trọng nhất.
  3. Ghép hai nhánh có hơn từng nhánh, hợp nhất sớm hay muộn tốt hơn? → Các cách ghép cho kết quả gần nhau; biểu diễn
     có đặc trưng mới là yếu tố quyết định.
- **Năm mục tiêu (mục 1.2.1):** (1) lý thuyết; (2) quy trình dữ liệu H&M; (3) cài đặt NeuMF-F và đối chứng; (4) đánh
  giá Top-K có kiểm định; (5) demo. **Tất cả đã hoàn thành** — Bảng 5.1 đối chiếu từng mục tiêu với kết quả.
- **Mạch của báo cáo:** Chương 1 đặt ba câu hỏi → Chương 2 cho cơ sở lý thuyết → Chương 3 thiết kế mô hình và quy trình
  để trả lời → Chương 4 trình bày kết quả và trả lời từng câu (mục 4.6, tóm tắt ở 4.7) → Chương 5 đối chiếu mục tiêu.

### 2.2 Cơ sở lý thuyết (Chương 2)

| Khái niệm | Nói ngắn | Mục |
|---|---|---|
| Lọc cộng tác | Gợi ý theo hành vi của những khách/sản phẩm giống nhau | 2.1 |
| UserKNN / ItemKNN | Tìm k khách (sản phẩm) giống nhất theo cosine, điểm = tổng độ giống | 2.1.2 |
| MF | Mỗi khách, sản phẩm là một vector; điểm = tích vô hướng | 2.2 |
| BPR | Học MF theo thứ hạng: món đã mua phải xếp trên món chưa mua | 2.2.3 |
| GMF | MF dạng mạng: nhân từng chiều rồi học trọng số riêng cho từng chiều | 2.3.1 |
| MLP | Nối hai vector rồi qua nhiều tầng phi tuyến | 2.3.2 |
| NeuMF | Ghép GMF và MLP ở lớp dự đoán (hợp nhất sớm) | 2.3.3, Hình 2.1 |
| Hợp nhất sớm / muộn | Sớm: ghép biểu diễn rồi một mô hình dự đoán. Muộn: mỗi mô hình dự đoán riêng rồi trộn điểm | 2.3.4, Hình 2.2 |
| NDCG@K | Món đúng càng ở trên càng nhiều điểm, chuẩn hóa 0–1 | 2.5 |
| Ba nghiên cứu nền tảng | He 2017 (NCF), Rendle 2020 (MF tinh chỉnh kỹ so với NeuMF), luận án cô Hồ Thị Linh 2023 | 2.6, Bảng 2.1 |
| Khoảng trống nghiên cứu | (1) mô hình NCF chưa khai thác đặc trưng cho Top-K; (2) thiếu đánh giá theo giao thức gần triển khai trên dữ liệu thời trang thật | 2.7 |

### 2.3 Dữ liệu và tiền xử lý (mục 3.2)

- H&M: 31,8 triệu giao dịch (20/09/2018 – 22/09/2020), 1,36 triệu khách, 104.547 sản phẩm có giao dịch.
- **Lấy mẫu theo khách** bằng hàm băm (giữ trọn lịch sử 2 năm của mỗi khách). Hai mẫu không có khách chung:
  **mẫu phát triển** (chọn cấu hình) và **mẫu kiểm định** (chấm điểm cuối).
- **Một sản phẩm = một mẫu thiết kế** (`product_code`, gộp mọi màu).
- Gộp giao dịch lặp thành một cặp (khách, sản phẩm) giữ ngày mua đầu; **lọc 10-core lặp, chỉ trên dữ liệu trước mốc kiểm
  thử** (Thuật toán 3.1).
- **Chia theo thời gian:** huấn luyện trước 01/07/2020; xác thực 01/07–28/07; kiểm thử 29/07–22/09/2020.
- **Tập ứng viên:** sản phẩm đã có dữ liệu huấn luyện, trừ món khách đã mua. **Món đúng:** món khách mua lần đầu trong
  cửa sổ đánh giá.
- **Đặc trưng theo thời điểm** (Bảng 3.4): sản phẩm (11 thuộc tính, văn bản TF-IDF + SVD 64 chiều, doanh số 7/28/91
  ngày, tuổi sản phẩm); khách (5 thuộc tính, số ngày từ lần mua gần nhất, số món đã mua). Mọi đặc trưng tại ngày t chỉ
  dùng dữ liệu **trước** ngày t.

### 2.4 Mô hình đề xuất NeuMF-F (mục 3.3, Hình 3.4)

- Mỗi nhánh có vector khách = vector ID + chiếu đặc trưng khách; vector sản phẩm = vector ID + chiếu đặc trưng sản phẩm.
- Nhánh **GMF-F** nhân từng phần tử (tuyến tính). Nhánh **MLP-F** nối hai vector, qua tháp 64 → 32 → 16 → 8 (với d = 32).
- Hai kết quả được nối, qua một lớp dự đoán chung (hợp nhất sớm). Xếp hạng dùng logit.
- Huấn luyện: BCE + lấy mẫu âm theo ngày ra mắt (Thuật toán 3.2), Adam, lô 512, dừng sớm theo NDCG@10 xác thực, rồi
  **huấn luyện lại từ đầu** đúng số epoch tốt nhất trên mọi dữ liệu trước mốc kiểm thử (Thuật toán 3.3).

### 2.5 Mô hình đối chứng (mục 3.4, Bảng 3.5)

| Nhóm | Mô hình | Câu hỏi được trả lời |
|---|---|---|
| Mô hình đơn lẻ | GMF, MLP; GMF-F, MLP-F | Ghép hai nhánh có hơn từng nhánh không |
| Học máy truyền thống | Content, ItemKNN, UserKNN, BPR-MF; Hybrid-CBCF (bổ sung) | Có hơn cách làm truyền thống, kể cả lai truyền thống, không |
| Chuyên biệt cho gợi ý | Most Popular, MostPopular-Recent, NeuMF, LateFusion-F | Có hơn xu hướng phổ biến, NCF gốc, hợp nhất muộn không |

Random là mốc dưới. Tổng cộng 14 mô hình đăng ký trước, cộng Hybrid-CBCF là 15.

### 2.6 Quy trình đánh giá (mục 3.7, Hình 3.5)

Sáu nguyên tắc (mục 3.7.2):
1. Tách mẫu phát triển và mẫu kiểm định.
2. Đăng ký trước kế hoạch và khóa tập kiểm thử.
3. Cùng ngân sách tinh chỉnh: 6 cấu hình mỗi mô hình (Bảng 3.6).
4. Huấn luyện lại trước khi chấm, 5 seed (42, 2024, 2025, 2026, 3407).
5. Kiểm định Wilcoxon ghép cặp theo khách, khoảng tin cậy bootstrap 95%, hiệu chỉnh Holm cho họ 10 so sánh.
6. "A tốt hơn B" chỉ khi đủ ba điều kiện: p Holm < 0,05; khoảng tin cậy không chứa 0; chênh lệch ≥ 5%.

Đánh giá bằng **xếp hạng toàn bộ** tập ứng viên (khoảng 6,7 nghìn sản phẩm mỗi khách), không lấy mẫu 100 ứng viên.

### 2.7 Kết quả (Chương 4)

- **H&M (mục 4.3):** bốn mô hình có đặc trưng đứng đầu (LateFusion-F, NeuMF-F, GMF-F, MLP-F), rồi đến UserKNN.
  NeuMF-F tốt hơn có ý nghĩa NeuMF chỉ ID, MLP-F và cả 5 mô hình đối chứng; tương đương GMF-F và LateFusion-F.
- **Theo K (mục 4.3.2):** thứ tự bốn mô hình đầu giữ nguyên ở mọi K = 10, 15, 20 và mọi độ đo. Báo cáo bỏ K = 5 vì danh sách 5 món quá ngắn để khuyến nghị trúng (số @5 vẫn lưu trong kết quả).
- **Bóc tách (mục 4.3.5):** đặc trưng thời gian quan trọng nhất, rồi đến thông tin khách hàng.
- **Hybrid-CBCF (mục 4.3.4):** NeuMF-F tốt hơn có ý nghĩa; Hybrid-CBCF chỉ ngang UserKNN trên H&M.
- **Amazon (mục 4.4):** kết luận về đặc trưng giữ nguyên; LateFusion-F cao nhất.
- **Trả lời câu hỏi (mục 4.6, 4.7):** câu 1 và câu 2 được trả lời "có" trên cả hai bộ; câu 3: biểu diễn có đặc trưng là
  yếu tố quyết định, cách hợp nhất có thể chọn theo dữ liệu.

### 2.8 Demo (mục 3.9)

Ba tầng: giao diện HTML/JS → API FastAPI (chỉ suy luận) → mô hình đã lưu (seed 42) và dữ liệu tra cứu. Chọn được H&M
hoặc Amazon. Có cửa hàng mô phỏng: NeuMF-F cố định bên trái, chọn một mô hình đối chứng đặt bên phải; khách giống gu
(UserKNN), sản phẩm tương tự (ItemKNN); màn hình kết quả đặt NeuMF-F cạnh từng mô hình đối chứng kèm kết luận kiểm định.
Khách mới nhận "Khuyến nghị phổ biến".

---

## Phần 3. Số liệu cần nhớ

Số tinh chỉnh chỉ dùng để **chọn cấu hình**; kết luận chỉ lấy từ tập kiểm thử của mẫu kiểm định và kiểm chứng trên
Amazon.

| Nội dung | Giá trị | Mở ở đâu |
|---|---|---|
| Mẫu phát triển | 500.269 giao dịch của 21.599 khách | mục 3.2.2 |
| Mẫu kiểm định | 500.164 giao dịch của 21.351 khách, **không có khách chung** với mẫu phát triển | mục 3.2.2 |
| Gộp theo mẫu thiết kế | Trước mốc kiểm thử: mẫu phát triển 55.971 → 27.370 sản phẩm, 401.293 → 359.181 cặp; mẫu kiểm định 55.683 → 27.291 sản phẩm, 398.653 → 356.740 cặp | mục 3.2.3 |
| Sau lọc 10-core | Mẫu phát triển: 8.039 khách, 6.801 sản phẩm, 245.644 cặp. Mẫu kiểm định: 7.994 khách, 6.749 sản phẩm, 243.696 cặp | mục 3.2.3, Bảng 3.3 |
| Mốc thời gian | Xác thực: 01/07–28/07/2020 (4 tuần). Kiểm thử: 29/07–22/09/2020 (8 tuần) | mục 3.2.4 |
| Tập kiểm thử mẫu kiểm định | 3.165 khách; 10.285 cặp đúng; trung bình 6.710 ứng viên mỗi khách | Bảng 3.3 |
| Kết quả tinh chỉnh (NDCG@10 xác thực) | LateFusion-F 0,03556 · NeuMF-F 0,03337 · MLP-F 0,03212 · GMF-F 0,03162 · GMF 0,02857 · UserKNN 0,02753 · MLP 0,02742 · NeuMF 0,02696 · BPR-MF 0,02636 · ItemKNN 0,02599 · MostPopular-Recent 0,02334 · Most Popular 0,02174 · Content 0,00459 | mục 4.2, Bảng 4.2 |
| Kết quả cuối H&M (NDCG@10, 5 seed) | **LateFusion-F 0,04093** · **NeuMF-F 0,04003** · GMF-F 0,03902 · MLP-F 0,03480 · UserKNN 0,03114 · ItemKNN 0,02860 · NeuMF 0,02783 · MostPopular-Recent 0,02760 · GMF 0,02695 · BPR-MF 0,02661 · MLP 0,02373 · Most Popular 0,02184 · Content 0,00506 · Random 0,00098 | mục 4.3.1, Bảng 4.4 |
| HR@10 | NeuMF-F khoảng 15% (cứ khoảng 1/6–1/7 khách có ít nhất một món đúng trong 10 gợi ý); cao nhất 15,8% (LateFusion-F) | Bảng 4.6 |
| Theo K (H&M, NeuMF-F) | NDCG@10/15/20 = 0,04003 / 0,04644 / 0,05166; HR@15 = 0,19406 | mục 4.3.2, Bảng 4.5–4.6 |
| 10 so sánh H&M | NeuMF-F tốt hơn 7 (NeuMF +43,8%, MLP-F +15,0%, BPR-MF +50,4%, ItemKNN +39,9%, UserKNN +28,5%, MostPopular-Recent +45,0%, Content +691,5%); tương đương 2 (GMF-F +2,6%, LateFusion-F −2,2%, p Holm 0,735). NeuMF vs BPR-MF: tương đương (+4,6%, p Holm 0,059) | mục 4.3.3, Bảng 4.7 |
| Bóc tách H&M (seed 42) | Bỏ thời gian **−42,3%**, bỏ thông tin khách −10,3% (khoảng tin cậy không chứa 0); bỏ thuộc tính −3,7%, văn bản −2,7% (khoảng tin cậy chứa 0) | mục 4.3.5, Bảng 4.9 |
| Hybrid-CBCF | H&M: NDCG@10 0,03183, hạng 5/15; NeuMF-F tốt hơn +25,8%; so với UserKNN +2,2% (tương đương). Amazon: 0,02664, hạng 5/15; NeuMF-F tốt hơn +23,0%; so với UserKNN +6,3% (tốt hơn) | mục 4.3.4, 4.4.2 |
| Trọng số Hybrid-CBCF | Content 0,12; UserKNN 0,60; ItemKNN 0,28 | mục 4.2, Bảng 4.3 |
| Trọng số LateFusion-F | w = 0,4 cho GMF-F (0,6 cho MLP-F) | mục 3.7.2, Thuật toán 3.5 |
| Amazon — dữ liệu | Bản 5-core: 198.502 đánh giá, 22.363 khách, 12.101 sản phẩm. Lọc 5-core trước 01/01/2014: 10.681 khách, 6.069 sản phẩm, 94.009 cặp. Kiểm thử 01/01–23/07/2014: 2.644 khách, 6.107 cặp đúng, 6.058 ứng viên mỗi khách | mục 4.4.1, Bảng 4.12 |
| Amazon — kết quả (NDCG@10, 5 seed) | **LateFusion-F 0,03747** · GMF-F 0,03298 · NeuMF-F 0,03277 · MLP-F 0,03065 · UserKNN 0,02506 · ItemKNN 0,02333 · NeuMF 0,01978 · GMF 0,01627 · MostPopular-Recent 0,01401 · MLP 0,01271 · BPR-MF 0,01144 · Content 0,00945 · Most Popular 0,00872 | mục 4.4.2, Bảng 4.13 |
| Amazon — 10 so sánh | NeuMF-F tốt hơn NeuMF +65,7% và cả 5 mô hình đối chứng (từ +30,8% với UserKNN); tương đương GMF-F (−0,6%) và MLP-F (+6,9%); LateFusion-F tốt hơn NeuMF-F (NeuMF-F −12,5%) | mục 4.4.3, Bảng 4.17–4.18 |
| Amazon — bóc tách | Bỏ thời gian −31,6%, bỏ thuộc tính −14,4% (khoảng tin cậy không chứa 0); bỏ văn bản −9,8%, bỏ thông tin khách +1,3% (khoảng tin cậy chứa 0) | mục 4.4.4, Bảng 4.19 |

**Cách nói số cho dễ nhớ:** "NeuMF-F hơn NeuMF gốc khoảng 44% trên H&M và 66% trên Amazon"; "bỏ đặc trưng thời gian thì
mất khoảng 40% chất lượng"; "hơn mô hình đối chứng mạnh nhất (UserKNN) khoảng 28%".

---

## Phần 4. Nội dung nào nói trong báo cáo, nội dung nào chỉ nói khi được hỏi

Nguyên tắc: báo cáo trình bày **đầy đủ kết quả** và **phạm vi** của kết luận, theo hướng nêu đóng góp. Chi tiết về quá
trình làm (các lần thử, sự cố, lý do kỹ thuật nhỏ) chỉ nói khi hội đồng hỏi, và nói thẳng, ngắn, có lý do.

| Nội dung | Trong báo cáo | Khi được hỏi thì nói thêm |
|---|---|---|
| LateFusion-F cao nhất, tốt hơn NeuMF-F trên Amazon | **Có**, nói rõ (mục 4.4.3, 4.6) — đây là kết quả, không được giấu | Lý do giữ NeuMF-F làm mô hình đề xuất (câu 5.4.1) |
| Khảo sát ban đầu: NeuMF chỉ ID không hơn BPR-MF | Có, như định hướng thiết kế (mục 3.7.1) | Giai đoạn đầu chỉ dùng mã ID, đánh giá trên mẫu phát triển |
| Khối 1 (mẫu kiểm định của bản kế hoạch đầu) | Không | Câu 5.6.1 |
| Seed 42 chạy lại, máy chạy (GPU RTX 3050 / CPU) | Không | Câu 5.6.2 |
| Content lệch nhẹ giữa Bảng 4.2 và 4.3 | Một câu ngắn (mục 4.2) | Vector văn bản được dựng lại trên máy khác khi chạy phần bổ sung; thứ hạng không đổi |
| K = 15 tính lại từ hạng đã lưu | Không nói chi tiết (mục 3.7.2 chỉ nói hạng được lưu) | Câu 5.3.6 |
| Hybrid-CBCF thêm sau đánh giá cuối | Có, ghi là phân tích bổ sung có kế hoạch riêng (mục 3.4, 4.3.4) | Câu 5.5.2 |
| Amazon không tinh chỉnh lại | Có, như một lựa chọn thiết kế (mục 4.4.1) | Câu 5.5.1 |
| Không có đối chứng FM dùng cùng đặc trưng | Một câu trong hạn chế và hướng phát triển (mục 5.3, 5.4) | Câu 5.2.4 |
| Lưới tinh chỉnh 6 cấu hình, vài cấu hình ở biên lưới | Bảng 3.6; không nêu trong hạn chế | Câu 5.3.3 |
| k-core dùng dữ liệu tháng 7 ảnh hưởng tập xác thực | Không | Câu 5.3.7 |
| Cold start | Có, là phạm vi (mục 1.2.2, 3.8, 5.3) | Câu 5.2.3 |
| Bỏ ID ngẫu nhiên chọn ρ = 0 | Có (mục 3.3.1, 4.2) | Câu 5.2.5 |
| Kế hoạch đăng ký trước, nhật ký mở tập kiểm thử | Báo cáo chỉ nói "lưu cùng mã nguồn" | Mở `neumf_project/audit/` khi cần chứng minh |

---

## Phần 5. Câu hỏi hội đồng hay hỏi

Cách trả lời câu khó: **thừa nhận ngắn → nêu lý do hoặc thiết kế đã xử lý → quay về điểm mạnh**. Không cãi, không vòng vo.

### 5.1 Đề tài và đóng góp

**5.1.1 "Đóng góp mới của đề tài là gì? NeuMF đã có từ 2017."**
NeuMF gốc chỉ học từ mã ID. Đề tài (1) đưa đặc trưng sản phẩm, khách hàng, thời gian vào **cả hai nhánh** theo cách
không dùng thông tin tương lai; (2) chứng minh mô hình này vượt các đối chứng được tinh chỉnh đầy đủ trên hai bộ dữ
liệu; (3) chỉ ra phần cải thiện đến từ đặc trưng, nhất là đặc trưng thời gian; (4) xây quy trình đánh giá tránh các lỗi
mà các nghiên cứu tái đánh giá đã chỉ ra. Mở: mục 2.7, 5.1 (Bảng 5.1), 5.2.

**5.1.2 "Ý nghĩa thực tiễn?"**
Mô hình chỉ dùng dữ liệu doanh nghiệp bán lẻ đã có (giao dịch, danh mục, hội viên, doanh số theo ngày). Kết quả gợi ý:
muốn gợi ý tốt hơn thì nên ưu tiên cập nhật doanh số theo thời gian và lịch sử mua, trước khi đầu tư kiến trúc phức tạp
hơn. Demo cho thấy hệ thống chạy được như một cửa hàng thật. Mở: mục 1.4.2, 5.2.

**5.1.3 "Vì sao chọn NeuMF mà không chọn mô hình mới hơn (Transformer, đồ thị)?"**
Ba lý do (mục 2.4.3): H&M chỉ ghi ngày mua, không có phiên, nên mô hình chuỗi khó dùng; dữ liệu có sẵn thuộc tính và
mô tả sản phẩm, hợp với cách "vector ID + đặc trưng"; cấu trúc hai nhánh tường minh cho phép tách đóng góp của từng phần
bằng so sánh trực tiếp. Các hướng mới là hướng phát triển (mục 5.4).

**5.1.4 "Hướng phát triển của đề tài là gì?"**
Nói theo thứ tự trong mục 5.4, mỗi hướng một câu "làm gì, làm bằng cách nào":
1. Làm giàu đặc trưng thời gian (nhóm mạnh nhất): thêm doanh số cùng kỳ năm trước, tốc độ tăng giảm doanh số, nhịp mua
   theo nhóm hàng; tính theo thời điểm như hiện tại.
2. Thêm ảnh và mô tả bằng mô hình tiền huấn luyện: biến ảnh, mô tả thành vector rồi nối vào đặc trưng sản phẩm — không
   phải sửa kiến trúc.
3. Sản phẩm mới, khách mới: NeuMF-F đã chấm được sản phẩm chỉ từ đặc trưng (m_i = 0); huấn luyện với xác suất bỏ ID > 0
   rồi đánh giá riêng. Khách mới: danh sách phổ biến theo nhóm tuổi, trạng thái hội viên.
4. Vận hành quy mô lớn: hai bước — hai tháp + tìm kiếm lân cận gần đúng để lọc vài trăm ứng viên, NeuMF-F xếp hạng lại;
   huấn luyện lại hằng tuần; đo bằng thử nghiệm A/B.
5. Học trọng số trộn theo nhóm khách (vì hợp nhất muộn tốt trên Amazon).
6. Mở rộng so sánh: Factorization Machines cùng đặc trưng, mô hình chuỗi, đồ thị — trên cùng quy trình đánh giá.
7. Giải thích gợi ý trong demo bằng mô hình ngôn ngữ lớn, dựa trên khách giống gu và sản phẩm tương tự đã có.

Ý chốt: khung NeuMF-F thêm được thông tin mới mà không đổi kiến trúc, và quy trình đánh giá dùng lại được nguyên.

### 5.2 Mô hình

**5.2.1 "Có thực sự là mô hình lai không?"**
Có. Lai ở hai mức: lai MF (nhánh GMF-F, tuyến tính) với DNN (nhánh MLP-F, phi tuyến) ở lớp dự đoán chung; và lai thông
tin cộng tác (vector ID) với thông tin nội dung, ngữ cảnh (đặc trưng). Hình 3.4 có kích thước từng ma trận: d = 32,
đặc trưng sản phẩm 157 chiều, khách 42 chiều, tháp 64 → 32 → 16 → 8, vector hợp nhất 40 chiều.

**5.2.2 "Vai trò của MF trong mô hình?"**
Ma trận khách × sản phẩm rất thưa (mật độ khoảng 0,45% sau lọc). MF nén thành hai bảng vector để suy ra điểm cho ô chưa
có dữ liệu. Trong NeuMF-F, nhánh GMF-F là MF trên vector có đặc trưng, nên còn học được tương tác giữa thuộc tính khách
và thuộc tính sản phẩm. GMF-F đứng riêng đã rất mạnh — nhánh MF có đặc trưng là phần cốt lõi.

**5.2.3 "Còn cold start?"**
- Khách mới: hệ thống trả danh sách sản phẩm phổ biến, luôn có gợi ý, demo minh họa được (mục 3.8, Thuật toán 3.7).
- Sản phẩm mới: nằm ngoài phạm vi đánh giá định lượng. Khảo sát ban đầu cho thấy ở quy mô mẫu này, khả năng gợi ý sản
  phẩm mới gần như không đo được (NDCG@10 trên nhóm này của mọi mô hình dưới 0,002), nên quy trình cuối chỉ đánh giá sản
  phẩm đã có lịch sử bán. Đây là hướng phát triển.

**5.2.4 "Lợi ích có phải do thêm thông tin chứ không phải do học sâu?"**
Đúng là lợi ích chính đến từ đặc trưng — đây chính là phát hiện của đề tài. So sánh NeuMF-F với NeuMF chỉ ID (cùng kiến
trúc) đo trực tiếp giá trị của đặc trưng. Để biết đặc trưng có cần học sâu không, cần thêm một đối chứng như Factorization
Machines dùng cùng đặc trưng; đã ghi ở hướng phát triển. Nhánh GMF-F có đặc trưng về bản chất gần với Factorization
Machines (mục 3.3.2).

**5.2.5 "Bỏ ID ngẫu nhiên có dùng không?"**
Là một siêu tham số được tinh chỉnh (ρ ∈ {0; 0,25; 0,5}). Tinh chỉnh chọn ρ = 0 cho NeuMF-F và MLP-F, ρ = 0,25 cho GMF-F.
Tức cấu hình cuối của NeuMF-F không dùng; đã ghi rõ trong báo cáo.

**5.2.6 "Chống quá khớp thế nào?"**
Dừng sớm theo NDCG@10 xác thực (sau 5 epoch không cải thiện), dropout ở tháp MLP, điều chuẩn L2. Khi huấn luyện lại chạy
đúng số epoch đã chọn. Mạng chọn trung bình 3–6 epoch (Bảng 4.10).

**5.2.7 "Lọc cộng tác hoạt động thế nào? Có phải lấy món người khác mua để gợi ý trực tiếp?"**
Không hẳn. Có hai cách:
- **Dựa trên láng giềng (UserKNN):** tính độ giống cosine giữa hai khách theo các món mua chung, giữ k khách giống nhất
  (k = 200, chọn trên tập xác thực); điểm của một món = tổng độ giống của các láng giềng đã mua món đó. ItemKNN làm tương
  tự theo sản phẩm. UserKNN là mô hình đối chứng mạnh nhất (0,03114 trên H&M).
- **Dựa trên mô hình (MF, NeuMF, NeuMF-F):** học một vector cho mỗi khách và mỗi sản phẩm từ toàn bộ lịch sử; khách mua
  giống nhau có vector gần nhau. NeuMF-F cộng thêm đặc trưng vào vector, nên có thêm thông tin ngoài lịch sử mua.

Mở: mục 2.1.2, 3.3.1. Demo có màn hình "khách giống gu" minh họa UserKNN.

**5.2.8 "Mẫu âm lấy thế nào?"**
Mỗi lượt mua lấy 4 hoặc 8 sản phẩm khách chưa mua, chỉ trong các sản phẩm **đã ra mắt** tại ngày mua (sản phẩm chưa bán
thì khách không thể mua). Lấy lại mỗi epoch. Khi đánh giá không lấy mẫu mà xếp hạng toàn bộ (mục 3.5.1).

### 5.3 Dữ liệu, đánh giá và thống kê

**5.3.1 "Có rò rỉ dữ liệu không?"**
Không. Các lớp bảo vệ: chia theo một mốc thời gian chung; mỗi cặp chỉ có một ngày mua đầu nên không thể vừa ở huấn luyện
vừa là món đúng; lọc k-core chỉ dùng dữ liệu trước mốc kiểm thử; đặc trưng tại ngày t chỉ dùng dữ liệu đến ngày t−1; mẫu
kiểm định là khách hàng khác hẳn; mọi mô hình đọc cùng một tệp dữ liệu. Mã nguồn có kiểm thử tự động cho các điều này.

**5.3.2 "Sao không chia leave-one-out như NCF?"**
Leave-one-out để lọt thông tin tương lai: dữ liệu huấn luyện chứa lượt mua của người khác xảy ra sau thời điểm cần dự
đoán. Đo trên mẫu phát triển: trung bình 11,2% tương tác huấn luyện xảy ra sau ngày của món kiểm thử; 60,9% khách có món
xác thực và món kiểm thử mua cùng ngày (mục 3.2.4).

**5.3.3 "Mỗi mô hình chỉ 6 cấu hình — có ít không, có thiệt cho đối chứng không?"**
Mọi mô hình, kể cả NeuMF-F, có **cùng** ngân sách 6 cấu hình, nên so sánh công bằng — đây là khuyến nghị của Rendle
(2020). Các mô hình chỉ có một tham số được thử đủ lưới. Nếu hỏi tiếp: vài cấu hình được chọn nằm ở biên lưới, nên mở
rộng lưới có thể cải thiện thêm cả đối chứng lẫn mô hình đề xuất.

**5.3.4 "Vì sao NDCG thấp (khoảng 0,04)?"**
Mỗi khách chỉ có khoảng 3 món đúng giữa khoảng 6,7 nghìn ứng viên; chỉ tính món **chưa từng mua**; dự đoán cho 8 tuần
tới; xếp hạng toàn bộ chứ không trên 100 ứng viên. Các bài NCF có HR@10 khoảng 0,7 vì chỉ xếp trên 101 ứng viên, nên
không so được. Điều cần xem là chênh lệch giữa các mô hình có ý nghĩa thống kê.

**5.3.5 "NDCG và các độ đo tính thế nào?"** (nên thuộc ví dụ tính tay)

| Độ đo | Cách tính cho một khách | Ý nghĩa |
|---|---|---|
| HR@K | 1 nếu có ít nhất một món đúng trong top-K, ngược lại 0 | Có trúng không |
| Precision@K | số món đúng trong top-K / K | Bao nhiêu phần gợi ý là đúng |
| Recall@K | số món đúng trong top-K / tổng số món đúng | Tìm lại được bao nhiêu phần |
| NDCG@K | DCG@K / IDCG@K, với DCG@K = tổng 1/log₂(r + 1) trên các món đúng có hạng r ≤ K | Món đúng càng ở trên càng nhiều điểm |

Ví dụ: một khách có 3 món đúng ở hạng 2, 7 và 40; K = 10.
- HR@10 = 1; Precision@10 = 2/10 = 0,2; Recall@10 = 2/3 ≈ 0,667.
- DCG = 1/log₂3 + 1/log₂8 = 0,631 + 0,333 = 0,964; IDCG = 1 + 0,631 + 0,5 = 2,131.
- NDCG@10 = 0,964 / 2,131 ≈ 0,453.

Độ đo lấy trung bình theo khách, rồi trung bình ± độ lệch chuẩn qua 5 seed. Luận án của cô dùng MAE/RMSE cho dự đoán điểm
đánh giá; H&M không có điểm đánh giá nên không dùng. HR@K chính là hit rate; NDCG cùng tinh thần ARHR (thưởng món đúng nằm
cao). Mở: mục 2.5.

**5.3.6 "K = 15 có chạy lại không?"**
Không. Đánh giá cuối lưu hạng của từng món đúng cho từng khách, từng mô hình, từng seed. Từ hạng đó tính được độ đo ở K bất
kỳ; tính lại @5, @10, @20 cho đúng y các số đã báo cáo.

**5.3.7 "Lọc k-core trên mọi cặp trước mốc kiểm thử có ảnh hưởng tập xác thực không?"**
Có, một phần: tập khách và sản phẩm ở giai đoạn xác thực phụ thuộc vào dữ liệu tháng 7/2020. Việc này chỉ ảnh hưởng
bước chọn cấu hình; tập kiểm thử của mẫu kiểm định hoàn toàn không bị ảnh hưởng.

**5.3.8 "Vì sao 5 seed? Kiểm định theo seed hay theo khách?"**
Theo khách (hàng nghìn khách). Mỗi khách lấy NDCG@10 trung bình qua 5 seed rồi so hai mô hình bằng Wilcoxon. Nếu kiểm định
theo seed thì với 5 seed, p nhỏ nhất chỉ 0,0625, không bao giờ dưới 0,05. Dao động giữa seed được báo cáo bằng độ lệch
chuẩn.

**5.3.9 "Vì sao thêm ngưỡng 5%?"**
Để loại khác biệt có ý nghĩa thống kê nhưng quá nhỏ về thực tiễn. Bỏ ngưỡng này thì không kết luận nào thay đổi.

**5.3.10 "Vì sao lấy mẫu 1,5% khách, k = 10?"**
Xếp hạng toàn bộ trên dữ liệu đầy đủ (633 nghìn khách × 80 nghìn sản phẩm với k = 10) là hàng chục tỷ cặp cho mỗi mô
hình. Với k = 5 trên mẫu phát triển, ước tính cần khoảng 10,7 GB bộ nhớ. Lấy mẫu theo khách bằng hàm băm giữ trọn lịch sử
và cho hai mẫu tương đương nhau (Bảng 3.3). Mở rộng quy mô là hướng phát triển.

### 5.4 Kết quả

**5.4.1 "LateFusion-F cao nhất, sao không chọn nó làm mô hình đề xuất?"** (câu quan trọng nhất)
- Mô hình đề xuất được cố định **trước** khi có kết quả kiểm thử. Đổi sau khi xem kết quả là chọn mô hình trên tập kiểm
  thử — đúng lỗi phương pháp mà đề tài tránh.
- LateFusion-F **dùng chính hai nhánh có đặc trưng của NeuMF-F**, chỉ khác bước trộn điểm. Vì vậy thành công của
  LateFusion-F cũng là bằng chứng cho phát hiện chính: biểu diễn có đặc trưng là yếu tố quyết định.
- Trên H&M hai cách tương đương (chênh 2,2%, p Holm 0,735). Trên Amazon hợp nhất muộn tốt hơn. Khi triển khai có thể chọn
  theo dữ liệu: NeuMF-F chỉ huấn luyện một mạng; LateFusion-F tốn gần gấp đôi nhưng ổn định hơn.

**5.4.2 "Vì sao ghép hai nhánh không hơn nhánh GMF-F đứng riêng?"**
GMF-F đứng riêng đã ngang NeuMF-F ở cả hai bộ (+2,6% H&M, −0,6% Amazon). Phần lớn lợi ích nằm ở đặc trưng đưa vào nhánh
MF, chứ không ở việc thêm nhánh phi tuyến. Đây là kết quả có giá trị: nó cho thấy nên đầu tư vào dữ liệu đặc trưng hơn là
vào độ sâu của mạng.

**5.4.3 "NeuMF chỉ ID không hơn BPR-MF — mô hình lai có vô dụng không?"**
Không vô dụng. Kết quả này khớp với các nghiên cứu tái đánh giá (Rendle 2020): khi chỉ có mã ID, NeuMF khó vượt MF được
tinh chỉnh kỹ. Chính phát hiện đó dẫn tới NeuMF-F, và khi có đặc trưng thì NeuMF-F vượt BPR-MF +50,4%.

**5.4.4 "Thứ hạng có ổn định giữa tinh chỉnh và kiểm thử không?"**
Ổn định ở nhóm đầu: bốn mô hình có đặc trưng đứng đầu cả hai lần; LateFusion-F và NeuMF-F giữ hai vị trí đầu. GMF, MLP
chỉ ID tụt từ hạng 5 và 7 xuống 9 và 11; ItemKNN lên từ hạng 10 lên 6 (Hình 4.5).

**5.4.5 "Đặc trưng văn bản có giúp không?"**
Trên H&M chưa khẳng định được (bỏ văn bản −2,7%, khoảng tin cậy chứa 0). Đặc trưng thời gian và thông tin khách quan
trọng hơn nhiều. Biểu diễn văn bản bằng mô hình ngôn ngữ là hướng phát triển.

### 5.5 Amazon Beauty và Hybrid-CBCF

**5.5.1 "Amazon dùng lại siêu tham số H&M — có công bằng không?"**
Là quyết định ghi trong kế hoạch **trước khi chạy** trên Amazon: mục đích là kiểm tra kết luận có còn đúng khi đổi dữ liệu
mà **không** chỉnh theo dữ liệu mới. Chỉ số epoch được chọn trên tập xác thực Amazon. Kết luận về đặc trưng vẫn giữ —
đó là bằng chứng mạnh nhất về tính tổng quát. Riêng BPR-MF có cấu hình không hợp Amazon (kém cả ItemKNN), nên hai so sánh
có BPR-MF trên Amazon không dùng làm bằng chứng (Bảng 4.18, dấu *).

**5.5.2 "Hybrid-CBCF thêm sau, có thiên lệch không?"**
Thêm theo góp ý của giảng viên hướng dẫn, làm như **phân tích bổ sung** có kế hoạch riêng: cách kết hợp chọn trên tập xác
thực, tập kiểm thử chấm một lần, hai so sánh bổ sung có hiệu chỉnh Holm riêng, kết luận cũ giữ nguyên. Nếu hỏi tiếp: lúc
thêm, nhóm đã biết kết quả kiểm thử của ba thành phần; vì vậy nó không được tính vào họ 10 so sánh.

**5.5.3 "Vì sao học trọng số Hybrid-CBCF theo cặp?"**
Luận án của cô học trọng số trên điểm đánh giá; dữ liệu đề tài chỉ có mua / không mua. Hồi quy logistic thường trên từng
cặp (khách, sản phẩm) cho trọng số âm và mô hình hỏng (NDCG@10 khoảng 0,0005), vì khác biệt giữa các khách lấn át thứ tự
trong danh sách của từng khách. Học theo cặp (món đúng so với món không đúng của **cùng một khách**) đúng mục tiêu xếp
hạng, cùng tiêu chí với BPR.

### 5.6 Quá trình làm (chỉ nói khi được hỏi)

**5.6.1 "Có thay đổi kế hoạch giữa chừng không?"**
Có, và đã ghi lại đầy đủ. Bản kế hoạch đầu coi mỗi màu là một sản phẩm, có sản phẩm mới trong tập ứng viên, và kiểm định
trên một mẫu khách khác (khối 1, mở ngày 04/10/2026). Theo góp ý của cô, bản cuối gộp theo mẫu thiết kế và bỏ sản phẩm
chưa có người mua. Vì bản cuối được quyết định sau khi xem khối 1, khối 1 bị loại và kết luận lấy trên một mẫu mới
hoàn toàn (khối 2), chưa ai xem. Độ đo chính, họ 10 so sánh và tiêu chí kết luận giữ nguyên từ bản đầu.

**5.6.2 "Chạy trên máy nào, mất bao lâu, có sự cố không?"**
Đánh giá cuối H&M chạy ngày 10/10/2026 trên GPU RTX 3050, khoảng 7,5 giờ cho 5 seed; Amazon 10–11/10/2026. Lần chạy đầu
dừng giữa chừng ở seed 42 trước khi lưu kết quả nào, nên seed 42 được chạy lại với cùng mã nguồn, cấu hình và dữ liệu;
việc này ghi trong nhật ký. Không quyết định nào thay đổi vì cấu hình đã cố định. Demo chạy được trên máy chỉ có CPU.

**5.6.3 "Khác gì so với đề cương?"**

| Đề cương | Thực tế | Lý do |
|---|---|---|
| Chia leave-one-out | Chia theo thời gian | Leave-one-out lọt thông tin tương lai |
| Sản phẩm theo `article_id` | Theo mẫu thiết kế (`product_code`) | Theo góp ý của cô |
| Baseline ALS | BPR-MF | Cùng nhóm MF cho phản hồi ẩn |
| K = 5/10/20 | Thêm K = 15 | Theo góp ý họp 04/10 |
| Một bộ dữ liệu | Thêm Amazon Beauty | Theo góp ý họp 04/10 |
| Demo FastAPI + Streamlit | FastAPI + giao diện HTML | Chức năng tương đương |

---

## Phần 6. Câu không được nói

- **Không nói "NeuMF-F tốt nhất".** Nói: "NeuMF-F vượt có ý nghĩa các mô hình đối chứng; nhóm mô hình có đặc trưng dẫn đầu."
- **Không nói "NeuMF-F không thua mô hình nào"** mà không nói rõ là trên H&M (trên Amazon LateFusion-F tốt hơn).
- **Không nói đề tài giải quyết cold start của sản phẩm.** Khách mới: có xử lý (gợi ý phổ biến), nhưng không đánh giá
  định lượng.
- **Không nói NeuMF-F "học được sản phẩm mới nhờ bỏ ID ngẫu nhiên"** (cấu hình cuối có ρ = 0).
- **Không so số của đề tài với số trong bài báo** (khác dữ liệu, cách chia, số ứng viên). Bảng 2.1 chỉ để thấy thiết lập
  khác nhau.
- **Không gọi MLP đứng riêng là hợp nhất sớm** (đó là mạng DNN thuần).
- **Không dùng hai so sánh có BPR-MF trên Amazon làm bằng chứng.**
- **Không tính Hybrid-CBCF vào "14 mô hình" hay họ 10 so sánh.**
- Dùng đúng thuật ngữ: tập huấn luyện / xác thực / kiểm thử; tinh chỉnh; lấy mẫu âm; mẫu phát triển / mẫu kiểm định;
  mô hình đề xuất.
- Nói theo đúng tên đề tài: **hệ thống khuyến nghị, mô hình khuyến nghị lai, danh sách khuyến nghị**; **mạng lưới thần kinh
  sâu** (DNN). Báo cáo đã đổi toàn bộ theo cách gọi này; chỉ giao diện demo còn chữ "Gợi ý phổ biến" — nếu hỏi thì
  "gợi ý" và "khuyến nghị" cùng nghĩa (recommendation).

---

## Phần 7. Kịch bản demo trước hội đồng

1. Chạy trước buổi bảo vệ: `cd neumf_project` rồi `python run.py demo`, mở `http://localhost:8000`. Lần nạp đầu khoảng
   15 giây (H&M), 5 giây (Amazon) — mở sẵn trước khi lên trình bày.
2. **Màn hình giới thiệu:** nói bài toán, dữ liệu, mô hình trong 30 giây.
3. **Cửa hàng mô phỏng:** bấm "khách ví dụ". Chỉ lịch sử mua (dữ liệu mô hình đã học) và 10 khuyến nghị.
4. **Mô hình đối chứng** để mặc định là NeuMF chỉ ID (NeuMF-F luôn ở cột trái), bấm "Xem khách đã mua gì": NeuMF-F đưa món khách thật sự mua lên vị trí 3 và
   6, NeuMF chỉ ID xếp món gần đầu nhất ở vị trí 164.
5. Bấm một sản phẩm → thẻ chi tiết và sản phẩm tương tự (ItemKNN). Kéo xuống → khách giống gu (UserKNN).
6. Nhập một mã khách không có trong dữ liệu → "Khuyến nghị phổ biến" (xử lý khách mới, không báo lỗi).
7. **Màn hình kết quả:** NeuMF-F cạnh từng mô hình đối chứng (NDCG@10, chênh lệch, kết luận kiểm định); chỉ ra NeuMF-F
   tốt hơn NeuMF chỉ ID có ý nghĩa, ngang LateFusion-F và GMF-F.
8. Chuyển sang Amazon Beauty trên thanh đầu trang để cho thấy hệ thống chạy trên bộ dữ liệu thứ hai.

Lưu ý: nếu máy chưa có thư mục ảnh H&M (`neumf_project/demo/static/images`, hoặc biến `DEMO_IMAGES_DIR`), demo hiện ô
màu ghi loại sản phẩm thay ảnh — vẫn chạy bình thường. Nên chép ảnh vào trước buổi bảo vệ. Số hạng và độ đo của từng
khách trong demo là của seed 42, có thể khác đôi chút so với trung bình 5 seed trong báo cáo.

---

## Phần 8. Tra nhanh báo cáo

| Chương | Mục chính | Bảng, hình, thuật toán |
|---|---|---|
| 1. Tổng quan | 1.1 bối cảnh (1.1.3 ba câu hỏi nghiên cứu); 1.2 mục tiêu, phạm vi; 1.3 phương pháp; 1.4 ý nghĩa | — |
| 2. Cơ sở lý thuyết | 2.1 hệ gợi ý; 2.2 MF, BPR; 2.3 NCF, hợp nhất; 2.4 hướng gần đây; 2.5 độ đo; 2.6 ba nghiên cứu nền tảng; 2.7 khoảng trống | Hình 2.1 NeuMF, Hình 2.2 hợp nhất; Bảng 2.1 |
| 3. Phương pháp | 3.1 đường ống; 3.2 dữ liệu; 3.3 NeuMF-F; 3.4 đối chứng; 3.5 lấy mẫu âm, BCE; 3.6 tinh chỉnh; 3.7 đánh giá (3.7.1 khảo sát ban đầu, 3.7.2 sáu nguyên tắc); 3.8 suy luận, khách mới; 3.9 demo | Hình 3.1 đường ống, 3.2 NeuMF-F, 3.3 quy trình đánh giá, 3.4–3.10 demo; Bảng 3.1–3.7; Thuật toán 3.1–3.7 |
| 4. Thực nghiệm | 4.1 cấu hình; 4.2 tinh chỉnh; 4.3 kết quả H&M (4.3.1 chính, 4.3.2 theo K, 4.3.3 kiểm định, 4.3.4 Hybrid-CBCF, 4.3.5 bóc tách, 4.3.6 độ phủ, 4.3.7 hội tụ); 4.4 Amazon; 4.5 phạm vi; 4.6 trả lời ba câu hỏi nghiên cứu; 4.7 tóm tắt chương | Bảng 4.2–4.10 (H&M), 4.10–4.18 (Amazon); Hình 4.1–4.6 |
| 5. Kết luận | 5.1 kết quả đạt được; 5.2 kết luận; 5.3 hạn chế; 5.4 hướng phát triển | Bảng 5.1 mức độ hoàn thành mục tiêu |

Thuật toán: 3.1 chuẩn bị dữ liệu và k-core · 3.2 lấy mẫu âm · 3.3 huấn luyện, huấn luyện lại · 3.4 xếp hạng toàn bộ ·
3.5 trọng số LateFusion-F · 3.6 cách kết hợp Hybrid-CBCF · 3.7 suy luận Top-K có xử lý khách mới.

Bằng chứng trong mã nguồn (chỉ mở khi hội đồng yêu cầu): kế hoạch đăng ký trước `neumf_project/audit/PREREG_v2.md`,
`PREREG_amazon.md`, `PREREG_bosung.md`; nhật ký mở tập kiểm thử `neumf_project/audit/test_access_log.csv`; kết quả
`neumf_project/outputs/`; mô hình `neumf_project/src/models/hybrid_features.py`.
