# Demo web — shop thời trang H&M (kèm Amazon Beauty)

Chọn bộ dữ liệu trên thanh đầu trang (`?ds=hm` / `?ds=amazon`):
- **H&M:** kết quả chính.
- **Amazon Beauty:** dữ liệu đối chứng (`audit/PREREG_amazon.md`). Demo nạp checkpoint seed 42 của
  `outputs/amazon/final/`. Chưa có thư mục này thì demo hiện lệnh cần chạy (`python run.py amazon-final --reason "..."`);
  demo không tự huấn luyện.
- **Sản phẩm Amazon:** một sản phẩm là một `asin`. Tên, thương hiệu, danh mục và giá lấy từ
  `data/processed/amazon/items.csv.gz` (do `python run.py amazon-data` tạo); ảnh lấy theo `imUrl` gốc của Amazon (trình
  duyệt tải thẳng từ máy chủ ảnh của Amazon); ảnh lỗi thì hiện ô thay thế.
- **Khách Amazon:** không có tuổi. "Khu vực mua nhiều nhất" là danh mục cấp 1, ví dụ Makeup hay Skin Care.

Web mô phỏng shop thời trang trên dữ liệu H&M. Demo chỉ **suy diễn** trên checkpoint của đánh giá cuối: không huấn luyện
lại, không sửa code huấn luyện (`src/`, `scripts/`), chỉ import hàm từ đó. Số liệu trên demo là **hiển thị lại** kết quả
đã chấm, không phải một lần chấm tập kiểm thử mới.

## 1. Chuẩn bị

Từ thư mục `neumf_project/`:

```bash
pip install -r requirements.txt
python run.py sample-hm      # mẫu phát triển
python run.py v2-data        # mẫu kiểm định + đặc trưng + dữ liệu đã lọc
```

- `data/raw/hm/` cần đủ 3 file Kaggle: `transactions_train.csv`; `articles.csv` (tên, loại sản phẩm; đặc trưng);
  `customers.csv` (đặc trưng; tuổi hiện trong danh sách chọn khách).
- Cần kết quả đánh giá cuối `outputs/v2/final/` — gồm `data.json` và `seed42/` kèm checkpoint — sinh bởi
  `python run.py v2-final` (`README.md` dự án, mục 3.3; đã có trong git).

## 2. Chạy

```bash
python run.py demo           # hoặc: python -m demo
```

- Mở **http://localhost:8000** (trang Cửa hàng; ba trang: Cửa hàng · Kết quả đánh giá · Giới thiệu đề tài; bảng số liệu đầy đủ mở từ trang Kết quả đánh giá; nút mặt trời / mặt trăng đổi sáng / tối). Lần nạp đầu mất khoảng 30 giây (dựng lại dữ liệu, nạp checkpoint); sau đó được cache.
- Sau khi chạy lại đánh giá cuối, nạp lại không cần khởi động lại: `curl -X POST http://localhost:8000/api/reload`.
- Mở thẳng một khách để chụp ảnh minh hoạ cho báo cáo:
  `http://localhost:8000/?user=<customer_id>&compare=1&a=NeuMF-F&b=NeuMF#admin`.
- Dừng: `Ctrl+C`. Nếu cổng 8000 đang bận (một demo cũ chưa tắt), demo tự dùng cổng trống kế tiếp và in địa chỉ ra màn hình; muốn giải phóng cổng 8000 trên Windows: `netstat -ano | findstr :8000` rồi `taskkill /PID <pid> /F`.

## 3. Màn hình

