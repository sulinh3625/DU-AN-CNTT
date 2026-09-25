"""Chạy từ neumf_project_v2/:  python -m pytest demo/tests -q"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from demo.backend import inference, metrics_io
from demo.backend.data_context import DataContext, resolve_latest_run_tag
from demo.backend.onboarding import Onboarding, load_onboarding_config
from src.data_pipeline.splitting import assert_disjoint_splits

TOL = 1e-6


@pytest.fixture(scope="module")
def ctx():
    try:
        resolve_latest_run_tag()
    except FileNotFoundError as exc:
        pytest.skip(str(exc))
    return DataContext(load_customers=False)


# ------------------------------------------------------------------ split
def test_splits_disjoint_and_one_item_per_user(ctx):
    assert_disjoint_splits(ctx.train_df, ctx.val_df, ctx.test_df)
    assert ctx.test_df["user"].is_unique and ctx.val_df["user"].is_unique


def test_test_item_not_in_history(ctx):
    for u, item in ctx.test_item.items():
        assert item not in ctx.train_pos[u]
    for u in ctx.test_users[:300]:
        hist = ctx.history(int(u))
        ids = {h["item_idx"] for h in hist}
        assert ctx.test_item[int(u)] not in ids
        assert ids == ctx.train_pos[int(u)]
        dates = [h["t_dat"] for h in hist]
        assert dates == sorted(dates)


def test_candidates_follow_protocol(ctx):
    u = int(ctx.test_users[0])
    rec = inference.eval_record(ctx, u)
    cand = set(rec.candidates.tolist())
    assert ctx.test_item[u] in cand
    assert not (ctx.train_val_pos[u] - {ctx.test_item[u]}) & cand
    assert len(cand) == ctx.n_items - len(ctx.train_val_pos[u] - {ctx.test_item[u]})


# --------------------------------------------------- per-user vs file
def test_demo_metrics_match_results_per_user(ctx):
    path = metrics_io.per_user_path(ctx.run_tag)
    if path is None:
        pytest.skip("Chưa có results_per_user.csv — chạy python demo/scripts/build_offline_artifacts.py")
    ref = pd.read_csv(path, dtype={"customer_id": str}).set_index(["model", "customer_id"])
    rng = np.random.default_rng(0)
    users = rng.choice(ctx.test_users, size=100, replace=False)
    k = max(ctx.k_values)
    for m in ctx.available_models:
        for u in users:
            out = inference.recommend(ctx, m, int(u), k)["evaluation"]
            row = ref.loc[(m, ctx.customer_ids[int(u)])]
            assert out["rank"] == row["rank"], (m, u)
            assert out["n_candidates"] == row["n_candidates"]
            for metric, v in out["metrics"].items():
                assert abs(v - row[metric]) <= TOL, (m, u, metric, v, row[metric])


def test_results_per_user_mean_matches_run(ctx):
    """Trung bình per-user phải khớp results_primary.csv do 03_run_experiment.py sinh ra."""
    path = metrics_io.per_user_path(ctx.run_tag)
    if path is None:
        pytest.skip("Chưa có results_per_user.csv")
    per_user = pd.read_csv(path)
    official = pd.read_csv(metrics_io.EXPERIMENTS_DIR / ctx.run_tag / "results_primary.csv", index_col=0)
    means = per_user.groupby("model")[list(official.columns)].mean()
    for m, row in means.iterrows():
        for metric, v in row.items():
            assert abs(v - official.loc[m, metric]) <= TOL, (m, metric)


# ------------------------------------------------------------- onboarding
def _toy():
    ts = pd.Timestamp("2020-01-10")
    articles = pd.DataFrame({
        "article_id": ["0000000001", "0000000002", "0000000003", "0000000004"],
        "index_group_name": ["Ladieswear", "Ladieswear", "Ladieswear", "Menswear"],
        "product_group_name": ["Garment Lower body", "Garment Lower body", "Accessories", "Shoes"],
        "perceived_colour_master_name": ["Red", "Blue", "Red", "Black"],
        "product_type_name": ["Trousers", "Trousers", "Bag", "Sneakers"],
    })
    train = pd.DataFrame({"user": [0, 1, 2, 3, 4], "item": [1, 1, 1, 2, 3],
                          "last_timestamp": [ts] * 5})
    return train, articles


def test_onboarding_uses_only_train_popularity():
    train, articles = _toy()
    ob = Onboarding(train, articles, pd.Series(dtype=float), load_onboarding_config())
    res = ob.recommend("women", k=5)
    counts = {it["item_idx"]: it["count"] for it in res["preferred"]}
    assert counts == train["item"].value_counts().loc[[1, 2]].to_dict()
    assert 0 not in counts  # item 0 không có lượt mua trong train -> không được gắn "bán chạy"


def test_onboarding_relaxes_conditions_in_order():
    train, articles = _toy()
    ob = Onboarding(train, articles, pd.Series(dtype=float), load_onboarding_config())
    res = ob.recommend("women", ["Garment Lower body"], ["Red"], k=5)
    # Không có item đỏ nào bán được -> nới màu, rồi nới loại sản phẩm.
    assert res["relaxations"] == ["Đã bỏ điều kiện màu", "Đã bỏ điều kiện loại sản phẩm (chỉ giữ khu vực)"]
    assert [it["item_idx"] for it in res["preferred"]] == [1, 2]
    # Bậc "bỏ màu" không thêm được item nào vẫn phải được báo là đã nới.
    res = ob.recommend("women", ["Shoes"], ["Red"], k=5)
    assert res["relaxations"] == ["Đã bỏ điều kiện màu", "Đã bỏ điều kiện loại sản phẩm (chỉ giữ khu vực)"]
    assert [it["relax_level"] for it in res["preferred"]] == [2, 2]


def test_onboarding_real_context_counts_train_window(ctx):
    ob = Onboarding(ctx.train_df, ctx.articles, pd.Series(dtype=float), load_onboarding_config())
    start, end = (pd.Timestamp(d) for d in ob.window_range)
    in_window = ctx.train_df["last_timestamp"].between(start, end)
    assert len(ob.window) == int(in_window.sum())
    assert set(ob.window["item"]) <= set(ctx.train_df["item"])
