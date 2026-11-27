# Chuẩn bị bảo vệ trước hội đồng — Mô hình gợi ý lai NeuMF-F

Tài liệu này để cả nhóm nắm toàn bộ đề tài và trả lời thống nhất trước hội đồng. Số mục, số bảng, số hình ghi theo
bản báo cáo viết gọn ngày 24/11/2026 (số mục, bảng, hình giữ nguyên như bản 18/11; phần demo có Bảng 3.7 số đo, Hình 3.8–3.9, hình kết quả demo là Hình 3.10, bảng điểm cuối API được thay bằng đoạn văn). Mọi số
liệu ở đây khớp với báo cáo và tệp kết quả cuối `neumf_project/outputs/*/final/` (kiểm bằng `python run.py
check-report` và đối chiếu từng số ngày 26/11/2026). Bản 26/11 viết lại Câu 1 về LateFusion-F (câu trọng tâm) và thêm
Phần 0.2, 0.3, 5.7, 5.8, 9. Bản 27/11 thêm mục (g) ở Câu 1 (điểm yếu của LateFusion-F, có đếm bộ nhớ và đo thời gian
trả kết quả), câu (m)–(o) ở 0.3, câu 5.8.10 về kết quả kiểm tra trùng lặp, bảng vị trí công
thức ở Phần 8 và Phần 10 (lời nói mẫu theo từng slide, có canh giờ).

Báo cáo nộp cuối (27/11) khác bản đã kiểm Turnitin (25/11) ở mấy điểm sau. Số chương, mục, bảng, hình và thuật toán vẫn
giữ nguyên:
- Lời cảm ơn được viết lại. Trang cảm ơn và trang cam đoan có khối ký tên hai cột.
- Công thức không còn đánh số, khi dẫn thì dẫn theo mục (Phần 8).
- Bỏ công thức MF lặp ở mục 1.1.2 và công thức BCE lặp ở mục 3.5.2, nay chỉ ghi $\mathcal{L} = \mathcal{L}_{BCE} + \lambda\|\Theta\|^2$.
- Các mục liệt kê mở đầu bằng nhãn dùng dấu hai chấm ("Độ thưa dữ liệu: mỗi khách…").

| Cần gì | Đọc phần |
|---|---|
| **Câu trọng tâm: vì sao chọn NeuMF-F mà không chọn LateFusion-F** | **Phần 0, Câu 1** |
| **10 câu dễ bị hỏi nhất — học trước** | **Phần 0** |
| Câu hỏi bám theo từng slide (hội đồng hỏi vào thứ đang chiếu) | Phần 0.2 |
| Câu hỏi xoáy mới, đã kiểm bằng số liệu và mã nguồn | Phần 0.3 |
| Kiến thức nền hay bị hỏi riêng từng bạn | Phần 5.7 |
| Phân công, mã nguồn, khó khăn, dùng AI, nguồn dữ liệu | Phần 5.8 |
| Mở đầu phần trình bày (3 phút) | Phần 1 |
| Hiểu toàn bộ đề tài theo từng chương | Phần 2 |
| Số liệu phải thuộc | Phần 3 |
| Cái gì nói trong báo cáo, cái gì chỉ nói khi được hỏi | Phần 4 |
| Câu hỏi hội đồng hay hỏi và cách trả lời | Phần 5 |
| Câu không được nói | Phần 6 |
| Kịch bản chạy demo | Phần 7 |
| Tra nhanh chương, mục, bảng, hình | Phần 8 |
| Buổi hỏi đáp mô phỏng, lời nói mẫu để luyện nói | Phần 9 |
| **Thuyết trình theo từng slide: lời nói mẫu, canh giờ, câu chuyển người** | **Phần 10** |
| Kết quả kiểm tra trùng lặp (Turnitin) và cách giải thích | câu 5.8.10 |
| Công thức nằm ở mục nào (báo cáo không đánh số công thức) | Phần 8 |

---

## Phần 0. 10 câu dễ bị hỏi nhất (sàng lọc 18/11/2026)

Chọn từ Phần 5 theo hai tiêu chí: hội đồng dễ hỏi (đụng tên đề tài, kết quả chính, độ tin cậy) và trả lời sai thì mất
điểm nặng. Mỗi câu có ý trả lời trong khoảng 30 giây, câu hỏi nối tiếp hay gặp và chỗ mở trong báo cáo. Học thuộc phần
"Trả lời ngắn"; phần chi tiết đọc ở câu tương ứng của Phần 5.

| # | Câu hỏi | Vì sao dễ bị hỏi | Chi tiết |
|---|---|---|---|
| 1 | LateFusion-F cao nhất, sao mô hình đề xuất lại là NeuMF-F? | Kết quả bất lợi nằm ngay trong bảng | **Câu 1 ngay dưới (trọng tâm)** |
| 2 | Đóng góp mới là gì, NeuMF có từ 2017? | Câu mở đầu quen thuộc | 5.1.1 |
| 3 | Có thật là mô hình lai không, MF đóng vai trò gì? | Tên đề tài | 5.2.1, 5.2.2 |
| 4 | Cải thiện do đặc trưng hay do học sâu? Sao ghép hai nhánh không hơn GMF-F? | GMF-F ngang NeuMF-F | 5.2.4, 5.4.2, 5.4.6 |
| 5 | Có rò rỉ dữ liệu không, sao không chia leave-one-out? | Lỗi phổ biến của đề tài gợi ý | 5.3.1, 5.3.2 |
| 6 | NDCG chỉ khoảng 0,04 có thấp không, tính thế nào? | Số nhìn nhỏ; hay bị bắt tính tay | 5.3.4, 5.3.5 |
| 7 | So sánh có công bằng không (6 cấu hình, Amazon dùng siêu tham số H&M)? | Nghi ngờ thiên vị mô hình đề xuất | 5.3.3, 5.5.1 |
| 8 | Cold start xử lý thế nào? | Điểm yếu kinh điển của lọc cộng tác | 5.2.3 |
| 9 | Sao chọn NeuMF mà không chọn Transformer, mạng đồ thị? | Hội đồng quan tâm mô hình mới | 5.1.3 |
| 10 | Ý nghĩa thực tiễn, triển khai trên dữ liệu thật được không (mới lấy mẫu khoảng 1,6% khách)? | Câu kết thường gặp | 5.1.2, 5.3.10, 5.1.4 |

Với đề tài làm nhóm, gần như chắc chắn có thêm câu "Mỗi em làm phần nào?" (5.8.1), và có thể có câu "Nhóm có dùng AI
không?" (5.8.6). Hai câu này không cần số liệu, nhưng trả lời lúng túng thì mất điểm không kém câu kỹ thuật.

**Câu 1. LateFusion-F cao nhất, sao mô hình đề xuất lại là NeuMF-F?** (câu trọng tâm — học kỹ nhất)

Số liệu của câu này đối chiếu ngày 26/11/2026 với tệp kết quả cuối: `outputs/v2/final/` (H&M, mẫu kiểm định, chạy
10/10/2026) và `outputs/amazon/final/` (10–11/10/2026); trùng với báo cáo. Không dùng số của các lần chạy cũ.

*(a) Trả lời 30 giây — học thuộc*

> Dạ, đề tài đặt mục tiêu xây dựng một mô hình lai, trong đó MF và DNN được ghép và học chung trong một mạng. NeuMF-F
> là mô hình đó, và được xác định là mô hình đề xuất ngay từ kế hoạch, trước khi có kết quả. LateFusion-F gồm hai mô
> hình huấn luyện riêng rồi trộn điểm; nhóm đưa vào để trả lời câu hỏi nên hợp nhất sớm hay muộn. Kết quả: trên H&M hai
> cách không khác biệt có ý nghĩa; trên Amazon NeuMF-F thấp hơn 12,5%. Đổi lại, NeuMF-F chỉ có một mạng, thời gian huấn
> luyện bằng khoảng một nửa hoặc ít hơn, và danh sách khuyến nghị đa dạng hơn. LateFusion-F được ghép từ chính hai nhánh
> có đặc trưng của NeuMF-F, nên nó mạnh cũng là nhờ đặc trưng mà đề tài xây dựng.

*(b) Trả lời đầy đủ — khoảng 2 phút, nói theo bốn ý*

1. **Vì sao NeuMF-F là mô hình đề xuất.** Tên đề tài là xây dựng mô hình khuyến nghị lai kết hợp MF và DNN. Báo cáo
   mục 1.1.3 nêu rõ: nhóm chọn hợp nhất sớm để MF và DNN được kết hợp trong một mô hình duy nhất và học chung; hợp nhất
   muộn của cùng hai nhánh được đưa vào làm đối chứng LateFusion-F để đo ảnh hưởng của cách hợp nhất. Đề tài không đặt
   mục tiêu tìm mô hình có điểm cao nhất, mà xây dựng và đánh giá trung thực mô hình lai này.
2. **Kết quả, nói thẳng.** Trên H&M: NDCG@10 0,04003 so với 0,04093, chênh −2,2%, khoảng tin cậy [−0,00252; +0,00072]
   chứa 0, p Holm 0,735 → không khác biệt có ý nghĩa. Trên Amazon: 0,03277 so với 0,03747, chênh −12,5%, khoảng tin cậy
   [−0,00668; −0,00279], p Holm < 0,001 → LateFusion-F tốt hơn. Báo cáo ghi rõ LateFusion-F có NDCG@10 trung bình cao
   nhất trên cả hai bộ (mục 4.7, 5.2).
3. **Đánh đổi đo được** (bảng ở (c)). NeuMF-F chỉ huấn luyện một mạng: 15,2 so với 30,1 phút mỗi seed trên H&M, 4,1 so
   với 10,9 phút trên Amazon. Độ phủ top-10 cao hơn trên cả hai bộ: 13,3% so với 5,3% (H&M), 20,5% so với 15,3%
   (Amazon). Ngược lại, LateFusion-F có NDCG@10 cao hơn và chỉnh được trọng số trộn mà không phải huấn luyện lại.
4. **Vì sao kết quả này củng cố chứ không làm yếu đóng góp.** LateFusion-F chỉ khác NeuMF-F ở bước trộn điểm; hai thành
   phần của nó là GMF-F và MLP-F, tức chính hai nhánh có đặc trưng của đề tài. Bốn vị trí đầu trên cả hai bộ đều là mô
   hình có đặc trưng. Dù hợp nhất sớm hay muộn, kết luận chính vẫn đứng: đặc trưng là nguồn cải thiện. Câu hỏi nghiên
   cứu thứ ba được đặt ra đúng để so hai cách hợp nhất, và câu trả lời là chọn theo dữ liệu.

*(c) Bảng số liệu (thuộc các số in đậm)*

| Chỉ số | H&M: NeuMF-F | H&M: LateFusion-F | Amazon: NeuMF-F | Amazon: LateFusion-F |
|---|---|---|---|---|
| NDCG@10 (trung bình ± độ lệch chuẩn 5 seed) | **0,04003** ± 0,00147 | **0,04093** ± 0,00212 | **0,03277** ± 0,00189 | **0,03747** ± 0,00180 |
| HR@10 | 0,15046 | 0,15798 | 0,09750 | 0,10802 |
| Recall@10 | 0,05953 | 0,06125 | 0,05568 | 0,06286 |
| Precision@10 | 0,01723 | 0,01833 | 0,01092 | 0,01222 |
| Thời gian huấn luyện mỗi seed | **15,2 phút** | **30,1 phút** (GMF-F 13,7; MLP-F 16,4) | **4,1 phút** | **10,9 phút** (GMF-F 6,1; MLP-F 4,9) |
| Số epoch được chọn (trung bình 5 seed) | 3,0 | GMF-F 4,4; MLP-F 4,6 | 5,4 | GMF-F 14,0; MLP-F 8,0 |
| Độ phủ top-10 (seed 42) | **13,3%** | **5,3%** | **20,5%** | **15,3%** |
| Số mạng phải huấn luyện, lưu và chạy | 1 | 2 | 1 | 2 |

Kiểm định (so sánh số 4 trong họ 10 so sánh, NeuMF-F so với LateFusion-F):
- H&M: chênh **−2,2%**, khoảng tin cậy [−0,00252; +0,00072], **p Holm 0,735** → không khác biệt có ý nghĩa.
- Amazon: chênh **−12,5%**, khoảng tin cậy [−0,00668; −0,00279], **p Holm < 0,001** → LateFusion-F tốt hơn.

Lúc tinh chỉnh (tập xác thực của mẫu phát triển H&M): LateFusion-F 0,03556, NeuMF-F 0,03337. Trọng số chọn: w = 0,4 cho
GMF-F, 0,6 cho MLP-F, giữ nguyên ở đánh giá cuối và trên Amazon.

Nguồn: Bảng 4.2, 4.4, 4.7, 4.10, 4.13, 4.17 và mục 4.7 của báo cáo. Riêng số epoch, thời gian và độ phủ của GMF-F,
MLP-F trên Amazon không có bảng trong báo cáo, lấy từ `outputs/amazon/final/beyond.csv`.

*(d) Mốc thời gian — chỉ đưa ra khi hội đồng nghi "chọn mô hình sau khi xem kết quả"*
- 03/10/2026: kế hoạch thực nghiệm đã ghi NeuMF-F là mô hình đề tài và LateFusion-F là so sánh số 4, khi chưa có kết
  quả tinh chỉnh của bất kỳ mô hình có đặc trưng nào (`audit/PREREG_v2_cu.md`, đã commit).
- 09–10/10/2026: tinh chỉnh xong trên tập xác thực của mẫu phát triển; bản kế hoạch cuối ngày 10/10 giữ nguyên mô hình
  đề xuất và họ so sánh (`audit/PREREG_v2.md`).
- 10/10/2026: mở tập kiểm thử H&M một lần, sau khi commit kế hoạch; Amazon mở 10–11/10 (`audit/test_access_log.csv`).

Không tự kể chi tiết các bản kế hoạch; nếu bị hỏi vì sao có hai bản thì xem câu 5.6.1.

*(e) Hỏi vặn hay gặp*

1. *"Lúc tinh chỉnh LateFusion-F đã cao hơn (0,03556 so với 0,03337). Sao không đổi mô hình đề xuất trước khi đánh giá
   cuối?"* → Dạ, tập xác thực dùng để chọn cấu hình bên trong từng mô hình, không dùng để đổi đối tượng nghiên cứu. Đối
   tượng của đề tài là một mô hình lai học chung, xác định từ đầu theo tên đề tài; LateFusion-F là một cách hợp nhất khác
   được đem ra so sánh. Nếu thấy số cao hơn là đổi, câu hỏi nghiên cứu sẽ bị đặt lại theo kết quả. Nhóm giữ mô hình đề
   xuất và báo cáo đầy đủ kết quả của LateFusion-F.
2. *"Nếu triển khai thật thì em chọn mô hình nào?"* → Dạ, chọn theo dữ liệu và chi phí, thử cả hai trên tập xác thực của
   dữ liệu mới. Cần mô hình gọn, huấn luyện lại thường xuyên, danh sách đa dạng thì chọn NeuMF-F; ưu tiên độ chính xác và
   chấp nhận huấn luyện, lưu trữ hai mạng thì chọn LateFusion-F. Với dữ liệu như H&M, hai mô hình tương đương về NDCG@10
   nên NeuMF-F có lợi về chi phí; với dữ liệu như Amazon nên cân nhắc LateFusion-F.
3. *"Ghép hai mô hình thì thường thắng. LateFusion-F hơn có phải vì nhiều tham số hơn? So sánh có công bằng không?"* →
   Dạ, không phải vì lớn hơn. GMF-F và MLP-F trong LateFusion-F đều dùng d = 32, như hai nhánh của NeuMF-F, vốn mỗi nhánh
   cũng có bảng vector nhúng riêng, nên số tham số gần như bằng nhau. Khác biệt nằm ở cách học: LateFusion-F huấn luyện
   hai mạng riêng rồi trộn điểm theo trọng số cố định, còn NeuMF-F học chung hai nhánh và một lớp dự đoán. Cái giá của
   LateFusion-F là thời gian huấn luyện gấp đôi trên H&M, gần gấp ba trên Amazon. Phép so sánh dùng cùng hai thành phần
   và cùng đặc trưng, nên đo đúng ảnh hưởng của cách hợp nhất.
4. *"Sao trên Amazon hợp nhất muộn tốt hơn hẳn, còn H&M thì không?"* → Dạ, báo cáo đưa ra một cách giải thích: trên
   Amazon, hai nhánh khuyến nghị những tập sản phẩm rất khác nhau, độ phủ top-10 của GMF-F là 32,1% còn MLP-F chỉ 5,4%;
   huấn luyện riêng rồi trộn điểm thì hai danh sách bổ sung cho nhau. Trên H&M, độ phủ của hai nhánh gần nhau (6,9% và
   5,3%), và hai cách hợp nhất cũng không khác biệt có ý nghĩa. Đây là cách giải thích, nhóm chưa làm thí nghiệm riêng để
   chứng minh.
