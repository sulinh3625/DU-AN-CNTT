# Đăng ký trước (pre-registration) — kiểm chứng trên Amazon Beauty

Trạng thái: đăng ký ngày 10/10/2026, **trước khi chạy bất kỳ mô hình nào của giao thức này trên Amazon và trước khi mở
tập kiểm thử Amazon**. Đánh giá cuối (`python run.py amazon-final`) chỉ chạy được khi file này đã commit và không bị
sửa (`scripts/23_final_v2.py`).

Bản đăng ký đầu tiên (commit `e4a3365`) có bước tinh chỉnh trên tập xác thực Amazon. Cùng ngày, trước khi chạy gì,
nhóm quyết định **bỏ bước tinh chỉnh** và dùng cấu hình đã chọn trên H&M (mục 4).

## 0. Mục đích

Chạy lại giao thức v2 của H&M (`audit/PREREG_v2.md`) trên một bộ dữ liệu thứ hai, để xem kết luận rút ra từ H&M có còn
đúng ở chỗ khác không.

Giữ nguyên:
- mã nguồn và 14 mô hình;
- **siêu tham số đã chọn trên H&M** (không tinh chỉnh lại);
- số seed, độ đo, họ 10 so sánh và tiêu chí kết luận.

Chỉ khác dữ liệu, kèm những điều chỉnh bắt buộc do dữ liệu khác (mục 3).

Cấu hình: `configs/amazon.yaml`, chọn bằng `NEUMF_CONFIG=configs/amazon.yaml`. Các lệnh `python run.py amazon-*` tự
đặt biến này.

## 1. Dữ liệu

- **Nguồn:** Amazon review data 2014 (McAuley, Stanford SNAP), danh mục Beauty.
  - `data/raw/amazon/reviews_Beauty_5.json.gz` — bản 5-core: 198.502 đánh giá của 22.363 khách cho 12.101 sản phẩm,
    từ 12/06/2002 đến 23/07/2014;
  - `data/raw/amazon/meta_Beauty.json.gz` — metadata sản phẩm.
- **Tương tác:** mỗi đánh giá là một tương tác ẩn khách–sản phẩm, như một giao dịch H&M. Không dùng điểm sao.
- **Sản phẩm:** một sản phẩm là một `asin`, không gộp biến thể. Mã số = vị trí của asin trong danh sách đã sắp xếp
  (`src/data_pipeline/adapters/amazon.py`).
- **Chia theo thời gian:** chỉ có một bộ dữ liệu, nên chọn số epoch và đánh giá cuối dùng cùng một file nhưng khác giai
  đoạn.

  | Giai đoạn | Khoảng thời gian |
  |---|---|
  | Huấn luyện khi chọn số epoch | trước 01/10/2013 |
  | Xác thực (chỉ để chọn số epoch) | 01/10–31/12/2013 |
  | Huấn luyện lại trước đánh giá cuối | trước 01/01/2014 |
  | Kiểm thử | 01/01/2014–23/07/2014 |

  Mốc được chọn theo số đánh giá mỗi quý của toàn bộ file: kiểm thử là phần dữ liệu năm 2014, xác thực là quý ngay
  trước. Tỉ lệ độ dài xác thực : kiểm thử khoảng 1 : 2, như H&M. Lúc chọn mốc chưa chạy mô hình nào trên Amazon.
- **k-core = 5**, lọc trên các cặp trước 01/01/2014. Bằng k của bộ 5-core gốc; H&M dùng 10, nhưng Amazon thưa hơn
  nhiều.
- **Dữ liệu đã lọc:** `outputs/amazon/data/reviews_Beauty_5.csv.gz`, MD5 ghi trong `outputs/amazon/data/manifest.json`,
  tạo bằng `python run.py amazon-data`. Số liệu của lần chạy thật ngày 10/10/2026 (chỉ số liệu trước mốc kiểm thử):

  | | Giá trị |
  |---|---|
  | MD5 (CSV chưa nén) | `1bbee3d37f6f2d99717b02e13f49c285` |
  | Trước 01/01/2014 | 11.493 sản phẩm, 140.193 cặp |
  | Sau k-core 5 | 10.681 khách, 6.069 sản phẩm, 94.009 cặp |
  | Giai đoạn xác thực | 82.281 cặp huấn luyện, 6.039 sản phẩm chấm được, 3.153 khách có đáp án, 7.880 cặp đúng, trung bình 6.031 ứng viên mỗi khách |

## 2. Giao thức

Như `PREREG_v2.md` mục 2 (`src/data_pipeline/protocol_v2.py`):
- k-core chỉ trên các cặp trước mốc kiểm thử;
- ứng viên = sản phẩm có cặp huấn luyện trước mốc cắt, trừ sản phẩm khách đã có;
- đáp án = sản phẩm khách tương tác lần đầu trong cửa sổ sau mốc;
- xếp hạng trên toàn bộ ứng viên, phá hoà bằng khoá tất định (seed 2026).

## 3. Mô hình — giống H&M, trừ phần đặc trưng

