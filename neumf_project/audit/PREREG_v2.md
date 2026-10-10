# Đăng ký trước (pre-registration) — giao thức v2, bản cuối

Ngày đăng ký: 10/10/2026. Bản này thay bản 03/10/2026 (`audit/PREREG_v2_cu.md`), vốn là kế hoạch của lần đánh giá cuối
trên khối 1 (`hm500k_b`, mở ngày 04/10/2026, kết quả ở `outputs/v2/final_cu/`).

Trạng thái lúc đăng ký:
- Đã tinh chỉnh xong trên tập xác thực của mẫu phát triển (09–10/10/2026, `audit/v2/`, mục 4). Đã chạy thử đường ống
  đánh giá cuối trên chính tập xác thực đó (1 epoch, 1 seed); số liệu của lần chạy thử không dùng vào việc gì.
- **Chưa** dựng tập kiểm thử của mẫu kiểm định, chưa huấn luyện hay chấm bất kỳ mô hình nào trên mẫu kiểm định. Về mẫu
  kiểm định mới chỉ biết các số trước mốc kiểm thử ở mục 1.
- Độ đo chính, họ so sánh và tiêu chí kết luận (mục 6–8) giữ nguyên như bản 03/10/2026, tức đã cố định trước khi có
  bất kỳ kết quả nào trên dữ liệu gộp theo `product_code`.

File này phải được commit **trước** lần chạy `scripts/23_final_v2.py` (script từ chối chạy nếu file chưa commit). Lệch
kế hoạch ghi ở mục 10 và trong báo cáo.

## 0. Vì sao có bản này

Giao thức v1 (`audit/PREREG.md`) và bản v2 đầu (`audit/PREREG_v2_cu.md`) đã cho kết quả kiểm thử trên mẫu hm500k và
khối 1. Bản cuối đổi bốn điểm, theo góp ý của GVHD và quyết định của nhóm ngày 09/10/2026:
1. Một sản phẩm = một `product_code` (= `article_id // 1000`): mọi màu của cùng một mẫu gộp làm một.
2. Bỏ sản phẩm chưa có người mua: tập ứng viên và sản phẩm đúng chỉ gồm sản phẩm đã có ít nhất một cặp huấn luyện trước
   mốc của giai đoạn. Không còn "sản phẩm mới", nên bỏ phân tích theo nhóm sản phẩm cũ/mới và phân tích độ nhạy "chỉ
   sản phẩm cũ" của bản 03/10.
3. Dữ liệu đã lọc được ghi ra file; mọi mô hình đọc cùng file đó và kiểm bằng MD5.
4. Đánh giá cuối trên **mẫu kiểm định mới (khối 2)**. Khối 1 đã mở ngày 04/10/2026 và các thay đổi trên được quyết định
   sau khi xem kết quả đó, nên khối 1 không còn dùng để kết luận.

Kết quả v1 và kết quả trên khối 1 chỉ là lịch sử phát triển; mọi kết luận của báo cáo lấy từ mẫu kiểm định (khối 2).

## 1. Dữ liệu

- Nguồn: H&M Personalized Fashion Recommendations (Kaggle) — `transactions_train.csv` (31.788.324 giao dịch,
  20/09/2018 → 22/09/2020), `articles.csv` (105.542 sản phẩm), `customers.csv` (1.371.980 khách).
- Lấy mẫu theo khách (`scripts/00_sample_hm.py`): băm `customer_id` (khoá băm cố định) vào 100.000 bucket, chia dãy
  bucket thành các khối liên tiếp, không giao nhau, mỗi khối vừa đủ 500.000 dòng giao dịch, giữ toàn bộ lịch sử mua
  của khách trong khối. Các khối không có khách chung.
  - **Mẫu phát triển** (khối 0, `data/processed/hm/mau_phat_trien.csv`, md5 `13f48afe5133d79bcb9c0832c4ee287d`, trùng
    file hm500k cũ): chỉ dùng để tinh chỉnh, và chỉ trên tập xác thực.
  - Khối 1 (`hm500k_b`): đã mở, không dùng.
  - **Mẫu kiểm định** (khối 2, `data/processed/hm/mau_kiem_dinh.csv`, md5 `62678d150392e99ac83bf5cb65341c85`).
