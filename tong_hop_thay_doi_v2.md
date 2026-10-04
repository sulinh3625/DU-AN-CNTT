# Tổng hợp giao thức v2: đồ án làm gì, kết quả, mức độ hoàn thành

Cập nhật: 04/10/2026, **sau đánh giá cuối trên mẫu B** (5/5 seed, chạy 04/10/2026 trên GPU RTX 3050).

---

## 1. Đồ án đang làm gì và vì sao

### 1.1 Đồ án làm gì — nói ngắn

- **Bài toán:** với mỗi khách hàng H&M, gợi ý 10 sản phẩm thời trang họ có khả năng mua lần đầu trong 8 tuần tới,
  chỉ dựa vào lịch sử mua (không có điểm đánh giá).
- **Mô hình đề tài — NeuMF-F:** mô hình lai giữ đúng khung của NeuMF (nhánh nhân tử hoá ma trận GMF + nhánh mạng nơ-ron
  sâu MLP, hợp nhất sớm), nhưng mỗi khách/sản phẩm không chỉ có vector ID mà còn có **đặc trưng**: thuộc tính và mô tả
  sản phẩm, thông tin khách, doanh số và thời gian.
- **Cách chứng minh:** so NeuMF-F với 13 mô hình khác trên **cùng** một tập kiểm thử, theo một kế hoạch ghi sẵn từ trước
  (`neumf_project/audit/PREREG_v2.md`), trên một nhóm khách hàng chưa từng được dùng để ra quyết định (mẫu B).

### 1.2 Vì sao phải làm như vậy

| Việc làm | Lý do |
|---|---|
| Lai **MF + DNN** (GMF + MLP) | Đúng tên đề tài. MF chỉ học tương tác tuyến tính (tích vô hướng); DNN học tương tác phi tuyến. NeuMF (He et al., 2017) là kiến trúc chuẩn ghép hai nhánh này |
| Thêm **đặc trưng** vào NeuMF | Ở v1, NeuMF chỉ dùng ID **không** hơn MF đã tinh chỉnh (0/8 so sánh có ý nghĩa). Vector ID chỉ học được từ lượt mua, nên dữ liệu thưa và sản phẩm mới là giới hạn cứng; phải thêm thông tin về chính sản phẩm/khách thì mô hình mới có cái để học thêm |
| Đưa **sản phẩm mới** vào tập ứng viên | Hàng thời trang ra mắt liên tục: ở mẫu A, 27% lượt mua lần đầu trong 8 tuần cuối là sản phẩm chưa từng bán. Bỏ chúng đi (như v1) là chấm một bài toán dễ hơn thực tế |
| Chia **theo thời gian**, không leave-one-out | Leave-one-out để lọt thông tin tương lai: đo trên mẫu A, 11,2% dữ liệu huấn luyện xảy ra **sau** món cần dự đoán |
| **Hai mẫu khách A/B** | Tập test của mẫu A đã bị xem nhiều lần ở v1. Mọi quyết định (chọn cấu hình) làm trên A; kết luận lấy trên B — khách khác hẳn, test chỉ mở một lần |
| **Đăng ký trước** + khoá test | Mô hình, lưới tinh chỉnh, độ đo, 10 so sánh và tiêu chí "tốt hơn" cố định trước khi xem kết quả, nên không thể chọn lại sau khi thấy số |
| **14 mô hình**, cùng ngân sách tinh chỉnh | Muốn nói "lai có tác dụng" thì phải so với: bản chỉ dùng ID (đặc trưng có giúp không), từng nhánh riêng (lai có hơn từng phần không), hợp nhất muộn (sớm hay muộn), và baseline mạnh (KNN, BPR-MF, phổ biến gần đây) |
| **5 seed**, kiểm định theo từng khách | Mạng nơ-ron dao động theo seed. Kiểm định Wilcoxon + bootstrap trên ~3.000 khách, hiệu chỉnh Holm cho 10 so sánh; với 5 seed, kiểm định theo seed không bao giờ đạt p < 0,05 |
| **Ablation**, nhóm sản phẩm cũ/mới | Biết NeuMF-F hơn/thua **ở đâu** và thành phần nào đóng góp |

### 1.3 Vì sao đổi từ v1 sang v2

