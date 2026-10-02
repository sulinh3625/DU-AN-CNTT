from __future__ import annotations

import numpy as np


def build_user_positive_sets(df, n_users: int):
    positives = [set() for _ in range(n_users)]
    for u, i in zip(df["user"].values, df["item"].values):
        positives[int(u)].add(int(i))
    return positives


def available_negatives(exclude_set: set[int], n_items: int) -> np.ndarray:
    if not exclude_set:
        return np.arange(n_items, dtype=np.int64)
    mask = np.ones(n_items, dtype=bool)
    valid = [i for i in exclude_set if 0 <= i < n_items]
    if valid:
        mask[np.fromiter(valid, dtype=np.int64)] = False
    return np.flatnonzero(mask).astype(np.int64)


def sample_train_negatives(
    exclude_set: set[int], n_items: int, n_samples: int, rng: np.random.Generator
) -> np.ndarray:
    available = available_negatives(exclude_set, n_items)
    if len(available) == 0:
        return np.empty(0, dtype=np.int64)
    return rng.choice(available, size=n_samples, replace=len(available) < n_samples).astype(np.int64)


def sample_eval_negatives(
    exclude_set: set[int], n_items: int, n_samples: int, rng: np.random.Generator
) -> np.ndarray:
    available = available_negatives(exclude_set, n_items)
    if len(available) == 0:
        return np.empty(0, dtype=np.int64)
    n_take = min(n_samples, len(available))
    return rng.choice(available, size=n_take, replace=False).astype(np.int64)
