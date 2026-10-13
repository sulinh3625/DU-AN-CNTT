# Tổng hợp giao thức v2: đồ án làm gì, kết quả, mức độ hoàn thành

Cập nhật: 10/10/2026, **sau đánh giá cuối của bản cuối giao thức v2** trên mẫu kiểm định B (khối 2; 5/5 seed, chạy
10/10/2026 trên GPU RTX 3050). Kết quả trên khối 1 (04/10/2026) chỉ còn là lịch sử (mục 1.4).

---

## 1. Đồ án đang làm gì và vì sao

### 1.1 Đồ án làm gì — nói ngắn

- **Bài toán:** với mỗi khách hàng H&M, gợi ý 10 sản phẩm thời trang họ có khả năng mua lần đầu trong 8 tuần tới,
  chỉ dựa vào lịch sử mua (không có điểm đánh giá). Một sản phẩm là một **mẫu thiết kế** (`product_code`, gộp mọi màu).
- **Mô hình đề tài — NeuMF-F:** mô hình lai giữ đúng khung của NeuMF (nhánh nhân tử hoá ma trận GMF + nhánh mạng nơ-ron
  sâu MLP, hợp nhất sớm), nhưng mỗi khách/sản phẩm không chỉ có vector ID mà còn có **đặc trưng**: thuộc tính và mô tả
  sản phẩm, thông tin khách, doanh số và thời gian.
- **Cách chứng minh:** so NeuMF-F với 13 mô hình khác trên **cùng** một tập kiểm thử, theo một kế hoạch ghi sẵn từ trước
  (`neumf_project/audit/PREREG_v2.md`), trên một nhóm khách hàng chưa từng được dùng để ra quyết định (mẫu B).

### 1.2 Vì sao phải làm như vậy

| Việc làm | Lý do |
|---|---|
| Lai **MF + DNN** (GMF + MLP) | Đúng tên đề tài. MF chỉ học tương tác tuyến tính (tích vô hướng); DNN học tương tác phi tuyến. NeuMF (He et al., 2017) là kiến trúc chuẩn ghép hai nhánh này |
| Thêm **đặc trưng** vào NeuMF | Ở v1, NeuMF chỉ dùng ID **không** hơn MF đã tinh chỉnh (0/8 so sánh có ý nghĩa). Vector ID chỉ học được từ lượt mua, nên với dữ liệu thưa, sản phẩm/khách ít lượt mua học được rất ít; phải thêm thông tin về chính sản phẩm/khách (loại hàng, xu hướng bán, nhóm khách) thì mô hình mới có cái để học thêm |
| **Một sản phẩm = một mẫu thiết kế**; ứng viên là sản phẩm đã có người mua trước mốc | Theo góp ý của cô (09/10/2026). Mọi mô hình — kể cả mô hình chỉ dùng ID — chấm được mọi ứng viên, nên so sánh không phụ thuộc khả năng xử lý sản phẩm chưa có lịch sử bán |
| Chia **theo thời gian**, không leave-one-out | Leave-one-out để lọt thông tin tương lai: đo trên mẫu A, 11,2% dữ liệu huấn luyện xảy ra **sau** món cần dự đoán |
| **Hai mẫu khách A/B** | Tập test của mẫu A đã bị xem nhiều lần ở v1. Mọi quyết định (chọn cấu hình) làm trên A; kết luận lấy trên B — khách khác hẳn, test chỉ mở một lần |
| Dữ liệu đã lọc ghi ra **file có MD5** | Mọi mô hình đọc đúng cùng một file; chương trình kiểm MD5 trước khi dùng |
| **Đăng ký trước** + khoá test | Mô hình, lưới tinh chỉnh, độ đo, 10 so sánh và tiêu chí "tốt hơn" cố định trước khi xem kết quả, nên không thể chọn lại sau khi thấy số |
| **14 mô hình**, cùng ngân sách tinh chỉnh | Muốn nói "lai có tác dụng" thì phải so với: bản chỉ dùng ID (đặc trưng có giúp không), từng nhánh riêng (lai có hơn từng phần không), hợp nhất muộn (sớm hay muộn), và baseline mạnh (KNN, BPR-MF, phổ biến gần đây) |
| **5 seed**, kiểm định theo từng khách | Mạng nơ-ron dao động theo seed. Kiểm định Wilcoxon + bootstrap trên ~3.000 khách, hiệu chỉnh Holm cho 10 so sánh; với 5 seed, kiểm định theo seed không bao giờ đạt p < 0,05 |
| **Ablation**, độ phủ | Biết thành phần nào của NeuMF-F đóng góp, và danh sách gợi ý có đa dạng không |

### 1.3 Vì sao đổi từ v1 sang v2

Giao thức v1 (mẫu A, chỉ ID) có ba vấn đề:

