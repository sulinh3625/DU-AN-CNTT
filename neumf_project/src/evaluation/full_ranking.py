from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import torch

from .metrics import multi_ranking_metrics
from .ranking_utils import rank_positives, deterministic_tie_key


@dataclass
class EvalRecord:
    user: int
    positive_item: int
    candidates: np.ndarray
    # Chia theo mốc thời gian chung: user có thể có nhiều item đúng. None = chỉ positive_item.
    positive_items: np.ndarray | None = None

    @property
    def positives(self) -> np.ndarray:
        if self.positive_items is None:
            return np.array([self.positive_item], dtype=np.int64)
        return self.positive_items


def build_full_ranking_records_multi(eval_df, n_items: int, seen_positive_sets, item_pool=None) -> list[EvalRecord]:
    """Một record cho mỗi user, gom mọi item đúng của user trong eval_df.

    candidates = item trong item_pool (mặc định: mọi item) trừ item đã thấy (seen);
    luôn giữ đủ các item đúng.
    """
    all_items = np.arange(n_items, dtype=np.int64)
    pool = np.ones(n_items, dtype=bool)
    if item_pool is not None:
        pool[:] = False
        pool[np.asarray(item_pool, dtype=np.int64)] = True
    records = []
    for u, g in eval_df.groupby("user", sort=True):
        u = int(u)
        positives = np.unique(g["item"].to_numpy(dtype=np.int64))
        seen = set(seen_positive_sets[u]) - set(positives.tolist())
        mask = pool.copy()
        mask[positives] = True
        if seen:
            mask[np.fromiter(seen, dtype=np.int64)] = False
        records.append(EvalRecord(u, int(positives[0]), all_items[mask], positives))
    return records


def _empty_metric_lists(k_values, include_redundant):
    out = {f"HR@{k}": [] for k in k_values}
    out.update({f"NDCG@{k}": [] for k in k_values})
    if include_redundant:
        out.update({f"Precision@{k}": [] for k in k_values})
        out.update({f"Recall@{k}": [] for k in k_values})
    return out


def _per_user_row(record, cand, ranks, metrics) -> dict:
    """Một dòng results_per_user: số candidate, rank từng item đúng, metric của riêng user này."""
    return {"user": int(record.user), "n_candidates": int(len(cand)), "n_positives": int(len(ranks)),
            "ranks": ";".join(str(int(r)) for r in ranks), **{name: vals[-1] for name, vals in metrics.items()}}


def _append(metrics, ranks, k_values, include_redundant):
    for k in k_values:
        m = multi_ranking_metrics(ranks, k)
        metrics[f"HR@{k}"].append(m["HR"])
        metrics[f"NDCG@{k}"].append(m["NDCG"])
        if include_redundant:
            metrics[f"Precision@{k}"].append(m["Precision"])
            metrics[f"Recall@{k}"].append(m["Recall"])


@torch.no_grad()
def evaluate_torch_model(model, records, k_values, device="cpu", batch_size=16384, tie_seed=2026, include_redundant=False, return_topk=False,
                         per_user: list | None = None):
    """Evaluate PyTorch model with flattened batched scoring.

    Tránh gọi model một lần cho từng user; toàn bộ candidate pairs được flatten
    rồi score theo batch lớn, sau đó cắt lại theo offsets để tính rank từng user.
    """
    model.eval()
    metrics = _empty_metric_lists(k_values, include_redundant)
    max_k = max(k_values)
    recommendations = {} if return_topk else None
    if not records:
        summary = {name: float("nan") for name in metrics}
        return (summary, recommendations) if return_topk else summary

    lengths = np.fromiter((len(r.candidates) for r in records), dtype=np.int64, count=len(records))
    offsets = np.concatenate(([0], np.cumsum(lengths)))
    total = int(offsets[-1])
    users_flat = np.empty(total, dtype=np.int64)
    items_flat = np.empty(total, dtype=np.int64)
    for idx, record in enumerate(records):
        a, b = int(offsets[idx]), int(offsets[idx + 1])
        users_flat[a:b] = record.user
        items_flat[a:b] = record.candidates

    score_flat = np.empty(total, dtype=np.float32)
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        users = torch.from_numpy(users_flat[start:end]).long().to(device)
        items = torch.from_numpy(items_flat[start:end]).long().to(device)
        score_flat[start:end] = model(users, items).detach().cpu().numpy()

    for idx, record in enumerate(records):
        a, b = int(offsets[idx]), int(offsets[idx + 1])
        cand = items_flat[a:b]
        scores = score_flat[a:b]
        ranks = rank_positives(scores, cand, record.positives, record.user, tie_seed)
        _append(metrics, ranks, k_values, include_redundant)
        if per_user is not None:
            per_user.append(_per_user_row(record, cand, ranks, metrics))
        if return_topk:
            tie = deterministic_tie_key(record.user, cand, tie_seed)
            order = np.lexsort((tie, -scores))[:max_k]
            recommendations[record.user] = cand[order].tolist()

    summary = {name: float(np.mean(vals)) if vals else float("nan") for name, vals in metrics.items()}
    return (summary, recommendations) if return_topk else summary


def evaluate_score_function(score_fn, records, k_values, tie_seed=2026, include_redundant=False, return_topk=False,
                            per_user: list | None = None):
    """score_fn(user, item) -> float; nếu có thêm score_fn.score_items(user, items)
    thì chấm điểm cả candidate set một lần (vector hoá, nhanh hơn nhiều)."""
    metrics = _empty_metric_lists(k_values, include_redundant)
    max_k = max(k_values)
    recommendations = {} if return_topk else None
    score_items = getattr(score_fn, "score_items", None)
    for record in records:
        cand = record.candidates
        if score_items is not None:
            scores = np.asarray(score_items(record.user, cand), dtype=np.float64)
        else:
            scores = np.fromiter((score_fn(record.user, int(i)) for i in cand), dtype=np.float64, count=len(cand))
        ranks = rank_positives(scores, cand, record.positives, record.user, tie_seed)
        _append(metrics, ranks, k_values, include_redundant)
        if per_user is not None:
            per_user.append(_per_user_row(record, cand, ranks, metrics))
        if return_topk:
            tie = deterministic_tie_key(record.user, cand, tie_seed)
            order = np.lexsort((tie, -scores))[:max_k]
            recommendations[record.user] = cand[order].tolist()
    summary = {name: float(np.mean(vals)) if vals else float("nan") for name, vals in metrics.items()}
    return (summary, recommendations) if return_topk else summary
