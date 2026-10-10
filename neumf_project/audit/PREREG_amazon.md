# Đăng ký trước (pre-registration) — kiểm chứng trên Amazon Beauty

Trạng thái: đăng ký ngày 10/10/2026, **trước khi tinh chỉnh và trước khi mở tập kiểm thử Amazon**. Đánh giá cuối
(`python run.py amazon-final`) chỉ chạy được khi file này đã commit và không bị sửa (`scripts/23_final_v2.py`).

## 0. Mục đích

Chạy lại **đúng giao thức v2 của H&M** (`audit/PREREG_v2.md`) trên một bộ dữ liệu thứ hai để xem kết luận rút ra từ
H&M có còn đúng ở chỗ khác không. Giữ nguyên mã, 14 mô hình, lưới tinh chỉnh, số seed, độ đo, họ 10 so sánh và tiêu
chí kết luận. Chỉ khác dữ liệu, kèm những điều chỉnh bắt buộc do dữ liệu khác, liệt kê ở mục 3. Cấu hình:
`configs/amazon.yaml`, chọn bằng `NEUMF_CONFIG=configs/amazon.yaml`; các lệnh `python run.py amazon-*` tự đặt biến này.

## 1. Dữ liệu

- **Nguồn:** Amazon review data 2014 (McAuley, Stanford SNAP), danh mục Beauty.
  - `data/raw/amazon/reviews_Beauty_5.json.gz`: bản 5-core, gồm 198.502 đánh giá của 22.363 khách cho 12.101 sản
    phẩm, từ 12/06/2002 đến 23/07/2014.
  - `data/raw/amazon/meta_Beauty.json.gz`: metadata sản phẩm.
- **Tương tác:** mỗi đánh giá là một tương tác ẩn khách–sản phẩm, tương đương một giao dịch H&M. Không dùng điểm sao.
- **Sản phẩm:** một sản phẩm là một `asin`, không gộp biến thể. Mã số = vị trí của asin trong danh sách đã sắp xếp
  (`src/data_pipeline/adapters/amazon.py`).
- **Chia theo thời gian:** chỉ có một bộ dữ liệu, nên tinh chỉnh và đánh giá cuối dùng cùng một file nhưng khác giai
  đoạn.

  | Giai đoạn | Khoảng thời gian |
  |---|---|
  | Huấn luyện khi tinh chỉnh | trước 01/10/2013 |
  | Xác thực | 01/10–31/12/2013 |
  | Huấn luyện lại trước đánh giá cuối | trước 01/01/2014 |
  | Kiểm thử | 01/01/2014–23/07/2014 |

- **Cách chọn mốc:** theo số đánh giá mỗi quý của toàn bộ file. Kiểm thử là phần dữ liệu năm 2014, xác thực là quý ngay
  trước đó, giữ tỉ lệ độ dài xác thực : kiểm thử khoảng 1 : 2 như H&M. Lúc chọn mốc chưa chạy mô hình nào trên Amazon.
- **k-core = 5:** lọc trên các cặp trước 01/01/2014, bằng k của bộ 5-core gốc. H&M dùng 10, nhưng Amazon thưa hơn nhiều.
- **Dữ liệu đã lọc:** `outputs/amazon/data/reviews_Beauty_5.csv.gz`, có MD5 trong
  `outputs/amazon/data/manifest.json`, tạo bằng `python run.py amazon-data`. Số liệu của lần chạy thật ngày 10/10/2026
  (chỉ số liệu trước mốc kiểm thử):

  | | Giá trị |
  |---|---|
  | MD5 (CSV chưa nén) | `1bbee3d37f6f2d99717b02e13f49c285` |
  | Trước 01/01/2014 | 11.493 sản phẩm, 140.193 cặp |
  | Sau k-core 5 | 10.681 khách, 6.069 sản phẩm, 94.009 cặp |
  | Giai đoạn xác thực | 82.281 cặp huấn luyện, 6.039 sản phẩm chấm được, 3.153 khách có đáp án, 7.880 cặp đúng, trung bình 6.031 ứng viên mỗi khách |

## 2. Giao thức

Như `PREREG_v2.md` mục 2, `src/data_pipeline/protocol_v2.py`:
- k-core chỉ trên các cặp trước mốc kiểm thử;
- ứng viên = sản phẩm có cặp huấn luyện trước mốc cắt, trừ sản phẩm khách đã có;
- đáp án = sản phẩm khách tương tác lần đầu trong cửa sổ sau mốc;
- xếp hạng trên toàn bộ ứng viên, phá hoà bằng khoá tất định (seed 2026).

## 3. Mô hình — giống H&M, trừ phần đặc trưng

14 mô hình như `PREREG_v2.md` mục 3. Phần đặc trưng đổi theo dữ liệu (`adapters/amazon.py`, `scripts/21_build_features.py`):

| Thành phần | H&M | Amazon Beauty |
|---|---|---|
| Thuộc tính sản phẩm | 11 thuộc tính danh mục | 5 thuộc tính: thương hiệu, danh mục cấp 1, 2, 3 (dưới "Beauty"), nhóm giá (8 nhóm, 0 = không có giá) |
| Văn bản | tên + mô tả, TF-IDF + SVD 64 chiều | title + description, cùng TF-IDF + SVD 64 chiều |
| Đặc trưng thời gian của sản phẩm | doanh số toàn H&M 7/28/91 ngày trước t, tuổi sản phẩm | số đánh giá trong toàn bộ file 5-core 7/28/91 ngày trước t, tuổi tính từ đánh giá đầu tiên; chỉ đọc các ngày < t |
| Thông tin khách | 5 thuộc tính tĩnh + đặc trưng thời gian | **không có thuộc tính tĩnh**: nhánh khách chỉ còn đặc trưng thời gian (khoảng cách tới lần gần nhất, số cặp đã có) |
| Content | one-hot nhóm sản phẩm, nhóm chỉ mục, nhóm may mặc | one-hot danh mục cấp 1, cấp 2 |
| MostPopular-Recent | doanh số toàn H&M trong cửa sổ | số đánh giá trong cửa sổ |

