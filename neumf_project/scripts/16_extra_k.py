"""Chỉ số bổ sung ở K khác (mặc định K = 20) tính lại từ hạng đã lưu — mô tả, không dùng để kết luận.

    python scripts/16_extra_k.py            # hoặc --k 20

Đọc cột `ranks` (hạng của từng item đúng trong Full Ranking) của outputs/final/seed*/results_per_user.csv do
11_final.py ghi (và outputs/final/extension/seed*/ nếu có). Không chấm lại mô hình nào, không truy cập test lần nữa:
mọi số @K đều suy ra được từ hạng đã có. Ra: outputs/final/extra_k<K>.csv (trung bình ± độ lệch chuẩn qua seed).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluation.metrics import multi_ranking_metrics  # noqa: E402

NAMES = ("NDCG", "Recall", "HR", "Precision")


def metrics_at_k(per_user: pd.DataFrame, k: int) -> pd.DataFrame:
    """Một dòng mỗi (model, seed, user) -> các chỉ số @k tính từ cột ranks."""
    rows = []
    for r in per_user.itertuples(index=False):
        ranks = [int(x) for x in str(r.ranks).split(";") if x != ""]
        m = multi_ranking_metrics(ranks, k)
        rows.append({"model": r.model, "seed": r.seed, "user": r.user, **{f"{n}@{k}": m[n] for n in NAMES}})
    return pd.DataFrame(rows)


def summarize(final_dir: Path, k: int) -> pd.DataFrame:
    files = sorted(final_dir.glob("seed*/results_per_user.csv")) + sorted(final_dir.glob("extension/seed*/results_per_user.csv"))
    if not files:
        raise SystemExit(f"Chưa có results_per_user.csv trong {final_dir} — chạy 11_final.py trước.")
    per = metrics_at_k(pd.concat([pd.read_csv(f) for f in files], ignore_index=True), k)
    cols = [f"{n}@{k}" for n in NAMES]
    by_seed = per.groupby(["model", "seed"])[cols].mean()
    out = by_seed.groupby("model").agg(["mean", "std"])
    out.columns = [f"{m}_{s}" for m, s in out.columns]
    return out.sort_values(f"NDCG@{k}_mean", ascending=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--k", type=int, default=20)
    ap.add_argument("--final-dir", default=str(PROJECT_ROOT / "outputs" / "final"))
    args = ap.parse_args()
    final_dir = Path(args.final_dir)
    out = summarize(final_dir, args.k)
    out.to_csv(final_dir / f"extra_k{args.k}.csv")
    pd.set_option("display.width", 200)
    print(out.round(5))


if __name__ == "__main__":
    main()
