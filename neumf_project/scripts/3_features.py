"""Dựng cache đặc trưng cho giao thức v2 (chạy một lần, khoảng 2–3 phút; không đụng nhãn kiểm thử nào):

    python scripts/21_build_features.py
    python run.py amazon-data          # Amazon Beauty (NEUMF_CONFIG=configs/amazon.yaml), kèm 02_prepare_data.py

H&M (configs/v2.yaml):
- data/processed/hm/catalog_v2.npz      thuộc tính sản phẩm + vector mô tả văn bản (articles.csv)
- data/processed/hm/daily_sales_v2.npz  số giao dịch mỗi (sản phẩm, ngày) của toàn bộ transactions_train.csv
Amazon (configs/amazon.yaml, src/data_pipeline/adapters/amazon.py): catalog (thương hiệu, danh mục, nhóm giá, văn bản
title + description), số đánh giá mỗi (sản phẩm, ngày) của toàn bộ file đánh giá, bảng thông tin sản phẩm cho demo —
đường dẫn ở mục features của cấu hình.

Đặc trưng thời gian tại ngày t chỉ đọc các ngày < t (src/data_pipeline/features.py), nên cache chứa cả giai đoạn kiểm
thử cũng không làm rò rỉ: mô hình chỉ được hỏi tại mốc cắt của từng giai đoạn.
"""
from __future__ import annotations

import argparse
import time

import v2_common as V
from src.data_pipeline.features import (build_catalog, build_daily_sales, save_catalog,  # noqa: E402
                                        save_daily_sales)

PROJECT_ROOT = V.PROJECT_ROOT
RAW = PROJECT_ROOT / "data" / "raw" / "hm"
OUT = PROJECT_ROOT / "data" / "processed" / "hm"
CATALOG = OUT / "catalog_v2.npz"
SALES = OUT / "daily_sales_v2.npz"


def build_amazon(text_dim: int, t0: float) -> None:
    from src.data_pipeline.adapters.amazon import build_features

    f = V.CFG["features"]
    cat, ds, info = build_features(PROJECT_ROOT / V.CFG["samples"]["dev"], PROJECT_ROOT / f["meta"], V.CFG["day0"],
                                   text_dim=text_dim)
    out = PROJECT_ROOT / f["catalog"]
    out.parent.mkdir(parents=True, exist_ok=True)
    save_catalog(cat, out)
    save_daily_sales(ds, PROJECT_ROOT / f["sales"])
    info.to_csv(PROJECT_ROOT / f["items"], index=True)
    known = {c: int((cat.cats[:, k] > 0).sum()) for k, c in enumerate(("thương hiệu", "danh mục 1", "danh mục 2",
                                                                        "danh mục 3", "giá"))}
    print(f"catalog Amazon: {len(cat.article_ids):,} sản phẩm, có " + ", ".join(f"{c} {n:,}" for c, n in known.items())
          + f"; văn bản {cat.text.shape[1]} chiều | đánh giá: {ds.counts.sum():,} trong {ds.n_days} ngày tính từ "
          f"{V.CFG['day0']} ({time.time() - t0:.0f}s)", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--text-dim", type=int, default=64)
    args = ap.parse_args()
    t0 = time.time()
    if V.DATASET == "amazon":
        build_amazon(args.text_dim, t0)
        return
    OUT.mkdir(parents=True, exist_ok=True)
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