5. *"Học chung lẽ ra tốt hơn trộn điểm cố định. Sao NeuMF-F lại thua trên Amazon?"* (chỉ nói khi bị hỏi sâu, và nói rõ
   là giả thuyết) → Dạ, nhóm có hai giả thuyết, chưa kiểm chứng. Một, trong NeuMF-F hai nhánh dừng sớm cùng lúc theo mô
   hình chung (trung bình 5,4 epoch trên Amazon), còn trong LateFusion-F mỗi nhánh tự dừng ở số epoch tốt nhất của nó
   (GMF-F 14,0, MLP-F 8,0). Hai, trộn hai mô hình huấn luyện độc lập giống lấy trung bình hai dự đoán, làm giảm sai số
   ngẫu nhiên, nhất là khi hai danh sách khác nhau nhiều. Bài NCF gốc có cách tiền huấn luyện từng nhánh rồi mới ghép;
   giao thức của đề tài huấn luyện mọi mạng từ đầu để cùng một quy trình. Thử tiền huấn luyện là một hướng tiếp theo.
6. *"Trên H&M LateFusion-F cao hơn ở cả bốn độ đo, sao em nói là tương đương?"* → Dạ, NDCG@10 là độ đo chính chọn từ
   đầu và chỉ nó được kiểm định. Ở NDCG@10, chênh 2,2%, khoảng tin cậy chứa 0, p Holm 0,735, nên nhóm kết luận không khác
   biệt có ý nghĩa, chứ không nói NeuMF-F bằng hay hơn. HR, Recall, Precision chỉ để mô tả; chênh cùng chiều và không
   được kiểm định. Thêm nữa, trên H&M LateFusion-F dao động giữa các seed nhiều hơn (độ lệch chuẩn 0,00212 so với
   0,00147).
7. *"Mô hình đề xuất không đứng đầu, vậy đề tài có thất bại không?"* → Dạ không. NeuMF-F đạt mục tiêu chính: tốt hơn có
   ý nghĩa NeuMF chỉ dùng ID (+43,8% trên H&M, +65,7% trên Amazon) và mọi mô hình truyền thống được so sánh, kể cả
   Hybrid-CBCF. Câu hỏi thứ ba hỏi nên hợp nhất sớm hay muộn, và nhóm trả lời bằng số liệu: tuỳ dữ liệu. Một kết quả
   trung thực có ích hơn một mô hình được chọn để đứng đầu.
8. *"Trọng số w = 0,4 chọn thế nào? Sang Amazon có chọn lại không?"* → Dạ, w được thử trên lưới 0; 0,1; …; 1 với GMF-F
   và MLP-F tốt nhất lúc tinh chỉnh, chọn theo NDCG@10 trên tập xác thực của mẫu phát triển H&M: 0,4 cho GMF-F, 0,6 cho
   MLP-F. Trọng số giữ nguyên ở đánh giá cuối và trên Amazon. Trước khi trộn, điểm của mỗi mô hình được chuẩn hoá min–max
   trên tập ứng viên của từng khách để hai thang điểm so được với nhau.
9. *"Có cách nào lấy ưu điểm của cả hai không?"* → Dạ, có hai hướng, chưa nằm trong báo cáo: tiền huấn luyện riêng hai
   nhánh rồi ghép vào NeuMF-F và huấn luyện tiếp; hoặc học trọng số trộn theo nhóm khách thay vì một trọng số chung. Cả
   hai đánh giá lại được bằng đúng quy trình hiện có.
10. *"Hội đồng góp ý nên lấy LateFusion-F làm mô hình chính thì sao?"* → Dạ, nhóm xin ghi nhận. Kết quả của LateFusion-F
    đã có đầy đủ trong báo cáo, kể cả kiểm định; nhóm sẽ chỉnh cách trình bày theo góp ý của hội đồng.

*(f) Không nói*
- "NeuMF-F là mô hình tốt nhất", "NeuMF-F tốt hơn LateFusion-F".
- "Hai mô hình như nhau" mà không nói "trên H&M".
- "LateFusion-F ổn định hơn": sai trên H&M (độ lệch chuẩn 0,00212 so với 0,00147); trên Amazon hai mức xấp xỉ nhau.
- "LateFusion-F thắng là do ngẫu nhiên": trên Amazon p Holm < 0,001.
- "LateFusion-F không phải mô hình lai": nó là lai theo kiểu hợp nhất muộn, đúng khung trong luận án của cô; chỉ khác là
  gồm hai mô hình riêng.
- "Nhóm chọn NeuMF-F vì huấn luyện nhanh hơn": lý do chọn là mục tiêu đề tài, có trước kết quả; thời gian và độ phủ là
  đánh đổi đo được sau đó.
- Số của các lần chạy cũ (khối 1, giao thức đầu).

*(g) Điểm yếu của LateFusion-F so với NeuMF-F: nói được gì, bằng số nào (kiểm ngày 27/11/2026)*

Dùng khi bị hỏi "NeuMF-F hơn LateFusion-F ở điểm nào?". Nói các điểm đo được trước, điểm thiết kế sau. Đây là đánh đổi
đo được sau khi đã chọn mô hình, không phải lý do chọn (xem (f)).

| Khía cạnh | NeuMF-F | LateFusion-F | Cách nói |
|---|---|---|---|
| Thời gian huấn luyện mỗi seed (Bảng 4.10, mục 4.7) | 15,2 phút (H&M); 4,1 phút (Amazon) | 30,1 phút (GMF-F 13,7 + MLP-F 16,4); 10,9 phút (6,1 + 4,9) | Gấp khoảng 2 lần trên H&M, khoảng 2,7 lần trên Amazon. |
| Tổng số epoch phải chạy | 3,0 (H&M); 5,4 (Amazon) | 4,4 + 4,6 = 9,0; 14,0 + 8,0 = 22,0 | Một phần khoản tiết kiệm đến từ việc NeuMF-F dừng sớm hơn. Số epoch hai nhánh trên Amazon lấy từ `beyond.csv`, không có trong báo cáo. |
| Số mạng phải huấn luyện, lưu và cập nhật | 1 | 2, cộng trọng số trộn $w$ | Mỗi lần có dữ liệu mới phải huấn luyện lại cả hai và giữ đúng cặp phiên bản. |
| Độ phủ top-10, seed 42 (Bảng 4.10, mục 4.7) | 13,3% (H&M); 20,5% (Amazon) | 5,3%; 15,3% | Danh sách của LateFusion-F dồn vào ít sản phẩm hơn. |
| Dao động giữa 5 seed (độ lệch chuẩn NDCG@10) | 0,00147 (H&M); 0,00189 (Amazon) | 0,00212; 0,00180 | Chỉ nói "trên H&M LateFusion-F dao động nhiều hơn"; trên Amazon hai mức xấp xỉ nhau. |

Điểm yếu về thiết kế, nói được mà không cần số:
- **Điểm phụ thuộc vào tập ứng viên.** LateFusion-F chuẩn hoá min–max điểm của từng nhánh trên toàn bộ tập ứng viên của
  khách rồi mới trộn (mục 2.3.4, Thuật toán 3.5). Danh sách ứng viên đổi (lọc theo loại hàng, thêm hàng mới) thì điểm của
  một sản phẩm cũng đổi, và không tính được điểm cho riêng một cặp khách–sản phẩm. NeuMF-F cho điểm độc lập từng cặp.
- **Thêm một siêu tham số.** Trọng số $w$ phải chọn trên tập xác thực (lưới 11 giá trị), và là một trọng số chung cho
  mọi khách.
- **Hai nhánh không học cùng nhau.** Bước trộn chỉ là tổng có trọng số cố định của hai điểm đã chuẩn hoá. NeuMF-F học
  trọng số của lớp dự đoán trên vector hợp nhất 40 chiều cùng lúc với hai nhánh. Điểm này cũng là lý do NeuMF-F đúng
  mục tiêu "một mô hình lai học chung" (mục 1.1.3).

Không được nói (đã kiểm, LateFusion-F không thua ở các mặt này):
- **"NeuMF-F tốn ít bộ nhớ hơn."** Số tham số gần như bằng nhau, vì NeuMF-F cũng có hai bảng vector nhúng riêng cho hai
  nhánh:
  - H&M: NeuMF-F 963.992 tham số, LateFusion-F (GMF-F cộng MLP-F) 968.848.
  - Amazon: 1.100.184 so với 1.118.416.
  - LateFusion-F chỉ nhiều hơn 0,5–1,7%, do mỗi nhánh giữ một bản vector nhúng thuộc tính riêng.
  - Tệp mô hình: 3,86 MB so với 1,94 MB + 1,95 MB.
  - Các số trên đếm từ mô hình đã lưu của seed 42, không có trong báo cáo.
- **"NeuMF-F trả kết quả nhanh hơn."** NeuMF-F chứa cả hai nhánh, nên khối lượng tính cho mỗi cặp gần bằng GMF-F cộng
  MLP-F. Nhóm đo qua API demo ngày 27/11 trên laptop chỉ có CPU, theo cách đo của Bảng 3.7 (300 khách, seed 2026). Trung
  vị thời gian trả top-10:
  - H&M: NeuMF-F 18,9 ms, LateFusion-F 13,5 ms.
  - Amazon: 15,6 ms và 15,0 ms.

  Số đo dao động giữa các lần chạy: Bảng 3.7 ghi NeuMF-F 16,1 ms. Lợi thế về thời gian của NeuMF-F chỉ nằm ở khâu
  huấn luyện.
- **"Tốn ít token hơn."** Đây không phải mô hình ngôn ngữ, nên không xử lý văn bản theo token. Mô tả sản phẩm đã được
  đổi thành vector TF-IDF 64 chiều trước khi vào mô hình, giống nhau cho cả hai. Nói "token" sẽ bị hiểu là nhầm loại mô
  hình.

Cần thừa nhận ưu điểm thật của LateFusion-F: NDCG@10 cao hơn (ngang trên H&M, cao hơn có ý nghĩa trên Amazon), chỉnh
lại $w$ không cần huấn luyện lại, và thay được từng nhánh độc lập.

Câu nói gọn khoảng 20 giây:
> So với LateFusion-F, NeuMF-F chỉ huấn luyện một mạng: thời gian bằng khoảng một nửa trên H&M và hơn một phần ba trên
> Amazon. Danh sách khuyến nghị của NeuMF-F phủ nhiều sản phẩm hơn, và điểm của mỗi cặp khách–sản phẩm không phụ thuộc
> danh sách ứng viên. Bộ nhớ và tốc độ trả kết quả thì hai mô hình tương đương. Đổi lại, LateFusion-F có NDCG@10 cao
> hơn, rõ nhất trên Amazon.

Mở: báo cáo mục 1.1.3 (lý do chọn hợp nhất sớm), 4.3.3 và 4.4.3 (kiểm định), 4.7 (đánh đổi), 5.2.

**Câu 2. Đóng góp mới là gì, NeuMF đã có từ 2017?**
- Trả lời ngắn: NeuMF gốc chỉ học từ mã ID. Đề tài đưa đặc trưng sản phẩm, khách hàng, thời gian vào **cả hai nhánh**,
  tính theo thời điểm nên không dùng thông tin tương lai; chứng minh mô hình vượt có ý nghĩa các đối chứng được tinh chỉnh
  đầy đủ trên hai lĩnh vực; và chỉ ra phần cải thiện đến từ đặc trưng, nhất là đặc trưng thời gian.
- Số nói được ngay: hơn NeuMF chỉ ID +43,8% (H&M), +65,7% (Amazon); hơn UserKNN (đối chứng mạnh nhất) +28,5% trên H&M.
- Mở: mục 2.7, 5.1 (Bảng 5.1).

**Câu 3. Có thật là mô hình lai không, MF đóng vai trò gì?**
- Trả lời ngắn: lai ở hai mức. (1) Lai MF (nhánh GMF-F, tuyến tính) với DNN (nhánh MLP-F, phi tuyến), hai nhánh nối lại
  qua một lớp dự đoán chung (hợp nhất sớm). (2) Lai thông tin cộng tác (vector ID) với thông tin nội dung, ngữ cảnh (đặc
  trưng): vector của mỗi khách, mỗi sản phẩm là **tổng** vector ID và phép chiếu đặc trưng.
- MF: ma trận khách × sản phẩm rất thưa (khoảng 0,45%); MF nén thành hai bảng vector để suy ra điểm cho ô chưa có dữ liệu.
- Hỏi nối tiếp: "Chỉ vào hình giải thích kích thước" → Hình 3.4: d = 32, đặc trưng sản phẩm 157 chiều, khách 42 chiều,
  tháp 64 → 32 → 16 → 8, vector hợp nhất 40 chiều; σ ở lớp dự đoán, huấn luyện bằng BCE với mẫu âm.

**Câu 4. Cải thiện do đặc trưng hay do học sâu? Sao ghép hai nhánh không hơn GMF-F đứng riêng?**
- Trả lời ngắn: đúng là chủ yếu do đặc trưng — đó là phát hiện của đề tài, không phải điểm yếu. Hai cách đo độc lập cùng
  chỉ về đặc trưng: thêm đặc trưng vào cùng kiến trúc (NeuMF-F so với NeuMF chỉ ID) và tắt đặc trưng thời gian (NDCG@10
  giảm 42,3% H&M, 31,6% Amazon). GMF-F ngang NeuMF-F (+2,6% H&M, −0,6% Amazon): nhánh MF có đặc trưng là phần cốt lõi.
- Ý chốt: nên đầu tư vào dữ liệu đặc trưng trước khi làm mạng sâu hơn.
- Hỏi nối tiếp: "Sao không so với Factorization Machines cùng đặc trưng?" → thừa nhận là hạn chế, đã ghi ở mục 5.3, 5.4;
  nhánh GMF-F có đặc trưng về bản chất gần FM. Mở: mục 4.5 (Bảng 4.20).

**Câu 5. Có rò rỉ dữ liệu không, sao không chia leave-one-out như bài NCF?**
- Trả lời ngắn: không rò rỉ. Chia theo một mốc thời gian chung (huấn luyện trước 01/07/2020, xác thực 4 tuần, kiểm thử
  8 tuần); lọc k-core chỉ trên dữ liệu trước mốc kiểm thử; đặc trưng tại ngày t chỉ dùng dữ liệu đến ngày t−1; mẫu kiểm
  định là khách hàng khác hẳn mẫu phát triển; có kiểm thử tự động cho các điều này.
- Leave-one-out lọt tương lai: trên mẫu phát triển, trung bình 11,2% tương tác huấn luyện xảy ra sau ngày của món kiểm thử.
- Mở: mục 3.2.4, Hình 3.3.

**Câu 6. NDCG chỉ khoảng 0,04 có thấp không? Tính NDCG thế nào?**
- Trả lời ngắn: bài toán khó hơn bài NCF nhiều — xếp hạng **toàn bộ** khoảng 6,7 nghìn ứng viên (không phải 100), mỗi
  khách chỉ khoảng 3 món đúng, chỉ tính món chưa từng mua, dự đoán cho 8 tuần tới. Không so số với bài báo được; điều cần
  xem là chênh lệch giữa các mô hình có ý nghĩa thống kê. Random chỉ đạt 0,00098, NeuMF-F 0,04003 (gấp khoảng 40 lần).
- Tính tay (thuộc ví dụ): 3 món đúng ở hạng 2, 7, 40; K = 10. DCG = 1/log₂3 + 1/log₂8 = 0,631 + 0,333 = 0,964;
  IDCG = 1 + 0,631 + 0,5 = 2,131; NDCG@10 ≈ 0,45. HR@10 = 1; Precision@10 = 0,2; Recall@10 ≈ 0,667.
- Mở: mục 2.5.

**Câu 7. So sánh có công bằng không?**
- Trả lời ngắn: mọi mô hình, kể cả NeuMF-F, có **cùng** ngân sách 6 cấu hình, cùng tập xác thực, cùng tập ứng viên, cùng
  5 seed, cùng mã đánh giá (Bảng 4.1). Kết luận "tốt hơn" cần đủ ba điều kiện: p Holm < 0,05, khoảng tin cậy bootstrap
  không chứa 0, chênh lệch ≥ 5%. Kế hoạch và họ 10 so sánh cố định trước khi mở tập kiểm thử.
- Amazon dùng siêu tham số của H&M là chủ ý: kiểm tra kết luận có giữ khi đổi dữ liệu mà không chỉnh theo dữ liệu mới;
  chỉ số epoch chọn trên tập xác thực Amazon. Hai so sánh có BPR-MF trên Amazon không dùng làm bằng chứng.
- Hỏi nối tiếp: "Sao kiểm định theo khách mà không theo seed?" → với 5 seed, p nhỏ nhất của Wilcoxon là 0,0625, không
  bao giờ dưới 0,05 (câu 5.3.8). Mở: mục 3.7, 4.1.

**Câu 8. Cold start xử lý thế nào?**
- Trả lời ngắn: khách mới (chưa có trong dữ liệu) nhận danh sách sản phẩm phổ biến, nên hệ thống luôn có gợi ý; demo
  minh hoạ được (Thuật toán 3.7). Sản phẩm mới nằm ngoài phạm vi đánh giá định lượng: khảo sát ban đầu cho NDCG@10 dưới
  0,002 ở mọi mô hình, quá nhỏ để so sánh. Đây là hướng phát triển: NeuMF-F chấm được sản phẩm chỉ từ đặc trưng.
- Không nói: "đề tài giải quyết cold start sản phẩm", "nhờ bỏ ID ngẫu nhiên" (cấu hình cuối có ρ = 0).
- Mở: mục 2.1.4, 3.8.