| Màn hình | Nội dung |
|---|---|
| **Tổng quan** (trang mặc định) | Đề tài làm gì: một câu bài toán, ba ô dữ liệu / mô hình / cách chấm, và một khách thật làm ví dụ (lịch sử mua, top-10 của NeuMF-F và của NeuMF, món khách mua sau mốc). Khách ví dụ do `/api/example` chọn theo dữ liệu: NeuMF-F trúng, NeuMF trượt, hạng tính lại trùng hạng đã lưu; tìm sẵn ở luồng nền khi nạp dữ liệu. |
| **Cửa hàng** (trang mặc định) | Cửa hàng mô phỏng: chọn khách (khách ví dụ mở sẵn, ngẫu nhiên, tìm theo mã, khách mới); thẻ sản phẩm đã mua trước mốc; K gợi ý của một mô hình hoặc hai mô hình cạnh nhau; nút **Xem khách đã mua gì** lật đáp án (món khách mua sau mốc được đánh dấu, kèm vị trí trong xếp hạng của từng mô hình); bấm thẻ sản phẩm mở thẻ chi tiết (tên, loại, màu, mô tả gốc, số khách đã mua, sản phẩm tương tự theo ItemKNN); mục **Khách có gu giống** theo UserKNN. URL `?user=<mã>&compare=1&a=NeuMF-F&b=NeuMF&k=5&reveal=1&item=<chỉ số sản phẩm>#/shop` mở sẵn một trạng thái (dùng khi chụp ảnh minh hoạ). |
| **Kết quả đánh giá** | Kết quả có đúng hướng không: số khách trên 100 có ít nhất một món đúng trong 10 gợi ý (HR@10) đặt cạnh LateFusion-F, NeuMF, bán chạy nhất, ngẫu nhiên; ba câu hỏi của đề tài với câu trả lời Có / Một phần / Không suy ra từ kết luận kiểm định đã lưu; xếp hạng NDCG@10; bóc tách (nhãn "chưa khẳng định" khi khoảng tin cậy chứa 0); phạm vi chưa trả lời. Đọc `/api/results`. |
| **Bảng số liệu đầy đủ** (mở từ trang Kết quả đánh giá) | Chỉ đọc `outputs/v2/final/*.csv` (Amazon: `outputs/amazon/final/*.csv`): kết quả 5 seed, đánh giá theo K (5 · 10 · 15 · 20, từ `by_k.csv` — tính lại từ hạng đã lưu), kiểm định họ 10 so sánh, độ phủ top-10 và chi phí huấn luyện, ablation NeuMF-F. Khi đã chấm bổ sung mô hình lai truyền thống (`scripts/25_bosung.py`), đọc bảng trong `final/bosung/` (thêm Hybrid-CBCF, dấu *) và hiện thêm thẻ kiểm định họ bổ sung B1–B2. Thiếu file thì hiện lệnh cần chạy. |

13 mô hình: NeuMF-F, LateFusion-F, GMF-F, MLP-F, NeuMF, GMF, MLP, BPR-MF, UserKNN, ItemKNN, MostPopular-Recent,
Content, Most Popular — seed 42, cấu hình theo `results.json`, đã huấn luyện lại trên mọi cặp trước 29/07/2020. Mặc định
so sánh NeuMF-F với NeuMF. Thêm mô hình lai truyền thống **Hybrid-CBCF** (Content + UserKNN + ItemKNN, trọng số trong
`final/bosung/results.json`) khi đã chấm bổ sung bằng `python run.py bosung-final` (Amazon: `amazon-bosung-final`);
chưa chấm thì mô hình này bị ẩn kèm lệnh cần chạy.

Giao diện có hai chế độ sáng và tối (nút mặt trăng / mặt trời góc trên bên phải). Lần đầu mở, demo theo cài đặt của hệ
điều hành; lựa chọn sau đó được lưu trong trình duyệt.

## 4. Cách chấm — khớp đánh giá cuối

- Chỉ nạp khi `data_md5` trong `outputs/v2/final/data.json` khớp `outputs/data/manifest.json` (kết quả được tạo từ đúng
  file dữ liệu đã lọc hiện tại) — kiểm trước khi dựng dữ liệu, để demo không dựng tập kiểm thử của mẫu kiểm định cho
  một kết quả cũ.
- Dữ liệu dựng lại bằng đúng `scripts/v2_common.py`, rồi đối chiếu số khách và số cặp đúng với `data.json`; lệch thì máy
  chủ báo lỗi thay vì nạp checkpoint với ánh xạ ID sai. Tập ứng viên và sản phẩm đích lấy thẳng từ dữ liệu dựng lại.