Giao thức v1 (mẫu A, chỉ ID) có bốn vấn đề:

1. NeuMF chỉ dùng ID không vượt được MF đã tinh chỉnh (0/8 so sánh có ý nghĩa).
2. Sản phẩm mới bị loại khỏi đánh giá.
3. Lọc k-core dùng cả dữ liệu của giai đoạn test.
4. Tập test của mẫu A đã bị xem nhiều lần (27/09, 29/09, 02/10), một số quyết định đưa ra sau khi xem.

v1 được giữ làm **lịch sử phát triển** (báo cáo mục 4.5); số v1 và số v2 không đặt cạnh nhau vì khác mẫu khách, khác
tập ứng viên và khác đáp án.

---

## 2. Kết quả đánh giá cuối (mẫu B)

### 2.1 Lần chạy

| Mục | Giá trị |
|---|---|
| Ngày, máy | 04/10/2026; GPU NVIDIA RTX 3050 Laptop; 5 seed tổng 247 phút |
| Truy vết | Commit `2d9e331`, cây mã sạch, mã băm mã nguồn trùng lúc tinh chỉnh; mỗi seed đúng 1 dòng trong `audit/test_access_log.csv`, không chạy lại seed nào |
| Mẫu B sau lọc | 7.038 khách, 19.109 sản phẩm (9.478 có ID, 7.372 sản phẩm mới) |
| Tập kiểm thử | 2.991 khách được đánh giá; 12.206 cặp đúng, trong đó **6.080 (49,8%) là sản phẩm mới**; trung bình 16.814 sản phẩm ứng viên mỗi khách |
| File | `neumf_project/outputs/v2/final/` (`summary.csv`, `significance.csv`, `groups.csv`, `ablation.csv`, `beyond.csv`); bảng gọn: `bang2_v2.txt` |

### 2.2 Bảng 2 — NDCG@10 trên tập kiểm thử mẫu B (trung bình ± độ lệch chuẩn, 5 seed)

| Hạng | Mô hình | Test | Val (mẫu A) | Chỉ SP cũ | SP mới |
|---|---|---|---|---|---|
| 1 | **LateFusion-F** | **0,01753 ± 0,00085** | 0,01632 | 0,02853 | 0,00017 |
| 2 | GMF-F | 0,01561 ± 0,00129 | 0,01570 | 0,02643 | 0,00070 |
| 3 | **NeuMF-F** (đề tài) | 0,01470 ± 0,00062 | **0,01687** | 0,02536 | 0,00057 |
| 4 | UserKNN | 0,01305 | 0,01216 | 0,02060 | 0 |
| 5 | BPR-MF | 0,01206 ± 0,00071 | 0,00934 | 0,01877 | 0 |
| 6 | NeuMF (chỉ ID) | 0,01071 ± 0,00068 | 0,01108 | 0,01673 | 0 |
| 7 | ItemKNN | 0,01027 | 0,01094 | 0,01606 | 0 |
| 8 | Most Popular | 0,01004 | 0,00734 | 0,01546 | 0 |
| 9 | MostPopular-Recent | 0,00995 | 0,00830 | 0,01554 | 0 |
| 10 | MLP | 0,00985 ± 0,00030 | 0,00797 | 0,01515 | 0 |
| 11 | MLP-F | 0,00978 ± 0,00175 | 0,01136 | 0,01626 | 0,00004 |
| 12 | GMF | 0,00967 ± 0,00060 | 0,00845 | 0,01504 | 0 |
| 13 | Content | 0,00384 | 0,00499 | 0,00573 | **0,00176** |
| 14 | Random | 0,00031 ± 0,00009 | — | 0,00062 | 0,00028 |

Mô hình không có độ lệch chuẩn là mô hình tất định (giống nhau ở mọi seed). Các độ đo phụ (Recall@10, HR@10,
Precision@10, NDCG@5, NDCG@20) cho cùng thứ tự ba hạng đầu; HR@10 của NeuMF-F là 6,5%, của LateFusion-F là 7,7%.

### 2.3 Họ 10 so sánh đăng ký trước

"A tốt hơn B" chỉ khi đủ cả ba: p sau Holm < 0,05; khoảng tin cậy 95% không chứa 0; chênh lệch ≥ 5%.

