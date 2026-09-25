"""Xếp hạng full-ranking cho một user, đúng protocol của src/evaluation/full_ranking.py."""
from __future__ import annotations

import numpy as np
import pandas as pd
import torch

from src.evaluation.full_ranking import build_full_ranking_records
from src.evaluation.metrics import hr_at_k, ndcg_at_k
from src.evaluation.ranking_utils import deterministic_tie_key, rank_positive

MAX_PAIRS_PER_BATCH = 400_000


@torch.no_grad()
def score_items(ctx, model_name: str, users: np.ndarray) -> np.ndarray:
    """Điểm của mọi item cho từng user, shape (len(users), n_items).

    Model neural trả logit float32 (giống evaluate_torch_model); không qua sigmoid vì
    sigmoid float32 bão hoà tạo tie giả và làm lệch rank.
    """
    users = np.asarray(users, dtype=np.int64)
    n_items = ctx.n_items
    if model_name == "MostPopular":
        return np.tile(ctx.train_item_counts.astype(np.float64), (len(users), 1))
    if model_name == "BPR-MF":
        if ctx.bpr is None:
            raise KeyError(model_name)
        P, Q = ctx.bpr
        return P[users] @ Q.T
    model = ctx.models[model_name]
    out = np.empty((len(users), n_items), dtype=np.float32)
    items = torch.arange(n_items, dtype=torch.long)
    chunk = max(1, MAX_PAIRS_PER_BATCH // n_items)
    for s in range(0, len(users), chunk):
        u = torch.from_numpy(users[s:s + chunk])
        uu = u.repeat_interleave(n_items)
        ii = items.repeat(len(u))
        out[s:s + chunk] = model(uu, ii).numpy().reshape(len(u), n_items)
    return out


def eval_record(ctx, u: int):
    """EvalRecord của test item, tạo bằng chính build_full_ranking_records (loại train ∪ val)."""
    eval_df = pd.DataFrame({"user": [u], "item": [ctx.test_item[u]]})
    return build_full_ranking_records(eval_df, ctx.n_items, ctx.train_val_pos)[0]


def rank_from_scores(ctx, u: int, scores_row: np.ndarray, top_k: int, record=None) -> dict:
    record = record or eval_record(ctx, u)
    cand = record.candidates
    scores = scores_row[cand]
    rank = rank_positive(scores, cand, record.positive_item, u, ctx.tie_seed)
    tie = deterministic_tie_key(u, cand, ctx.tie_seed)
    order = np.lexsort((tie, -np.asarray(scores, dtype=np.float64)))[:top_k]
    metrics = {}
    for k in ctx.k_values:
        metrics[f"HR@{k}"] = hr_at_k(rank, k)
        metrics[f"NDCG@{k}"] = ndcg_at_k(rank, k)
    return {
        "rank": int(rank),
        "n_candidates": int(len(cand)),
        "metrics": metrics,
        "top_items": cand[order].tolist(),
        "top_scores": [float(s) for s in scores[order]],
    }


def recommend(ctx, model_name: str, u: int, k: int) -> dict:
    scores = score_items(ctx, model_name, np.array([u]))[0]
    res = rank_from_scores(ctx, u, scores, k)
    test_item = ctx.test_item[u]
    items = [
        {**ctx.item_info(i), "rank": r, "score": s, "is_test_item": i == test_item}
        for r, (i, s) in enumerate(zip(res["top_items"], res["top_scores"]), start=1)
    ]
    return {
        "model": model_name,
        "k": k,
        "score_kind": "số khách mua trong train" if model_name == "MostPopular" else "logit",
        "items": items,
        "evaluation": {k_: res[k_] for k_ in ("rank", "n_candidates", "metrics")},
    }