- Dữ liệu đã lọc (`scripts/02_prepare_data.py`, `outputs/data/manifest.json`; MD5 tính trên nội dung chưa nén). Chỉ ghi
  số trước mốc kiểm thử:

  | | Mẫu phát triển | Mẫu kiểm định |
  |---|---|---|
  | File | `outputs/data/mau_phat_trien.csv.gz` | `outputs/data/mau_kiem_dinh.csv.gz` |
  | MD5 | `f7e79f29e1535a2bf4d1feefeadee410` | `ba5498d1071b903ef77a78b0e6125def` |
  | Sản phẩm trước mốc kiểm thử: theo article → theo product_code | 55.971 → 27.370 | 55.683 → 27.291 |
  | Cặp trước mốc kiểm thử: theo article → theo product_code | 401.293 → 359.181 | 398.653 → 356.740 |
  | Sau 10-core: khách / sản phẩm / cặp | 8.039 / 6.801 / 245.644 | 7.994 / 6.749 / 243.696 |

- Đặc trưng (`scripts/21_build_features.py`): danh mục sản phẩm từ `articles.csv`, doanh số theo ngày của từng sản phẩm
  trên **toàn bộ** giao dịch H&M, thuộc tính khách từ `customers.csv`. Gộp theo `product_code` (`group_by_product`):
  thuộc tính lấy theo biến thể có `article_id` nhỏ nhất, 3 cột màu đặt về hằng số, văn bản = trung bình các biến thể
  rồi chuẩn hoá L2, doanh số = tổng các biến thể, ngày bán đầu = ngày sớm nhất.

## 2. Giao thức v2 (`src/data_pipeline/protocol_v2.py`)

- Gộp giao dịch thành cặp (khách, sản phẩm) với ngày mua đầu; mốc xác thực 01/07/2020, mốc kiểm thử 29/07/2020; cửa
  sổ xác thực 01/07–28/07, cửa sổ kiểm thử 29/07–22/09/2020.
- Lọc 10-core (`k_core: 10`) **chỉ trên các cặp có ngày mua đầu trước mốc kiểm thử**.
- Với mỗi giai đoạn (xác thực: mốc 01/07; kiểm thử: mốc 29/07):
  - tập huấn luyện = các cặp đã lọc có ngày mua đầu trước mốc; khi đánh giá ở giai đoạn kiểm thử, tập này gồm cả cửa
    sổ xác thực (tức "huấn luyện ∪ xác thực");
  - sản phẩm chấm được = sản phẩm có ít nhất một cặp huấn luyện;
  - tập ứng viên của một người dùng = sản phẩm chấm được, trừ sản phẩm người đó đã mua trước mốc;
  - sản phẩm đúng = các cặp mua lần đầu trong cửa sổ của giai đoạn, của người dùng có lịch sử huấn luyện, với sản phẩm
    thuộc tập ứng viên. Một người dùng có thể có nhiều sản phẩm đúng.
- **Đặc trưng theo thời điểm** (không dùng thông tin tương lai): đặc trưng thời gian của sản phẩm tại ngày t chỉ dùng
  doanh số của các ngày trước t; đặc trưng thời gian của khách tại ngày t chỉ dùng các cặp có ngày mua đầu trước t.
  Khi huấn luyện, mỗi cặp dương mang ngày mua đầu t của nó; khi đánh giá, t = mốc của giai đoạn. Mẫu âm của một cặp ở
  ngày t chỉ lấy trong các sản phẩm của tập huấn luyện đã ra mắt trước hoặc trong ngày t, trừ sản phẩm khách đã mua.