| # | So sánh | Chênh lệch NDCG@10 | Kết luận |
|---|---|---|---|
| 1 | NeuMF-F vs NeuMF | +37,2% | **NeuMF-F tốt hơn** |
| 2 | NeuMF-F vs GMF-F | −5,8% | Không khác biệt có ý nghĩa |
| 3 | NeuMF-F vs MLP-F | +50,3% | **NeuMF-F tốt hơn** |
| 4 | NeuMF-F vs LateFusion-F | −16,1% | **LateFusion-F tốt hơn** |
| 5 | NeuMF-F vs BPR-MF | +21,9% | **NeuMF-F tốt hơn** |
| 6 | NeuMF-F vs ItemKNN | +43,1% | **NeuMF-F tốt hơn** |
| 7 | NeuMF-F vs UserKNN | +12,7% | Không khác biệt có ý nghĩa (p nhỏ nhưng khoảng tin cậy chứa 0) |
| 8 | NeuMF-F vs MostPopular-Recent | +47,8% | **NeuMF-F tốt hơn** |
| 9 | NeuMF-F vs Content | +283% | **NeuMF-F tốt hơn** |
| 10 | NeuMF vs BPR-MF | −11,2% | Không khác biệt có ý nghĩa (p Holm = 0,055) |

**Tổng: NeuMF-F tốt hơn 6/9 đối thủ, ngang 2 (GMF-F, UserKNN), thua 1 (LateFusion-F).**

### 2.4 Phân tích phụ (chỉ mô tả, không kiểm định)

- **Sản phẩm cũ và mới:** phần hơn của các mô hình có đặc trưng nằm gần hết ở **sản phẩm cũ** (NeuMF-F 0,0238 so với
  NeuMF 0,0167). Với **sản phẩm mới**, mọi mô hình đều rất thấp; cao nhất là Content (0,00176), NeuMF-F 0,00057.
  Mô hình chỉ dùng ID bằng 0 ở nhóm này đúng như thiết kế.
- **Ablation NeuMF-F (seed 42, đầy đủ = 0,01486):** bỏ **đặc trưng thời gian −30,2%** (khoảng tin cậy không chứa 0 —
  thành phần quan trọng nhất); bỏ thuộc tính sản phẩm −8,7%, bỏ văn bản −7,4%, bỏ thông tin khách −3,6% (cả ba khoảng
  tin cậy chứa 0). Biến thể "bỏ cơ chế bỏ ID ngẫu nhiên" **trùng hệt** bản đầy đủ vì tinh chỉnh đã chọn ρ = 0 cho
  NeuMF-F — biến thể này không mang thông tin.
- **Top-10:** NeuMF-F phủ 6,9% danh mục, 7,1% gợi ý là sản phẩm mới; LateFusion-F phủ 2,5%, chỉ 0,4% sản phẩm mới.
  Thời gian huấn luyện mỗi seed: NeuMF-F 9,3 phút, NeuMF 2,8 phút, BPR-MF 1,9 phút (GPU).

### 2.5 Trả lời câu hỏi nghiên cứu

| Câu hỏi | Trả lời |
|---|---|
| Đặc trưng có cải thiện mô hình lai không? | **Có** — NeuMF-F hơn NeuMF chỉ ID 37%, có ý nghĩa. Phần lớn nhờ đặc trưng thời gian |
| Lai có hơn từng nhánh đứng riêng không? | **Hơn nhánh DNN** (MLP-F, +50%); **không hơn nhánh MF** (GMF-F, −6%, không có ý nghĩa) |
| Hợp nhất sớm hay muộn? | **Muộn tốt hơn** trên dữ liệu này: LateFusion-F hơn NeuMF-F 16%, có ý nghĩa |
| NeuMF-F so với baseline? | Hơn BPR-MF, ItemKNN, MostPopular-Recent, Content; ngang UserKNN |
| NeuMF chỉ ID so với MF? | Không khác biệt có ý nghĩa — lặp lại kết luận của v1 trên mẫu khách mới |
| Sản phẩm mới? | Đặc trưng cho phép chấm và gợi ý sản phẩm mới, nhưng độ chính xác trên nhóm này còn rất thấp |

