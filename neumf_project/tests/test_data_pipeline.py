from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.data_pipeline.kcore import iterative_k_core
from src.data_pipeline.preprocessing import aggregate_unique_user_item
from src.data_pipeline.negative_sampling import build_user_positive_sets, sample_train_negatives
from src.data_pipeline.dataset import TrainDataset
from src.data_pipeline.adapters.hm import HMAdapter


def test_aggregate_before_kcore_counts_unique_edges():
    events = pd.DataFrame({
        "user_raw": ["u1"] * 5 + ["u1", "u2", "u2"],
        "item_raw": ["a"] * 5 + ["b", "a", "b"],
        "timestamp": pd.date_range("2020-01-01", periods=8),
        "value_raw": [1.0] * 8,
        "source_order": np.arange(8),
    })
    agg = aggregate_unique_user_item(events)
    # u1 has only 2 unique items, not 6 interactions as raw rows suggest.
    assert len(agg[agg.user_raw == "u1"]) == 2
    filtered = iterative_k_core(agg, 2)
    assert set(filtered.user_raw) == {"u1", "u2"}
    assert set(filtered.item_raw) == {"a", "b"}


def test_negative_sampler_never_returns_positive():
    rng = np.random.default_rng(0)
    positives = {0, 1, 2, 3, 4}
    negs = sample_train_negatives(positives, 6, 10, rng)
    assert len(negs) == 10
    assert set(negs) == {5}


def test_train_dataset_never_labels_positive_as_negative():
    train = pd.DataFrame({"user": [0, 0], "item": [0, 1], "sample_weight": [1.0, 1.0]})
    pos = build_user_positive_sets(train, 1)
    ds = TrainDataset(train, n_items=3, train_positive_sets=pos, neg_ratio=4, seed=0)
    negative_items = ds.items[ds.labels == 0]
    assert set(negative_items) == {2}


def test_hm_adapter_rejects_excel(tmp_path):
    fake = tmp_path / "transactions_train.xlsx"
    fake.write_bytes(b"")
    with pytest.raises(ValueError):
        HMAdapter(fake).load_events()