**Câu 9. Sao chọn NeuMF mà không chọn Transformer, mạng đồ thị?**
- Trả lời ngắn: H&M chỉ ghi ngày mua, không có phiên nên mô hình chuỗi khó dùng; dữ liệu có sẵn thuộc tính, mô tả, doanh
  số nên hợp cách "vector ID + đặc trưng"; cấu trúc hai nhánh tường minh cho phép tách đóng góp từng phần bằng so sánh
  trực tiếp — đúng mục tiêu trả lời ba câu hỏi nghiên cứu. Mô hình mới là hướng phát triển, dùng lại được nguyên quy trình
  đánh giá.
- Mở: mục 2.4.2, 5.4.

**Câu 10. Ý nghĩa thực tiễn? Triển khai trên dữ liệu thật được không khi mới lấy mẫu khoảng 1,6% khách?**
- Trả lời ngắn: mô hình chỉ dùng dữ liệu bán lẻ doanh nghiệp đã có (giao dịch, danh mục, hội viên, doanh số theo ngày).
  Bài học: cập nhật doanh số theo thời gian và lịch sử mua đem lại nhiều hơn làm mạng phức tạp. Lấy mẫu vì xếp hạng toàn
  bộ trên dữ liệu đầy đủ là hàng chục tỷ cặp mỗi mô hình; mẫu lấy theo khách bằng hàm băm, giữ trọn lịch sử 2 năm.
- Triển khai lớn: hai bước — hai tháp + tìm lân cận gần đúng lọc vài trăm ứng viên, NeuMF-F xếp hạng lại; huấn luyện lại
  hằng tuần; đo bằng thử nghiệm A/B. Đo trên laptop chỉ dùng CPU (i5-1135G7): một danh sách Top-10 của NeuMF-F trả về trong trung vị 16,1 ms (H&M) và 11,3 ms (Amazon), 95% yêu cầu dưới 20 ms (báo cáo Bảng 3.7).
- Mở: mục 1.4.2, 5.2, 5.4.

Cách trả lời câu khó: **thừa nhận ngắn → nêu lý do hoặc thiết kế đã xử lý → quay về điểm mạnh.** Không cãi, không vòng vo.

### 0.1 Bốn điểm yếu hội đồng có thể xoáy sâu (đánh giá 18/11/2026)

Bốn điểm dưới đây là giới hạn thật của thực nghiệm, không sửa được bằng câu chữ và không chạy lại được, vì tập kiểm thử
đã mở. Cách xử lý là chuẩn bị câu trả lời có số liệu.

**(a) "Nhánh DNN không thêm gì: NeuMF-F ngang GMF-F. Vậy 'kết hợp MF và DNN' ở tên đề tài có ý nghĩa gì?"**
Thừa nhận: ở quy mô này, nhánh MLP-F chưa thêm được khác biệt có ý nghĩa so với GMF-F (+2,6% H&M, −0,6% Amazon). Lý do và
điểm mạnh: (1) NeuMF-F hơn nhánh MLP-F +15,0% trên H&M, tức ghép hai nhánh không làm mất phần mạnh của nhánh MF; (2) câu
hỏi nghiên cứu 3 được đặt ra chính để đo điều này, và kết quả "biểu diễn có đặc trưng quan trọng hơn cách ghép" là một
phát hiện có ích: muốn khuyến nghị tốt hơn thì đầu tư vào đặc trưng trước khi làm mạng sâu hơn; (3) trên H&M, độ phủ
top-10 của NeuMF-F cao nhất trong các mạng nơ-ron (mục 4.3.6).
Không nói "DNN giúp tăng độ chính xác".

**(b) "Bóc tách chỉ chạy một seed, sao dám nói đặc trưng thời gian quan trọng nhất?"**
Thừa nhận: bóc tách dùng seed 42 và báo cáo ghi rõ là phân tích mô tả, không qua kiểm định đa so sánh (mục 4.3.5). Nhưng
mức giảm khi bỏ đặc trưng thời gian (NDCG@10 từ 0,04137 xuống 0,02386, −42,3%) lớn gấp khoảng 12 lần độ lệch chuẩn giữa 5
seed của NeuMF-F (0,00147), khoảng tin cậy bootstrap theo khách không chứa 0, và kết quả lặp lại trên Amazon (−31,6%).
Với thuộc tính và văn bản trên H&M, báo cáo đã nói chưa khẳng định được.

**(c) "NeuMF-F hơn NeuMF có phải chỉ vì nhiều tham số hơn?"**
Không. Khi tinh chỉnh với cùng ngân sách, NeuMF chỉ dùng ID **chọn d = 64**, còn NeuMF-F **chọn d = 32** (Bảng 4.2).
Mô hình có vector nhúng nhỏ hơn mà vẫn hơn +43,8%. Ước tính trên mẫu kiểm định (7.994 khách, 6.749 sản phẩm): bảng nhúng
ID của NeuMF-F khoảng 0,94 triệu tham số, phép chiếu đặc trưng thêm khoảng 13 nghìn ((157 + 42) × 32 × 2 nhánh); NeuMF
với d = 64 có khoảng 1,9 triệu tham số nhúng, gấp đôi. Thêm nữa, các biến thể bóc tách giữ nguyên kiến trúc, chỉ tắt thông tin, mà vẫn giảm mạnh.

**(d) "Không có đối chứng dùng cùng đặc trưng mà không phải mạng nơ-ron (FM, LightFM)?"**
Thừa nhận, đã ghi ở hạn chế và hướng phát triển (mục 5.3, 5.4). Phạm vi đề tài là họ NeuMF. Đối chứng ngoài mạng nơ-ron
có dùng thông tin nội dung là Content và Hybrid-CBCF, và NeuMF-F tốt hơn có ý nghĩa cả hai, trên cả hai bộ dữ liệu. Nhánh
GMF-F có đặc trưng về bản chất gần với FM.

Ngoài ra, báo cáo bản 18/11 đã sửa ba chỗ hội đồng có thể bắt lỗi: mật độ ma trận ở mục 1.1.1 (0,02% theo mã sản phẩm,
0,04% theo mẫu thiết kế, tính lại từ tệp giao dịch gốc); câu "tốt hơn cả năm mô hình đối chứng trên Amazon" nay nói rõ
không dựa vào BPR-MF (bỏ so sánh đó ra, chênh nhỏ nhất vẫn +30,8% với UserKNN). Bản viết gọn 24/11 dẫn lại bảng, hình,
mục và công thức trong thân bài; tóm tắt vẫn không nêu số liệu.

### 0.2 Câu hỏi bám theo từng slide (soạn 26/11/2026)

Hội đồng thường hỏi vào đúng thứ đang chiếu hoặc vừa nghe. Mỗi slide dưới đây có những câu dễ bị hỏi nhất kèm ý trả
lời ngắn; chi tiết ở câu được dẫn. Ai trình bày phần nào thì chuẩn bị trước các câu của phần đó.

**Slide 2 — Bối cảnh và bài toán**
- "Ma trận thưa đến mức nào?" → Trên toàn bộ H&M khoảng 0,02% (theo mã sản phẩm) và 0,04% (theo mẫu thiết kế). Sau lọc
  10-core trên mẫu kiểm định khoảng 0,45% (243.696 cặp trên 7.994 × 6.749 ô). Mở: mục 1.1.1, 3.2.3.
- "Bốn nhóm thông tin này doanh nghiệp có sẵn không?" → Có, nằm trong ba tệp của H&M: `articles.csv` (thuộc tính, mô
  tả), `transactions_train.csv` (doanh số theo ngày), `customers.csv` (tuổi, hội viên). Không phải thu thập thêm.

**Slide 3 — Câu hỏi nghiên cứu**
- "Câu hỏi 3 được trả lời là có hay không?" → Không trả lời có/không. Khi đã có đặc trưng, các cách ghép cho kết quả
  gần nhau: trên H&M NeuMF-F hơn MLP-F, ngang GMF-F và LateFusion-F; trên Amazon LateFusion-F tốt hơn. Kết luận: biểu
  diễn có đặc trưng là yếu tố quyết định, cách hợp nhất chọn theo dữ liệu. Mở: mục 4.7; Phần 0, Câu 1; câu 5.4.2.

**Slide 4 — Từ NeuMF đến NeuMF-F**
- "Ô màu cam là gì? Đặc trưng được nối thêm hay cộng vào?" → Cộng vào. Trong mỗi nhánh, vector khách = vector ID +
  W_U·x_u, vector sản phẩm = vector ID + W_I·x_i. W là phép chiếu tuyến tính không có độ lệch (32 × 157 cho sản phẩm,
  32 × 42 cho khách), mỗi nhánh một bộ riêng. Cộng giữ nguyên d = 32 chiều, nên phần còn lại của NeuMF không đổi. Mở:
  mục 3.3.1.
- "157 và 42 chiều gồm những gì?" → Sản phẩm: 11 thuộc tính, mỗi thuộc tính một vector nhúng 8 chiều học cùng mô hình
  (88), văn bản 64, thời gian 5. Khách: 5 thuộc tính × 8 = 40, cộng 2 đặc trưng thời gian.
- "Sao 8 mẫu âm? Sao tháp 64 → 32 → 16 → 8?" → Số mẫu âm được tinh chỉnh trong {4, 8} và chọn 8. Tháp giảm một nửa qua
  mỗi lớp như NCF, bắt đầu từ 2d = 64.
- "Qua sigmoid rồi xếp hạng theo xác suất à?" → Xếp hạng theo logit, tức điểm trước sigmoid. Sigmoid đồng biến nên
  không đổi thứ tự, nhưng với số float32, nhiều điểm lớn sau sigmoid thành đúng 1,0 và bị bằng điểm. Mở: mục 3.3.4.

**Slide 5 — Dữ liệu**
- "'Khách mua sản phẩm mới' là hàng mới ra mắt à?" → Không. Đó là món khách chưa từng mua trước mốc, tức mới với khách
  đó. Sản phẩm chưa có dữ liệu huấn luyện, kể cả hàng vừa ra mắt, không nằm trong tập ứng viên. Đây là chỗ dễ hiểu nhầm
  nhất, nên nói rõ ngay khi trình bày slide này. Mở: mục 3.2.4.
- "Có 7.994 khách mà chỉ 3.165 khách được đánh giá?" → Chỉ khách mua ít nhất một món chưa từng mua trong 8 tuần kiểm
  thử mới được đánh giá, khoảng 40% số khách sau lọc.
- "Có 6.749 sản phẩm mà mỗi khách chỉ 6.710 ứng viên?" → Ứng viên của một khách là mọi sản phẩm có dữ liệu huấn luyện,
  trừ những món khách đó đã mua; 6.710 là trung bình theo khách.
- "Amazon là lượt đánh giá, sao coi như lượt mua? Sao Amazon 5-core mà H&M 10-core?" → Mỗi đánh giá được coi là một
  tương tác ẩn, không dùng số sao. Amazon thưa hơn nhiều và bản gốc phát hành ở dạng 5-core; H&M dùng 10-core để xếp
  hạng toàn bộ vừa bộ nhớ (câu 5.3.10). Mở: mục 4.4.1.

**Slide 6 — Quy trình thực nghiệm**
- "Đã chọn được số epoch, sao còn huấn luyện lại?" → Để mô hình học cả 4 tuần xác thực, tức dữ liệu gần nhất, trước khi
  dự đoán 8 tuần kiểm thử, giống khi triển khai. Số epoch giữ đúng như đã chọn, nên tập kiểm thử không bao giờ được dùng
  để dừng. Mở: mục 3.6, Thuật toán 3.3.
- "Sao xác thực 4 tuần mà kiểm thử 8 tuần?" → Kiểm thử là 8 tuần cuối của bộ dữ liệu (đến 22/09/2020). Cửa sổ dài hơn
  thì nhiều khách có món mới để đánh giá hơn: khoảng 40% số khách ở cửa sổ kiểm thử, so với 32% ở cửa sổ xác thực. Vì
  hai cửa sổ dài khác nhau, NDCG lúc tinh chỉnh và lúc đánh giá cuối không cùng thang; nhóm chỉ so thứ hạng (mục 4.3.7).
- "Wilcoxon, bootstrap, Holm là gì?" → Bảng ở 5.7.

**Slide 7 — Mô hình đối chứng**
- "Đưa Random vào làm gì?" → Làm mốc dưới, cho thấy độ đo có ý nghĩa: NDCG@10 của NeuMF-F gấp khoảng 40 lần Random
  (0,04003 so với 0,00098).
- "Hybrid-CBCF là gì?" → Mô hình lai truyền thống theo luận án của cô: trộn điểm đã chuẩn hoá min–max của Content,
  UserKNN, ItemKNN, với trọng số học theo cặp (0,12; 0,60; 0,28). Câu 5.5.2, 5.5.3.
- "Sao không so với ALS, FM, LightFM, mô hình chuỗi, mạng đồ thị?" → ALS được thay bằng BPR-MF, cùng nhóm MF cho phản
  hồi ẩn (5.6.3); thiếu FM dùng cùng đặc trưng là hạn chế đã nêu (0.1 (d)); mô hình chuỗi, đồ thị ở câu 5.1.3.

**Slide 8 — Kết quả trên H&M**
- "+43,8% là tương đối hay tuyệt đối?" → Tương đối: (0,04003 − 0,02783) / 0,02783. Tuyệt đối là +0,0122 NDCG@10, khoảng
  tin cậy 95% [+0,00876; +0,01566], p Holm < 0,001.
- "'5/5' là năm mô hình nào?" → Năm mô hình đối chứng trong họ 10 so sánh (so sánh 5–9): BPR-MF, ItemKNN, UserKNN,
  MostPopular-Recent, Content. Hybrid-CBCF nằm ở phân tích bổ sung và cũng thua có ý nghĩa (+25,8%, dòng dưới của
  slide). Slide 7 xếp MostPopular-Recent vào nhóm "chuyên biệt cho khuyến nghị", nên nếu bị hỏi thì nói rõ như trên.
- "Biểu đồ có mô hình cao hơn NeuMF-F?" → Có, LateFusion-F (0,04093), nhưng trên H&M hai mô hình không khác biệt có ý
  nghĩa (−2,2%, p Holm 0,735); slide 11 bàn cách hợp nhất. Nói thẳng, không né (Phần 0, Câu 1).

**Slide 9 — Kết quả trên Amazon Beauty**
- "NeuMF-F đứng thứ mấy trên Amazon?" → Thứ ba, sau LateFusion-F và GMF-F; GMF-F chỉ hơn 0,6% và không khác biệt có ý
  nghĩa. Nên tự nói ra trước khi bị hỏi.
- "'5/5' có tính BPR-MF, mà BPR-MF dùng cấu hình H&M nên kém hẳn?" → Có tính, nhưng báo cáo không dùng so sánh với BPR-MF
  trên Amazon làm bằng chứng. Bỏ BPR-MF ra, NeuMF-F vẫn tốt hơn có ý nghĩa bốn mô hình còn lại, chênh nhỏ nhất +30,8%
  (UserKNN), và tốt hơn Hybrid-CBCF +23,0%. Câu 5.5.1.
- "NeuMF-F so với MLP-F có p Holm 0,050, sao không kết luận tốt hơn?" → Tiêu chí cần đủ ba điều kiện, trong đó có khoảng
  tin cậy không chứa 0. Ở đây khoảng tin cậy là [−0,00044; +0,00457], có chứa 0.

**Slide 10 — Đặc trưng nào đóng góp nhiều nhất?**
- "Bỏ một nhóm đặc trưng là huấn luyện lại hay chỉ đặt bằng 0 lúc dự đoán?" → Huấn luyện lại một mô hình riêng không có
  nhóm đặc trưng đó, giữ nguyên siêu tham số, cách lấy mẫu âm và quy trình của NeuMF-F, với seed 42. Mở: mục 3.4.1,
  4.3.5.
- "Đặc trưng thời gian gồm gì, sao lại quan trọng nhất?" → Của sản phẩm: doanh số 7, 28, 91 ngày trước, tuổi sản phẩm,
  cờ chưa từng bán; của khách: số ngày từ lần mua gần nhất, số món đã mua; tất cả tính đến ngày t − 1. Hàng thời trang
  đổi xu hướng nhanh, mà mô hình chỉ dùng ID không biết món nào đang bán chạy hay vừa ra. NeuMF-F vẫn hơn
  MostPopular-Recent (cùng nguồn doanh số nhưng không cá nhân hoá) +45,0%, tức mô hình không chỉ đoán theo xu hướng chung.
- "Một seed có đủ tin không?" → Câu 0.1 (b).
- "Trên Amazon bỏ thông tin khách hàng lại tăng 1,3%?" → Khoảng tin cậy chứa 0, tức không thay đổi có ý nghĩa. Amazon
  không có thuộc tính khách, nên biến thể này chỉ bỏ hai đặc trưng thời gian của khách.

**Slide 11 — Hợp nhất sớm và hợp nhất muộn**
- "Thời gian đo trên máy nào?" → Laptop CPU AMD Ryzen 7 6800H, GPU RTX 3050 Laptop; trung bình mỗi seed; chỉ là thời
  gian huấn luyện, chưa tính tạo danh sách. Thời gian của LateFusion-F là tổng của GMF-F và MLP-F (13,7 + 16,4 = 30,1
  phút trên H&M).
