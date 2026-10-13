"""ItemKNN / UserKNN thưa top-K (src/baselines/neighborhood.py) và late fusion (src/models/late_fusion.py)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import torch

from src.baselines import ItemKNNBaseline, UserKNNBaseline
from src.baselines.neighborhood import interaction_matrix, topk_cosine
from src.models.late_fusion import LateFusion, minmax
from src.models.neumf import GMF, MLP


def _toy():
    # 5 user × 6 item, mỗi cặp là một lần mua
    pairs = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 1), (2, 2), (2, 3), (3, 3), (3, 4), (4, 4), (4, 5), (4, 0)]
    return pd.DataFrame(pairs, columns=["user", "item"]), 5, 6


def _dense_cosine(X, shrink=0.0):
    X = X.astype(float)
    co = X @ X.T
    n = np.sqrt(np.diag(co))
    sim = co / (n[:, None] * n[None, :] + shrink)
    np.fill_diagonal(sim, 0.0)
    return sim


def _topk_dense(sim, k):
    out = np.zeros_like(sim)
    for r in range(len(sim)):
        idx = np.argsort(-sim[r], kind="stable")[:k]
        out[r, idx] = sim[r, idx]
    out[out < 0] = 0
    return out


@pytest.mark.parametrize("k,shrink", [(1, 0.0), (2, 0.0), (3, 5.0), (10, 0.0)])
def test_topk_cosine_matches_dense_bruteforce(k, shrink):
    df, nu, ni = _toy()
    X = interaction_matrix(df, nu, ni)
    got = topk_cosine(X, k, shrink, block=2).toarray()
    sim = _dense_cosine(X.toarray(), shrink)
    for r in range(nu):
        # cùng tập giá trị top-k (hoà điểm có thể chọn chỉ số khác nhau) và chỉ giữ sim > 0
        assert np.allclose(np.sort(got[r][got[r] > 0]), np.sort(_topk_dense(sim, k)[r][_topk_dense(sim, k)[r] > 0]))


def test_itemknn_scores_follow_definition():
    df, nu, ni = _toy()
    model = ItemKNNBaseline(df, nu, ni, k=ni, shrink=0.0)  # k đủ lớn -> giữ mọi láng giềng
    sim = _dense_cosine(interaction_matrix(df, nu, ni).toarray().T)  # item × item
    X = interaction_matrix(df, nu, ni).toarray()
    for u in range(nu):
        expected = sim @ X[u]  # điểm item j = tổng sim(j, i) trên item i user đã mua
        assert np.allclose(model.score_items(u, np.arange(ni)), expected)


def test_userknn_scores_and_neighbors():
    df, nu, ni = _toy()
    model = UserKNNBaseline(df, nu, ni, k=2, shrink=0.0)
    X = interaction_matrix(df, nu, ni).toarray()
    sim = _topk_dense(_dense_cosine(X), 2)
    for u in range(nu):
        assert np.allclose(model.score_items(u, np.arange(ni)), sim[u] @ X)
    nb = model.neighbors(0, top=2)
    assert [n["similarity"] for n in nb] == sorted([n["similarity"] for n in nb], reverse=True)
    assert all(n["n_common"] == int((X[0] * X[n["user"]]).sum()) for n in nb)


def test_minmax_constant_is_zero():
    assert np.all(minmax(np.array([3.0, 3.0, 3.0])) == 0.0)
    assert np.allclose(minmax(np.array([1.0, 3.0, 2.0])), [0.0, 1.0, 0.5])


def test_late_fusion_extremes_reproduce_component_ranking():
    torch.manual_seed(0)
    gmf, mlp = GMF(6, 9, 4).eval(), MLP(6, 9, 4, [8, 4, 2, 1], 0.0).eval()
    items = np.arange(9)
    for user in range(6):
        with torch.no_grad():
            u = torch.full((9,), user, dtype=torch.long)
            g = gmf(u, torch.arange(9)).numpy()
            m = mlp(u, torch.arange(9)).numpy()
        assert np.array_equal(np.argsort(-LateFusion(gmf, mlp, 1.0).score_items(user, items), kind="stable"),
                              np.argsort(-g, kind="stable"))
        assert np.array_equal(np.argsort(-LateFusion(gmf, mlp, 0.0).score_items(user, items), kind="stable"),
                              np.argsort(-m, kind="stable"))
    with pytest.raises(ValueError):
        LateFusion(gmf, mlp, 1.5)
