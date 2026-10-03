"""Chạy từ neumf_project/:  python -m pytest demo/tests -q"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from demo.backend import inference, metrics_io
from demo.backend.data_context import (FINAL_DIR, FINAL_SEED, V2_DIR, DataContext, final_available,
                                      resolve_latest_run_tag, v2_available)
from demo.backend.onboarding import Onboarding, load_onboarding_config
from src.data_pipeline.splitting import assert_disjoint_splits

TOL = 1e-6
# Logit tính lại trên CPU có thể lệch ~1e-7 so với GPU lúc đánh giá cuối -> hai item gần như hoà điểm có thể đổi chỗ
# ở hạng rất sâu. Mọi hạng trong vùng top-DEEP phải trùng tuyệt đối; sâu hơn cho phép lệch vài vị trí.
DEEP, DEEP_SLACK = 100, 3


@pytest.fixture(scope="module")
def ctx():
    """Chế độ explore: run khám phá leave-one-out."""
    try:
        resolve_latest_run_tag()
    except FileNotFoundError as exc:
        pytest.skip(str(exc))
    return DataContext(load_customers=False, mode="explore")


@pytest.fixture(scope="module")
def fctx():
    """Chế độ final: checkpoint của đánh giá cuối (outputs/final/seed42)."""
    if not final_available():
        pytest.skip("Chưa có outputs/final/seed42 kèm checkpoint — chạy scripts/11_final.py")
    return DataContext(load_customers=False, mode="final")


@pytest.fixture(scope="module")
def vctx():
    """Chế độ v2: checkpoint seed 42 của đánh giá cuối giao thức v2 (outputs/v2/final/seed42) — kết quả chính."""
    if not v2_available():
        pytest.skip("Chưa có outputs/v2/final/seed42 kèm checkpoint — chạy scripts/23_final_v2.py")
    return DataContext(load_customers=False, mode="v2")


V2_KEY = {"NeuMF-F": "neumf_f", "GMF-F": "gmf_f", "MLP-F": "mlp_f", "NeuMF": "neumf", "GMF": "gmf", "MLP": "mlp",
          "LateFusion-F": "late_f", "BPR-MF": "bpr", "UserKNN": "userknn", "ItemKNN": "itemknn",
          "MostPopular-Recent": "recent_pop", "Content": "content", "MostPopular": "popularity"}


# ------------------------------------------------------------------ explore: split
def test_splits_disjoint_and_one_item_per_user(ctx):
    assert_disjoint_splits(ctx.train_df, ctx.val_df, ctx.test_df)
    assert ctx.test_df["user"].is_unique and ctx.val_df["user"].is_unique


def test_target_follows_run_evaluated_on(ctx):
    """Demo chấm đúng tập của bảng kết quả run: validation (khoá test) hoặc test (--final)."""
    assert ctx.evaluated_on == ctx.run_metadata.get("evaluated_on", "test")
    target_df = ctx.test_df if ctx.evaluated_on == "test" else ctx.val_df
    assert ctx.target_item == dict(zip(target_df["user"].astype(int), target_df["item"].astype(int)))
    assert ctx.seen_pos is (ctx.train_val_pos if ctx.evaluated_on == "test" else ctx.train_pos)


def test_target_item_not_in_history(ctx):
    for u, item in ctx.target_item.items():
        assert item not in ctx.train_pos[u]
    for u in ctx.target_users[:300]:
        hist = ctx.history(int(u))
        ids = {h["item_idx"] for h in hist}
        assert ctx.target_item[int(u)] not in ids
        assert ids == ctx.train_pos[int(u)]
        dates = [h["t_dat"] for h in hist]
        assert dates == sorted(dates)


def test_candidates_follow_protocol(ctx):
    u = int(ctx.target_users[0])
    rec = inference.eval_record(ctx, u)
    cand = set(rec.candidates.tolist())
    assert ctx.target_item[u] in cand
    assert not (ctx.seen_pos[u] - {ctx.target_item[u]}) & cand
    assert len(cand) == ctx.n_items - len(ctx.seen_pos[u] - {ctx.target_item[u]})


# --------------------------------------------------- explore: per-user vs file
def test_demo_metrics_match_results_per_user(ctx):
    path = metrics_io.per_user_path(ctx.run_tag)
    if path is None:
        pytest.skip("Chưa có results_per_user.csv — chạy python demo/scripts/build_offline_artifacts.py")
    ref = pd.read_csv(path, dtype={"customer_id": str}).set_index(["model", "customer_id"])
    rng = np.random.default_rng(0)
    users = rng.choice(ctx.target_users, size=100, replace=False)
    k = max(ctx.k_values)
    for m in ctx.available_models:
        for u in users:
            out = inference.recommend(ctx, m, int(u), k)["evaluation"]
            row = ref.loc[(m, ctx.customer_ids[int(u)])]
            assert out["rank"] == row["rank"], (m, u)
            assert out["n_candidates"] == row["n_candidates"]
            for metric, v in out["metrics"].items():
                if metric in row:
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


# ------------------------------------------------------------------ final: đúng mô hình của Chương 4
def test_final_targets_are_test_pairs_and_unseen(fctx):
    assert fctx.mode == "final" and fctx.evaluated_on == "test"
    expected = {int(u): sorted(int(i) for i in g["item"]) for u, g in fctx.test_df.groupby("user")}
    assert fctx.target_items == expected
    for u in fctx.target_users[:300]:
        u = int(u)
        assert not set(fctx.target_items[u]) & fctx.train_pos[u]
        hist = fctx.history(u)
        assert {h["item_idx"] for h in hist} == fctx.train_pos[u]
        assert all(h["t_dat"] < str(fctx.cfg.dataset.test_start) for h in hist)  # lịch sử chỉ trước mốc test


def test_final_candidates_match_evaluation_records(fctx):
    """Tập ứng viên của demo trùng record của 11_final.py (build_full_ranking_records_multi trên train ∪ val)."""
    from src.evaluation.full_ranking import build_full_ranking_records_multi
    pool = np.flatnonzero(fctx.pool_mask)
    users = set(int(u) for u in fctx.target_users[:200])
    sub = fctx.test_df[fctx.test_df["user"].isin(users)]
    for rec in build_full_ranking_records_multi(sub, fctx.n_items, fctx.seen_pos, pool):
        mine = inference.eval_record(fctx, rec.user)
        assert np.array_equal(mine.candidates, rec.candidates)
        assert np.array_equal(mine.positives, rec.positives)


def test_final_metrics_match_chapter4_per_user(fctx):
    """Chỉ số per-user của demo khớp outputs/final/seed42/results_per_user.csv (số của Chương 4)."""
    ref = pd.read_csv(FINAL_DIR / f"seed{FINAL_SEED}" / "results_per_user.csv").set_index(["model", "user"])
    rng = np.random.default_rng(1)
    users = rng.choice(fctx.target_users, size=60, replace=False)
    models = [m for m in fctx.available_models if m in ref.index.get_level_values(0)]
    assert set(models) >= {"NeuMF-Pretrained", "NeuMF-Scratch", "GMF", "MLP", "BPR-MF", "MostPopular"}
    for m in models:
        for u in users:
            out = inference.recommend(fctx, m, int(u), 10)["evaluation"]
            row = ref.loc[(m, int(u))]
            want = [int(x) for x in str(row["ranks"]).split(";")]
            assert out["n_candidates"] == row["n_candidates"]
            for got, exp in zip(out["ranks"], want):
                assert got == exp if min(got, exp) <= DEEP else abs(got - exp) <= DEEP_SLACK, (m, u, got, exp)
            for metric, v in out["metrics"].items():
                if metric in row:
                    assert abs(v - row[metric]) <= TOL, (m, u, metric, v, row[metric])


def test_final_late_fusion_minmax_on_candidates(fctx):
    """Late fusion chuẩn hoá min-max trên tập ứng viên (như 17_extension.py), không phải trên toàn catalog."""
    if "LateFusion-GMF-MLP" not in fctx.scorers:
        pytest.skip("Chưa có tham số mở rộng trong best_configs.json")
    u = int(fctx.target_users[0])
    rec = inference.eval_record(fctx, u)
    scores = inference.candidate_scores(fctx, "LateFusion-GMF-MLP", u, rec)
    assert len(scores) == len(rec.candidates) and scores.min() >= 0 and scores.max() <= 1


def test_final_neighbors_are_sorted_and_counted(fctx):
    if "UserKNN" not in fctx.scorers:
        pytest.skip("Chưa có tham số UserKNN trong best_configs.json")
    u = int(fctx.target_users[5])
    nb = fctx.neighbors(u, 10)
    assert 0 < len(nb) <= 10
    sims = [n["similarity"] for n in nb]
    assert sims == sorted(sims, reverse=True)
    for n in nb:
        v = fctx.user2idx[n["customer_id"]]
        assert n["n_common"] == len(fctx.train_pos[u] & fctx.train_pos[v]) > 0
        assert {t["item_idx"] for t in n["bought_target"]} <= set(fctx.target_items[u])


def test_final_dashboard_reads_result_files(fctx):
    d = metrics_io.final_dashboard(fctx)
    assert d["summary"]["status"] == "ok"
    models = {r["model"] for r in d["summary"]["data"]}
    assert {"BPR-MF", "NeuMF-Pretrained", "Random"} <= models
    assert d["stats"]["data"]["n_test_users"] == len(fctx.target_users)


# ------------------------------------------------------------- v2 (kết quả chính)
def test_v2_metrics_match_per_user_file(vctx):
    """Chỉ số per-user của demo khớp outputs/v2/final/seed42/per_user.csv.gz (số của Chương 4)."""
    per = pd.read_csv(V2_DIR / f"seed{FINAL_SEED}" / "per_user.csv.gz").set_index(["model", "user"])
    rng = np.random.default_rng(2)
    users = rng.choice(vctx.target_users, size=min(40, len(vctx.target_users)), replace=False)
    assert {"NeuMF-F", "NeuMF", "GMF-F", "MLP-F", "LateFusion-F", "BPR-MF"} <= set(vctx.available_models)
    for m in vctx.available_models:
        for u in users:
            out = inference.recommend(vctx, m, int(u), 10)["evaluation"]
            row = per.loc[(V2_KEY[m], int(u))]
            want = [int(x) for x in str(row["ranks"]).split(";")]
            assert out["n_candidates"] == row["n_candidates"]
            for got, exp in zip(out["ranks"], want):
                assert got == exp if min(got, exp) <= DEEP else abs(got - exp) <= DEEP_SLACK, (m, u, got, exp)
            assert abs(out["metrics"]["NDCG@10"] - row["NDCG@10"]) <= TOL, (m, u)


def test_v2_id_only_models_rank_new_items_last(vctx):
    """Mô hình chỉ dùng ID xếp mọi sản phẩm mới sau mọi sản phẩm cũ; sản phẩm mới được gắn cờ is_new."""
    u = next(u for u, items in vctx.target_items.items() if any(vctx.new_mask[i] for i in items))
    rec = inference.eval_record(vctx, int(u))
    n_old = int((~vctx.new_mask[rec.candidates]).sum())
    for m in ("NeuMF", "GMF", "MLP", "BPR-MF", "MostPopular"):
        if m in vctx.available_models:
            out = inference.recommend(vctx, m, int(u), 10)
            new_ranks = [t["rank"] for t in out["targets"] if t["is_new"]]
            assert new_ranks and min(new_ranks) > n_old, m


def test_v2_dashboard_reads_result_files(vctx):
    d = metrics_io.v2_dashboard(vctx)
    assert d["summary"]["status"] == "ok" and d["significance"]["status"] == "ok"
    assert {"NeuMF-F", "NeuMF", "UserKNN"} <= {r["model"] for r in d["summary"]["data"]}
    assert len(d["significance"]["data"]) == 10
    assert d["stats"]["data"]["n_test_users"] == len(vctx.target_users)


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
