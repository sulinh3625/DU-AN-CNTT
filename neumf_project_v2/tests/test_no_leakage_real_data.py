"""Không rò rỉ thời gian trên dữ liệu thật hm500k (bỏ qua nếu chưa tạo dữ liệu)."""
from __future__ import annotations

from functools import lru_cache

import pandas as pd
import pytest

from scripts.common import build_adapter
from src.data_pipeline.preprocessing import build_interactions
from src.data_pipeline.splitting import assert_disjoint_splits, global_temporal_split, temporal_leave_one_out


@lru_cache(maxsize=None)
def _data(config_path: str):
    cfg, adapter = build_adapter(config_path)
    if not adapter.path.exists():
        pytest.skip(f"Chưa có {adapter.path} — chạy python run.py sample-hm")
    return cfg, build_interactions(adapter.load_events(), cfg.dataset.k_core)


def test_global_split_respects_one_timeline():
    cfg, data = _data("configs/hm500k_global.yaml")
    train, val, test = global_temporal_split(data.df, cfg.dataset.val_start, cfg.dataset.test_start)
    assert_disjoint_splits(train, val, test)
    vs, ts = pd.Timestamp(cfg.dataset.val_start), pd.Timestamp(cfg.dataset.test_start)
    assert train["first_timestamp"].max() < vs <= val["first_timestamp"].min()
    assert val["first_timestamp"].max() < ts <= test["first_timestamp"].min()
    # Mô hình chỉ thấy train: mọi user/item trong val/test phải có mặt trong train.
    assert set(val["user"]) | set(test["user"]) <= set(train["user"])
    assert set(val["item"]) | set(test["item"]) <= set(train["item"])
    assert len(val) and len(test)


def test_loo_split_is_temporal_per_user():
    cfg, data = _data("configs/hm500k.yaml")
    train, val, test = temporal_leave_one_out(data.df, cfg.dataset.min_interactions_for_loo)
    assert_disjoint_splits(train, val, test)
    last_train = train.groupby("user")["last_timestamp"].max()
    v = val.set_index("user")["last_timestamp"]
    t = test.set_index("user")["last_timestamp"]
    assert (v >= last_train.reindex(v.index)).all()
    assert (t >= v.reindex(t.index)).all()
    assert val["user"].is_unique and test["user"].is_unique
