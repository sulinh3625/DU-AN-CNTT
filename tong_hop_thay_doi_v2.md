# Tổng hợp thay đổi (giao thức v2) và tình hình hoàn thành

Cập nhật: 03/10/2026, 22h00. Phạm vi: mọi thay đổi kể từ commit `e29164e` (chưa commit).

---

## 1. Tóm tắt

Đề tài chuyển từ **giao thức v1** sang **giao thức v2**; v2 là kết quả chính của báo cáo, v1 được giữ làm lịch sử phát triển.

**Vì sao đổi.** v1 có bốn vấn đề:

1. NeuMF chỉ dùng mã khách/mã sản phẩm (ID) không vượt được MF đã tinh chỉnh (0/8 so sánh có ý nghĩa).
2. Sản phẩm mới bị loại khỏi đánh giá, dù chiếm 27% số lượt mua lần đầu trong 8 tuần cuối của mẫu A.
3. Lọc k-core dùng cả dữ liệu của giai đoạn test.
4. Tập test của mẫu A đã bị xem nhiều lần, và một số quyết định được đưa ra sau khi xem.

**v2 làm gì.**

- Xây mô hình đề tài **NeuMF-F**: giữ cấu trúc MF + DNN của NeuMF, bổ sung đặc trưng sản phẩm, khách hàng và thời gian.
- Đưa sản phẩm mới vào tập ứng viên.
- Tinh chỉnh trên mẫu A, kết luận trên **mẫu B** — khách hàng khác hẳn A, mở tập kiểm thử đúng một lần, theo kế hoạch
  đăng ký trước.

---

## 2. Thay đổi mới — giao thức v2

### 2.1 Dữ liệu và giao thức

| Thay đổi | Nội dung | File |
|---|---|---|
| Mẫu kiểm định B | 500.125 giao dịch, 21.030 khách, **không có khách chung** với mẫu A (500.269 giao dịch, 21.599 khách). Mã MD5 của hai mẫu ghi trong kế hoạch đăng ký trước | `scripts/00_sample_hm.py` (`--holdout`) |
| Đặc trưng | Mỗi sản phẩm: 11 thuộc tính danh mục, vector mô tả văn bản 64 chiều (TF-IDF → SVD), 5 đặc trưng thời gian (doanh số toàn H&M 7/28/91 ngày, tuổi sản phẩm, cờ chưa từng bán). Mỗi khách: 5 thuộc tính, 2 đặc trưng thời gian | `src/data_pipeline/features.py`, `scripts/21_build_features.py` |
| Chống rò rỉ thời gian | Đặc trưng tại ngày t chỉ dùng dữ liệu **trước** t; mẫu âm chỉ lấy trong sản phẩm đã ra mắt tại ngày mua | `features.py`, `src/data_pipeline/feature_dataset.py` |
| Giai đoạn đánh giá | k-core chỉ lọc trên dữ liệu trước mốc test (29/07/2020). Tập ứng viên = sản phẩm cũ ∪ sản phẩm mới (chưa từng bán trước mốc). Mô hình chỉ dùng ID xếp sản phẩm mới xuống cuối | `src/data_pipeline/protocol_v2.py` |
| Cấu hình | Mốc thời gian, k = 10, 5 seed, ngân sách tinh chỉnh | `configs/v2.yaml` |

### 2.2 Mô hình

