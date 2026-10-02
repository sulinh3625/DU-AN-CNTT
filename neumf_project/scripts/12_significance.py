"""Kiểm định theo PREREG mục 6/8 trên kết quả test của scripts/11_final.py.

    python scripts/12_significance.py

Per-user NDCG@10 trung bình qua các seed -> Wilcoxon signed-rank + paired bootstrap 95% CI (10.000 lần, seed 0),
hiệu chỉnh Holm trên họ 8 so sánh cố định. "Tốt hơn" chỉ khi p_Holm < 0,05, CI không chứa 0 và chênh lệch tương đối
>= 5%. Ra: outputs/final/summary.csv (mean ± std qua seed) và outputs/final/significance.csv.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

PROJECT_ROOT = Path(__file__).resolve().parents[1]
METRIC = "NDCG@10"
# Họ so sánh cố định, đăng ký trước khi chạy test (PREREG mục 8, loop 14).
COMPARISONS = [
    ("NeuMF-Pretrained", "BPR-MF"), ("NeuMF-Pretrained", "MostPopular"), ("NeuMF-Pretrained", "GMF"),
    ("NeuMF-Pretrained", "MLP"), ("NeuMF-Pretrained", "NeuMF-Scratch"),
    ("NeuMF-Scratch", "BPR-MF"), ("NeuMF-Scratch", "GMF"), ("NeuMF-Scratch", "MLP"),
]


def holm(p) -> np.ndarray:
    p = np.asarray(p, dtype=float)
    order = np.argsort(p)
    adj = np.maximum.accumulate((len(p) - np.arange(len(p))) * p[order]).clip(max=1.0)
    out = np.empty_like(adj)
    out[order] = adj
    return out


def bootstrap_ci(diff, n=10_000, seed=0):
    rng = np.random.default_rng(seed)
    means = np.array([diff[rng.integers(0, len(diff), len(diff))].mean() for _ in range(n)])
    return np.percentile(means, [2.5, 97.5])


def analyse(final_dir: Path):
    per = pd.concat([pd.read_csv(f) for f in sorted(final_dir.glob("seed*/results_per_user.csv"))], ignore_index=True)
    seeds = sorted(per["seed"].unique())
    metrics = [c for c in ("NDCG@10", "Recall@10", "HR@10", "Precision@10", "NDCG@5") if c in per.columns]
    by_seed = per.groupby(["model", "seed"])[metrics].mean()
    summary = by_seed.groupby("model").agg(["mean", "std"])
    summary.columns = [f"{m}_{s}" for m, s in summary.columns]
    user_mean = per.groupby(["model", "user"])[METRIC].mean().unstack("model")  # user x model, TB qua seed

    rows = []
    for a, b in COMPARISONS:
        diff = (user_mean[a] - user_mean[b]).to_numpy()
        ma, mb = user_mean[a].mean(), user_mean[b].mean()
        lo, hi = bootstrap_ci(diff)
        rows.append(dict(A=a, B=b, mean_A=ma, mean_B=mb, diff=diff.mean(), rel_diff=(ma - mb) / mb,
                         ci_low=lo, ci_high=hi, n_users=len(diff),
                         p_wilcoxon=wilcoxon(diff).pvalue if np.any(diff) else 1.0))
    sig = pd.DataFrame(rows)
    sig["p_holm"] = holm(sig["p_wilcoxon"])
    better = (sig["p_holm"] < 0.05) & ((sig["ci_low"] > 0) | (sig["ci_high"] < 0)) & (sig["rel_diff"].abs() >= 0.05)
    sig["verdict"] = np.where(~better, "không khác biệt có ý nghĩa", np.where(sig["diff"] > 0, "A tốt hơn", "B tốt hơn"))
    return seeds, summary.sort_values(f"{METRIC}_mean", ascending=False), sig


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--final-dir", default=str(PROJECT_ROOT / "outputs" / "final"))
    final_dir = Path(ap.parse_args().final_dir)
    seeds, summary, sig = analyse(final_dir)
    summary.to_csv(final_dir / "summary.csv")
    sig.to_csv(final_dir / "significance.csv", index=False)
    pd.set_option("display.width", 200)
    print(f"Seed: {seeds}\n\n{summary.round(5)}\n\n{sig.round(5).to_string(index=False)}")


if __name__ == "__main__":
    main()