### 2.6 Điểm cần nói thật khi bảo vệ

1. **NeuMF-F không phải mô hình tốt nhất.** Nó cao nhất trên tập xác thực của A (0,01687) nên được chọn làm mô hình đề
   tài, nhưng trên test của B đứng thứ 3. Theo PREREG_v2 mục 8, báo cáo đúng như vậy, không đổi mô hình chính.
2. **Ba mô hình có đặc trưng đứng đầu ở cả hai mẫu** (LateFusion-F, GMF-F, NeuMF-F), rồi đến UserKNN — kết luận "đặc
   trưng giúp ích" vững; thứ tự bên trong nhóm thì đảo khi đổi mẫu.
3. **MLP-F không ổn định:** độ lệch chuẩn 0,00175 (gấp ~3 lần mô hình khác), số epoch tốt nhất giữa các seed là 1, 10,
   1, 20, 2.
4. **Cơ chế bỏ ID ngẫu nhiên (DropoutNet)** có trong thiết kế nhưng NeuMF-F cuối cùng **không dùng** (ρ = 0 được chọn);
   chỉ MLP-F dùng (ρ = 0,5). Báo cáo/vấn đáp không được nói NeuMF-F "học chấm sản phẩm mới nhờ bỏ ID ngẫu nhiên".

---

## 3. Thay đổi của giao thức v2

### 3.1 Dữ liệu và giao thức

| Thay đổi | Nội dung | File |
|---|---|---|
| Mẫu kiểm định B | 500.125 giao dịch, 21.030 khách, **không có khách chung** với mẫu A (500.269 giao dịch, 21.599 khách). Mã MD5 của hai mẫu ghi trong kế hoạch đăng ký trước | `scripts/00_sample_hm.py` (`--holdout`) |
| Đặc trưng | Mỗi sản phẩm: 11 thuộc tính danh mục, vector mô tả văn bản 64 chiều (TF-IDF → SVD), 5 đặc trưng thời gian (doanh số toàn H&M 7/28/91 ngày, tuổi sản phẩm, cờ chưa từng bán). Mỗi khách: 5 thuộc tính, 2 đặc trưng thời gian | `src/data_pipeline/features.py`, `scripts/21_build_features.py` |
| Chống rò rỉ thời gian | Đặc trưng tại ngày t chỉ dùng dữ liệu **trước** t; mẫu âm chỉ lấy trong sản phẩm đã ra mắt tại ngày mua | `features.py`, `src/data_pipeline/feature_dataset.py` |
| Giai đoạn đánh giá | k-core chỉ lọc trên dữ liệu trước mốc test (29/07/2020). Tập ứng viên = sản phẩm cũ ∪ sản phẩm mới (chưa từng bán trước mốc). Mô hình chỉ dùng ID xếp sản phẩm mới xuống cuối | `src/data_pipeline/protocol_v2.py` |
| Cấu hình | Mốc thời gian, k = 10, 5 seed, ngân sách tinh chỉnh | `configs/v2.yaml` |

### 3.2 Mô hình

| Mô hình | Vai trò | File |
|---|---|---|
| **NeuMF-F** | Mô hình đề tài. Hai nhánh GMF-F + MLP-F hợp nhất sớm; mỗi vector = Embedding ID + chiếu tuyến tính của đặc trưng. Có tuỳ chọn bỏ ID sản phẩm ngẫu nhiên khi huấn luyện (ρ ∈ {0; 0,25; 0,5}; tinh chỉnh chọn ρ = 0) | `src/models/hybrid_features.py` |
| GMF-F, MLP-F | Từng nhánh của NeuMF-F đứng riêng — đo "lai có hơn từng nhánh không" | như trên |
| LateFusion-F | Hợp nhất muộn: trộn điểm GMF-F và MLP-F huấn luyện riêng (w = 0,3 chọn trên tập xác thực) | `src/models/late_fusion.py` |
| GMF, MLP, NeuMF (chỉ ID) | Kiến trúc NCF gốc — đo "đặc trưng có giúp không" | `src/models/neumf.py` |
| Baseline | Random, Most Popular, **MostPopular-Recent**, **Content**, ItemKNN, UserKNN, BPR-MF | `hybrid_features.py`, `src/baselines/` |
| Ablation NeuMF-F | Lần lượt bỏ: văn bản, thời gian, thông tin khách, thuộc tính sản phẩm, cơ chế bỏ ID ngẫu nhiên | `scripts/v2_common.py` |

