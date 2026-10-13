# Đồ án CNTT — Mô hình khuyến nghị lai NeuMF-F trên dữ liệu H&M

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu.
**Sinh viên:** Lê Minh Lý (52300220), Sử Thị Yến Linh (52300218). **GVHD:** TS. Hồ Thị Linh.

Mô hình đề xuất **NeuMF-F** giữ hai nhánh của NeuMF — GMF (nhân tử hoá ma trận) và MLP (mạng nơ-ron sâu), hợp nhất
sớm — và bổ sung đặc trưng sản phẩm, khách hàng, thời gian. Cấu hình được tinh chỉnh trên mẫu phát triển; kết luận lấy
trên mẫu kiểm định độc lập, mở tập kiểm thử đúng một lần theo kế hoạch đăng ký trước. Kết luận được kiểm chứng lại trên
bộ dữ liệu thứ hai, Amazon Beauty.

**Trạng thái (13/10/2026):**

- Thực nghiệm đã xong trên H&M (10/10) và kiểm chứng trên Amazon Beauty (10–11/10). Báo cáo và demo đã sửa theo góp ý
  buổi họp 04/10.
- Kết quả: NeuMF-F tốt hơn có ý nghĩa mô hình chỉ dùng ID và các baseline trên cả hai bộ dữ liệu, nhưng không hơn nhánh
  GMF-F đứng riêng; trên Amazon, hợp nhất muộn LateFusion-F tốt hơn NeuMF-F.
- Baseline đã xếp theo ba nhóm (mô hình đơn lẻ, học máy truyền thống, chuyên biệt cho gợi ý). Nhóm học máy truyền thống
  có thêm mô hình lai truyền thống Hybrid-CBCF (Content + UserKNN + ItemKNN, theo luận án của cô) — phân tích bổ sung
  có kế hoạch đăng ký riêng; đã chấm tập kiểm thử trên cả hai bộ, NeuMF-F tốt hơn nó có ý nghĩa.
- Còn lại: chờ cô xác nhận cách xếp nhóm và các câu hỏi còn lại, làm slide, gửi cô checkpoint.

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
