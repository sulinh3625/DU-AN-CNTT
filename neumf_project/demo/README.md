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
  `customers.csv` (đặc trưng; lọc tuổi cho khách mới).
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
| **Khách hàng mới** | Gợi ý **theo luật** (lọc theo lựa chọn của khách + độ phổ biến trong dữ liệu huấn luyện). **Không phải** mô hình — có nhãn rõ trên giao diện. |
| **Admin kiểm thử mô hình** | Chọn khách có sản phẩm đích: lịch sử mua (đúng dữ liệu mô hình đã học), top-K của một mô hình hoặc so sánh hai mô hình, hạng của từng sản phẩm đích, HR@K, NDCG@K, Recall@K. Sản phẩm mới có nhãn **"Mới"**. Thẻ **"10 khách tương đồng nhất"** (UserKNN): độ tương đồng, số món mua chung, láng giềng đã mua sản phẩm đích nào. |
| **Dashboard** | Chỉ đọc file kết quả đã chạy (chế độ v2: `outputs/v2/final/*.csv` — kết quả 5 seed, kiểm định họ 10 so sánh, NDCG@10 theo nhóm sản phẩm cũ/mới, độ phủ và tỉ lệ sản phẩm mới, ablation NeuMF-F). Thiếu file thì hiện lệnh cần chạy. |

## 4. Chế độ

Chọn bằng biến môi trường `DEMO_MODE`; không đặt thì tự chọn theo thứ tự v2 → final → explore (chế độ đầu tiên có
checkpoint).

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
- HR@K, NDCG@K, Recall@K, Precision@K tính với nhiều sản phẩm đích mỗi khách; K chọn trong các giá trị của cấu hình.
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

Mapping khu vực mua sắm → `index_group_name`, cửa sổ độ phổ biến và ngưỡng nhóm tuổi của màn hình Khách hàng mới nằm
trong `demo/backend/onboarding_config.yaml`.

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
│   ├── data_context.py      ba chế độ: dựng dữ liệu, ánh xạ ID, nạp checkpoint, láng giềng UserKNN
│   ├── inference.py         xếp hạng toàn bộ ứng viên cho một khách
│   ├── onboarding.py        gợi ý theo luật cho khách hàng mới (+ onboarding_config.yaml)
│   └── metrics_io.py        đọc file kết quả cho dashboard
├── frontend/                index.html, app.js, style.css (HTML tĩnh + Chart.js qua CDN)
├── scripts/                 copy_images.py, build_offline_artifacts.py
└── tests/test_demo.py       python -m pytest demo/tests -q
```

| Endpoint | Chức năng |
|---|---|
| `GET /api/context` | Chế độ, run, số khách/sản phẩm, giá trị K, mô hình khả dụng và mô hình bị ẩn kèm lý do |
| `POST /api/reload` | Xoá cache, nạp lại |
| `GET /api/users/buckets` | Ngưỡng nhóm khách ít / trung bình / nhiều giao dịch |
| `GET /api/users/search?q=&bucket=&limit=` | Tìm khách có sản phẩm đích theo tiền tố `customer_id` |
| `GET /api/users/random?bucket=` | Khách ngẫu nhiên có sản phẩm đích |
| `GET /api/users/{customer_id}/history` | Lịch sử mua mô hình đã học, sắp theo thời gian |
| `GET /api/users/{customer_id}/recommend?model=&k=` | Top-K, hạng từng sản phẩm đích, số ứng viên, HR/NDCG/Recall@K |
| `GET /api/users/{customer_id}/neighbors?k=10` | Khách tương đồng nhất theo UserKNN, số món mua chung, láng giềng đã mua sản phẩm đích nào |
| `GET /api/onboarding/options` | Lựa chọn cho màn hình Khách hàng mới (lấy từ `articles.csv`) |
| `POST /api/onboarding/recommend` | Gợi ý theo luật cho khách hàng mới |
| `GET /api/dashboard` | Các khối của dashboard, kèm file nguồn |
| `GET /api/image/{article_id}` | Ảnh sản phẩm hoặc ô thay thế |

Bản đóng gói Docker (`Dockerfile`, `docker-compose.yml`) chưa được kiểm tra với chế độ v2.