- "Độ phủ 13,3% nghĩa là gì?" → Khoảng 900 trong 6.749 sản phẩm có mặt trong top-10 của ít nhất một khách (seed 42).
  LateFusion-F chỉ 5,3%, tức nhiều khách nhận danh sách giống nhau hơn. Độ phủ chỉ có nghĩa khi xem cùng độ chính xác:
  Random phủ 98,9%.
- "LateFusion-F là ghép hai mô hình, so với một mạng có công bằng không?" → Nó dùng hai mạng nên thời gian huấn luyện
  gấp đôi trên H&M, gần gấp ba trên Amazon; nhóm đưa nó vào họ so sánh để đo cách hợp nhất. Báo cáo giải thích kết quả
  trên Amazon: hai nhánh khuyến nghị những tập sản phẩm rất khác nhau (độ phủ GMF-F 32,1%, MLP-F 5,4%), nên trộn điểm
  thì bổ sung cho nhau. Chi tiết: Phần 0, Câu 1.

**Slide 12–13 — Demo**
- "Hệ thống có dùng cơ sở dữ liệu không?" → Không dùng hệ quản trị cơ sở dữ liệu. Tầng mô hình và dữ liệu nạp tệp đã xử
  lý, trọng số đã huấn luyện và kết quả đánh giá vào bộ nhớ một lần khi khởi động (15,2 giây với H&M, 4,6 giây với
  Amazon); API chỉ làm suy luận.
- "Khách mua thêm thì danh sách có cập nhật không?" → Demo dùng mô hình cố định tại mốc kiểm thử. Khi triển khai thật
  thì huấn luyện lại định kỳ, ví dụ hằng tuần (câu 5.1.4).
- "Khách ví dụ có phải được chọn cho đẹp?" → Đúng, nút "Xem ví dụ" chọn khách mà NeuMF-F trúng còn mô hình đối chứng
  trượt, để minh hoạ; kết quả trung bình nằm ở slide 8–9. Có thể chọn ngay một khách ngẫu nhiên trước hội đồng. Nếu
  NeuMF-F trượt ở khách đó thì bình thường: HR@10 khoảng 15%, tức phần lớn khách không có món đúng trong top-10.
- "Phản hồi có nhanh không?" → Top-10 của NeuMF-F trả về trong trung vị 16,1 ms (H&M) và 11,3 ms (Amazon) trên laptop
  chỉ dùng CPU; 95% yêu cầu dưới 19,0 ms và 15,2 ms (Bảng 3.7).
- "Số trên demo khác số trong báo cáo?" → Phần 7.

**Slide 14 — Kết luận**
- "Hạn chế lớn nhất là gì?" → Nói ba ý, mỗi ý kèm hướng khắc phục: (1) mẫu khoảng 1,6% khách, lọc 10-core, nên kết luận
  áp dụng cho khách có lịch sử dày → mở rộng dữ liệu, hạ ngưỡng lọc; (2) chưa đo được sản phẩm vừa ra mắt → đánh giá
  riêng, vì NeuMF-F đã chấm được sản phẩm chỉ từ đặc trưng; (3) nhánh DNN chưa thêm khác biệt có ý nghĩa so với GMF-F, và
  chưa có đối chứng FM dùng cùng đặc trưng (0.1 (a), (d)).
- "'Quy trình đánh giá dùng lại được' cụ thể là gì?" → Amazon Beauty chạy bằng cùng mã nguồn huấn luyện và đánh giá,
  chỉ thay dữ liệu, bộ đặc trưng và tệp cấu hình; sáu nguyên tắc ở mục 3.7 giữ nguyên.

### 0.3 Câu hỏi xoáy mới (kiểm bằng số liệu và mã nguồn ngày 26/11/2026)

Các câu dưới đây chưa có ở phần trên. Câu trả lời đã được đối chiếu với kết quả đã lưu trong `neumf_project/outputs/` và
với mã nguồn, không mở lại tập kiểm thử.

**(e) "NeuMF-F lấy mẫu âm theo ngày ra mắt, còn NeuMF lấy đều. Phần hơn có phải do cách lấy mẫu âm chứ không do đặc
trưng?"**
Không. Biến thể bóc tách bỏ đặc trưng thời gian vẫn được huấn luyện bằng đúng cách lấy mẫu âm theo ngày ra mắt của
NeuMF-F (đã kiểm trong mã: hàm `fit_torch` của `scripts/common.py` dùng cùng bộ dữ liệu huấn luyện cho mọi biến thể
có đặc trưng), vậy mà NDCG@10 vẫn giảm 42,3% trên H&M và 31,6% trên Amazon. NeuMF lấy mẫu đều như NCF gốc vì mô hình
chỉ dùng ID không nhận ngày làm đầu vào.

**(f) "`customers.csv` không có mốc thời gian. Có rò rỉ không?"**
Thừa nhận: tệp này là một ảnh chụp không ghi thời điểm, và báo cáo đã nói rõ nhóm coi các thuộc tính này là ít thay
đổi (mục 3.2.5). Đó là nhóm tuổi, trạng thái hội viên, tần suất nhận tin, FN, Active; không thuộc tính nào cho biết
khách sẽ mua món gì. Mọi đặc trưng có yếu tố thời gian đều tính đến ngày t − 1. Trên Amazon không có thuộc tính khách
nào mà kết luận về đặc trưng vẫn giữ nguyên.

**(g) "Sao báo cáo bỏ K = 5? Có phải ở K = 5 kết quả xấu?"**
Không. Hạng của từng món đúng đã được lưu, nên độ đo @5 tính lại được từ kết quả đã lưu (`outputs/*/final/by_k.csv`)
mà không mở lại tập kiểm thử. Ở K = 5 thứ tự giữ nguyên: trên H&M là LateFusion-F, NeuMF-F, GMF-F, MLP-F rồi UserKNN,
theo cả NDCG@5 lẫn HR@5; trên Amazon là LateFusion-F, GMF-F, NeuMF-F, MLP-F rồi UserKNN, giống @10. Nhóm bỏ K = 5 vì
mỗi khách chỉ có khoảng 3 món đúng giữa khoảng 6.700 ứng viên, danh sách 5 món quá ngắn và độ đo dao động giữa các seed
nhiều hơn (mục 4.1). Số @5 không có trong báo cáo, chỉ nói khi được hỏi.

**(h) "Precision@10 chỉ 1,7%, tức 98% khuyến nghị là sai?"**
Precision bị giới hạn bởi số món đúng: trung bình mỗi khách chỉ có 3,2 món đúng (10.285 cặp trên 3.165 khách), nên dù
đoán hoàn hảo, Precision@10 cũng chỉ khoảng 0,3. Random đạt 0,00049, NeuMF-F đạt 0,01723, gấp khoảng 35 lần. Dễ hiểu
hơn là HR@10: cứ khoảng 7 khách thì có 1 khách mua thật một món trong 10 khuyến nghị, dù khách chưa từng thấy danh sách
đó. Tác động khi khách nhìn thấy khuyến nghị phải đo bằng thử nghiệm A/B.

**(i) "Amazon không có mẫu khách độc lập. Có chọn gì trên tập kiểm thử không?"**
Không. Trên Amazon không có bước tinh chỉnh nào: mọi cấu hình lấy từ H&M. Thứ duy nhất chọn trên Amazon là số epoch,
dùng tập xác thực 01/10–31/12/2013, trước tập kiểm thử 01/01–23/07/2014. Tập kiểm thử Amazon cũng chỉ mở một lần. Mở:
mục 4.4.1.

**(j) "Mạng chỉ chạy khoảng 3 epoch, có phải chưa học xong?"**
Số epoch do dừng sớm chọn: tối đa 20 epoch, dừng khi NDCG@10 xác thực không tăng sau 5 epoch. NDCG@10 xác thực đạt đỉnh
sớm rồi không tăng thêm, nên chạy tiếp không giúp gì. Mỗi epoch đã duyệt khoảng 240 nghìn cặp (khách, sản phẩm), mỗi
cặp kèm 8 mẫu âm, tức hơn 2 triệu mẫu. Trên Amazon, NeuMF-F chọn trung bình 5,4 epoch. Mở: mục 4.3.6.

**(k) "Doanh số tính trên toàn bộ H&M, kể cả khách ngoài mẫu. Có dùng thông tin của chính khách đang được đánh giá
không?"**
Doanh số tại ngày t chỉ cộng giao dịch đến ngày t − 1, nên chỉ là dữ liệu quá khứ mà doanh nghiệp có thật lúc dự đoán.
Không giao dịch nào sau mốc được dùng. MostPopular-Recent dùng cùng nguồn doanh số nên phép so sánh công bằng, và NeuMF-F
vẫn hơn nó 45,0%.

**(l) "Sao UserKNN, ItemKNN, Content có độ lệch chuẩn bằng 0?"**
Các mô hình này không có bước ngẫu nhiên khi huấn luyện, nên năm seed cho cùng một kết quả (mục 4.3.1). Mô hình có khởi
tạo ngẫu nhiên thì dao động nhỏ, ví dụ NeuMF-F là 0,04003 ± 0,00147.

**(m) "Bảng 4.10 ghi UserKNN chỉ 0,0 phút, NeuMF-F mất 15,2 phút mà chỉ hơn 28,5%. Mạng nơ-ron có đáng không?"**
Bảng làm tròn một chữ số. Trên mẫu này UserKNN mất khoảng 3 giây, ItemKNN khoảng 2 giây, vì ma trận tương đồng của
khoảng 8 nghìn khách và 6,7 nghìn sản phẩm còn nhỏ. Có ba ý để trả lời:
1. Phần hơn 28,5% NDCG@10 có ý nghĩa thống kê. Trên Amazon con số này là 30,8%.
2. Huấn luyện là việc chạy định kỳ, không chạy trong lúc khách chờ. Lúc phục vụ, NeuMF-F trả một danh sách top-10 trong
   khoảng 16 ms (Bảng 3.7).
3. Khi dữ liệu lớn lên, ma trận tương đồng đầy đủ của KNN tăng theo bình phương số khách hoặc số sản phẩm. Chi phí huấn
   luyện mô hình học tham số chỉ tăng tuyến tính theo số tương tác (mục 2.1.2).

Thời gian 0,1 phút của Hybrid-CBCF đo trên một máy khác (CPU i5, Bảng 4.1), nên không so trực tiếp với các mô hình còn
lại. Mở: mục 4.3.6.

**(n) "Khách mới nhận danh sách Most Popular, trong khi MostPopular-Recent tốt hơn. Sao không dùng MostPopular-Recent?"**
Thừa nhận đây là chỗ cải tiến được. Nhóm chọn Most Popular cho khách mới vì đơn giản và không phải chọn cửa sổ W. Báo
cáo cũng không đánh giá định lượng nhóm khách mới (mục 5.3). Trên khách đã có lịch sử, MostPopular-Recent tốt hơn Most
Popular trên cả hai bộ: 0,02760 so với 0,02184 (H&M), 0,01401 so với 0,00872 (Amazon). Vì vậy dùng nó cho khách mới là
cải tiến hợp lý, chỉ cần đổi nguồn danh sách phổ biến. Không khẳng định nó tốt hơn cho khách mới, vì chưa đo trên nhóm
này. Mở: mục 3.8.

**(o) "Bảng 2.1 ở chương 2 đã có kết quả của đề tài. Sao kết quả xuất hiện trước chương 4?"**
Bảng 2.1 là bảng đối chiếu thiết lập theo yêu cầu của cô. Bảng đặt thiết lập của đề tài cạnh ba nghiên cứu nền tảng để
thấy khác biệt về dữ liệu, bài toán, cách chia và số ứng viên. Dòng của đề tài ghi kết quả chính để người đọc thấy ngay
khác biệt đó, còn số đầy đủ và kiểm định nằm ở chương 4. Đoạn văn ngay trước bảng đã nói rõ các con số không so trực tiếp
được với nhau. Không đọc số của bài báo cạnh số của đề tài khi trả lời câu này (Phần 6).

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
| 4 | Quy trình đánh giá và hệ thống hoàn chỉnh | Sáu nguyên tắc đánh giá (mục 3.7), demo chạy được trên cả hai bộ dữ liệu, 14 mô hình |

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
  để trả lời → Chương 4 trình bày kết quả, chỉ ra phần cải thiện đến từ đặc trưng (mục 4.5) và trả lời từng câu (mục 4.7) → Chương 5 đối chiếu mục tiêu.

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

Sáu nguyên tắc (mục 3.7):
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
- **Nguồn gốc cải thiện (mục 4.5, Bảng 4.20):** bảy yếu tố có thể tác động đến kết quả (tinh chỉnh, điều kiện đánh
  giá, rò rỉ, dao động ngẫu nhiên, kiến trúc, chọn cấu hình, một bộ dữ liệu) và cách loại trừ từng yếu tố.
- **Trả lời câu hỏi (mục 4.7):** câu 1 và câu 2 được trả lời "có" trên cả hai bộ; câu 3: biểu diễn có đặc trưng là
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
| Trọng số LateFusion-F | w = 0,4 cho GMF-F (0,6 cho MLP-F) | mục 3.7, Thuật toán 3.5 |
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
| LateFusion-F cao nhất, tốt hơn NeuMF-F trên Amazon | **Có**, nói rõ (mục 4.4.3, 4.7) — đây là kết quả, không được giấu | Lý do giữ NeuMF-F làm mô hình đề xuất (Phần 0, Câu 1) |
| Khảo sát ban đầu: NeuMF chỉ ID không hơn BPR-MF | Có, như định hướng thiết kế (mục 3.7) | Giai đoạn đầu chỉ dùng mã ID, đánh giá trên mẫu phát triển |
| Khối 1 (mẫu kiểm định của bản kế hoạch đầu) | Không | Câu 5.6.1 |
| Seed 42 chạy lại, máy chạy (GPU RTX 3050 / CPU) | Không | Câu 5.6.2 |
| Content lệch nhẹ giữa Bảng 4.2 và 4.3 | Một câu ngắn (mục 4.2) | Vector văn bản được dựng lại trên máy khác khi chạy phần bổ sung; thứ hạng không đổi |
| K = 15 tính lại từ hạng đã lưu | Không nói chi tiết (mục 3.7 chỉ nói hạng được lưu) | Câu 5.3.6 |
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
Ba lý do (mục 2.4.2): H&M chỉ ghi ngày mua, không có phiên, nên mô hình chuỗi khó dùng; dữ liệu có sẵn thuộc tính và
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
Ba cơ chế được tinh chỉnh như siêu tham số: dropout ở tháp MLP {0; 0,2}, điều chuẩn L2 {0; 10⁻⁶} và dừng sớm theo
NDCG@10 xác thực (sau 5 epoch không cải thiện). Cấu hình chọn của NeuMF-F là dropout = 0, L2 = 10⁻⁶, nên cơ chế chính là
dừng sớm: NeuMF-F chọn trung bình 3 epoch trên H&M (Bảng 4.10). Khi huấn luyện lại chạy đúng số epoch đã chọn. Không
nói "NeuMF-F dùng dropout" (Bảng 4.2 ghi dropout = 0).

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
tới; xếp hạng toàn bộ chứ không trên 101 ứng viên lấy mẫu như bài NCF, nên không đặt số của đề tài cạnh số của bài báo.
Mốc để so là Random (0,00098) và các mô hình đối chứng; điều cần xem là chênh lệch giữa các mô hình có ý nghĩa thống kê.

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
- NDCG@10 = 0,964 / 2,131 ≈ 0,45.

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

**5.3.10 "Vì sao lấy mẫu khoảng 1,6% khách, k = 10?"**
Xếp hạng toàn bộ trên dữ liệu đầy đủ (633 nghìn khách × 80 nghìn sản phẩm với k = 10) là hàng chục tỷ cặp cho mỗi mô
hình. Với k = 5 trên mẫu phát triển, ước tính cần khoảng 10,7 GB bộ nhớ. Lấy mẫu theo khách bằng hàm băm giữ trọn lịch sử
và cho hai mẫu tương đương nhau (Bảng 3.3). Mở rộng quy mô là hướng phát triển.

### 5.4 Kết quả

**5.4.1 "LateFusion-F cao nhất, sao không chọn nó làm mô hình đề xuất?"** (câu trọng tâm)
Bản đầy đủ ở **Phần 0, Câu 1**: trả lời 30 giây, trả lời 2 phút, bảng số liệu, mốc thời gian, 10 câu hỏi vặn. Ý chính:
NeuMF-F là mô hình lai một mạng, học chung, đúng mục tiêu đề tài (báo cáo mục 1.1.3) và được xác định trước khi có kết
quả. LateFusion-F là hợp nhất muộn của chính hai nhánh có đặc trưng: tương đương trên H&M (−2,2%, p Holm 0,735), tốt hơn
trên Amazon (NeuMF-F −12,5%, p Holm < 0,001). Đổi lại, NeuMF-F huấn luyện nhanh hơn và có độ phủ top-10 cao hơn trên cả
hai bộ.