- Mẫu phát triển ở giai đoạn xác thực: 8.039 người dùng, 6.801 sản phẩm; 2.569 người dùng xác thực, 8.636 cặp đúng,
  trung bình 6.762 ứng viên mỗi người dùng.

## 3. Mô hình

| Nhóm | Mô hình (mã) | Ghi chú |
|---|---|---|
| Cận dưới | Random (`random`) | điểm ngẫu nhiên, chỉ để đối chiếu |
| Phổ biến | Most Popular (`popularity`) | số cặp trong tập huấn luyện của mẫu |
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
  mục, nhóm chỉ mục, khu, nhóm may mặc; 3 cột màu là hằng số sau khi gộp `product_code`), mỗi thuộc tính một embedding
  8 chiều; vector văn bản 64 chiều (TF-IDF 1–2 từ của tên và mô tả sản phẩm → TruncatedSVD → chuẩn hoá L2); 5 đặc
  trưng thời gian (log(1 + doanh số 7, 28, 91 ngày trước t), log(1 + tuổi sản phẩm), cờ chưa từng bán trước t);
- khách: 5 thuộc tính tĩnh (nhóm tuổi, trạng thái hội viên, tần suất nhận tin, FN, Active), mỗi thuộc tính một
  embedding 8 chiều; 2 đặc trưng thời gian (log(1 + số ngày từ lần mua gần nhất), log(1 + số cặp đã mua)).
Khi huấn luyện, embedding ID của sản phẩm bị bỏ ngẫu nhiên với xác suất `id_dropout`, buộc mô hình dựa vào đặc trưng.
GMF-F, MLP-F là NeuMF-F tắt một nhánh. Huấn luyện bằng BCE với mẫu âm (như NCF), Adam, batch 512.

**Ablation của NeuMF-F** (cùng siêu tham số với NeuMF-F, tắt một thành phần): bỏ vector văn bản, bỏ đặc trưng thời
gian, bỏ thông tin khách, bỏ thuộc tính sản phẩm, bỏ cơ chế bỏ ID ngẫu nhiên (`id_dropout` = 0). Biến thể nào trùng
NeuMF-F thì không chạy. Cấu hình NeuMF-F đã chọn (mục 4) có `id_dropout` = 0, nên biến thể "bỏ ID ngẫu nhiên" **không
chạy** và ablation còn 4 biến thể.

## 4. Tinh chỉnh — chỉ trên tập xác thực của mẫu phát triển (`scripts/22_tune_v2.py`)

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
- Mỗi cấu hình ghi một dòng `audit/v2/tuning_log.csv` (tham số, commit, mã băm mã nguồn `code_hash`, `data_md5`, epoch
  tốt nhất, thời gian, chỉ số xác thực); cấu hình có NDCG@10 xác thực cao nhất vào `audit/v2/best_configs.json`. Không
  dựng tập kiểm thử của mẫu nào khi tinh chỉnh.
- **Đã chạy:** 09/10/2026 23:17 → 10/10/2026 03:58, 76 cấu hình, 4,7 giờ; commit `b7a92bb`, `code_hash`
  `0f1ea1eec5a86c31`, `data_md5` `f7e79f29e1535a2bf4d1feefeadee410` (mẫu phát triển). Kết quả commit ở `91e464c`.
  Cấu hình chọn:

  | Mô hình | Cấu hình chọn | Epoch tốt nhất | NDCG@10 xác thực |
  |---|---|---|---|
  | Most Popular | — | — | 0,02174 |
  | MostPopular-Recent | W = 28 ngày | — | 0,02334 |
  | Content | half_life = 30 ngày | — | 0,00459 |
  | ItemKNN | k = 100, shrink = 50 | — | 0,02599 |
  | UserKNN | k = 200, shrink = 0 | — | 0,02753 |
  | BPR-MF | d = 128, lr = 0,03, reg = 0,001, 20 epoch | — | 0,02636 |
  | GMF | d = 32, lr = 1e-3, neg = 8, wd = 1e-6 | 7 | 0,02857 |
  | MLP | d = 32, lr = 1e-3, neg = 8, wd = 1e-6, dropout = 0 | 7 | 0,02742 |
  | NeuMF | d = 64, lr = 5e-4, neg = 4, wd = 1e-6, dropout = 0,2 | 4 | 0,02696 |
  | GMF-F | d = 32, lr = 1e-3, neg = 8, wd = 0, id_dropout = 0,25 | 8 | 0,03162 |
  | MLP-F | d = 32, lr = 1e-3, neg = 8, wd = 1e-6, dropout = 0, id_dropout = 0 | 10 | 0,03212 |
  | NeuMF-F | d = 32, lr = 1e-3, neg = 8, wd = 1e-6, dropout = 0, id_dropout = 0 | 4 | 0,03337 |
  | LateFusion-F | w = 0,4 (GMF-F), 1 − w = 0,6 (MLP-F) | — | 0,03556 |

