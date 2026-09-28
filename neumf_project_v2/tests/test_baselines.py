from __future__ import annotations

import numpy as np

from src.baselines.classical import first_uniform, kth_available
from src.data_pipeline.negative_sampling import available_negatives


def test_first_uniform_matches_numpy_default_rng():
    seeds = np.concatenate([[0, 1, 42, 2**32 - 1], np.random.default_rng(1).integers(0, 2**32, size=2000)])
    want = np.array([np.random.default_rng(int(s)).random() for s in seeds])
    assert np.array_equal(first_uniform(seeds), want)


def test_kth_available_matches_available_negatives():
    rng = np.random.default_rng(0)
    for _ in range(200):
        n = int(rng.integers(1, 40))
        pos = np.unique(rng.integers(0, n, size=int(rng.integers(0, n))))
        avail = available_negatives(set(pos.tolist()), n)
        assert [kth_available(pos, k) for k in range(len(avail))] == avail.tolist()
