# Đăng ký trước (pre-registration) — giao thức v2

Ngày đăng ký: 03/10/2026. Viết trong lúc đợt tinh chỉnh đầu tiên trên mẫu phát triển A đang chạy: đã có kết quả của
các baseline, **chưa có** kết quả tinh chỉnh của bất kỳ mô hình có đặc trưng nào, **chưa** dựng tập kiểm thử của mẫu
kiểm định B và chưa huấn luyện hay chấm bất kỳ mô hình nào trên B. File này phải được commit **trước** lần chạy
`scripts/23_final_v2.py` (script từ chối chạy nếu file chưa commit). Lệch kế hoạch ghi ở mục 10 và trong báo cáo.

## 0. Vì sao có giao thức v2

Giao thức cũ (`audit/PREREG.md`, gọi là v1) đã cho kết quả trên tập kiểm thử của mẫu hm500k. Rà soát kết quả đó cho
thấy bốn vấn đề làm số liệu chưa đủ chuẩn để kết luận về mô hình lai:
1. Tập kiểm thử đã được xem nhiều lần (27/09, 29/09, 02/10) và một số quyết định được đưa ra sau khi xem.
2. Lọc k-core dùng cả dữ liệu của giai đoạn kiểm thử để chọn người dùng và sản phẩm.
3. Sản phẩm mới ra mắt trong giai đoạn kiểm thử bị loại khỏi tập ứng viên, dù trong mẫu này 27% cặp mua lần đầu
   trong giai đoạn kiểm thử (28.671 cặp, chưa lọc) là sản phẩm chưa từng bán trước 29/07/2020. Như vậy bài toán được
   đánh giá dễ hơn thực tế, và mô hình chỉ dùng ID không phải đối mặt với hạn chế lớn nhất của nó.
4. Mô hình chỉ dùng ID (NeuMF, GMF, MLP) không tận dụng được thông tin sản phẩm (thuộc tính, mô tả), khách hàng và
   thời gian có sẵn trong bộ dữ liệu H&M.

Giao thức v2 sửa cả bốn điểm: đánh giá cuối trên một **mẫu khách hàng độc lập** (mẫu B) chỉ mở tập kiểm thử đúng một
lần, k-core chỉ dùng dữ liệu trước mốc kiểm thử, sản phẩm mới có trong tập ứng viên, và mô hình lai được bổ sung đặc
trưng (NeuMF-F). Kết quả v1 được giữ làm **lịch sử phát triển**; mọi kết luận của báo cáo lấy từ mẫu B.

## 1. Dữ liệu

- Nguồn: H&M Personalized Fashion Recommendations (Kaggle) — `transactions_train.csv` (31.788.324 giao dịch,
  20/09/2018 → 22/09/2020), `articles.csv` (105.542 sản phẩm), `customers.csv` (1.371.980 khách).
- **Mẫu phát triển A** (`data/processed/hm/hm500k_transactions.csv`, md5 `13f48afe5133d79bcb9c0832c4ee287d`):
  500.269 giao dịch của 21.599 khách, chọn theo băm `customer_id` (`scripts/00_sample_hm.py`, các bucket băm
  [0, 1597) trên 100.000). Chỉ dùng để tinh chỉnh, và chỉ trên tập xác thực.
- **Mẫu kiểm định B** (`data/processed/hm/hm500k_b_transactions.csv`, md5 `19ba444b60694b8240b1df41d834cd98`):
  500.125 giao dịch của 21.030 khách, các bucket kế tiếp [1597, 3160) với cùng khoá băm (`00_sample_hm.py --holdout`),
  nên **không có khách nào chung** với A. Đến lúc đăng ký mới chỉ đếm số dòng và số khách của B.
- Đặc trưng (`scripts/21_build_features.py`): danh mục sản phẩm từ `articles.csv`, doanh số theo ngày của từng sản
  phẩm trên **toàn bộ** giao dịch H&M (không chỉ trong mẫu), thuộc tính khách từ `customers.csv`.

## 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`)

