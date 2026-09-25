# Demo shop thời trang H&M — hướng dẫn chạy

Web mô phỏng shop thời trang trên dữ liệu **H&M Personalized Fashion Recommendations**.
Chỉ suy diễn (inference-only) trên checkpoint đã huấn luyện; demo không train lại mô hình
và không sửa code huấn luyện (`src/`, `scripts/`), chỉ import hàm từ đó.

Có ba màn hình:

| Màn hình | Nội dung |
|---|---|
| **Khách hàng mới** | Gợi ý **rule-based** (lọc theo lựa chọn + độ phổ biến trong train). Đây **không phải** mô hình NeuMF và được gắn nhãn rõ trên UI. |
| **Admin kiểm thử mô hình** | Chọn khách hàng có test item: lịch sử mua (train), Top-K của từng model (so sánh 2 model), rank của test item, Hit@K và NDCG@K. |
| **Dashboard** | Chỉ đọc từ file kết quả đã chạy; file thiếu thì hiện lệnh cần chạy. |

## 1. Chuẩn bị dữ liệu và huấn luyện

Từ thư mục `neumf_project_v2/`:

```bash
pip install -r requirements.txt
# data/raw/hm/ cần có: transactions_train.csv, articles.csv, customers.csv (tuỳ chọn, để lọc theo tuổi)
python scripts/run_all.py --config configs/hm_subset.yaml
```

Demo dựng lại pipeline theo `configs/hm_subset.yaml` (mặc định) rồi **đối chiếu với
`outputs/experiments/<run_tag>/metadata.json`** (số users, items, interactions, train/val/test).
Nếu lệch thì server báo lỗi thay vì nạp checkpoint sai ID. Vì vậy config phải đúng với config
đã dùng để train run đó (đặc biệt là `nrows` và `k_core`).

## 2. Sinh file offline cho dashboard (khuyến nghị)

```bash
python demo/scripts/build_offline_artifacts.py            # hoặc --run-tag hm_xxx
```

Script ghi vào `demo/artifacts/<run_tag>/`:

- `results_per_user.csv`: rank của test item cho từng user và từng model, dùng cho biểu đồ phân phối rank và cho test.
- `popularity_bias.csv`: top 20 item được gợi ý nhiều nhất trong top-K của toàn bộ test user, kèm độ phổ biến trong train.

Cuối script, trung bình per-user được so với `results_primary.csv` của run; nếu lệch quá 1e-6 thì script dừng với lỗi.
Nếu đã có `outputs/tables/<run_tag>/results_per_user.csv`, demo ưu tiên đọc file đó.

Bảng multi-seed (mean ± std) chỉ hiện khi đã chạy:

```bash
python scripts/04_multi_seed.py --config configs/hm_subset.yaml --seeds 42 2024 2025 2026 3407 7
python scripts/06_aggregate_seeds.py --config-name hm --seeds 42 2024 2025 2026 3407 7
```

## 3. Ảnh sản phẩm (tuỳ chọn)

Ảnh H&M có dạng `images/<3 chữ số đầu>/<article_id 10 chữ số>.jpg`. Script dưới đây chỉ copy
ảnh của các item trong catalog sau k-core:

```bash
HM_IMAGES_DIR=/duong/dan/h-and-m/images python demo/scripts/copy_images.py
```

Item không có ảnh sẽ hiển thị placeholder SVG ghi `product_type_name`.

## 4. Chạy web

```bash
python -m uvicorn demo.backend.main:app --port 8000 --host 127.0.0.1
```

Mở **http://localhost:8000**. Lần gọi đầu mất khoảng 10 giây để dựng lại dữ liệu; sau đó được cache theo run_tag.
Sau khi train xong run mới, gọi `curl -X POST http://localhost:8000/api/reload` để nạp run mới nhất mà không cần khởi động lại.

