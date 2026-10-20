"""Chạy web demo:  python -m demo  (từ thư mục neumf_project/)

Cổng mặc định 8000; nếu cổng đang bận (thường do một demo cũ chưa tắt) thì tự dùng cổng trống kế tiếp và in địa chỉ."""
import socket

import uvicorn


def free_port(start: int = 8000, tries: int = 20) -> int:
    for port in range(start, start + tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise SystemExit(f"Các cổng {start}–{start + tries - 1} đều bận; tắt demo cũ rồi chạy lại.")


port = free_port()
if port != 8000:
    print(f"[demo] cổng 8000 đang bận (có thể một demo cũ còn chạy), dùng cổng {port}.")
print(f"[demo] mở http://localhost:{port} (lần nạp đầu mất khoảng 30 giây; Ctrl+C để dừng)")
uvicorn.run("demo.backend.main:app", host="127.0.0.1", port=port)