- Gộp giao dịch thành cặp (khách, sản phẩm) với ngày mua đầu; mốc xác thực 01/07/2020, mốc kiểm thử 29/07/2020; cửa
  sổ xác thực 01/07–28/07, cửa sổ kiểm thử 29/07–22/09/2020.
- Lọc 10-core (`k_core: 10`) **chỉ trên các cặp có ngày mua đầu trước mốc kiểm thử**.
- Với mỗi giai đoạn (xác thực: mốc 01/07; kiểm thử: mốc 29/07):
  - tập huấn luyện = các cặp đã lọc có ngày mua đầu trước mốc; khi đánh giá ở giai đoạn kiểm thử, tập này gồm cả cửa
    sổ xác thực (tức "huấn luyện ∪ xác thực");
  - sản phẩm **cũ** (chấm được bằng ID) = sản phẩm có ít nhất một cặp huấn luyện;
  - sản phẩm **mới** = sản phẩm trong danh mục chưa từng bán (trên toàn H&M) trước mốc. **Giả định:** doanh nghiệp
    biết trước danh mục sắp bán (có thuộc tính và mô tả) nhưng không biết sản phẩm nào sẽ bán được;
  - tập ứng viên của một người dùng = sản phẩm cũ ∪ sản phẩm mới, trừ sản phẩm người đó đã mua trước mốc;
  - sản phẩm đúng = các cặp mua lần đầu trong cửa sổ của giai đoạn, của người dùng có lịch sử huấn luyện, với sản phẩm
    thuộc tập ứng viên. Một người dùng có thể có nhiều sản phẩm đúng.
- Mô hình chỉ dùng ID không có vector cho sản phẩm mới: sản phẩm không có dữ liệu huấn luyện nhận điểm −∞, tức bị
  xếp cuối (`MaskedScorer`, `MaskedScoreFn`). Mô hình có đặc trưng và gợi ý theo nội dung chấm được sản phẩm mới.
- **Đặc trưng theo thời điểm** (không dùng thông tin tương lai): đặc trưng thời gian của sản phẩm tại ngày t chỉ dùng
  doanh số của các ngày trước t; đặc trưng thời gian của khách tại ngày t chỉ dùng các cặp có ngày mua đầu trước t.
  Khi huấn luyện, mỗi cặp dương mang ngày mua đầu t của nó; khi đánh giá, t = mốc của giai đoạn. Mẫu âm của một cặp ở
  ngày t chỉ lấy trong các sản phẩm của tập huấn luyện đã ra mắt trước hoặc trong ngày t, trừ sản phẩm khách đã mua.
- Mẫu A ở giai đoạn xác thực: 7.134 người dùng, 19.228 sản phẩm (9.596 có ID); 2.229 người dùng xác thực,
  7.074 cặp đúng (930 cặp là sản phẩm mới).

## 3. Mô hình

| Nhóm | Mô hình (mã) | Ghi chú |
|---|---|---|
| Cận dưới | Random (`random`) | điểm ngẫu nhiên, chỉ để đối chiếu |
| Phổ biến | Most Popular (`popularity`) | số cặp trong tập huấn luyện của mẫu; sản phẩm mới xếp cuối |
| | MostPopular-Recent (`recent_pop`) | số giao dịch toàn H&M trong W ngày trước mốc |
| Nội dung | Content (`content`) | hồ sơ khách = trung bình (có trọng số theo độ mới) vector nội dung sản phẩm đã mua; cosine |
| Láng giềng | ItemKNN (`itemknn`), UserKNN (`userknn`) | cosine trên vector mua nhị phân, hệ số co, top-k láng giềng |
| MF | BPR-MF (`bpr`) | MF tối ưu BPR, chỉ dùng ID |
| Chỉ dùng ID | GMF (`gmf`), MLP (`mlp`), NeuMF (`neumf`) | kiến trúc NCF; NeuMF = hợp nhất sớm GMF + MLP |
| Có đặc trưng | GMF-F (`gmf_f`), MLP-F (`mlp_f`) | từng nhánh của NeuMF-F đứng riêng |
| **Mô hình đề tài** | **NeuMF-F** (`neumf_f`) | hợp nhất sớm (Early Fusion) MF + DNN có đặc trưng |
| Hợp nhất muộn | LateFusion-F (`late_f`) | w·minmax(GMF-F) + (1 − w)·minmax(MLP-F), hai mô hình huấn luyện riêng |

