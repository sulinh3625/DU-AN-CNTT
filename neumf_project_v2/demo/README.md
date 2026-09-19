# Demo NeuMF — hướng dẫn chạy

Giao diện thực nghiệm suy diễn (inference-only), đúng thiết kế 3 tầng ở mục 3.7
báo cáo (`Report DACNTT/content/C3.tex`). Không huấn luyện lại mô hình — chỉ
nạp checkpoint đã có trong `outputs/checkpoints/`.

## Chạy

Từ thư mục `neumf_project_v2/`:

```bash
pip install -r requirements.txt
python -m uvicorn demo.backend.main:app --port 8000 --host 127.0.0.1
```

Mở trình duyệt tại **http://localhost:8000**.

Lần đầu chọn mỗi bộ dữ liệu sẽ mất vài giây (server tái tạo pipeline tiền xử
lý để suy ra đúng ánh xạ ID -> checkpoint), các lần sau tức thời vì đã cache
trong bộ nhớ tiến trình.

## Yêu cầu trước khi chạy

Cần đã chạy xong ít nhất một lần các run tag sau (đã có sẵn trong repo này):

- `outputs/checkpoints/dataco_20260918_verify/` (GMF, MLP, EarlyFusion, NeuMF-Scratch, NeuMF-Pretrained)
- `outputs/checkpoints/hm_20260918_verify/`

Nếu đổi sang run tag khác, sửa `DATASETS` trong `demo/backend/main.py`.

## Cấu trúc

- `backend/main.py` — FastAPI, expose `/api/*` (xem Bảng 3.9 báo cáo) + phục vụ luôn `frontend/` tại `/`.
- `frontend/index.html` — trang tĩnh, gọi API bằng `fetch`, vẽ biểu đồ so sánh mô hình bằng Chart.js.

## Dừng server

Nhấn `Ctrl+C` trong terminal đang chạy uvicorn, hoặc trên Windows tìm PID đang
lắng nghe cổng 8000 (`netstat -ano | findstr :8000`) rồi `taskkill /PID <pid> /F`.
