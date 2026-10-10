# Đồ án CNTT — Mô hình khuyến nghị lai NeuMF-F trên dữ liệu H&M

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu.
**Sinh viên:** Lê Minh Lý (52300220), Sử Thị Yến Linh (52300218). **GVHD:** TS. Hồ Thị Linh.

Mô hình đề tài **NeuMF-F** giữ hai nhánh của NeuMF — GMF (nhân tử hoá ma trận) và MLP (mạng nơ-ron sâu), hợp nhất sớm —
và bổ sung đặc trưng sản phẩm, khách hàng, thời gian. Cấu hình được tinh chỉnh trên mẫu phát triển; kết luận lấy trên
mẫu kiểm định độc lập, mở tập kiểm thử đúng một lần (giao thức v2).

**Trạng thái (10/10/2026):** đánh giá cuối trên mẫu kiểm định đã chạy xong (5 seed). NeuMF-F đứng 2/14
(NDCG@10 = 0,04003), tốt hơn có ý nghĩa 7/9 đối thủ trong họ so sánh đăng ký trước, không khác biệt có ý nghĩa với
GMF-F (0,03902) và LateFusion-F (0,04093, cao nhất). Kết quả: `neumf_project/outputs/v2/final/ket_qua.txt`.
`tong_hop_thay_doi_v2.md` và `van_dap.md` còn ghi số của lần đánh giá trước (04/10/2026).

## Thư mục

| Thư mục / file | Nội dung |
|---|---|
| `neumf_project/` | Mã nguồn, dữ liệu, kết quả, demo web |
| `Report DACNTT/` | Báo cáo LaTeX (`main.tex`, biên dịch bằng `compile.bat`) |
| `tai_lieu/` | Tài liệu tham khảo (luận án của GVHD) |
| `van_dap.md` | Chuẩn bị vấn đáp: trả lời 17 góp ý của GVHD |
| `tong_hop_thay_doi_v2.md` | Đồ án làm gì và vì sao, kết quả v2, đối chiếu 17 góp ý, mức độ hoàn thành |

## Đọc gì, ở đâu

| Cần | Đọc |
|---|---|
| Cài đặt và chạy | [`neumf_project/README.md`](neumf_project/README.md) |
| Bài toán, phạm vi, phương pháp | [`neumf_project/pham_vi_du_an.md`](neumf_project/pham_vi_du_an.md) |
| Kế hoạch đăng ký trước (mô hình, độ đo, 10 so sánh) | [`neumf_project/audit/PREREG_v2.md`](neumf_project/audit/PREREG_v2.md) |
| Demo web | [`neumf_project/demo/README.md`](neumf_project/demo/README.md) |
| Tình hình hiện tại | [`tong_hop_thay_doi_v2.md`](tong_hop_thay_doi_v2.md) |
| Chuẩn bị vấn đáp | [`van_dap.md`](van_dap.md) |

Giao thức v1 (mẫu phát triển, mô hình chỉ dùng ID) là **lịch sử phát triển**: kế hoạch ở
`neumf_project/audit/PREREG.md`, báo cáo mục 4.5; mã nguồn và kết quả nằm trong lịch sử git (commit `9799f1a`).
