"""00_sample_hm.py — Lấy mẫu khách hàng theo khối bucket từ transactions_train.csv gốc (31,8 triệu dòng).

Lấy mẫu THEO KHÁCH HÀNG trải đủ 2018-09-20 → 2020-09-22: băm customer_id (hash key cố định) vào --buckets bucket, chia
dãy bucket thành các KHỐI liên tiếp, không giao nhau, mỗi khối vừa đủ --target-rows dòng, rồi giữ toàn bộ lịch sử mua
của khách trong khối được chọn. Đọc file theo chunk 2 lượt nên RAM chỉ khoảng 0,5 GB. File ra giữ nguyên cột như file
gốc.

    python run.py sample-hm                    # khối 0 -> data/processed/hm/mau_phat_trien.csv
    python run.py sample-hm --block 2          # khối 2 -> data/processed/hm/mau_kiem_dinh.csv
    python scripts/00_sample_hm.py --block 1 --output <file>

- Khối 0: mẫu phát triển (trước đây hm500k) — tinh chỉnh, chỉ dùng tập xác thực.
- Khối 1: trước đây hm500k_b — đã bị mở trong lúc phát triển nên KHÔNG dùng nữa; phải truyền --output tường minh.
- Khối 2: mẫu kiểm định — chỉ dùng cho lần đánh giá cuối của giao thức v2, tập kiểm thử mở đúng một lần.
Cùng hash key, cùng --buckets và --target-rows thì mọi máy ra đúng cùng các khối, và các khối không có khách chung.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

COLUMNS = ["t_dat", "customer_id", "article_id", "price", "sales_channel_id"]
DEFAULT_OUTPUT = {0: "data/processed/hm/mau_phat_trien.csv", 2: "data/processed/hm/mau_kiem_dinh.csv"}


def bucket_of(customer_ids: pd.Series, n_buckets: int, hash_key: str) -> np.ndarray:
    """Stable hash -> bucket; same key gives the same customers on every run and machine."""
    h = pd.util.hash_pandas_object(customer_ids.astype(str), index=False, hash_key=hash_key)
    return (h.to_numpy() % np.uint64(n_buckets)).astype(np.int64)


def select_buckets(counts: np.ndarray, target_rows: int, block: int = 0) -> tuple[int, int]:
    """(bucket đầu, số bucket) của khối thứ `block`: các khối nối tiếp nhau từ bucket 0, không giao nhau, mỗi khối gồm
    số bucket ít nhất để đủ target_rows dòng (khối chạm cuối mảng thì lấy hết phần còn lại). block=0 / block=1 trùng
    mẫu hm500k / hm500k_b cũ."""
    if block < 0:
        raise SystemExit(f"--block phải >= 0, nhận {block}")

    def n_needed(start):
        if start >= len(counts):
            raise SystemExit(f"Hết bucket: không còn bucket cho khối {block} — giảm --target-rows hoặc tăng --buckets")
        return min(int(np.searchsorted(np.cumsum(counts[start:]), target_rows)) + 1, len(counts) - start)

    start = 0
    for _ in range(block):
        start += n_needed(start)
    return start, n_needed(start)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", default="data/raw/hm/transactions_train.csv")
    ap.add_argument("--output", default=None,
                    help="mặc định: khối 0 -> mau_phat_trien.csv, khối 2 -> mau_kiem_dinh.csv; khối khác phải truyền")
    ap.add_argument("--target-rows", type=int, default=500_000)
    ap.add_argument("--buckets", type=int, default=100_000, help="Sampling granularity (customers per bucket ~ customers/buckets)")
    ap.add_argument("--hash-key", default="0123456789123456", help="16 chars; change it to draw a different sample")
    ap.add_argument("--chunksize", type=int, default=2_000_000)
    ap.add_argument("--block", type=int, default=0,
                    help="khối bucket: 0 = mẫu phát triển, 1 = đã mở lúc phát triển (không dùng), 2 = mẫu kiểm định")
    args = ap.parse_args()
    if len(args.hash_key) != 16:
        raise SystemExit("--hash-key must be exactly 16 characters")
    if args.output is None:
        if args.block not in DEFAULT_OUTPUT:
            raise SystemExit(f"--block {args.block} không có file ra mặc định — truyền --output tường minh")
        args.output = DEFAULT_OUTPUT[args.block]
    if args.block == 1:
        print("CẢNH BÁO: khối 1 (hm500k_b cũ) đã bị mở trong lúc phát triển — không dùng cho đánh giá cuối.",
              flush=True)

    t0 = time.time()
    counts = np.zeros(args.buckets, dtype=np.int64)
    for chunk in pd.read_csv(args.input, usecols=["customer_id"], dtype={"customer_id": "string"}, chunksize=args.chunksize):
        counts += np.bincount(bucket_of(chunk["customer_id"], args.buckets, args.hash_key), minlength=args.buckets)
    total = int(counts.sum())
    b0, n_sel = select_buckets(counts, args.target_rows, args.block)
    expected = int(counts[b0:b0 + n_sel].sum())
    print(f"Pass 1: {total:,} rows in {time.time() - t0:.0f}s -> block {args.block}: keep buckets [{b0}, {b0 + n_sel}) "
          f"of {args.buckets} ({100 * n_sel / args.buckets:.2f}% of customers), expected {expected:,} rows", flush=True)

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