| Mô hình | Vai trò | File |
|---|---|---|
| **NeuMF-F** | Mô hình đề tài. Hai nhánh GMF-F + MLP-F hợp nhất sớm; mỗi vector = Embedding ID + chiếu tuyến tính của đặc trưng. Khi huấn luyện, ID sản phẩm bị bỏ ngẫu nhiên để mô hình học chấm cả sản phẩm chưa từng bán | `src/models/hybrid_features.py` |
| GMF-F, MLP-F | Từng nhánh của NeuMF-F đứng riêng — đo "lai có hơn từng nhánh không" | như trên |
| LateFusion-F | Hợp nhất muộn: trộn điểm GMF-F và MLP-F huấn luyện riêng — đo "hợp nhất sớm hay muộn" | `src/models/late_fusion.py` |
| GMF, MLP, NeuMF (chỉ ID) | Kiến trúc NCF gốc — đo "đặc trưng có giúp không" | `src/models/neumf.py` |
| Baseline | Random, Most Popular, **MostPopular-Recent** (mới), **Content** (mới), ItemKNN, UserKNN, BPR-MF | `hybrid_features.py`, `src/baselines/` |
| Ablation NeuMF-F | Lần lượt bỏ: văn bản, thời gian, thông tin khách, thuộc tính sản phẩm, cơ chế bỏ ID ngẫu nhiên | `scripts/v2_common.py` |

Tổng cộng **14 mô hình**, cùng ngân sách tinh chỉnh (6 cấu hình mỗi mô hình có học).

### 2.3 Quy trình thực nghiệm

| Bước | Nội dung | File |
|---|---|---|
| Đăng ký trước | Mô hình, lưới tinh chỉnh, 5 seed, độ đo chính NDCG@10, **họ 10 so sánh** (Wilcoxon + bootstrap + Holm), tiêu chí "tốt hơn", hạn chế đã biết | `neumf_project/audit/PREREG_v2.md` |
| Tinh chỉnh | Chỉ trên tập xác thực của A. Nhật ký mỗi cấu hình kèm **mã băm nội dung mã nguồn** | `scripts/22_tune_v2.py` |
| Đánh giá cuối | Khoá test từ chối chạy nếu: kế hoạch chưa commit, thiếu lý do, mã nguồn có thay đổi, hoặc mã băm khác lúc tinh chỉnh. Mỗi seed ghi nhật ký trước khi chấm; chạy tiếp được nếu bị ngắt; có chạy thử (`--dry-run`) và bản sao nhật ký (`--mirror-log`) | `scripts/23_final_v2.py` |
| Đánh giá theo nhóm | NDCG riêng cho sản phẩm cũ/mới; phân tích "chỉ sản phẩm cũ" | `src/evaluation/v2.py` |
| Kiểm định và xuất báo cáo | Bảng, hình, macro LaTeX tự sinh — không gõ tay số. Có chế độ `--tuning-only` để xuất kết quả tinh chỉnh trước | `scripts/24_report_v2.py` |
| Đối chiếu báo cáo | Kiểm tra câu chữ v2 và phần lịch sử v1 với số liệu; báo macro, bảng, hình còn thiếu | `scripts/19_check_report.py` (viết lại) |
| Lệnh tắt | `v2-data`, `v2-tune`, `v2-dry-run`, `v2-final`, `v2-report` | `run.py` |

### 2.4 Demo và chạy trên GPU

- **Demo chế độ v2:**
  - mặc định so NeuMF-F với NeuMF, gắn nhãn "Mới" cho sản phẩm mới;
  - giữ thẻ 10 khách tương đồng (UserKNN);
  - dashboard đọc kết quả v2.
  - Đã kiểm tra trên bản chạy thử: NDCG@10 theo từng khách khớp tuyệt đối với file kết quả. File: `demo/backend/*`, `demo/frontend/*`, `demo/README.md`.
- **Notebook Colab (GPU) cho đánh giá cuối** (`notebooks/colab_v2.ipynb`):
  - tự chuẩn bị dữ liệu và lưu lên Drive;
  - kiểm tra khoá test trước khi mở test;
  - ghi bản sao nhật ký test lên Drive;
  - đóng gói kết quả để chép về repo.

### 2.5 Kiểm thử

- Thêm `tests/test_v2.py` và `tests/test_v2_final.py`, kiểm tra:
  - đặc trưng không dùng dữ liệu tương lai, mẫu âm hợp lệ;
  - k-core chỉ dùng dữ liệu trước mốc test, tập ứng viên có sản phẩm mới;
  - NeuMF-F cho cùng điểm lúc huấn luyện và lúc đánh giá;
  - khoá test, tiêu chí kết luận, họ so sánh.