## Biến môi trường

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `DEMO_CONFIG` | `configs/hm_subset.yaml` | Config dùng để dựng lại dữ liệu và kiến trúc model |
| `DEMO_RUN_TAG` | run `hm_*` mới nhất có `results.json` và checkpoint | Cố định run muốn demo |
| `HM_IMAGES_DIR` | (không có) | Thư mục `images/` gốc của H&M, dùng cho `copy_images.py` |
| `DEMO_IMAGES_DIR` | `demo/static/images` | Thư mục ảnh mà server phục vụ |

Mapping khu vực mua sắm → `index_group_name`, cửa sổ độ phổ biến và ngưỡng nhóm tuổi nằm trong
`demo/backend/onboarding_config.yaml`.

## Cách chấm (khớp protocol huấn luyện)

- Split: temporal leave-one-out (`src/data_pipeline/splitting.py`), có kiểm tra `assert_disjoint_splits`.
- Candidates của test item: toàn bộ item trừ các item user đã có trong train ∪ validation, tạo bằng chính
  `build_full_ranking_records` (`src/evaluation/full_ranking.py`). Rank dùng `rank_positive` với cùng tie-break seed.
- Model neural được xếp hạng bằng logit (không qua sigmoid, vì sigmoid float32 bão hoà sẽ tạo tie giả).
- `HR@K = 1[rank ≤ K]`, `NDCG@K = 1/log2(rank+1)` nếu rank ≤ K; K chỉ được chọn trong `evaluation.k_values`.
- MostPopular = số user mua item trong train. **BPR-MF bị ẩn** vì `scripts/03_run_experiment.py` chưa lưu
  checkpoint BPR. Nếu sau này có `outputs/checkpoints/<run_tag>/bpr.npz` (mảng `P`, `Q`) thì demo tự hiện.

## Cấu trúc

```
demo/
  backend/
    main.py                FastAPI app, phục vụ frontend/
    routes.py              các endpoint /api/*
    data_context.py        nạp dữ liệu, split, ánh xạ ID, checkpoint; đối chiếu metadata của run
    inference.py           full ranking cho một user (model + MostPopular/BPR)
    onboarding.py          gợi ý rule-based cho khách hàng mới
    onboarding_config.yaml
    metrics_io.py          đọc file kết quả cho dashboard
  frontend/                index.html, app.js, style.css (HTML tĩnh + Chart.js qua CDN)
  scripts/                 build_offline_artifacts.py, copy_images.py
  tests/test_demo.py       python -m pytest demo/tests -q
```

### API

| Endpoint | Chức năng |
|---|---|
| `GET /api/context` | Dataset, lát cắt, run_tag, số users/items, k_values, model khả dụng và model bị ẩn kèm lý do |
| `POST /api/reload` | Xoá cache, nạp run mới nhất |
| `GET /api/users/buckets` | Ngưỡng nhóm ít / trung bình / nhiều giao dịch train |
| `GET /api/users/search?q=&bucket=&limit=` | Tìm user có test item theo tiền tố customer_id |
| `GET /api/users/random?bucket=` | User ngẫu nhiên có test item |
| `GET /api/users/{customer_id}/history` | Item trong train kèm ngày mua, sắp theo thời gian |
| `GET /api/users/{customer_id}/recommend?model=&k=` | Top-K, rank test item, số candidates, Hit/NDCG@K |
| `GET /api/onboarding/options` | Lựa chọn lấy từ articles.csv (theo catalog sau k-core) |
| `POST /api/onboarding/recommend` | Gợi ý rule-based cho khách hàng mới |
| `GET /api/dashboard` | Mọi khối dashboard, kèm file nguồn và run_tag |
| `GET /api/image/{article_id}` | Ảnh sản phẩm hoặc placeholder SVG |

## Dừng server

`Ctrl+C` trong terminal đang chạy uvicorn, hoặc trên Windows: `netstat -ano | findstr :8000` rồi `taskkill /PID <pid> /F`.
