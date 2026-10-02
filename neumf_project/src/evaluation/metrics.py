from __future__ import annotations

import math


def hr_at_k(rank: int, k: int) -> float:
    return 1.0 if rank <= k else 0.0


def ndcg_at_k(rank: int, k: int) -> float:
    return 1.0 / math.log2(rank + 1) if rank <= k else 0.0


def precision_at_k(rank: int, k: int) -> float:
    return 1.0 / k if rank <= k else 0.0


def recall_at_k(rank: int, k: int) -> float:
    return hr_at_k(rank, k)


def multi_ranking_metrics(ranks, k: int) -> dict[str, float]:
    """HR/NDCG/Precision/Recall@k khi user có nhiều item đúng (relevance nhị phân).

    ranks: rank (1-based) của từng item đúng. Với 1 item đúng các giá trị trùng
    đúng hr_at_k / ndcg_at_k / precision_at_k / recall_at_k.
    """
    ranks = [int(r) for r in ranks]
    hits = [r for r in ranks if r <= k]
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, min(k, len(ranks)) + 1))
    return {
        "HR": 1.0 if hits else 0.0,
        "NDCG": sum(1.0 / math.log2(r + 1) for r in hits) / idcg if idcg else 0.0,
        "Precision": len(hits) / k,
        "Recall": len(hits) / len(ranks) if ranks else 0.0,
    }
