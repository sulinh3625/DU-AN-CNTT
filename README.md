# Đồ án CNTT — Mô hình khuyến nghị lai NeuMF-F trên dữ liệu H&M

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu.
**Sinh viên:** Lê Minh Lý (52300220), Sử Thị Yến Linh (52300218). **GVHD:** TS. Hồ Thị Linh.

Mô hình đề tài **NeuMF-F** giữ hai nhánh của NeuMF — GMF (nhân tử hoá ma trận) và MLP (mạng nơ-ron sâu), hợp nhất sớm —
và bổ sung đặc trưng sản phẩm, khách hàng, thời gian để chấm được cả sản phẩm mới. Cấu hình được tinh chỉnh trên mẫu
khách hàng A; kết luận lấy trên mẫu khách hàng B độc lập, mở tập kiểm thử đúng một lần (giao thức v2).

## Thư mục

| Thư mục / file | Nội dung |
|---|---|
| `neumf_project/` | Mã nguồn, dữ liệu, kết quả, demo web, notebook Colab |
| `Report DACNTT/` | Báo cáo LaTeX (`main.tex`, biên dịch bằng `compile.bat`) |
| `tai_lieu/` | Tài liệu tham khảo (luận án của GVHD) |
| `van_dap.md` | Chuẩn bị vấn đáp: trả lời 17 góp ý của GVHD |
| `tong_hop_thay_doi_v2.md` | Thay đổi của giao thức v2 và mức độ hoàn thành hiện tại |

## Đọc gì, ở đâu

| Cần | Đọc |
|---|---|
| Cài đặt và chạy | [`neumf_project/README.md`](neumf_project/README.md) |
| Bài toán, phạm vi, phương pháp | [`neumf_project/pham_vi_du_an.md`](neumf_project/pham_vi_du_an.md) |
| Kế hoạch đăng ký trước (mô hình, độ đo, 10 so sánh) | [`neumf_project/audit/PREREG_v2.md`](neumf_project/audit/PREREG_v2.md) |
| Demo web | [`neumf_project/demo/README.md`](neumf_project/demo/README.md) |
| Tình hình hiện tại | [`tong_hop_thay_doi_v2.md`](tong_hop_thay_doi_v2.md) |
| Chuẩn bị vấn đáp | [`van_dap.md`](van_dap.md) |

Giao thức v1 (mẫu A, mô hình chỉ dùng ID) là **lịch sử phát triển**: kế hoạch ở `neumf_project/audit/PREREG.md`, kết
quả ở `neumf_project/outputs/final/`, báo cáo mục 4.5.
