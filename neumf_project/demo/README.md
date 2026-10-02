# Demo shop thời trang H&M — hướng dẫn chạy

Web mô phỏng shop thời trang trên dữ liệu **H&M Personalized Fashion Recommendations**.
Chỉ suy diễn (inference-only) trên checkpoint đã huấn luyện; demo không train lại mô hình
và không sửa code huấn luyện (`src/`, `scripts/`), chỉ import hàm từ đó.

## Hai chế độ

| Chế độ | Mặc định khi | Mô hình nạp | Sản phẩm đích |
|---|---|---|---|
| **`final`** | có `outputs/final/seed42/` kèm checkpoint | Đúng các mô hình của **đánh giá cuối** (Chương 4): GMF, MLP, NeuMF-Scratch, NeuMF-Pretrained, BPR-MF, MostPopular với cấu hình riêng từng mô hình (`results.json`), đã huấn luyện lại trên train ∪ val; thêm late fusion GMF + MLP, BPR-MF + MLP, ItemKNN, UserKNN nếu `audit/best_configs.json` có tham số mở rộng | Mọi món khách mua **lần đầu** trong giai đoạn test (có thể nhiều món mỗi khách) |
| **`explore`** | không có checkpoint đánh giá cuối, hoặc `DEMO_MODE=explore` | Run khám phá leave-one-out `hm500k_seed42` (cấu hình mặc định, chưa tune) | Item validation (khoá test) hoặc test, theo run |

Ở chế độ `final`, số per-user trên demo khớp `outputs/final/seed42/results_per_user.csv` (số của Chương 4 — có test tự
động). Đây là **hiển thị lại** kết quả đã chấm, không phải một lần chấm test mới.

Có ba màn hình:

| Màn hình | Nội dung |
|---|---|
| **Khách hàng mới** | Gợi ý **rule-based** (lọc theo lựa chọn + độ phổ biến trong dữ liệu huấn luyện). Đây **không phải** mô hình NeuMF và được gắn nhãn rõ trên UI. |
| **Admin kiểm thử mô hình** | Chọn khách hàng có sản phẩm đích: lịch sử mua (đúng dữ liệu mô hình đã học), Top-K của từng mô hình (so sánh 2 mô hình), hạng của từng sản phẩm đích, HR@K, NDCG@K, Recall@K. Chế độ `final` có thêm thẻ **"10 khách tương đồng nhất" (UserKNN)**: độ tương đồng, số món mua chung, láng giềng đã mua sản phẩm đích nào. |
| **Dashboard** | Chỉ đọc từ file kết quả đã chạy (chế độ `final`: `outputs/final/*.csv` — bảng kết quả, kiểm định họ chính và họ mở rộng, phân tầng, beyond-accuracy, Sampled-99, độ trễ); file thiếu thì hiện lệnh cần chạy. |

## 1. Chuẩn bị

Từ thư mục `neumf_project/`:

```bash
pip install -r requirements.txt
# data/raw/hm/ cần có: transactions_train.csv; articles.csv (tên/loại sản phẩm), customers.csv (lọc tuổi cho khách mới)
python run.py sample-hm      # tạo data/processed/hm/hm500k_transactions.csv
```

Chế độ `final` dùng checkpoint đã có trong repo (`outputs/final/seed42/`, sinh bởi `python run.py final`). Demo dựng
lại dữ liệu theo `configs/hm500k_global.yaml` rồi **đối chiếu** số user test và số item ứng viên với `results.json`;
lệch thì server báo lỗi thay vì nạp checkpoint với ánh xạ ID sai.

Chế độ `explore` cần run khám phá (`python run.py all` → `hm500k_seed42`); demo dựng lại theo `configs/hm500k.yaml` và
đối chiếu `outputs/experiments/<run_tag>/metadata.json`.

Mô hình lai của đề tài là NeuMF (GMF + MLP). `articles.csv` chỉ dùng để hiển thị tên/loại sản phẩm và cho
gợi ý rule-based của khách mới — không mô hình nào trong demo học từ thuộc tính sản phẩm.

## 2. File offline cho dashboard chế độ `explore` (tuỳ chọn)

```bash
python demo/scripts/build_offline_artifacts.py            # hoặc --run-tag hm500k_seed42
```

Script (luôn ở chế độ `explore`) ghi vào `demo/artifacts/<run_tag>/`:

- `results_per_user.csv`: rank của item đích cho từng user và từng model, dùng cho biểu đồ phân phối rank và cho test.
- `popularity_bias.csv`: top 20 item được gợi ý nhiều nhất trong top-K của toàn bộ user, kèm độ phổ biến trong train.

Cuối script, trung bình per-user được so với `results_primary.csv` của run; nếu lệch quá 1e-6 thì script dừng với lỗi.
Chế độ `final` không cần bước này (dashboard đọc thẳng `outputs/final/`).

## 3. Ảnh sản phẩm (tuỳ chọn)

Ảnh H&M có dạng `images/<3 chữ số đầu>/<article_id 10 chữ số>.jpg`. Script dưới đây chỉ copy
ảnh của các item trong catalog sau k-core:

```bash
HM_IMAGES_DIR=/duong/dan/h-and-m/images python demo/scripts/copy_images.py
```

Item không có ảnh sẽ hiển thị placeholder SVG ghi `product_type_name`.

## 4. Chạy web

```bash
python run.py demo            # hoặc: python -m demo
```

Mở **http://localhost:8000**. Lần gọi đầu mất khoảng 10–15 giây để dựng lại dữ liệu và ItemKNN/UserKNN; sau đó được
cache. Sau khi chạy lại đánh giá cuối, gọi `curl -X POST http://localhost:8000/api/reload` để nạp lại mà không cần khởi
động lại. Mở thẳng một khách để chụp ảnh minh hoạ:
`http://localhost:8000/?user=<customer_id>&compare=1&a=NeuMF-Pretrained&b=BPR-MF#admin`.