14 mô hình như `PREREG_v2.md` mục 3. Phần đặc trưng đổi theo dữ liệu (`adapters/amazon.py`,
`scripts/21_build_features.py`):

| Thành phần | H&M | Amazon Beauty |
|---|---|---|
| Thuộc tính sản phẩm | 11 thuộc tính danh mục | 5 thuộc tính: thương hiệu, danh mục cấp 1, 2, 3 (dưới "Beauty"), nhóm giá (8 nhóm, 0 = không có giá) |
| Văn bản | tên + mô tả, TF-IDF + SVD 64 chiều | title + description, cùng TF-IDF + SVD 64 chiều |
| Đặc trưng thời gian của sản phẩm | doanh số toàn H&M 7/28/91 ngày trước t, tuổi sản phẩm | số đánh giá trong toàn bộ file 5-core 7/28/91 ngày trước t, tuổi tính từ đánh giá đầu tiên; chỉ đọc các ngày < t |
| Thông tin khách | 5 thuộc tính tĩnh + đặc trưng thời gian | **không có thuộc tính tĩnh**: nhánh khách chỉ còn đặc trưng thời gian (khoảng cách tới lần gần nhất, số cặp đã có) |
| Content | one-hot nhóm sản phẩm, nhóm chỉ mục, nhóm may mặc | one-hot danh mục cấp 1, cấp 2 |
| MostPopular-Recent | doanh số toàn H&M trong cửa sổ | số đánh giá trong cửa sổ |

Ablation NeuMF-F làm như H&M: tắt một nhóm đặc trưng, giữ siêu tham số, chỉ chạy seed 42, chỉ để mô tả. Riêng trên
Amazon:
- "Bỏ thông tin khách hàng" nghĩa là bỏ đặc trưng thời gian của khách, vì Amazon không có thuộc tính tĩnh.
- Biến thể "bỏ ID ngẫu nhiên" không chạy, vì cấu hình của NeuMF-F có `id_dropout = 0`.

## 4. Không tinh chỉnh — dùng cấu hình đã chọn trên H&M

**Cấu hình dùng lại:** `audit/v2/best_configs.json`, commit `91e464c`, MD5 sau khi chuẩn hoá xuống dòng LF
`b89b9d17771528e1355d8b3235b2dec8`. Đây là cấu hình được chọn trên tập xác thực của mẫu phát triển H&M. Không chạy
`scripts/22_tune_v2.py` trên Amazon (script tự dừng với `configs/amazon.yaml`).

| Mô hình | Cấu hình |
|---|---|
| MostPopular-Recent | window 28 |
| Content | half_life 30 |
| ItemKNN | k 100, shrink 50 |
| UserKNN | k 200, shrink 0 |
| BPR-MF | d 128, lr 0,03, reg 0,001, 20 epoch |
| GMF | d 32, lr 0,001, 8 mẫu âm, weight_decay 1e-6 |
| MLP | d 32, lr 0,001, 8 mẫu âm, weight_decay 1e-6, dropout 0 |
| NeuMF | d 64, lr 0,0005, 4 mẫu âm, weight_decay 1e-6, dropout 0,2 |
| GMF-F | d 32, lr 0,001, 8 mẫu âm, weight_decay 0, id_dropout 0,25 |
| MLP-F | d 32, lr 0,001, 8 mẫu âm, weight_decay 1e-6, dropout 0, id_dropout 0 |
| NeuMF-F | d 32, lr 0,001, 8 mẫu âm, weight_decay 1e-6, dropout 0, id_dropout 0 |
| LateFusion-F | w 0,4 (trộn GMF-F và MLP-F) |

Thứ duy nhất được chọn trên dữ liệu Amazon là **số epoch** của mạng nơ-ron. Việc chọn này nằm trong bước đánh giá cuối:
- huấn luyện trên các cặp trước 01/10/2013;
- dừng sớm theo NDCG@10 trên tập xác thực (tối đa 20 epoch, dừng sau 5 epoch không cải thiện);
- rồi huấn luyện lại từ đầu trên mọi cặp trước 01/01/2014, đúng số epoch đó.

## 5. Đánh giá cuối

Như `PREREG_v2.md` mục 5 (`scripts/23_final_v2.py`): 5 seed (42, 2024, 2025, 2026, 3407), ghi ra
`outputs/amazon/final/`.

Khoá kiểm thử gồm:
- file này đã commit;
- có `--reason`;
- tree sạch, nên `audit/v2/best_configs.json` cũng không bị sửa;
- mỗi seed ghi một dòng `amazon_kiemdinh_seed<N>` vào `audit/test_access_log.csv` trước khi chấm.

Không so mã băm mã nguồn với nhật ký tinh chỉnh, vì không có bước tinh chỉnh trên Amazon. Commit và mã băm của lần chạy
vẫn được ghi vào `results.json`. **Tập kiểm thử Amazon chỉ mở đúng một lần.**

## 6–7. Độ đo và kiểm định