**5.4.2 "Vì sao ghép hai nhánh không hơn nhánh GMF-F đứng riêng?"**
GMF-F đứng riêng đã ngang NeuMF-F ở cả hai bộ (+2,6% H&M, −0,6% Amazon). Phần lớn lợi ích nằm ở đặc trưng đưa vào nhánh
MF, chứ không ở việc thêm nhánh phi tuyến. Đây là kết quả có giá trị: nó cho thấy nên đầu tư vào dữ liệu đặc trưng hơn là
vào độ sâu của mạng.

**5.4.3 "NeuMF chỉ ID không hơn BPR-MF — mô hình lai có vô dụng không?"**
Không vô dụng. Khi chỉ có mã ID, NeuMF và MF học từ cùng một nguồn thông tin, nên NeuMF khó vượt MF đã tinh chỉnh kỹ;
vì vậy đề tài làm theo khuyến nghị của Rendle (2020) là luôn so với MF được tinh chỉnh đầy đủ. Kết quả khảo sát ban đầu
này là lý do nhóm bổ sung thông tin thay vì thêm tham số, từ đó có NeuMF-F; khi có đặc trưng, NeuMF-F vượt BPR-MF +50,4%
trên H&M.

**5.4.4 "Thứ hạng có ổn định giữa tinh chỉnh và kiểm thử không?"**
Ổn định ở nhóm đầu: bốn mô hình có đặc trưng đứng đầu cả hai lần; LateFusion-F và NeuMF-F giữ hai vị trí đầu. GMF, MLP
chỉ ID tụt từ hạng 5 và 7 xuống 9 và 11; ItemKNN lên từ hạng 10 lên 6 (Hình 4.4).

**5.4.5 "Đặc trưng văn bản có giúp không?"**
Trên H&M chưa khẳng định được (bỏ văn bản −2,7%, khoảng tin cậy chứa 0). Đặc trưng thời gian và thông tin khách quan
trọng hơn nhiều. Biểu diễn văn bản bằng mô hình ngôn ngữ là hướng phát triển.

**5.4.6 "Làm sao biết NeuMF-F tốt hơn là nhờ đặc trưng, không phải do may mắn hay do cách làm thực nghiệm?"**
Báo cáo mục 4.5 (Bảng 4.20) trả lời câu này. Mọi yếu tố khác được giữ giống nhau cho mọi mô hình hoặc được kiểm tra riêng:
- Cùng ngân sách tinh chỉnh, cùng độ đo, cùng tập xác thực; cùng mẫu khách, tập ứng viên, năm seed và mã đánh giá.
- Chia dữ liệu theo thời gian, đặc trưng tính tại thời điểm dự đoán nên không rò rỉ tương lai.
- Năm lần chạy, Wilcoxon trên từng khách, bootstrap và Holm nên không phải dao động ngẫu nhiên.
- Cấu hình chọn trên mẫu phát triển, kết luận rút trên mẫu kiểm định (khách khác); lặp lại trên Amazon không tinh chỉnh lại.

Hai cách đo độc lập cùng chỉ về đặc trưng: thêm đặc trưng vào cùng kiến trúc (NeuMF-F so với NeuMF chỉ ID: +43,8% H&M,
+65,7% Amazon, đều có ý nghĩa) và tắt đặc trưng thời gian (NDCG@10 giảm 42,3% H&M, 31,6% Amazon).

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

### 5.7 Kiến thức nền (hay bị hỏi riêng từng bạn)

Hội đồng hay chỉ vào một ký hiệu trên slide rồi hỏi bạn không trình bày phần đó. Cả hai bạn cần nói được mỗi khái niệm
dưới đây trong một, hai câu, kèm chỗ nó xuất hiện trong đề tài.

| Khái niệm | Nói ngắn | Trong đề tài |
|---|---|---|
| Vector nhúng (*embedding*) | Bảng tham số, mỗi mã ID một hàng gồm d số, học bằng lan truyền ngược; tương đương nhân vector one-hot với một ma trận | Bảng ID của mỗi nhánh, d = 32; mỗi thuộc tính danh mục một vector 8 chiều |
| Phép chiếu đặc trưng | Nhân ma trận W với vector đặc trưng để đưa về d chiều, rồi cộng vào vector ID | W cỡ 32 × 157 (sản phẩm), 32 × 42 (khách), không có độ lệch, riêng cho từng nhánh |
| Phép nhân Hadamard ⊙ | Nhân từng phần tử của hai vector | Nhánh GMF-F; lớp đầu ra học trọng số cho từng chiều, trọng số bằng 1 và không có đặc trưng thì quay về MF |
| ReLU, dropout | ReLU(x) = max(0, x). Dropout tắt ngẫu nhiên một phần nơ-ron khi huấn luyện để chống quá khớp | Tháp MLP; dropout tinh chỉnh trong {0; 0,2}, NeuMF-F chọn 0 |
| Sigmoid, logit | σ(z) = 1 / (1 + e^(−z)) đưa điểm về khoảng (0, 1); logit là z trước sigmoid | Huấn luyện dùng σ, xếp hạng dùng logit |
| BCE | L = −[y·log ŷ + (1 − y)·log(1 − ŷ)]; phạt nặng khi mô hình đoán chắc mà sai | y = 1 với lượt mua, y = 0 với mẫu âm; cộng điều chuẩn L2 |
| BPR | Học theo cặp: món đã mua phải có điểm cao hơn món chưa mua, tối đa hoá σ(x̂ᵤᵢ − x̂ᵤⱼ) | BPR-MF; cách học trọng số của Hybrid-CBCF. NeuMF-F giữ BCE như NeuMF gốc để so trực tiếp với NeuMF |
| Lấy mẫu âm | Phản hồi ẩn chỉ có món đã mua; "chưa mua" không có nghĩa là không thích, nên lấy ngẫu nhiên vài món chưa mua làm nhãn 0 | 8 mẫu âm mỗi lượt mua, chỉ trong sản phẩm đã ra mắt, lấy lại mỗi epoch |
| Adam | Tối ưu theo gradient, tự điều chỉnh bước học cho từng tham số | Tốc độ học 0,001, lô 512 |
| Dừng sớm | Dừng khi độ đo trên tập xác thực không tăng sau P epoch, giữ trạng thái tốt nhất | NDCG@10 xác thực, P = 5, tối đa 20 epoch |
| k-core lặp | Bỏ khách và sản phẩm có ít hơn k tương tác, lặp lại đến khi mọi khách và sản phẩm còn lại đều có ít nhất k | k = 10 (H&M), 5 (Amazon), chỉ trên dữ liệu trước mốc kiểm thử |
| TF-IDF + SVD | TF-IDF cho trọng số cao với từ xuất hiện nhiều trong một mô tả nhưng hiếm trong cả danh mục; SVD rút gọn nén vector còn ít chiều | Từ đơn và cặp từ, giữ tối đa 30.000 mục từ, nén còn 64 chiều, chuẩn hoá độ dài 1 |
| Độ giống cosine | cos(a, b) = a·b / (‖a‖·‖b‖) | ItemKNN, UserKNN trên vector lịch sử mua; Content trên vector nội dung |
| Kiểm định Wilcoxon dấu hạng ghép cặp | Kiểm định phi tham số trên hiệu từng cặp: xếp hạng trị tuyệt đối của các hiệu rồi so tổng hạng của hiệu dương với hiệu âm | Mỗi khách cho một hiệu NDCG@10 (trung bình 5 seed) giữa hai mô hình. Không dùng t-test vì ở mỗi lần chạy khoảng 85% khách có NDCG@10 = 0 (HR@10 khoảng 15%), phân phối rất lệch |
| Giá trị p | Xác suất thấy chênh lệch ít nhất lớn như vậy nếu thật ra hai mô hình như nhau | So với 0,05 sau hiệu chỉnh Holm |
| Hiệu chỉnh Holm | Càng làm nhiều phép so sánh càng dễ có kết luận sai do ngẫu nhiên. Holm sắp các p tăng dần, so p nhỏ nhất với 0,05/10, p kế tiếp với 0,05/9…, dừng ở lần đầu không đạt. Cách này giữ xác suất có ít nhất một kết luận sai trong cả họ dưới 5%, nhưng ít khắt khe hơn Bonferroni (mọi p so với 0,05/10) | Họ 10 so sánh; hai so sánh với Hybrid-CBCF hiệu chỉnh riêng |
| Khoảng tin cậy bootstrap | Lấy mẫu lại có hoàn lại danh sách khách 10.000 lần, mỗi lần tính trung bình hiệu; khoảng 95% là phân vị 2,5% và 97,5% | Khoảng không chứa 0 thì chênh lệch có hướng rõ |
| Xếp hạng toàn bộ | Chấm mọi sản phẩm ứng viên thay vì 100 món lấy mẫu; Krichene và Rendle (2020) chỉ ra lấy mẫu có thể đảo ngược kết luận "A tốt hơn B" | Khoảng 6.710 ứng viên mỗi khách |
| Độ phủ | Tỉ lệ sản phẩm có mặt trong top-10 của ít nhất một khách | Phải xem cùng độ chính xác (Random phủ 98,9%) |

HR, Precision, Recall, NDCG và ví dụ tính tay: câu 5.3.5.

### 5.8 Nhóm, quá trình và công cụ

**5.8.1 "Mỗi em làm phần nào?"** (gần như chắc chắn bị hỏi)
Theo tệp `Kế hoạch phân công tiến độ DACNTT.xlsx`:

| Mảng việc | Yến Linh | Minh Lý |
|---|---|---|
| Lý thuyết, đề cương | MF, BPR, NCF/NeuMF; xác định bài toán Top-K; Chương 1–2 | Khảo sát dữ liệu và độ đo; kế hoạch thực nghiệm |
| Dữ liệu | Đọc H&M, lấy mẫu theo khách, chia theo thời gian, lọc k-core trước mốc kiểm thử, xây dựng đặc trưng; gộp theo mẫu thiết kế; chọn Amazon Beauty và lập kế hoạch kiểm chứng | — |
| Mô hình | Thiết kế NeuMF-F và LateFusion-F; Hybrid-CBCF | Cài đặt GMF, MLP, NeuMF và các mô hình đối chứng |
| Đánh giá | — | Mô-đun xếp hạng toàn bộ; quy trình đánh giá (kế hoạch, tinh chỉnh, khoá tập kiểm thử); chạy đánh giá cuối 5 seed trên H&M và Amazon |
| Báo cáo, trình bày | Chương 1–3, sơ đồ, văn phong; trình bày tổng quan, lý thuyết, dữ liệu, mô hình | Chương 4, phần Amazon, kiểm số liệu, hình kết quả; demo, slide, poster; trình bày thực nghiệm, kết quả, demo |

Cách trả lời: mỗi bạn nói phần mình làm chính trong hai, ba câu, rồi nói phần cả nhóm cùng làm (rà soát báo cáo, chuẩn
bị bảo vệ). Hội đồng hay hỏi chéo, ví dụ hỏi Yến Linh về kiểm định hay hỏi Minh Lý về đặc trưng, để xem ai cũng hiểu
toàn đề tài, nên cả hai cần thuộc Phần 0 và 0.3. Khi bạn kia đang trả lời thì không chen ngang; cần bổ sung thì xin
phép nói sau. Gợi ý ai trả lời trước: câu về dữ liệu, đặc trưng, kiến trúc, Hybrid-CBCF, lý thuyết là Yến Linh; câu về
đánh giá, kiểm định, kết quả H&M và Amazon, demo là Minh Lý.

**5.8.2 "Các mô hình tự cài đặt hay dùng thư viện có sẵn?"**
Nhóm tự cài đặt mọi mô hình trên các thư viện nền, không dùng thư viện khuyến nghị dựng sẵn:
- Các mạng lưới thần kinh (GMF, MLP, NeuMF và ba mô hình có đặc trưng) viết bằng PyTorch.
- BPR-MF viết bằng NumPy, tự cập nhật theo cặp bằng SGD (`src/baselines/classical.py`).
- ItemKNN, UserKNN viết trên ma trận thưa của SciPy: tính cosine, giữ k láng giềng, hệ số co
  (`src/baselines/neighborhood.py`).
- Content, hai mô hình phổ biến, LateFusion-F và Hybrid-CBCF cũng do nhóm viết.
- Phần dùng thư viện: TF-IDF và SVD rút gọn của scikit-learn, kiểm định Wilcoxon của SciPy. Bootstrap và hiệu chỉnh
  Holm do nhóm viết (`scripts/7_report.py`).
- Demo: API bằng FastAPI, giao diện HTML và JavaScript thuần, biểu đồ bằng Chart.js.

**5.8.3 "Làm sao biết mã nguồn chạy đúng?"**
- Có 110 bài kiểm thử tự động cho dữ liệu, mô hình và đánh giá, cộng 21 bài cho demo. Ví dụ: mẫu âm chỉ gồm sản phẩm
  đã ra mắt và không trùng món khách đã mua; các màu của cùng một mẫu thiết kế được gộp đúng; trang kết quả của demo khớp
  từng số với báo cáo.
- Số trong báo cáo không gõ tay mà sinh tự động từ tệp kết quả; có công cụ đối chiếu câu chữ của báo cáo với số liệu
  (`python run.py check-report`).
- Dữ liệu đã lọc của mỗi mẫu được ghi ra một tệp có kiểm MD5, mọi mô hình đọc cùng tệp đó.

**5.8.4 "Chạy trên máy nào, mất bao lâu?"**
Đánh giá cuối trên H&M và Amazon chạy trên cùng một laptop: CPU AMD Ryzen 7 6800H, GPU RTX 3050 Laptop. NeuMF-F mất
trung bình 15,2 phút mỗi seed trên H&M và 4,1 phút trên Amazon; toàn bộ đánh giá cuối H&M mất khoảng 7,5 giờ cho 5
seed. Demo chạy được trên laptop chỉ có CPU (Intel Core i5-1135G7).

**5.8.5 "Khó khăn lớn nhất là gì, nhóm giải quyết thế nào?"**
Chọn hai, ba ý, nói theo mẫu "gặp gì → làm gì → được gì":
1. Bộ nhớ: xếp hạng toàn bộ trên dữ liệu đầy đủ là hàng chục tỷ cặp cho mỗi mô hình; ngay với k = 5 trên mẫu phát
   triển đã cần khoảng 10,7 GB. → Lấy mẫu theo khách bằng hàm băm và lọc 10-core, vẫn giữ trọn lịch sử 2 năm của mỗi
   khách.
2. Cách chia leave-one-out lọt thông tin tương lai (11,2% tương tác huấn luyện xảy ra sau món kiểm thử). → Chia theo
   một mốc thời gian chung, đặc trưng tính theo thời điểm.
3. Ở khảo sát ban đầu, NeuMF chỉ dùng ID không vượt BPR-MF đã tinh chỉnh. → Bổ sung thông tin thay vì thêm tham số, từ
   đó có NeuMF-F.
4. Phải thử nhiều cấu hình mà vẫn giữ kết luận khách quan. → Cố định kế hoạch trước, tinh chỉnh trên mẫu phát triển,
   mở tập kiểm thử đúng một lần.
5. Tệp vector văn bản dựng trên hai máy hơi khác nhau do khác phiên bản thư viện. → Demo hiện số đã lưu của đánh giá
   cuối và báo khi thứ hạng tính trên máy đang chạy bị lệch (Phần 7).

Bài học chung: dữ liệu và cách đánh giá quyết định độ tin cậy của kết luận nhiều hơn độ phức tạp của mạng.

**5.8.6 "Nhóm có dùng công cụ AI (ChatGPT, Claude…) không?"**
Nói thật và đúng mức đã dùng. Nếu đã dùng mà phủ nhận, khi bị hỏi vặn sẽ mất điểm nặng hơn nhiều so với thừa nhận
ngay. Ý trả lời gợi ý, cần sửa cho khớp thực tế của nhóm: "Có. Nhóm dùng trợ lý AI để hỗ trợ viết mã, tìm lỗi và chỉnh
câu chữ báo cáo. Các lựa chọn chính như dữ liệu, cách chia, nhóm mô hình đối chứng được thống nhất với cô qua các buổi
họp. Mọi số liệu đến từ mã chạy thật, có kiểm thử tự động, và lịch sử git ghi lại toàn bộ quá trình. Nhóm hiểu và giải
thích được từng phần." Cách chứng minh tốt nhất là trả lời vững các câu kỹ thuật ở Phần 0. Nếu khoa có quy định khai
báo việc dùng AI thì làm theo; báo cáo hiện chưa có dòng khai báo, nên hỏi cô trước buổi bảo vệ.

**5.8.7 "Dữ liệu lấy ở đâu, có vấn đề quyền riêng tư không?"**
H&M là bộ dữ liệu công khai của cuộc thi H&M Personalized Fashion Recommendations trên Kaggle (2022); mã khách là chuỗi
đã băm, không có tên hay địa chỉ, và nhóm không dùng mã bưu chính, giá, kênh bán. Amazon Beauty thuộc bộ dữ liệu đánh
giá sản phẩm Amazon năm 2014 do McAuley và cộng sự công bố cho nghiên cứu. Nhóm dùng cả hai cho mục đích học tập. Ảnh
sản phẩm chỉ hiển thị trong demo, không đưa vào mô hình. Mở: mục 3.2.1, 4.4.1.

