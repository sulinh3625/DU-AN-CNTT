"""Tính offline cho dashboard demo, ghi vào demo/artifacts/<run_tag>/:

- results_per_user.csv : rank của test item theo từng model (full ranking, loại train ∪ val).
- popularity_bias.csv  : top 20 item được gợi ý nhiều nhất trong top-K của toàn bộ test user.

Cuối cùng so sánh trung bình per-user với results_primary.csv của run (do
scripts/03_run_experiment.py sinh ra) và báo lỗi nếu lệch > 1e-6.

Chạy từ neumf_project_v2/:  python demo/scripts/build_offline_artifacts.py [--run-tag hm_xxx]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from demo.backend import inference  # noqa: E402
from demo.backend.data_context import EXPERIMENTS_DIR, DataContext  # noqa: E402
from demo.backend.metrics_io import ARTIFACTS_DIR  # noqa: E402

TOP_N_BIAS = 20
USER_CHUNK = 256
TOLERANCE = 1e-6


def per_user_results(ctx: DataContext, top_k: int):
    rows, top_lists = [], {m: [] for m in ctx.available_models}
    users = ctx.test_users
    for s in range(0, len(users), USER_CHUNK):
        chunk = users[s:s + USER_CHUNK]
        scores = {m: inference.score_items(ctx, m, chunk) for m in ctx.available_models}
        for j, u in enumerate(chunk):
            u = int(u)
            record = inference.eval_record(ctx, u)
            for m in ctx.available_models:
                r = inference.rank_from_scores(ctx, u, scores[m][j], top_k, record=record)
                rows.append({"customer_id": ctx.customer_ids[u], "user_idx": u, "model": m,
                             "test_item": record.positive_item, "rank": r["rank"],
                             "n_candidates": r["n_candidates"], **r["metrics"]})
                top_lists[m].append(r["top_items"])
        print(f"  {min(s + USER_CHUNK, len(users))}/{len(users)} users", end="\r")
    print()
    return pd.DataFrame(rows), top_lists


def popularity_bias(ctx: DataContext, top_lists: dict, top_k: int) -> pd.DataFrame:
    pop_rank = pd.Series(ctx.train_item_counts).rank(ascending=False, method="min").astype(int)
    out = []
    for m, lists in top_lists.items():
        counts = pd.Series(np.concatenate(lists)).value_counts().head(TOP_N_BIAS)
        for pos, (item, n) in enumerate(counts.items(), start=1):
            info = ctx.item_info(int(item))
            out.append({
                "model": m, "position": pos, "item_idx": int(item), "article_id": info["article_id"],
                "prod_name": info["prod_name"], "product_type_name": info["product_type_name"],
                "n_users_recommended": int(n), "share_of_test_users": n / len(lists),
                "train_count": info["train_count"], "train_popularity_rank": int(pop_rank[int(item)]),
                "is_head": info["is_head"], "top_k": top_k,
            })
    return pd.DataFrame(out)


def check_against_run(ctx: DataContext, per_user: pd.DataFrame) -> list[str]:
    official = pd.read_csv(EXPERIMENTS_DIR / ctx.run_tag / "results_primary.csv", index_col=0)
    errors = []
    means = per_user.groupby("model")[[c for c in official.columns if c in per_user.columns]].mean()
    for m, row in means.iterrows():
        for metric, v in row.items():
            ref = official.loc[m, metric]
            status = "OK" if abs(v - ref) <= TOLERANCE else "LỆCH"
            print(f"  {m:17s} {metric:8s} demo={v:.6f} run={ref:.6f} {status}")
            if status != "OK":
                errors.append(f"{m} {metric}: {v} vs {ref}")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-tag", default=None)
    args = ap.parse_args()

    ctx = DataContext(args.run_tag, load_customers=False)
    top_k = max(ctx.k_values)
    out_dir = ARTIFACTS_DIR / ctx.run_tag
    out_dir.mkdir(parents=True, exist_ok=True)

    per_user, top_lists = per_user_results(ctx, top_k)
    per_user.to_csv(out_dir / "results_per_user.csv", index=False)
    popularity_bias(ctx, top_lists, top_k).to_csv(out_dir / "popularity_bias.csv", index=False)
    print(f"Đã ghi {out_dir}")

    print("So sánh trung bình per-user với results_primary.csv của run:")
    errors = check_against_run(ctx, per_user)
    if errors:
        raise SystemExit("Metric demo không khớp kết quả run:\n" + "\n".join(errors))


if __name__ == "__main__":
    main()
