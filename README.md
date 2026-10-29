# Đồ án CNTT — Mô hình khuyến nghị lai NeuMF-F trên dữ liệu H&M

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu.
**Sinh viên:** Lê Minh Lý (52300220), Sử Thị Yến Linh (52300218). **GVHD:** TS. Hồ Thị Linh.

Mô hình đề xuất **NeuMF-F** giữ hai nhánh của NeuMF — GMF (nhân tử hoá ma trận) và MLP (mạng nơ-ron sâu), hợp nhất
sớm — và bổ sung đặc trưng sản phẩm, khách hàng, thời gian. Cấu hình được tinh chỉnh trên mẫu phát triển; kết luận lấy
trên mẫu kiểm định độc lập, mở tập kiểm thử đúng một lần theo kế hoạch đăng ký trước. Kết luận được kiểm chứng lại trên
bộ dữ liệu thứ hai, Amazon Beauty.

**Trạng thái (29/10/2026):**

- Thực nghiệm đã xong trên H&M (10/10) và kiểm chứng trên Amazon Beauty (10–11/10); tập kiểm thử đã mở đúng một lần,
  không chạy lại. Báo cáo, sơ đồ và demo đã sửa theo góp ý buổi họp 23/10 (hình NeuMF-F chỉ còn mô hình đề xuất, ghi
  Top-K, giải thích ŷ và nhãn; bỏ K = 5; có mục thiết lập thực nghiệm; ảnh demo lưu trên máy).
- Kết quả (NDCG@10): NeuMF-F tốt hơn có ý nghĩa NeuMF chỉ dùng ID (+43,8% trên H&M, +65,7% trên Amazon) và các mô hình
  đối chứng truyền thống trên cả hai bộ dữ liệu, nhưng không hơn nhánh GMF-F đứng riêng. LateFusion-F cao nhất trên cả
  hai bộ: trên H&M chênh với NeuMF-F không có ý nghĩa, trên Amazon tốt hơn NeuMF-F có ý nghĩa. NeuMF-F vẫn là mô hình
  đề xuất vì đã chốt trong kế hoạch đăng ký trước.
- Baseline xếp theo ba nhóm (mô hình đơn lẻ, học máy truyền thống, chuyên biệt cho gợi ý). Nhóm học máy truyền thống
  có thêm mô hình lai truyền thống Hybrid-CBCF (Content + UserKNN + ItemKNN, theo luận án của cô) — phân tích bổ sung
  có kế hoạch đăng ký riêng; NeuMF-F tốt hơn nó có ý nghĩa trên cả hai bộ.
- Còn lại: xác nhận với khoa việc nộp báo cáo giữa kỳ (hạn nghe được khoảng 25/10), chép lại ảnh H&M cho demo
  (`demo/scripts/copy_images.py`), làm slide, nộp báo cáo cuối (tháng 11).

Số liệu, tiến độ chi tiết và đối chiếu góp ý: [`tong_hop.md`](tong_hop.md).

## Thư mục

| Thư mục / file | Nội dung |
|---|---|
| `neumf_project/` | Mã nguồn, dữ liệu, kết quả, demo web |
| `Report DACNTT/` | Báo cáo LaTeX (`main.tex`, biên dịch bằng `compile.bat`) |
| `tai_lieu/` | Tài liệu tham khảo (luận án của GVHD) |
| `tong_hop.md` | Tổng hợp đồ án: phương pháp, kết quả H&M và Amazon, tiến độ, đối chiếu góp ý |
| `van_dap.md` | Chuẩn bị vấn đáp: trả lời góp ý của GVHD và các câu hỏi khó |

## Đọc gì, ở đâu

| Cần | Đọc |
|---|---|
| Tình hình, kết quả, phương pháp | [`tong_hop.md`](tong_hop.md) |
| Cài đặt và chạy | [`neumf_project/README.md`](neumf_project/README.md) |
| Demo web | [`neumf_project/demo/README.md`](neumf_project/demo/README.md) |
| Kế hoạch đăng ký trước (mô hình, độ đo, 10 so sánh) | [`neumf_project/audit/PREREG_v2.md`](neumf_project/audit/PREREG_v2.md) |
| Kế hoạch kiểm chứng trên Amazon Beauty | [`neumf_project/audit/PREREG_amazon.md`](neumf_project/audit/PREREG_amazon.md) |
| Kế hoạch bổ sung: mô hình lai truyền thống | [`neumf_project/audit/PREREG_bosung.md`](neumf_project/audit/PREREG_bosung.md) |
| Chuẩn bị vấn đáp | [`van_dap.md`](van_dap.md) |

Giai đoạn phát triển ban đầu (mô hình chỉ dùng ID; trong mã gọi là "v1") và bản đầu của kế hoạch đánh giá (khối 1) là
**lịch sử phát triển**: xem `tong_hop.md` mục 13 và báo cáo mục 4.6.
