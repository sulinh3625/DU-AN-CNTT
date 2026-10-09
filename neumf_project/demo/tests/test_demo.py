"""Chạy từ neumf_project/:  python -m pytest demo/tests -q"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from demo.backend import inference, metrics_io
from demo.backend.data_context import (FINAL_DIR, FINAL_SEED, V2_DIR, DataContext, _v2_common, final_available,
                                      resolve_latest_run_tag, user_table, v2_available, v2_data_mismatch)
from demo.backend.routes import filter_users, user_position, user_rows
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
        pytest.skip("Chưa có outputs/v2/final/seed42 kèm checkpoint tạo từ file dữ liệu đã lọc hiện tại — chạy "
                    "scripts/23_final_v2.py")
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


def test_v2_results_from_other_data_are_refused(tmp_path, monkeypatch):
    """Kết quả v2 tạo từ dữ liệu khác file đã lọc hiện tại (thiếu / lệch data_md5) không được nạp: demo không dựng tập
    kiểm thử của mẫu kiểm định cho một kết quả cũ."""
    V = _v2_common()
    (tmp_path / "seed42").mkdir()
    (tmp_path / "seed42" / "results.json").write_text(json.dumps({"evaluated_on": "test"}), encoding="utf-8")
    (tmp_path / "manifest.json").write_text(json.dumps({V.data_name("holdout"): {"md5": "abc"}}), encoding="utf-8")
    monkeypatch.setattr(V, "MANIFEST", tmp_path / "manifest.json")
    for data_md5, usable in ((None, False), ("xyz", False), ("abc", True)):
        (tmp_path / "data.json").write_text(json.dumps({"data_md5": data_md5}), encoding="utf-8")
        assert (v2_data_mismatch(tmp_path, 42) is None) == usable, data_md5


# ------------------------------------------------------------- danh sách chọn khách (Admin)
def _users() -> pd.DataFrame:
    """5 khách, khách gh05 không có sản phẩm đích; mua nhiều nhất: ab01 đồ nữ 2/3, bf04 đồ nữ 2/4."""
    days = (1, 5, 3, 2, 2, 9, 1, 2, 3, 4, 1)
    train = pd.DataFrame({"user": [0, 0, 0, 1, 1, 2, 3, 3, 3, 3, 4], "item": [0, 1, 2, 0, 3, 3, 0, 1, 2, 3, 0],
                          "last_timestamp": pd.to_datetime([f"2020-01-0{d}" for d in days])})
    articles = pd.DataFrame({"index_group_name": ["Ladieswear", "Ladieswear", "Menswear", "Divided"]})
    ids = np.array(["ab01", "ab02", "cd03", "bf04", "gh05"], dtype=object)
    return user_table(ids, {0: [3], 1: [1, 2], 2: [0], 3: [5, 6, 7]}, train, articles, pd.Series({0: 31.0, 3: 22.0}))


def test_user_table_counts_area_age_and_buckets():
    df = _users()
    assert df.index.tolist() == ["ab01", "ab02", "cd03", "bf04"]
    assert df["train_count"].tolist() == [3, 2, 1, 4] and df["n_targets"].tolist() == [1, 2, 1, 3]
    assert (df.loc["ab01", "area"], df.loc["ab01", "area_share"]) == ("Ladieswear", round(2 / 3, 3))
    assert (df.loc["ab01", "first_date"], df.loc["ab01", "last_date"]) == ("2020-01-01", "2020-01-05")
    assert df.attrs["thresholds"] == (2.0, 3.0) and df["bucket"].tolist() == ["mid", "low", "low", "high"]
    assert user_rows(df.loc[["ab01", "ab02"]])[0]["age"] == 31 and user_rows(df.loc[["ab02"]])[0]["age"] is None


def test_filter_users_search_sort_and_position():
    df = _users()
    assert filter_users(df, " B")["customer_id"].tolist() == ["bf04", "ab01", "ab02"]  # khớp ở đầu xếp trước
    assert filter_users(df, sort="train_asc")["customer_id"].tolist() == ["cd03", "ab02", "ab01", "bf04"]
    assert filter_users(df, bucket="low", sort="id")["customer_id"].tolist() == ["ab02", "cd03"]
    assert filter_users(df, area="Ladieswear")["customer_id"].tolist() == ["bf04", "ab01"]
    full = filter_users(df)  # mua nhiều nhất trước: bf04, ab01, ab02, cd03
    pos = user_position(full, "ab01")
    assert (pos["index"], pos["total"]) == (1, 4)
    assert (pos["prev"]["customer_id"], pos["next"]["customer_id"]) == ("bf04", "ab02")
    assert user_position(full, "bf04")["prev"] is None and user_position(full, "cd03")["next"] is None
    out = user_position(filter_users(df, bucket="high"), "ab01")  # ngoài bộ lọc: "sau" = khách đầu danh sách
    assert out["index"] is None and out["prev"] is None and out["next"]["customer_id"] == "bf04"
    ranks = pd.Series({"ab01": 3, "ab02": 25, "cd03": 10, "bf04": 11})  # hạng món đích tốt nhất của một mô hình
    assert filter_users(df, best_rank=ranks, hit="hit", k=10, sort="rank")["customer_id"].tolist() == ["ab01", "cd03"]
    assert filter_users(df, best_rank=ranks, hit="miss", k=20)["customer_id"].tolist() == ["ab02"]
    assert filter_users(df, best_rank=ranks)["best_rank"].tolist() == [11, 3, 25, 10]  # không lọc: chỉ thêm cột


def test_final_best_ranks_match_recommend(fctx):
    """Hạng dùng để lọc khách gợi ý trúng = đúng hạng mà màn Kiểm thử mô hình hiển thị cho từng khách."""
    users = fctx.target_users[:12]
    for m in ("GMF", "MostPopular", "LateFusion-GMF-MLP"):
        if m in fctx.available_models:
            got = inference.best_ranks(fctx, m, users, chunk=5)
            assert got == {int(u): inference.recommend(fctx, m, int(u), 10)["evaluation"]["rank"] for u in users}, m