**5.8.8 "Đề tài khác gì luận án của cô?"**
Luận án của cô hệ thống hoá hợp nhất sớm, hợp nhất muộn và việc thêm nguồn thông tin ngoài ma trận tương tác, cho bài
toán dự đoán điểm đánh giá, đo bằng độ đo sai số. Đề tài dùng khung hợp nhất đó cho một bài toán khác: phản hồi ẩn
(mua hay không mua), khuyến nghị Top-K, đo bằng độ đo xếp hạng, trên họ mô hình NCF, chia dữ liệu theo thời gian.
Hybrid-CBCF làm theo chương 3 của luận án, nhưng học trọng số theo cặp vì không có điểm đánh giá (câu 5.5.3). Mở: mục
2.6, Bảng 2.1.

**5.8.9 "Nếu làm lại, nhóm sẽ làm khác điều gì?"**
Nêu hai, ba việc cụ thể, không tự hạ kết quả: lưu mã kiểm MD5 cho cả tệp đặc trưng ngay từ đầu để kết quả tái lập tuyệt
đối trên mọi máy; đưa Factorization Machines dùng cùng đặc trưng vào danh sách đối chứng từ đầu; dành một phần đánh giá
riêng cho sản phẩm vừa ra mắt.

**5.8.10 "Báo cáo kiểm trùng lặp được bao nhiêu phần trăm? Những đoạn nào trùng?"**
Lần kiểm Turnitin gần nhất (bản ngày 25/11/2026) cho chỉ số tương đồng 10%. Trong đó nguồn internet 8%, ấn phẩm 6%, bài
nộp của sinh viên 6%; không nguồn nào quá 2%:
- Nguồn lớn nhất (2%) là các bài nộp tại Trường Đại học Tôn Đức Thắng. Phần trùng nằm ở trang bìa, trang cam đoan, mẫu
  xác nhận của giảng viên và tên các mục trong mục lục. Các trang này theo mẫu chung của Trường.
- Hai nguồn kế tiếp (mỗi nguồn 1%) trùng ở tên đề tài và các cụm thuật ngữ quen thuộc như "hệ thống khuyến nghị", "mô
  hình đối chứng", "khác biệt có ý nghĩa".
- Mỗi nguồn còn lại dưới 1%: cụm thuật ngữ, tên độ đo, tên cột bảng, và danh mục tài liệu tham khảo. Lần kiểm không bật
  loại trừ trích dẫn và tài liệu tham khảo, nên các mục tài liệu tham khảo cũng bị tính.
- Số liệu của bài báo trong Bảng 2.1 khớp với nguồn vì đó là số trích có ghi nguồn.

Không có đoạn nào trong thân bài trùng liền nhiều câu với một nguồn khác. Từ bản kiểm đến bản nộp cuối, nhóm chỉ sửa câu
chữ, bỏ chỗ lặp ý và sửa định dạng, không viết lại câu để hạ tỉ lệ trùng.

Nếu hỏi tiếp "Có dùng công cụ viết lại câu để né kiểm tra không?": nói "Không". Nối sang câu 5.8.6: nhóm hiểu và giải
thích được từng phần, lịch sử git ghi lại toàn bộ quá trình làm.

---

## Phần 6. Câu không được nói

- **Không nói "NeuMF-F tốt nhất".** Nói: "NeuMF-F vượt có ý nghĩa các mô hình đối chứng không dùng chung bộ đặc trưng;
  nhóm mô hình có đặc trưng dẫn đầu."
- **Không nói "NeuMF-F không thua mô hình nào"** mà không nói rõ là trên H&M (trên Amazon LateFusion-F tốt hơn).
- **Không nói "LateFusion-F ổn định hơn"** (sai trên H&M: độ lệch chuẩn 0,00212 so với 0,00147 của NeuMF-F) **hay
  "LateFusion-F không phải mô hình lai"** (nó là lai theo kiểu hợp nhất muộn). Xem Phần 0, Câu 1 (f).
- **Không nói đề tài giải quyết cold start của sản phẩm.** Khách mới: có xử lý (gợi ý phổ biến), nhưng không đánh giá
  định lượng.
- **Không nói NeuMF-F "học được sản phẩm mới nhờ bỏ ID ngẫu nhiên"** (cấu hình cuối có ρ = 0).
- **Không so số của đề tài với số trong bài báo** (khác dữ liệu, cách chia, số ứng viên). Bảng 2.1 chỉ để thấy thiết lập
  khác nhau.
- **Không gọi MLP đứng riêng là hợp nhất sớm** (đó là mạng DNN thuần).
- **Không dùng hai so sánh có BPR-MF trên Amazon làm bằng chứng.**
- **Không tính Hybrid-CBCF vào "14 mô hình" hay họ 10 so sánh.**
- **Không nói "sản phẩm mới" khi ý là món khách mua lần đầu.** Nói "món khách chưa từng mua"; "sản phẩm mới" dễ bị hiểu
  là hàng vừa ra mắt, vốn nằm ngoài phạm vi đánh giá (0.2, slide 5).
- **Không nói "NeuMF-F dùng dropout"** (cấu hình chọn có dropout = 0, câu 5.2.6).
- **Không phủ nhận việc dùng công cụ AI nếu nhóm có dùng** (câu 5.8.6).
- **Không nói "báo cáo không trùng gì" hay "đã chỉnh để giảm trùng lặp".** Nói đúng con số 10% và giải thích các nguồn
  trùng (câu 5.8.10).
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

Lưu ý:
- Ảnh sản phẩm nằm ở `neumf_project/demo/static/images/` (không có trong git). Máy chưa có ảnh thì demo hiện ô màu ghi
  loại sản phẩm thay ảnh, vẫn chạy bình thường. Ảnh H&M tải bằng `demo/scripts/download_hm_images.py` hoặc chép từ máy
  đã có ảnh.
- Tệp đặc trưng `data/processed/hm/catalog_v2.npz` và `data/processed/amazon/catalog.npz` không có trong git. Trên máy
  khác máy GPU, hạng tính lại của bốn mô hình có đặc trưng lệch hạng đã lưu ở gần như mọi khách (đo 09/11 trên máy CPU:
  39–40/40 khách H&M, NeuMF chỉ dùng ID khớp 40/40); khi đó demo hiện số đã lưu kèm dòng "Thứ hạng trên máy này lệch với
  số đã lưu…". Khách ví dụ (nút "Xem ví dụ") được chọn trong số khách khớp, nên trên máy CPU vẫn
  trúng ở vị trí 3 và 6 như Hình 3.7, nhưng thứ tự các món không trúng (vị trí 7–10) khác ảnh trong báo cáo. Nếu hội đồng hỏi: số trong báo cáo là số đã lưu của đánh giá cuối; vector văn bản
  dựng lại bằng phiên bản thư viện khác nên lệch. Muốn tránh thì demo trên máy GPU hoặc chép hai tệp này từ máy GPU sang.
- Số hạng và độ đo của từng khách trong demo là của seed 42, có thể khác đôi chút so với trung bình 5 seed trong báo cáo.

---

## Phần 8. Tra nhanh báo cáo

| Chương | Mục chính | Bảng, hình, thuật toán |
|---|---|---|
| 1. Tổng quan | 1.1 bối cảnh (1.1.3 ba câu hỏi nghiên cứu); 1.2 mục tiêu, phạm vi; 1.3 phương pháp; 1.4 ý nghĩa; 1.5 bố cục | Hình 1.1 các bước thực hiện |
| 2. Cơ sở lý thuyết | 2.1 hệ gợi ý; 2.2 MF, BPR; 2.3 NCF, hợp nhất; 2.4 mô hình lai dựa trên đặc trưng; 2.5 độ đo; 2.6 ba nghiên cứu nền tảng; 2.7 khoảng trống | Hình 2.1 NeuMF, Hình 2.2 hợp nhất; Bảng 2.1 |
| 3. Phương pháp | 3.1 đường ống; 3.2 dữ liệu; 3.3 NeuMF-F; 3.4 đối chứng; 3.5 lấy mẫu âm, BCE; 3.6 tinh chỉnh; 3.7 đánh giá (khảo sát ban đầu, sáu nguyên tắc); 3.8 suy luận, khách mới; 3.9 demo | Hình 3.1 đường ống, 3.2 xử lý dữ liệu, 3.3 chia theo thời gian, 3.4 NeuMF-F, 3.5 tinh chỉnh và đánh giá cuối, 3.6 kiến trúc demo, 3.7–3.10 giao diện demo (cửa hàng, thẻ sản phẩm và khách có gu giống, khách mới, kết quả); Bảng 3.1–3.7 (3.7: số đo demo); Thuật toán 3.1–3.7 |
| 4. Thực nghiệm | 4.1 thiết lập thực nghiệm; 4.2 tinh chỉnh; 4.3 kết quả H&M (4.3.1 chính, 4.3.2 theo K, 4.3.3 kiểm định, 4.3.4 Hybrid-CBCF, 4.3.5 bóc tách, 4.3.6 độ phủ, 4.3.7 độ ổn định giữa hai mẫu); 4.4 Amazon; 4.5 nguồn gốc của phần cải thiện; 4.6 phạm vi; 4.7 trả lời ba câu hỏi nghiên cứu | Bảng 4.1 điều kiện chung, 4.2–4.10 (H&M), 4.11–4.19 (Amazon), 4.20 các yếu tố đã loại trừ; Hình 4.1–4.4 (H&M) |
| 5. Kết luận | 5.1 kết quả đạt được; 5.2 kết luận; 5.3 hạn chế; 5.4 hướng phát triển | Bảng 5.1 mức độ hoàn thành mục tiêu |

Thuật toán: 3.1 chuẩn bị dữ liệu và k-core · 3.2 lấy mẫu âm · 3.3 huấn luyện, huấn luyện lại · 3.4 xếp hạng toàn bộ ·
3.5 trọng số LateFusion-F · 3.6 cách kết hợp Hybrid-CBCF · 3.7 suy luận Top-K có xử lý khách mới.

Công thức trong báo cáo không đánh số, vì không chỗ nào dẫn lại công thức bằng số. Khi hội đồng hỏi "công thức … ở
đâu", chỉ theo mục:

| Công thức | Mục |
|---|---|
| Độ tương đồng cosine, điểm của ItemKNN và UserKNN | 2.1.2 |
| Phản hồi ẩn nhị phân $y_{ui}$ | 2.1.3 |
| MF: tích vô hướng $p_u^T q_i$ | 2.2.1 |
| Hàm mất mát BPR | 2.2.3 |
| GMF, MLP, NeuMF | 2.3.1, 2.3.2, 2.3.3 |
| Hợp nhất sớm, hợp nhất muộn; trộn điểm có chuẩn hoá min–max (LateFusion-F) | 2.3.4 |
| Entropy chéo nhị phân (BCE) | 2.3.5 |
| HR@K, Precision@K, Recall@K, NDCG@K | 2.5 |
| Độ phủ Coverage@K | 2.5.2 |
| Tập huấn luyện, tập ứng viên, sản phẩm mục tiêu theo mốc $\tau$ | 3.2.4 |
| Đặc trưng thời gian của sản phẩm (doanh số 7, 28, 91 ngày) | 3.2.5 |
| Vector lai: mã ID cộng phần chiếu đặc trưng | 3.3.1 |
| GMF-F, MLP-F, lớp dự đoán của NeuMF-F | 3.3.2, 3.3.3, 3.3.4 |
| Hàm mất mát cuối: BCE cộng điều chuẩn $L_2$ | 3.5.2 |

Bằng chứng trong mã nguồn (chỉ mở khi hội đồng yêu cầu): kế hoạch đăng ký trước `neumf_project/audit/PREREG_v2.md`,
`PREREG_amazon.md`, `PREREG_bosung.md`; nhật ký mở tập kiểm thử `neumf_project/audit/test_access_log.csv`; kết quả
`neumf_project/outputs/`; mô hình `neumf_project/src/models/hybrid_features.py`.

---

## Phần 9. Buổi hỏi đáp mô phỏng (lời nói mẫu để luyện, soạn 26/11/2026)

Khoảng 15 phút, theo thứ tự hội đồng hay hỏi: Chủ tịch hỏi tổng quan, Giảng viên phản biện xoáy vào kết quả và phương
pháp, Ủy viên hỏi kiến thức nền, demo và thực tiễn. Mỗi đáp án ghi người nên trả lời trước theo phân công (5.8.1). Cách
luyện: đọc câu hỏi, che đáp án, tự nói thành tiếng trong 45–60 giây rồi mới so. Số liệu giống Phần 0–5.

### Vòng 1 — Chủ tịch hội đồng: đề tài và đóng góp

**Hỏi 1.** *"Các em cho hội đồng biết đóng góp mới của đề tài là gì. NeuMF có từ năm 2017 rồi mà."*

> **Yến Linh:** Dạ, NeuMF gốc chỉ học từ mã khách và mã sản phẩm. Nhóm em có ba đóng góp. Thứ nhất, nhóm xây dựng
> NeuMF-F, đưa đặc trưng sản phẩm, khách hàng và thời gian vào cả hai nhánh GMF và MLP; đặc trưng tính theo đúng thời
> điểm nên không dùng thông tin tương lai. Thứ hai, NeuMF-F tốt hơn có ý nghĩa thống kê NeuMF chỉ dùng ID, hơn 43,8%
> NDCG@10 trên H&M và 65,7% trên Amazon Beauty, và tốt hơn mọi mô hình đối chứng không dùng chung bộ đặc trưng, kể cả
> mô hình lai truyền thống Hybrid-CBCF. Thứ ba, nhóm chỉ ra phần cải thiện đến từ đặc trưng, trong đó đặc trưng thời
> gian quan trọng nhất.

*Hỏi vặn:* "Vậy cái mới chỉ là thêm đặc trưng vào NeuMF? Có đơn giản quá không?"

> Dạ, nhóm giữ gần nguyên kiến trúc là có chủ ý: NeuMF-F chỉ khác NeuMF ở đầu vào, nên so hai mô hình là đo đúng giá
> trị của đặc trưng. Phần khó nằm ở chỗ làm cho đúng: đặc trưng phải tính tại thời điểm mua, mẫu âm chỉ lấy trong sản
> phẩm đã ra mắt, đánh giá không được rò rỉ. Kết quả cũng có ích cho doanh nghiệp: muốn khuyến nghị tốt hơn thì nên đầu
> tư vào dữ liệu đặc trưng trước khi làm mạng sâu hơn.

**Hỏi 2.** *"Tên đề tài là mô hình lai kết hợp MF và DNN. Em chỉ vào hình xem lai ở chỗ nào."*

> **Yến Linh:** Dạ, lai ở hai mức. Mức thứ nhất là lai MF với DNN. Nhánh GMF-F là nhân tử hoá ma trận dạng tổng quát,
> nhân từng phần tử hai vector để học tương tác tuyến tính. Nhánh MLP-F đưa hai vector qua các lớp 64, 32, 16, 8 để học
> tương tác phi tuyến. Hai nhánh nối thành vector 40 chiều, qua một lớp dự đoán chung và học chung trong một mạng; đó là
> hợp nhất sớm. Mức thứ hai là lai thông tin cộng tác với thông tin nội dung: vector của mỗi khách, mỗi sản phẩm là vector
> nhúng ID cộng với phép chiếu của đặc trưng, tức ô màu cam trên hình.

*Hỏi vặn:* "Đặc trưng được nối vào hay cộng vào? Sao lại cộng?"

> Dạ, cộng. Đặc trưng sản phẩm 157 chiều được nhân với ma trận chiếu cỡ 32 × 157 để về 32 chiều, rồi cộng vào vector ID;
> đặc trưng khách 42 chiều cũng làm như vậy. Cộng thì giữ nguyên số chiều, nên toàn bộ phần phía sau của NeuMF không phải
> đổi.

**Hỏi 3.** *"Sao em chọn NeuMF mà không dùng Transformer hay mạng đồ thị?"*

> **Yến Linh:** Dạ, có ba lý do. H&M chỉ ghi ngày mua, không có phiên truy cập, nên mô hình chuỗi khó tận dụng. Dữ liệu
> có sẵn thuộc tính, mô tả và doanh số, hợp với cách cộng đặc trưng vào vector ID. Cấu trúc hai nhánh tường minh cho phép
> tách đóng góp của từng phần bằng so sánh trực tiếp, đúng với ba câu hỏi nghiên cứu. Các mô hình mới hơn là hướng phát
> triển, và quy trình đánh giá của nhóm dùng lại được nguyên.

### Vòng 2 — Giảng viên phản biện: kết quả bất lợi

**Hỏi 4.** *"Bảng của các em cho thấy LateFusion-F cao nhất trên cả hai bộ, trên Amazon còn hơn NeuMF-F có ý nghĩa. Vậy
các em đề xuất một mô hình kém hơn à?"* (câu trọng tâm; bản đầy đủ và 10 câu hỏi vặn ở Phần 0, Câu 1)