Ablation NeuMF-F như H&M:
- tắt một nhóm đặc trưng, cùng siêu tham số, chỉ seed 42, chỉ mô tả;
- "bỏ thông tin khách hàng" trên Amazon nghĩa là bỏ đặc trưng thời gian của khách;
- biến thể "bỏ ID ngẫu nhiên" chỉ chạy khi cấu hình chọn có `id_dropout > 0`.

## 4. Tinh chỉnh

Như `PREREG_v2.md` mục 4, `scripts/22_tune_v2.py`:
- cùng lưới, 6 cấu hình mỗi mô hình (cấu hình mặc định + 5 cấu hình rút cố định, `grid_seed` 0);
- seed 42, tối đa 20 epoch, dừng sớm sau 5 epoch không cải thiện NDCG@10 trên tập xác thực;
- chọn cấu hình theo NDCG@10 trên tập xác thực.

Nhật ký: `audit/amazon/tuning_log.csv` và `best_configs.json`. Không dựng tập kiểm thử. Không dùng cấu hình đã chọn
trên H&M.

## 5. Đánh giá cuối

Như `PREREG_v2.md` mục 5, `scripts/23_final_v2.py`:
- 5 seed: 42, 2024, 2025, 2026, 3407;
- mạng nơ-ron chọn số epoch trên tập xác thực rồi huấn luyện lại từ đầu trên mọi cặp trước 01/01/2014;
- kết quả ghi vào `outputs/amazon/final/`.

Khoá kiểm thử:
- file này đã commit;
- có `--reason`;
- tree sạch;
- mã băm mã nguồn trùng lúc tinh chỉnh Amazon;
- mỗi seed ghi một dòng `amazon_kiemdinh_seed<N>` vào `audit/test_access_log.csv` trước khi chấm.

**Tập kiểm thử Amazon chỉ mở đúng một lần.**

## 6–7. Độ đo và kiểm định

Giống hệt `PREREG_v2.md` mục 6–7:
- NDCG@10 là độ đo chính, kèm Recall@10, HR@10, Precision@10, NDCG@5, NDCG@20;
- họ 10 so sánh cố định, Wilcoxon signed-rank, bootstrap ghép cặp 95%, hiệu chỉnh Holm;
- "A tốt hơn B" chỉ khi đồng thời: p Holm < 0,05, khoảng tin cậy không chứa 0, chênh lệch ≥ 5%;
- phân tích: `scripts/24_report_v2.py` ra `outputs/amazon/final/ket_qua.txt` cùng các CSV.

## 8. Kết luận được phép

- Trình bày là **kiểm chứng**: với từng kết luận của H&M, cho biết trên Amazon kết luận đó còn đúng, ngược lại, hay
  không có khác biệt có ý nghĩa. Ba kết luận cần đối chiếu:
  1. mô hình có đặc trưng so với mô hình chỉ dùng ID;
  2. NeuMF-F so với GMF-F, MLP-F, LateFusion-F;
  3. NeuMF so với BPR-MF.
- Không gộp số của hai bộ dữ liệu. Không chọn lại mô hình đề tài hay tiêu chí sau khi xem kết quả. Kết quả Amazon
  ngược với H&M thì báo cáo đúng như vậy.

## 9. Hạn chế đã biết lúc đăng ký

- Bộ 5-core đã được lọc sẵn theo số đánh giá, thiên về khách và sản phẩm hoạt động nhiều. Đặc trưng thời gian của sản
  phẩm đếm trên chính file 5-core, không phải toàn bộ đánh giá Amazon.
- Đánh giá không đồng nghĩa với mua. Không có thông tin khách, nên nhánh khách của NeuMF-F yếu hơn H&M.
- Chỉ một bộ dữ liệu nên không có "mẫu khách độc lập" như H&M. Tinh chỉnh và đánh giá cuối khác nhau theo thời gian,
  không khác nhau theo khách.
- **Lần chạy thử trước khi đăng ký.** Ngày 10/10/2026 lúc 22:08, một script khác (`scripts/promo_amazon.py`, nay không
  còn trong repo) đã chạy thử trên tập xác thực Amazon, với mốc khác (01/07/2013 – 01/01/2014), 1 epoch, chỉ Random,
  MostPopular và BPR-MF. Kết quả của nó nằm ở `outputs/v2/amazon/`, ghi `"evaluated_on": "tap xac thuc (dry-run)"`;
  không mở tập kiểm thử. Không quyết định nào trong file này dựa trên các số đó.
- **Mã nguồn có thay đổi** để chạy được Amazon:
  - `day0` cho chỉ số ngày;
  - nhánh khách không có thuộc tính;
  - cột one-hot của Content theo cấu hình.

  Với H&M, mặc định vẫn cho đúng hành vi cũ, các test cũ đều qua. Nhưng mã băm mã nguồn đã khác lần đánh giá cuối H&M
  ngày 10/10/2026.

## 10. Lệch kế hoạch

(chưa có)