- `tests/test_pure_cf.py`: ràng buộc "thuần lọc cộng tác" chỉ áp cho pipeline v1.
- **Kết quả: 146 test qua, 5 bỏ qua** (test demo v2 chờ có kết quả cuối).

---

## 3. Báo cáo (`Report DACNTT/`)

| Phần | Thay đổi |
|---|---|
| Chương 1 | Viết lại động lực (dữ liệu thưa, nhiều sản phẩm mới), mục tiêu, phạm vi. Sản phẩm mới nay thuộc phạm vi; khách hàng mới vẫn ngoài phạm vi |
| Chương 2 | Thêm lý thuyết mô hình lai dùng đặc trưng (FM, Wide & Deep, DeepFM), khởi đầu lạnh của sản phẩm (DropoutNet), TF-IDF và LSA. Cập nhật Early/Late Fusion, độ đo theo nhóm sản phẩm cũ/mới, khoảng trống nghiên cứu |
| Chương 3 | Viết lại toàn bộ: hai mẫu A/B, giai đoạn đánh giá có sản phẩm mới, lý do không chia leave-one-out, đặc trưng theo thời điểm, kiến trúc NeuMF-F (**Hình 3.1, 3.2 mới**), lấy mẫu âm, bảng siêu tham số, quy trình đánh giá không thiên lệch, demo v2 |
| Chương 4 | Viết lại theo v2, mọi số lấy qua macro. Kết quả v1 chuyển thành mục 4.5 "Lịch sử phát triển" |
| Chương 5, tóm tắt Việt/Anh, phụ lục | Viết lại theo v2 (số qua macro) |
| Tài liệu tham khảo | Thêm 5: DropoutNet, TF-IDF (Salton & Buckley), LSA (Deerwester), cold-start (Schein), content-based (Lops) |
| Rà soát | Bỏ một hạn chế còn sót từ v1 ở mục 4.6 (sản phẩm đúng mua cùng ngày với sản phẩm trong lịch sử — không xảy ra ở v2 vì chia theo mốc chung); câu "kết quả tính trên CPU" đổi thành macro tự ghi máy chạy đánh giá cuối (CPU hay GPU) |
| Kỹ thuật | Biên dịch sạch (81 trang): không lỗi, không tham chiếu hỏng, không dòng tràn lề. `19_check_report.py`: 0 khẳng định sai, 0 dòng tài liệu ghi số cũ. Chỗ chưa có số hiện "[chưa có]" cho tới khi chạy đánh giá cuối |

---

## 4. Tài liệu đi kèm

- **Viết lại gọn các file giới thiệu**, v2 lên trước, v1 chỉ còn một mục lịch sử ngắn:
  - `README.md` (gốc): đề tài, thư mục, bảng "cần gì — đọc file nào";
  - `neumf_project/README.md`: cài đặt → dữ liệu → chạy v2 (tinh chỉnh, chạy thử, đánh giá cuối, sau khi chạy) →
    kiểm thử → demo → cấu trúc thư mục → v1 (từ 393 dòng còn khoảng 220 dòng);
  - `neumf_project/pham_vi_du_an.md`: bài toán, câu hỏi nghiên cứu, phạm vi, dữ liệu, mô hình, đánh giá, hạn chế theo v2
    (từ 612 dòng còn khoảng 330 dòng); bỏ các mục mô tả v1 như kết quả chính, không đặt số v1 cạnh số v2;
  - `neumf_project/demo/README.md`: chế độ v2 lên đầu, thêm biến `DEMO_V2_DIR`, cách chấm của chế độ v2.
