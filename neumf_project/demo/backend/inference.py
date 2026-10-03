"""Xếp hạng full-ranking cho một user, đúng protocol của src/evaluation/full_ranking.py."""
from __future__ import annotations

import numpy as np
import torch

from src.evaluation.full_ranking import EvalRecord
from src.evaluation.metrics import multi_ranking_metrics
from src.evaluation.ranking_utils import deterministic_tie_key

MAX_PAIRS_PER_BATCH = 400_000
SCORE_KIND = {"MostPopular": "lượt mua train", "BPR-MF": "điểm", "ItemKNN": "Σ sim", "UserKNN": "Σ sim",
              "LateFusion-GMF-MLP": "điểm trộn", "LateFusion-BPR-MLP": "điểm trộn", "LateFusion-F": "điểm trộn",
              "MostPopular-Recent": "giao dịch gần đây", "Content": "cosine"}
METRIC_NAMES = ("HR", "NDCG", "Recall", "Precision")


@torch.no_grad()
def score_items(ctx, model_name: str, users: np.ndarray) -> np.ndarray:
    """Điểm của mọi item cho từng user (chỉ mạng PyTorch), shape (len(users), n_items).

    Trả logit float32 (giống evaluate_torch_model); không qua sigmoid vì sigmoid float32 bão hoà tạo tie giả
    và làm lệch rank.
    """
    users = np.asarray(users, dtype=np.int64)
    n_items = ctx.n_items
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


def eval_record(ctx, u: int) -> EvalRecord:
    """Record của user u, cùng quy tắc với build_full_ranking_records_multi: ứng viên = item trong pool (final:
    item của train ∪ val; explore: mọi item) trừ item đã mua, luôn giữ đủ các item đích."""
    positives = np.asarray(sorted(ctx.target_items[u]), dtype=np.int64)
    mask = ctx.pool_mask.copy()
    mask[positives] = True
    seen = ctx.seen_pos[u] - set(positives.tolist())
    if seen:
        mask[np.fromiter(seen, dtype=np.int64)] = False
    return EvalRecord(u, int(positives[0]), np.arange(ctx.n_items, dtype=np.int64)[mask], positives)


def candidate_scores(ctx, model_name: str, u: int, record, all_items_row=None) -> np.ndarray:
    """Điểm trên record.candidates. Mô hình không phải mạng PyTorch chấm thẳng trên candidates (đúng như
    evaluate_score_function — late fusion chuẩn hoá min-max trên chính tập này). all_items_row: hàng điểm mọi item
    của mạng PyTorch đã tính sẵn theo lô."""
    scorer = ctx.scorers.get(model_name)
    if scorer is not None:
        return np.asarray(scorer.score_items(u, record.candidates), dtype=np.float64)
    if all_items_row is None:
        all_items_row = score_items(ctx, model_name, np.array([u]))[0]
    return all_items_row[record.candidates]


def rank_from_scores(ctx, u: int, scores: np.ndarray, top_k: int, record) -> dict:
    """scores: điểm trên record.candidates (cùng thứ tự). Thứ hạng = điểm giảm dần, hoà thì theo khoá tất định."""
    cand = record.candidates
    tie = deterministic_tie_key(u, cand, ctx.tie_seed)
    order = np.lexsort((tie, -np.asarray(scores, dtype=np.float64)))
    ranked = cand[order]
    pos_idx = np.flatnonzero(np.isin(ranked, record.positives))
    ranks = pos_idx + 1
    metrics = {f"{name}@{k}": v for k in ctx.k_values
               for name, v in multi_ranking_metrics(ranks, k).items() if name in METRIC_NAMES}
    return {
        "ranks": [int(r) for r in ranks],
        "item_rank": {int(ranked[i]): int(i) + 1 for i in pos_idx},
        "n_candidates": int(len(cand)),
        "metrics": metrics,
        "top_items": ranked[:top_k].tolist(),
        "top_scores": [float(s) for s in np.asarray(scores)[order[:top_k]]],
    }


def recommend(ctx, model_name: str, u: int, k: int) -> dict:
    record = eval_record(ctx, u)
    res = rank_from_scores(ctx, u, candidate_scores(ctx, model_name, u, record), k, record)
    targets = set(int(i) for i in record.positives)
    items = [
        {**ctx.item_info(i), "rank": r, "score": s, "is_target": i in targets}
        for r, (i, s) in enumerate(zip(res["top_items"], res["top_scores"]), start=1)
    ]
    target_rows = sorted(({**ctx.item_info(i), "rank": r} for i, r in res["item_rank"].items()),
                         key=lambda t: t["rank"])
    return {
        "model": model_name,
        "k": k,
        "score_kind": SCORE_KIND.get(model_name, "logit"),
        "items": items,
        "targets": target_rows,
        "evaluation": {"rank": min(res["ranks"]), "ranks": res["ranks"], "n_candidates": res["n_candidates"],
                       "metrics": res["metrics"]},
    }
