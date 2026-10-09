# Demo web — shop thời trang H&M

Web mô phỏng shop thời trang trên dữ liệu H&M. Demo chỉ **suy diễn** trên checkpoint đã huấn luyện: không huấn luyện
lại, không sửa code huấn luyện (`src/`, `scripts/`), chỉ import hàm từ đó. Số liệu trên demo là **hiển thị lại** kết quả
đã chấm, không phải một lần chấm tập kiểm thử mới.

## 1. Chuẩn bị

Từ thư mục `neumf_project/`:

```bash
pip install -r requirements.txt
python run.py sample-hm      # mẫu A
python run.py v2-data        # mẫu B + đặc trưng (chế độ v2)
```

- `data/raw/hm/` cần đủ 3 file Kaggle: `transactions_train.csv`; `articles.csv` (tên, loại sản phẩm; đặc trưng);
  `customers.csv` (đặc trưng; tuổi hiện trong danh sách chọn khách).
- Chế độ v2 (mặc định) cần kết quả đánh giá cuối `outputs/v2/final/` — gồm `data.json` và `seed42/` kèm checkpoint —
  sinh bởi `python run.py v2-final` (`README.md` dự án, mục 3.3).

## 2. Chạy

```bash
python run.py demo           # hoặc: python -m demo
```

- Mở **http://localhost:8000**. Lần nạp đầu ở chế độ v2 mất khoảng 30 giây (dựng lại dữ liệu, nạp checkpoint); sau đó
  được cache.
- Sau khi chạy lại đánh giá cuối, nạp lại không cần khởi động lại: `curl -X POST http://localhost:8000/api/reload`.
- Mở thẳng một khách để chụp ảnh minh hoạ cho báo cáo:
  `http://localhost:8000/?user=<customer_id>&compare=1&a=NeuMF-F&b=NeuMF#admin`.
- Dừng: `Ctrl+C`; trên Windows nếu cổng còn bận: `netstat -ano | findstr :8000` rồi `taskkill /PID <pid> /F`.

## 3. Màn hình

