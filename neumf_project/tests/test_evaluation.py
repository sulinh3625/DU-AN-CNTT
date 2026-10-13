from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest
import torch

from src.evaluation.full_ranking import (EvalRecord, build_full_ranking_records_multi, evaluate_score_function,
                                         evaluate_torch_model)
from src.evaluation.metrics import hr_at_k, multi_ranking_metrics, ndcg_at_k, precision_at_k, recall_at_k
from src.evaluation.ranking_utils import rank_positives


def test_full_ranking_excludes_seen_and_keeps_positive():
    eval_df = pd.DataFrame({"user": [0], "item": [4]})
    rec = build_full_ranking_records_multi(eval_df, 6, [{0, 1, 2, 3, 4}])[0]
    assert rec.candidates.tolist() == [4, 5]  # món đã mua bị loại, món đúng luôn giữ


def test_multi_records_keep_all_positives_and_pool():
    eval_df = pd.DataFrame({"user": [0, 0], "item": [2, 3]})
    rec = build_full_ranking_records_multi(eval_df, 6, [{0, 1}], item_pool=[0, 1, 2, 4])[0]
    assert rec.positives.tolist() == [2, 3]              # item 3 ngoài pool vẫn giữ vì là item đúng
    assert rec.candidates.tolist() == [2, 3, 4]


def test_tie_ranking_is_deterministic():
    candidates = np.array([1, 2, 3, 4])
    scores = np.array([1.0, 1.0, 1.0, 1.0])
    r1 = rank_positives(scores, candidates, [3], user=7, tie_seed=2026)
    r2 = rank_positives(scores, candidates, [3], user=7, tie_seed=2026)
    assert r1.tolist() == r2.tolist() and 1 <= r1[0] <= 4


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


def test_perfect_model_hr_ndcg_one():
    class Perfect(torch.nn.Module):
        def forward(self, u, i):
            return (i == 5).float() * 10.0

    records = [EvalRecord(0, 5, np.array([1, 2, 5, 6], dtype=np.int64))]
    result = evaluate_torch_model(Perfect(), records, [1, 3], tie_seed=1)
    assert result["HR@1"] == 1.0
    assert result["NDCG@1"] == 1.0


def test_perfect_scorer_gets_ndcg_one_with_many_positives():
    rec = EvalRecord(0, 2, np.arange(6), np.array([2, 5]))
    res = evaluate_score_function(lambda u, i: 1.0 if i in (2, 5) else 0.0, [rec], [2], include_redundant=True)
    assert res["NDCG@2"] == 1.0 and res["Recall@2"] == 1.0 and res["HR@2"] == 1.0


def test_per_user_rows_match_summary_and_count_candidates():
    records = [EvalRecord(0, 5, np.array([1, 2, 5, 6], dtype=np.int64)),
               EvalRecord(1, 2, np.array([2, 3, 4, 7, 8], dtype=np.int64), np.array([2, 8]))]
    rows = []
    summary = evaluate_score_function(lambda u, i: float(i), records, [2], include_redundant=True, per_user=rows)
    assert [r["n_candidates"] for r in rows] == [4, 5]
    assert [r["n_positives"] for r in rows] == [1, 2]
    assert rows[0]["ranks"] == "2" and rows[1]["ranks"] == "1;5"   # điểm = id item -> 8 đứng đầu, 2 đứng cuối
    for name, value in summary.items():
        assert np.mean([r[name] for r in rows]) == value