1. NeuMF chỉ dùng ID không vượt được MF đã tinh chỉnh (0/8 so sánh có ý nghĩa).
2. Lọc k-core dùng cả dữ liệu của giai đoạn test.
3. Tập test của mẫu A đã bị xem nhiều lần (27/09, 29/09/2026), một số quyết định đưa ra sau khi xem.

v1 được giữ làm **lịch sử phát triển** (báo cáo mục 4.5); số v1 và số v2 không đặt cạnh nhau vì khác mẫu khách, khác
tập ứng viên và khác đáp án.

### 1.4 Vì sao có bản cuối (khối 2, `product_code`)

Bản v2 đầu (kế hoạch `audit/PREREG_v2_cu.md`, 03/10/2026) tính mỗi `article_id` (từng màu) là một sản phẩm, đưa cả
sản phẩm mới (chưa từng bán trước mốc) vào tập ứng viên, và đánh giá trên **khối 1**. Tập test của khối 1 được mở ngày
04/10/2026. Kết quả khối 1 (lịch sử, không dùng để kết luận): NeuMF-F đứng 3/14, LateFusion-F tốt hơn NeuMF-F có ý nghĩa
(−16,1%), và NDCG@10 trên nhóm sản phẩm mới của mọi mô hình đều dưới 0,002.

Theo góp ý của cô và quyết định của nhóm ngày 09/10/2026, kế hoạch đổi thành **bản cuối** (`audit/PREREG_v2.md` mục 0):

1. Một sản phẩm = một `product_code` (gộp mọi màu của cùng một mẫu).
2. Bỏ sản phẩm chưa có người mua khỏi tập ứng viên và đáp án (không còn phân tích sản phẩm cũ/mới).
3. Dữ liệu đã lọc ghi ra file, mọi mô hình đọc cùng file và kiểm MD5.
4. Đánh giá cuối trên **mẫu kiểm định mới — khối 2**.

Vì các thay đổi này được quyết định **sau khi đã xem kết quả khối 1**, khối 1 không còn dùng để kết luận; mô hình được
tinh chỉnh lại trên mẫu A theo dữ liệu mới, và kế hoạch bản cuối được commit trước khi dựng tập test của khối 2.

---

## 2. Kết quả đánh giá cuối (mẫu B = khối 2)

### 2.1 Lần chạy

| Mục | Giá trị |
|---|---|
| Ngày, máy | 10/10/2026; GPU NVIDIA RTX 3050 Laptop (AMD Ryzen 7 6800H), PyTorch 2.6.0; 5 seed tổng 7,5 giờ |
| Truy vết | Commit `e4e4f25`, mã nguồn không có thay đổi chưa lưu, mã băm mã nguồn `0f1ea1eec5a86c31` trùng lúc tinh chỉnh, dữ liệu `data_md5` `ba5498d1…` |
| Lệch kế hoạch | Lần chạy đầu dừng giữa chừng ở seed 42 (đã chấm Random và 5 mô hình tất định, chưa lưu kết quả nào) → seed 42 chạy lại một lần (`--allow-rerun`), ghi ở `PREREG_v2.md` mục 10 và dòng `v2_kiemdinh_seed42_rerun` của nhật ký. Các seed khác mở test đúng một lần |
| Mẫu B sau lọc | 7.994 khách, 6.749 sản phẩm (mẫu thiết kế), 243.696 cặp |
| Tập kiểm thử | 3.165 khách được đánh giá; 10.285 cặp đúng; trung bình 6.710 sản phẩm ứng viên mỗi khách |
| File | `neumf_project/outputs/v2/final/` (`summary.csv`, `significance.csv`, `ablation.csv`, `beyond.csv`, `data.json`, `seed*/`); bảng dạng chữ: `ket_qua.txt` |

### 2.2 Bảng 2 — NDCG@10 trên tập kiểm thử mẫu B (trung bình ± độ lệch chuẩn, 5 seed)

| Hạng | Mô hình | Test | Val (mẫu A) |
|---|---|---|---|
| 1 | **LateFusion-F** | **0,04093 ± 0,00212** | **0,03556** |
| 2 | **NeuMF-F** (đề tài) | 0,04003 ± 0,00147 | 0,03337 |
| 3 | GMF-F | 0,03902 ± 0,00124 | 0,03162 |
| 4 | MLP-F | 0,03480 ± 0,00177 | 0,03212 |
| 5 | UserKNN | 0,03114 | 0,02753 |
| 6 | ItemKNN | 0,02860 | 0,02599 |
| 7 | NeuMF (chỉ ID) | 0,02783 ± 0,00109 | 0,02696 |
| 8 | MostPopular-Recent | 0,02760 | 0,02334 |
| 9 | GMF | 0,02695 ± 0,00311 | 0,02857 |
| 10 | BPR-MF | 0,02661 ± 0,00114 | 0,02636 |
| 11 | MLP | 0,02373 ± 0,00207 | 0,02742 |
| 12 | Most Popular | 0,02184 | 0,02174 |
| 13 | Content | 0,00506 | 0,00459 |
| 14 | Random | 0,00098 ± 0,00040 | — |

