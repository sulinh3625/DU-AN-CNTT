"""Tải một lần ảnh Amazon Beauty của các sản phẩm demo đang dùng về demo/static/images/amazon/<asin>.jpg.

Sau khi tải, demo phục vụ ảnh từ máy (qua /api/image/<asin>?dataset=amazon), không kéo trực tiếp từ Amazon lúc trình
bày. Ảnh nào tải lỗi thì demo vẽ ô thay thế. Chạy lại chỉ tải phần còn thiếu.
Chạy từ neumf_project/ (cần mạng):
    python demo/scripts/download_amazon_images.py
"""
from __future__ import annotations

import argparse
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from demo.backend.data_context import DataContext  # noqa: E402
from demo.backend.routes import amazon_image_path  # noqa: E402

HEADERS = {"User-Agent": "Mozilla/5.0 (neumf-demo image cache)"}


def fetch(asin: str, url: str, timeout: float) -> str:
    """Tải một ảnh; thử lại bằng máy chủ ảnh hiện tại của Amazon nếu link 2014 lỗi. Trả về 'ok', 'skip' hoặc 'fail'."""
    dst = Path(amazon_image_path(asin))
    if dst.exists() and dst.stat().st_size > 0:
        return "skip"
    name = url.rsplit("/images/I/", 1)[-1]
    for u in (url, f"https://m.media-amazon.com/images/I/{name}"):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=HEADERS), timeout=timeout) as r:
                data = r.read()
            if data[:3] == b"\xff\xd8\xff":  # chỉ giữ tệp JPEG thật
                tmp = dst.with_suffix(".part")
                tmp.write_bytes(data)
                tmp.replace(dst)
                return "ok"
        except OSError:
            time.sleep(0.5)
    return "fail"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--timeout", type=float, default=15)
    args = ap.parse_args()

    arts = DataContext(load_customers=False, dataset="amazon").articles
    todo = [(a, u) for a, u in zip(arts["article_id"], arts["image_src"]) if a and u]
    Path(amazon_image_path("x")).parent.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(args.workers) as ex:
        res = list(ex.map(lambda au: fetch(au[0], au[1], args.timeout), todo))
    n = {k: res.count(k) for k in ("ok", "skip", "fail")}
    print(f"{len(arts)} sản phẩm, {len(todo)} có link ảnh: tải mới {n['ok']}, đã có {n['skip']}, lỗi {n['fail']} "
          f"(dùng ô thay thế). Thư mục: {Path(amazon_image_path('x')).parent}")


if __name__ == "__main__":
    main()
