# Tổng hợp đồ án: phương pháp, kết quả và tiến độ

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu.
**Sinh viên:** Lê Minh Lý (52300220), Sử Thị Yến Linh (52300218). **GVHD:** TS. Hồ Thị Linh.
**Cập nhật:** 06/11/2026, sau đợt rà soát toàn bộ code, demo và báo cáo (mục 2.1). Trước đó (29/10): sửa báo cáo, sơ đồ
và demo theo góp ý buổi họp ngày 23/10/2026. Trước nữa
(14/10, commit `fcf33f3`): sửa theo góp ý buổi họp 04/10, thêm mô hình lai truyền thống Hybrid-CBCF cho nhóm baseline
"học máy truyền thống" (mục 8.5; kết quả ở mục 3.7 và 4.6), và viết lại văn phong báo cáo (mục 10.4).

File này thay cho hai file cũ `neumf_project/pham_vi_du_an.md` (phạm vi, phương pháp) và `tong_hop_thay_doi_v2.md`
(kết quả, tiến độ). Tài liệu khác:

- Cài đặt và chạy: `neumf_project/README.md`; demo: `neumf_project/demo/README.md`.
- Chuẩn bị vấn đáp: `van_dap.md`.
- Ràng buộc đầy đủ của thực nghiệm: kế hoạch đăng ký trước `audit/PREREG_v2.md` (H&M) và `audit/PREREG_amazon.md`
  (Amazon Beauty).

Quy ước đọc:

- Các thư mục `audit/`, `configs/`, `scripts/`, `src/`, `outputs/`, `tests/`, `demo/` đều nằm trong `neumf_project/`.
- "Báo cáo mục 4.5", "Bảng 4.3", "Hình 3.1", "Thuật toán 3.6" là số trong báo cáo LaTeX; "mục 2.2" không kèm chữ "báo
  cáo" là mục của file này.

| Cần biết | Mục |
|---|---|
| Đồ án làm gì và kết quả chính, đọc trong một phút | 1 |
| Đang ở đâu, còn việc gì, cần hỏi cô gì | 2 |
| Kết quả trên H&M và trên Amazon Beauty | 3, 4 |
| Những điều phải nói thẳng khi bảo vệ | 5 |
| Bài toán, dữ liệu, mô hình, cách đánh giá | 6–9 |
| Code, demo, kiểm thử, báo cáo | 10 |
| Hạn chế, đối chiếu 17 góp ý trước, lịch sử phát triển | 11–13 |
| Danh sách file, tài liệu tham khảo | 14 |
| **Học từ gốc**: khái niệm nền, công thức, ví dụ tính tay, thuật ngữ, câu hỏi tự kiểm tra | 15 |

---

## 1. Đồ án làm gì — nói ngắn

- **Bài toán:** với mỗi khách hàng H&M, gợi ý 10 sản phẩm thời trang khách có khả năng mua lần đầu trong 8 tuần tới. Chỉ
  có lịch sử mua (phản hồi ngầm), không có điểm đánh giá. Một sản phẩm là một **mẫu thiết kế** (`product_code`, gộp mọi
  màu).
- **Mô hình đề xuất NeuMF-F:** giữ khung NeuMF — nhánh nhân tử hoá ma trận (GMF) và nhánh mạng nơ-ron sâu (MLP), hợp nhất
  sớm. Ngoài vector ID, mỗi khách và sản phẩm có thêm **đặc trưng**: thuộc tính và mô tả sản phẩm, thông tin khách, doanh
  số và thời gian.
- **Cách chứng minh:** so NeuMF-F với 13 mô hình khác trên cùng một tập kiểm thử, theo kế hoạch ghi sẵn từ trước. Mọi
  quyết định (chọn cấu hình) làm trên **mẫu phát triển**; kết luận lấy trên **mẫu kiểm định** — nhóm khách khác hẳn, tập
  kiểm thử chỉ mở một lần. Sau đó chạy lại đúng quy trình trên **Amazon Beauty** để kiểm chứng.
- **Kết quả chính:**
  - Trên H&M, NeuMF-F đứng 2/14 (NDCG@10 = 0,04003), tốt hơn có ý nghĩa 7/9 đối thủ và không khác biệt có ý nghĩa với
    GMF-F và LateFusion-F (0,04093, cao nhất).
  - Đặc trưng là phần đóng góp chính: NeuMF-F hơn NeuMF chỉ dùng ID 43,8% trên H&M và 65,7% trên Amazon, đều có ý nghĩa.
  - Trên Amazon, LateFusion-F tốt hơn NeuMF-F có ý nghĩa (NeuMF-F thấp hơn 12,5%). Báo cáo ghi đúng như vậy.
- **Baseline ba nhóm (góp ý họp 04/10):** mô hình đơn lẻ; học máy truyền thống; chuyên biệt cho gợi ý (mục 8.3). Nhóm
  học máy truyền thống có thêm **mô hình lai truyền thống Hybrid-CBCF** (Content + UserKNN + ItemKNN, theo chương 3
  luận án của cô) — phân tích bổ sung sau đánh giá cuối, có kế hoạch đăng ký riêng (mục 8.5). NeuMF-F tốt hơn nó có ý
  nghĩa trên cả hai bộ (+25,8% trên H&M, +23,0% trên Amazon); Hybrid-CBCF xếp 5/15, ngay sau bốn mô hình có đặc trưng.
- **Tên gọi:** báo cáo dùng "mẫu phát triển", "mẫu kiểm định", "mô hình đề xuất"; không dùng "mẫu A/B" hay "v1/v2".
  Chữ `v2` chỉ còn trong tên file, thư mục và lệnh (`PREREG_v2.md`, `outputs/v2/`, `v2-final`).

---

## 2. Tiến độ (18/11/2026)

### 2.1 Tình hình