Mô hình không có độ lệch chuẩn là mô hình tất định (giống nhau ở mọi seed). HR@10 của NeuMF-F là 15,0%, của
LateFusion-F là 15,8% — khoảng 1/6 số khách có ít nhất một món đúng trong 10 gợi ý. Cột Val chỉ để chọn cấu hình, không
cùng thang với cột Test (khác mẫu khách, cửa sổ kiểm thử dài gấp đôi).

### 2.3 Họ 10 so sánh đăng ký trước

"A tốt hơn B" chỉ khi đủ cả ba: p sau Holm < 0,05; khoảng tin cậy 95% không chứa 0; chênh lệch ≥ 5%.

| # | So sánh | Chênh lệch NDCG@10 | p Holm | Kết luận |
|---|---|---|---|---|
| 1 | NeuMF-F vs NeuMF | +43,8% | < 0,001 | **NeuMF-F tốt hơn** |
| 2 | NeuMF-F vs GMF-F | +2,6% | 0,735 | Không khác biệt có ý nghĩa |
| 3 | NeuMF-F vs MLP-F | +15,0% | 0,003 | **NeuMF-F tốt hơn** |
| 4 | NeuMF-F vs LateFusion-F | −2,2% | 0,735 | Không khác biệt có ý nghĩa |
| 5 | NeuMF-F vs BPR-MF | +50,4% | < 0,001 | **NeuMF-F tốt hơn** |
| 6 | NeuMF-F vs ItemKNN | +39,9% | < 0,001 | **NeuMF-F tốt hơn** |
| 7 | NeuMF-F vs UserKNN | +28,5% | < 0,001 | **NeuMF-F tốt hơn** |
| 8 | NeuMF-F vs MostPopular-Recent | +45,0% | < 0,001 | **NeuMF-F tốt hơn** |
| 9 | NeuMF-F vs Content | +691,5% | < 0,001 | **NeuMF-F tốt hơn** |
| 10 | NeuMF vs BPR-MF | +4,6% | 0,059 | Không khác biệt có ý nghĩa |

**Tổng: 7/10 so sánh đạt tiêu chí. NeuMF-F tốt hơn 7/9 đối thủ, ngang 2 (GMF-F, LateFusion-F), không thua mô hình nào.**

### 2.4 Phân tích phụ (chỉ mô tả, không kiểm định)

- **Ablation NeuMF-F (seed 42, đầy đủ = 0,04137):** bỏ **đặc trưng thời gian −42,3%** (khoảng tin cậy không chứa 0 —
  thành phần quan trọng nhất); bỏ **thông tin khách −10,3%** (khoảng tin cậy cũng không chứa 0); bỏ thuộc tính sản phẩm
  −3,7% và bỏ văn bản −2,7% (khoảng tin cậy chứa 0). Biến thể "bỏ cơ chế bỏ ID ngẫu nhiên" **không chạy** vì trùng hệt
  NeuMF-F (tinh chỉnh chọn ρ = 0), nên ablation còn 4 biến thể.
- **Độ phủ top-10 (seed 42):** Most Popular và MostPopular-Recent thấp nhất (0,3%); trong mô hình cá nhân hoá, MLP thấp
  nhất (3,3%); NeuMF-F 13,3% — cao nhất trong các mạng nơ-ron, sau ItemKNN (20,4%) và Content (78,2%). LateFusion-F 5,3%.
- **Thời gian huấn luyện mỗi seed (GPU):** NeuMF-F 15,2 phút, GMF-F 13,7, MLP-F 16,4, NeuMF 6,2, BPR-MF 4,3.
- **Ổn định giữa hai mẫu:** bốn mô hình có đặc trưng đứng đầu ở cả tinh chỉnh (A) lẫn test (B); LateFusion-F và NeuMF-F
  giữ hai vị trí đầu. GMF và MLP chỉ dùng ID tụt từ hạng 5 và 7 xuống 9 và 11 (hai mô hình duy nhất có NDCG@10 test thấp
  hơn val); ItemKNN lên từ hạng 10 lên 6.

### 2.5 Trả lời câu hỏi nghiên cứu