- Không tinh chỉnh trên mẫu kiểm định. Không tinh chỉnh lại sau khi mở tập kiểm thử của mẫu kiểm định.

## 5. Đánh giá cuối trên mẫu kiểm định (`scripts/23_final_v2.py`)

- Cấu hình: `audit/v2/best_configs.json` của mẫu phát triển (mục 4), giữ nguyên.
- 5 seed: 42, 2024, 2025, 2026, 3407. Với mỗi seed:
  - Mạng nơ-ron (GMF, MLP, NeuMF, GMF-F, MLP-F, NeuMF-F): huấn luyện trên tập huấn luyện của giai đoạn xác thực của
    mẫu kiểm định, dừng sớm theo NDCG@10 xác thực (như lúc tinh chỉnh) để chọn số epoch e*; huấn luyện lại từ đầu trên
    mọi cặp trước mốc kiểm thử đúng e* epoch; chấm tập kiểm thử.
  - BPR-MF: khớp trên mọi cặp trước mốc kiểm thử, số epoch theo cấu hình.
  - Most Popular, MostPopular-Recent, Content, ItemKNN, UserKNN: khớp trên mọi cặp trước mốc kiểm thử (tất định, giống
    nhau ở mọi seed). Random theo seed.
  - LateFusion-F: trộn điểm của đúng GMF-F và MLP-F đã huấn luyện lại ở seed đó, w theo mục 4.
- Ablation (mục 3): chỉ seed 42, cùng quy trình, chấm cùng tập kiểm thử. Chỉ mô tả, không kiểm định, không dùng để
  chọn lại gì.
- Khoá kiểm thử: script từ chối chạy nếu file này chưa commit, thiếu `--reason`, có file đã theo dõi bị sửa mà chưa
  commit (trừ `outputs/` và `audit/test_access_log.csv` — do chính đánh giá cuối ghi, để chạy tiếp seed còn thiếu nếu bị
  ngắt), có file mã nguồn chưa được theo dõi trong `src/`, `scripts/`, `configs/`, tinh chỉnh chưa đủ mô hình, hoặc mã
  nguồn khác mã nguồn đã dùng khi tinh chỉnh (so `code_hash`). Mỗi seed ghi một dòng `audit/test_access_log.csv`
  (`run_tag` = `v2_kiemdinh_seed<N>`) **trước** khi chấm; seed đã có dòng nhật ký thì không chạy lại trừ khi có
  `--allow-rerun` (khi đó ghi vào mục 10 và báo cáo). Các dòng `v2_final_seed<N>` là lần mở khối 1, không tính.
- Ra: `outputs/v2/final/seed<N>/` (chỉ số, chỉ số theo từng người dùng kèm hạng của từng sản phẩm đúng, lịch sử huấn
  luyện, thông tin thời gian), top-20 và checkpoint của seed 42. Thư mục ra còn kết quả của dữ liệu khác (`data_md5`
  khác) thì script dừng, không ghi lẫn.

## 6. Độ đo

- Xếp hạng toàn bộ tập ứng viên của từng người dùng (khoảng 6,8 nghìn sản phẩm ở mẫu phát triển), hoà điểm phá bằng
  khoá giả ngẫu nhiên tất định (seed 2026). Trung bình theo người dùng.
