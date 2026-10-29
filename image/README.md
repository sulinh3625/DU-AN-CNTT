# Sơ đồ của đề tài

Mọi sơ đồ vẽ bằng draw.io từ script `src/so_do_bao_cao.py` (kể cả `pipeline_neumf_5trang.drawio` ở gốc repo:
5 trang tổng quan, dữ liệu, chia thời gian, NeuMF-F, tinh chỉnh và đánh giá; bản vẽ tay cũ ở `src/pipeline_goc.drawio`). Màu chỉ để phân loại khối: xám là dữ liệu và đầu vào, xanh
dương là bước xử lý và nhánh GMF, tím nhạt là nhánh MLP, cam là bước chính hoặc phép hợp nhất, xanh lá là kết quả. Các
hình minh hoạ theo quy ước của bài báo NCF: vector vẽ thành dãy ô, vector one-hot có một ô tô đậm, phép toán (⊙, σ)
là vòng tròn nhỏ, kho dữ liệu là hình trụ, màn hình giao diện là khung cửa sổ.

## Nguyên tắc vẽ

Tổng hợp từ các hướng dẫn vẽ lưu đồ (Visual Paradigm, Creately, Lucid) và khung hướng dẫn sơ đồ mạng nơ-ron của
Marshall, Freitas và Jay (PLOS One, 2025):

1. Cả hình đi một hướng: trên xuống (báo cáo) hoặc trái sang phải (slide tổng quan).
2. Không có đường cắt nhau. Khi cấu trúc dễ gây cắt thì đổi chỗ khối, không vẽ đường vòng. Ví dụ ở hình NeuMF-F: hai đầu
   vào xếp chồng ở giữa, đường của khách hàng ra hai cột ngoài, đường của sản phẩm vào hai cột trong.
3. Mỗi khối một tên ngắn và nhiều nhất một dòng phụ. Không đặt khung ghi chú trong hình; giải thích để ở chú thích và
   lời văn.
4. Có đủ đầu vào và đầu ra của cả hệ thống; một kiểu mũi tên; các khối cùng hàng cùng cỡ, thẳng hàng.
5. Ký hiệu theo quy ước của bài báo gốc: ⊙ là nhân từng phần tử, [a ; b] là nối, σ là sigmoid.

## Tệp

| Tệp | Nội dung | Dùng ở |
|---|---|---|
| `bc_01_duong_ong` | Dữ liệu → tiền xử lý → đặc trưng → huấn luyện → lưu mô hình → khuyến nghị Top-K | Báo cáo Hình 3.1 |
| `bc_02_xu_ly_du_lieu` | Bốn bước xử lý dữ liệu H&M, ra mẫu phát triển và mẫu kiểm định | Báo cáo Hình 3.2, slide 2 |
| `bc_03_chia_thoi_gian` | Hai giai đoạn trên một trục thời gian | Báo cáo Hình 3.3, slide 3 |
| `bc_04_kien_truc_neumf_f` | Kiến trúc NeuMF-F | Báo cáo Hình 3.4, slide 4 |
| `bc_05_tinh_chinh_danh_gia` | Tinh chỉnh trên mẫu phát triển, đánh giá cuối trên mẫu kiểm định | Báo cáo Hình 3.5, slide 6 |
| `bc_06_kien_truc_demo` | Ba tầng của demo | Báo cáo, mục kiến trúc demo |
| `bc_07_kien_truc_neumf` | Kiến trúc NeuMF gốc (chỉ dùng mã ID) | Báo cáo Hình 2.1, slide 7 |
| `bc_08_hop_nhat` | Hợp nhất sớm và hợp nhất muộn | Báo cáo Hình 2.2, slide 8 |
| `bc_09_cac_buoc` | Bốn bước thực hiện đề tài | Báo cáo Hình 1.1 |
| `slide_01_tong_quan` | Đường ống trên một hàng, trái sang phải | Slide 1 |
| `slide_05_doi_chung` | NeuMF-F và ba nhóm mô hình đối chứng | Slide 5 |

Các tệp `slide_02`, `03`, `04`, `06`, `07`, `08` là cùng hình với báo cáo, xuất PNG cho slide.

## Sửa và xuất lại

Cần draw.io desktop (Windows: `%LOCALAPPDATA%\Programs\draw.io\draw.io.exe`). Từ thư mục `image/src/`:

```bash
python so_do_bao_cao.py   # ghi so_do_bao_cao.drawio, so_do_slide.drawio; xuất bc_*.png/pdf, slide_*.png; chép PDF vào báo cáo
```

Mỗi hình là một hàm trong `so_do_bao_cao.py`, mỗi khối là một lệnh `t.o(loại, x, y, rộng, cao, nhãn)`, mỗi mũi tên là
`t.mt(từ, đến, cạnh ra, cạnh vào)`. Có thể mở tệp `.drawio` để chỉnh tay, nhưng lần chạy script sau sẽ ghi đè. Sửa xong
thì biên dịch lại báo cáo.