**NeuMF-F** (`src/models/hybrid_features.py`) giữ cấu trúc hai nhánh của NeuMF: nhánh GMF (tích từng phần tử) và nhánh
MLP (tháp [2d, d, d/2, d/4], ReLU, dropout), nối đầu ra rồi một lớp dự đoán chung. Vector khách/sản phẩm của mỗi nhánh
= embedding ID + phép chiếu tuyến tính (không bias) của đặc trưng:
- sản phẩm: 11 thuộc tính danh mục (mã loại, nhóm sản phẩm, hoạ tiết, nhóm màu, độ đậm màu, màu chủ đạo, bộ phận, chỉ
  mục, nhóm chỉ mục, khu, nhóm may mặc), mỗi thuộc tính một embedding 8 chiều; vector văn bản 64 chiều (TF-IDF 1–2 từ
  của tên và mô tả sản phẩm → TruncatedSVD → chuẩn hoá L2); 5 đặc trưng thời gian (log(1 + doanh số 7, 28, 91 ngày
  trước t), log(1 + tuổi sản phẩm), cờ chưa từng bán trước t);
- khách: 5 thuộc tính tĩnh (nhóm tuổi, trạng thái hội viên, tần suất nhận tin, FN, Active), mỗi thuộc tính một
  embedding 8 chiều; 2 đặc trưng thời gian (log(1 + số ngày từ lần mua gần nhất), log(1 + số cặp đã mua)).
Sản phẩm không có ID dùng vector ID bằng 0 (chỉ còn phần đặc trưng). Khi huấn luyện, ID của sản phẩm bị bỏ ngẫu nhiên
với xác suất `id_dropout` để mô hình học cách chấm khi thiếu ID. GMF-F, MLP-F là NeuMF-F tắt một nhánh. Huấn luyện bằng
BCE với mẫu âm (như NCF), Adam, batch 512.

**Ablation của NeuMF-F** (cùng siêu tham số với NeuMF-F, tắt một thành phần): bỏ vector văn bản, bỏ đặc trưng thời
gian, bỏ thông tin khách, bỏ thuộc tính sản phẩm, bỏ cơ chế bỏ ID ngẫu nhiên (`id_dropout` = 0).

## 4. Tinh chỉnh — chỉ trên tập xác thực của mẫu A (`scripts/22_tune_v2.py`)

- Seed 42. Mô hình có học: 6 cấu hình mỗi mô hình (cấu hình mặc định + 5 cấu hình rút không lặp từ lưới bằng numpy
  seed 0). Mạng nơ-ron: tối đa 20 epoch, dừng sớm sau 5 epoch không cải thiện NDCG@10 trên tập xác thực.
- Lưới (in đậm là mặc định):
  - GMF, MLP, NeuMF: lr {**1e-3**, 5e-4}, negative_ratio {**4**, 8}, embedding_dim {**32**, 64}, weight_decay
    {0, **1e-6**}, dropout {0, **0,2**} (GMF không có dropout).
  - GMF-F, MLP-F, NeuMF-F: như trên + id_dropout {0, **0,25**, 0,5}.
  - BPR-MF: embedding_dim {**32**, 64, 128}, lr {0,01; **0,03**; 0,05}, reg {0,001; **0,005**; 0,01}, epochs {**20**, 40}.
  - ItemKNN, UserKNN: k {20, 50, **100**, 200, 500} × shrink {**0**, 10, 50}.
  - Mô hình một tham số thử đủ lưới: MostPopular-Recent W {7, 14, 28, 56, 91} ngày; Content half_life {không trọng
    số, 30, 90, 180, 365} ngày; LateFusion-F w {0; 0,1; …; 1} trên GMF-F, MLP-F tốt nhất (checkpoint lúc tinh chỉnh).
