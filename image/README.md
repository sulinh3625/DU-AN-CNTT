# Sơ đồ của đề tài

Chín hình sơ đồ của báo cáo được vẽ bằng draw.io từ script `src/hinh_bao_cao.py`, lưu trong `hinh_bao_cao.drawio`
(mỗi hình một trang, mở bằng draw.io sửa tay được). PNG nằm ở thư mục này, PDF vector được chép vào
`Report DACNTT/media/figures/so_do/`, nơi các chương C1–C3 dùng.

| Hình | Nội dung | Chương |
|---|---|---|
| `hinh_cac_buoc` | Bốn bước thực hiện đề tài | C1 |
| `hinh_kien_truc_neumf` | Kiến trúc NeuMF (chỉ dùng mã ID) | C2 |
| `hinh_hop_nhat` | Hợp nhất sớm và hợp nhất muộn | C2 |
| `hinh_duong_ong` | Đường ống huấn luyện và đánh giá mô hình | C3 |
| `hinh_xu_ly_du_lieu` | Bốn bước xử lý dữ liệu H&M, ra hai mẫu khách hàng | C3 |
| `hinh_chia_thoi_gian` | Hai giai đoạn trên một trục thời gian | C3 |
| `hinh_kien_truc_neumf_f` | Kiến trúc mô hình đề xuất NeuMF-F | C3 |
| `hinh_tinh_chinh_danh_gia` | Tinh chỉnh trên mẫu phát triển, đánh giá cuối trên mẫu kiểm định | C3 |
| `hinh_kien_truc_demo` | Ba tầng của hệ thống demo | C3 |

Các trang thêm chỉ dùng cho slide (không vào báo cáo, không xuất PDF), là bản nằm ngang của hình báo cáo để chữ đủ lớn
trên khổ 16:9, cùng thẻ, cùng màu, cùng số thứ tự: `hinh_neumf_ngang`, `hinh_neumf_f_ngang` (slide 4, NeuMF đổi thành
NeuMF-F tại chỗ), `hinh_du_lieu_hm_ngang`, `hinh_du_lieu_amazon_ngang` (slide 5), `hinh_demo_ngang` (slide 12).
Slide 6 dùng thẳng `hinh_chia_thoi_gian`, slide 11 dùng `hinh_hop_nhat`.

Poster (`Report DACNTT/poster/`): sơ đồ NeuMF-F rộng hết cột (`media/poster_mo_hinh.png`, xuất hệ số 4 mỗi lần chạy
script); phần demo là trang cửa hàng của demo, gồm khách ví dụ và hai danh sách khuyến nghị (`build_poster.py` tự cắt
từ `media/figures/demo/demo_v2.png`; số liệu đã có ở phần kết quả của poster nên không lặp lại).

## Lối vẽ

Học từ sơ đồ kiến trúc của khóa luận nhóm (`Report KLTN/so_do/gen2.py`):
- Thẻ nền trắng viền rõ, chữ đậm; số thứ tự (một màu xanh) ở góc thẻ hoặc trên mũi tên; vòng cập nhật khi huấn luyện vẽ
  nét đứt, đi ngoài lề; khung nét đứt nhạt chỉ dùng để gom khối cùng nhóm; khối hợp nhất của NeuMF/NeuMF-F nền navy.
- Mỗi thẻ một biểu tượng ô màu (`src/bieu_tuong.py`, nét vẽ từ bộ Tabler, giấy phép MIT).
- Quy trình nhiều bước xếp dọc, mỗi bước một hàng (dễ đọc hơn hàng ngang khi thu vào khổ giấy).
- Màu chỉ để phân loại, đúng như lời văn báo cáo, và giống nhau ở mọi hình: mọi thẻ bước nền trắng, biểu tượng xanh
  (không tô riêng một bước); xám là dữ liệu đầu vào; xanh lá là đầu ra; xanh là nhánh GMF, tím là nhánh MLP; cam chỉ dùng
  cho đặc trưng (và giai đoạn kiểm thử trên trục thời gian); navy cho khối hợp nhất và tên tầng của demo.
- Một hướng đọc cho cả hình, không đường nào cắt hình hay cắt nhau; mỗi khối một tên ngắn và nhiều nhất hai dòng phụ;
  ký hiệu theo bài báo NCF: vector là dãy ô, ⊙ là nhân từng phần tử, [a ; b] là nối, σ là sigmoid.
- Vector của NeuMF-F là tổng của nhúng ID và phép chiếu đặc trưng (báo cáo C3), nên vẽ bằng ô chuyển màu, không nối thêm ô.

## Sửa và xuất lại

Không cần draw.io desktop, nhưng cần mạng để nạp trình xem draw.io. Từ `image/src/`:

```bash
python hinh_bao_cao.py                   # ghi ../hinh_bao_cao.drawio, ../hinh_*.png và PDF vào báo cáo
python hinh_bao_cao.py hinh_hop_nhat     # chỉ xuất PNG của các hình được nêu tên, để sửa nhanh
python xuat_anh_drawio.py <file.drawio> <thư_mục> [tên ...]   # xuất PNG cho file .drawio bất kỳ
```

Mỗi hình là một hàm trong `hinh_bao_cao.py`. Sửa xong thì biên dịch lại báo cáo (`Report DACNTT/compile.bat`).