Tổng cộng **14 mô hình**, cùng ngân sách tinh chỉnh (6 cấu hình mỗi mô hình có học).

### 3.3 Quy trình thực nghiệm

| Bước | Nội dung | File |
|---|---|---|
| Đăng ký trước | Mô hình, lưới tinh chỉnh, 5 seed, độ đo chính NDCG@10, **họ 10 so sánh** (Wilcoxon + bootstrap + Holm), tiêu chí "tốt hơn", hạn chế đã biết | `neumf_project/audit/PREREG_v2.md` |
| Tinh chỉnh | Chỉ trên tập xác thực của A. Nhật ký mỗi cấu hình kèm **mã băm nội dung mã nguồn** | `scripts/22_tune_v2.py` |
| Đánh giá cuối | Khoá test từ chối chạy nếu: kế hoạch chưa commit, thiếu lý do, mã nguồn có thay đổi, hoặc mã băm khác lúc tinh chỉnh. Mỗi seed ghi nhật ký trước khi chấm; chạy tiếp được nếu bị ngắt | `scripts/23_final_v2.py` |
| Đánh giá theo nhóm | NDCG riêng cho sản phẩm cũ/mới; phân tích "chỉ sản phẩm cũ" | `src/evaluation/v2.py` |
| Kiểm định và xuất báo cáo | Bảng, hình, macro LaTeX tự sinh — không gõ tay số | `scripts/24_report_v2.py` |
| Đối chiếu báo cáo | Kiểm tra câu chữ báo cáo với số liệu; báo macro, bảng, hình còn thiếu | `scripts/19_check_report.py` |
| Lệnh tắt | `v2-data`, `v2-tune`, `v2-dry-run`, `v2-final`, `v2-report` | `run.py` |

### 3.4 Demo và chạy trên GPU

- **Demo chế độ v2:** mặc định so NeuMF-F với NeuMF, gắn nhãn "Mới" cho sản phẩm mới; thẻ 10 khách tương đồng (UserKNN);
  dashboard đọc kết quả v2. Dùng checkpoint seed 42 của đánh giá cuối (`outputs/v2/final/seed42/`).
- **Notebook Colab** (`notebooks/colab_v2.ipynb`) cho đánh giá cuối trên GPU. Lần chạy thật dùng máy RTX 3050 thay vì Colab.

### 3.5 Kiểm thử

- `tests/test_v2.py`, `tests/test_v2_final.py`: đặc trưng không dùng dữ liệu tương lai, mẫu âm hợp lệ; k-core chỉ dùng
  dữ liệu trước mốc test; NeuMF-F cho cùng điểm lúc huấn luyện và lúc đánh giá; khoá test, tiêu chí kết luận, họ so sánh.
- **Kết quả ngày 04/10 (`pytest -q`):** 132 qua, 1 lỗi. Test lỗi là `test_report_claims_hold_on_committed_results`,
  đúng câu sai ở C4.tex dòng 91 (mục 4) — lỗi ở câu chữ báo cáo, không phải ở code; sửa câu đó thì test qua.

---

## 4. Báo cáo (`Report DACNTT/`)

| Phần | Trạng thái |
|---|---|
| Chương 1–3 | Viết xong theo v2. Còn thiếu 2 ảnh chụp demo v2 (`media/figures/demo/demo_v2.png`, `demo_v2_neighbors.png`) |
| Chương 4 | Bảng, hình, macro **đã có số thật** (sinh ngày 04/10 vào `content/tables/v2/`, `media/figures/v2/`). Còn: 1 câu sai theo `19_check_report.py` (C4.tex dòng 91: "Most Popular có độ phủ top-10 không cao hơn mô hình cá nhân hoá nào" — thực tế Most Popular 0,095% > MLP-F 0,083%); phần thảo luận bằng chữ cần viết theo kết quả thật (mục 2.6 ở trên) |
| Chương 5, tóm tắt | Số qua macro đã có; cần viết lại câu kết luận cho đúng: NeuMF-F không tốt nhất, hợp nhất muộn tốt hơn |
| Chương 2 dòng 293 | Câu "NeuMF-F áp dụng ý tưởng này (bỏ ID ngẫu nhiên)" cần thêm: tinh chỉnh chọn ρ = 0 nên NeuMF-F cuối cùng không dùng |
| Biên dịch | `main.pdf` hiện là bản 03/10 — cần biên dịch lại |