- **Độ đo chính (kết luận): NDCG@10** trên tập kiểm thử của mẫu kiểm định.
- Độ đo phụ: Recall@10, HR@10, Precision@10, NDCG@5, NDCG@20.
- Mô tả thêm: độ phủ danh mục của top-10 (seed 42), số epoch chọn của từng seed, thời gian huấn luyện.

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
- Ablation: báo cáo trung bình và khoảng tin cậy bootstrap, không kiểm định, không dùng để kết luận chính.

## 8. Kết luận được phép

- Mô hình đề tài là NeuMF-F, cố định từ trước — không chọn lại theo kết quả kiểm thử.
- Câu trả lời cho câu hỏi chính dựa trên họ so sánh ở mục 7. **Nếu NeuMF-F không vượt baseline nào đó, báo cáo đúng
  như vậy**; không đổi độ đo, mẫu, họ so sánh hay tiêu chí sau khi xem kết quả.
- Kết quả v1 và kết quả trên khối 1 chỉ được nhắc như lịch sử phát triển, không gộp hay đặt cạnh kết quả trên mẫu kiểm
  định (dữ liệu khác: theo article, có sản phẩm mới).

## 9. Hạn chế đã biết lúc đăng ký

- k-core lọc trên mọi cặp trước mốc kiểm thử, nên tập người dùng/sản phẩm của giai đoạn xác thực phụ thuộc một phần
  vào dữ liệu tháng 7/2020. Điều này chỉ ảnh hưởng việc chọn cấu hình, không ảnh hưởng tập kiểm thử.
- `customers.csv` không có mốc thời gian: thuộc tính khách là ảnh chụp tại thời điểm công bố dữ liệu, giả định ít đổi.
- Vector văn bản được khớp (TF-IDF, SVD) trên toàn bộ danh mục; phép khớp không dùng dữ liệu mua.
- MostPopular-Recent và đặc trưng doanh số dùng giao dịch của toàn H&M trước mốc — dữ liệu mà doanh nghiệp có.
- Không còn sản phẩm mới: kết quả không nói về khả năng gợi ý sản phẩm vừa ra mắt (cold-start). Gợi ý ở mức mẫu sản
  phẩm, không ở mức màu.
- Ngân sách tinh chỉnh nhỏ (6 cấu hình mỗi mô hình có học). Vài cấu hình chọn nằm ở biên lưới: BPR-MF (d = 128 lớn
  nhất, reg = 0,001 nhỏ nhất), ItemKNN (shrink = 50 lớn nhất); mạng nơ-ron phần lớn chọn d = 32 (nhỏ nhất) và
  lr = 1e-3 (lớn nhất). Một số mô hình có thể còn tốt hơn nếu mở rộng lưới.
- Trên tập xác thực, các mô hình có đặc trưng chỉ chênh nhau 0,0005–0,0022 NDCG@10; thứ hạng giữa chúng trên tập xác
  thực không dùng để đoán kết quả kiểm thử.
- Ở lần đánh giá cuối trên khối 1, vài seed của GMF và MLP-F dừng ở epoch 1–2; GMF, MLP, MLP-F có độ phủ top-10 xấp
  xỉ Most Popular, tức gợi ý gần như toàn sản phẩm phổ biến. Số epoch chọn của từng seed được báo cáo (mục 6).
- Một mẫu kiểm định (khoảng 8 nghìn khách); kết luận áp dụng cho dữ liệu H&M và khung thời gian này.
- Máy chạy: AMD Ryzen 7 6800H, GPU NVIDIA RTX 3050 Laptop (CUDA), PyTorch 2.6.0. Ước lượng đánh giá cuối 6–8 giờ
  (theo thời gian tinh chỉnh). Chạy trên máy khác có thể lệch nhẹ ở chữ số cuối.

## 10. Lệch kế hoạch

(Chưa có.)
