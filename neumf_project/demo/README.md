# Demo web — shop thời trang H&M

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

- Mở **http://localhost:8000**. Lần nạp đầu mất khoảng 30 giây (dựng lại dữ liệu, nạp checkpoint); sau đó được cache.
- Sau khi chạy lại đánh giá cuối, nạp lại không cần khởi động lại: `curl -X POST http://localhost:8000/api/reload`.
- Mở thẳng một khách để chụp ảnh minh hoạ cho báo cáo:
  `http://localhost:8000/?user=<customer_id>&compare=1&a=NeuMF-F&b=NeuMF#admin`.
- Dừng: `Ctrl+C`; trên Windows nếu cổng còn bận: `netstat -ano | findstr :8000` rồi `taskkill /PID <pid> /F`.

## 3. Màn hình

| Màn hình | Nội dung |
|---|---|
| **Kiểm thử mô hình** (trang mặc định) | **Chọn khách**: thanh khách hiện mã, số món đã mua / món đích, nhóm giao dịch, khu vực mua nhiều nhất, tuổi, loại sản phẩm hay mua; nút ‹ › (phím ← →) sang khách trước / sau trong danh sách đang lọc, nút Ngẫu nhiên. Bảng chọn mở bằng **Ctrl K** hoặc **/**: tìm theo một đoạn `customer_id`, lọc nhóm giao dịch và khu vực, lọc **Gợi ý trúng / Gợi ý trượt** (có / không có món đích trong top-K của mô hình và K đang chọn; lần đầu với mỗi mô hình chấm mọi khách mất vài giây, sau đó giữ lại), sắp xếp (kể cả theo hạng món đích tốt nhất), ↑ ↓ Enter để chọn, mục "Xem gần đây" (lưu trong trình duyệt). URL giữ `?user=` nên tải lại hay gửi link vẫn mở đúng khách. **Sau khi chọn**: lịch sử mua (đúng dữ liệu mô hình đã học), top-K của một mô hình hoặc so sánh hai mô hình, hạng của từng sản phẩm đích, HR@K, NDCG@K, Recall@K. Thẻ **"10 khách tương đồng nhất"** (UserKNN): độ tương đồng, số món mua chung, láng giềng đã mua sản phẩm đích nào. |
| **Dashboard** | Chỉ đọc `outputs/v2/final/*.csv`: kết quả 5 seed, đánh giá theo K (5 · 10 · 20), kiểm định họ 10 so sánh, độ phủ top-10 và chi phí huấn luyện, ablation NeuMF-F. Thiếu file thì hiện lệnh cần chạy. |

13 mô hình: NeuMF-F, LateFusion-F, GMF-F, MLP-F, NeuMF, GMF, MLP, BPR-MF, UserKNN, ItemKNN, MostPopular-Recent,
Content, Most Popular — seed 42, cấu hình theo `results.json`, đã huấn luyện lại trên mọi cặp trước 29/07/2020. Mặc định
so sánh NeuMF-F với NeuMF.

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
  thêm K = 20 (`DEMO_EXTRA_K` trong `data_context.py`) để xem danh sách dài hơn — cùng thứ hạng nên số @5/@10 không đổi.
- Số theo từng khách khớp `outputs/v2/final/seed42/per_user.csv.gz` — có test tự động (`demo/tests/test_demo.py`). Đánh
  giá cuối chạy trên GPU, logit tính lại trên CPU có thể làm vài cặp gần như hoà điểm ở hạng rất sâu (trên 100) đổi chỗ —
  không ảnh hưởng chỉ số @K.

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
| `GET /api/context` | Mẫu, số khách/sản phẩm, giá trị K, mô hình khả dụng và mô hình bị ẩn kèm lý do |
| `POST /api/reload` | Xoá cache, nạp lại |
| `GET /api/users/facets` | Số khách có sản phẩm đích; ngưỡng và số khách của nhóm ít / trung bình / nhiều giao dịch; số khách theo khu vực mua nhiều nhất |
| `GET /api/users/search?q=&bucket=&area=&hit=&model=&k=&sort=&offset=&limit=` | Danh sách khách có sản phẩm đích: `customer_id` chứa `q` (khớp ở đầu xếp trước), lọc nhóm / khu vực, `hit=hit\|miss` theo top-`k` của `model` (kèm cột `best_rank`), sắp `train_desc` · `train_asc` · `targets_desc` · `rank` · `id`; trả `total` và một trang |
| `GET /api/users/random?…` | Khách ngẫu nhiên trong bộ lọc (cùng tham số, bỏ qua `q`) |
| `GET /api/users/{customer_id}/position?…` | Vị trí của khách trong danh sách đang lọc (cùng tham số), kèm khách liền trước / liền sau |
| `GET /api/users/{customer_id}/history` | Thông tin khách (`profile`) và lịch sử mua mô hình đã học, sắp theo thời gian |
| `GET /api/users/{customer_id}/recommend?model=&k=` | Top-K, hạng từng sản phẩm đích, số ứng viên, HR/NDCG/Recall@K |
| `GET /api/users/{customer_id}/neighbors?k=10` | Khách tương đồng nhất theo UserKNN, số món mua chung, láng giềng đã mua sản phẩm đích nào |
| `GET /api/dashboard` | Các khối của dashboard, kèm file nguồn |
| `GET /api/image/{article_id}` | Ảnh sản phẩm hoặc ô thay thế |

Bản đóng gói Docker (`Dockerfile`, `docker-compose.yml`) chưa được kiểm tra với dữ liệu hiện tại.