- Một sản phẩm là một mẫu (`product_code`, mọi màu gộp lại); tên, loại và ảnh lấy theo màu có `article_id` nhỏ nhất.
- Lịch sử hiển thị = mọi cặp trước mốc kiểm thử 29/07/2020 (đúng dữ liệu mô hình đã học); ngày hiển thị là ngày mua đầu.
- Sản phẩm đích = các món khách mua lần đầu trong giai đoạn kiểm thử. Ứng viên = sản phẩm có dữ liệu huấn luyện, trừ món
  khách đã mua.
- Xếp theo điểm giảm dần; hoà điểm phá bằng cùng khoá tất định với lúc đánh giá. Mạng nơ-ron xếp bằng logit (không qua
  sigmoid). LateFusion-F chuẩn hoá min–max điểm trên tập ứng viên của khách.
- HR@K, NDCG@K, Recall@K, Precision@K tính với nhiều sản phẩm đích mỗi khách; K chọn trong các giá trị của cấu hình,
  thêm K = 15, 20 (`DEMO_EXTRA_K` trong `data_context.py`) như bảng theo K của báo cáo — cùng thứ hạng nên số @5/@10
  không đổi.
- **Luôn có gợi ý.** Khách không có trong dữ liệu đã học (khách mới, hoặc quá ít lần mua để qua lọc k-core) nhận danh
  sách Most Popular gắn nhãn "Gợi ý phổ biến" thay cho lỗi 404 (`inference.popular`); khách có lịch sử nhưng không mua
  món mới nào trong giai đoạn đánh giá vẫn nhận gợi ý của mô hình đang chọn, chỉ không có chỉ số (không có sản phẩm
  đích). Trong bảng chọn khách, gõ một mã không có trong danh sách rồi bấm "Xem gợi ý cho mã …".
- **Đối chiếu với đánh giá cuối.** Với mỗi khách đã được đánh giá, demo so hạng tính lại với
  `outputs/<bộ dữ liệu>/final/seed42/per_user.csv.gz` (Hybrid-CBCF: `bosung/per_user.csv.gz`) và trả kèm số đã lưu
  (`evaluation.final`: hạng, chỉ số, `match`). Mô hình không dùng vector văn bản trùng hạng đã lưu trên mọi máy đã thử,
  kể cả máy chỉ có CPU. Bốn mô hình có đặc trưng, Content và Hybrid-CBCF đọc vector văn bản trong `data/processed/`;
  tệp này mỗi máy tự dựng và phụ thuộc phiên bản thư viện, nên chỉ trùng khi giống máy đã tạo kết quả. Khi lệch, khối
  đánh giá hiện số đã lưu kèm lý do. Có test tự động (`demo/tests/test_demo.py`).

## 5. Biến môi trường

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `DEMO_V2_DIR` | `outputs/v2/final` | Thư mục kết quả (vd. `outputs/v2/dry_run` — bản chạy thử trên tập xác thực của mẫu phát triển) |
| `HM_IMAGES_DIR` | (không có) | Thư mục `images/` gốc của H&M, dùng cho `copy_images.py` |
| `DEMO_IMAGES_DIR` | `demo/static/images` | Thư mục ảnh mà máy chủ phục vụ |

## 6. Ảnh sản phẩm (tuỳ chọn)

Ảnh H&M có dạng `images/<3 chữ số đầu>/<article_id 10 chữ số>.jpg`. Lệnh dưới chỉ chép ảnh của các sản phẩm demo dùng;
sản phẩm không có ảnh hiển thị ô thay thế ghi loại sản phẩm.

```bash
HM_IMAGES_DIR=/duong/dan/h-and-m/images python demo/scripts/copy_images.py
```

## 7. Cấu trúc mã và API

```text
demo/
├── backend/
│   ├── main.py              FastAPI, phục vụ frontend/
│   ├── routes.py            các endpoint /api/*
│   ├── data_context.py      dựng dữ liệu, nạp checkpoint, bảng sản phẩm và bảng khách, láng giềng UserKNN
│   ├── inference.py         xếp hạng toàn bộ ứng viên cho một khách
│   └── metrics_io.py        đọc file kết quả cho dashboard
├── frontend/                index.html, app.js, style.css (HTML tĩnh + Chart.js qua CDN)
├── scripts/copy_images.py
└── tests/test_demo.py       python -m pytest demo/tests -q
```