## Biến môi trường

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `DEMO_MODE` | tự chọn (`final` nếu có checkpoint đánh giá cuối) | `final` hoặc `explore` |
| `DEMO_FINAL_SEED` | `42` | Seed của đánh giá cuối được nạp (`outputs/final/seed<N>/`) |
| `DEMO_CONFIG` | `configs/hm500k.yaml` | Config của chế độ `explore` |
| `DEMO_RUN_TAG` | run `<tên config>_*` mới nhất có `results.json` và checkpoint | Cố định run của chế độ `explore` |
| `HM_IMAGES_DIR` | (không có) | Thư mục `images/` gốc của H&M, dùng cho `copy_images.py` |
| `DEMO_IMAGES_DIR` | `demo/static/images` | Thư mục ảnh mà server phục vụ |

Mapping khu vực mua sắm → `index_group_name`, cửa sổ độ phổ biến và ngưỡng nhóm tuổi nằm trong
`demo/backend/onboarding_config.yaml`.

## Cách chấm (khớp protocol đánh giá)

- **Chế độ `final`:** chia theo một mốc thời gian chung (`global_temporal_split`, `refit_data`); lịch sử hiển thị =
  train ∪ val (đúng dữ liệu mô hình đã học; ngày hiển thị là ngày mua đầu, luôn trước mốc test); sản phẩm đích = các cặp
  test của khách; candidates = item có trong train ∪ val trừ món khách đã mua — cùng quy tắc với
  `build_full_ranking_records_multi` (có test so sánh trực tiếp với record của đánh giá cuối).
- **Chế độ `explore`:** temporal leave-one-out; item đích = đúng tập mà bảng kết quả của run dùng (`evaluated_on` trong
  `metadata.json`): validation nếu run chưa `--final` (khoá test), test nếu đã `--final`; candidates = mọi item trừ item
  đã mua.
- Thứ hạng: điểm giảm dần, hoà điểm phá bằng cùng khoá tất định (`deterministic_tie_key`, tie-break seed của config).
  Mạng PyTorch xếp bằng logit (không qua sigmoid, vì sigmoid float32 bão hoà sẽ tạo tie giả). Mô hình không phải mạng
  (MostPopular, BPR-MF, ItemKNN, UserKNN, late fusion) chấm bằng `score_items` trên chính tập candidates — late fusion
  chuẩn hoá min-max trên tập này, đúng như `scripts/17_extension.py`.
- HR@K, NDCG@K, Recall@K, Precision@K theo `multi_ranking_metrics` (nhiều sản phẩm đích); K chỉ được chọn trong
  `evaluation.k_values`.
- Logit tính lại trên CPU có thể lệch ~1e-7 so với GPU lúc đánh giá cuối: vài cặp gần như hoà điểm ở hạng rất sâu
  (trên 100) có thể đổi chỗ, không ảnh hưởng chỉ số @K.

## Cấu trúc

```
demo/
  backend/
    main.py                FastAPI app, phục vụ frontend/
    routes.py              các endpoint /api/*
    data_context.py        hai chế độ final/explore: dữ liệu, split, ánh xạ ID, checkpoint, láng giềng UserKNN
    inference.py           full ranking cho một user (mạng PyTorch và mô hình score_items)
    onboarding.py          gợi ý rule-based cho khách hàng mới
    onboarding_config.yaml
    metrics_io.py          đọc file kết quả cho dashboard (final: outputs/final/; explore: outputs/tables/ + artifacts)
  frontend/                index.html, app.js, style.css (HTML tĩnh + Chart.js qua CDN)
  scripts/                 build_offline_artifacts.py, copy_images.py
  tests/test_demo.py       python -m pytest demo/tests -q
```

### API

| Endpoint | Chức năng |
|---|---|
| `GET /api/context` | Chế độ, dataset, run_tag, số users/items, k_values, mô hình khả dụng (kể cả mở rộng) và mô hình bị ẩn kèm lý do |
| `POST /api/reload` | Xoá cache, nạp lại |
| `GET /api/users/buckets` | Ngưỡng nhóm ít / trung bình / nhiều giao dịch |
| `GET /api/users/search?q=&bucket=&limit=` | Tìm user có sản phẩm đích theo tiền tố customer_id |
| `GET /api/users/random?bucket=` | User ngẫu nhiên có sản phẩm đích |
| `GET /api/users/{customer_id}/history` | Sản phẩm mô hình đã học kèm ngày mua, sắp theo thời gian |
| `GET /api/users/{customer_id}/recommend?model=&k=` | Top-K, hạng từng sản phẩm đích, số candidates, HR/NDCG/Recall@K |
| `GET /api/users/{customer_id}/neighbors?k=10` | Top-K khách tương đồng theo UserKNN, số món mua chung, láng giềng đã mua sản phẩm đích nào (chế độ `final`) |
| `GET /api/onboarding/options` | Lựa chọn lấy từ articles.csv (theo catalog sau k-core) |
| `POST /api/onboarding/recommend` | Gợi ý rule-based cho khách hàng mới |
| `GET /api/dashboard` | Mọi khối dashboard, kèm file nguồn |
| `GET /api/image/{article_id}` | Ảnh sản phẩm hoặc placeholder SVG |

## Dừng server

`Ctrl+C` trong terminal đang chạy uvicorn, hoặc trên Windows: `netstat -ano | findstr :8000` rồi `taskkill /PID <pid> /F`.