---

## 5. Tài liệu đi kèm

- `README.md` (gốc), `neumf_project/README.md`, `neumf_project/pham_vi_du_an.md`, `neumf_project/demo/README.md`: viết
  theo v2, v1 chỉ còn mục lịch sử. Ngày 04/10: thêm số liệu mẫu B và tóm tắt kết quả vào `pham_vi_du_an.md`.
- `van_dap.md`: trả lời 17 góp ý; ngày 04/10 cập nhật theo kết quả thật (bỏ các câu "chờ đánh giá cuối", sửa câu về
  bỏ ID ngẫu nhiên, thêm câu hỏi khó về việc NeuMF-F thua LateFusion-F).
- `neumf_project/outputs/v2/final/bang2_v2.txt`: bảng dạng chữ để dán vào báo cáo — Bảng 2 (NDCG@10: test, val, theo
  nhóm sản phẩm), Bảng 3 (NDCG@10, Recall@10, HR@10, Precision@10), Bảng 4 (NDCG@5, @10, @20).

---

## 6. Thay đổi giai đoạn trước (giao thức v1)

- **Thuật ngữ theo luận án của GVHD:** NeuMF là Early Fusion; Late Fusion là trộn điểm của các mô hình huấn luyện riêng;
  MLP đứng riêng là DNN thuần. Đã sửa trong code và báo cáo.
- **Trình bày:** chú thích bảng/hình tiếng Việt, bỏ so sánh với số liệu bài báo.
- **Kiểm tra:** `18_preflight.py` có sai số cho phép khi chạy lại trên CPU. `audit/PREREG.md` có thêm mục ngày 03/10.
- **Kết quả v1** (lịch sử, `outputs/final/`): BPR-MF cao nhất; 0/8 so sánh có ý nghĩa; tiền huấn luyện không giúp.

---

## 7. Hiệu quả so với v1

| Tiêu chí | v1 | v2 |
|---|---|---|
| Độ tin cậy số liệu | Test đã xem nhiều lần; nhiều quyết định sau khi xem | Mẫu B độc lập, mở test một lần (5 dòng nhật ký, không chạy lại), đăng ký trước, khoá bằng mã băm mã nguồn |
| Bài toán | Bỏ sản phẩm mới → dễ hơn thực tế | Có sản phẩm mới (49,8% cặp đúng của test B) → sát thực tế |
| Rò rỉ | k-core dùng dữ liệu test | Hết rò rỉ đã biết (có test tự động) |
| Mô hình lai | NeuMF chỉ dùng ID | NeuMF-F có đặc trưng; tách được 3 câu hỏi: đặc trưng, hợp nhất, sớm/muộn |
| Đối chứng | 7 mô hình | 14 mô hình |
| Thống kê | 3 seed, 8 so sánh | 5 seed, 10 so sánh đăng ký trước |
| **Kết quả** | Mô hình lai **không hơn** baseline nào (0/8) | Mô hình lai có đặc trưng **hơn 6/9** đối thủ; nhưng thua hợp nhất muộn |

Số tuyệt đối v1 và v2 không so được (khác mẫu khách, tập ứng viên, đáp án). Chỉ thứ tự các mô hình chỉ dùng ID là
so được, và giống nhau: BPR-MF > NeuMF, NeuMF không hơn BPR-MF có ý nghĩa ở cả hai.

---

## 8. Đối chiếu 17 góp ý của GVHD

Mức: **Đạt** = đã làm và có số liệu/bằng chứng; **Đạt, còn việc nhỏ** = phần chính xong, còn việc hoàn thiện;
**Một phần** = làm được một phần, phần còn lại ghi là hạn chế; **Chưa** = chưa làm.

