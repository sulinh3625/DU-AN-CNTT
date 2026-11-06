"""Tải một lần ảnh H&M của các sản phẩm demo đang dùng về demo/static/images/<3 số đầu>/<article_id>.jpg.

Dùng khi không có thư mục images/ gốc của cuộc thi (copy_images.py cần HM_IMAGES_DIR) và tài khoản Kaggle chưa chấp
nhận luật cuộc thi. Nguồn: bộ dữ liệu Kaggle tbierhance/hm-fashion-images-squared-896 — ảnh gốc của cuộc thi, đệm
vuông 896x896. Tải từng tệp qua Kaggle API bị giới hạn (429), nên script gọi API đúng một lần để lấy đường dẫn của tệp
zip (2,4 GB), đọc mục lục zip rồi chỉ tải phần byte của các ảnh cần (khoảng 100 MB). Cần Kaggle API đã đăng nhập
(~/.kaggle). Chạy lại chỉ tải phần còn thiếu; sản phẩm không có ảnh thì demo vẽ ô thay thế.
Chạy từ neumf_project/ (cần mạng):
    python demo/scripts/download_hm_images.py
"""
from __future__ import annotations

import argparse
import io
import struct
import sys
import time
import urllib.request
import zipfile
import zlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from demo.backend.data_context import DataContext  # noqa: E402
from demo.backend.routes import IMAGES_DIR  # noqa: E402

OWNER, SLUG = "tbierhance", "hm-fashion-images-squared-896"


def get_range(url: str, start: int, end: int) -> bytes:
    """Byte [start, end) của url (HTTP Range)."""
    req = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end - 1}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


class RangeFile(io.RawIOBase):
    """Tệp chỉ đọc trên HTTP Range — đủ để zipfile đọc mục lục ở cuối tệp zip mà không tải cả tệp."""
    def __init__(self, url: str, size: int):
        self.url, self.size, self.pos = url, size, 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = {0: off, 1: self.pos + off, 2: self.size + off}[whence]
        return self.pos

    def read(self, n=-1):
        end = self.size if n is None or n < 0 else min(self.size, self.pos + n)
        if end <= self.pos:
            return b""
        data = get_range(self.url, self.pos, end)
        self.pos += len(data)
        return data


def zip_url() -> tuple[str, int]:
    """Một lần gọi Kaggle API: đường dẫn có chữ ký của tệp zip (sau chuyển hướng) và kích thước."""
    from kaggle.api.kaggle_api_extended import KaggleApi
    from kagglesdk.datasets.types.dataset_api_service import ApiDownloadDatasetRequest
    api = KaggleApi()
    api.authenticate()
    with api.build_kaggle_client() as k:
        req = ApiDownloadDatasetRequest()
        req.owner_slug, req.dataset_slug = OWNER, SLUG
        r = k.datasets.dataset_api_client.download_dataset(req)
    r.close()  # chỉ cần đường dẫn, không đọc thân
    return r.url, int(r.headers["Content-Length"])


def member_bytes(url: str, info: zipfile.ZipInfo) -> bytes:
    """Nội dung một mục zip: đọc local header (30 byte + tên + extra) rồi giải nén nếu cần."""
    slack = 30 + len(info.filename.encode()) + 1024  # extra của local header có thể dài hơn bản trong mục lục
    raw = get_range(url, info.header_offset, info.header_offset + slack + info.compress_size)
    n, m = struct.unpack("<HH", raw[26:30])
    data = raw[30 + n + m:30 + n + m + info.compress_size]
    return data if info.compress_type == zipfile.ZIP_STORED else zlib.decompressobj(-15).decompress(data)


def fetch(url: str, info: zipfile.ZipInfo | None, dst: Path) -> str:
    """'ok', 'skip' (đã có), 'missing' (nguồn không có ảnh) hoặc 'fail'."""
    if dst.exists() and dst.stat().st_size > 0:
        return "skip"
    if info is None:
        return "missing"
    for attempt in range(3):
        try:
            data = member_bytes(url, info)
            if data[:3] != b"\xff\xd8\xff":  # chỉ giữ tệp JPEG thật
                return "fail"
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.with_suffix(".part").write_bytes(data)
            dst.with_suffix(".part").replace(dst)
            return "ok"
        except OSError:
            time.sleep(1 + attempt)
    return "fail"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--dst", default=IMAGES_DIR)
    args = ap.parse_args()

    aids = DataContext(load_customers=False).articles["article_id"].tolist()
    dst = Path(args.dst)
    t0 = time.time()
    url, size = zip_url()
    index = {Path(i.filename).stem: i for i in zipfile.ZipFile(RangeFile(url, size)).infolist()}
    print(f"Mục lục zip: {len(index)} ảnh ({time.time() - t0:.0f} giây).")
    with ThreadPoolExecutor(args.workers) as ex:
        res = list(ex.map(lambda a: fetch(url, index.get(a), dst / a[:3] / f"{a}.jpg"), aids))
    n = {k: res.count(k) for k in ("ok", "skip", "missing", "fail")}
    print(f"{len(aids)} sản phẩm: tải mới {n['ok']}, đã có {n['skip']}, nguồn không có ảnh {n['missing']}, lỗi "
          f"{n['fail']} (dùng ô thay thế; chạy lại để thử tiếp). {time.time() - t0:.0f} giây. Thư mục: {dst}")


if __name__ == "__main__":
    main()
