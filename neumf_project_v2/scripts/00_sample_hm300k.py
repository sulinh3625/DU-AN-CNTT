"""00_sample_hm.py — Lấy mẫu ~300k dòng H&M trải trên TOÀN BỘ 2 năm giao dịch.

Lấy ngẫu nhiên (tất định theo seed) một tập KHÁCH HÀNG và giữ toàn bộ lịch sử
mua của họ, cho tới khi đủ ~--rows dòng.

Không lấy ngẫu nhiên theo DÒNG: 300k dòng rải trên 1,36 triệu khách thì mỗi
khách chỉ còn ~0,2 giao dịch và lọc k-core=5 xoá sạch dữ liệu (đã đo: ngẫu nhiên
theo dòng hay cách đều theo dòng đều còn 0 tương tác sau k-core).

Output giữ nguyên cột và ID gốc của transactions_train.csv (demo tra tên/ảnh
sản phẩm theo article_id gốc), giữ nguyên thứ tự dòng gốc (tie-break thời gian).

Chạy (~2-3 phút, đọc CSV theo lô nên RAM thấp):
    python scripts/00_sample_hm300k.py
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH_DEFAULT = PROJECT_ROOT / "data" / "raw" / "hm" / "transactions_train.csv"
OUT_PATH_DEFAULT = PROJECT_ROOT / "data" / "processed" / "hm" / "hm300k_transactions.csv"


def main():
    ap = argparse.ArgumentParser(description="Lấy mẫu H&M theo khách hàng, trải trên toàn bộ thời gian")
    ap.add_argument("--raw-path", default=str(RAW_PATH_DEFAULT))
    ap.add_argument("--out-path", default=str(OUT_PATH_DEFAULT))
    ap.add_argument("--rows", type=int, default=300_000, help="Số dòng mục tiêu (xấp xỉ)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--chunksize", type=int, default=2_000_000)
    args = ap.parse_args()

    raw_path, out_path = Path(args.raw_path), Path(args.out_path)
    t0 = time.time()

    # Lượt 1: đếm số giao dịch của từng khách.
    print(f"[1/2] Đếm giao dịch theo khách: {raw_path}")
    counts = None
    for chunk in pd.read_csv(raw_path, usecols=["customer_id"], dtype={"customer_id": "string"}, chunksize=args.chunksize):
        c = chunk["customer_id"].value_counts()
        counts = c if counts is None else counts.add(c, fill_value=0)
    counts = counts.astype(np.int64).sort_index()  # sort để thứ tự không phụ thuộc thứ tự đọc
    print(f"      {int(counts.sum()):,} dòng | {len(counts):,} khách | {time.time() - t0:.0f}s")

    # Chọn khách theo hoán vị tất định cho tới khi đủ số dòng.
    perm = np.random.default_rng(args.seed).permutation(len(counts))
    n_take = int(np.searchsorted(np.cumsum(counts.to_numpy()[perm]), args.rows)) + 1
    chosen = set(counts.index[perm[:n_take]])
    print(f"      Chọn {len(chosen):,} khách ({100 * len(chosen) / len(counts):.2f}%)")

    # Lượt 2: giữ toàn bộ dòng của các khách đã chọn, đúng thứ tự gốc.
    print("[2/2] Trích giao dịch của các khách đã chọn")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    parts = [
        chunk[chunk["customer_id"].isin(chosen)]
        for chunk in pd.read_csv(raw_path, dtype={"customer_id": "string", "article_id": "string"}, chunksize=args.chunksize)
    ]
    sample = pd.concat(parts, ignore_index=True)
    sample.to_csv(out_path, index=False)

    # Kiểm tra trùng lặp.
    exact_dup = int(sample.duplicated().sum())
    pair_dup = int(len(sample) - len(sample.drop_duplicates(["customer_id", "article_id"])))
    assert sample["customer_id"].nunique() == len(chosen), "thiếu khách đã chọn"
    assert len(sample) == int(counts[list(chosen)].sum()), "không giữ đủ lịch sử của khách đã chọn"

    print("\nHoàn tất lấy mẫu H&M.")
    print(f"  Số dòng          : {len(sample):,}")
    print(f"  Khách / sản phẩm : {sample['customer_id'].nunique():,} / {sample['article_id'].nunique():,}")
    print(f"  Khoảng thời gian : {sample['t_dat'].min()} -> {sample['t_dat'].max()}")
    print(f"  Dòng trùng hệt nhau (cùng khách, SP, ngày, giá, kênh): {exact_dup:,} "
          f"({100 * exact_dup / len(sample):.1f}%) — mua nhiều đơn vị, được gộp ở bước aggregate")
    print(f"  Dòng lặp cặp (khách, SP) tổng cộng: {pair_dup:,} — gộp thành 1 tương tác/cặp khi tiền xử lý")
    print(f"  Output           : {out_path} ({out_path.stat().st_size / 1e6:.1f} MB) | {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