Giống hệt `PREREG_v2.md` mục 6–7:
- NDCG@10 là độ đo chính, kèm Recall@10, HR@10, Precision@10, NDCG@5, NDCG@20;
- họ 10 so sánh cố định, Wilcoxon signed-rank, bootstrap ghép cặp 95%, hiệu chỉnh Holm;
- "A tốt hơn B" chỉ khi đồng thời: p Holm < 0,05, khoảng tin cậy không chứa 0, chênh lệch ≥ 5%.

Phân tích bằng `scripts/24_report_v2.py`, ra `outputs/amazon/final/ket_qua.txt` và các CSV.

## 8. Kết luận được phép

Trình bày là **kiểm chứng**: với từng kết luận của H&M, nói rõ trên Amazon nó còn đúng, ngược lại, hay không có khác
biệt có ý nghĩa. Ba kết luận cần đối chiếu:
1. mô hình có đặc trưng so với mô hình chỉ dùng ID;
2. NeuMF-F so với GMF-F, MLP-F, LateFusion-F;
3. NeuMF so với BPR-MF.

Mọi so sánh trên Amazon đều là so sánh **với cấu hình chọn trên H&M**. Nếu một mô hình kém đi, không tách được do mô
hình hay do cấu hình không hợp với Amazon, và phải viết rõ điều đó. Không gộp số của hai bộ dữ liệu, không chọn lại mô
hình đề tài hay tiêu chí sau khi xem kết quả. Kết quả Amazon ngược với H&M thì báo cáo đúng như vậy.

## 9. Hạn chế đã biết lúc đăng ký

- **Không tinh chỉnh cho Amazon:** siêu tham số chọn trên H&M có thể có lợi cho mô hình này và bất lợi cho mô hình
  khác khi chuyển sang Amazon (vd. kích thước embedding, số mẫu âm, k của KNN).
- **Dữ liệu đã lọc sẵn:** bộ 5-core thiên về khách và sản phẩm hoạt động nhiều. Đặc trưng thời gian của sản phẩm đếm
  trên chính file 5-core, không phải toàn bộ đánh giá Amazon.
- **Đánh giá không phải lần mua:** đánh giá không đồng nghĩa với mua. Amazon cũng không có thông tin khách, nên nhánh
  khách của NeuMF-F yếu hơn H&M.
- **Không có mẫu khách độc lập:** chỉ có một bộ dữ liệu, nên không có "mẫu khách độc lập" như H&M. Bước chọn số epoch
  và đánh giá cuối khác nhau theo thời gian, không khác nhau theo khách.
- **Một lần chạy thử trước khi đăng ký:** lúc 22:08 ngày 10/10/2026, một script khác (`scripts/promo_amazon.py`, nay
  không còn trong repo) đã chạy thử trên tập xác thực Amazon, chưa mở tập kiểm thử.
  - Lần chạy đó dùng mốc khác (01/07/2013 – 01/01/2014), 1 epoch, chỉ Random, MostPopular và BPR-MF.
  - Kết quả nằm ở `outputs/v2/amazon/`, ghi `"evaluated_on": "tap xac thuc (dry-run)"`.
  - Không quyết định nào trong file này dựa trên các số đó.
- **Mã nguồn đã sửa để chạy được Amazon:** thêm `day0` cho chỉ số ngày, cho phép nhánh khách không có thuộc tính, đưa
  cột one-hot của Content vào cấu hình. Với H&M, mặc định vẫn cho đúng hành vi cũ và các test cũ đều qua. Tuy vậy, mã
  băm mã nguồn đã khác lần đánh giá cuối H&M ngày 10/10/2026.
- **Nhóm giá là giá lúc thu thập dữ liệu** *(ghi thêm ngày 13/10/2026, sau đánh giá cuối; chỉ ghi nhận hạn chế, không
  đổi kế hoạch, cấu hình hay kết quả):* thuộc tính nhóm giá lấy từ trường `price` của `meta_Beauty.json.gz`, là giá tại
  thời điểm thu thập metadata (năm 2014), không phải giá tại ngày của từng đánh giá. Với đánh giá cũ, nhóm giá có thể
  khác giá lúc khách mua, và thuộc tính này mang một phần thông tin từ thời điểm sau ngày dự đoán — tương tự thuộc tính
  khách hàng của H&M chỉ có một ảnh chụp.

## 10. Lệch kế hoạch

1. **Thêm K = 15 và bảng đủ bốn độ đo ở K = 5, 10, 15, 20 (sau đánh giá cuối).** Như `PREREG_v2.md` mục 10.2: theo
   góp ý của GVHD (họp 04/10/2026), các số này tính lại từ hạng đã lưu ở lần đánh giá cuối (`by_k.csv`), không chấm lại
   tập kiểm thử, không đổi độ đo chính, họ so sánh hay tiêu chí kết luận; chỉ để mô tả, không kiểm định.
2. **Báo cáo bỏ K = 5 (24/10/2026).** Như `PREREG_v2.md` mục 10.3: chỉ trình bày K = 10, 15, 20; số @5 vẫn được lưu.
