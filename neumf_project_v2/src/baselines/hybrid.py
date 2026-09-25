"""Hybrid lai ghép muộn (weighted late fusion): CF (NeuMF) + Content-based.

score = alpha * minmax(CF) + (1 - alpha) * minmax(CBF), chuẩn hoá min-max
trên tập candidate của TỪNG user để hai thang điểm (logit NeuMF, cosine CBF)
so sánh được với nhau. alpha chọn theo NDCG@10 trên VALIDATION.
"""
from __future__ import annotations

import numpy as np
import torch

from src.evaluation.metrics import ndcg_at_k
from src.evaluation.ranking_utils import rank_positive


def _minmax(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    lo, hi = x.min(), x.max()
    if hi - lo < 1e-12:
        return np.zeros_like(x)
    return (x - lo) / (hi - lo)


class HybridScorer:
    def __init__(self, cf_model, content_model, alpha: float, device="cpu"):
        self.cf_model = cf_model
        self.content_model = content_model
        self.alpha = float(alpha)
        self.device = device

    @torch.no_grad()
    def cf_scores(self, user: int, items: np.ndarray) -> np.ndarray:
        self.cf_model.eval()
        items_t = torch.from_numpy(np.asarray(items, dtype=np.int64)).to(self.device)
        users_t = torch.full_like(items_t, int(user))
        return self.cf_model(users_t, items_t).detach().cpu().numpy().astype(np.float64)

    def score_items(self, user: int, items: np.ndarray) -> np.ndarray:
        cf = _minmax(self.cf_scores(user, items))
        cb = _minmax(self.content_model.score_items(user, items))
        return self.alpha * cf + (1.0 - self.alpha) * cb

    def __call__(self, user: int, item: int) -> float:
        return float(self.score_items(user, np.array([item]))[0])


def tune_hybrid_alpha(cf_model, content_model, val_records, alphas, device="cpu", k: int = 10, tie_seed: int = 2026):
    """Grid-search alpha trên VALIDATION; trả về (best_alpha, {alpha: NDCG@k})."""
    probe = HybridScorer(cf_model, content_model, 0.5, device)
    cached = [
        (r, _minmax(probe.cf_scores(r.user, r.candidates)), _minmax(content_model.score_items(r.user, r.candidates)))
        for r in val_records
    ]
    results = {}
    for alpha in alphas:
        vals = [
            ndcg_at_k(rank_positive(alpha * cf + (1 - alpha) * cb, r.candidates, r.positive_item, r.user, tie_seed), k)
            for r, cf, cb in cached
        ]
        results[float(alpha)] = float(np.mean(vals)) if vals else 0.0
    best = max(results, key=lambda a: (results[a], a))  # hoà điểm -> ưu tiên alpha lớn (gần NeuMF gốc)
    return best, results