| Câu hỏi | Trả lời |
|---|---|
| Đặc trưng có cải thiện mô hình lai không? | **Có** — NeuMF-F hơn NeuMF chỉ ID 43,8%, có ý nghĩa. Phần lớn nhờ đặc trưng thời gian, tiếp theo là thông tin khách |
| Lai có hơn từng nhánh đứng riêng không? | **Hơn nhánh DNN** (MLP-F, +15,0%); **không hơn nhánh MF** (GMF-F, +2,6%, không có ý nghĩa) |
| Hợp nhất sớm hay muộn? | **Không khác biệt có ý nghĩa** — LateFusion-F cao hơn NeuMF-F 2,2% (p Holm 0,735) |
| NeuMF-F so với baseline? | Hơn cả 5 baseline trong họ so sánh: BPR-MF, ItemKNN, UserKNN, MostPopular-Recent, Content |
| NeuMF chỉ ID so với MF? | Không khác biệt có ý nghĩa — cùng kết luận với v1, trên mẫu khách mới |

### 2.6 Điểm cần nói thật khi bảo vệ

1. **NeuMF-F không phải mô hình có NDCG@10 cao nhất.** LateFusion-F cao hơn một chút (0,04093 so với 0,04003), nhưng
   chênh lệch **không có ý nghĩa**. NeuMF-F là mô hình đề tài cố định từ trước (PREREG_v2 mục 8), không chọn lại theo
   kết quả. Lợi ích chủ yếu đến từ **đặc trưng**, không từ cách ghép hai nhánh (NeuMF-F ngang GMF-F đứng riêng).
2. **Bản cuối được quyết định sau khi xem kết quả khối 1** (mục 1.4). Vì vậy khối 1 bị loại và kết luận lấy trên khối 2 —
   chưa ai xem; kế hoạch bản cuối commit trước khi dựng tập test của khối 2. Nói thẳng điều này nếu được hỏi.
3. **Seed 42 chạy lại một lần** (lần đầu dừng giữa chừng): đã ghi lệch kế hoạch; không quyết định nào đưa ra sau khi thấy
   các số trên màn hình; 5 mô hình tất định cho cùng kết quả ở lần chạy lại.
4. **Không còn sản phẩm mới** trong đánh giá: không được nói đề tài "xử lý khởi đầu lạnh của sản phẩm" hay NeuMF-F "chấm
   được sản phẩm mới" như một kết quả. Cơ chế bỏ ID ngẫu nhiên có trong thiết kế nhưng NeuMF-F và MLP-F chọn ρ = 0 (chỉ
   GMF-F chọn ρ = 0,25).
5. **Kết quả khối 1 khác bản cuối** (khối 1: LateFusion-F tốt hơn NeuMF-F có ý nghĩa; bản cuối: không khác biệt). Hai lần
   khác dữ liệu (theo màu, có sản phẩm mới) — chỉ bản cuối dùng để kết luận; không đặt số hai lần cạnh nhau.

---

## 3. Thay đổi của giao thức v2 (bản cuối)

### 3.1 Dữ liệu và giao thức

| Thay đổi | Nội dung | File |
|---|---|---|
| Mẫu kiểm định B | Khối 2: 500.164 giao dịch, 21.351 khách, nhóm băm [3160, 4734), **không có khách chung** với mẫu A (khối 0: 500.269 giao dịch, 21.599 khách). Khối 1 đã mở, không dùng. MD5 hai mẫu ghi trong kế hoạch đăng ký trước | `scripts/00_sample_hm.py` (`--block 0`, `--block 2`) |
| Gộp theo mẫu thiết kế | `product_code` = `article_id // 1000`. Trước mốc test: mẫu A 55.971 → 27.370 sản phẩm, 401.293 → 359.181 cặp; mẫu B 55.683 → 27.291 sản phẩm, 398.653 → 356.740 cặp | `scripts/02_prepare_data.py` |
| Dữ liệu đã lọc | Lọc 10-core chỉ trên cặp trước mốc test (29/07/2020), ghi `outputs/data/<mẫu>.csv.gz` + MD5 trong `manifest.json`; mọi mô hình đọc cùng file | `scripts/02_prepare_data.py`, `src/data_pipeline/protocol_v2.py` |
| Đặc trưng | Mỗi sản phẩm: 11 thuộc tính danh mục (3 thuộc tính màu là hằng số sau khi gộp), vector mô tả văn bản 64 chiều (TF-IDF → SVD), 5 đặc trưng thời gian (doanh số toàn H&M 7/28/91 ngày, tuổi sản phẩm, cờ chưa từng bán). Mỗi khách: 5 thuộc tính, 2 đặc trưng thời gian | `src/data_pipeline/features.py`, `scripts/21_build_features.py` |
| Chống rò rỉ thời gian | Đặc trưng tại ngày t chỉ dùng dữ liệu **trước** t; mẫu âm chỉ lấy trong sản phẩm đã ra mắt tại ngày mua | `features.py`, `src/data_pipeline/feature_dataset.py` |
| Giai đoạn đánh giá | Tập ứng viên = sản phẩm có ít nhất một cặp huấn luyện trước mốc, trừ món khách đã mua; đáp án chỉ gồm sản phẩm thuộc tập ứng viên | `src/data_pipeline/protocol_v2.py` |
| Cấu hình | Mốc thời gian, k = 10, 5 seed, ngân sách tinh chỉnh | `configs/v2.yaml` |