- `van_dap.md`: **viết lại gọn, dễ hiểu theo v2**:
  - quy tắc tránh nói sai, đề tài trong 1 phút, các số liệu đã chắc chắn;
  - trả lời 17 góp ý bằng lời đơn giản, kèm mục báo cáo để mở;
  - phần câu hỏi khó và bảng khác biệt so với đề cương;
  - bỏ các chi tiết cũ không còn trong báo cáo (mô hình B, số iALS/CFNet, độ trễ, số Sampled-99, số hiệu bảng của bản cũ).

---

## 5. Thay đổi giai đoạn trước (giao thức v1, đầu phiên)

- **Thuật ngữ theo luận án của GVHD:** NeuMF là Early Fusion; Late Fusion là trộn điểm của các mô hình huấn luyện riêng; MLP đứng riêng là DNN thuần. Đã sửa trong code (`early_fusion.py`, `03_run_experiment.py`, `05_evaluate.py`) và báo cáo.
- **Trình bày:** chú thích bảng/hình tiếng Việt, bỏ so sánh với số liệu bài báo (`13_plot_final.py`, `15_export_report.py`). Bảng, hình v1 sinh lại, số liệu không đổi.
- **Kiểm tra:** `18_preflight.py` có sai số cho phép khi chạy lại trên CPU. `audit/PREREG.md` có thêm mục ngày 03/10.
- **Dọn dẹp:** xoá `.vscode/settings.json` và checkpoint thừa `early_fusion.pt`.

---

## 6. Hiệu quả so với trước

| Tiêu chí | v1 | v2 |
|---|---|---|
| Độ tin cậy số liệu | Test đã xem nhiều lần; nhiều quyết định sau khi xem | Mẫu B độc lập, mở test một lần, đăng ký trước, khoá bằng mã băm mã nguồn |
| Bài toán | Bỏ sản phẩm mới → dễ hơn thực tế | Có sản phẩm mới → sát thực tế |
| Rò rỉ | k-core dùng dữ liệu test | Hết rò rỉ đã biết (có test tự động) |
| Mô hình lai | NeuMF chỉ dùng ID | NeuMF-F có đặc trưng; tách được 3 câu hỏi: đặc trưng, hợp nhất, sớm/muộn |
| Đối chứng | 7 mô hình | 14 mô hình (thêm MostPopular-Recent, Content) |
| Thống kê | 3 seed, 8 so sánh | 5 seed, 10 so sánh đăng ký trước |

**Lưu ý:** không đặt số v1 cạnh số v2, vì khác tập ứng viên và khác đáp án. Hiệu quả về **độ chính xác** của NeuMF-F
chỉ biết sau đánh giá cuối trên mẫu B.

---

## 7. Đối chiếu 17 góp ý của GVHD

| # | Góp ý | Trạng thái | Còn chờ |
|---|---|---|---|
| 1 | Kết quả cao bất thường, rò rỉ | Xong — chặt hơn v1 | Số trên mẫu B |
| 2 | Bộ test chuẩn chung | Xong — test của B chung cho 14 mô hình | Số |
| 3 | Top-K khách tương đồng / sản phẩm | Xong — UserKNN, ItemKNN là baseline chính thức; demo có thẻ khách tương đồng | — |
| 4 | Lọc cộng tác hoạt động thế nào | Xong | — |
| 5 | Khởi đầu lạnh | Tốt hơn v1 — sản phẩm mới trong phạm vi; khách mới dùng gợi ý theo luật | Số nhóm sản phẩm mới |
| 6 | NDCG và các chỉ số | Xong — thêm nhóm cũ/mới, K = 5, 10, 20 | — |
| 7 | Trình bày kết quả | Xong — bảng tự sinh | Số |
| 8 | Vai trò của MF | Xong | — |
| 9 | Mô hình lai thực sự | Xong — NeuMF-F | Kết quả so sánh #1–#4 |
| 10 | Transformer, Temporal, BERT | Đã dùng mô tả sản phẩm (TF-IDF + SVD); BERT/Transformer là hướng phát triển (không bắt buộc) | — |
| 11 | Yếu tố thời gian | Tốt hơn v1 — thời gian là đặc trưng đầu vào; có baseline MostPopular-Recent | Số ablation |
| 12–13 | Early / Late fusion | Xong — so sánh #4 đăng ký trước | Kết quả #4 |
| 14 | Baseline; lai có hơn trước khi lai | Xong — so sánh #1–#3 | Kết quả |
| 15 | Sơ đồ kiến trúc | Xong — Hình 3.1, 3.2 mới | Ảnh chụp demo |
| 16 | Mô hình "variational" | Chưa làm — chờ cô xác nhận (test của B chưa mở nên vẫn thêm được đúng quy trình) | Cô xác nhận |
| 17 | Lộ trình 10 bước | Bước 1–7, 9 xong | Bước 8, 10 chờ đánh giá cuối |

