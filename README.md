# Đồ án CNTT — Mô hình khuyến nghị lai NeuMF-F trên dữ liệu H&M

**Đề tài:** Xây dựng mô hình khuyến nghị lai kết hợp nhân tử hoá ma trận và mạng lưới thần kinh sâu.
**Sinh viên:** Lê Minh Lý (52300220), Sử Thị Yến Linh (52300218). **GVHD:** TS. Hồ Thị Linh.

Mô hình đề tài **NeuMF-F** giữ hai nhánh của NeuMF — GMF (nhân tử hoá ma trận) và MLP (mạng nơ-ron sâu), hợp nhất sớm —
và bổ sung đặc trưng sản phẩm, khách hàng, thời gian để chấm được cả sản phẩm mới. Cấu hình được tinh chỉnh trên mẫu
khách hàng A; kết luận lấy trên mẫu khách hàng B độc lập, mở tập kiểm thử đúng một lần (giao thức v2).

**Trạng thái (04/10/2026):** đánh giá cuối trên mẫu B đã chạy xong (5 seed). NeuMF-F đứng 3/14 (NDCG@10 = 0,01470),
tốt hơn 6/9 đối thủ trong họ so sánh đăng ký trước, ngang GMF-F và UserKNN, thua LateFusion-F (0,01753). Chi tiết, mức
độ hoàn thành và đối chiếu 17 góp ý của GVHD: [`tong_hop_thay_doi_v2.md`](tong_hop_thay_doi_v2.md).

## Thư mục

| Thư mục / file | Nội dung |
|---|---|
| `neumf_project/` | Mã nguồn, dữ liệu, kết quả, demo web, notebook Colab |
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

Giao thức v1 (mẫu A, mô hình chỉ dùng ID) là **lịch sử phát triển**: kế hoạch ở `neumf_project/audit/PREREG.md`, kết
quả ở `neumf_project/outputs/final/`, báo cáo mục 4.5.