### 3.2 Mô hình

| Mô hình | Vai trò | File |
|---|---|---|
| **NeuMF-F** | Mô hình đề tài. Hai nhánh GMF-F + MLP-F hợp nhất sớm; mỗi vector = Embedding ID + chiếu tuyến tính của đặc trưng. Có tuỳ chọn bỏ ID sản phẩm ngẫu nhiên khi huấn luyện (ρ ∈ {0; 0,25; 0,5}; tinh chỉnh chọn ρ = 0) | `src/models/hybrid_features.py` |
| GMF-F, MLP-F | Từng nhánh của NeuMF-F đứng riêng — đo "lai có hơn từng nhánh không" (GMF-F chọn ρ = 0,25, MLP-F chọn ρ = 0) | như trên |
| LateFusion-F | Hợp nhất muộn: trộn điểm GMF-F (w = 0,4) và MLP-F (1 − w = 0,6) huấn luyện riêng, w chọn trên tập xác thực | `src/models/late_fusion.py` |
| GMF, MLP, NeuMF (chỉ ID) | Kiến trúc NCF gốc — đo "đặc trưng có giúp không" | `src/models/neumf.py` |
| Baseline | Random, Most Popular, **MostPopular-Recent** (W = 28 ngày), **Content**, ItemKNN (k = 100), UserKNN (k = 200), BPR-MF | `hybrid_features.py`, `src/baselines/` |
| Ablation NeuMF-F | Lần lượt bỏ: văn bản, thời gian, thông tin khách, thuộc tính sản phẩm (biến thể "bỏ cơ chế bỏ ID ngẫu nhiên" trùng NeuMF-F nên không chạy) | `scripts/v2_common.py` |

Tổng cộng **14 mô hình**, cùng ngân sách tinh chỉnh (6 cấu hình mỗi mô hình có học).

### 3.3 Quy trình thực nghiệm

| Bước | Nội dung | File |
|---|---|---|
| Đăng ký trước | Mô hình, lưới tinh chỉnh, 5 seed, độ đo chính NDCG@10, **họ 10 so sánh** (Wilcoxon + bootstrap + Holm), tiêu chí "tốt hơn", hạn chế đã biết; mục 10 ghi lệch kế hoạch | `neumf_project/audit/PREREG_v2.md` |
| Tinh chỉnh | Chỉ trên tập xác thực của A (09/10 23:17 → 10/10 03:58, 76 cấu hình, 4,7 giờ). Nhật ký mỗi cấu hình kèm **mã băm nội dung mã nguồn** và `data_md5` | `scripts/22_tune_v2.py` |
| Đánh giá cuối | Khoá test từ chối chạy nếu: kế hoạch chưa commit, thiếu lý do, mã nguồn có thay đổi, mã băm khác lúc tinh chỉnh, hoặc seed đã mở test (trừ khi `--allow-rerun`). Mỗi seed ghi nhật ký trước khi chấm | `scripts/23_final_v2.py` |
| Kiểm định và xuất báo cáo | Bảng, hình, macro LaTeX, `ket_qua.txt` tự sinh — không gõ tay số | `scripts/24_report_v2.py` |
| Đối chiếu báo cáo | 31 câu nhận xét bằng chữ của báo cáo được kiểm trên file kết quả; báo macro, bảng, hình còn thiếu | `scripts/19_check_report.py` |
| Lệnh tắt | `sample-hm`, `v2-data`, `prepare`, `v2-tune`, `v2-dry-run`, `v2-final`, `v2-report`, `check-report`, `demo` | `run.py` |

### 3.4 Demo

- Chỉ còn chế độ của đánh giá cuối: checkpoint seed 42 (`outputs/v2/final/seed42/`), sản phẩm theo mẫu thiết kế (tên và
  ảnh của màu đầu tiên, kèm số màu), mặc định so NeuMF-F với NeuMF; thẻ 10 khách tương đồng (UserKNN); dashboard đọc
  `outputs/v2/final/*.csv`. Demo chỉ phục vụ khách đã có lịch sử mua.

### 3.5 Kiểm thử

- `tests/` (94 test): đặc trưng không dùng dữ liệu tương lai, mẫu âm hợp lệ; k-core chỉ dùng dữ liệu trước mốc test;
  gộp theo `product_code`; file dữ liệu tất định và kiểm MD5; NeuMF-F cho cùng điểm lúc huấn luyện và lúc đánh giá; khoá
  test, tiêu chí kết luận, họ so sánh; câu chữ báo cáo khớp số liệu.