| # | Góp ý | Mức | Bằng chứng | Còn lại |
|---|---|---|---|---|
| 1 | Kết quả cao bất thường, rò rỉ | **Đạt** | Chia theo thời gian, k-core trước mốc, đặc trưng theo thời điểm, mẫu B độc lập, khoá test; test tự động. NDCG@10 cao nhất 0,0175 — hợp lý cho ~17 nghìn ứng viên | — |
| 2 | Bộ test chuẩn chung | **Đạt** | 14 mô hình cùng một tập test B: 2.991 khách, 12.206 cặp đúng, cùng ứng viên, cùng 5 seed | — |
| 3 | Top-K khách/sản phẩm tương đồng | **Đạt** | UserKNN (k = 200) hạng 4 — baseline mạnh nhất; ItemKNN; demo có thẻ 10 khách tương đồng | — |
| 4 | Lọc cộng tác hoạt động thế nào | **Đạt** | Báo cáo mục 2.1.2, 3.3.1; `van_dap.md` câu 4 | — |
| 5 | Khởi đầu lạnh | **Một phần** | Sản phẩm mới nằm trong đánh giá (49,8% cặp đúng); NeuMF-F chấm được và gợi ý 7,1% sản phẩm mới | NDCG trên sản phẩm mới rất thấp (0,00057); khách mới ngoài phạm vi (demo dùng luật). Ghi là hạn chế |
| 6 | NDCG và các chỉ số | **Đạt** | NDCG/Recall/HR/Precision @5/10/20, NDCG theo nhóm cũ/mới; ví dụ tính tay trong `van_dap.md` | — |
| 7 | Trình bày kết quả | **Đạt, còn việc nhỏ** | Bảng, hình, macro tự sinh; `bang2_v2.txt` | Sửa 1 câu sai C4.tex:91, biên dịch lại |
| 8 | Vai trò của MF | **Đạt** | BPR-MF, GMF; nhánh GMF-F là thành phần mạnh nhất của NeuMF-F (GMF-F ngang NeuMF-F) | — |
| 9 | Mô hình lai thực sự | **Đạt** | NeuMF-F: MF + DNN + đặc trưng; hơn NeuMF chỉ ID 37% (có ý nghĩa) | — |
| 10 | Transformer, Temporal, BERT | **Một phần** | Dùng mô tả văn bản (TF-IDF + SVD); ablation: bỏ văn bản −7,4% (không có ý nghĩa) | BERT/Transformer là hướng phát triển (cô ghi không bắt buộc) |
| 11 | Yếu tố thời gian | **Đạt** | Chia theo thời gian; đặc trưng thời gian; MostPopular-Recent. Ablation: bỏ thời gian **−30,2%** — thành phần quan trọng nhất | — |
| 12 | Early fusion | **Đạt** | NeuMF-F (và NeuMF) là early fusion theo định nghĩa trong luận án của cô | — |
| 13 | Late fusion | **Đạt** | LateFusion-F; so sánh #4 đăng ký trước: **late fusion tốt hơn 16%** | — |
| 14 | Baseline; lai có hơn trước khi lai | **Đạt** | So sánh #1–#3, #5–#9: hơn NeuMF, MLP-F, BPR-MF, ItemKNN, MostPopular-Recent, Content; ngang GMF-F, UserKNN | — |
| 15 | Sơ đồ kiến trúc | **Đạt, còn việc nhỏ** | Hình 2.1, 2.2, 3.1, 3.2, 3.3 | Chụp 2 ảnh demo v2 |
| 16 | Mô hình "variational" | **Chưa** | Lý thuyết Mult-VAE ở mục 2.4.4 | Test B đã mở, nên nếu cô yêu cầu thì chỉ thêm được dưới dạng **thăm dò sau kiểm thử**, ghi lệch kế hoạch (PREREG_v2 mục 10), không đưa vào họ 10 so sánh. Cần hỏi cô |
| 17 | Lộ trình 10 bước | **Đạt, còn việc nhỏ** | Bước 1–10 đều có kết quả (xem `van_dap.md` câu 17) | Bước 10: viết phần thảo luận Chương 4 |

**Tổng: 11/17 Đạt, 3/17 Đạt còn việc nhỏ, 2/17 Một phần, 1/17 Chưa.**