| Màn hình | Nội dung |
|---|---|
| **Kiểm thử mô hình** (trang mặc định) | **Chọn khách**: thanh khách hiện mã, số món đã mua / món đích, nhóm giao dịch, khu vực mua nhiều nhất, tuổi, loại sản phẩm hay mua; nút ‹ › (phím ← →) sang khách trước / sau trong danh sách đang lọc, nút Ngẫu nhiên. Bảng chọn mở bằng **Ctrl K** hoặc **/**: tìm theo một đoạn `customer_id`, lọc nhóm giao dịch và khu vực, lọc **Gợi ý trúng / Gợi ý trượt** (có / không có món đích trong top-K của mô hình và K đang chọn; lần đầu với mỗi mô hình chấm mọi khách mất vài giây, sau đó giữ lại), sắp xếp (kể cả theo hạng món đích tốt nhất), ↑ ↓ Enter để chọn, mục "Xem gần đây" (lưu trong trình duyệt). URL giữ `?user=` nên tải lại hay gửi link vẫn mở đúng khách. **Sau khi chọn**: lịch sử mua (đúng dữ liệu mô hình đã học), top-K của một mô hình hoặc so sánh hai mô hình, hạng của từng sản phẩm đích, HR@K, NDCG@K, Recall@K. Sản phẩm mới có nhãn **"Mới"**. Thẻ **"10 khách tương đồng nhất"** (UserKNN): độ tương đồng, số món mua chung, láng giềng đã mua sản phẩm đích nào. |
| **Dashboard** | Chỉ đọc file kết quả đã chạy; thẻ **Đánh giá theo K (5 · 10 · 20)** gom NDCG / Recall / HR / Precision ở mọi K có trong file (chế độ final: @20 từ `outputs/final/extra_k20.csv` của `scripts/16_extra_k.py`). Chế độ v2: `outputs/v2/final/*.csv` — kết quả 5 seed, kiểm định họ 10 so sánh, NDCG@10 theo nhóm sản phẩm cũ/mới, độ phủ và tỉ lệ sản phẩm mới, ablation NeuMF-F). Thiếu file thì hiện lệnh cần chạy. |

## 4. Chế độ

Chọn bằng biến môi trường `DEMO_MODE`; không đặt thì tự chọn theo thứ tự v2 → final → explore (chế độ đầu tiên có
checkpoint). Chế độ v2 chỉ dùng được khi `data_md5` trong `data.json` của kết quả khớp `outputs/data/manifest.json`
(kết quả được tạo từ đúng file dữ liệu đã lọc hiện tại); kết quả cũ thì tự chọn chế độ khác, còn `DEMO_MODE=v2` báo lỗi
— kiểm trước khi dựng dữ liệu, để demo không dựng tập kiểm thử của mẫu kiểm định ngoài đánh giá cuối.

| Chế độ | Nội dung |
|---|---|
| **`v2`** (kết quả chính) | Mô hình của **đánh giá cuối giao thức v2** — mẫu kiểm định B, seed 42, cấu hình theo `results.json`, đã huấn luyện lại trên mọi cặp trước 29/07/2020. 13 mô hình: NeuMF-F, LateFusion-F, GMF-F, MLP-F, NeuMF, GMF, MLP, BPR-MF, UserKNN, ItemKNN, MostPopular-Recent, Content, Most Popular. Mặc định so sánh NeuMF-F với NeuMF. |
| `final` | Mô hình của đánh giá cuối giao thức v1 (lịch sử phát triển): `outputs/final/seed42/`, mẫu A, không có sản phẩm mới. |
| `explore` | Run khám phá leave-one-out `hm500k_seed42` của giai đoạn đầu (cấu hình mặc định, chưa tinh chỉnh). |

Thử chế độ v2 trước khi có kết quả đánh giá cuối: `DEMO_V2_DIR=outputs/v2/dry_run` (bản chạy thử trên tập xác thực của
mẫu A, `python run.py v2-dry-run`).

## 5. Cách chấm — khớp đánh giá cuối

**Chế độ v2:**

- Dữ liệu dựng lại bằng đúng `scripts/v2_common.py`, rồi đối chiếu số khách và số cặp đúng với
  `outputs/v2/final/data.json`; lệch thì máy chủ báo lỗi thay vì nạp checkpoint với ánh xạ ID sai.
- Lịch sử hiển thị = mọi cặp trước mốc kiểm thử 29/07/2020 (đúng dữ liệu mô hình đã học); ngày hiển thị là ngày mua đầu.
- Sản phẩm đích = các món khách mua lần đầu trong giai đoạn kiểm thử, **gồm cả sản phẩm mới**.
- Ứng viên = sản phẩm cũ ∪ sản phẩm mới, trừ món khách đã mua. Mô hình chỉ dùng ID xếp mọi sản phẩm mới cuối danh sách
  (như lúc chấm); mô hình có đặc trưng và Content chấm được chúng.
- Số theo từng khách khớp `outputs/v2/final/seed42/per_user.csv.gz` — có test tự động (`demo/tests/test_demo.py`).

**Chung cho mọi chế độ:**

- Xếp theo điểm giảm dần; hoà điểm phá bằng cùng khoá tất định với lúc đánh giá (tie-break seed của cấu hình). Mạng
  nơ-ron xếp bằng logit (không qua sigmoid). LateFusion chuẩn hoá min–max điểm trên tập ứng viên của khách.
- HR@K, NDCG@K, Recall@K, Precision@K tính với nhiều sản phẩm đích mỗi khách; K chọn trong các giá trị của cấu hình,
  thêm K = 20 (`DEMO_EXTRA_K` trong `data_context.py`) để xem danh sách dài hơn — cùng thứ hạng nên số @5/@10 không đổi.
- Nếu đánh giá cuối chạy trên GPU, logit tính lại trên CPU có thể làm vài cặp gần như hoà điểm ở hạng rất sâu (trên 100)
  đổi chỗ — không ảnh hưởng chỉ số @K.

Chế độ `final` dựng lại dữ liệu theo `configs/hm500k_global.yaml` và đối chiếu với `outputs/final/seed42/results.json`;
chế độ `explore` dựng theo `configs/hm500k.yaml` và đối chiếu `outputs/experiments/<run_tag>/metadata.json`.

## 6. Biến môi trường

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `DEMO_MODE` | tự chọn: v2 → final → explore | `v2`, `final` hoặc `explore` |
| `DEMO_V2_DIR` | `outputs/v2/final` | Thư mục kết quả v2 (vd. `outputs/v2/dry_run`) |
| `DEMO_FINAL_SEED` | `42` | Seed của checkpoint được nạp (`seed<N>/`; đánh giá cuối v2 chỉ lưu checkpoint của seed 42) |
| `DEMO_CONFIG` | `configs/hm500k.yaml` | Cấu hình của chế độ `explore` |
| `DEMO_RUN_TAG` | run mới nhất có kết quả và checkpoint | Run của chế độ `explore` |
| `HM_IMAGES_DIR` | (không có) | Thư mục `images/` gốc của H&M, dùng cho `copy_images.py` |
| `DEMO_IMAGES_DIR` | `demo/static/images` | Thư mục ảnh mà máy chủ phục vụ |

## 7. Tuỳ chọn

**Ảnh sản phẩm.** Ảnh H&M có dạng `images/<3 chữ số đầu>/<article_id 10 chữ số>.jpg`. Lệnh dưới chỉ chép ảnh của các
sản phẩm thuộc chế độ đang dùng; sản phẩm không có ảnh hiển thị ô thay thế ghi loại sản phẩm.

```bash
HM_IMAGES_DIR=/duong/dan/h-and-m/images python demo/scripts/copy_images.py
```

**File offline cho dashboard chế độ `explore`.** `python demo/scripts/build_offline_artifacts.py` ghi
`demo/artifacts/<run_tag>/` (hạng của sản phẩm đích theo từng khách, top sản phẩm được gợi ý nhiều nhất); chế độ v2 và
final không cần bước này.

## 8. Cấu trúc mã và API

```text
demo/
├── backend/
│   ├── main.py              FastAPI, phục vụ frontend/
│   ├── routes.py            các endpoint /api/*
│   ├── data_context.py      ba chế độ: dựng dữ liệu, ánh xạ ID, nạp checkpoint, láng giềng UserKNN, bảng khách
│   ├── inference.py         xếp hạng toàn bộ ứng viên cho một khách
│   └── metrics_io.py        đọc file kết quả cho dashboard
├── frontend/                index.html, app.js, style.css (HTML tĩnh + Chart.js qua CDN)
├── scripts/                 copy_images.py, build_offline_artifacts.py
└── tests/test_demo.py       python -m pytest demo/tests -q
```

| Endpoint | Chức năng |
|---|---|
| `GET /api/context` | Chế độ, run, số khách/sản phẩm, giá trị K, mô hình khả dụng và mô hình bị ẩn kèm lý do |
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

Bản đóng gói Docker (`Dockerfile`, `docker-compose.yml`) chưa được kiểm tra với chế độ v2.