---

## 8. Tình hình hiện tại và mức độ hoàn thành

### 8.1 Theo hạng mục

| Hạng mục | Hoàn thành | Ghi chú |
|---|---|---|
| Dữ liệu và đặc trưng (mẫu B, danh mục, doanh số) | 100% | Đã sinh, MD5 ghi trong kế hoạch |
| Code giao thức v2 (dữ liệu, mô hình, huấn luyện, đánh giá) | 100% | 146 test qua; chạy thử trọn đường ống trên tập xác thực của A |
| Kế hoạch đăng ký trước (PREREG_v2) | 100% | **Chờ commit** |
| Tinh chỉnh trên mẫu A | 8/13 mô hình | Còn NeuMF, GMF-F, MLP-F, NeuMF-F, LateFusion-F — khoảng 4 giờ nữa (các mô hình có đặc trưng chạy lâu nhất) |
| Đánh giá cuối trên mẫu B | 0% | Cần tinh chỉnh xong + commit. CPU 12–17 giờ; GPU/Colab 2–5 giờ |
| Script kiểm định và xuất báo cáo | 100% | Đã chạy thử; chạy thật sau đánh giá cuối |
| Báo cáo: Chương 1–3, phụ lục, tài liệu tham khảo | 100% | Chương 3: chờ ảnh chụp demo |
| Báo cáo: Chương 4–5, tóm tắt | Khoảng 70% | Khung, bảng, hình, macro xong; phần thảo luận bằng chữ viết sau khi có số |
| Demo v2 | 90% | Code xong, đã kiểm tra khớp số; chờ checkpoint thật và ảnh chụp |
| Tài liệu (README, vấn đáp, phạm vi, notebook) | 90% | Số v2 cập nhật sau đánh giá cuối |

**Tổng thể: khoảng 75–80%.** Phần còn lại chủ yếu là thời gian máy chạy (tinh chỉnh khoảng 4 giờ + đánh giá cuối) và
viết phần thảo luận theo số liệu thật (khoảng 1–2 giờ).

### 8.2 Kết quả tinh chỉnh đã có

Tập xác thực của mẫu A, NDCG@10. Số này chỉ dùng để chọn cấu hình, không dùng để kết luận.

| Mô hình | Cấu hình chọn | NDCG@10 |
|---|---|---|
| UserKNN | k = 200, shrink = 0 | 0,01216 |
| ItemKNN | k = 100, shrink = 50 | 0,01094 |
| BPR-MF | d = 128, lr = 0,03, reg = 0,001, 20 epoch | 0,00934 |
| GMF | d = 64, lr = 0,001, 8 mẫu âm, wd = 10⁻⁶ | 0,00845 |
| MostPopular-Recent | cửa sổ 14 ngày | 0,00830 |
| MLP | d = 32, lr = 0,0005, 4 mẫu âm, dropout 0 | 0,00797 |
| Most Popular | — | 0,00734 |
| Content | chu kỳ bán rã 30 ngày | 0,00499 |
| NeuMF, GMF-F, MLP-F, NeuMF-F, LateFusion-F | đang chạy | — |

### 8.3 Việc tiếp theo

