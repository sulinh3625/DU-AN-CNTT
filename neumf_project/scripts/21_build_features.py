"""Dựng cache đặc trưng cho giao thức v2 (chạy một lần, khoảng 2–3 phút; không đụng nhãn kiểm thử nào):

    python scripts/21_build_features.py

- data/processed/hm/catalog_v2.npz      thuộc tính sản phẩm + vector mô tả văn bản (articles.csv)
- data/processed/hm/daily_sales_v2.npz  số giao dịch mỗi (sản phẩm, ngày) của toàn bộ transactions_train.csv

Đặc trưng thời gian tại ngày t chỉ đọc các ngày < t (src/data_pipeline/features.py), nên cache chứa cả giai đoạn kiểm
thử cũng không làm rò rỉ: mô hình chỉ được hỏi tại mốc cắt của từng giai đoạn.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_pipeline.features import (build_catalog, build_daily_sales, save_catalog,  # noqa: E402
                                        save_daily_sales)

RAW = PROJECT_ROOT / "data" / "raw" / "hm"
OUT = PROJECT_ROOT / "data" / "processed" / "hm"
CATALOG = OUT / "catalog_v2.npz"
SALES = OUT / "daily_sales_v2.npz"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--text-dim", type=int, default=64)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    cat = build_catalog(RAW / "articles.csv", text_dim=args.text_dim)
    save_catalog(cat, CATALOG)
    print(f"catalog: {len(cat.article_ids):,} sản phẩm, {len(cat.cardinalities)} thuộc tính, văn bản "
          f"{cat.text.shape[1]} chiều ({time.time() - t0:.0f}s)", flush=True)
    ds = build_daily_sales(RAW / "transactions_train.csv", cat)
    save_daily_sales(ds, SALES)
    sold = int((ds.first_day < ds.n_days).sum())
    print(f"doanh số: {ds.counts.sum():,} giao dịch, {ds.n_days} ngày, {sold:,} sản phẩm từng bán, "
          f"{ds.counts.nnz:,} cặp (sản phẩm, ngày) ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