- Mỗi cấu hình ghi một dòng `audit/v2/tuning_log.csv` (tham số, commit, mã băm mã nguồn `code_hash`, epoch tốt nhất,
  thời gian, chỉ số xác thực); cấu hình có NDCG@10 xác thực cao nhất vào `audit/v2/best_configs.json`. Không dựng tập
  kiểm thử của mẫu nào khi tinh chỉnh.
- Không tinh chỉnh trên mẫu B. Không tinh chỉnh lại sau khi mở tập kiểm thử của B.

## 5. Đánh giá cuối trên mẫu B (`scripts/23_final_v2.py`)

- Cấu hình: `audit/v2/best_configs.json` của mẫu A, giữ nguyên.
- 5 seed: 42, 2024, 2025, 2026, 3407. Với mỗi seed:
  - Mạng nơ-ron (GMF, MLP, NeuMF, GMF-F, MLP-F, NeuMF-F): huấn luyện trên tập huấn luyện của giai đoạn xác thực của B,
    dừng sớm theo NDCG@10 xác thực của B (như lúc tinh chỉnh) để chọn số epoch e*; huấn luyện lại từ đầu trên mọi cặp
    trước mốc kiểm thử đúng e* epoch; chấm tập kiểm thử của B.
  - BPR-MF: khớp trên mọi cặp trước mốc kiểm thử, số epoch theo cấu hình.
  - Most Popular, MostPopular-Recent, Content, ItemKNN, UserKNN: khớp trên mọi cặp trước mốc kiểm thử (tất định, giống
    nhau ở mọi seed). Random theo seed.
  - LateFusion-F: trộn điểm của đúng GMF-F và MLP-F đã huấn luyện lại ở seed đó, w theo mẫu A.
- Ablation (mục 3): chỉ seed 42, cùng quy trình, chấm cùng tập kiểm thử. Chỉ mô tả, không kiểm định, không dùng để
  chọn lại gì.
- Phân tích độ nhạy "chỉ sản phẩm cũ": cùng các mô hình đã huấn luyện, chấm lại với tập ứng viên chỉ gồm sản phẩm cũ
  và sản phẩm đúng chỉ gồm sản phẩm cũ (gần với giao thức v1). Chỉ mô tả.
- Khoá kiểm thử: script từ chối chạy nếu file này chưa commit, thiếu `--reason`, có file đã theo dõi bị sửa mà chưa
  commit (trừ `outputs/` và `audit/test_access_log.csv` — do chính đánh giá cuối ghi, để chạy tiếp seed còn thiếu nếu bị
  ngắt), có file mã nguồn chưa được theo dõi trong `src/`, `scripts/`, `configs/`, tinh chỉnh chưa đủ mô hình, hoặc mã
  nguồn khác mã nguồn đã dùng khi tinh chỉnh (so `code_hash`). Mỗi seed ghi một dòng `audit/test_access_log.csv`
  **trước** khi chấm; seed đã có dòng nhật ký thì không chạy lại trừ khi có `--allow-rerun` (khi đó ghi vào mục 10 và
  báo cáo).
- Ra: `outputs/v2/final/seed<N>/` (chỉ số, chỉ số theo từng người dùng kèm hạng của từng sản phẩm đúng, lịch sử huấn
  luyện, thông tin thời gian), top-20 của seed 42.

## 6. Độ đo

- Xếp hạng toàn bộ tập ứng viên của từng người dùng (khoảng 17 nghìn sản phẩm), hoà điểm phá bằng khoá giả ngẫu nhiên
  tất định (seed 2026). Trung bình theo người dùng.
- **Độ đo chính (kết luận): NDCG@10** trên tập kiểm thử của mẫu B.
- Độ đo phụ: Recall@10, HR@10, Precision@10, NDCG@5, NDCG@20.
- Theo nhóm sản phẩm: NDCG@10 riêng cho sản phẩm đúng **cũ** và **mới** — chỉ các sản phẩm đúng của nhóm được coi là
  liên quan, hạng lấy trong cùng danh sách xếp hạng đầy đủ; người dùng không có sản phẩm đúng thuộc nhóm không tính
  vào trung bình của nhóm.
