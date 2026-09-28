from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import torch

from .metrics import hr_at_k, ndcg_at_k, precision_at_k, recall_at_k
from .ranking_utils import rank_positive, deterministic_tie_key


@dataclass
class EvalRecord:
    user: int
    positive_item: int
    candidates: np.ndarray


class FullRankingRecord:
    """EvalRecord cho Full Ranking, sinh candidates khi cần.

    Chỉ giữ các item đã thấy (vài chục phần tử) thay vì mảng dài n_items cho
    mỗi user — giữ sẵn mảng đó cho mọi user tốn RAM theo n_users × n_items.
    """

    __slots__ = ("user", "positive_item", "n_items", "seen")

    def __init__(self, user: int, positive_item: int, n_items: int, seen: np.ndarray):
        self.user, self.positive_item, self.n_items, self.seen = user, positive_item, n_items, seen

    @property
    def candidates(self) -> np.ndarray:
        mask = np.ones(self.n_items, dtype=bool)
        mask[self.seen] = False
        mask[self.positive_item] = True
        return np.flatnonzero(mask).astype(np.int64, copy=False)


def build_full_ranking_records(eval_df, n_items: int, seen_positive_sets) -> list[FullRankingRecord]:
    records = []
    for u, pos in zip(eval_df["user"].values, eval_df["item"].values):
        u, pos = int(u), int(pos)
        seen = np.fromiter(seen_positive_sets[u], dtype=np.int64)
        records.append(FullRankingRecord(u, pos, n_items, seen))
    return records


def _empty_metric_lists(k_values, include_redundant):
    out = {f"HR@{k}": [] for k in k_values}
    out.update({f"NDCG@{k}": [] for k in k_values})
    if include_redundant:
        out.update({f"Precision@{k}": [] for k in k_values})
        out.update({f"Recall@{k}": [] for k in k_values})
    return out


def _append(metrics, rank, k_values, include_redundant):
    for k in k_values:
        metrics[f"HR@{k}"].append(hr_at_k(rank, k))
        metrics[f"NDCG@{k}"].append(ndcg_at_k(rank, k))
        if include_redundant:
            metrics[f"Precision@{k}"].append(precision_at_k(rank, k))
            metrics[f"Recall@{k}"].append(recall_at_k(rank, k))


@torch.no_grad()
def evaluate_torch_model(model, records, k_values, device="cpu", batch_size=16384, tie_seed=2026, include_redundant=False, return_topk=False, max_pairs=4_000_000):
    """Evaluate PyTorch model with flattened batched scoring.

    Tránh gọi model một lần cho từng user: candidate pairs của một nhóm user
    được flatten rồi score theo batch lớn, sau đó cắt lại theo offsets để tính
    rank từng user. Mỗi nhóm giới hạn ~max_pairs cặp nên RAM không tăng theo
    tổng n_users × n_items.
    """
    model.eval()
    metrics = _empty_metric_lists(k_values, include_redundant)
    max_k = max(k_values)
    recommendations = {} if return_topk else None
    if not records:
        summary = {name: float("nan") for name in metrics}
        return (summary, recommendations) if return_topk else summary

    def flush(chunk):
        lengths = np.fromiter((len(c) for _, c in chunk), dtype=np.int64, count=len(chunk))
        offsets = np.concatenate(([0], np.cumsum(lengths)))
        users_flat = np.repeat(np.fromiter((r.user for r, _ in chunk), dtype=np.int64, count=len(chunk)), lengths)
        items_flat = np.concatenate([c for _, c in chunk])
        score_flat = np.empty(len(items_flat), dtype=np.float32)
        for start in range(0, len(items_flat), batch_size):
            end = start + batch_size
            users = torch.from_numpy(users_flat[start:end]).to(device)
            items = torch.from_numpy(items_flat[start:end]).to(device)
            score_flat[start:end] = model(users, items).detach().cpu().numpy()

        for idx, (record, cand) in enumerate(chunk):
            scores = score_flat[offsets[idx]:offsets[idx + 1]]
            rank = rank_positive(scores, cand, record.positive_item, record.user, tie_seed)
            _append(metrics, rank, k_values, include_redundant)
            if return_topk:
                tie = deterministic_tie_key(record.user, cand, tie_seed)
                order = np.lexsort((tie, -scores))[:max_k]
                recommendations[record.user] = cand[order].tolist()

    chunk, n_pairs = [], 0
    for record in records:
        cand = np.asarray(record.candidates, dtype=np.int64)
        chunk.append((record, cand))
        n_pairs += len(cand)
        if n_pairs >= max_pairs:
            flush(chunk)
            chunk, n_pairs = [], 0
    if chunk:
        flush(chunk)

    summary = {name: float(np.mean(vals)) if vals else float("nan") for name, vals in metrics.items()}
    return (summary, recommendations) if return_topk else summary


def evaluate_score_function(score_fn, records, k_values, tie_seed=2026, include_redundant=False, return_topk=False):
    metrics = _empty_metric_lists(k_values, include_redundant)
    max_k = max(k_values)
    recommendations = {} if return_topk else None
    for record in records:
        cand = np.asarray(record.candidates, dtype=np.int64)
        scores = np.asarray(score_fn(record.user, cand), dtype=np.float64)  # score_fn nhận cả mảng item
        rank = rank_positive(scores, cand, record.positive_item, record.user, tie_seed)
        _append(metrics, rank, k_values, include_redundant)
        if return_topk:
            tie = deterministic_tie_key(record.user, cand, tie_seed)
            order = np.lexsort((tie, -scores))[:max_k]
            recommendations[record.user] = cand[order].tolist()
    summary = {name: float(np.mean(vals)) if vals else float("nan") for name, vals in metrics.items()}
    return (summary, recommendations) if return_topk else summary