---

## 9. Mức độ hoàn thành

### 9.1 Theo hạng mục

| Hạng mục | Hoàn thành | Ghi chú |
|---|---|---|
| Dữ liệu và đặc trưng (mẫu A, B) | 100% | MD5 ghi trong kế hoạch |
| Code giao thức v2 | 100% | 132/133 test qua; test lỗi duy nhất do 1 câu trong báo cáo (mục 3.5) |
| Kế hoạch đăng ký trước (PREREG_v2) | 100% | Đã commit trước khi chấm (khoá test xác nhận) |
| Tinh chỉnh trên mẫu A | 100% | 13/13 mô hình có cấu hình tốt nhất (`audit/v2/best_configs.json`) |
| Đánh giá cuối trên mẫu B | 100% | 5/5 seed, mỗi seed mở test đúng một lần |
| Kiểm định, bảng, hình, macro | 100% | Đã sinh — **chưa commit** |
| Báo cáo Chương 1–3 | 95% | Thiếu 2 ảnh demo; sửa 1 câu về bỏ ID ngẫu nhiên |
| Báo cáo Chương 4–5, tóm tắt | 80% | Số đã tự điền; còn 1 câu sai và phần thảo luận theo kết quả thật |
| Demo v2 | 95% | Có checkpoint seed 42; thiếu ảnh chụp |
| Tài liệu md | 100% | Cập nhật 04/10 |

**Tổng thể: khoảng 90%.** Phần thực nghiệm đã xong hoàn toàn; phần còn lại là viết và hoàn thiện báo cáo (khoảng 3–4 giờ).

### 9.2 Việc tiếp theo

1. **Commit kết quả** (`outputs/v2/final/`, `audit/test_access_log.csv`, `Report DACNTT/content/tables/v2/`,
   `Report DACNTT/media/figures/v2/`) — để `19_check_report.py` có bản đối chiếu và mốc thời gian được lưu.
2. **Sửa báo cáo:** C4.tex dòng 91 (độ phủ Most Popular); C2.tex dòng 293 (ρ = 0); viết phần thảo luận Chương 4–5 theo
   mục 2.5–2.6 ở trên.
3. **Chạy demo, chụp 2 ảnh** `demo_v2.png`, `demo_v2_neighbors.png`.
4. **Biên dịch lại** báo cáo, chạy `python run.py check-report --strict`, commit.
5. **Hỏi cô** về góp ý 16 (mô hình variational).

### 9.3 Lưu ý

- **Không chạy lại** `23_final_v2.py`: mọi seed đã có dòng nhật ký; chạy lại cần `--allow-rerun` và phải ghi lệch kế hoạch.
- Lý do mở test ghi trong nhật ký chỉ là "chạy" — đủ để khoá test chấp nhận, nhưng nên nói rõ khi được hỏi: đây là lần
  đánh giá cuối chính thức theo PREREG_v2.
- PREREG_v2 mục 10 (lệch kế hoạch) vẫn trống — đúng, vì lần chạy không lệch kế hoạch.
- Không đặt số v1 cạnh số v2 trong báo cáo.

---

## 10. Danh sách file

- **Kết quả v2:** `neumf_project/outputs/v2/final/` (summary, significance, groups, ablation, beyond, data.json,
  figures/, seed*/, `bang2_v2.txt`)
- **Kế hoạch và nhật ký:** `neumf_project/audit/PREREG_v2.md`, `neumf_project/audit/v2/`, `neumf_project/audit/test_access_log.csv`
- **Code v2:** `neumf_project/src/data_pipeline/{features,protocol_v2,feature_dataset}.py`,
  `neumf_project/src/models/hybrid_features.py`, `neumf_project/src/evaluation/v2.py`,
  `neumf_project/scripts/{21_build_features,22_tune_v2,23_final_v2,24_report_v2,v2_common}.py`, `configs/v2.yaml`
- **Test:** `neumf_project/tests/{test_v2,test_v2_final}.py`
- **Báo cáo:** `Report DACNTT/` (bảng v2: `content/tables/v2/`, hình v2: `media/figures/v2/`)
- **Lịch sử v1:** `neumf_project/audit/PREREG.md`, `neumf_project/outputs/final/`