| Hạng mục | Trạng thái |
|---|---|
| Thực nghiệm H&M | Xong ngày 10/10/2026. Tập kiểm thử đã mở, không chạy lại |
| Kiểm chứng Amazon Beauty | Xong ngày 10–11/10/2026; đã đưa vào báo cáo (báo cáo mục 4.4, Chương 5, tóm tắt) |
| 21 yêu cầu của buổi họp 04/10 | **20 hoàn thành** (#8 chờ cô xác nhận cách xếp nhóm), 1 chưa làm (mục 2.2) |
| Mô hình lai truyền thống (bổ sung) | Xong 13/10: mã, kế hoạch `PREREG_bosung.md`, tinh chỉnh trên tập xác thực, chấm tập kiểm thử một lần trên H&M và một lần trên Amazon (commit `fcf33f3`); kết quả ở mục 3.7 và 4.6 |
| Báo cáo | `main.pdf` 98 trang (rút gọn 12/11 theo skill định dạng: bớt ảnh demo trùng ý, hình hội tụ, hình Amazon trùng bảng, bảng API, câu rào đón), biên dịch không lỗi, không còn hộp tràn trang; mục 4.5 mới (Bảng 4.20) chỉ ra phần cải thiện đến từ đặc trưng, không từ tinh chỉnh, dữ liệu hay dao động ngẫu nhiên; 9 sơ đồ vẽ lại bằng `image/src/hinh_bao_cao.py` với một quy tắc màu chung; baseline trình bày theo ba nhóm; có kết quả Hybrid-CBCF; tóm tắt Việt, Anh có đoạn kết quả (nêu rõ LateFusion-F cao nhất), mỗi bản một trang; `check-report`: 75/75 câu nhận xét khớp số liệu, đủ mọi macro, bảng, hình |
| Demo | Luôn có gợi ý (khách mới nhận danh sách phổ biến); chọn được K = 10, 15, 20; ảnh Amazon lưu trên máy (`demo/static/images/amazon/`); ảnh H&M tải ngày 07/11 (6.728/6.749 sản phẩm, `demo/scripts/download_hm_images.py`); ảnh demo trong báo cáo (Hình 3.7, 3.8) chụp lại có ảnh thật |
| Bản nộp (15/11) | Đã commit bản 12/11 (`5d75321`) và bản dọn repo 14/11 (`1780b56`: bỏ comment, xoá ảnh/biểu tượng/sơ đồ cũ không dùng, hai zip công cụ vẽ). Ngày 15/11 dựng lại `main.pdf`, `Slide_DACNTT.pptx`, `Poster_DACNTT.pptx/.pdf` từ code sau khi dọn; khôi phục khuôn `poster/Poster.pptx` (bị xoá trên máy, `build_poster.py` cần); xoá `texput.log` |
| Bản sửa 18/11 | Commit `ad9eef8`: C2–C5 sửa câu chữ cho bớt lặp từ (không đổi số mục, bảng, hình, số liệu); thêm phiếu theo dõi tiến độ (`Report DACNTT/phieu_tien_do/`). Tối 18/11, sau khi rà như hội đồng: sửa mật độ ma trận ở mục 1.1.1 (0,02% theo mã sản phẩm, 0,04% theo mẫu thiết kế, tính lại từ tệp giao dịch gốc); C4 nói rõ kết luận "tốt hơn cả năm mô hình đối chứng" trên Amazon không dựa vào BPR-MF; bỏ mọi chỗ dẫn "Mục X.Y", "Công thức (…)", bảng hoặc thuật toán ở xa trong thân bài (chỉ giữ câu giới thiệu bảng, hình, thuật toán đặt ngay sau); tóm tắt vẫn không có số liệu; tài liệu tham khảo 24 nguồn đều được dẫn và đã đối chiếu (12 DOI qua Crossref, PDF gốc NCF và Rendle 2020 cho Bảng 2.1, luận án TS. Hồ Thị Linh trong `tai_lieu/`, BibTeX chính thức NeurIPS cho DropoutNet và PyTorch nên bỏ số trang không có trong bản ghi), xoá 6 mục thừa không được dẫn trong `references.bib`. Lượt rà cuối 18/11: thân bài không còn câu nhắc bảng, hình, thuật toán, mục (người xem tự xem bảng, hình đặt sau đoạn văn tương ứng), gọn các câu dài; phần demo thêm số đo hiệu năng đo thật (Bảng 3.7, script `demo/scripts/benchmark_demo.py`) và hai hình (thẻ sản phẩm kèm khách có gu giống; khách mới), bảng điểm cuối API chuyển thành đoạn văn; con số "trung vị 10 ms" cũ không có nguồn đã thay bằng số đo; 99 trang, `check-report` 75/75. Bản final (chuẩn bị nộp, ghi ngày 01/12/2026 ở Lời cảm ơn và trang cam đoan): Turnitin trên bản 16/11 (`baocao.pdf`) cho chỉ số trùng 11%, chủ yếu ở trang bìa, trang cam đoan theo mẫu, mục lục, danh mục viết tắt, tài liệu tham khảo và cụm thuật ngữ; Lời cảm ơn viết lại cho cụ thể (bỏ các câu sáo), phần thân giữ nguyên. Bản nộp gồm hai tệp, giữ cả hai: `main.pdf` (99 trang) và bản Word `BaoCaoWordDA.docx` (bản hiện có là 15/11, cần xuất lại từ `main.pdf` 18/11). `baocao.pdf` là bản PDF 16/11, chưa có phần sửa 18/11 |
| Kiểm thử | `tests/` 110/110 qua; `demo/tests` 21/21 qua (18/11); `check-report` khớp (18/11); demo đối chiếu từng kết quả với số đã lưu (mục 10.3) |
| Rà soát 06/11 | Code: test và biên dịch toàn bộ mã Python qua; demo chạy thật trên cả hai bộ (mọi trang, khách mới, K sai, mô hình sai, đường dẫn ảnh lạ), không lỗi console, trung vị khoảng 7 ms mỗi lần gợi ý. Đã sửa: hình kết quả đánh dấu Hybrid-CBCF bằng * như bảng (trước là †); Hình 3.2 dùng [H]; bỏ "khởi đầu lạnh" còn sót ở mục 2.1.4; Bảng 2.1 thêm kết quả của đề tài; Chương 5 nêu LateFusion-F cao nhất; `main.pdf` biên dịch lại với hình mới; README demo bỏ Docker đã xoá |
| Góp ý buổi họp 23/10 | Xong 8/9 việc của báo cáo và demo (bảng dưới); còn việc nộp báo cáo giữa kỳ (mục 2.3) |

Đối chiếu góp ý buổi họp 23/10/2026:

| Góp ý của cô | Trạng thái |
|---|---|
| Nói thẳng có mô hình cao hơn NeuMF-F | Xong: báo cáo mục 4.3, 4.4, 4.6, Chương 5 và tóm tắt Việt, Anh nêu LateFusion-F cao nhất trên cả hai bộ |
| Bỏ K = 5, dùng K = 10, 15, 20 | Xong (báo cáo mục 4.1 có lý do) |
| Trình bày quá trình xử lý dữ liệu | Xong (báo cáo mục 3.2, Hình 3.2) |
| Hình mô hình chỉ giữ NeuMF-F, vẽ lớn, bỏ mô hình đối chứng | Xong (Hình 3.4) |
| Hình ghi Top-K, không ghi Top-10 | Xong |
| Giải thích đầu ra: ŷ, hàm kích hoạt cuối, BCE và mẫu âm | Xong: hình ghi "ŷ: điểm dự đoán trong khoảng (0, 1)", σ ở lớp dự đoán, "BCE với nhãn y: 1 = đã mua, 0 = mẫu âm" |
| Mũi tên không chồng, không cắt nhau | Xong |
| Cold start không vẽ trong hình nhưng có viết | Xong (báo cáo mục 2.1.4 và 3.8) |
| Mục thiết lập thực nghiệm: so sánh cùng điều kiện | Xong (báo cáo mục 4.1, bảng điều kiện chung) |
| Ảnh demo lưu trên máy, không kéo từ nguồn ngoài | Amazon xong; H&M cần chép lại ảnh (mục 2.3) |

### 2.2 Đối chiếu 21 yêu cầu của buổi họp 04/10/2026

Nguồn: Google Doc "Tiến độ DACNTT theo góp ý họp 04 10". Bản trên Doc (12/10, commit `15fc47d`) ghi 9/21; bảng dưới là
trạng thái theo commit `e053c39`.

| # | Nhóm | Yêu cầu | Trạng thái | Minh chứng |
|---|---|---|---|---|
| 1 | Dữ liệu | Bỏ sản phẩm chưa có người mua khỏi ứng viên và đáp án | Hoàn thành | `make_stage` trong `src/data_pipeline/protocol_v2.py`; `PREREG_v2.md` mục 0; báo cáo mục 3.2.4 |
| 2 | Dữ liệu | Gộp các màu của một mẫu thành một sản phẩm | Hoàn thành | Mẫu phát triển: 55.971 → 27.370 sản phẩm trước mốc; Thuật toán 3.1 |
| 3 | Dữ liệu | Lọc khách và sản phẩm từ 10 giao dịch | Hoàn thành | k-core 10: còn 8.039 khách (mẫu phát triển), 7.994 khách (mẫu kiểm định) |
| 4 | Dữ liệu | Lưu dữ liệu đã lọc ra file, mọi mô hình đọc cùng file | Hoàn thành | `outputs/data/*.csv.gz`, kiểm MD5 theo `manifest.json` |
| 5 | Dữ liệu | Đánh giá cuối trên mẫu khách chưa từng dùng | Hoàn thành | Mẫu kiểm định là khối 2 |
| 6 | Dữ liệu | Dữ liệu đối chứng Amazon 5-core | Hoàn thành | Mục 4; báo cáo mục 4.4 (Bảng 4.11–4.19), Chương 5, tóm tắt |
| 7 | Mô hình | Chỉ một mô hình đề xuất | Hoàn thành | Báo cáo gọi thống nhất "mô hình đề xuất (NeuMF-F)" |
| 8 | Mô hình | Baseline ba nhóm: đơn lẻ, học máy truyền thống, chuyên biệt cho gợi ý | Hoàn thành | Bảng 3.5 (ba nhóm); Bảng 4.4 và 4.13 xếp theo nhóm. Mô hình lai truyền thống Hybrid-CBCF (mục 8.5): Thuật toán 3.6, Bảng 4.3, mục 4.3.4 (Bảng 4.8), Bảng 4.16. Cách xếp nhóm là đề xuất của nhóm, chờ cô xác nhận |
| 9 | Đánh giá | Báo cáo ở K = 10, 15, 20 (bỏ K = 5 ngày 24/10) | Hoàn thành | Bảng 4.5–4.6 (H&M), 4.14–4.15 (Amazon); K = 15 tính từ hạng đã lưu, đã ghi vào PREREG mục 10 |
| 10 | Đánh giá | Đường ống: đặc trưng → huấn luyện → lưu mô hình → suy diễn | Hoàn thành | Hình 3.1; báo cáo mục 3.8, Thuật toán 3.7; demo chỉ nạp checkpoint |
| 11 | Báo cáo | Ba nghiên cứu nền tảng và bảng đối chiếu số liệu tương đối | Hoàn thành | Bảng 2.1 (báo cáo mục 2.6): He et al. 2017, Rendle et al. 2020, luận án của cô |
| 12 | Báo cáo | Vẽ lại hình mô hình: kích thước ma trận, σ → sắp xếp → Top-K, không có ô đánh giá | Hoàn thành | Hình 2.1 (NeuMF), Hình 3.4 (NeuMF-F, vẽ lại lần hai theo góp ý 23/10) |
| 13 | Báo cáo | Vẽ lại đường ống, tách riêng quy trình đánh giá | Hoàn thành | Hình 3.1 (đường ống), Hình 3.5 (quy trình đánh giá); thêm Hình 3.2 (xử lý dữ liệu), Hình 3.3 (chia theo thời gian) |
| 14 | Báo cáo | Mã giả các thuật toán | Hoàn thành | Thuật toán 3.1–3.7 (3.6: mô hình lai truyền thống) |
| 15 | Báo cáo | Trình bày tiền xử lý thẳng thắn, thống nhất tên gọi | Hoàn thành | Báo cáo mục 3.2; bỏ "mẫu A/B", "v1/v2" |
| 16 | Báo cáo | Khởi đầu lạnh: khách mới thì gợi ý sản phẩm phổ biến | Hoàn thành | Báo cáo mục 2.1.4, 3.8, 3.9, 5.3; sửa câu "API báo lỗi" |
| 17 | Demo | Hiện tên và mô tả sản phẩm | Hoàn thành | Tên, mô tả, ảnh; H&M và Amazon |
| 18 | Demo | So hai mô hình cạnh nhau, kèm vị trí đoán trúng | Hoàn thành | Chế độ so sánh; Hình 3.7 |
| 19 | Demo | Luôn có gợi ý, không để trống | Hoàn thành | Mục 10.2 |
| 20 | Demo | Giao diện gọn | Hoàn thành | — |
| 21 | Làm việc với cô | Gửi các mô hình cho cô xem | **Chưa làm** | Checkpoint đã có trong git: `outputs/v2/final/seed42/`, `outputs/amazon/final/seed42/` |

**Tổng: 20/21 hoàn thành (#8 chờ cô xác nhận cách xếp nhóm), 1 chưa làm (#21).** Trong 17 việc
cần sửa ghi trên Google Doc, đã xong 15 (thêm "trình bày baseline theo ba nhóm"); việc còn lại nằm ở mục 2.3.

Một điểm làm khác ghi chú ban đầu (#19): ghi chú đề nghị trả danh sách phổ biến cho cả khách không có đáp án. Demo chỉ
làm vậy với khách chưa có trong dữ liệu; khách có lịch sử nhưng không có đáp án vẫn nhận gợi ý của mô hình, vì mô hình
chấm được khách này.

### 2.3 Việc còn lại

Đã xong ngày 13/10: chấm tập kiểm thử cho Hybrid-CBCF (H&M và Amazon) và viết nhận xét theo kết quả; viết lại văn phong
báo cáo (mục 10.4). Đã xong ngày 23–29/10: sửa theo góp ý buổi họp 23/10 (mục 2.1); vẽ lại gọn các sơ đồ của
báo cáo; từ 11/11 các hình sơ đồ sinh bằng `image/src/hinh_bao_cao.py` (bộ sơ đồ cũ đã xóa ngày 14/11).

1. **Hỏi khoa về báo cáo giữa kỳ**: hạn nghe được khoảng 25/10, không nộp bị trừ 1 điểm; nộp ở mục nộp bài (không phải
   mục báo cáo tiến độ hàng tuần), hệ thống đang đổi giao diện. Báo cáo cuối nộp tháng 11.
2. **Chạy demo khi bảo vệ trên máy GPU** (máy đã chạy đánh giá cuối, RTX 3050). Đo ngày 06/11: trên máy này 14 mô
   hình đăng ký trước trùng hạng đã lưu ở mọi khách (riêng NeuMF-F trên Amazon lệch 1/2.644 khách); Hybrid-CBCF, chấm
   trên máy chỉ có CPU, trùng 1.146/3.165 khách H&M và 1.617/2.644 khách Amazon, các khách còn lại demo hiện số đã lưu
   kèm lý do (mục 10.3). Nếu demo trên máy CPU thì chép `data/processed/hm/catalog_v2.npz` và
   `data/processed/amazon/catalog.npz` từ máy GPU sang; gửi cô checkpoint cũng nên kèm hai tệp này.
3. **Hỏi cô 5 câu**, rồi sửa báo cáo theo câu trả lời:
   1. Nhóm baseline "học máy truyền thống": nhóm đã thêm mô hình lai truyền thống Hybrid-CBCF (Content + UserKNN +
      ItemKNN theo chương 3 luận án của cô) và xếp ba nhóm như mục 8.3 — cô có đồng ý cách xếp này không?
   2. Amazon dùng lại siêu tham số chọn trên H&M, không tinh chỉnh riêng — cách kiểm chứng này có được chấp nhận không?
   3. Trên Amazon, LateFusion-F tốt hơn NeuMF-F có ý nghĩa. Nhóm giữ NeuMF-F là mô hình đề xuất như đã đăng ký và báo cáo
      đúng kết quả — cách trình bày này có ổn không?
   4. K = 15 tính lại từ thứ hạng đã lưu, không chạy lại mô hình — có được không?
   5. Ba nghiên cứu nền tảng là He et al. (2017), Rendle et al. (2020) và luận án của cô (2023) — cô có muốn đổi bài nào
      không?
4. **Gửi cô checkpoint** (`outputs/v2/final/seed42/`, `outputs/amazon/final/seed42/`) kèm hướng dẫn chạy demo
   (`neumf_project/demo/README.md`).
5. ~~**Làm slide**~~ — xong 06/11, làm lại 12/11: slide 15 trang (`Report DACNTT/slides/`: `build_slides.py` sinh
   `Slide_DACNTT.pptx`, nội dung hiện dần theo pha) và poster theo khung Khoa CNTT (`Report DACNTT/poster/`:
   `build_poster.py` sinh `Poster_DACNTT.pptx`, `.png`, `.pdf`). Số trên slide và poster chép từ mục 3–4; kết quả đổi
   thì sửa tay theo.
6. **Cập nhật Google Doc tiến độ** theo mục 2.2.

### 2.4 Mức độ hoàn thành theo hạng mục

| Hạng mục | Hoàn thành | Ghi chú |
|---|---|---|
| Dữ liệu và đặc trưng (hai mẫu H&M, Amazon) | 100% | MD5 của mẫu và của file dữ liệu đã lọc ghi trong kế hoạch |
| Kế hoạch đăng ký trước (H&M, Amazon) | 100% | Commit trước khi mở tập kiểm thử (khoá kiểm thử xác nhận) |
| Tinh chỉnh trên mẫu phát triển | 100% | 13/13 mô hình có cấu hình tốt nhất (`audit/v2/best_configs.json`) |
| Đánh giá cuối H&M | 100% | 5/5 seed; đã commit |
| Kiểm chứng Amazon | 100% | 5/5 seed; đã commit, đã vào báo cáo |
| Kiểm định, bảng, hình, macro (kể cả theo K) | 100% | Đã commit |
| Mô hình lai truyền thống (bổ sung) | 100% | Mã, kế hoạch, tinh chỉnh, chấm tập kiểm thử H&M và Amazon, nhận xét trong báo cáo |
| Code và kiểm thử | 100% | 110/110 test; demo 21/21 (mục 10.3) |
| Demo | 100% | Luôn có gợi ý; 4 ảnh trong báo cáo (Hình 3.7–3.10) và Bảng 3.7 số đo demo (`demo/scripts/benchmark_demo.py`, kết quả `outputs/demo/benchmark.json`); có ảnh sản phẩm thật cho cả H&M và Amazon |
| Báo cáo | 100% (bản nộp 12/11) | `main.pdf` 98 trang; đủ kết quả, kể cả Hybrid-CBCF; sửa theo góp ý 23/10; trình bày lựa chọn của nhóm theo tên đề tài; rút gọn theo skill định dạng; kiểm văn phong 0 cảnh báo; `check-report` khớp. Nếu cô trả lời 5 câu hỏi khác đề xuất của nhóm thì sửa theo |
| Slide, poster | 100% (bản nộp 12/11) | `Slide_DACNTT.pptx` 15 trang, `Poster_DACNTT.pdf`, cùng sơ đồ, màu và cách trình bày với báo cáo |
| Chuẩn bị bảo vệ | Một phần | `van_dap.md` viết lại cho hội đồng (20/10), thêm câu 5.4.6 về nguồn gốc cải thiện (12/11), thêm Phần 0 "10 câu dễ bị hỏi nhất" có trả lời ngắn và câu hỏi nối tiếp (18/11); còn luyện thuyết trình, vấn đáp và gửi cô checkpoint |

---

## 3. Kết quả trên H&M — đánh giá cuối trên mẫu kiểm định

### 3.1 Lần chạy

| Mục | Giá trị |
|---|---|
| Ngày, máy | 10/10/2026; GPU NVIDIA RTX 3050 Laptop (AMD Ryzen 7 6800H), PyTorch 2.6.0; 5 seed, tổng 7,5 giờ |
| Truy vết | Commit `e4e4f25`; mã nguồn không có thay đổi chưa lưu; mã băm mã nguồn `0f1ea1eec5a86c31`, trùng lúc tinh chỉnh; dữ liệu `data_md5` `ba5498d1…` |
| Lệch kế hoạch | Lần chạy đầu dừng giữa chừng ở seed 42 (đã chấm Random và 5 mô hình tất định, chưa lưu kết quả). Seed 42 được chạy lại một lần (`--allow-rerun`), ghi ở `PREREG_v2.md` mục 10 và dòng `v2_kiemdinh_seed42_rerun` của nhật ký. Các seed khác mở tập kiểm thử đúng một lần |
| Mẫu kiểm định sau lọc | 7.994 khách, 6.749 sản phẩm, 243.696 cặp |
| Tập kiểm thử | 3.165 khách được đánh giá, 10.285 cặp đúng, trung bình 6.710 ứng viên mỗi khách |
| File | `outputs/v2/final/`; đọc nhanh ở `ket_qua.txt` |

### 3.2 NDCG@10 của 14 mô hình (trung bình ± độ lệch chuẩn qua 5 seed)

| Hạng | Mô hình | Tập kiểm thử | Lúc tinh chỉnh (mẫu phát triển) |
|---|---|---|---|
| 1 | **LateFusion-F** | **0,04093 ± 0,00212** | **0,03556** |
| 2 | **NeuMF-F** (mô hình đề xuất) | 0,04003 ± 0,00147 | 0,03337 |
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

- Mô hình không có độ lệch chuẩn là mô hình tất định (giống nhau ở mọi seed).
- HR@10 của NeuMF-F là 15,0%, của LateFusion-F là 15,8%: khoảng 1/6 số khách có ít nhất một món đúng trong 10 gợi ý.
- Cột "lúc tinh chỉnh" chỉ dùng để chọn cấu hình, không cùng thang với cột tập kiểm thử (khác mẫu khách, cửa sổ kiểm thử
  dài gấp đôi).

### 3.3 Theo K (báo cáo mục 4.3.2, Bảng 4.5–4.6 chỉ trình bày K = 10, 15, 20; cột K = 5 dưới đây để tham khảo)

NeuMF-F, trung bình qua 5 seed:

| Độ đo | K = 5 | K = 10 | K = 15 | K = 20 |
|---|---|---|---|---|
| NDCG@K | 0,03120 | 0,04003 | 0,04644 | 0,05166 |
| Recall@K | 0,03453 | 0,05953 | 0,07801 | 0,09451 |
| HR@K | 0,09352 | 0,15046 | 0,19406 | 0,22976 |
| Precision@K | 0,02046 | 0,01723 | 0,01534 | 0,01403 |

- Ở mọi K và cả bốn độ đo, thứ tự LateFusion-F, NeuMF-F, GMF-F, MLP-F giữ nguyên và đứng trên mọi mô hình còn lại.
  Thứ tự giữa các baseline có đổi nhỏ (MostPopular-Recent vượt UserKNN ở HR@15 và HR@20).
- Cách tính: lấy cột hạng `ranks` đã lưu trong `seed*/per_user.csv.gz` (`scripts/7_report.py` → `by_k.csv`). Số
  @5/@10/@20 tính lại trùng hoàn toàn số đã lưu của lần đánh giá cuối (chênh lệch lớn nhất 0).

### 3.4 Họ 10 so sánh đăng ký trước

"A tốt hơn B" chỉ khi đủ cả ba điều kiện: p sau hiệu chỉnh Holm < 0,05; khoảng tin cậy 95% không chứa 0; chênh lệch
≥ 5%.

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

### 3.5 Phân tích phụ (chỉ mô tả, không kiểm định)

- **Ablation NeuMF-F (seed 42, bản đầy đủ = 0,04137):**
  - bỏ **đặc trưng thời gian: −42,3%** (khoảng tin cậy không chứa 0 — thành phần quan trọng nhất);
  - bỏ **thông tin khách: −10,3%** (khoảng tin cậy cũng không chứa 0);
  - bỏ thuộc tính sản phẩm −3,7% và bỏ văn bản −2,7% (khoảng tin cậy chứa 0).
- **Độ phủ top-10 (seed 42):** Most Popular và MostPopular-Recent thấp nhất (0,3%). Trong các mô hình cá nhân hoá, MLP
  thấp nhất (3,3%). NeuMF-F đạt 13,3% — cao nhất trong các mạng nơ-ron, sau ItemKNN (20,4%) và Content (78,2%).
  LateFusion-F đạt 5,3%.
- **Thời gian huấn luyện mỗi seed (GPU):** NeuMF-F 15,2 phút, GMF-F 13,7, MLP-F 16,4, NeuMF 6,2, BPR-MF 4,3.
- **Ổn định giữa hai mẫu:** bốn mô hình có đặc trưng đứng đầu ở cả lúc tinh chỉnh (mẫu phát triển) lẫn tập kiểm thử (mẫu
  kiểm định); LateFusion-F và NeuMF-F giữ hai vị trí đầu. GMF và MLP chỉ dùng ID tụt từ hạng 5 và 7 xuống 9 và 11 — hai
  mô hình duy nhất có NDCG@10 trên tập kiểm thử thấp hơn lúc tinh chỉnh. ItemKNN lên từ hạng 10 lên hạng 6.

### 3.6 Trả lời câu hỏi nghiên cứu

| Câu hỏi | Trả lời trên H&M |
|---|---|
| Đặc trưng có cải thiện mô hình lai không? | **Có.** NeuMF-F hơn NeuMF chỉ dùng ID 43,8%, có ý nghĩa. Phần lớn nhờ đặc trưng thời gian, tiếp theo là thông tin khách |
| Lai có hơn từng nhánh đứng riêng không? | **Hơn nhánh DNN** (MLP-F, +15,0%); **không hơn nhánh MF** (GMF-F, +2,6%, không có ý nghĩa) |
| Hợp nhất sớm hay muộn? | **Không khác biệt có ý nghĩa.** LateFusion-F cao hơn NeuMF-F 2,2% (p Holm 0,735) |
| NeuMF-F so với baseline? | Hơn cả 5 baseline trong họ so sánh: BPR-MF, ItemKNN, UserKNN, MostPopular-Recent, Content |
| NeuMF chỉ dùng ID so với MF? | Không khác biệt có ý nghĩa — cùng kết luận với giai đoạn phát triển ban đầu, trên mẫu khách mới |

### 3.7 Phân tích bổ sung: mô hình lai truyền thống Hybrid-CBCF (báo cáo mục 4.3.4, Bảng 4.8)

Chấm một lần ngày 13/10/2026 (commit `fcf33f3`, máy chỉ có CPU, dưới 1 phút), nhật ký `bosung_hybrid_hm`. Cách kết hợp và
trọng số chọn trên tập xác thực của mẫu phát triển (mục 8.5). Không thuộc họ 10 so sánh; hạng tính trên 15 mô hình.

| Mục | Giá trị |
|---|---|
| NDCG@10 / HR@10 | 0,03183 / 0,12354 — hạng 5/15, ngay sau bốn mô hình có đặc trưng, trên UserKNN (0,03114) |
| NDCG@K, K = 5 / 10 / 15 / 20 | 0,02550 / 0,03183 / 0,03748 / 0,04194 |
| Độ phủ top-10 | 10,8% — giữa UserKNN (5,7%) và ItemKNN (20,4%) |

| # | So sánh (họ bổ sung, Holm riêng) | Chênh NDCG@10 | Khoảng tin cậy 95% của A − B | p Holm | Kết luận |
|---|---|---|---|---|---|
| B1 | NeuMF-F vs Hybrid-CBCF | +25,8% | [0,00445; 0,01195] | < 0,001 | **NeuMF-F tốt hơn** |
| B2 | Hybrid-CBCF vs UserKNN | +2,2% | [−0,00061; 0,00195] | 0,152 | Không khác biệt có ý nghĩa |

- Mô hình lai học sâu có đặc trưng hơn rõ mô hình lai truyền thống. Trên H&M, Hybrid-CBCF chỉ nhỉnh hơn thành phần mạnh
  nhất của nó (UserKNN): trọng số dồn vào UserKNN (0,60) và Content đứng riêng rất yếu.
- Đối chiếu thành phần: UserKNN, ItemKNN chấm lại trùng hạng ở 3.165/3.165 khách. Content đạt 0,00481 so với 0,00506 lúc
  đánh giá cuối, do tệp đặc trưng văn bản dựng lại trên máy khác; Content chỉ chiếm trọng số 0,12.

---

## 4. Kiểm chứng trên Amazon Beauty

Mục đích: xem các kết luận của H&M có còn đúng trên một bộ dữ liệu khác không. Cùng mã, cùng 14 mô hình, cùng họ 10 so
sánh. **Không tinh chỉnh lại**: mọi mô hình dùng cấu hình chọn trên H&M, chỉ số epoch được chọn trên tập xác thực Amazon.
Dữ liệu và cách chia: mục 7.6.

### 4.1 Lần chạy

| Mục | Giá trị |
|---|---|
| Kế hoạch | `audit/PREREG_amazon.md`: commit bản đầu lúc 22:41 ngày 10/10/2026; 22:55 sửa thành **không tinh chỉnh**, dùng cấu hình chọn trên H&M. Cả hai trước khi chạy mô hình nào trên Amazon. `PREREG_amazon.md` mục 10 (lệch kế hoạch): chưa có |
| Ngày, máy | Bắt đầu 23:11 ngày 10/10/2026; 5 seed, tổng khoảng 3 giờ; GPU NVIDIA RTX 3050 Laptop, PyTorch 2.6.0 |
| Truy vết | Commit `f866337`, tree sạch; mã băm mã nguồn `8a14d1b03f4e8926`; dữ liệu `data_md5` `1bbee3d3…`; cấu hình lấy từ `audit/v2/best_configs.json`; nhật ký `amazon_kiemdinh_seed<N>` (5 dòng, mỗi seed mở tập kiểm thử một lần) |
| Tập kiểm thử | 2.644 khách được đánh giá, 6.107 cặp đúng, trung bình 6.058 ứng viên mỗi khách |
| Chạy thử trước khi đăng ký | 22:08 ngày 10/10: một script khác chạy thử trên tập xác thực Amazon (Random, MostPopular, BPR-MF, 1 epoch, mốc khác), không mở tập kiểm thử. Ghi ở `PREREG_amazon.md` mục 9; không quyết định nào dựa trên số đó |
| File | `outputs/amazon/final/`; đọc nhanh ở `ket_qua.txt` |

### 4.2 Kết quả trên tập kiểm thử Amazon (5 seed; báo cáo Bảng 4.13)

| Hạng | Mô hình | NDCG@10 | HR@10 |
|---|---|---|---|
| 1 | **LateFusion-F** | **0,03747 ± 0,00180** | **0,10802** |
| 2 | GMF-F | 0,03298 ± 0,00259 | 0,09410 |
| 3 | **NeuMF-F** (mô hình đề xuất) | 0,03277 ± 0,00189 | 0,09750 |
| 4 | MLP-F | 0,03065 ± 0,00193 | 0,08737 |
| 5 | UserKNN | 0,02506 | 0,07716 |
| 6 | ItemKNN | 0,02333 | 0,07186 |
| 7 | NeuMF (chỉ ID) | 0,01978 ± 0,00176 | 0,06694 |
| 8 | GMF | 0,01627 ± 0,00173 | 0,05582 |
| 9 | MostPopular-Recent | 0,01401 | 0,03858 |
| 10 | MLP | 0,01271 ± 0,00054 | 0,04667 |
| 11 | BPR-MF | 0,01144 ± 0,00091 | 0,04115 |
| 12 | Content | 0,00945 | 0,03215 |
| 13 | Most Popular | 0,00872 | 0,03744 |
| 14 | Random | 0,00101 ± 0,00028 | 0,00446 |

Theo K (báo cáo Bảng 4.14–4.15): LateFusion-F cao nhất ở mọi K và cả bốn độ đo. NeuMF-F và GMF-F bám sát nhau: GMF-F
cao hơn một chút ở NDCG@K; NeuMF-F cao hơn một chút ở Recall@K, HR@K và Precision@K từ K = 10 trở lên. NDCG@K của
NeuMF-F: 0,02450 / 0,03277 / 0,03751 / 0,04144 ở K = 5 / 10 / 15 / 20.

### 4.3 Họ 10 so sánh, đặt cạnh kết luận của H&M (báo cáo Bảng 4.17–4.18)

| # | So sánh | Chênh (Amazon) | Khoảng tin cậy 95% của A − B | p Holm | Kết luận Amazon | Kết luận H&M |
|---|---|---|---|---|---|---|
| 1 | NeuMF-F vs NeuMF | +65,7% | [0,00936; 0,01681] | < 0,001 | **NeuMF-F tốt hơn** | NeuMF-F tốt hơn |
| 2 | NeuMF-F vs GMF-F | −0,6% | [−0,00228; 0,00186] | 0,534 | Không khác biệt có ý nghĩa | Không khác biệt |
| 3 | NeuMF-F vs MLP-F | +6,9% | [−0,00044; 0,00457] | 0,050 | Không khác biệt có ý nghĩa | NeuMF-F tốt hơn |
| 4 | NeuMF-F vs LateFusion-F | −12,5% | [−0,00668; −0,00279] | < 0,001 | **LateFusion-F tốt hơn** | Không khác biệt |
| 5 | NeuMF-F vs BPR-MF | +186,5% \* | [0,01756; 0,02528] | < 0,001 | **NeuMF-F tốt hơn** | NeuMF-F tốt hơn |
| 6 | NeuMF-F vs ItemKNN | +40,5% | [0,00477; 0,01417] | < 0,001 | **NeuMF-F tốt hơn** | NeuMF-F tốt hơn |
| 7 | NeuMF-F vs UserKNN | +30,8% | [0,00313; 0,01232] | < 0,001 | **NeuMF-F tốt hơn** | NeuMF-F tốt hơn |
| 8 | NeuMF-F vs MostPopular-Recent | +134,0% | [0,01553; 0,02201] | < 0,001 | **NeuMF-F tốt hơn** | NeuMF-F tốt hơn |
| 9 | NeuMF-F vs Content | +246,7% | [0,01902; 0,02766] | < 0,001 | **NeuMF-F tốt hơn** | NeuMF-F tốt hơn |
| 10 | NeuMF vs BPR-MF | +72,9% \* | [0,00630; 0,01038] | < 0,001 | **NeuMF tốt hơn** | Không khác biệt |

\* Trên Amazon, BPR-MF dùng cấu hình chọn trên H&M và chỉ đạt 0,01144 — thấp hơn cả ItemKNN, UserKNN và
MostPopular-Recent. Hai so sánh có BPR-MF ở Amazon chỉ nên đọc kèm cảnh báo này.

- So sánh 3: p Holm = 0,0499 (dưới 0,05) nhưng khoảng tin cậy chứa 0, nên theo tiêu chí là không khác biệt có ý nghĩa.
- **Tổng trên Amazon:** NeuMF-F tốt hơn 6/9 đối thủ, ngang 2 (GMF-F, MLP-F), thua 1 (LateFusion-F).

### 4.4 Ba kết luận của H&M có còn đúng không (báo cáo mục 4.4.3)

| Kết luận của H&M | Trên Amazon |
|---|---|
| (1) Mô hình có đặc trưng hơn mô hình chỉ dùng ID | **Còn đúng.** NeuMF-F hơn NeuMF 65,7%; bốn mô hình có đặc trưng đứng đầu và NeuMF-F hơn có ý nghĩa cả năm baseline trên cả hai bộ. Đây là kết luận vững nhất: giữ nguyên khi đổi lĩnh vực, loại tương tác (đánh giá thay vì mua), bộ đặc trưng nghèo hơn, và không tinh chỉnh lại |
| (2) NeuMF-F so với GMF-F, MLP-F, LateFusion-F | **Chỉ đúng một phần.** Vẫn ngang GMF-F; lợi thế so với MLP-F không còn; LateFusion-F **tốt hơn** NeuMF-F có ý nghĩa |
| (3) NeuMF chỉ dùng ID so với BPR-MF | **Không đối chiếu được.** Chênh +72,9% nhiều khả năng do cấu hình của BPR-MF không hợp với Amazon; không tinh chỉnh nên không tách được nguyên nhân |

### 4.5 Ablation và độ phủ (seed 42; báo cáo Bảng 4.19)

- **Ablation (bản đầy đủ = 0,03378):** bỏ **đặc trưng thời gian −31,6%** và bỏ **thuộc tính sản phẩm −14,4%** (khoảng tin
  cậy không chứa 0); bỏ văn bản −9,8% và bỏ thông tin khách +1,3% (khoảng tin cậy chứa 0). Trên Amazon, "thông tin khách"
  chỉ là hai đặc trưng thời gian của khách.
- **Độ phủ top-10:** NeuMF-F đạt 20,5%. Hai nhánh khác nhau rất xa: GMF-F 32,1%, MLP-F 5,4%. LateFusion-F đạt 15,3%. Most
  Popular và MostPopular-Recent thấp nhất (0,2% và 0,3%).
- **Số epoch chọn của NeuMF-F theo seed:** 4, 5, 3, 6, 9; huấn luyện khoảng 4,1 phút mỗi seed.

### 4.6 Hybrid-CBCF trên Amazon (phân tích bổ sung; báo cáo mục 4.4.2, Bảng 4.16)

Dùng nguyên cách kết hợp và trọng số chọn trên H&M, không chọn lại; chấm một lần ngày 13/10/2026 (nhật ký
`bosung_hybrid_amazon`).

| Mục | Giá trị |
|---|---|
| NDCG@10 / HR@10 | 0,02664 / 0,08169 — hạng 5/15, ngay sau bốn mô hình có đặc trưng, trên UserKNN (0,02506) |
| Độ phủ top-10 | 46,6% — giữa UserKNN (34,6%) và ItemKNN (63,2%) |
| B1: NeuMF-F vs Hybrid-CBCF | +23,0%, khoảng tin cậy [0,00138; 0,01083], p Holm < 0,001 — **NeuMF-F tốt hơn** |
| B2: Hybrid-CBCF vs UserKNN | +6,3%, khoảng tin cậy [0,00026; 0,00292], p Holm 0,009 — **Hybrid-CBCF tốt hơn** |

- B1 giống H&M; B2 khác H&M. Một khác biệt có thể góp phần (nhận định, chưa kiểm chứng): Content đứng riêng chỉ bằng
  khoảng 1/6 NDCG@10 của UserKNN trên H&M nhưng hơn 1/3 trên Amazon (0,00945 so với 0,02506), nên thành phần nội dung
  mang thêm nhiều thông tin hơn.
- Đối chiếu thành phần: UserKNN, ItemKNN trùng hạng ở 2.644/2.644 khách; Content 0,00942 so với 0,00945.

---

## 5. Những điều phải nói thẳng khi bảo vệ

1. **NeuMF-F không phải mô hình tốt nhất.** Trên H&M, LateFusion-F cao hơn một chút (0,04093 so với 0,04003) nhưng không
   khác biệt có ý nghĩa; trên Amazon, LateFusion-F tốt hơn có ý nghĩa. NeuMF-F là mô hình đề xuất cố định từ trước
   (`PREREG_v2.md` mục 8), không chọn lại theo kết quả. Lợi ích chủ yếu đến từ **đặc trưng**, không từ cách ghép hai
   nhánh: NeuMF-F ngang GMF-F đứng riêng trên cả hai bộ dữ liệu.
2. **Lý do LateFusion-F thắng trên Amazon chỉ là nhận định, chưa kiểm chứng:** hai nhánh gợi ý những tập sản phẩm rất
   khác nhau (độ phủ 32,1% so với 5,4%) nên trộn điểm tận dụng được sự khác nhau đó; hoặc trọng số trộn w và cấu hình
   chọn trên H&M hợp với LateFusion-F hơn.
3. **Bản cuối được quyết định sau khi xem kết quả khối 1** (mục 13.2). Vì vậy khối 1 bị loại; kết luận lấy trên khối 2,
   chưa ai xem trước; kế hoạch bản cuối được commit trước khi dựng tập kiểm thử của khối 2.
4. **Seed 42 của H&M chạy lại một lần** vì lần đầu dừng giữa chừng: đã ghi lệch kế hoạch; không quyết định nào đưa ra sau
   khi thấy các số trên màn hình; 5 mô hình tất định cho cùng kết quả ở lần chạy lại.
5. **Không có sản phẩm mới trong đánh giá.** Không được nói đề tài "xử lý khởi đầu lạnh của sản phẩm". Cơ chế bỏ ID ngẫu
   nhiên có trong thiết kế, nhưng NeuMF-F và MLP-F chọn ρ = 0 (chỉ GMF-F chọn ρ = 0,25). Khách mới chỉ được xử lý ở mức
   hệ thống (gợi ý phổ biến), không được đánh giá.
6. **Kết quả khối 1 khác bản cuối** (khối 1: LateFusion-F tốt hơn NeuMF-F có ý nghĩa; bản cuối trên H&M: không khác
   biệt). Hai lần khác dữ liệu; chỉ bản cuối dùng để kết luận; không đặt số của hai lần cạnh nhau.
7. **Amazon không tinh chỉnh lại:** mô hình nào kém đi thì không tách được do bản thân mô hình hay do cấu hình. Rõ nhất là
   BPR-MF, nên hai so sánh có BPR-MF trên Amazon chỉ đọc kèm cảnh báo.
8. **Amazon không có mẫu khách độc lập:** chọn số epoch và đánh giá cuối khác nhau theo thời gian, không theo khách. Đánh
   giá sản phẩm không đồng nghĩa với mua. Nhóm giá là giá lúc thu thập metadata (2014), không phải giá tại ngày đánh giá
   — hạn chế này được ghi thêm ngày 13/10/2026, sau đánh giá cuối, không đổi kế hoạch, cấu hình hay kết quả.
9. **K = 15 không có trong kế hoạch đăng ký trước:** tính lại từ hạng đã lưu, không mở lại tập kiểm thử; chỉ mô tả, không
   kiểm định.
10. **Hybrid-CBCF được thêm sau khi đã mở tập kiểm thử** của 14 mô hình, kể cả ba thành phần của nó. Thiết kế lấy từ luận
    án của cô, cách kết hợp chọn trên tập xác thực, kế hoạch bổ sung commit trước khi chấm; kết quả chỉ là phân tích bổ
    sung, họ kiểm định riêng, không đổi kết luận đã đăng ký.

---

## 6. Bài toán, câu hỏi nghiên cứu và phạm vi

### 6.1 Bài toán

Khuyến nghị Top-K từ **phản hồi ngầm**: chỉ biết khách đã mua gì ($y_{ui} = 1$), không có điểm đánh giá. $y_{ui} = 0$
không có nghĩa là khách không thích — có thể chỉ là chưa thấy. Vì vậy bài toán là **xếp hạng**, và khi huấn luyện cần lấy
mẫu âm.

Tại một mốc thời gian, với mỗi khách, mô hình chấm điểm mọi sản phẩm trong **tập ứng viên** — các sản phẩm đã có dữ liệu
huấn luyện trước mốc, trừ món khách đã mua — rồi xếp giảm dần và lấy K món đầu.

### 6.2 Câu hỏi nghiên cứu

Trả lời bằng **họ 10 so sánh** đăng ký trước (cách kiểm định ở mục 9.3). Cùng họ này được chạy lại trên Amazon Beauty.

| Câu hỏi | So sánh |
|---|---|
| Đặc trưng có cải thiện mô hình lai không? | NeuMF-F vs NeuMF |
| Mô hình lai có hơn từng nhánh đứng riêng không? | NeuMF-F vs GMF-F; NeuMF-F vs MLP-F |
| Hợp nhất sớm hay hợp nhất muộn? | NeuMF-F vs LateFusion-F |
| NeuMF-F so với các baseline đã tinh chỉnh | NeuMF-F vs BPR-MF, ItemKNN, UserKNN, MostPopular-Recent, Content |
| Mô hình lai chỉ dùng ID so với MF | NeuMF vs BPR-MF |

### 6.3 Yêu cầu R1–R9

| Mã | Yêu cầu |
|---|---|
| R1 | H&M Personalized Fashion Recommendations là bộ dữ liệu **chính** cho kết quả. Amazon Beauty 2014 (5-core) chỉ dùng để **kiểm chứng** kết luận, không tinh chỉnh trên đó |
| R2 | **Lai MF + DNN có đặc trưng**: lõi là GMF + MLP hợp nhất sớm như NeuMF; được dùng thuộc tính và mô tả văn bản của sản phẩm (`articles.csv`), thuộc tính khách (`customers.csv`), doanh số theo ngày của toàn H&M. Trên H&M không dùng ảnh, giá. NeuMF, GMF, MLP chỉ dùng ID giữ làm đối chứng |
| R3 | GMF + MLP → NeuMF theo He et al. (2017) |
| R4 | **Không dùng thông tin tương lai**: đặc trưng tại ngày t chỉ dùng dữ liệu trước t; k-core chỉ dùng cặp trước mốc kiểm thử; mẫu âm chỉ lấy trong sản phẩm đã ra mắt |
| R5 | Tinh chỉnh có hệ thống; mọi cấu hình ghi vào `audit/v2/tuning_log.csv` kèm mã băm mã nguồn |
| R6 | Precision@K, Recall@K, NDCG@K (giữ HR@K) ở K = 5, 10, 15, 20; **Full Ranking** trên toàn bộ tập ứng viên |
| R7 | Triển khai được: demo web suy diễn bằng đúng mô hình của đánh giá cuối, luôn có gợi ý (khách mới nhận danh sách phổ biến) |
| R8 | Báo cáo khớp code và file kết quả (số liệu qua macro tự sinh) |
| R9 | Kết luận lấy trên **mẫu khách hàng độc lập** (mẫu kiểm định), mở tập kiểm thử đúng một lần theo kế hoạch đăng ký trước |

### 6.4 Phạm vi

**Trong phạm vi**

- Dữ liệu H&M: hai mẫu khách hàng không giao nhau, khoảng 500 nghìn giao dịch mỗi mẫu; sản phẩm theo mẫu thiết kế.
- Đặc trưng sản phẩm (thuộc tính, mô tả văn bản), khách hàng (thuộc tính) và thời gian (doanh số, tuổi sản phẩm, khoảng
  cách lần mua) — tính theo thời điểm.
- 14 mô hình cùng ngân sách tinh chỉnh; 5 seed; kiểm định có hiệu chỉnh Holm; ablation 4 thành phần của NeuMF-F; bốn độ
  đo ở K = 5, 10, 15, 20.
- Kiểm chứng trên Amazon Beauty 2014 (5-core) với cấu hình chọn trên H&M.
- Demo web suy diễn bằng đúng mô hình của đánh giá cuối, cho cả H&M và Amazon Beauty.

**Ngoài phạm vi**

- Khởi đầu lạnh của **sản phẩm**: sản phẩm chưa có người mua trước mốc (gồm sản phẩm vừa ra mắt) không thuộc tập ứng viên.
- Khởi đầu lạnh của **khách hàng** như một kết quả đánh giá. Khách chưa có lịch sử chỉ được xử lý ở mức hệ thống: demo
  gợi ý sản phẩm phổ biến (Most Popular), đủ lịch sử mới dùng mô hình đề xuất (báo cáo mục 3.7). Chất lượng gợi ý cho
  nhóm này không được đo.
- Gợi ý ở mức màu (`article_id`) — đề tài gợi ý ở mức mẫu thiết kế.
- Ảnh và giá sản phẩm H&M; biểu diễn mô tả bằng mô hình ngôn ngữ (BERT, Transformer) — đề tài dùng TF-IDF + SVD.
- Mô hình chuỗi (SASRec), mô hình đồ thị (LightGCN), tự mã hoá biến phân (Mult-VAE) — hướng phát triển (báo cáo mục 5.3).
- Toàn bộ H&M: Full Ranking trên toàn bộ danh mục vượt khả năng máy của nhóm (mục 7.1).
- Tìm siêu tham số tự động; tinh chỉnh riêng cho Amazon; triển khai production.

### 6.5 Vì sao thiết kế như vậy

| Việc làm | Lý do |
|---|---|
| Lai **MF + DNN** (GMF + MLP) | Đúng tên đề tài. MF chỉ học tương tác tuyến tính (tích vô hướng); DNN học tương tác phi tuyến. NeuMF (He et al., 2017) là kiến trúc chuẩn ghép hai nhánh này |
| Thêm **đặc trưng** vào NeuMF | Ở giai đoạn phát triển ban đầu, NeuMF chỉ dùng ID **không** hơn MF đã tinh chỉnh (0/8 so sánh có ý nghĩa). Vector ID chỉ học được từ lượt mua, nên với dữ liệu thưa, sản phẩm và khách ít lượt mua học được rất ít. Phải thêm thông tin về chính sản phẩm và khách (loại hàng, xu hướng bán, nhóm khách) thì mô hình mới có thêm cái để học |
| **Một sản phẩm = một mẫu thiết kế**; ứng viên là sản phẩm đã có người mua trước mốc | Theo góp ý của cô (09/10/2026). Mọi mô hình — kể cả mô hình chỉ dùng ID — chấm được mọi ứng viên, nên so sánh không phụ thuộc khả năng xử lý sản phẩm chưa có lịch sử bán |
| Chia **theo thời gian**, không leave-one-out | Leave-one-out để lọt thông tin tương lai: đo trên mẫu phát triển, 11,2% dữ liệu huấn luyện xảy ra **sau** món cần dự đoán (mục 7.4) |
| **Hai mẫu khách: phát triển và kiểm định** | Tập kiểm thử của mẫu phát triển đã bị xem nhiều lần ở giai đoạn phát triển. Mọi quyết định làm trên mẫu phát triển; kết luận lấy trên mẫu kiểm định — khách khác hẳn, tập kiểm thử chỉ mở một lần |
| Dữ liệu đã lọc ghi ra **file có MD5** | Mọi mô hình đọc đúng cùng một file; chương trình kiểm MD5 trước khi dùng |
| **Đăng ký trước** + khoá kiểm thử | Mô hình, lưới tinh chỉnh, độ đo, 10 so sánh và tiêu chí "tốt hơn" cố định trước khi xem kết quả, nên không thể chọn lại sau khi thấy số |
| **14 mô hình**, cùng ngân sách tinh chỉnh | Muốn nói "lai có tác dụng" thì phải so với: bản chỉ dùng ID (đặc trưng có giúp không), từng nhánh riêng (lai có hơn từng phần không), hợp nhất muộn (sớm hay muộn), và baseline mạnh (KNN, BPR-MF, phổ biến gần đây) |
| **5 seed**, kiểm định theo từng khách | Mạng nơ-ron dao động theo seed. Kiểm định Wilcoxon + bootstrap trên khoảng 3.000 khách, hiệu chỉnh Holm cho 10 so sánh; với chỉ 5 seed, kiểm định theo seed không bao giờ đạt p < 0,05 |
| **Ablation**, độ phủ | Biết thành phần nào của NeuMF-F đóng góp, và danh sách gợi ý có đa dạng không |
| **K = 5, 10, 15, 20** | Cô yêu cầu (họp 04/10). Tính lại từ hạng đã lưu nên không phải mở lại tập kiểm thử |
| **Kiểm chứng trên Amazon Beauty** | Cô yêu cầu dữ liệu đối chứng 5-core có bài báo đã dùng (họp 04/10). Một bộ dữ liệu không đủ để nói kết luận có tổng quát không. Chạy lại đúng quy trình, **không tinh chỉnh lại**, với kế hoạch riêng đăng ký trước, để không chọn lại gì theo dữ liệu mới |

---

## 7. Dữ liệu

### 7.1 Nguồn H&M và lý do lấy mẫu

Cuộc thi Kaggle H&M Personalized Fashion Recommendations:

| File | Nội dung | Dùng |
|---|---|---|
| `transactions_train.csv` | 31.788.324 giao dịch, 20/09/2018 → 22/09/2020 | `customer_id`, `article_id`, `t_dat` (ngày mua) |
| `articles.csv` | 105.542 sản phẩm (theo màu) | `product_code`, 11 thuộc tính danh mục, tên và mô tả |
| `customers.csv` | 1.371.980 khách | tuổi, trạng thái hội viên, tần suất nhận tin, FN, Active |

- Không dùng giá, kênh bán, mã bưu chính; ảnh chỉ hiển thị trên demo.
- `article_id` đọc dạng chuỗi và `zfill(10)` để giữ số 0 đầu. `product_code` = `article_id // 1000` (ba chữ số cuối là
  biến thể màu; có kiểm tra khớp cột `product_code` của `articles.csv`).
- **Vì sao lấy mẫu:** Full Ranking phải chấm **mọi** sản phẩm ứng viên cho mỗi khách. Trên toàn bộ H&M, ngay cả với
  k = 10 vẫn còn 633.130 khách × 80.265 sản phẩm — hàng chục tỷ cặp cho mỗi mô hình — vượt khả năng máy của nhóm (RAM
  16 GB). Vì vậy đề tài lấy mẫu **theo khách hàng** và giữ trọn lịch sử hai năm của khách được chọn; lấy theo dòng sẽ cắt
  vụn lịch sử từng khách.

### 7.2 Hai mẫu khách hàng

Băm `customer_id` (khoá cố định) vào 100.000 nhóm, chia dãy nhóm thành các **khối** liên tiếp, mỗi khối vừa đủ khoảng
500.000 giao dịch (`scripts/1_sample.py`).

| | Mẫu phát triển | Mẫu kiểm định |
|---|---|---|
| Khối | 0 | 2 |
| File (`data/processed/hm/`) | `mau_phat_trien.csv` | `mau_kiem_dinh.csv` |
| Nhóm băm `customer_id` (trên 100.000) | [0, 1597) | [3160, 4734) |
| Giao dịch | 500.269 | 500.164 |
| Khách | 21.599 | 21.351 |
| Dùng cho | Tinh chỉnh — chỉ trên tập xác thực | Đánh giá cuối — mở tập kiểm thử đúng một lần |

- Các khối không chồng nhau nên **không có khách chung** (đã kiểm tra trên hai file).
- Lấy mẫu bằng hàm băm với khoá cố định nên chạy lại luôn ra đúng cùng file (MD5 ghi trong `PREREG_v2.md` mục 1).
- **Vì sao mẫu kiểm định là khối 2:** mẫu phát triển cũng là mẫu của giai đoạn phát triển ban đầu, nên tập kiểm thử của
  nó đã bị xem nhiều lần; khối 1 ([1597, 3160)) là mẫu kiểm định của bản đầu kế hoạch và đã được mở ngày 04/10/2026
  (mục 13.2).

### 7.3 Tiền xử lý (`scripts/2_prepare.py`; báo cáo Thuật toán 3.1)

1. **Gộp màu theo `product_code`**: mọi màu của một mẫu là một sản phẩm; khách mua nhiều màu của cùng một mẫu chỉ tính
   một cặp. Trước mốc kiểm thử: mẫu phát triển từ 55.971 xuống 27.370 sản phẩm, từ 401.293 xuống 359.181 cặp; mẫu kiểm
   định từ 55.683 xuống 27.291 sản phẩm, từ 398.653 xuống 356.740 cặp.
2. **Gộp** giao dịch lặp thành cặp (khách, sản phẩm) duy nhất, giữ **ngày mua đầu**.
3. **Lọc 10-core** lặp tới hội tụ, **chỉ trên các cặp có ngày mua đầu trước mốc kiểm thử 29/07/2020**, để việc chọn
   khách và sản phẩm không dùng thông tin của giai đoạn kiểm thử. Còn lại: mẫu phát triển 8.039 khách, 6.801 sản phẩm,
   245.644 cặp; mẫu kiểm định 7.994 khách, 6.749 sản phẩm, 243.696 cặp.
   - Chọn k = 10 thay vì 5 vì giới hạn RAM: ở k = 5, danh mục mẫu phát triển theo `article_id` còn 23.067 sản phẩm và
     Full Ranking ước tính cần khoảng 10,7 GB RAM (khảo sát ở giai đoạn phát triển).
   - Hệ quả: dữ liệu thiên về khách mua nhiều.
4. **Ghi ra file** `outputs/data/<mẫu>.csv.gz` kèm MD5 trong `outputs/data/manifest.json`; mọi mô hình đọc cùng file và
   kiểm MD5 trước khi dùng.
5. **Phản hồi nhị phân**: mua = 1.

### 7.4 Giai đoạn đánh giá và tập ứng viên

| | Giai đoạn xác thực | Giai đoạn kiểm thử |
|---|---|---|
| Mốc τ | 01/07/2020 | 29/07/2020 |
| Cửa sổ sản phẩm đúng | 01/07 – 28/07/2020 (4 tuần) | 29/07 – 22/09/2020 (8 tuần) |
| Dữ liệu huấn luyện | Cặp đã lọc có ngày mua đầu trước τ | Như vậy — nên gồm cả cửa sổ xác thực |
| Dùng cho | Chọn cấu hình (mẫu phát triển); chọn số epoch (mẫu kiểm định) | Kết luận (chỉ mẫu kiểm định) |

- **Tập ứng viên** của một khách = sản phẩm có ít nhất một cặp huấn luyện trước τ, trừ món khách đã mua trước τ. Sản
  phẩm chưa có người mua trước τ (gồm sản phẩm vừa ra mắt) không thuộc tập ứng viên lẫn đáp án — thay đổi của bản cuối
  theo góp ý của cô (`PREREG_v2.md` mục 0).
- **Sản phẩm đúng** = món khách mua lần đầu trong cửa sổ và thuộc tập ứng viên. Một khách có thể có nhiều sản phẩm đúng;
  chỉ khách có dữ liệu huấn luyện mới được đánh giá. Món đã mua trước τ không bao giờ là sản phẩm đúng — mô hình dự đoán
  món **mới đối với khách**.
- Quy mô: mẫu phát triển ở giai đoạn xác thực có 2.569 khách được đánh giá, 8.636 cặp đúng, trung bình 6.762 ứng viên mỗi
  khách. Tập kiểm thử của mẫu kiểm định: mục 3.1.
- **Không chia leave-one-out** (cách của He et al., 2017) vì cách này để lọt thông tin tương lai (Meng et al., 2020). Đo
  trên mẫu phát triển ở giai đoạn phát triển, tính trung bình theo người dùng: 11,2% tương tác trong tập huấn luyện xảy ra
  sau ngày mua sản phẩm kiểm thử của người dùng đó; 60,9% người dùng có sản phẩm xác thực và sản phẩm kiểm thử mua cùng
  một ngày.

### 7.5 Đặc trưng theo thời điểm (H&M)

| Nhóm | Đặc trưng | Mã hoá |
|---|---|---|
| Sản phẩm — thuộc tính | 11 thuộc tính danh mục: loại, nhóm sản phẩm, hoạ tiết, nhóm màu, độ đậm màu, màu chủ đạo, bộ phận, chỉ mục, nhóm chỉ mục, khu, nhóm may mặc (3 thuộc tính màu là hằng số sau khi gộp theo mẫu) | Embedding 8 chiều mỗi thuộc tính (88 chiều) |
| Sản phẩm — văn bản | Tên và mô tả chi tiết | TF-IDF (từ đơn và cặp từ) → SVD 64 chiều → chuẩn hoá L2 |
| Sản phẩm — thời gian tại t | Doanh số toàn H&M trong 7, 28, 91 ngày trước t; tuổi sản phẩm; cờ "chưa từng bán trước t" | log(1 + x)/10; cờ 0/1 (5 chiều) |
| Khách — tĩnh | Nhóm tuổi, trạng thái hội viên, tần suất nhận tin, FN, Active | Embedding 8 chiều mỗi thuộc tính (40 chiều) |
| Khách — thời gian tại t | Số ngày từ lần mua gần nhất; số cặp đã mua | log(1 + x)/10 (2 chiều) |

- Đặc trưng tại ngày t chỉ dùng dữ liệu **trước** t. Khi huấn luyện, mỗi cặp dương mang chính ngày mua đầu của nó; khi
  đánh giá, t = τ. Có test tự động kiểm tra điều này.
- Doanh số lấy trên toàn bộ giao dịch H&M (dữ liệu doanh nghiệp có tại thời điểm dự đoán), không chỉ trong mẫu.
- TF-IDF và SVD khớp trên toàn bộ danh mục; phép khớp không dùng dữ liệu mua.
- Gộp theo mẫu: thuộc tính lấy theo biến thể có `article_id` nhỏ nhất; văn bản = trung bình các biến thể rồi chuẩn hoá
  L2; doanh số = tổng các biến thể; ngày bán đầu = ngày sớm nhất.
- Code: `scripts/3_features.py`, `src/data_pipeline/features.py`.

### 7.6 Amazon Beauty (`audit/PREREG_amazon.md`)

- **Nguồn:** Amazon review data 2014 (McAuley et al., 2015), danh mục Beauty, bản 5-core: 198.502 đánh giá của 22.363
  khách cho 12.101 sản phẩm (12/06/2002 – 23/07/2014). Mỗi đánh giá là một tương tác ẩn, không dùng điểm sao. Một sản
  phẩm là một `asin`.
- **Chia theo thời gian** (chỉ có một bộ dữ liệu, nên không có mẫu khách độc lập):

  | Giai đoạn | Khoảng thời gian |
  |---|---|
  | Huấn luyện khi chọn số epoch | trước 01/10/2013 |
  | Xác thực (chỉ để chọn số epoch) | 01/10 – 31/12/2013 |
  | Huấn luyện lại trước đánh giá cuối | mọi cặp trước 01/01/2014 |
  | Kiểm thử | 01/01 – 23/07/2014 |

- **k-core = 5**, lọc trên các cặp trước 01/01/2014: còn 10.681 khách, 6.069 sản phẩm, 94.009 cặp.
- **Đặc trưng:** 5 thuộc tính sản phẩm (thương hiệu, danh mục cấp 1–3, nhóm giá); văn bản title + description, cùng
  TF-IDF + SVD 64 chiều; đặc trưng thời gian của sản phẩm là số đánh giá 7/28/91 ngày trước t và tuổi sản phẩm. Amazon
  **không có thuộc tính khách**: nhánh khách chỉ còn hai đặc trưng thời gian.
- **Không tinh chỉnh:** mọi mô hình dùng cấu hình chọn trên H&M (`audit/v2/best_configs.json`; mục 8.3); chỉ số epoch của
  mạng nơ-ron được chọn trên tập xác thực Amazon.
- Code: `src/data_pipeline/adapters/amazon.py`, `configs/amazon.yaml`.

---

## 8. Mô hình

### 8.1 NeuMF-F — mô hình đề xuất (`src/models/hybrid_features.py`)

Mỗi nhánh b ∈ {G (GMF), M (MLP)} có embedding ID $P^b$, $Q^b$ và hai phép chiếu tuyến tính $W^b_U$, $W^b_I$ (không hệ
số chệch). Vector của khách u và sản phẩm i tại ngày t:

$$p^b_u(t) = P^b_u + W^b_U\, x_u(t), \qquad q^b_i(t) = m_i\, Q^b_i + W^b_I\, x_i(t)$$

- $x_u(t)$, $x_i(t)$: vector đặc trưng của khách và sản phẩm (mục 7.5). Embedding thuộc tính dùng chung cho hai nhánh;
  phép chiếu riêng từng nhánh.
- $m_i = 1$ với sản phẩm có dữ liệu huấn luyện — với tập ứng viên ở mục 7.4 là mọi sản phẩm được chấm. Khi huấn luyện,
  $m_i$ bị đặt về 0 ngẫu nhiên với xác suất ρ ∈ {0; 0,25; 0,5} (**bỏ ID ngẫu nhiên**, ý tưởng từ DropoutNet) để mô hình
  dựa một phần vào đặc trưng thay vì chỉ vào ID. ρ là siêu tham số.
- **Nhánh GMF-F:** $\phi^G = p^G_u \odot q^G_i$ (nhân từng phần tử — tương tác tuyến tính).
- **Nhánh MLP-F:** nối $[p^M_u ; q^M_i]$ rồi qua tháp [2d → d → d/2 → d/4], ReLU, dropout (tương tác phi tuyến).
- **Hợp nhất sớm:** $\hat{y}_{ui} = \sigma\big(h^\top [\phi^G ; \phi^M_L]\big)$. Khi xếp hạng dùng logit (trước sigmoid),
  vì sigmoid float32 bão hoà tạo điểm bằng nhau giả.
- **Huấn luyện:** binary cross-entropy với mẫu âm lấy lại mỗi epoch, chỉ trong các sản phẩm đã ra mắt tại ngày t của cặp
  dương, trừ món khách đã mua; Adam, batch 512, tối đa 20 epoch, dừng sớm sau 5 epoch không cải thiện NDCG@10 trên tập
  xác thực.
- **Cấu hình đã chọn:** d = 32, lr = 0,001, 8 mẫu âm mỗi cặp dương, weight decay 1e-6, dropout 0, ρ = 0.
- **Suy diễn Top-K:** chấm mọi ứng viên của khách, xếp theo logit, lấy K món đầu. Khách chưa có trong dữ liệu đã học nhận
  danh sách Most Popular (báo cáo mục 3.7, Thuật toán 3.7).

### 8.2 Hợp nhất sớm và hợp nhất muộn

Theo luận án của cô (Hồ Thị Linh, 2023):

- *Early fusion* (hợp nhất sớm) nối biểu diễn của các view rồi dùng **một** mô hình dự đoán — NeuMF và NeuMF-F thuộc
  loại này.
- *Late fusion* (hợp nhất muộn) cho mỗi view một mô hình riêng rồi gộp điểm — LateFusion-F.
- MLP-F đứng riêng là mô hình DNN thuần, không phải hợp nhất MF + DNN.

### 8.3 Mô hình đối chứng và cấu hình đã chọn

Cấu hình chọn trên tập xác thực của mẫu phát triển (`audit/v2/best_configs.json`); Amazon dùng lại đúng các cấu hình này.

| Nhóm | Mô hình | Cách hoạt động | Cấu hình đã chọn |
|---|---|---|---|
| Cận dưới | Random | Điểm ngẫu nhiên | — |
| Phổ biến | Most Popular | Số cặp trong tập huấn luyện của mẫu | — |
| | MostPopular-Recent | Số giao dịch toàn H&M (Amazon: số đánh giá) trong W ngày trước mốc | W = 28 ngày |
| Nội dung | Content | Hồ sơ khách = trung bình có trọng số theo độ mới của vector nội dung các sản phẩm đã mua; điểm = cosine | Chu kỳ bán rã 30 ngày |
| Láng giềng | ItemKNN | Cosine trên vector mua nhị phân của sản phẩm, có hệ số co, top-k láng giềng | k = 100, hệ số co 50 |
| | UserKNN | Như ItemKNN nhưng theo khách | k = 200, hệ số co 0 |
| MF | BPR-MF | MF tối ưu thứ hạng theo cặp (Rendle et al., 2009), chỉ dùng ID | d = 128, lr = 0,03, reg = 0,001, 20 epoch |
| Chỉ dùng ID | GMF, MLP, NeuMF | Kiến trúc NCF gốc (He et al., 2017) | GMF, MLP: d = 32, 8 mẫu âm; NeuMF: d = 64, 4 mẫu âm, dropout 0,2 |
| Có đặc trưng | GMF-F, MLP-F | NeuMF-F chỉ giữ một nhánh | d = 32, 8 mẫu âm; GMF-F ρ = 0,25, MLP-F ρ = 0 |
| Hợp nhất muộn | LateFusion-F | w · minmax(GMF-F) + (1 − w) · minmax(MLP-F), hai mô hình huấn luyện riêng | w = 0,4 |

Tổng cộng **14 mô hình** (kể cả NeuMF-F), cùng ngân sách tinh chỉnh. BPR-MF (d = 128, reg = 0,001) và ItemKNN (hệ số co
50) chọn ở biên lưới. Thêm mô hình bổ sung Hybrid-CBCF (mục 8.5) sau đánh giá cuối.

**Ba nhóm baseline** (báo cáo mục 4.2; cách xếp do nhóm đề xuất, chờ cô xác nhận — mục 2.3):

| Nhóm | Mô hình | Câu hỏi trả lời |
|---|---|---|
| Mô hình đơn lẻ | GMF, MLP (chỉ ID); GMF-F, MLP-F (có đặc trưng) | Hợp nhất hai nhánh có hơn từng nhánh đứng riêng không |
| Học máy truyền thống | Content, ItemKNN, UserKNN, BPR-MF; Hybrid-CBCF (bổ sung) | Mô hình lai học sâu có hơn các phương pháp truyền thống, kể cả một mô hình lai truyền thống, không |
| Chuyên biệt cho gợi ý | Most Popular, MostPopular-Recent; NeuMF; LateFusion-F | Có hơn xu hướng phổ biến, kiến trúc NCF gốc và hợp nhất muộn của cùng hai nhánh không |

Random là cận dưới. Bảng kết quả chính (H&M và Amazon) xếp mô hình theo ba nhóm; thứ hạng "xếp thứ k trong 14 mô
hình" vẫn tính trên 14 mô hình đăng ký trước.

### 8.4 Ablation NeuMF-F

- Cùng siêu tham số, tắt một thành phần: bỏ vector văn bản, bỏ đặc trưng thời gian, bỏ thông tin khách, bỏ thuộc tính
  sản phẩm. Chỉ seed 42, chỉ mô tả.
- Biến thể thứ năm của kế hoạch — bỏ cơ chế bỏ ID ngẫu nhiên (ρ = 0) — trùng hệt NeuMF-F vì NeuMF-F đã chọn ρ = 0, nên
  không chạy.
- Code: `scripts/common.py`.

### 8.5 Mô hình lai truyền thống Hybrid-CBCF — bổ sung sau đánh giá cuối

Theo góp ý "baseline ba nhóm" (họp 04/10), nhóm học máy truyền thống cần một mô hình lai truyền thống để đối chiếu với mô
hình lai học sâu của đề tài. Kế hoạch đăng ký bổ sung: `audit/PREREG_bosung.md` (13/10/2026); mã:
`src/baselines/hybrid.py`, `scripts/6_bosung.py`; báo cáo mục 4.2 (Bảng 4.3), 4.3.4 (Bảng 4.8), 4.4.2 (Bảng 4.16),
Thuật toán 3.6.

- **Theo chương 3 luận án của cô:** ba mô hình đơn lẻ truyền thống — lọc nội dung, lọc cộng tác theo người dùng, theo
  sản phẩm — dự đoán riêng, rồi kết hợp điểm bằng bỏ phiếu (max, min, trung bình) hoặc tổng có trọng số học bởi mạng
  truyền thẳng f(x) = Σ wᵢxᵢ.
- **Trong đề tài:** thành phần là Content, UserKNN, ItemKNN với đúng cấu hình đã chọn (không tinh chỉnh lại); điểm từng
  thành phần chuẩn hoá min–max trên tập ứng viên của khách (như LateFusion-F).
- **Học trọng số theo cặp:** phản hồi ẩn không có điểm đánh giá, nên với mỗi sản phẩm đúng p của một khách, rút 50 sản
  phẩm không đúng j trong tập ứng viên của khách đó; hồi quy logistic không hệ số chặn trên hiệu x_p − x_j — tức tiêu
  chí BPR với hàm điểm tuyến tính. Hồi quy logistic thường (từng cặp khách–sản phẩm độc lập) đã thử và bỏ: gộp mọi
  khách vào một hồi quy cho trọng số âm và NDCG@10 ≈ 0,0005 trên tập xác thực.
- **Chọn trên tập xác thực của mẫu phát triển** (4 cách; NDCG@10 của cách trọng số tính bằng khớp chéo hai phần theo
  khách; mọi dòng tính trên máy của nhóm, chỉ CPU):

  | Mô hình | NDCG@10 xác thực |
  |---|---|
  | Content đứng riêng | 0,00435 (lần tinh chỉnh đã đăng ký: 0,00459 — tệp đặc trưng văn bản dựng lại trên máy khác) |
  | UserKNN đứng riêng | 0,02753 |
  | ItemKNN đứng riêng | 0,02599 |
  | Bỏ phiếu: trung bình | 0,02634 |
  | Bỏ phiếu: max | 0,01483 |
  | Bỏ phiếu: min | 0,02143 |
  | **Trọng số học theo cặp (được chọn)** | **0,02815** |

  Trọng số (chia cho tổng): Content 0,12; UserKNN 0,60; ItemKNN 0,28. Trung bình kém UserKNN đứng riêng vì Content rất
  yếu mà nhận trọng số ngang hai thành phần kia.
- **Đánh giá:** chấm một lần trên tập kiểm thử của mẫu kiểm định H&M và một lần trên Amazon (dùng nguyên cách kết hợp và
  trọng số chọn trên H&M); mô hình tất định nên một lần chấm dùng cho cả 5 seed. Nhật ký `bosung_hybrid_hm`,
  `bosung_hybrid_amazon`. Ba thành phần được chấm lại cùng lúc và so hạng của từng khách với lần đánh giá cuối.
- **Kiểm định họ bổ sung** (Holm riêng, cùng tiêu chí "tốt hơn"): B1 NeuMF-F vs Hybrid-CBCF; B2 Hybrid-CBCF vs
  UserKNN. Họ 10 so sánh đăng ký trước giữ nguyên.
- **Kết quả trên tập kiểm thử:** mục 3.7 (H&M) và 4.6 (Amazon). Lệch kế hoạch: không có (`PREREG_bosung.md` mục 8).

---

## 9. Đánh giá, kiểm định và chống thiên lệch

### 9.1 Full Ranking và độ đo

- Chấm toàn bộ tập ứng viên của từng khách (khoảng 6,7–6,8 nghìn sản phẩm trên H&M). Hoà điểm phá bằng khoá giả ngẫu
  nhiên tất định (seed 2026). Trung bình theo khách.
- **Độ đo chính: NDCG@10** trên tập kiểm thử của mẫu kiểm định. Độ đo phụ: Recall@10, HR@10, Precision@10, NDCG@5,
  NDCG@20.
- **Bảng theo K = 10, 15, 20** (bỏ K = 5 ngày 24/10/2026; số @5 vẫn lưu trong `by_k.csv`) cho cả bốn độ đo, trên cả hai bộ dữ liệu: tính lại từ hạng của từng sản phẩm đúng đã
  lưu ở lần đánh giá cuối (`by_k.csv`), không chấm lại tập kiểm thử. K = 15 thêm theo góp ý của cô (họp 04/10/2026),
  không có trong kế hoạch đăng ký trước: chỉ mô tả, không kiểm định.
- **Mô tả thêm** (seed 42): độ phủ danh mục của top-10, số epoch chọn, thời gian huấn luyện.

Với $T_u$ là tập sản phẩm đúng của khách u, $\text{hits}_u$ là số sản phẩm đúng trong top-K, $r$ là hạng (tính từ 1):

| Độ đo | Công thức (trung bình theo khách) |
|---|---|
| HR@K | $\mathbb{1}[\text{hits}_u \ge 1]$ |
| Precision@K | $\text{hits}_u / K$ |
| Recall@K | $\text{hits}_u / \lvert T_u \rvert$ |
| NDCG@K | $\dfrac{\sum_{i \in T_u,\, r_i \le K} 1/\log_2(r_i + 1)}{\sum_{j=1}^{\min(\lvert T_u \rvert, K)} 1/\log_2(j + 1)}$ |

Công thức cài ở `src/evaluation/metrics.py`, có unit test tính tay.

### 9.2 Tinh chỉnh và đánh giá cuối

- **Tinh chỉnh** (`scripts/4_tune.py`): chỉ trên tập xác thực của mẫu phát triển, seed 42. Mỗi mô hình có học thử 6
  cấu hình (cấu hình mặc định + 5 cấu hình rút ngẫu nhiên cố định từ lưới) — cùng ngân sách cho mọi mô hình; mô hình một
  tham số thử đủ lưới. Lưới: `PREREG_v2.md` mục 4. Đã chạy 09/10 23:17 → 10/10 03:58 (76 cấu hình, 4,7 giờ).
- **Đánh giá cuối** (`scripts/5_final.py`): giữ nguyên cấu hình tốt nhất của mẫu phát triển; 5 seed (42, 2024, 2025,
  2026, 3407).
  - Mạng nơ-ron chọn số epoch trên tập xác thực của mẫu kiểm định, rồi huấn luyện lại từ đầu trên mọi cặp trước
    29/07/2020.
  - BPR-MF và các baseline không học khớp trên mọi cặp trước 29/07/2020.
  - LateFusion-F trộn đúng GMF-F và MLP-F của cùng seed.
  - Amazon Beauty làm y như vậy với các mốc ở mục 7.6.

### 9.3 Kiểm định

- Với mỗi khách, lấy NDCG@10 trung bình qua 5 seed. So sánh từng cặp mô hình bằng **Wilcoxon signed-rank** ghép cặp theo
  khách và **khoảng tin cậy bootstrap 95%** của hiệu trung bình (10.000 lần, seed 0).
- **Họ 10 so sánh** cố định (mục 6.2), hiệu chỉnh **Holm** trên cả họ, α = 0,05.
- Chỉ viết "A tốt hơn B" khi **đồng thời**: p sau Holm < 0,05, khoảng tin cậy không chứa 0, chênh lệch tương đối NDCG@10
  ≥ 5%. Ngược lại ghi "không khác biệt có ý nghĩa".
- Ablation: báo cáo trung bình và khoảng tin cậy, không kiểm định, không dùng để kết luận chính.
- **Họ bổ sung** (`PREREG_bosung.md` mục 4, sau đánh giá cuối): B1 NeuMF-F vs Hybrid-CBCF, B2 Hybrid-CBCF vs UserKNN —
  cùng Wilcoxon, bootstrap và tiêu chí "tốt hơn", hiệu chỉnh Holm riêng trong họ; không đổi họ 10 so sánh.

### 9.4 Quy trình chống thiên lệch

1. **Đăng ký trước:** mô hình, lưới, seed, độ đo, họ so sánh, tiêu chí nằm trong `PREREG_v2.md`, commit trước đánh giá
   cuối. Lệch kế hoạch ghi ở mục 10 của file đó và trong báo cáo. Amazon có kế hoạch riêng (`PREREG_amazon.md`), cũng
   commit trước khi mở tập kiểm thử.
2. **Tách vai trò dữ liệu:** mọi quyết định dựa trên mẫu phát triển; kết luận chỉ dựa trên tập kiểm thử của mẫu kiểm
   định — khách chưa từng được dùng cho quyết định nào.
3. **Khoá kiểm thử:** `5_final.py` từ chối chạy khi kế hoạch chưa commit, có file đã theo dõi bị sửa mà chưa commit,
   hoặc mã băm mã nguồn khác lúc tinh chỉnh. Mỗi lần mở tập kiểm thử ghi một dòng `audit/test_access_log.csv` trước khi
   chấm.
4. **Không dùng thông tin tương lai:** k-core trước mốc kiểm thử, đặc trưng theo thời điểm, mẫu âm trong sản phẩm đã ra
   mắt — có test tự động (`tests/test_v2.py`).
5. **So sánh công bằng:** cùng file dữ liệu đã lọc (kiểm MD5), cùng tập ứng viên, cùng quy tắc loại món đã mua, cùng ngân
   sách tinh chỉnh (theo khuyến nghị của Rendle et al., 2020 và Ferrari Dacrema et al., 2019).
6. **Không gõ tay số:** số trong báo cáo sinh tự động từ file kết quả qua macro; chưa có thì hiện "[chưa có]". Bảng theo K
   tính từ hạng đã lưu, không mở lại tập kiểm thử.
7. **Bài báo chỉ là cơ sở phương pháp:** không so số của đề tài với số công bố (khác dữ liệu, cách chia, giao thức), không
   đặt cạnh kết quả cuộc thi Kaggle (MAP@12, độ đo và giao thức khác). Ngoại lệ duy nhất: Bảng 2.1 (báo cáo mục 2.6)
   ghi thiết lập và số công bố của ba nghiên cứu nền tảng theo yêu cầu của cô, kèm chênh lệch tương đối của đề tài và ghi
   rõ các số này không so trực tiếp được với nhau.

---

## 10. Code, demo, kiểm thử và báo cáo

### 10.1 Quy trình thực nghiệm

Lệnh chạy chi tiết: `neumf_project/README.md` mục 3.

| Bước | Nội dung | File |
|---|---|---|
| Đăng ký trước | Mô hình, lưới tinh chỉnh, 5 seed, độ đo chính NDCG@10, **họ 10 so sánh** (Wilcoxon + bootstrap + Holm), tiêu chí "tốt hơn", hạn chế đã biết; mục 10 của mỗi kế hoạch ghi lệch kế hoạch | `audit/PREREG_v2.md`, `audit/PREREG_amazon.md` |
| Chuẩn bị dữ liệu | Lấy mẫu, đặc trưng, gộp mẫu, k-core, file dữ liệu đã lọc + MD5 | `scripts/1_sample.py`, `3_features.py`, `2_prepare.py` |
| Tinh chỉnh | Chỉ trên tập xác thực của mẫu phát triển; nhật ký mỗi cấu hình kèm **mã băm nội dung mã nguồn** và `data_md5` | `scripts/4_tune.py` |
| Đánh giá cuối | Khoá kiểm thử (mục 9.4); mỗi seed ghi nhật ký trước khi chấm và lưu hạng của từng sản phẩm đúng | `scripts/5_final.py` |
| Kiểm định, xuất báo cáo | Bảng, hình, macro LaTeX, `ket_qua.txt` tự sinh. Bảng theo K tính lại từ hạng đã lưu (`by_k.csv`; số @5/@10/@20 phải trùng số đã lưu, lệch thì dừng). Amazon ghi bảng vào `content/tables/amazon/`, macro `\ARes`, `\ASig`, ... | `scripts/7_report.py` |
| Đối chiếu báo cáo | 72 câu nhận xét bằng chữ của báo cáo (H&M, Amazon, theo K và Hybrid-CBCF) được kiểm trên file kết quả; báo macro, bảng, hình còn thiếu và số chép tay đã cũ trong tài liệu md | `scripts/8_check_report.py` |
| Bổ sung: mô hình lai truyền thống | `tune`: 4 cách kết hợp trên tập xác thực của mẫu phát triển; `final`: chấm một lần tập kiểm thử (khoá kiểm thử riêng, run_tag `bosung_hybrid_*`), chấm lại ba thành phần để đối chiếu. `7_report.py` thêm Hybrid-CBCF (dấu *) vào bảng theo ba nhóm và kiểm định họ B1–B2 | `scripts/6_bosung.py`, `audit/PREREG_bosung.md` |
| Lệnh tắt | `sample-hm`, `v2-data`, `prepare`, `all`, `v2-tune`, `v2-dry-run`, `v2-final`, `v2-report`, `check-report`, `demo`, `amazon-data`, `amazon-dry-run`, `amazon-final`, `amazon-report`, `bosung-tune`, `bosung-dry-run`, `bosung-final`, `amazon-bosung-final` | `run.py` |

### 10.2 Demo (`demo/README.md`)

- Hai bộ dữ liệu (H&M, Amazon Beauty), chỉ nạp checkpoint seed 42 của đánh giá cuối, không huấn luyện lại.
- Sản phẩm H&M theo mẫu thiết kế (tên và ảnh của màu đầu tiên, kèm số màu). Mặc định so NeuMF-F với NeuMF cạnh nhau,
  kèm hạng của từng sản phẩm đích. Thẻ 10 khách tương đồng (UserKNN). Dashboard đọc `outputs/*/final/*.csv`, bảng theo K
  đọc `by_k.csv`.
- **Luôn có gợi ý (13/10/2026):**
  - Khách chưa có trong dữ liệu đã học nhận 10 sản phẩm phổ biến nhất (Most Popular), nhãn "Gợi ý phổ biến", thay cho
    lỗi 404.
  - Khách có lịch sử nhưng không có sản phẩm đích vẫn nhận gợi ý của mô hình, chỉ không có chỉ số.
  - Bảng chọn khách có nút "Xem gợi ý cho mã …" cho mã bất kỳ.
- Chọn được K = 10, 15, 20 (giữ trong URL).
- **Mô hình lai truyền thống (13/10/2026):** Hybrid-CBCF có trong danh sách mô hình đối chứng của demo (ví dụ NeuMF-F
  cạnh Hybrid-CBCF) khi đã có kết quả chấm bổ sung (`outputs/*/final/bosung/results.json`, đã có cho cả hai bộ); nếu
  thiếu, demo ẩn nó kèm lệnh cần chạy, để không chấm tập kiểm thử ngoài kế hoạch. Dashboard đọc bảng `bosung/` (14 mô
  hình + Hybrid-CBCF, dấu *) và có thẻ kiểm định họ bổ sung B1–B2.
- Ảnh trong báo cáo: Hình 3.7 (cửa hàng, so sánh NeuMF-F và NeuMF), Hình 3.8 (thẻ sản phẩm và khách có gu giống), Hình 3.9 (khách mới), Hình 3.10 (màn hình kết quả); Bảng 3.7 số đo demo.

### 10.3 Kiểm thử

- `tests/` (108 test; 6 test của `test_bosung.py` cho mô hình lai truyền thống và khoá kiểm thử bổ sung): đặc trưng
  không dùng dữ liệu tương lai, mẫu âm hợp lệ; k-core chỉ dùng dữ liệu trước mốc kiểm thử;
  gộp theo `product_code`; file dữ liệu tất định và kiểm MD5; NeuMF-F cho cùng điểm lúc huấn luyện và lúc đánh giá; khoá
  kiểm thử, tiêu chí kết luận, họ so sánh; bảng theo K tính lại từ hạng đã lưu; dữ liệu Amazon; câu chữ báo cáo khớp số
  liệu.
- `demo/tests/` (20 test):
  - Test không cần dữ liệu: bảng sản phẩm H&M và Amazon, danh sách khách và bộ lọc, từ chối kết quả của dữ liệu khác,
    thiếu kết quả thì hiện lệnh cần chạy.
  - Test nạp checkpoint: khớp số theo từng khách với file kết quả, khách mới nhận danh sách phổ biến, khách không có
    sản phẩm đích nhận gợi ý của mô hình, lịch sử, late fusion, láng giềng, sản phẩm tương tự, hạng tốt nhất, dashboard,
    khách ví dụ, trang Kết quả khớp macro của báo cáo (H&M và Amazon), câu trả lời ba câu hỏi theo kiểm định.
- **Kết quả ngày 14/10/2026** (máy chỉ có CPU): `tests/` 108/108 qua; `demo/tests` 14/14 qua.
- **Kết quả ngày 06/11/2026** (máy GPU đã chạy đánh giá cuối): `tests/` 108/108 qua; `demo/tests` 20/20 qua. Trên máy
  này 14 mô hình đăng ký trước trùng hạng đã lưu ở mọi khách (riêng NeuMF-F trên Amazon lệch 1/2.644 khách);
  Hybrid-CBCF, chấm ngày 13/10 trên máy CPU với tệp `catalog` MD5 `496f3566…`, trùng 1.146/3.165 khách H&M và
  1.617/2.644 khách Amazon. Demo hiện số đã lưu kèm lý do cho các khách lệch.
- **Kết quả ngày 12/11/2026** (máy chỉ có CPU): `tests/` 110/110 qua; `demo/tests` 21/21 qua; `check-report` khớp.
- **Chẩn đoán test demo hỏng trước đây (14/10):** nguyên nhân **không phải** CPU/GPU. So hạng demo tính lại với hạng
  đã lưu trên 300 khách H&M và 200 khách Amazon: mọi mô hình không dùng vector văn bản (NeuMF, GMF, MLP, BPR-MF,
  UserKNN, ItemKNN, MostPopular, MostPopular-Recent) và Hybrid-CBCF trùng tuyệt đối. Bốn mô hình có đặc trưng lệch
  NDCG@10 ở 11–14% số khách H&M (3–5% Amazon); Content lệch 1%. Lý do: `catalog_v2.npz` (vector văn bản TF-IDF + SVD)
  trên máy này khác máy GPU; dựng lại trên máy này cho đúng từng byte tệp cũ (MD5 `496f3566…`), nên khác biệt đến từ
  phiên bản thư viện giữa hai máy. Đánh giá cuối không ghi MD5 tệp đặc trưng, nên không xác minh được tệp của máy GPU.
- **Cách sửa:** demo đối chiếu từng kết quả với hạng đã lưu (`saved_final_ranks`, `inference.final_result`) và hiện số
  đã lưu kèm lý do khi lệch. Test đòi trùng tuyệt đối với mô hình không dùng vector văn bản; với mô hình dùng vector
  văn bản, hoặc trùng, hoặc demo phải báo lệch và trả đúng số đã lưu. Báo cáo không nêu chi tiết này vì đó là tình trạng mã nguồn, không phải nội dung nghiên cứu; xem
  `neumf_project/README.md` mục 4.

### 10.4 Báo cáo LaTeX (`Report DACNTT/`)

Số mục, bảng, hình và thuật toán trong bảng này là số của báo cáo.

| Phần | Nội dung hiện tại |
|---|---|
| Chương 1 | Mục tiêu và phạm vi có thêm kiểm chứng Amazon và cách xử lý khách mới; bố cục theo các mục mới |
| Chương 2 | Hình 2.1 (NeuMF) vẽ lại với kích thước ma trận; mục 2.6 và Bảng 2.1 ba nghiên cứu nền tảng (hàng của đề tài có kết quả NDCG@10, 06/11); đoạn cold start cập nhật |
| Chương 3 | Hình 3.1 đường ống, Hình 3.2 xử lý dữ liệu, Hình 3.3 chia theo thời gian, Hình 3.4 NeuMF-F, Hình 3.5 quy trình đánh giá; Thuật toán 3.1–3.7 (3.6: chọn cách kết hợp của mô hình lai truyền thống); mục 3.7 nguyên tắc đánh giá; mục 3.8 suy luận Top-K và khách mới; mục 3.9 demo (Hình 3.6 kiến trúc, Hình 3.7–3.10 ảnh demo) |
| Chương 4 | 4.1 thiết lập thực nghiệm (Bảng 4.1 điều kiện chung); 4.2 tinh chỉnh (Bảng 4.2–4.3); 4.3 đánh giá cuối H&M (Bảng 4.4–4.10, Hình 4.1–4.4; theo K: Bảng 4.5–4.6; Hybrid-CBCF: mục 4.3.4, Bảng 4.8); 4.4 kiểm chứng Amazon (Bảng 4.11–4.19); 4.5 nguồn gốc của phần cải thiện (Bảng 4.20, bảy yếu tố đã loại trừ); 4.6 phạm vi của kết luận; 4.7 thảo luận và trả lời ba câu hỏi nghiên cứu. Mọi số qua macro tự sinh |
| Chương 5, tóm tắt Việt/Anh | Chương 5: kết quả đạt được (Bảng 5.1), kết luận (LateFusion-F có NDCG@10 trung bình cao nhất trên cả hai bộ), hạn chế và hướng phát triển. Tóm tắt Việt, Anh có đoạn kết quả, mỗi bản một trang. Không có phụ lục: kế hoạch đăng ký trước, nhật ký mở tập kiểm thử và mã nguồn được trích như tài liệu tham khảo; hướng dẫn chạy mã nguồn ở README |
| Kiểm tra | `python run.py check-report`: 75/75 câu nhận xét khớp số liệu; không còn số chép tay cũ trong tài liệu md; đủ mọi macro, bảng, hình |
| Biên dịch | `main.pdf` 98 trang (12/11) (XeLaTeX + Biber, `compile.bat`); 7 thuật toán; không lỗi, không tham chiếu treo |
| Chương 2, 4 (bổ sung 13/10) | C2 mục 2.1.1: mô hình lai truyền thống (phân loại của Burke, chương 3 luận án của cô); C4 mục 4.2: bảng ba nhóm mô hình đối chứng + mô tả Hybrid-CBCF, sửa mô tả Content (ba thuộc tính, không phải bốn); 4.3: bảng các cách kết hợp; 4.4: mục "Phân tích bổ sung"; 4.5, 4.8, Chương 5: câu về Hybrid-CBCF bằng macro |
| Văn phong (sửa 13–14/10) | Viết lại Chương 1–5, tóm tắt và phụ lục: không in đậm trong thân bài; câu ngắn, bỏ gạch ngang chèn ý; thuật ngữ tiếng Việt thống nhất (mô hình đối chứng, vector nhúng, hợp nhất sớm/muộn, xếp hạng toàn bộ, phân tích bóc tách); mỗi nguồn trích ở chỗ dùng, không trích trong tóm tắt và Chương 4–5; bảng kiểu booktabs; chú thích bảng, hình ngắn, chi tiết chuyển xuống ghi chú hoặc thân bài; Phụ lục A còn 36 nguồn, đúng các nguồn được trích trong thân bài. Ngày 14/10: tách các câu dài; tóm tắt bỏ số liệu; bỏ khỏi báo cáo mọi chi tiết tình trạng mã nguồn (MD5, mã băm, nhật ký, commit, bộ kiểm thử tự động, tệp đặc trưng); gộp các ý lặp giữa các chương; bỏ đoạn liệt kê số rời rạc ở Chương 4 (số đã có trong bảng); viết lại Chương 5; bỏ Phụ lục B |
| Chờ cô | Xác nhận cách xếp ba nhóm và mô hình lai truyền thống; ý kiến về các câu hỏi còn lại (mục 2.3 của file này) |

### 10.5 Lưu ý khi làm tiếp

- **Không chạy lại** `5_final.py` cho H&M hay Amazon: mọi seed đã có dòng nhật ký. Số mới (K khác, bảng mới) phải tính
  từ file đã lưu trong `outputs/`, không mở lại tập kiểm thử.
- Mã nguồn đã đổi sau lần chạy H&M (dọn mã, rồi mở rộng cho Amazon), nên mã băm hiện tại khác `0f1ea1eec5a86c31`. Kết quả
  H&M gắn với commit `e4e4f25`, kết quả Amazon gắn với commit `f866337`. Chạy lại H&M sẽ cần `--allow-code-change` và phải
  ghi lệch kế hoạch.
- Các sửa đổi ngày 13/10 không đụng mã huấn luyện và đánh giá (`src/`, `common.py`, `4_tune.py`,
  `2_prepare.py`, cấu hình), nên mã băm mã nguồn không đổi.
- Nhật ký `audit/test_access_log.csv`:
  - 6 dòng H&M ngày 10/10: dòng 08:56 của lần chạy bị dừng ("Đánh giá cuối bản cuối theo PREREG_v2 (406b62c)") và 5 dòng
    của lần chạy hoàn tất ("Đánh giá cuối theo PREREG_v2; seed 42 chạy lại theo mục 10"), trong đó seed 42 mang nhãn
    `_rerun`;
  - 5 dòng Amazon (`amazon_kiemdinh_seed<N>`), từ 23:11 ngày 10/10 đến 01:37 ngày 11/10.
- Không đặt số của giai đoạn phát triển ban đầu hay số khối 1 cạnh số của bản cuối. Không gộp số của H&M và Amazon; chỉ
  đặt cạnh **kết luận** (Bảng 4.18).
- Kết quả chỉ chép tay ở hai nơi: file này và `van_dap.md`. Khi số đổi, `check-report` liệt kê các dòng còn ghi số cũ.
- **Mô hình lai truyền thống:** đã chấm xong cả hai bộ (nhật ký `bosung_hybrid_hm`, `bosung_hybrid_amazon`); không chạy
  lại `bosung-final` (khoá kiểm thử từ chối khi đã có dòng nhật ký). Kết quả gắn với commit `fcf33f3`, mã băm mã nguồn
  `6a0c777afa432125`.
- Tệp đặc trưng `data/processed/hm/catalog_v2.npz` (Amazon: `data/processed/amazon/catalog.npz`) không nằm trong git;
  mỗi máy tự dựng bằng TF-IDF + SVD, và phiên bản thư viện khác cho vector văn bản khác. Đây là nguyên nhân Content lệch
  ở lần chấm bổ sung (`PREREG_bosung.md` mục 3) và bốn mô hình có đặc trưng lệch trên demo của máy CPU (mục 10.3). Máy
  GPU có đúng tệp của đánh giá cuối; muốn khớp tuyệt đối trên máy khác, chép tệp từ máy GPU vào `data/processed/`.
  Hybrid-CBCF thì ngược lại, chỉ khớp tuyệt đối với tệp của máy CPU (mục 2.3).

---

## 11. Hạn chế đã biết

| Hạn chế | Ghi chú |
|---|---|
| Quy mô dữ liệu | Hai mẫu H&M, mỗi mẫu khoảng 1,6% khách của H&M |
| k-core = 10 | Chọn vì giới hạn RAM; dữ liệu thiên về khách mua nhiều |
| Phạm vi sản phẩm | Sản phẩm chưa có người mua trước mốc (gồm sản phẩm vừa ra mắt) không thuộc tập ứng viên — kết quả không nói về khả năng gợi ý sản phẩm mới. Gợi ý ở mức mẫu thiết kế, không ở mức màu |
| Khách mới | Chỉ xử lý ở mức hệ thống (demo gợi ý Most Popular); không đo chất lượng gợi ý cho khách chưa có lịch sử |
| Thuộc tính khách | `customers.csv` không có mốc thời gian — coi là ít thay đổi |
| k-core ở giai đoạn xác thực | Lọc dùng mọi cặp trước mốc kiểm thử, nên tập khách và sản phẩm ở giai đoạn xác thực phụ thuộc một phần dữ liệu tháng 7/2020. Chỉ ảnh hưởng việc chọn cấu hình trên mẫu phát triển, không ảnh hưởng tập kiểm thử của mẫu kiểm định |
| Một mẫu kiểm định | Khoảng 3 nghìn khách có sản phẩm đúng; một khung thời gian (07–09/2020) |
| Ngân sách tinh chỉnh | 6 cấu hình mỗi mô hình có học; BPR-MF và ItemKNN chọn ở biên lưới |
| Phạm vi đặc trưng | Chưa dùng ảnh, giá (H&M), chuỗi hành vi; văn bản chỉ TF-IDF + SVD |
| Ablation | Một seed, chỉ mô tả; 4 biến thể (biến thể "bỏ ID ngẫu nhiên" trùng NeuMF-F vì ρ = 0) |
| K = 15 | Không có trong kế hoạch đăng ký trước; tính lại từ hạng đã lưu, chỉ mô tả |
| Amazon — cấu hình | Không tinh chỉnh cho Amazon: cấu hình chọn trên H&M có thể bất lợi cho một số mô hình (rõ nhất BPR-MF); mô hình kém đi thì không tách được do mô hình hay do cấu hình |
| Amazon — dữ liệu | Một bộ, chia theo thời gian, không có mẫu khách độc lập; đánh giá không đồng nghĩa với mua; không có thuộc tính khách; bộ 5-core thiên về khách và sản phẩm hoạt động nhiều; nhóm giá là giá lúc thu thập metadata, không phải giá tại ngày đánh giá (`PREREG_amazon.md` mục 9) |
| Tái lập trên máy khác | Mô hình không dùng vector văn bản cho đúng hạng đã lưu cả trên máy chỉ có CPU. Vector văn bản phụ thuộc phiên bản thư viện và tệp đặc trưng không lưu kèm checkpoint, nên bốn mô hình có đặc trưng và Content chỉ khớp khi dùng đúng tệp của máy đã chạy (mục 10.3) |
| Mô hình lai truyền thống | Thêm sau khi đã xem kết quả kiểm thử của 14 mô hình (kể cả ba thành phần của nó); chỉ là phân tích bổ sung, họ kiểm định riêng; trọng số học trên H&M dùng nguyên cho Amazon; Content trên máy chạy bổ sung lệch nhẹ do tệp đặc trưng văn bản dựng lại |

---

## 12. Đối chiếu 17 góp ý trước của GVHD

Đây là 17 góp ý có từ trước buổi họp 04/10 (cách trả lời trước hội đồng ở `van_dap.md` Phần 5). Mức: **Đạt** = đã làm và có số liệu
hoặc bằng chứng; **Một phần** = làm được một phần, phần còn lại ghi là hạn chế; **Chưa** = chưa làm.

| # | Góp ý | Mức | Bằng chứng | Còn lại |
|---|---|---|---|---|
| 1 | Kết quả cao bất thường, rò rỉ | **Đạt** | Chia theo thời gian, k-core trước mốc, đặc trưng theo thời điểm, mẫu kiểm định độc lập, khoá kiểm thử; test tự động. NDCG@10 cao nhất trên H&M là 0,0409 — hợp lý với khoảng 6,7 nghìn ứng viên | — |
| 2 | Bộ kiểm thử chuẩn chung | **Đạt** | 14 mô hình cùng một tập kiểm thử của mẫu kiểm định (3.165 khách, 10.285 cặp đúng), cùng ứng viên, cùng 5 seed, cùng file dữ liệu kiểm MD5; Amazon cũng vậy (2.644 khách) | — |
| 3 | Top-K khách và sản phẩm tương đồng | **Đạt** | UserKNN (k = 200) hạng 5/14 — baseline mạnh nhất trên cả hai bộ; ItemKNN hạng 6; demo có thẻ 10 khách tương đồng | — |
| 4 | Lọc cộng tác hoạt động thế nào | **Đạt** | Báo cáo mục 2.1.2, 3.3.1; `van_dap.md` câu 5.2.7 | — |
| 5 | Khởi đầu lạnh | **Một phần** | Khách mới: gợi ý sản phẩm phổ biến (báo cáo mục 3.7, demo). Bản đầu kế hoạch (khối 1) đã thử đưa sản phẩm mới vào đánh giá: NDCG@10 trên nhóm này của mọi mô hình dưới 0,002; bản cuối bỏ sản phẩm chưa có người mua theo góp ý | Không đo chất lượng gợi ý cho khách mới và sản phẩm mới — ghi là hạn chế và hướng phát triển |
| 6 | NDCG và các chỉ số | **Đạt** | NDCG, Recall, HR, Precision ở K = 10, 15, 20 cho cả hai bộ; ví dụ tính tay ở `van_dap.md` câu 5.3.5 | — |
| 7 | Trình bày kết quả | **Đạt** | Bảng, hình, macro tự sinh; `ket_qua.txt`; 75/75 câu nhận xét khớp số liệu; PDF 98 trang | — |
| 8 | Vai trò của MF | **Đạt** | BPR-MF, GMF; nhánh GMF-F là thành phần mạnh nhất của NeuMF-F (GMF-F ngang NeuMF-F trên cả hai bộ) | — |
| 9 | Mô hình lai thực sự | **Đạt** | NeuMF-F = MF + DNN + đặc trưng; hơn NeuMF chỉ dùng ID 43,8% (H&M) và 65,7% (Amazon), có ý nghĩa | — |
| 10 | Transformer, Temporal, BERT | **Một phần** | Dùng mô tả văn bản (TF-IDF + SVD). Ablation: bỏ văn bản −2,7% (H&M), −9,8% (Amazon), khoảng tin cậy chứa 0 ở cả hai | BERT, Transformer là hướng phát triển (cô ghi không bắt buộc) |
| 11 | Yếu tố thời gian | **Đạt** | Chia theo thời gian; đặc trưng thời gian; MostPopular-Recent. Ablation: bỏ thời gian **−42,3%** (H&M), **−31,6%** (Amazon) — thành phần quan trọng nhất ở cả hai bộ | — |
| 12 | Early fusion | **Đạt** | NeuMF-F (và NeuMF) là early fusion theo định nghĩa trong luận án của cô | — |
| 13 | Late fusion | **Đạt** | LateFusion-F; so sánh #4: trên H&M cao hơn NeuMF-F 2,2% nhưng **không khác biệt có ý nghĩa**; trên Amazon **tốt hơn có ý nghĩa** (NeuMF-F thấp hơn 12,5%) | — |
| 14 | Baseline; lai có hơn trước khi lai | **Đạt** | Trên H&M, NeuMF-F hơn NeuMF, MLP-F, BPR-MF, ItemKNN, UserKNN, MostPopular-Recent, Content; ngang GMF-F. Trên Amazon hơn NeuMF và cả năm baseline. Phân tích bổ sung: NeuMF-F hơn mô hình lai truyền thống Hybrid-CBCF trên cả hai bộ (+25,8%, +23,0%) | Baseline đã trình bày theo ba nhóm; chờ cô xác nhận cách xếp |
| 15 | Sơ đồ kiến trúc | **Đạt** | Hình 2.1 (NeuMF) và 3.4 (NeuMF-F) vẽ lại theo góp ý 04/10 và 23/10; Hình 3.1 (đường ống), 3.2 (xử lý dữ liệu), 3.3 (chia theo thời gian), 3.5 (quy trình đánh giá); Hình 2.2 (hai cách hợp nhất), 3.6 (kiến trúc demo); ảnh demo Hình 3.7–3.8; bộ sơ đồ cho slide ở `image/` | — |
| 16 | Mô hình "variational" | **Chưa** | Không đưa vào báo cáo (phạm vi chốt 20/10, báo cáo rút gọn còn 98 trang) | Buổi họp 04/10 không nêu lại. Tập kiểm thử đã mở, nên nếu cô yêu cầu thì chỉ thêm được dưới dạng **thăm dò sau kiểm thử**, ghi lệch kế hoạch, không đưa vào họ 10 so sánh |
| 17 | Lộ trình 10 bước | **Đạt** | Bước 1–10 đều có kết quả, kể cả phần thảo luận Chương 4 | — |

**Tổng: 14/17 Đạt, 2/17 Một phần, 1/17 Chưa.**

---

## 13. Lịch sử phát triển

Không đặt số của các giai đoạn dưới đây cạnh số của bản cuối: khác dữ liệu, khác tập ứng viên và khác sản phẩm đúng.

### 13.1 Giai đoạn phát triển ban đầu — chỉ dùng ID

Trong mã và `audit/PREREG.md` gọi là "v1". Tập kiểm thử của mẫu phát triển được chấm các ngày 27/09 và 29/09/2026.

- **Thiết lập:** mẫu phát triển; mỗi `article_id` là một sản phẩm; một mốc thời gian chung; tập ứng viên không có sản
  phẩm mới.
- **Mô hình:** chỉ dùng ID — GMF, MLP, NeuMF-Scratch, NeuMF-Pretrained (có tiền huấn luyện), BPR-MF, Most Popular,
  Random; phần mở rộng thêm late fusion (GMF + MLP, BPR-MF + MLP), ItemKNN, UserKNN. 3 seed, họ 8 so sánh có hiệu chỉnh
  Holm.
- **Kết quả:** BPR-MF có NDCG@10 cao nhất; không biến thể NeuMF nào tốt hơn BPR-MF có ý nghĩa (0/8 so sánh đạt tiêu
  chí); tiền huấn luyện không cho lợi ích có ý nghĩa.
- **Vì sao bỏ:**
  1. NeuMF chỉ dùng ID không vượt được MF đã tinh chỉnh.
  2. Lọc k-core dùng cả dữ liệu của giai đoạn kiểm thử.
  3. Tập kiểm thử của mẫu phát triển đã bị xem nhiều lần, một số quyết định đưa ra sau khi xem.

### 13.2 Bản đầu của kế hoạch đánh giá (khối 1) và vì sao có bản cuối

Bản đầu (`audit/PREREG_v2_cu.md`, 03/10/2026) dùng cùng mô hình, lưới, độ đo và họ 10 so sánh như bản cuối, nhưng:
mỗi `article_id` (từng màu) là một sản phẩm, tập ứng viên gồm cả sản phẩm mới (chưa từng bán trước mốc), và mẫu kiểm
định là **khối 1**. Tập kiểm thử của khối 1 được mở ngày 04/10/2026.

Kết quả khối 1 (chỉ là lịch sử): NeuMF-F đứng 3/14; LateFusion-F tốt hơn NeuMF-F có ý nghĩa (−16,1%); NDCG@10 trên nhóm
sản phẩm mới của mọi mô hình đều dưới 0,002.

Theo góp ý của cô và quyết định của nhóm ngày 09/10/2026, kế hoạch đổi thành **bản cuối** (`PREREG_v2.md` mục 0):

1. Một sản phẩm = một `product_code` (gộp mọi màu của cùng một mẫu).
2. Bỏ sản phẩm chưa có người mua khỏi tập ứng viên và đáp án.
3. Dữ liệu đã lọc ghi ra file; mọi mô hình đọc cùng file và kiểm MD5.
4. Đánh giá cuối trên **mẫu kiểm định mới — khối 2**.

Vì các thay đổi này được quyết định **sau khi đã xem kết quả khối 1**, khối 1 không còn dùng để kết luận. Mô hình được
tinh chỉnh lại trên mẫu phát triển theo dữ liệu mới, và kế hoạch bản cuối được commit trước khi dựng tập kiểm thử của
khối 2.

### 13.3 Bản cuối so với giai đoạn phát triển ban đầu

| Tiêu chí | Giai đoạn phát triển ban đầu | Bản cuối |
|---|---|---|
| Độ tin cậy số liệu | Tập kiểm thử đã xem nhiều lần; nhiều quyết định sau khi xem | Mẫu kiểm định độc lập (khối 2), mở tập kiểm thử một lần (seed 42 chạy lại một lần, đã ghi lệch kế hoạch), đăng ký trước, khoá bằng mã băm mã nguồn |
| Bài toán | Theo màu (`article_id`) | Theo mẫu thiết kế (`product_code`); ứng viên là sản phẩm đã có người mua trước mốc |
| Rò rỉ | k-core dùng dữ liệu kiểm thử | Hết rò rỉ đã biết (có test tự động) |
| Mô hình lai | NeuMF chỉ dùng ID | NeuMF-F có đặc trưng; tách được 3 câu hỏi: đặc trưng, hợp nhất, sớm hay muộn |
| Đối chứng | 7 mô hình | 14 mô hình |
| Thống kê | 3 seed, 8 so sánh | 5 seed, 10 so sánh đăng ký trước; bốn độ đo ở K = 10, 15, 20 |
| Bộ dữ liệu | H&M | H&M; kiểm chứng trên Amazon Beauty |
| **Kết quả** | Mô hình lai **không hơn** baseline nào (0/8) | Trên H&M, mô hình lai có đặc trưng **hơn 7/9** đối thủ, ngang GMF-F và LateFusion-F. Trên Amazon, lợi ích của đặc trưng vẫn còn nhưng LateFusion-F tốt hơn |

Kết luận giống nhau ở cả hai giai đoạn trên H&M: NeuMF chỉ dùng ID không hơn BPR-MF có ý nghĩa.

### 13.4 Dọn mã (10/10/2026)

- Xoá toàn bộ mã, cấu hình, test, notebook và kết quả của giai đoạn phát triển ban đầu, cùng kết quả khối 1
  (`outputs/v2/final_cu/`). Tất cả vẫn nằm trong lịch sử git (commit `9799f1a`, tag cục bộ `truoc-don-dep`).
- Giữ `audit/PREREG.md` và `audit/PREREG_v2_cu.md` vì `PREREG_v2.md` dẫn tới.
- Bỏ phần tính chỉ số sản phẩm cũ/mới khỏi `evaluate_v2` (không còn sản phẩm mới); chỉ số chính không đổi (đã so với bản
  cũ: trùng từng số).

### 13.5 Đổi tên script (27/11/2026, commit `12abda7`)

Các script trong `scripts/` được đánh số lại theo thứ tự chạy; nội dung không đổi, mọi chỗ gọi đã cập nhật theo tên mới.
`audit/PREREG*.md`, `audit/test_access_log.csv` và các tệp trong `outputs/` vẫn ghi tên cũ vì đó là vết của lúc chạy.

| Tên cũ | Tên mới |
|---|---|
| `00_sample_hm.py` | `1_sample.py` |
| `02_prepare_data.py` | `2_prepare.py` |
| `21_build_features.py` | `3_features.py` |
| `22_tune_v2.py` | `4_tune.py` |
| `23_final_v2.py` | `5_final.py` |
| `25_bosung.py` | `6_bosung.py` |
| `24_report_v2.py` | `7_report.py` |
| `19_check_report.py` | `8_check_report.py` |
| `v2_common.py` | `common.py` |

Mã băm mã nguồn (`code_hash`) có tính cả đường dẫn tệp, nên sau khi đổi tên sẽ khác mã băm ghi lúc tinh chỉnh. Việc này
chỉ ảnh hưởng nếu chạy lại `5_final.py`/`6_bosung.py final` (đã chạy xong, không chạy lại); kết quả đã lưu không đổi.

---

## 14. Danh sách file và tài liệu tham khảo

### 14.1 File

| Nội dung | File | Mục trong báo cáo |
|---|---|---|
| Kế hoạch đăng ký trước | `audit/PREREG_v2.md` (H&M), `audit/PREREG_amazon.md` (Amazon) | 3.6 |
| Tinh chỉnh | `audit/v2/tuning_log.csv`, `audit/v2/best_configs.json` | 4.3 |
| Kết quả H&M | `outputs/v2/final/` (`summary.csv`, `by_k.csv`, `significance.csv`, `ablation.csv`, `beyond.csv`, `data.json`, `items.csv.gz`, `figures/`, `seed*/`, `ket_qua.txt`) | 4.4 |
| Kết quả Amazon | `outputs/amazon/final/` (cùng các file như H&M) | 4.5 |
| Dữ liệu đã lọc | `outputs/data/manifest.json` (MD5 từng mẫu H&M), `outputs/amazon/data/` | 3.2 |
| Nhật ký mở tập kiểm thử | `audit/test_access_log.csv` | — |
| Code | `src/data_pipeline/{features,protocol_v2,feature_dataset}.py`, `src/data_pipeline/adapters/{hm,amazon}.py`, `src/models/hybrid_features.py`, `src/evaluation/v2.py`, `scripts/{1_sample,2_prepare,3_features,4_tune,5_final,6_bosung,7_report,8_check_report,common}.py`, `configs/{v2,amazon}.yaml` | Chương 3 |
| Test | `tests/`, `demo/tests/` | — |
| Báo cáo | `Report DACNTT/` (bảng: `content/tables/v2/`, `content/tables/amazon/`; hình: `media/figures/v2/`, `media/figures/amazon/`, `media/figures/demo/`) | — |
| Bổ sung: mô hình lai truyền thống | `audit/PREREG_bosung.md`, `audit/v2/bosung_tuning_log.csv`, `audit/v2/bosung_best_configs.json`, `src/baselines/hybrid.py`, `scripts/6_bosung.py`, `tests/test_bosung.py`; kết quả (sau khi chấm): `outputs/v2/final/bosung/`, `outputs/amazon/final/bosung/` | 4.2–4.5 |
| Lịch sử | `audit/PREREG.md` (giai đoạn phát triển ban đầu), `audit/PREREG_v2_cu.md` (bản đầu của kế hoạch); mã và kết quả trong lịch sử git (commit `9799f1a`) | 4.6 |

### 14.2 Tài liệu tham khảo chính

- He, X., Liao, L., Zhang, H., Nie, L., Hu, X., & Chua, T.-S. (2017). Neural Collaborative Filtering. *WWW*.
- Rendle, S., Freudenthaler, C., Gantner, Z., & Schmidt-Thieme, L. (2009). BPR: Bayesian Personalized Ranking from
  Implicit Feedback. *UAI*.
- Sarwar, B., Karypis, G., Konstan, J., & Riedl, J. (2001). Item-based Collaborative Filtering Recommendation
  Algorithms. *WWW*.
- Resnick, P., Iacovou, N., Suchak, M., Bergstrom, P., & Riedl, J. (1994). GroupLens: An Open Architecture for
  Collaborative Filtering of Netnews. *CSCW*.
- Volkovs, M., Yu, G., & Poutanen, T. (2017). DropoutNet: Addressing Cold Start in Recommender Systems. *NIPS*.
- Salton, G., & Buckley, C. (1988). Term-weighting Approaches in Automatic Text Retrieval. *Information Processing and
  Management*.
- Deerwester, S., Dumais, S. T., Furnas, G. W., Landauer, T. K., & Harshman, R. (1990). Indexing by Latent Semantic
  Analysis. *JASIS*.
- Hồ Thị Linh (2023). *Multi-Source Integration for Recommendation Systems*. Luận án tiến sĩ, Trường Đại học Tôn Đức
  Thắng.
- Rendle, S., Krichene, W., Zhang, L., & Anderson, J. (2020). Neural Collaborative Filtering vs. Matrix Factorization
  Revisited. *RecSys*.
- Ferrari Dacrema, M., Cremonesi, P., & Jannach, D. (2019). Are We Really Making Much Progress? A Worrying Analysis of
  Recent Neural Recommendation Approaches. *RecSys*.
- Meng, Z., McCreadie, R., Macdonald, C., & Ounis, I. (2020). Exploring Data Splitting Strategies for the Evaluation of
  Recommendation Models. *RecSys*.
- Krichene, W., & Rendle, S. (2020). On Sampled Metrics for Item Recommendation. *KDD*.
- McAuley, J., Targett, C., Shi, Q., & van den Hengel, A. (2015). Image-Based Recommendations on Styles and Substitutes.
  *SIGIR*. (Nguồn dữ liệu Amazon Beauty.)
- Wilcoxon, F. (1945). Individual Comparisons by Ranking Methods. *Biometrics Bulletin*.
- Holm, S. (1979). A Simple Sequentially Rejective Multiple Test Procedure. *Scandinavian Journal of Statistics*.
- Efron, B., & Tibshirani, R. J. (1993). *An Introduction to the Bootstrap*. Chapman & Hall.
- Kaggle — H&M Personalized Fashion Recommendations:
  https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations

---

## 15. Học từ gốc: kiến thức nền của đề tài

Mục này viết cho hai thành viên ôn bảo vệ: mỗi khái niệm đi theo thứ tự **là gì → công thức → ví dụ bằng số của đề tài →
nằm ở đâu trong code**. Các mục 6–9 ở trên ghi thiết kế và số liệu; mục này giải thích *vì sao* và *hoạt động thế nào*.
Đọc lần lượt từ 15.1 đến 15.12; cuối mục có bảng thuật ngữ (15.13) và câu hỏi tự kiểm tra (15.14).

### 15.1 Hệ khuyến nghị và bài toán của đề tài

- **Hệ khuyến nghị** (*recommender system*): từ dữ liệu quá khứ, đoán món mỗi người dùng có khả năng thích hoặc mua, rồi
  đưa ra một danh sách ngắn. Ví dụ: "Gợi ý cho bạn" của Shopee, Netflix.
- **Phản hồi tường minh** (*explicit feedback*): người dùng tự cho điểm (1–5 sao). **Phản hồi ngầm** (*implicit
  feedback*): chỉ biết hành vi (mua, xem, đánh giá). Đề tài dùng phản hồi ngầm: **mua = 1**; **không mua ≠ không thích**
  (có thể chưa thấy món đó). Đây là lý do phải dùng mẫu âm (15.6) và xếp hạng thay vì đoán điểm.
- **Bài toán Top-K**: với mỗi khách, xếp mọi sản phẩm ứng viên theo điểm rồi lấy K món đầu (đề tài: K = 10; thêm 15, 20).
- **Ma trận tương tác**: hàng = khách, cột = sản phẩm, ô = 1 nếu đã mua. Rất **thưa**: mẫu kiểm định sau lọc có 243.696
  cặp trên 7.994 × 6.749 ≈ 54 triệu ô, tức chỉ khoảng **0,45%** ô bằng 1. Mô hình phải đoán 99,5% ô còn lại.
- **Cold start**: khách hoặc sản phẩm mới, chưa có (hoặc có rất ít) lịch sử. Mô hình chỉ dùng ID không biết gì về họ; đặc
  trưng (thuộc tính, mô tả) giúp xử lý. Demo: khách mới nhận danh sách Most Popular.

### 15.2 Các họ phương pháp và mô hình đối chứng tương ứng

| Họ | Ý tưởng | Mô hình trong đề tài |
|---|---|---|
| Phổ biến | Ai cũng gợi ý các món bán chạy nhất | Most Popular, MostPopular-Recent (bán chạy trong 28 ngày gần nhất) |
| Dựa trên nội dung (*content-based*) | Gợi ý món **giống** món khách đã mua (theo thuộc tính, mô tả) | Content |
| Lọc cộng tác theo láng giềng (*neighborhood CF*) | "Người giống bạn đã mua…" / "Món hay được mua cùng…" | UserKNN, ItemKNN |
| Nhân tử hoá ma trận (*MF*) | Học vector ẩn cho khách và sản phẩm, điểm = tích vô hướng | BPR-MF, GMF |
| Mạng nơ-ron (*deep learning*) | Học hàm tương tác phi tuyến | MLP, NeuMF |
| Lai (*hybrid*) | Kết hợp nhiều nguồn | NeuMF-F, GMF-F, MLP-F, LateFusion-F (lai học sâu); Hybrid-CBCF (lai truyền thống) |

**Độ tương đồng cosine** (dùng trong Content, UserKNN, ItemKNN):

$$\cos(\mathbf{a}, \mathbf{b}) = \frac{\mathbf{a}\cdot\mathbf{b}}{\lVert\mathbf{a}\rVert\,\lVert\mathbf{b}\rVert}$$

- ItemKNN: mỗi sản phẩm là một vector 0/1 dài bằng số khách (khách nào đã mua). Hai sản phẩm cùng được nhiều khách mua →
  cosine cao. Ví dụ: áo A được khách {1, 2, 3} mua, áo B được {2, 3, 4} mua → tích vô hướng = 2, độ dài mỗi vector =
  √3 → cos = 2/3 ≈ 0,67.
- **Hệ số co** (*shrink*) h: mẫu số cộng thêm h (`src/baselines/neighborhood.py`, `denom = norms·norms + shrink`) để
  hạ điểm của cặp chỉ có rất ít khách chung (tương đồng "ăn may"). ItemKNN chọn h = 50, UserKNN h = 0.
- **Top-k láng giềng**: mỗi sản phẩm chỉ giữ k láng giềng giống nhất (ItemKNN k = 100). Điểm của món i cho khách u = tổng
  độ tương đồng giữa i và các món u đã mua.
- UserKNN làm y hệt nhưng theo khách (k = 200): điểm = tổng độ tương đồng của các khách giống u đã mua món i. Thẻ
  "Khách có gu giống khách này" trong demo chính là láng giềng UserKNN; "Sản phẩm tương tự" là láng giềng ItemKNN.
- **Content**: hồ sơ khách = trung bình vector nội dung (văn bản + thuộc tính) các món đã mua, món mua gần đây nặng hơn
  (chu kỳ bán rã 30 ngày: món mua cách đây 30 ngày chỉ còn nửa trọng số); điểm = cosine giữa hồ sơ và món ứng viên.

### 15.3 Embedding và nhân tử hoá ma trận (MF)

- **Embedding**: một bảng tra, mỗi ID (khách hoặc sản phẩm) ứng với một vector d số thực **do mô hình tự học**. Ban đầu
  ngẫu nhiên; huấn luyện đẩy vector của khách lại gần vector các món khách mua.

  | ID sản phẩm | Vector (d = 4, ví dụ) |
  |---|---|
  | 0 (quần jean) | [0,8; −0,1; 0,3; 0,0] |
  | 1 (áo thun) | [0,2; 0,9; −0,4; 0,1] |

- **MF**: điểm của khách u với sản phẩm i là tích vô hướng $\hat{y}_{ui} = \mathbf{p}_u^\top \mathbf{q}_i$. Mỗi chiều
  có thể hiểu như một "gu" ẩn (thích đồ thể thao, thích màu tối…); không ai đặt tên, mô hình tự tìm.
- **BPR-MF** (Rendle et al., 2009): thay vì đoán 0/1, học **thứ tự**: món u đã mua (i) phải có điểm cao hơn món u chưa
  mua (j).

  $$L_{\text{BPR}} = -\sum_{(u,i,j)} \ln \sigma(\hat{y}_{ui} - \hat{y}_{uj}) + \lambda \lVert\Theta\rVert^2$$

  σ là hàm sigmoid, λ là hệ số phạt (*regularization*, đề tài chọn 0,001) để vector không phình to. Code:
  `src/baselines/classical.py`.

### 15.4 Mạng nơ-ron cơ bản

- **Lớp tuyến tính** (*linear / fully-connected*): $\mathbf{h} = W\mathbf{x} + \mathbf{b}$, biến vector n chiều thành m
  chiều; W, b học được.
- **Hàm kích hoạt**: ReLU(z) = max(0, z) tạo tính phi tuyến (không có nó, nhiều lớp tuyến tính chồng lên vẫn chỉ là một
  phép tuyến tính). Sigmoid σ(z) = 1/(1 + e^{−z}) ép số bất kỳ về (0, 1), dùng như xác suất "sẽ mua".
- **Logit**: giá trị z trước sigmoid. Đề tài **xếp hạng theo logit**, không theo σ(z): khi z lớn, σ(z) làm tròn thành
  1,0 ở float32 và nhiều món bằng điểm giả (mục 8.1).
- **Tháp MLP**: nhiều lớp tuyến tính + ReLU, mỗi lớp nhỏ dần. Đề tài: 64 → 32 → 16 → 8 (với d = 32).
- **Dropout**: khi huấn luyện, ngẫu nhiên tắt một phần nơ-ron để tránh học thuộc; khi chấm thì bật hết. Cấu hình chọn của
  NeuMF-F: dropout = 0.

### 15.5 NCF: GMF, MLP, NeuMF và bản có đặc trưng NeuMF-F

He et al. (2017) đề xuất khung **NCF** gồm ba mô hình (`src/models/neumf.py`):

| Mô hình | Cách tính tương tác | Ý nghĩa |
|---|---|---|
| **GMF** | $\phi = \mathbf{p}_u \odot \mathbf{q}_i$ (nhân **từng phần tử**), rồi qua một lớp tuyến tính | MF tổng quát: như tích vô hướng nhưng mỗi chiều có trọng số học được |
| **MLP** | Nối $[\mathbf{p}_u ; \mathbf{q}_i]$ rồi qua tháp MLP | Học tương tác phi tuyến |
| **NeuMF** | GMF và MLP chạy song song, nối đầu ra rồi một lớp tuyến tính → logit | Kết hợp tuyến tính + phi tuyến; **hợp nhất sớm** |

Ví dụ ⊙: [1, 2, 3] ⊙ [4, 0, −1] = [4, 0, −3]; tích vô hướng là tổng các phần tử này = 1.

**NeuMF-F** (mô hình đề xuất, `src/models/hybrid_features.py`) giữ nguyên NeuMF nhưng vector khách và sản phẩm không
chỉ là embedding ID mà **cộng thêm đặc trưng đã chiếu**:

$$\mathbf{q}_i = \mathbf{e}^{\text{ID}}_i + W_I\,\mathbf{x}_i, \qquad \mathbf{p}_u = \mathbf{e}^{\text{ID}}_u + W_U\,\mathbf{x}_u$$

- $\mathbf{x}_i$ (sản phẩm) gồm 3 phần nối nhau:

  | Phần | Cách tạo | H&M | Amazon |
  |---|---|---|---|
  | Thuộc tính danh mục | Mỗi thuộc tính một embedding 8 chiều (`cat_dim = 8`), nối lại | 11 × 8 = 88 | 5 × 8 = 40 |
  | Văn bản | TF-IDF → SVD 64 chiều (15.7) | 64 | 64 |
  | Thời gian tại ngày t | Bán trong 7, 28, 91 ngày trước t; tuổi sản phẩm; cờ "chưa từng bán" | 5 | 5 |
  | **Tổng $d_I$** | | **157** | **109** |

- $\mathbf{x}_u$ (khách): H&M = 5 thuộc tính × 8 (nhóm tuổi, hội viên, nhận tin, FN, Active) + 2 đặc trưng thời gian (số
  ngày từ lần mua gần nhất, số cặp đã mua) = **42 chiều**; Amazon không có thông tin khách nên chỉ còn 2.
- $W_I$, $W_U$ là ma trận học được, đưa $\mathbf{x}$ về đúng d chiều (32) để **cộng** được với embedding ID. Mỗi nhánh
  (GMF, MLP) có ma trận riêng.
- **Vì sao cộng chứ không thay ID**: sản phẩm mua nhiều thì embedding ID học tốt; sản phẩm ít người mua thì phần đặc
  trưng gánh phần lớn. **Bỏ ID ngẫu nhiên** (ρ): khi huấn luyện đôi lúc giấu embedding ID để ép mô hình học cả từ đặc
  trưng; cấu hình chọn của NeuMF-F là ρ = 0 (GMF-F chọn 0,25).
- **Tính chất thời điểm**: đặc trưng thời gian luôn tính tại ngày của cặp (khi huấn luyện) hoặc ngày mốc τ (khi chấm), chỉ
  dùng dữ liệu **trước** ngày đó → không lộ tương lai.
- GMF-F, MLP-F = NeuMF-F chỉ giữ một nhánh. LateFusion-F (15.5b) huấn luyện hai nhánh **riêng** rồi trộn điểm.

**15.5b Hợp nhất sớm và muộn.** Hợp nhất sớm (*early fusion*): nối biểu diễn các nhánh rồi một mô hình dự đoán, học
**chung** (NeuMF-F). Hợp nhất muộn (*late fusion*): mỗi nhánh là một mô hình riêng, xong mới trộn **điểm** (LateFusion-F):

$$s = w\cdot\text{minmax}(s_{\text{GMF-F}}) + (1-w)\cdot\text{minmax}(s_{\text{MLP-F}}), \quad w = 0{,}4$$

Chuẩn hoá min–max trên tập ứng viên của từng khách: $s' = (s - \min)/(\max - \min)$, đưa điểm hai mô hình về cùng thang
[0, 1] trước khi cộng. Ví dụ điểm GMF-F của 3 món là [2, 5, 8] → [0; 0,5; 1].

### 15.6 Huấn luyện: hàm mất mát, mẫu âm, epoch, dừng sớm, seed

- **Hàm mất mát BCE** (*binary cross-entropy*, `nn.BCEWithLogitsLoss` trong `src/training/trainer.py`), với z là logit,
  y = 1 (đã mua) hoặc 0 (mẫu âm):

  $$L = -\big[y \ln\sigma(z) + (1-y)\ln(1-\sigma(z))\big]$$

  Ví dụ: món đã mua mà σ(z) = 0,9 → L = −ln 0,9 ≈ 0,105 (phạt nhẹ); nếu σ(z) = 0,1 → L ≈ 2,30 (phạt nặng).
- **Mẫu âm** (*negative sampling*): chỉ có cặp "đã mua", nên mỗi cặp dương rút thêm **8** món khách chưa mua làm y = 0
  (tỉ lệ 1 : 8), chỉ trong các món **đã ra mắt** tại ngày mua đó. Rút lại mới ở mỗi epoch.
  Code: `src/data_pipeline/negative_sampling.py`, `feature_dataset.py`.
- **Batch, epoch**: dữ liệu chia thành gói 512 mẫu (*batch*); mỗi gói → tính L → cập nhật trọng số một lần. Đi hết mọi
  gói = **1 epoch**. Tối đa 20 epoch.
- **Adam**: thuật toán cập nhật trọng số (biến thể của gradient descent, tự điều chỉnh bước cho từng tham số). Tốc độ học
  lr = 0,001; **weight decay** 1e-6 là phạt nhỏ lên độ lớn trọng số.
- **Dừng sớm** (*early stopping*): sau mỗi epoch chấm NDCG@10 trên tập xác thực; 5 epoch liền không tăng (`patience: 5`)
  thì dừng và lấy epoch tốt nhất. Ví dụ NDCG theo epoch 0,020 / 0,026 / 0,031 / 0,033 / 0,032 / 0,032 / 0,031 / 0,030 /
  0,029 → tốt nhất ở epoch 4, dừng ở epoch 9.
- **Seed**: con số khởi đầu cho bộ sinh số ngẫu nhiên (khởi tạo trọng số, mẫu âm, thứ tự batch). Cùng seed → chạy lại ra
  đúng kết quả. Đề tài chạy 5 seed (42, 2024, 2025, 2026, 3407) để biết kết quả có ổn định không; báo "trung bình ±
  độ lệch chuẩn". Mô hình **không có bước ngẫu nhiên** (Most Popular, Content, KNN, Hybrid-CBCF) cho cùng kết quả mọi
  seed → độ lệch chuẩn đúng bằng 0, **không phải thiếu số**.

### 15.7 Biểu diễn văn bản: TF-IDF và SVD

1. **TF-IDF** (`src/data_pipeline/features.py`, `text_vectors`): mỗi mô tả sản phẩm thành một vector, mỗi chiều là một
   từ hoặc cụm 2 từ. Trọng số cao khi từ xuất hiện nhiều trong mô tả này (**TF**) nhưng hiếm trong các mô tả khác
   (**IDF**, xấp xỉ log(N / số mô tả chứa từ)). "the", "and" bị bỏ (từ dừng); "denim" hay "push-up" có trọng số cao.
   Giữ tối đa 30.000 từ, từ phải xuất hiện ở ít nhất 3 sản phẩm.
2. **SVD cắt cụt** (*truncated SVD*, cũng là ý tưởng của LSA — Deerwester et al., 1990): nén vector 30.000 chiều, gần như
   toàn số 0, xuống **64 chiều** giữ phần thông tin lớn nhất; các từ hay đi cùng nhau ("jeans", "denim", "skinny") gộp
   vào cùng hướng.
3. **Chuẩn hoá L2**: chia vector cho độ dài của nó để mọi vector dài bằng 1 (mô tả dài hay ngắn không ảnh hưởng).

Vector văn bản tính **một lần** trên toàn danh mục (không dùng dữ liệu mua) rồi giữ cố định; khác embedding thuộc tính là
thứ học trong lúc huấn luyện.

### 15.8 Dữ liệu: lấy mẫu, lọc k-core, chia theo thời gian

- **Lấy mẫu theo khách** (mục 7.1–7.2): giữ trọn lịch sử 2 năm của khách được chọn, vì Full Ranking trên toàn H&M không
  vừa RAM 16 GB. Hai mẫu không chung khách: mẫu phát triển (để chọn cấu hình) và mẫu kiểm định (để kết luận).
- **Gộp theo mẫu thiết kế** (`product_code`): áo cùng kiểu khác màu là một sản phẩm.
- **Lọc k-core** (`src/data_pipeline/kcore.py`), k = 10 (Amazon 5): bỏ khách mua < 10 món và sản phẩm < 10 khách mua,
  **lặp** đến khi không bỏ thêm được (bỏ sản phẩm có thể làm một khách tụt dưới 10, nên phải lặp). Lý do: món/khách quá
  ít dữ liệu không học được gì và làm phình tập ứng viên. Chỉ lọc trên dữ liệu **trước mốc kiểm thử**.
- **Chia theo thời gian** (mục 7.4): huấn luyện trên mọi thứ trước mốc τ = 29/07/2020; đáp án là món khách **mua lần
  đầu** trong 8 tuần sau τ. Giống thực tế: hôm nay dự đoán tuần sau. Cách **leave-one-out** (giấu món cuối của từng
  khách) bị loại vì để lọt tương lai: 11,2% cặp huấn luyện xảy ra sau món kiểm thử của chính khách đó (Meng et al., 2020).
- **Ba tập**: **huấn luyện** (học trọng số), **xác thực** (01/07–28/07/2020: chọn cấu hình, chọn số epoch),
  **kiểm thử** (29/07–22/09/2020: chỉ để kết luận, mở đúng một lần).
- **Rò rỉ dữ liệu** (*data leakage*): khi mô hình vô tình thấy thông tin của tương lai/đáp án lúc huấn luyện → điểm đẹp
  giả. Đề tài chặn bằng: k-core trước τ, đặc trưng tính trước ngày t, mẫu âm trong món đã ra mắt, có test tự động
  (`tests/test_v2.py`).

### 15.9 Đánh giá: Full Ranking và các độ đo, ví dụ tính tay

- **Full Ranking**: chấm **mọi** sản phẩm ứng viên của khách (~6.700 món) rồi xếp hạng. **Sampled Ranking** chỉ trộn món
  đúng với ~100 món ngẫu nhiên — rẻ hơn nhưng có thể đảo thứ hạng giữa các mô hình (Krichene & Rendle, 2020), nên đề tài
  không dùng để kết luận.
- **Tập ứng viên**: sản phẩm đã có người mua trước τ, trừ món khách đã mua (chỉ gợi ý món **mới với khách**).
- Hoà điểm phá bằng khoá giả ngẫu nhiên cố định; mọi độ đo tính cho từng khách rồi lấy **trung bình theo khách**.

**Ví dụ** — khách KH0261 trong demo và báo cáo (Hình 3.7): sau mốc mua 2 món, NeuMF-F xếp chúng ở hạng **3** và **6**.

| Độ đo | Công thức | Tính | Kết quả |
|---|---|---|---|
| HR@10 | có ít nhất 1 món đúng trong top-10? | có | **1** |
| Precision@10 | số món đúng trong top-10 / 10 | 2 / 10 | **0,2** |
| Recall@10 | số món đúng trong top-10 / tổng số món đúng | 2 / 2 | **1** |
| NDCG@10 | DCG / IDCG (dưới đây) | 0,856 / 1,631 | **≈ 0,525** |

- **DCG** (lợi ích tích luỹ có chiết khấu): món đúng ở hạng r đóng góp 1/log₂(r + 1) — càng xuống thấp càng ít điểm.
  DCG = 1/log₂4 + 1/log₂7 = 0,5 + 0,356 = 0,856.
- **IDCG**: DCG lý tưởng — 2 món đúng nằm ở hạng 1 và 2: 1/log₂2 + 1/log₂3 = 1 + 0,631 = 1,631.
- **NDCG** = DCG / IDCG ∈ [0, 1]; = 1 khi mọi món đúng nằm trên cùng. NDCG thưởng cho việc xếp món đúng **lên cao**, nên
  là độ đo chính. Cùng khách đó, NeuMF xếp món gần nhất ở hạng 164 → ngoài top-10 → NDCG@10 = 0.
- **Vì sao NDCG@10 của đề tài chỉ khoảng 0,04**: trung bình trên 3.165 khách của tập kiểm thử H&M, phần lớn khách không có món đúng nào lọt
  top-10 trong số ~6.700 ứng viên. Random chỉ được 0,001; Most Popular 0,022; NeuMF-F 0,040 — gấp ~40 lần ngẫu nhiên.
- **Độ phủ** (*coverage*@10): số sản phẩm khác nhau xuất hiện trong top-10 của ít nhất một khách / số sản phẩm ứng viên.
  Most Popular chỉ 0,3% (ai cũng nhận cùng một danh sách); mô hình cá nhân hoá phủ rộng hơn.

Code: `src/evaluation/metrics.py` (có test tính tay), `src/evaluation/full_ranking.py`, `src/evaluation/v2.py`.

### 15.10 Tinh chỉnh, đăng ký trước và khoá kiểm thử

- **Siêu tham số** (*hyperparameter*): thứ con người chọn, mô hình không tự học — d, lr, số mẫu âm, dropout, ρ, k của
  KNN… Khác **tham số** (trọng số, embedding) do huấn luyện học ra.
- **Tinh chỉnh** (`scripts/4_tune.py`): mỗi mô hình thử 6 cấu hình (cùng ngân sách cho mọi mô hình để so công bằng),
  chấm trên tập **xác thực** của mẫu phát triển, giữ cấu hình tốt nhất (`audit/v2/best_configs.json`).
- **Vì sao không chọn trên tập kiểm thử**: chọn theo kiểm thử là "học tủ đề thi" — điểm cao vì chọn đúng cấu hình ăn may
  trên đúng tập đó, không phản ánh dữ liệu mới.
- **Đăng ký trước** (*pre-registration*, `audit/PREREG_v2.md`): viết sẵn và commit mô hình, lưới, seed, độ đo, các cặp
  so sánh, tiêu chí "tốt hơn" **trước** khi mở tập kiểm thử. Không thể sửa kế hoạch cho hợp kết quả.
- **Khoá kiểm thử** (`scripts/5_final.py`): từ chối chạy nếu kế hoạch chưa commit hoặc mã nguồn đang sửa dở; mỗi lần mở
  tập kiểm thử ghi một dòng vào `audit/test_access_log.csv` trước khi chấm.
- **Đánh giá cuối**: với mỗi seed, mạng nơ-ron chọn số epoch trên tập xác thực của mẫu kiểm định, rồi **huấn luyện lại từ
  đầu** trên mọi cặp trước τ với đúng số epoch đó, rồi chấm tập kiểm thử.

### 15.11 Thống kê: so sánh hai mô hình có thật sự khác không

- **Chênh lệch tương đối**: (A − B) / B. Ví dụ NeuMF-F (0,04003) so NeuMF (0,02783): (0,04003 − 0,02783) / 0,02783 ≈
  **+43,8%**.
- **Vì sao cần kiểm định**: hai mô hình chênh 2% có thể chỉ do ngẫu nhiên (khách nào được chọn, seed nào). Kiểm định cho
  biết chênh lệch có đáng tin không.
- **Ghép cặp theo khách**: hai mô hình chấm **cùng** khách, nên so từng khách: $d_u$ = NDCG@10 của A − của B (mỗi bên đã
  lấy trung bình 5 seed).
- **Wilcoxon signed-rank** (`scipy.stats.wilcoxon`, `scripts/7_report.py`): bỏ các $d_u$ = 0, xếp hạng |d_u| từ nhỏ đến
  lớn, so tổng hạng của các khách A hơn với tổng hạng của khách B hơn. Không giả định phân phối chuẩn (NDCG của từng khách
  lệch rất mạnh, đa số bằng 0). Kết quả là **p-value**: xác suất thấy chênh lệch lớn như vậy *nếu thật ra hai mô hình
  ngang nhau*. p nhỏ → khó là ngẫu nhiên.
- **Bootstrap 95%**: rút ngẫu nhiên có hoàn lại 10.000 lần một tập khách cùng cỡ, mỗi lần tính trung bình $d_u$; lấy
  phân vị 2,5% và 97,5% làm khoảng tin cậy. Khoảng **không chứa 0** → chênh lệch nhất quán về một phía.
- **So sánh bội và Holm**: làm 10 phép kiểm định, mỗi phép α = 5%, thì khả năng ít nhất một kết luận sai lên tới ~40%.
  **Holm** (`holm()` trong `scripts/7_report.py`) sửa bằng cách: xếp p tăng dần p₍₁₎ ≤ … ≤ p₍₁₀₎, nhân p₍ₖ₎ với
  (10 − k + 1) — nhỏ nhất nhân 10, kế tiếp nhân 9, … — và giữ tính đơn điệu. Ví dụ p nhỏ nhất 0,003 → 0,03 < 0,05 vẫn có
  ý nghĩa; p = 0,02 đứng thứ 3 → × 8 = 0,16 → không còn ý nghĩa.
- **Tiêu chí "tốt hơn"** (`verdict()`): **đồng thời** p sau Holm < 0,05, khoảng bootstrap không chứa 0, và chênh lệch
  tương đối ≥ 5%. Thiếu một điều kiện → "không khác biệt có ý nghĩa" ("ngang nhau" trên demo). Vì vậy NeuMF-F vs GMF-F
  (+2,6%) và vs LateFusion-F (−2,2%) là "ngang nhau" trên H&M.
- **Ablation** (bóc tách): tắt lần lượt một nhóm đặc trưng của NeuMF-F, xem NDCG giảm bao nhiêu → biết nhóm nào quan
  trọng. H&M: bỏ đặc trưng thời gian giảm 42,3% (quan trọng nhất), bỏ thông tin khách giảm 10,3%; bỏ thuộc tính và bỏ
  văn bản giảm ít và khoảng tin cậy chứa 0 → "chưa khẳng định". Chỉ seed 42, chỉ mô tả.

### 15.12 Hệ thống: từ dữ liệu gốc tới báo cáo và demo

```
data/raw (Kaggle, Amazon)
  └─ 1_sample.py ─ lấy mẫu khách ─► data/processed/hm/mau_*.csv
       └─ 3_features.py ─ đặc trưng sản phẩm (TF-IDF, SVD, doanh số) ─► data/processed/*.npz
       └─ 2_prepare.py ─ gộp mẫu, k-core, MD5 ─► outputs/data/*.csv.gz
            └─ 4_tune.py ─ tinh chỉnh trên xác thực ─► audit/v2/best_configs.json
                 └─ 5_final.py (+ 6_bosung.py) ─ 5 seed trên kiểm thử ─► outputs/*/final/ (kết quả + checkpoint)
                      └─ 7_report.py ─ kiểm định, bảng, hình, macro ─► Report DACNTT/content/tables, media/figures
                           └─ 8_check_report.py ─ đối chiếu câu chữ báo cáo với số liệu
```

Mọi bước gọi qua `python run.py <lệnh>` (mục 10.1). Phần dùng chung (nạp dữ liệu, dựng mô hình, huấn luyện, chấm) nằm ở
`scripts/common.py` và `src/`.

**Demo** (`demo/`): backend **FastAPI** (Python) nạp checkpoint seed 42 và kết quả đã lưu, mở các API như
`/api/users/{id}/recommend`, `/neighbors`, `/api/results`; frontend là HTML/CSS/JavaScript thuần gọi các API đó. Khi bấm
một khách: trình duyệt gọi API → backend chấm ~6.700 món bằng mô hình đã huấn luyện (~16 ms trung vị trên H&M) → trả
top-K kèm ảnh, tên. Demo **không huấn luyện**, chỉ suy diễn; số trên trang Kết quả đọc thẳng từ file của `7_report.py`
nên trùng báo cáo.

### 15.13 Bảng thuật ngữ

| Tiếng Việt (báo cáo) | Tiếng Anh | Một câu giải thích |
|---|---|---|
| Phản hồi ngầm | Implicit feedback | Chỉ biết hành vi (mua), không có điểm đánh giá |
| Ma trận tương tác | Interaction matrix | Khách × sản phẩm, ô = 1 nếu đã mua |
| Nhân tử hoá ma trận | Matrix factorization (MF) | Học vector ẩn, điểm = tích vô hướng |
| Lọc cộng tác | Collaborative filtering (CF) | Dựa vào hành vi của người/món giống nhau |
| Lọc dựa trên nội dung | Content-based filtering | Dựa vào thuộc tính, mô tả sản phẩm |
| Vector nhúng | Embedding | Vector học được cho mỗi ID / giá trị thuộc tính |
| Hợp nhất sớm / muộn | Early / late fusion | Gộp biểu diễn rồi dự đoán / dự đoán riêng rồi gộp điểm |
| Mẫu âm | Negative sample | Món chưa mua dùng làm ví dụ y = 0 |
| Hàm mất mát | Loss function | Đo mô hình sai bao nhiêu; huấn luyện = làm nó nhỏ đi |
| Dừng sớm | Early stopping | Dừng khi điểm xác thực không tăng nữa |
| Siêu tham số | Hyperparameter | Thứ người chọn trước khi huấn luyện (d, lr…) |
| Tập xác thực / kiểm thử | Validation / test set | Để chọn cấu hình / để kết luận |
| Rò rỉ dữ liệu | Data leakage | Mô hình lỡ thấy thông tin tương lai |
| Xếp hạng toàn bộ | Full ranking | Chấm mọi ứng viên, không lấy mẫu |
| Khởi đầu lạnh | Cold start | Khách/sản phẩm chưa có lịch sử (báo cáo giữ tiếng Anh) |
| Phân tích bóc tách | Ablation study | Tắt từng thành phần để đo đóng góp |
| Đăng ký trước | Pre-registration | Ghi kế hoạch trước khi xem kết quả |
| Khoảng tin cậy | Confidence interval (CI) | Khoảng chứa giá trị thật với độ tin cậy 95% |
| Hiệu chỉnh Holm | Holm correction | Sửa p-value khi làm nhiều phép kiểm định |
| Độ phủ | Coverage | Tỉ lệ danh mục từng được gợi ý |

### 15.14 Câu hỏi tự kiểm tra

Trả lời được hết mà không nhìn là nắm đề tài. Câu hỏi sát hội đồng hơn: `van_dap.md`.

1. Vì sao không dùng điểm sao mà dùng "đã mua = 1"? Vì sao cần mẫu âm? *(15.1, 15.6)*
2. GMF khác tích vô hướng MF ở đâu? MLP thêm được gì? *(15.3, 15.5)*
3. NeuMF-F khác NeuMF đúng ở công thức nào? Vì sao $d_I$ = 157 trên H&M và 109 trên Amazon? *(15.5)*
4. Hợp nhất sớm và muộn khác nhau thế nào; mô hình nào của đề tài thuộc loại nào? *(15.5b)*
5. Tính NDCG@10 khi món đúng duy nhất nằm ở hạng 1, hạng 10, hạng 11. *(Đáp án: 1; 1/log₂11 ≈ 0,289; 0.)*
6. Vì sao chia theo thời gian mà không leave-one-out? *(15.8)*
7. Vì sao có hai mẫu khách? Chọn cấu hình trên tập kiểm thử thì sai ở đâu? *(15.8, 15.10)*
8. Vì sao NeuMF-F hơn NeuMF 43,8% thì "tốt hơn", còn hơn GMF-F 2,6% thì "ngang nhau"? *(15.11)*
9. "± 0,00000" trong bảng nghĩa là gì? *(15.6)*
10. Nhóm đặc trưng nào quan trọng nhất theo ablation, và vì sao hợp lý với thời trang? *(15.11: đặc trưng thời gian —
    hàng mới và hàng đang bán chạy đổi theo mùa.)*
11. Vì sao mô hình đề xuất không đứng đầu (LateFusion-F cao hơn) mà đề tài vẫn có ý nghĩa? *(mục 5, 3.6)*
12. Demo có huấn luyện lại không? Khách mới nhận gợi ý gì? *(15.12)*