- `demo/tests/` (10 test): 4 test không cần dữ liệu (bảng sản phẩm, danh sách khách, từ chối kết quả của dữ liệu khác);
  6 test nạp checkpoint (khớp số theo từng khách với file kết quả, lịch sử, láng giềng, dashboard).
- **Kết quả ngày 10/10:** 98/98 qua (94 test của `tests/` và 4 test demo không cần dữ liệu). 6 test demo nạp checkpoint
  **chưa chạy** — chạy bằng `py -m pytest demo/tests -q`.

### 3.6 Dọn mã (10/10/2026)

- Xoá toàn bộ mã, cấu hình, test, notebook và kết quả của giao thức v1, cùng kết quả khối 1 (`outputs/v2/final_cu/`);
  tất cả vẫn nằm trong lịch sử git (commit `9799f1a`, tag cục bộ `truoc-don-dep`). Giữ `audit/PREREG.md` và
  `audit/PREREG_v2_cu.md` vì `PREREG_v2.md` dẫn tới.
- Bỏ phần tính chỉ số sản phẩm cũ/mới khỏi `evaluate_v2` (không còn sản phẩm mới); chỉ số chính không đổi (đã so với bản
  cũ: trùng từng số).
- Vì mã nguồn đã đổi, mã băm hiện tại khác `0f1ea1eec5a86c31` của lần chạy; kết quả gắn với commit `e4e4f25`.

---

## 4. Báo cáo (`Report DACNTT/`)

| Phần | Trạng thái |
|---|---|
| Chương 1–3 | Viết theo bản cuối (khối 2, `product_code`, tập ứng viên không có sản phẩm mới). Còn thiếu 2 ảnh chụp demo (`media/figures/demo/demo_v2.png`, `demo_v2_neighbors.png`) |
| Chương 4 | Kết quả, kiểm định, ablation, độ phủ, ổn định giữa hai mẫu, lệch kế hoạch, lịch sử (v1 và khối 1), giới hạn, thảo luận — viết theo số ngày 10/10; mọi số qua macro tự sinh |
| Chương 5, tóm tắt Việt/Anh, phụ lục | Viết theo kết quả mới |
| Đối chiếu | `python run.py check-report`: 31/31 câu nhận xét khớp số liệu, đủ macro và bảng; chỉ thiếu 2 ảnh demo |
| Biên dịch | `main.pdf` hiện là bản cũ — cần biên dịch lại (`compile.bat`, máy có MiKTeX) |

---

## 5. Tài liệu đi kèm

- `README.md` (gốc), `neumf_project/README.md`, `neumf_project/pham_vi_du_an.md`, `neumf_project/demo/README.md`: viết
  theo bản cuối; v1 và khối 1 chỉ còn mục lịch sử. Cập nhật 10/10.
- `van_dap.md`: trả lời 17 góp ý theo kết quả ngày 10/10 (thêm câu hỏi khó về bản cuối, khối 1 và việc chạy lại seed 42).
- `neumf_project/outputs/v2/final/ket_qua.txt`: bảng dạng chữ — kết quả chính, NDCG theo K, 10 so sánh, ablation, độ phủ
  và số epoch.

---

## 6. Thay đổi giai đoạn trước (giao thức v1)

- **Thuật ngữ theo luận án của GVHD:** NeuMF là Early Fusion; Late Fusion là trộn điểm của các mô hình huấn luyện riêng;
  MLP đứng riêng là DNN thuần. Đã sửa trong code và báo cáo.
- **Trình bày:** chú thích bảng/hình tiếng Việt, bỏ so sánh với số liệu bài báo.
- **Kết quả v1** (lịch sử, lịch sử git commit `9799f1a`): BPR-MF cao nhất; 0/8 so sánh có ý nghĩa; tiền huấn luyện không
  giúp.

---

## 7. Hiệu quả so với v1

| Tiêu chí | v1 | v2 (bản cuối) |
|---|---|---|
| Độ tin cậy số liệu | Test đã xem nhiều lần; nhiều quyết định sau khi xem | Mẫu B độc lập (khối 2), mở test một lần (seed 42 chạy lại một lần, đã ghi lệch kế hoạch), đăng ký trước, khoá bằng mã băm mã nguồn |
| Bài toán | Theo màu (`article_id`) | Theo mẫu thiết kế (`product_code`); ứng viên là sản phẩm đã có người mua trước mốc |
| Rò rỉ | k-core dùng dữ liệu test | Hết rò rỉ đã biết (có test tự động) |
| Mô hình lai | NeuMF chỉ dùng ID | NeuMF-F có đặc trưng; tách được 3 câu hỏi: đặc trưng, hợp nhất, sớm/muộn |
| Đối chứng | 7 mô hình | 14 mô hình |
| Thống kê | 3 seed, 8 so sánh | 5 seed, 10 so sánh đăng ký trước |
| **Kết quả** | Mô hình lai **không hơn** baseline nào (0/8) | Mô hình lai có đặc trưng **hơn 7/9** đối thủ; ngang GMF-F và LateFusion-F |

