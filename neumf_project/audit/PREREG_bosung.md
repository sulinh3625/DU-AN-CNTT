# Đăng ký bổ sung — mô hình lai truyền thống (sau đánh giá cuối)

Ngày đăng ký: 13/10/2026. Bổ sung cho `audit/PREREG_v2.md` (H&M) và `audit/PREREG_amazon.md` (Amazon Beauty).

Trạng thái lúc đăng ký:
- Đánh giá cuối của 14 mô hình đã xong và đã mở tập kiểm thử: H&M ngày 10/10/2026 (mẫu kiểm định, khối 2), Amazon Beauty
  10–11/10/2026. Kết quả, họ 10 so sánh và kết luận của hai lần đó **giữ nguyên**.
- Mô hình bổ sung **chưa** được chấm trên tập kiểm thử nào. Ngày 13/10/2026 đã chạy thử trên tập xác thực của mẫu phát
  triển H&M để chốt cách học trọng số (mục 1); không dựng tập kiểm thử.
- Lý do bổ sung: góp ý của GVHD ở buổi họp 04/10/2026 (yêu cầu #8) — trình bày baseline theo ba nhóm: mô hình đơn lẻ,
  học máy truyền thống, mô hình chuyên biệt cho gợi ý. Nhóm học máy truyền thống cần một **mô hình lai truyền thống** để
  đối chiếu với mô hình lai học sâu của đề tài.
- Quyết định thêm mô hình được đưa ra **sau** khi đã xem kết quả kiểm thử của 14 mô hình, nên kết quả của mô hình bổ sung
  là **phân tích bổ sung**: không thuộc họ 10 so sánh đăng ký trước, không dùng để thay đổi kết luận chính, và luôn được
  ghi chữ "bổ sung" trong báo cáo.

File này phải được commit **trước** lần chạy `scripts/25_bosung.py final` (script từ chối chạy nếu chưa commit). Lệch kế
hoạch ghi ở mục 8.

## 1. Mô hình: Hybrid-CBCF (`src/baselines/hybrid.py`)

Theo mô hình lai trong luận án của Hồ Thị Linh (2023, chương 3): kết hợp ba mô hình đơn lẻ truyền thống — lọc nội dung
(M1), lọc cộng tác theo người dùng (M2) và theo sản phẩm (M3) — ở mức điểm dự đoán. Trong đề tài:

- M1 = Content, M2 = UserKNN, M3 = ItemKNN, với đúng cấu hình đã chọn khi tinh chỉnh (`audit/v2/best_configs.json`:
  Content chu kỳ bán rã 30 ngày; UserKNN k = 200, shrink = 0; ItemKNN k = 100, shrink = 50), khớp trên dữ liệu huấn luyện
  của giai đoạn như ở đánh giá cuối. Không tinh chỉnh lại ba thành phần.
- Điểm của mỗi thành phần được chuẩn hoá min–max trên tập ứng viên của khách (như LateFusion-F), thành vector
  x = (x_Content, x_UserKNN, x_ItemKNN).
- Bốn cách kết hợp, như luận án: **bỏ phiếu** — trung bình, max, min của ba điểm; **trọng số** — điểm lai = w · x. Luận
  án học w bằng mạng truyền thẳng f(x) = Σ w_i x_i trên điểm đánh giá; phản hồi ẩn không có điểm đánh giá nên w được học
  **theo cặp**: với mỗi sản phẩm đúng p của một khách, rút 50 sản phẩm không đúng j trong tập ứng viên của khách đó
  (không lặp, numpy seed 0); mẫu là hiệu x_p − x_j (nhãn 1) và x_j − x_p (nhãn 0); hồi quy logistic không hệ số chặn,
  C = 1 (scikit-learn, lbfgs). Đây là tiêu chí BPR với hàm điểm tuyến tính.
- Đã thử và **bỏ** cách học w bằng hồi quy logistic trên từng cặp (khách, ứng viên) độc lập: chạy thử ngày 13/10 trên
  tập xác thực cho trọng số âm và NDCG@10 ≈ 0,0005 — gộp mọi khách vào một hồi quy, trọng số bị chi phối bởi khác biệt
  giữa các khách chứ không phải thứ tự trong danh sách của từng khách.
- Không có khởi tạo ngẫu nhiên: cùng dữ liệu cho cùng kết quả ở mọi seed.

## 2. Chọn cách kết hợp — chỉ trên tập xác thực của mẫu phát triển H&M (`scripts/25_bosung.py tune`)

- 4 cấu hình (dưới ngân sách 6 cấu hình của các mô hình có học): `mean`, `max`, `min`, `lr`.
- NDCG@10 xác thực của `lr` tính bằng **khớp chéo hai phần theo khách** (khách có chỉ số chẵn được chấm bằng w học trên
  khách lẻ và ngược lại), để số không lạc quan vì w học trên chính khách được chấm. Trọng số dùng về sau học trên toàn
  bộ tập xác thực.
- Chọn cấu hình có NDCG@10 xác thực cao nhất. Mỗi cấu hình một dòng `audit/v2/bosung_tuning_log.csv` (kèm mã băm mã
  nguồn, `data_md5`, MD5 tệp đặc trưng); cấu hình chọn vào `audit/v2/bosung_best_configs.json`. Hai tệp này được commit
  cùng file này.

## 3. Đánh giá — mở tập kiểm thử một lần cho mỗi bộ dữ liệu (`scripts/25_bosung.py final`)

- **H&M:** tập kiểm thử của mẫu kiểm định (khối 2) — cùng tệp dữ liệu (kiểm `data_md5` với `outputs/v2/final/data.json`),
  cùng ứng viên, cùng quy tắc phá hoà như đánh giá cuối ngày 10/10/2026; ba thành phần khớp trên mọi cặp trước
  29/07/2020.
- **Amazon Beauty:** cách kết hợp và trọng số chọn trên H&M, không chọn lại (như `PREREG_amazon.md` mục 4); thành phần
  khớp trên mọi cặp trước 01/01/2014.
- Mô hình tất định nên chấm một lần; giá trị theo từng khách dùng chung cho cả 5 seed khi tính trung bình và kiểm định.
- **Khoá kiểm thử:** file này và kết quả tinh chỉnh đã commit; có `--reason`; không có file đã theo dõi bị sửa (trừ
  `outputs/` và `audit/test_access_log.csv`); không có file mã nguồn chưa theo dõi; mã băm mã nguồn trùng lúc tinh chỉnh
  (H&M). Mỗi bộ dữ liệu ghi một dòng `audit/test_access_log.csv` **trước** khi chấm, `run_tag` = `bosung_hybrid_hm` /
  `bosung_hybrid_amazon`; đã có dòng thì không chạy lại trừ khi có `--allow-rerun` (ghi vào mục 8).
- **Đối chiếu thành phần:** ba thành phần được chấm lại cùng lúc và so hạng của từng khách với lần đánh giá cuối đã đăng
  ký. Đã biết trước: tệp đặc trưng (`catalog_v2.npz`) không nằm trong git, mỗi máy tự dựng, và vector văn bản (TF-IDF +
  SVD ngẫu nhiên hoá) phụ thuộc phiên bản thư viện; trên máy chạy bổ sung, Content ở tập xác thực của mẫu phát triển đạt
  NDCG@10 0,00435, so với 0,00459 lúc tinh chỉnh. UserKNN, ItemKNN không dùng đặc trưng và trùng khớp (0,02753; 0,02599).
  Mức lệch trên tập kiểm thử được ghi trong `results.json` và báo cáo.
- Ra: `outputs/v2/final/bosung/`, `outputs/amazon/final/bosung/` (`results.json`, `per_user.csv.gz` kèm hạng của từng
  sản phẩm đúng, `topk.json.gz`).

## 4. Độ đo và kiểm định

- Như `PREREG_v2.md` mục 6–7: NDCG@10 là độ đo chính; bốn độ đo ở K = 5, 10, 15, 20 tính từ hạng đã lưu; độ phủ top-10.
- **Họ bổ sung 2 so sánh** — Wilcoxon signed-rank theo khách trên NDCG@10 trung bình qua 5 seed, khoảng tin cậy bootstrap
  ghép cặp 95% (10.000 lần, seed 0), hiệu chỉnh Holm **trong họ này**, α = 0,05; cùng tiêu chí "tốt hơn" (p Holm < 0,05,
  khoảng tin cậy không chứa 0, chênh lệch tương đối ≥ 5%):
  - B1. NeuMF-F vs Hybrid-CBCF — mô hình lai học sâu đề xuất so với mô hình lai truyền thống.
  - B2. Hybrid-CBCF vs UserKNN — mô hình lai truyền thống so với thành phần có NDCG@10 xác thực cao nhất của nó.
- Họ 10 so sánh đăng ký trước giữ nguyên, không hiệu chỉnh lại.

## 5. Trình bày theo ba nhóm baseline

Bảng kết quả xếp các mô hình đối chứng theo ba nhóm (nhóm đề xuất, chờ GVHD xác nhận):
- **Mô hình đơn lẻ** — một nhánh của mô hình lai đứng riêng: GMF, MLP, GMF-F, MLP-F.
- **Học máy truyền thống**: Content, ItemKNN, UserKNN, BPR-MF và **Hybrid-CBCF** (bổ sung).
- **Chuyên biệt cho gợi ý**: Most Popular, MostPopular-Recent, NeuMF, LateFusion-F.

Random là cận dưới. Thứ hạng "xếp thứ k trong 14 mô hình" trong báo cáo vẫn tính trên 14 mô hình đăng ký trước.

## 6. Kết luận được phép

- Chỉ kết luận về Hybrid-CBCF theo họ bổ sung (mục 4); mọi câu về nó ghi rõ là phân tích bổ sung.
- Nếu NeuMF-F không tốt hơn Hybrid-CBCF có ý nghĩa, báo cáo đúng như vậy.

## 7. Hạn chế đã biết lúc đăng ký

- Mô hình được thêm **sau** khi đã xem kết quả kiểm thử của 14 mô hình, kể cả ba thành phần của nó. Thiết kế (thành
  phần, cách kết hợp) lấy từ luận án của GVHD và chọn trên tập xác thực, không dựa trên số kiểm thử; nhưng kết quả kiểm
  thử của từng thành phần đã biết trước.
- Ngân sách nhỏ: 4 cách kết hợp; không tinh chỉnh lại thành phần, không thử thêm thành phần (ví dụ BPR-MF,
  MostPopular-Recent).
- Trọng số học trên tập xác thực của mẫu phát triển H&M rồi dùng nguyên cho mẫu kiểm định và cho Amazon.
- Máy chạy bổ sung có thể khác máy đã chạy đánh giá cuối (máy chỉ có CPU); mô hình không có mạng nơ-ron. Content có thể
  lệch nhẹ (mục 3).

## 8. Lệch kế hoạch

Chưa có.
