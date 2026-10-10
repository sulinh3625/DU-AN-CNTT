from __future__ import annotations

import numpy as np


def deterministic_tie_key(user: int, item_ids: np.ndarray, seed: int) -> np.ndarray:
    # 64-bit integer mixing; stable between Python runs.
    x = item_ids.astype(np.uint64)
    x ^= np.uint64((int(user) + 1) * 0x9E3779B1)
    x ^= np.uint64((int(seed) + 1) * 0x85EBCA77)
    x *= np.uint64(0xC2B2AE3D)
    x ^= x >> np.uint64(16)
    return x


def rank_positives(scores: np.ndarray, candidates: np.ndarray, positives, user: int, tie_seed: int) -> np.ndarray:
    """Rank (1-based) của TỪNG item đúng: xếp theo điểm giảm dần, hoà điểm theo khoá tất định tăng dần."""
    scores = np.asarray(scores, dtype=np.float64)
    candidates = np.asarray(candidates, dtype=np.int64)
    positives = np.asarray(positives, dtype=np.int64)
    tie = deterministic_tie_key(user, candidates, tie_seed)
    order = np.lexsort((tie, -scores))
    ranks = np.flatnonzero(np.isin(candidates[order], positives)) + 1
    if len(ranks) != len(np.unique(positives)):
        raise ValueError("Mỗi item đúng phải xuất hiện đúng 1 lần trong candidate set")
    return ranks