Số tuyệt đối v1 và v2 không so được (khác mẫu khách, đơn vị sản phẩm, tập ứng viên, đáp án). Kết luận giống nhau ở cả
hai: NeuMF chỉ dùng ID không hơn BPR-MF có ý nghĩa.

---

## 8. Đối chiếu 17 góp ý của GVHD

Mức: **Đạt** = đã làm và có số liệu/bằng chứng; **Đạt, còn việc nhỏ** = phần chính xong, còn việc hoàn thiện;
**Một phần** = làm được một phần, phần còn lại ghi là hạn chế; **Chưa** = chưa làm.

| # | Góp ý | Mức | Bằng chứng | Còn lại |
|---|---|---|---|---|
| 1 | Kết quả cao bất thường, rò rỉ | **Đạt** | Chia theo thời gian, k-core trước mốc, đặc trưng theo thời điểm, mẫu B độc lập, khoá test; test tự động. NDCG@10 cao nhất 0,0409 — hợp lý cho ~6,7 nghìn ứng viên | — |
| 2 | Bộ test chuẩn chung | **Đạt** | 14 mô hình cùng một tập test B: 3.165 khách, 10.285 cặp đúng, cùng ứng viên, cùng 5 seed, cùng file dữ liệu (kiểm MD5) | — |
| 3 | Top-K khách/sản phẩm tương đồng | **Đạt** | UserKNN (k = 200) hạng 5/14 — baseline mạnh nhất (0,03114); ItemKNN hạng 6; demo có thẻ 10 khách tương đồng | — |
| 4 | Lọc cộng tác hoạt động thế nào | **Đạt** | Báo cáo mục 2.1.2, 3.3.1; `van_dap.md` câu 4 | — |
| 5 | Khởi đầu lạnh | **Một phần** | Bản v2 đầu (khối 1) đã thử đưa sản phẩm mới vào đánh giá: NDCG@10 trên nhóm này của mọi mô hình dưới 0,002. Bản cuối bỏ sản phẩm chưa có người mua theo góp ý | Khởi đầu lạnh (sản phẩm và khách) nằm ngoài phạm vi kết quả cuối — ghi là hạn chế và hướng phát triển |
| 6 | NDCG và các chỉ số | **Đạt** | NDCG/Recall/HR/Precision @5/10/20; ví dụ tính tay trong `van_dap.md` | — |
| 7 | Trình bày kết quả | **Đạt, còn việc nhỏ** | Bảng, hình, macro tự sinh; `ket_qua.txt`; 31/31 câu nhận xét khớp số liệu | Biên dịch lại PDF |
| 8 | Vai trò của MF | **Đạt** | BPR-MF, GMF; nhánh GMF-F là thành phần mạnh nhất của NeuMF-F (GMF-F ngang NeuMF-F) | — |
| 9 | Mô hình lai thực sự | **Đạt** | NeuMF-F: MF + DNN + đặc trưng; hơn NeuMF chỉ ID 43,8% (có ý nghĩa) | — |
| 10 | Transformer, Temporal, BERT | **Một phần** | Dùng mô tả văn bản (TF-IDF + SVD); ablation: bỏ văn bản −2,7% (khoảng tin cậy chứa 0) | BERT/Transformer là hướng phát triển (cô ghi không bắt buộc) |
| 11 | Yếu tố thời gian | **Đạt** | Chia theo thời gian; đặc trưng thời gian; MostPopular-Recent (hơn Most Popular). Ablation: bỏ thời gian **−42,3%** — thành phần quan trọng nhất | — |
| 12 | Early fusion | **Đạt** | NeuMF-F (và NeuMF) là early fusion theo định nghĩa trong luận án của cô | — |
| 13 | Late fusion | **Đạt** | LateFusion-F; so sánh #4 đăng ký trước: LateFusion-F cao hơn 2,2% nhưng **không khác biệt có ý nghĩa** | — |
| 14 | Baseline; lai có hơn trước khi lai | **Đạt** | So sánh #1–#3, #5–#9: hơn NeuMF, MLP-F, BPR-MF, ItemKNN, UserKNN, MostPopular-Recent, Content; ngang GMF-F | — |
| 15 | Sơ đồ kiến trúc | **Đạt, còn việc nhỏ** | Hình 2.1, 2.2, 3.1, 3.2, 3.3 | Chụp 2 ảnh demo |
| 16 | Mô hình "variational" | **Chưa** | Lý thuyết Mult-VAE ở mục 2.4.4 | Test B đã mở (10/10), nên nếu cô yêu cầu thì chỉ thêm được dưới dạng **thăm dò sau kiểm thử**, ghi lệch kế hoạch (PREREG_v2 mục 10), không đưa vào họ 10 so sánh. Cần hỏi cô |
| 17 | Lộ trình 10 bước | **Đạt** | Bước 1–10 đều có kết quả, kể cả phần thảo luận Chương 4 (xem `van_dap.md` câu 17) | — |

