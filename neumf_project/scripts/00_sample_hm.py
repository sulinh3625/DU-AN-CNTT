"""00_sample_hm.py — Tạo bộ dữ liệu mặc định hm500k từ transactions_train.csv gốc (31,8 triệu dòng).

Lấy mẫu THEO KHÁCH HÀNG trải đủ 2018-09-20 → 2020-09-22: giữ toàn bộ lịch sử mua của một tập
khách chọn ngẫu nhiên cố định (hash customer_id), sao cho tổng khoảng --target-rows dòng.
Đọc file theo chunk 2 lượt nên RAM chỉ khoảng 0,5 GB. File ra giữ nguyên cột như file gốc.

    python run.py sample-hm            (= python scripts/00_sample_hm.py)
    python scripts/00_sample_hm.py --holdout   # mẫu kiểm thử độc lập hm500k_b: khách KHÁC hẳn hm500k

--holdout lấy các bucket ngay sau các bucket của hm500k (cùng hash key, cùng cỡ) nên hai tập khách không giao nhau;
mẫu này chỉ dùng cho lần đánh giá cuối của giao thức v2 (PREREG_v2.md), không dùng để tinh chỉnh.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

COLUMNS = ["t_dat", "customer_id", "article_id", "price", "sales_channel_id"]


def bucket_of(customer_ids: pd.Series, n_buckets: int, hash_key: str) -> np.ndarray:
    """Stable hash -> bucket; same key gives the same customers on every run and machine."""
    h = pd.util.hash_pandas_object(customer_ids.astype(str), index=False, hash_key=hash_key)
    return (h.to_numpy() % np.uint64(n_buckets)).astype(np.int64)


def select_buckets(counts: np.ndarray, target_rows: int, holdout: bool = False) -> tuple[int, int]:
    """(bucket đầu, số bucket) của mẫu: các bucket đầu tiên đủ target_rows dòng; với holdout là đoạn kế tiếp ngay sau
    đoạn đó (không giao nhau), cũng đủ target_rows dòng."""
    def n_needed(c):
        return min(int(np.searchsorted(np.cumsum(c), target_rows)) + 1, len(c))
    n_main = n_needed(counts)
    if not holdout:
        return 0, n_main
    if n_main >= len(counts):
        raise SystemExit("Không còn bucket cho mẫu holdout — giảm --target-rows")
    return n_main, n_needed(counts[n_main:])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", default="data/raw/hm/transactions_train.csv")
    ap.add_argument("--output", default="data/processed/hm/hm500k_transactions.csv")
    ap.add_argument("--target-rows", type=int, default=500_000)
    ap.add_argument("--buckets", type=int, default=100_000, help="Sampling granularity (customers per bucket ~ customers/buckets)")
    ap.add_argument("--hash-key", default="0123456789123456", help="16 chars; change it to draw a different sample")
    ap.add_argument("--chunksize", type=int, default=2_000_000)
    ap.add_argument("--holdout", action="store_true",
                    help="mẫu thứ hai, khách không trùng mẫu mặc định (ra hm500k_b_transactions.csv)")
    args = ap.parse_args()
    if len(args.hash_key) != 16:
        raise SystemExit("--hash-key must be exactly 16 characters")
    if args.holdout and args.output == ap.get_default("output"):
        args.output = "data/processed/hm/hm500k_b_transactions.csv"

    t0 = time.time()
    counts = np.zeros(args.buckets, dtype=np.int64)
    for chunk in pd.read_csv(args.input, usecols=["customer_id"], dtype={"customer_id": "string"}, chunksize=args.chunksize):
        counts += np.bincount(bucket_of(chunk["customer_id"], args.buckets, args.hash_key), minlength=args.buckets)
    total = int(counts.sum())
    b0, n_sel = select_buckets(counts, args.target_rows, args.holdout)
    expected = int(counts[b0:b0 + n_sel].sum())
    print(f"Pass 1: {total:,} rows in {time.time() - t0:.0f}s -> keep buckets [{b0}, {b0 + n_sel}) of {args.buckets} "
          f"({100 * n_sel / args.buckets:.2f}% of customers), expected {expected:,} rows", flush=True)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    written, customers, t_min, t_max, first = 0, set(), None, None, True
    for chunk in pd.read_csv(args.input, usecols=COLUMNS, chunksize=args.chunksize,
                             dtype={"customer_id": "string", "article_id": "string"}):
        b = bucket_of(chunk["customer_id"], args.buckets, args.hash_key)
        keep = chunk[(b >= b0) & (b < b0 + n_sel)]
        if keep.empty:
            continue
        keep[COLUMNS].to_csv(out, mode="w" if first else "a", header=first, index=False)
        first = False
        written += len(keep)
        customers.update(keep["customer_id"].tolist())
        lo, hi = keep["t_dat"].min(), keep["t_dat"].max()
        t_min = lo if t_min is None else min(t_min, lo)
        t_max = hi if t_max is None else max(t_max, hi)

    print(f"Pass 2: wrote {written:,} rows, {len(customers):,} customers, dates {t_min} -> {t_max} "
          f"to {out} ({out.stat().st_size / 1e6:.0f} MB) in {time.time() - t0:.0f}s total")
    assert written == expected, "row count changed between passes (input file modified?)"


if __name__ == "__main__":
    main()