> **Minh Lý:** Dạ, đề tài đặt mục tiêu xây dựng một mô hình lai, trong đó MF và DNN được ghép và học chung trong một
> mạng. NeuMF-F là mô hình đó, và được xác định là mô hình đề xuất ngay từ kế hoạch, trước khi có kết quả. LateFusion-F
> gồm hai mô hình huấn luyện riêng rồi trộn điểm; nhóm đưa vào để trả lời câu hỏi nên hợp nhất sớm hay muộn. Kết quả:
> trên H&M hai cách không khác biệt có ý nghĩa; trên Amazon NeuMF-F thấp hơn 12,5%. Đổi lại, NeuMF-F chỉ có một mạng,
> thời gian huấn luyện bằng khoảng một nửa hoặc ít hơn, và danh sách khuyến nghị đa dạng hơn. LateFusion-F được ghép từ
> chính hai nhánh có đặc trưng của NeuMF-F, nên nó mạnh cũng là nhờ đặc trưng mà đề tài xây dựng.

*Hỏi vặn:* "Vậy nếu doanh nghiệp hỏi nên dùng mô hình nào thì em trả lời sao?"

> Dạ, chọn theo dữ liệu và chi phí. NeuMF-F chỉ huấn luyện một mạng, 15,2 phút mỗi seed trên H&M so với 30,1 phút của
> LateFusion-F, và độ phủ danh mục cao hơn, 13,3% so với 5,3%. LateFusion-F có NDCG@10 cao hơn, rõ nhất trên Amazon, và
> chỉnh được trọng số trộn mà không phải huấn luyện lại.

**Hỏi 5.** *"NeuMF-F ngang GMF-F, tức nhánh MLP gần như không thêm gì. Phần DNN trong tên đề tài còn ý nghĩa gì?"*

> **Minh Lý:** Dạ, nhóm em thừa nhận: ở quy mô này, nhánh MLP-F chưa thêm khác biệt có ý nghĩa so với GMF-F (hơn 2,6%
> trên H&M, kém 0,6% trên Amazon). Câu hỏi nghiên cứu thứ ba được đặt ra chính để đo điều này, và câu trả lời là một
> phát hiện: khi đã có đặc trưng, biểu diễn có đặc trưng quyết định nhiều hơn cách ghép hai nhánh. Ghép hai nhánh cũng
> không làm mất gì: trên H&M, NeuMF-F hơn MLP-F 15,0% có ý nghĩa và có độ phủ top-10 cao nhất trong các mạng lưới thần
> kinh.

*Hỏi vặn:* "Sao không so với Factorization Machines dùng cùng đặc trưng? Biết đâu FM cũng đạt như vậy."

> Dạ, đó là hạn chế nhóm đã ghi ở phần hạn chế và hướng phát triển; phạm vi đề tài là họ NeuMF. Nhánh GMF-F có đặc trưng
> về bản chất gần với FM: tích của hai vector có chứa đặc trưng đã mô hình hoá tương tác giữa thuộc tính khách và thuộc
> tính sản phẩm. Hai đối chứng không phải mạng lưới thần kinh mà có dùng nội dung là Content và Hybrid-CBCF, và NeuMF-F
> tốt hơn có ý nghĩa cả hai, trên cả hai bộ.

**Hỏi 6.** *"Phân tích bóc tách chỉ chạy một seed. Sao dám kết luận đặc trưng thời gian quan trọng nhất?"*

> **Minh Lý:** Dạ, báo cáo ghi rõ bóc tách là phân tích mô tả, không qua kiểm định đa so sánh. Nhưng mức giảm rất lớn:
> bỏ đặc trưng thời gian thì NDCG@10 từ 0,04137 xuống 0,02386, giảm 42,3%, gấp khoảng 12 lần độ lệch chuẩn giữa 5 seed
> của NeuMF-F. Khoảng tin cậy bootstrap không chứa 0, và kết quả lặp lại trên Amazon với mức giảm 31,6%. Với thuộc tính
> và văn bản trên H&M, khoảng tin cậy chứa 0, nên nhóm nói là chưa khẳng định được.

*Hỏi vặn:* "Bỏ đặc trưng là đặt bằng 0 lúc dự đoán hay huấn luyện lại?"

> Dạ, huấn luyện lại một mô hình riêng không có nhóm đặc trưng đó, giữ nguyên siêu tham số và quy trình của NeuMF-F.

### Vòng 3 — Giảng viên phản biện: phương pháp đánh giá

**Hỏi 7.** *"Đề tài khuyến nghị hay bị rò rỉ dữ liệu. Sao em chắc là không? Bài NCF chia leave-one-out, sao em không làm
vậy?"*

> **Yến Linh:** Dạ, nhóm có bốn lớp bảo vệ. Một, dữ liệu chia theo một mốc thời gian chung: huấn luyện trước 01/07/2020,
> xác thực 4 tuần, kiểm thử 8 tuần cuối. Hai, lọc 10-core chỉ trên dữ liệu trước mốc kiểm thử. Ba, đặc trưng tại ngày t
> chỉ dùng dữ liệu đến ngày t − 1. Bốn, kết luận lấy trên mẫu kiểm định, gồm những khách hàng khác hẳn mẫu dùng để tinh
> chỉnh. Leave-one-out thì lọt tương lai: đo trên mẫu phát triển, trung bình 11,2% tương tác huấn luyện của mỗi khách xảy
> ra sau ngày của món kiểm thử.

*Hỏi vặn:* "Tệp customers.csv không có mốc thời gian, vậy cũng là thông tin tương lai chứ?"

> Dạ, đúng là tệp này là một ảnh chụp không ghi thời điểm, và báo cáo nói rõ nhóm coi các thuộc tính này là ít thay đổi.
> Đó là nhóm tuổi, trạng thái hội viên, tần suất nhận tin; không thuộc tính nào cho biết khách sẽ mua gì. Trên Amazon
> không có thuộc tính khách nào, mà kết luận về đặc trưng vẫn giữ.

**Hỏi 8.** *"So sánh có công bằng không, hay các em tinh chỉnh kỹ mô hình của mình hơn?"*

> **Minh Lý:** Dạ, mọi mô hình, kể cả NeuMF-F, có cùng ngân sách 6 cấu hình, chọn theo NDCG@10 trên cùng tập xác thực
> của mẫu phát triển, rồi được đánh giá với cùng tập ứng viên, cùng 5 seed và cùng mã đánh giá. Kết luận "A tốt hơn B"
> phải đủ ba điều kiện: p sau hiệu chỉnh Holm dưới 0,05, khoảng tin cậy bootstrap không chứa 0, và chênh lệch ít nhất 5%.
> Kế hoạch so sánh được ghi lại trước khi đánh giá trên tập kiểm thử, và tập kiểm thử chỉ mở một lần; nhóm có nhật ký nếu
> hội đồng muốn xem.

*Hỏi vặn:* "NeuMF-F lấy mẫu âm theo ngày ra mắt, còn NeuMF lấy đều. Biết đâu phần hơn 43,8% là do cách lấy mẫu?"

> Dạ, nhóm đã kiểm điều này. Biến thể bóc tách bỏ đặc trưng thời gian vẫn lấy mẫu âm đúng như NeuMF-F, vậy mà NDCG@10
> vẫn giảm 42,3%. Như vậy phần lớn chênh lệch đến từ đặc trưng. NeuMF lấy mẫu đều như NCF gốc vì mô hình chỉ dùng ID không
> nhận ngày làm đầu vào.

*Hỏi vặn tiếp:* "Amazon dùng lại siêu tham số của H&M, như vậy có thiệt cho đối chứng không?"

> Dạ, quy định này áp dụng cho cả 14 mô hình, kể cả NeuMF-F, và được ghi trong kế hoạch trước khi chạy Amazon. Mục đích là
> xem kết luận có giữ khi đổi dữ liệu mà không chỉnh theo dữ liệu mới; trên Amazon chỉ chọn số epoch. BPR-MF có cấu hình
> không hợp Amazon, nên nhóm không dùng so sánh với nó làm bằng chứng. Bỏ BPR-MF ra, NeuMF-F vẫn hơn đối chứng mạnh nhất
> là UserKNN 30,8%.

**Hỏi 9.** *"NDCG@10 chỉ khoảng 0,04, Precision@10 chưa tới 2%. Kết quả như vậy có dùng được không?"*

> **Minh Lý:** Dạ, giá trị tuyệt đối thấp vì bài toán khó. Mỗi khách được xếp hạng trên khoảng 6.710 sản phẩm nhưng
> trung bình chỉ có 3,2 món đúng, và chỉ tính những món khách chưa từng mua trong 8 tuần tới. Dù đoán hoàn hảo,
> Precision@10 cũng chỉ khoảng 0,3. So với mốc dưới là Random, NDCG@10 của NeuMF-F cao gấp khoảng 40 lần. Dễ hình dung
> nhất là HR@10 khoảng 15%: cứ 7 khách thì có 1 khách mua thật một món trong 10 khuyến nghị, dù chưa từng thấy danh sách
> đó.

*Hỏi vặn:* "Sao báo cáo bỏ K = 5? Ở K = 5 kết quả xấu à?"

> Dạ không. Hạng của từng món đúng được lưu lại, nên nhóm tính lại được K = 5 mà không phải đánh giá lại. Ở K = 5, thứ
> tự các mô hình giữ nguyên trên cả hai bộ. Nhóm bỏ vì mỗi khách chỉ có khoảng 3 món đúng giữa hàng nghìn ứng viên, danh
> sách 5 món quá ngắn, và độ đo dao động giữa các seed nhiều hơn.

### Vòng 4 — Ủy viên: kiến thức nền, hỏi chéo

Hội đồng hay cố ý hỏi người không trình bày phần đó.

**Hỏi 10.** *"Em Yến Linh giải thích kiểm định Wilcoxon và hiệu chỉnh Holm. Sao không dùng t-test?"*

> **Yến Linh:** Dạ, với mỗi khách, nhóm lấy NDCG@10 trung bình 5 seed của hai mô hình rồi tính hiệu. Wilcoxon dấu hạng
> xếp hạng trị tuyệt đối của các hiệu, rồi so tổng hạng của hiệu dương với hiệu âm; đây là kiểm định ghép cặp, phi tham
> số. Nhóm không dùng t-test vì ở mỗi lần chạy khoảng 85% khách có NDCG@10 bằng 0, phân phối rất lệch. Làm 10 phép so
> sánh thì dễ có kết luận sai do ngẫu nhiên, nên nhóm dùng Holm: sắp các p tăng dần, so p nhỏ nhất với 0,05/10, p kế tiếp
> với 0,05/9, và cứ thế. Cách này giữ xác suất có ít nhất một kết luận sai trong cả họ dưới 5%, nhưng ít khắt khe hơn
> Bonferroni.

*Hỏi vặn:* "Sao kiểm định theo khách mà không theo 5 seed?"

> Dạ, với 5 seed thì p nhỏ nhất của Wilcoxon là 0,0625, không bao giờ xuống dưới 0,05. Kiểm định theo khách dùng được
> hàng nghìn khách. Dao động giữa các seed được báo cáo riêng bằng độ lệch chuẩn.

**Hỏi 11.** *"Em Minh Lý viết hàm mất mát lên bảng. Sao huấn luyện qua sigmoid mà xếp hạng lại dùng logit?"*

> **Minh Lý:** Dạ, nhóm dùng entropy chéo nhị phân, L = −[y·log ŷ + (1 − y)·log(1 − ŷ)], cộng thêm điều chuẩn L2. Mỗi
> lượt mua có nhãn 1; mỗi lượt kèm 8 sản phẩm khách chưa mua, đã ra mắt tại ngày đó, làm mẫu âm với nhãn 0. ŷ là sigmoid
> của logit. Khi xếp hạng, nhóm dùng logit vì sigmoid đồng biến nên không đổi thứ tự, còn với số float32, nhiều điểm lớn
> sau sigmoid thành đúng 1,0 và bị bằng điểm.

*Hỏi vặn:* "Sao không dùng hàm mất mát BPR như BPR-MF?"

> Dạ, NeuMF gốc huấn luyện bằng BCE với mẫu âm. Nhóm giữ nguyên để NeuMF-F chỉ khác NeuMF ở đặc trưng, như vậy so sánh mới
> đo đúng giá trị của đặc trưng. BPR-MF là đối chứng đại diện cho cách học theo cặp.

**Hỏi 12.** *"Mô hình có bị quá khớp không? NeuMF-F hơn NeuMF có phải chỉ vì nhiều tham số hơn?"*

> **Yến Linh:** Dạ, nhóm tinh chỉnh dropout và điều chuẩn L2, và dừng sớm khi NDCG@10 trên tập xác thực không tăng sau 5
> epoch. Cấu hình chọn của NeuMF-F có dropout bằng 0, nên cơ chế chính là dừng sớm: NeuMF-F chọn trung bình 3 epoch, rồi
> được huấn luyện lại từ đầu đúng số epoch đó trước khi đánh giá. Về tham số thì ngược lại: NeuMF chỉ dùng ID chọn d = 64,
> còn NeuMF-F chọn d = 32. Bảng nhúng của NeuMF-F khoảng 0,94 triệu tham số, phần chiếu đặc trưng thêm khoảng 13 nghìn;
> NeuMF khoảng 1,9 triệu. Mô hình nhỏ hơn mà vẫn hơn 43,8%.

### Vòng 5 — Ủy viên: demo và thực tiễn

**Hỏi 13.** *"Khách hàng mới, sản phẩm mới thì sao? Cold start là điểm yếu kinh điển của lọc cộng tác."*

> **Yến Linh:** Dạ, khách chưa có trong dữ liệu sẽ nhận danh sách sản phẩm bán chạy, nên hệ thống luôn có khuyến nghị;
> demo minh hoạ được ngay. Sản phẩm vừa ra mắt nằm ngoài phạm vi đánh giá định lượng: ở quy mô mẫu này, khảo sát ban đầu
> cho NDCG@10 dưới 0,002 ở mọi mô hình, quá nhỏ để so sánh. Về cấu trúc, NeuMF-F đã chấm được một sản phẩm chỉ từ đặc
> trưng, khi không có vector ID; đánh giá riêng phần này là hướng phát triển.

*Hỏi vặn:* "Slide dữ liệu ghi 'khách mua sản phẩm mới', vậy là có đánh giá sản phẩm mới?"

> Dạ, cụm đó chỉ món khách chưa từng mua trước mốc, tức mới với khách đó, không phải hàng vừa ra mắt.

**Hỏi 14.** *"Khách trong demo là em chọn sẵn cho đẹp phải không? Em chọn thử một khách bất kỳ xem."*

> **Minh Lý:** Dạ đúng, nút "Xem ví dụ" chọn khách mà NeuMF-F trúng còn mô hình đối chứng trượt, để minh hoạ. Kết quả
> chung trên 3.165 khách là các bảng nhóm vừa trình bày. Em xin chọn ngay một khách ngẫu nhiên. Nếu NeuMF-F trượt ở khách
> này thì cũng bình thường: HR@10 khoảng 15%, tức phần lớn khách không có món đúng trong 10 khuyến nghị.

*Hỏi vặn:* "Hệ thống phản hồi có nhanh không? Có dùng cơ sở dữ liệu không?"

> Dạ, đo trên laptop chỉ dùng CPU, danh sách Top-10 của NeuMF-F trả về trong trung vị 16,1 ms với H&M và 11,3 ms với
> Amazon. Demo không dùng hệ quản trị cơ sở dữ liệu: dữ liệu đã xử lý, trọng số mô hình và kết quả đánh giá được nạp vào
> bộ nhớ một lần khi khởi động; API FastAPI chỉ làm suy luận.

Lưu ý khi demo: nên chạy trên máy đã chạy đánh giá cuối. Trên máy khác, các mô hình có đặc trưng có thể hiện dòng "thứ
hạng trên máy này lệch với số đã lưu", vì tệp vector văn bản được dựng bằng phiên bản thư viện khác (Phần 7).

**Hỏi 15.** *"Ý nghĩa thực tiễn là gì? Các em mới lấy 1,6% khách, triển khai cho H&M thật được không?"*

> **Minh Lý:** Dạ, mô hình chỉ dùng dữ liệu doanh nghiệp bán lẻ đã có: giao dịch, danh mục, thông tin hội viên, doanh số
> theo ngày. Bài học thực tế là cập nhật doanh số theo thời gian đem lại nhiều hơn làm mạng phức tạp. Nhóm lấy mẫu vì xếp
> hạng toàn bộ trên dữ liệu đầy đủ là hàng chục tỷ cặp cho mỗi mô hình; mẫu lấy theo khách bằng hàm băm và giữ trọn lịch
> sử 2 năm của mỗi khách. Khi triển khai lớn, nhóm đề xuất làm hai bước: dùng mô hình hai tháp kèm tìm lân cận gần đúng
> để lọc ra vài trăm ứng viên, rồi để NeuMF-F xếp hạng lại. Mô hình được huấn luyện lại hằng tuần, hiệu quả đo bằng thử
> nghiệm A/B.

### Vòng 6 — Chủ tịch hội đồng: nhóm và quá trình

**Hỏi 16.** *"Mỗi em làm phần nào trong đề tài?"* (hỏi từng bạn; sửa cho đúng nếu thực tế khác file kế hoạch)