| Endpoint | Chức năng |
|---|---|
| `GET /api/datasets` | Bộ dữ liệu của demo (H&M, Amazon Beauty) và lý do chưa nạp được (thiếu kết quả đánh giá cuối) |
| `GET /api/context` | Mẫu, số khách/sản phẩm, giá trị K, mô hình khả dụng và mô hình bị ẩn kèm lý do |
| `POST /api/reload` | Xoá cache, nạp lại |
| `GET /api/users/facets` | Số khách có sản phẩm đích; ngưỡng và số khách của nhóm ít / trung bình / nhiều giao dịch; số khách theo khu vực mua nhiều nhất |
| `GET /api/users/search?q=&bucket=&area=&hit=&model=&k=&sort=&offset=&limit=` | Danh sách khách có sản phẩm đích: `customer_id` chứa `q` (khớp ở đầu xếp trước), lọc nhóm / khu vực, `hit=hit\|miss` theo top-`k` của `model` (kèm cột `best_rank`), sắp `train_desc` · `train_asc` · `targets_desc` · `rank` · `id`; trả `total` và một trang |
| `GET /api/users/showcase?a=&b=&k=&limit=` | Nút "Xem ví dụ": khách có món đích trong top-`k` của mô hình `a` nhưng không trong top-`k` của `b`, hạng trùng số đã lưu ở đánh giá cuối với cả hai mô hình, xếp theo chênh hạng giảm dần (cột `best_rank` của `a`, `rank_b`) |
| `GET /api/users/random?…` | Khách ngẫu nhiên trong bộ lọc (cùng tham số, bỏ qua `q`) |
| `GET /api/users/{customer_id}/position?…` | Vị trí của khách trong danh sách đang lọc (cùng tham số), kèm khách liền trước / liền sau |
| `GET /api/users/{customer_id}/history` | Thông tin khách (`profile`) và lịch sử mua mô hình đã học, sắp theo thời gian; khách mới: `is_new = true`, lịch sử rỗng |
| `GET /api/users/{customer_id}/recommend?model=&k=` | Top-K, hạng từng sản phẩm đích, số ứng viên, HR/NDCG/Recall@K; khách mới: danh sách Most Popular (`fallback = "popular"`, `evaluation = null`); khách không có sản phẩm đích: gợi ý của mô hình, `evaluation = null` |
| `GET /api/users/{customer_id}/neighbors?k=10` | Khách tương đồng nhất theo UserKNN, số món mua chung, láng giềng đã mua sản phẩm đích nào; khách mới: danh sách rỗng kèm ghi chú | Dùng ở mục Khách có gu giống của trang Cửa hàng.
| `GET /api/items/{item_idx}/similar?k=6` | Thẻ chi tiết sản phẩm: thông tin sản phẩm (kèm mô tả gốc `detail_desc` và các màu của mẫu với H&M), số khách đã mua trước mốc, k sản phẩm tương tự nhất theo ItemKNN đã chọn |
| `GET /api/dashboard` | Các khối của dashboard, kèm file nguồn |
| `GET /api/results` | Trang Kết quả đánh giá: mô hình (NDCG@10, HR@10), họ 10 so sánh, bóc tách, câu trả lời của ba câu hỏi, quy mô tập kiểm thử; đọc `summary.csv` (hoặc `bosung/summary.csv`), `significance.csv`, `ablation.csv`, `data.json`. Test `test_results_page_matches_report_macros` đối chiếu từng số với macro của báo cáo |
| `GET /api/example` | Khách ví dụ của trang Tổng quan (hồ sơ, lịch sử, gợi ý của NeuMF-F và NeuMF) |
| `GET /api/image/{article_id}` | Ảnh sản phẩm hoặc ô thay thế |

Mọi endpoint (trừ `/api/datasets`) nhận thêm `?dataset=hm|amazon`, mặc định `hm`.

Bản đóng gói Docker (`Dockerfile`, `docker-compose.yml`) chưa được kiểm tra với dữ liệu hiện tại.
