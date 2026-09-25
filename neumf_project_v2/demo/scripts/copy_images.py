"""Copy ảnh H&M của các item trong catalog (sau k-core, theo run đang dùng) sang demo/static/images.

Cấu trúc ảnh gốc: <HM_IMAGES_DIR>/<3 chữ số đầu>/<article_id 10 chữ số>.jpg
Chạy từ neumf_project_v2/:
    HM_IMAGES_DIR=/path/to/h-and-m/images python demo/scripts/copy_images.py
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from demo.backend.data_context import DataContext  # noqa: E402
from demo.backend.routes import IMAGES_DIR  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.environ.get("HM_IMAGES_DIR"), help="Thư mục images/ của H&M (hoặc đặt HM_IMAGES_DIR)")
    ap.add_argument("--dst", default=IMAGES_DIR)
    ap.add_argument("--run-tag", default=None)
    args = ap.parse_args()
    if not args.src or not Path(args.src).is_dir():
        raise SystemExit("Cần --src hoặc biến môi trường HM_IMAGES_DIR trỏ tới thư mục images/ của H&M.")

    ctx = DataContext(args.run_tag, load_customers=False)
    src, dst = Path(args.src), Path(args.dst)
    copied = missing = 0
    for aid in ctx.article_ids:
        rel = Path(aid[:3]) / f"{aid}.jpg"
        if not (src / rel).exists():
            missing += 1
            continue
        (dst / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src / rel, dst / rel)
        copied += 1
    print(f"Đã copy {copied}/{len(ctx.article_ids)} ảnh vào {dst}; {missing} item không có ảnh (sẽ dùng placeholder).")


if __name__ == "__main__":
    main()
