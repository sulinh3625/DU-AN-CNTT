from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from src.data_pipeline.splitting import assert_disjoint_splits, global_temporal_split, refit_data
from src.evaluation.full_ranking import EvalRecord, build_full_ranking_records_multi, evaluate_score_function
from src.evaluation.long_tail import split_records_head_tail
from src.evaluation.metrics import hr_at_k, multi_ranking_metrics, ndcg_at_k, precision_at_k, recall_at_k
from src.evaluation.ranking_utils import rank_positive, rank_positives


@pytest.mark.parametrize("rank", [1, 2, 3, 7, 10, 11, 500])
@pytest.mark.parametrize("k", [1, 5, 10, 20])
def test_multi_metrics_equal_single_item_formulas(rank, k):
    m = multi_ranking_metrics([rank], k)
    assert m["HR"] == hr_at_k(rank, k)
    assert m["NDCG"] == ndcg_at_k(rank, k)
    assert m["Precision"] == precision_at_k(rank, k)
    assert m["Recall"] == recall_at_k(rank, k)


def test_multi_metrics_two_relevant_items():
    m = multi_ranking_metrics([1, 4], k=3)
    assert m["HR"] == 1.0 and m["Recall"] == 0.5 and m["Precision"] == pytest.approx(1 / 3)
    assert m["NDCG"] == pytest.approx(1.0 / (1.0 + 1 / math.log2(3)))
    assert multi_ranking_metrics([1, 2], k=10)["NDCG"] == pytest.approx(1.0)  # thứ tự lý tưởng


def test_rank_positives_matches_rank_positive():
    rng = np.random.default_rng(0)
    cand = np.arange(50)
    scores = rng.integers(0, 5, size=50).astype(float)  # nhiều tie
    for pos in (3, 17, 42):
        assert rank_positives(scores, cand, [pos], 9, 2026).tolist() == [rank_positive(scores, cand, pos, 9, 2026)]


def test_global_split_uses_one_cutoff_and_keeps_only_warm_users_items():
    t = pd.Timestamp
    df = pd.DataFrame({
        "user": [0, 0, 1, 1, 0, 1, 2, 0, 1],
        "item": [0, 1, 0, 2, 2, 1, 1, 9, 3],
        "first_timestamp": [t("2020-01-01"), t("2020-01-05"), t("2020-01-02"), t("2020-01-20"),  # train
                            t("2020-02-10"),                                                   # val
                            t("2020-03-01"),                                                   # test
                            t("2020-03-02"),   # user 2 không có lịch sử train -> bỏ
                            t("2020-03-03"),   # item 9 chưa từng bán trước test -> bỏ
                            t("2020-02-15")],  # item 3 chưa có trong train -> bỏ khỏi val
    })
    df = pd.concat([df, pd.DataFrame({"user": [0], "item": [3], "first_timestamp": [t("2020-03-04")]})],
                   ignore_index=True)  # item 3 mới có từ val -> test vẫn giữ (mô hình train lại trên train ∪ val)
    train, val, test = global_temporal_split(df, "2020-02-01", "2020-02-28")
    assert set(zip(train.user, train.item)) == {(0, 0), (0, 1), (1, 0), (1, 2)}
    assert set(zip(val.user, val.item)) == {(0, 2)}
    assert set(zip(test.user, test.item)) == {(1, 1), (0, 3)}
    refit = refit_data(df, "2020-02-28")
    assert set(zip(refit.user, refit.item)) == {(0, 0), (0, 1), (1, 0), (1, 2), (0, 2), (1, 3)}
    assert_disjoint_splits(train, val, test)
    assert train["first_timestamp"].max() < pd.Timestamp("2020-02-01") <= val["first_timestamp"].min()
    with pytest.raises(ValueError):
        global_temporal_split(df, "2020-03-01", "2020-02-01")


def test_multi_records_keep_all_positives_and_pool():
    eval_df = pd.DataFrame({"user": [0, 0], "item": [2, 3]})
    rec = build_full_ranking_records_multi(eval_df, 6, [{0, 1}], item_pool=[0, 1, 2, 4])[0]
    assert rec.positives.tolist() == [2, 3]              # item 3 ngoài pool vẫn giữ vì là item đúng
    assert rec.candidates.tolist() == [2, 3, 4]


def test_perfect_scorer_gets_ndcg_one_with_many_positives():
    rec = EvalRecord(0, 2, np.arange(6), np.array([2, 5]))
    res = evaluate_score_function(lambda u, i: 1.0 if i in (2, 5) else 0.0, [rec], [2], include_redundant=True)
    assert res["NDCG@2"] == 1.0 and res["Recall@2"] == 1.0 and res["HR@2"] == 1.0


def test_head_tail_split_separates_mixed_records():
    rec = EvalRecord(0, 1, np.arange(6), np.array([1, 4]))
    head, tail = split_records_head_tail([rec], head_items={1})
    assert head[0].positives.tolist() == [1] and 4 not in head[0].candidates
    assert tail[0].positives.tolist() == [4] and 1 not in tail[0].candidates
    single = EvalRecord(0, 4, np.arange(6))
    assert split_records_head_tail([single], {1}) == ([], [single])