**Tổng: 12/17 Đạt, 2/17 Đạt còn việc nhỏ, 2/17 Một phần, 1/17 Chưa.**

---

## 9. Mức độ hoàn thành

### 9.1 Theo hạng mục

| Hạng mục | Hoàn thành | Ghi chú |
|---|---|---|
| Dữ liệu và đặc trưng (mẫu A, B) | 100% | MD5 mẫu và file dữ liệu đã lọc ghi trong kế hoạch |
| Code giao thức v2 | 100% | 98/98 test qua (chưa tính 6 test demo nạp checkpoint); mã v1 đã dọn |
| Kế hoạch đăng ký trước (PREREG_v2, bản cuối) | 100% | Commit trước khi chấm (khoá test xác nhận); mục 10 ghi việc chạy lại seed 42 |
| Tinh chỉnh trên mẫu A | 100% | 13/13 mô hình có cấu hình tốt nhất (`audit/v2/best_configs.json`) |
| Đánh giá cuối trên mẫu B | 100% | 5/5 seed; đã commit kết quả |
| Kiểm định, bảng, hình, macro | 100% | Đã commit |
| Báo cáo Chương 1–5, tóm tắt, phụ lục | 95% | Viết theo kết quả mới; còn 2 ảnh demo và biên dịch PDF |
| Demo | 90% | Đã chuyển sang dữ liệu bản cuối; còn chạy test có checkpoint và chụp ảnh |
| Tài liệu md | 100% | Cập nhật 10/10 |

**Tổng thể: khoảng 97%.** Thực nghiệm và viết đã xong; còn kiểm tra demo, chụp ảnh và biên dịch báo cáo.

### 9.2 Việc tiếp theo

1. **Chạy test demo có checkpoint:** `py -m pytest demo/tests -q` (khớp số theo từng khách với file kết quả).
2. **Chạy demo, chụp 2 ảnh** `demo_v2.png`, `demo_v2_neighbors.png` vào `Report DACNTT/media/figures/demo/`.
3. **Biên dịch lại** báo cáo (`compile.bat`), chạy `python run.py check-report --strict`, commit.
4. **Hỏi cô** về góp ý 16 (mô hình variational).
5. Push khi đã sẵn sàng.

### 9.3 Lưu ý

- **Không chạy lại** `23_final_v2.py`: mọi seed đã có dòng nhật ký; mã nguồn đã đổi sau khi dọn (mã băm khác lúc tinh
  chỉnh), nên chạy lại còn cần `--allow-code-change` và phải ghi lệch kế hoạch.
- Nhật ký `audit/test_access_log.csv` có 6 dòng ngày 10/10: dòng 08:56 của lần chạy bị dừng ("Đánh giá cuối bản cuối
  theo PREREG_v2 (406b62c)") và 5 dòng của lần chạy hoàn tất ("Đánh giá cuối theo PREREG_v2; seed 42 chạy lại theo mục
  10"), trong đó seed 42 mang nhãn `_rerun`.
- Không đặt số v1 hay số khối 1 cạnh số của bản cuối trong báo cáo.

---

## 10. Danh sách file

- **Kết quả v2:** `neumf_project/outputs/v2/final/` (summary, significance, ablation, beyond, data.json, items.csv.gz,
  figures/, seed*/, `ket_qua.txt`)
- **Dữ liệu đã lọc:** `neumf_project/outputs/data/manifest.json` (MD5 của file dữ liệu từng mẫu)
- **Kế hoạch và nhật ký:** `neumf_project/audit/PREREG_v2.md`, `neumf_project/audit/v2/`, `neumf_project/audit/test_access_log.csv`
- **Code v2:** `neumf_project/src/data_pipeline/{features,protocol_v2,feature_dataset}.py`,
  `neumf_project/src/models/hybrid_features.py`, `neumf_project/src/evaluation/v2.py`,
  `neumf_project/scripts/{00_sample_hm,02_prepare_data,21_build_features,22_tune_v2,23_final_v2,24_report_v2,v2_common}.py`,
  `configs/v2.yaml`
- **Test:** `neumf_project/tests/`, `neumf_project/demo/tests/`
- **Báo cáo:** `Report DACNTT/` (bảng v2: `content/tables/v2/`, hình v2: `media/figures/v2/`)
- **Lịch sử:** `neumf_project/audit/PREREG.md` (v1), `neumf_project/audit/PREREG_v2_cu.md` (bản v2 đầu); mã và kết quả
  trong lịch sử git (commit `9799f1a`)
