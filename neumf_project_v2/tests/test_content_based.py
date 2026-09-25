from __future__ import annotations

import numpy as np
import pandas as pd
import torch

from src.baselines import (
    AgeGroupPopularityBaseline, CategoryPopularityBaseline, ContentBasedBaseline,
    HybridScorer, build_item_feature_matrix, tune_hybrid_alpha,
)
from src.data_pipeline.preprocessing import build_interactions
from src.data_pipeline.side_features import age_bucket, load_hm_item_features, load_hm_user_age_groups
from src.evaluation.cold_start import build_strict_cold_start
from src.evaluation.full_ranking import EvalRecord, evaluate_score_function

ITEMS = pd.DataFrame({
    "product_type_name": ["Trousers", "Trousers", "Sweater", "Sweater"],
    "colour_group_name": ["Black", "Blue", "Black", "Red"],
    "detail_desc": ["slim denim jeans", "wide denim jeans", "wool knit sweater", "cotton knit sweater"],
})


def _matrix():
    return build_item_feature_matrix(ITEMS, ["product_type_name", "colour_group_name"], ["detail_desc"])


def test_item_feature_rows_are_l2_normalized():
    X = _matrix()
    norms = np.sqrt(np.asarray(X.multiply(X).sum(axis=1)).ravel())
    assert np.allclose(norms, 1.0)


def test_content_based_prefers_similar_items():
    train = pd.DataFrame({"user": [0], "item": [0]})
    model = ContentBasedBaseline(_matrix(), train)
    scores = model.score_items(0, np.array([1, 2, 3]))
    assert scores[0] > scores[2]  # cùng loại quần denim > áo len khác màu


def test_content_based_unknown_user_scores_zero():
    model = ContentBasedBaseline(_matrix(), pd.DataFrame({"user": [0], "item": [0]}))
    assert not model.score_items(99, np.array([0, 1])).any()


def test_recency_decay_weights_latest_item_more():
    train = pd.DataFrame({
        "user": [0, 0], "item": [0, 2],
        "last_timestamp": pd.to_datetime(["2020-01-01", "2020-02-01"]),
        "last_source_order": [0, 1],
    })
    model = ContentBasedBaseline(_matrix(), train, recency_decay=0.1)
    s = model.score_items(0, np.array([1, 3]))
    assert s[1] > s[0]  # item gần nhất là áo len -> ưu tiên áo len


def test_category_popularity_vectorized_matches_scalar():
    train = pd.DataFrame({"user": [0, 1, 1, 2], "item": [0, 1, 2, 2]})
    cats = {0: "a", 1: "a", 2: "b", 3: "b"}
    bl = CategoryPopularityBaseline(train, cats, 4)
    items = np.arange(4)
    assert np.allclose(bl.score_items(0, items), [bl.score(0, int(i)) for i in items])
    assert np.allclose(bl.score_items(42, items), [bl.score(42, int(i)) for i in items])


def test_age_group_popularity_uses_own_group():
    train = pd.DataFrame({"user": [0, 1, 2], "item": [0, 0, 1]})
    groups = {0: "<25", 1: "<25", 2: "55+", 3: "55+"}
    bl = AgeGroupPopularityBaseline(train, 2, groups)
    s = bl.score_items(3, np.array([0, 1]))
    assert s[1] > s[0]


def test_age_bucket():
    assert age_bucket(20) == "<25"
    assert age_bucket(25) == "25-34"
    assert age_bucket(70) == "55+"
    assert age_bucket(np.nan) == "unknown"


def test_evaluate_score_function_uses_score_items():
    class Scorer:
        def score_items(self, user, items):
            return (items == 3).astype(float)

        def __call__(self, user, item):  # không được gọi
            raise AssertionError

    recs = [EvalRecord(0, 3, np.array([1, 2, 3], dtype=np.int64))]
    assert evaluate_score_function(Scorer(), recs, [1])["HR@1"] == 1.0


def test_hybrid_alpha_extremes():
    class CF(torch.nn.Module):
        def forward(self, u, i):
            return (i == 1).float()

    class CB:
        def score_items(self, user, items):
            return (np.asarray(items) == 2).astype(float)

    items = np.array([0, 1, 2])
    assert HybridScorer(CF(), CB(), 1.0).score_items(0, items).argmax() == 1
    assert HybridScorer(CF(), CB(), 0.0).score_items(0, items).argmax() == 2
    recs = [EvalRecord(0, 2, items)]
    best, scores = tune_hybrid_alpha(CF(), CB(), recs, [0.0, 1.0])
    assert best == 0.0 and scores[0.0] > scores[1.0]


def test_load_hm_item_features_maps_to_item_index(tmp_path):
    pd.DataFrame({
        "article_id": ["0108775015", "0108775044"],
        "product_type_name": ["Vest top", "Bra"],
    }).to_csv(tmp_path / "articles.csv", index=False)
    item2idx = {"0108775044": 0, "0108775015": 1}
    df = load_hm_item_features(item2idx, tmp_path / "articles.csv", ["product_type_name"])
    assert df.loc[0, "product_type_name"] == "Bra"
    assert df.loc[1, "product_type_name"] == "Vest top"


def test_load_hm_features_via_id_map_for_parquet_codes(tmp_path):
    pd.DataFrame({"article_id": ["0000000001"], "product_type_name": ["Bra"]}).to_csv(
        tmp_path / "articles.csv", index=False)
    pd.DataFrame({"article_id": ["0000000001"], "item_raw": [7]}).to_parquet(tmp_path / "imap.parquet")
    df = load_hm_item_features({7: 0}, tmp_path / "articles.csv", ["product_type_name"], tmp_path / "imap.parquet")
    assert df.loc[0, "product_type_name"] == "Bra"

    pd.DataFrame({"customer_id": ["c1"], "age": [30]}).to_csv(tmp_path / "customers.csv", index=False)
    pd.DataFrame({"customer_id": ["c1"], "user_raw": [5]}).to_parquet(tmp_path / "umap.parquet")
    assert load_hm_user_age_groups([5], tmp_path / "customers.csv", tmp_path / "umap.parquet") == {5: "25-34"}


def test_strict_cold_start_only_excluded_users_and_known_items():
    rows = []
    for u in ("a", "b"):  # 2 user x 3 item -> sống sót k-core=2
        for i in ("x", "y", "z"):
            rows.append((u, i))
    rows += [("new", "x"), ("new", "y"), ("new", "unknown_item"), ("solo", "x")]
    events = pd.DataFrame(rows, columns=["user_raw", "item_raw"])
    events["timestamp"] = pd.Timestamp("2020-01-01") + pd.to_timedelta(np.arange(len(events)), "D")
    events["value_raw"] = 1.0
    events["source_order"] = np.arange(len(events))

    data = build_interactions(events[events.user_raw.isin(["a", "b"])], k_core=2)
    profile, test, raw_by_idx = build_strict_cold_start(events, data, max_users=None)
    assert list(raw_by_idx.values()) == ["new"]  # "solo" chỉ có 1 item -> loại
    assert test.item.tolist() == [data.item2idx["y"]]  # item cuối trong catalog
    assert profile.item.tolist() == [data.item2idx["x"]]
    assert set(test.user) == {data.n_users}