> **Yến Linh:** Dạ, em phụ trách lý thuyết và dữ liệu: đọc dữ liệu H&M, lấy mẫu theo khách, chia theo thời gian, lọc
> k-core, xây dựng đặc trưng. Em thiết kế NeuMF-F, LateFusion-F và Hybrid-CBCF, chọn Amazon Beauty, viết Chương 1 đến 3 và
> vẽ sơ đồ.
>
> **Minh Lý:** Dạ, em phụ trách cài đặt GMF, MLP, NeuMF và các mô hình đối chứng, mô-đun xếp hạng toàn bộ và quy trình
> đánh giá. Em chạy đánh giá cuối 5 seed trên H&M và Amazon, viết Chương 4, làm demo, slide và poster. Cả nhóm cùng rà
> soát báo cáo và chuẩn bị bảo vệ.

**Hỏi 17.** *"Nhóm có dùng ChatGPT hay công cụ AI nào không?"* (sửa cho đúng mức nhóm đã dùng; không phủ nhận nếu có dùng)

> Dạ có. Nhóm dùng trợ lý AI để hỗ trợ viết mã, tìm lỗi và chỉnh câu chữ báo cáo. Các lựa chọn chính như dữ liệu, cách
> chia, nhóm mô hình đối chứng được thống nhất với cô qua các buổi họp. Mọi số liệu đến từ mã chạy thật, có 131 bài kiểm
> thử tự động, và lịch sử git ghi lại toàn bộ quá trình. Nhóm sẵn sàng giải thích bất kỳ phần nào.

**Hỏi 18.** *"Khó khăn lớn nhất là gì? Nếu làm lại em sẽ làm khác điều gì?"*

> **Yến Linh:** Dạ, khó nhất là làm sao để kết luận đáng tin. Ban đầu NeuMF chỉ dùng ID không vượt được BPR-MF đã tinh
> chỉnh, nên nhóm chuyển sang bổ sung thông tin thay vì thêm tham số. Cách chia leave-one-out lọt tương lai, nên nhóm chia
> theo thời gian. Bộ nhớ không đủ để xếp hạng toàn bộ trên dữ liệu đầy đủ, nên nhóm lấy mẫu theo khách. Nếu làm lại, nhóm
> sẽ đưa Factorization Machines dùng cùng đặc trưng vào đối chứng ngay từ đầu, và dành một phần đánh giá riêng cho sản
> phẩm vừa ra mắt.

### Ba lỗi dễ mất điểm khi trả lời

- Trả lời dài: mỗi câu 30–60 giây, nói ý chính trước, số liệu sau.
- Cãi lại hội đồng: thừa nhận ngắn, nêu lý do hoặc thiết kế đã xử lý, rồi quay về điểm mạnh.
- Hai bạn nói lệch số: thống nhất trước các số chính — 43,8%, 65,7%, 42,3%, 31,6%, 28,5%, −2,2% với p Holm 0,735,
  −12,5%, HR@10 khoảng 15%.

---

## Phần 10. Thuyết trình theo từng slide (lời nói mẫu, soạn 27/11/2026)

Lời nói bám đúng chữ và số trên 15 slide hiện tại (`Report DACNTT/slides/Slide_DACNTT.pptx`). Canh giờ cho khoảng 13
phút trình bày, chưa tính khoảng 3 phút demo trực tiếp (Phần 7). Hội đồng cho ít thời gian hơn thì bỏ các câu trong
ngoặc vuông [ ] trước.

Theo phân công ở 5.8.1, Yến Linh nói slide 1–7 (bài toán, mô hình, dữ liệu, quy trình), Minh Lý nói slide 8–15 (kết
quả, demo, kết luận). Mỗi slide chỉ có một thông điệp, nói theo ý chứ không đọc thuộc. Chỉ dùng số đã có trên slide;
các số khác để dành cho lúc được hỏi.

| Slide | Người nói | Thời gian | Thông điệp |
|---|---|---|---|
| 1 Trang bìa | Yến Linh | 0:30 | Giới thiệu nhóm, đề tài, mô hình đề xuất |
| 2 Bối cảnh | Yến Linh | 1:00 | NeuMF chỉ học từ mã ID, bỏ phí thông tin sẵn có |
| 3 Mục tiêu, câu hỏi | Yến Linh | 0:45 | Ba câu hỏi nghiên cứu |
| 4 NeuMF → NeuMF-F | Yến Linh | 1:30 | Phần mới là lớp biểu diễn lai |
| 5 Dữ liệu | Yến Linh | 1:00 | Hai mẫu khách tách rời và một bộ dữ liệu thứ hai |
| 6 Quy trình | Yến Linh | 1:15 | Học trên quá khứ, đánh giá trên tương lai |
| 7 Đối chứng | Yến Linh | 0:45 | Hậu tố -F; mọi mô hình cùng điều kiện |
| 8 Kết quả H&M | Minh Lý | 1:15 | +43,8% so với NeuMF chỉ ID; vượt các đối chứng |
| 9 Kết quả Amazon | Minh Lý | 0:45 | Kết luận lặp lại, không tinh chỉnh lại |
| 10 Đặc trưng | Minh Lý | 0:45 | Đặc trưng thời gian đóng góp nhiều nhất |
| 11 Hợp nhất | Minh Lý | 1:15 | Đánh đổi; cả hai cách đều nhờ đặc trưng |
| 12 Demo: kiến trúc | Minh Lý | 0:30 | Ba tầng, chạy trên máy |
| 13 Demo: giao diện | Minh Lý | 0:30 | Chuyển sang demo trực tiếp |
| 14 Kết luận | Minh Lý | 1:00 | Trả lời ba câu hỏi, đóng góp, hướng phát triển |
| 15 Cảm ơn | Minh Lý | 0:15 | Mời hội đồng đặt câu hỏi |

**Slide 1 (Yến Linh).** "Kính thưa quý thầy cô trong hội đồng. Chúng em là Sử Thị Yến Linh và Lê Minh Lý, thực hiện đề
tài dưới sự hướng dẫn của TS. Hồ Thị Linh. Đề tài của nhóm là xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma
trận và mạng lưới thần kinh sâu. Mô hình đề xuất có tên NeuMF-F. Mô hình được đánh giá trên dữ liệu thời trang H&M và
kiểm chứng trên Amazon Beauty."

**Slide 2.** "Một cửa hàng thời trang trực tuyến có hàng chục nghìn mặt hàng, nhưng mỗi khách chỉ mua vài món, nên ma
trận khách – sản phẩm gần như trống (chỉ vào ma trận). NeuMF kết hợp nhân tử hoá ma trận với mạng nơ-ron, nhưng vẫn chỉ
học từ mã khách và mã sản phẩm. Trong khi đó doanh nghiệp đã có sẵn bốn nhóm thông tin: thuộc tính sản phẩm, mô tả văn
bản, doanh số theo thời gian và thông tin khách hàng. Giải pháp của nhóm là đưa bốn nhóm thông tin này vào cả hai nhánh
của NeuMF." Câu chuyển: "Từ đó nhóm đặt ra mục tiêu và ba câu hỏi nghiên cứu."

**Slide 3.** "Mục tiêu của đề tài là bổ sung đặc trưng vào NeuMF và đánh giá trên hai bộ dữ liệu thực tế. Câu hỏi 1 là
câu hỏi chính: NeuMF-F có khuyến nghị tốt hơn các mô hình đối chứng được tinh chỉnh đầy đủ không. Câu hỏi 2: đặc trưng
có giúp không, và nhóm đặc trưng nào đóng góp nhiều nhất. Câu hỏi 3: ghép hai nhánh có tốt hơn dùng từng nhánh, và nên
hợp nhất sớm hay muộn. Phần kết quả sẽ trả lời lần lượt từng câu."

**Slide 4.** "NeuMF có hai nhánh. Nhánh GMF nhân từng phần tử vector khách với vector sản phẩm, là dạng tổng quát của
nhân tử hoá ma trận. Nhánh MLP nối hai vector rồi đưa qua các lớp ẩn để học tương tác phi tuyến. Hai nhánh được nối trước
một lớp dự đoán chung và cả mạng học chung, gọi là hợp nhất sớm. Phần mới của NeuMF-F là lớp biểu diễn lai (chỉ ô màu
cam): vector của mỗi khách và mỗi sản phẩm bằng vector nhúng mã ID cộng phần chiếu của đặc trưng. Đặc trưng gồm thuộc
tính và mô tả sản phẩm; doanh số 7, 28 và 91 ngày trước cùng tuổi sản phẩm; thông tin khách và số ngày từ lần mua gần
nhất. Tất cả được tính tại đúng thời điểm mua. Mô hình học bằng hàm mất mát BCE, mỗi lượt mua kèm 8 mẫu âm, rồi khuyến
nghị K sản phẩm có điểm cao nhất." [ "Tháp MLP là 64, 32, 16, 8." ]

**Slide 5.** "Bộ H&M có khoảng 31,8 triệu lượt mua, quá lớn để xếp hạng toàn bộ cho mọi mô hình, nên nhóm lấy hai mẫu
khách tách rời. Mẫu phát triển gồm 8.039 khách, chỉ dùng để chọn cấu hình. Mẫu kiểm định gồm 7.994 khách, dùng để kết
luận. Trong 8 tuần kiểm thử có 3.165 khách mua món họ chưa từng mua, và mỗi khách được xếp hạng trên khoảng 6.710 sản
phẩm. Amazon Beauty là bộ thứ hai, thuộc lĩnh vực khác: sau lọc còn 10.681 khách, trong đó 2.644 khách được đánh giá. Bộ
này không có thông tin khách hàng, và nhóm giữ nguyên cấu hình đã chọn trên H&M." Lưu ý: nói "món chưa từng mua", không
nói "sản phẩm mới".

**Slide 6.** "Nguyên tắc chung là học trên quá khứ, đánh giá trên tương lai. Giai đoạn A chọn cấu hình trên mẫu phát
triển, dùng dữ liệu trước 01/07/2020. Mỗi mô hình có tham số học được thử 6 cấu hình và chọn theo NDCG@10 trên tập xác thực 4 tuần.
Cấu hình được cố định rồi mới sang giai đoạn B. Giai đoạn B làm trên mẫu kiểm định: huấn luyện lại 5 lần chạy với dữ liệu
trước 29/07/2020, xếp hạng mọi ứng viên của từng khách trong 8 tuần cuối, rồi kiểm định thống kê. Đặc trưng và mẫu âm đều
tính tại đúng thời điểm, nên mô hình không nhìn thấy thông tin của giai đoạn được đánh giá." [ "Nhóm chỉ kết luận A tốt
hơn B khi p sau hiệu chỉnh Holm dưới 0,05, khoảng tin cậy không chứa 0 và chênh lệch từ 5% trở lên." ]

**Slide 7.** "Các mô hình đối chứng chia ba nhóm. Nhóm mô hình đơn lẻ là từng nhánh, có và không có đặc trưng. Nhóm học
máy truyền thống gồm láng giềng, nhân tử hoá BPR-MF, lọc nội dung và mô hình lai truyền thống Hybrid-CBCF. Nhóm chuyên
biệt gồm các mô hình phổ biến, NeuMF gốc và LateFusion-F. Random chỉ làm mốc dưới. Hậu tố -F chỉ mô hình có đặc trưng:
so từng cặp có và không có -F sẽ thấy phần cải thiện do đặc trưng. Mọi mô hình dùng cùng dữ liệu, cùng tập ứng viên và
cùng ngân sách tinh chỉnh." Câu chuyển người: "Sau đây bạn Minh Lý xin trình bày kết quả."

**Slide 8 (Minh Lý).** "Đây là kết quả trên tập kiểm thử H&M, trung bình 5 lần chạy trên 3.165 khách. NeuMF-F và NeuMF chỉ
dùng ID có cùng kiến trúc. NeuMF-F hơn NeuMF chỉ ID 43,8% NDCG@10, khác biệt có ý nghĩa thống kê, và đó là phần cải thiện
do đặc trưng. NeuMF-F cũng tốt hơn có ý nghĩa cả năm mô hình đối chứng trong họ so sánh: BPR-MF, ItemKNN, UserKNN,
MostPopular-Recent và Content. Mạnh nhất trong năm mô hình này là UserKNN, NeuMF-F hơn 28,5%. So với mô hình lai truyền
thống Hybrid-CBCF, NeuMF-F hơn 25,8%. Bốn vị trí đầu bảng đều là mô hình có đặc trưng." Lưu ý: chữ "5/5" trên slide là
năm so sánh này, có cả MostPopular-Recent, nên nói đủ tên.

**Slide 9.** "Trên Amazon Beauty, nhóm giữ nguyên cấu hình chọn trên H&M, không tinh chỉnh lại. NeuMF-F hơn NeuMF chỉ ID
65,7%, hơn UserKNN 30,8% và hơn Hybrid-CBCF 23,0%, đều có ý nghĩa. Bỏ so sánh với BPR-MF ra thì chênh lệch nhỏ nhất vẫn
là 30,8% so với UserKNN. Kết luận về giá trị của đặc trưng lặp lại ở một lĩnh vực khác, dù bộ này không có thông tin khách
hàng."

**Slide 10.** "Để trả lời câu hỏi 2, nhóm tắt lần lượt từng nhóm đặc trưng. Bỏ đặc trưng thời gian làm NDCG@10 giảm
42,3% trên H&M và 31,6% trên Amazon, mức giảm lớn nhất trong các nhóm. Doanh số gần đây của sản phẩm và nhịp mua của
khách là thông tin có giá trị nhất, và đó là dữ liệu doanh nghiệp nào cũng có sẵn." [ "Phân tích này chạy một seed và mang
tính mô tả." ]

**Slide 11.** "Câu hỏi 3 so hai cách hợp nhất trên cùng hai nhánh có đặc trưng. Hợp nhất muộn LateFusion-F huấn luyện hai
nhánh riêng rồi trộn điểm. NDCG@10 của nó cao hơn: không khác biệt có ý nghĩa với NeuMF-F trên H&M, và cao hơn có ý nghĩa
trên Amazon. NeuMF-F là một mạng, huấn luyện một lần: 15,2 so với 30,1 phút trên H&M, 4,1 so với 10,9 phút trên Amazon,
và danh sách khuyến nghị phủ được nhiều sản phẩm hơn. LateFusion-F dùng lại chính hai nhánh có đặc trưng của NeuMF-F, nên
kết quả cao của nó cũng nhờ đặc trưng. Giá trị của đặc trưng rõ với cả hai cách hợp nhất." Đây là chỗ duy nhất nói về
LateFusion-F trong phần trình bày; câu hỏi sâu hơn trả lời theo Phần 0, Câu 1.

**Slide 12.** "Hệ thống demo có ba tầng. Giao diện web có ba màn hình và chỉ gọi API. API suy luận viết bằng FastAPI xếp
hạng mọi ứng viên của khách và trả về Top-K; khách mới nhận danh sách bán chạy. Tầng mô hình và dữ liệu nạp trọng số đã
huấn luyện một lần khi khởi động. Demo chạy hoàn toàn trên máy, không cần mạng."

**Slide 13.** "Màn hình cửa hàng đặt NeuMF-F bên trái, mô hình đối chứng bên phải; dòng xanh là món khách thật sự mua sau
mốc. Màn hình kết quả đặt NeuMF-F cạnh từng mô hình đối chứng, kèm kết luận kiểm định và mức giảm khi bỏ từng nhóm đặc
trưng. Sau đây nhóm xin demo trực tiếp." → làm theo Phần 7, khoảng 3 phút. Nếu không đủ giờ thì chỉ làm bước 3–4 và 6.

**Slide 14.** "Nhóm xin trả lời ba câu hỏi nghiên cứu. Câu 1: có. NeuMF-F tốt hơn có ý nghĩa mọi mô hình học máy truyền
thống trên cả hai bộ, và hơn NeuMF chỉ ID 43,8% trên H&M, 65,7% trên Amazon. Câu 2: có, đặc trưng thời gian đóng góp
nhiều nhất. Câu 3: cả hai cách hợp nhất đều hưởng lợi từ đặc trưng; hợp nhất sớm gọn và huấn luyện nhanh hơn, hợp nhất
muộn có NDCG@10 cao hơn. Đóng góp của đề tài là một mô hình lai có đặc trưng, việc chỉ ra nhóm đặc trưng quan trọng nhất,
và một quy trình đánh giá dùng lại được. Hướng phát triển gồm mở rộng dữ liệu, đánh giá riêng trên sản phẩm vừa ra mắt,
và biểu diễn ảnh, mô tả bằng mô hình tiền huấn luyện."

**Slide 15.** "Nhóm xin cảm ơn quý thầy cô đã lắng nghe, và rất mong nhận được câu hỏi, góp ý của hội đồng."

Cách luyện:
- Mỗi bạn nói phần của mình ba lần có bấm giờ. Lần cuối nói liền 15 slide cùng demo, đúng thứ tự, có chuyển người.
- Thuộc lòng câu mở (slide 1), câu chuyển người (cuối slide 7) và câu kết (slide 14–15). Phần còn lại nói theo ý.
- Khi chiếu bảng hoặc biểu đồ, chỉ vào đúng dòng đang nói, nhất là dòng NeuMF-F và dòng đối chứng.
- Nếu bị hỏi ngắt giữa chừng, trả lời gọn trong 30 giây rồi xin phép trình bày tiếp. Câu dài để dành cho phần hỏi đáp.
- Trong lúc bạn kia trình bày, bạn còn lại mở sẵn demo (Phần 7, bước 1) và theo dõi giờ.