- Mô tả thêm (seed 42): độ phủ danh mục của top-10, tỉ lệ sản phẩm mới trong top-10, thời gian huấn luyện.

## 7. Kiểm định

- Với mỗi người dùng, lấy NDCG@10 trung bình qua 5 seed (mô hình tất định: giá trị như nhau ở mọi seed). So sánh từng
  cặp bằng **Wilcoxon signed-rank** trên hiệu theo người dùng và **khoảng tin cậy bootstrap ghép cặp 95%** của hiệu
  trung bình (10.000 lần lấy mẫu, seed 0).
- **Họ 10 so sánh cố định**, hiệu chỉnh **Holm** trên cả họ, α = 0,05:
  1. NeuMF-F vs NeuMF — đặc trưng có cải thiện mô hình lai không
  2. NeuMF-F vs GMF-F — mô hình lai so với nhánh MF đứng riêng
  3. NeuMF-F vs MLP-F — mô hình lai so với nhánh DNN đứng riêng
  4. NeuMF-F vs LateFusion-F — hợp nhất sớm so với hợp nhất muộn
  5. NeuMF-F vs BPR-MF
  6. NeuMF-F vs ItemKNN
  7. NeuMF-F vs UserKNN
  8. NeuMF-F vs MostPopular-Recent
  9. NeuMF-F vs Content
  10. NeuMF vs BPR-MF — mô hình lai chỉ dùng ID so với MF
- "A tốt hơn B" chỉ được viết khi đồng thời: p sau hiệu chỉnh Holm < 0,05, khoảng tin cậy bootstrap không chứa 0 và
  chênh lệch tương đối NDCG@10 ≥ 5%. Ngược lại viết "không khác biệt có ý nghĩa" (hoặc "B tốt hơn" nếu hiệu âm và
  thoả cả ba điều kiện).
- Theo nhóm sản phẩm cũ/mới, ablation, độ nhạy "chỉ sản phẩm cũ": báo cáo trung bình và khoảng tin cậy bootstrap,
  không kiểm định, không dùng để kết luận chính.

## 8. Kết luận được phép

- Mô hình đề tài là NeuMF-F, cố định từ trước — không chọn lại theo kết quả kiểm thử.
- Câu trả lời cho câu hỏi chính dựa trên họ so sánh ở mục 7. **Nếu NeuMF-F không vượt baseline nào đó, báo cáo đúng
  như vậy**; không đổi độ đo, mẫu, họ so sánh hay tiêu chí sau khi xem kết quả.
- Kết quả v1 chỉ được nhắc như lịch sử phát triển, không gộp với kết quả v2.

## 9. Hạn chế đã biết lúc đăng ký

- k-core lọc trên mọi cặp trước mốc kiểm thử, nên tập người dùng/sản phẩm của giai đoạn xác thực phụ thuộc một phần
  vào dữ liệu tháng 7/2020. Điều này chỉ ảnh hưởng việc chọn cấu hình trên A, không ảnh hưởng tập kiểm thử của B.
- `customers.csv` không có mốc thời gian: thuộc tính khách là ảnh chụp tại thời điểm công bố dữ liệu, giả định ít đổi.
- Vector văn bản được khớp (TF-IDF, SVD) trên toàn bộ danh mục, kể cả sản phẩm ra mắt sau — phù hợp giả định "biết
  trước danh mục"; phép khớp không dùng dữ liệu mua.
- MostPopular-Recent và đặc trưng doanh số dùng giao dịch của toàn H&M trước mốc — dữ liệu mà doanh nghiệp có.
- Một mẫu kiểm định (khoảng 3 nghìn người dùng có sản phẩm đúng); kết luận áp dụng cho dữ liệu H&M và khung thời gian này.
- Máy của nhóm không có GPU: thời gian chạy trên CPU dài (ước lượng tinh chỉnh 5–6 giờ, đánh giá cuối 10–12 giờ).
  Chạy trên GPU có thể lệch nhẹ ở chữ số cuối so với CPU (mục 10 ghi rõ máy đã chạy).

## 10. Lệch kế hoạch

(Chưa có.)