1. **Bạn — ngay bây giờ:** `git add -A`, commit, push. Commit trước khi có kết quả tinh chỉnh của các mô hình có đặc trưng thì mốc thời gian mới chứng minh được kế hoạch có trước.
2. **Tự động — khoảng 4 giờ:** tinh chỉnh xong. Sau đó chạy `python scripts/24_report_v2.py --tuning-only` để đưa bảng tinh chỉnh vào báo cáo, viết mục 4.3, rồi **commit lần 2**.
3. **Bạn — chạy đánh giá cuối:** `python run.py v2-final --reason "Đánh giá cuối v2 theo PREREG_v2"`, chọn một trong ba nơi:
   - máy của bạn (CPU, 12–17 giờ);
   - máy RTX 3050 của bạn nhóm;
   - `notebooks/colab_v2.ipynb`.
4. **Sau đánh giá cuối:**
   - script tự sinh bảng, hình, kiểm định;
   - viết phần thảo luận Chương 4–5, cập nhật số v2 trong `van_dap.md`;
   - chụp ảnh demo, biên dịch báo cáo, commit.

### 8.4 Lưu ý và rủi ro

- **Không sửa** `src/`, `scripts/v2_common.py`, `scripts/22_tune_v2.py`, `configs/v2.yaml` cho tới khi đánh giá cuối xong. Đánh giá cuối sẽ từ chối chạy nếu mã nguồn khác lúc tinh chỉnh.
- **Không chạy** `23_final_v2.py` ngoài lần chạy chính thức. Mọi lần mở test của B đều bị ghi nhật ký.
- **NeuMF-F có thể không vượt** UserKNN/ItemKNN (hai baseline rất mạnh trên tập xác thực). Nếu vậy, báo cáo đúng như kế hoạch đã đăng ký; phân tích nhóm cũ/mới và ablation cho biết NeuMF-F hơn hay thua ở đâu.
- **Giả định "biết trước danh mục sắp bán"** cần nói rõ khi bảo vệ (PREREG_v2 mục 9, báo cáo mục 4.6).
- **Chạy trên GPU** có thể lệch nhẹ ở chữ số cuối so với CPU. Máy chạy được ghi tự động trong kết quả.
- **Mục 16 (variational):** nếu cô yêu cầu, cần làm **trước** khi mở test của B.

---

## 9. Danh sách file

**File mới (21):**

- Dữ liệu và kế hoạch: `neumf_project/audit/PREREG_v2.md`, `neumf_project/audit/v2/` (tuning_log.csv, best_configs.json, data_dev.json), `neumf_project/configs/v2.yaml`
- Code: `neumf_project/src/data_pipeline/{features,protocol_v2,feature_dataset}.py`, `neumf_project/src/models/hybrid_features.py`, `neumf_project/src/evaluation/v2.py`
- Script: `neumf_project/scripts/{21_build_features,22_tune_v2,23_final_v2,24_report_v2,v2_common}.py`
- Test và notebook: `neumf_project/tests/{test_v2,test_v2_final}.py`, `neumf_project/notebooks/colab_v2.ipynb`
- Log tinh chỉnh: `neumf_project/outputs/v2/` (tune_all.log, tune_all.err, tune_part1.log)

**File sửa chính:**

- Báo cáo: `Report DACNTT/` (C1–C5, tóm tắt, phụ lục, `preamble.tex`, `references.bib`, danh mục viết tắt)
- Demo: `neumf_project/demo/` (backend, frontend, README, test)
- Script và code: `run.py`, `00_sample_hm.py`, `19_check_report.py`, `src/training/trainer.py`
- Tài liệu: `neumf_project/README.md`, `neumf_project/pham_vi_du_an.md`, `van_dap.md`
- Thay đổi v1 đầu phiên: mục 5 ở trên

Quy mô: khoảng 2.700 dòng code mới cho v2 và test; 76 file đã theo dõi được sửa (+1.885 / −901 dòng).
