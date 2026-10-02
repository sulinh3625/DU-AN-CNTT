"""Mở rộng PREREG mục 9: ItemKNN/UserKNN thưa top-K, late fusion MF + DNN, chỉ số @K từ hạng đã lưu, khoá test."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import torch

from src.baselines import ItemKNNBaseline, UserKNNBaseline
from src.baselines.neighborhood import interaction_matrix, topk_cosine
from src.evaluation.full_ranking import EvalRecord, evaluate_score_function
from src.evaluation.metrics import multi_ranking_metrics
from src.models.late_fusion import CachedLateFusion, LateFusion, fusion_cache, minmax
from src.models.neumf import GMF, MLP

ROOT = Path(__file__).resolve().parents[1]


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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


def _nets(nu=6, ni=9):
    torch.manual_seed(0)
    return GMF(nu, ni, 4).eval(), MLP(nu, ni, 4, [8, 4, 2, 1], 0.0).eval()


def test_late_fusion_extremes_reproduce_component_ranking():
    gmf, mlp = _nets()
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


def test_cached_late_fusion_equals_direct():
    gmf, mlp = _nets()
    records = [EvalRecord(user=u, positive_item=u, candidates=np.arange(9)) for u in range(6)]
    cache = fusion_cache(gmf, mlp, records)
    for w in (0.0, 0.3, 1.0):
        direct = evaluate_score_function(LateFusion(gmf, mlp, w), records, [5])
        cached = evaluate_score_function(CachedLateFusion(cache, w), records, [5])
        assert direct == cached


def test_extra_k_matches_metric_formula():
    extra = _load("extra_k", "16_extra_k.py")
    per = pd.DataFrame([{"model": "A", "seed": 1, "user": 0, "ranks": "2;7;40"},
                        {"model": "A", "seed": 1, "user": 1, "ranks": "25"}])
    got = extra.metrics_at_k(per, 20)
    for row, ranks in zip(got.itertuples(index=False), ([2, 7, 40], [25])):
        m = multi_ranking_metrics(ranks, 20)
        assert row._3 == pytest.approx(m["NDCG"]) and row._6 == pytest.approx(m["Precision"])


def test_extension_refuses_without_registered_prereg(monkeypatch):
    ext = _load("ext", "17_extension.py")
    monkeypatch.setattr(sys, "argv", ["17_extension.py", "--reason", "x"])
    monkeypatch.setattr(ext, "prereg_committed", lambda p: False)
    with pytest.raises(SystemExit, match="PREREG"):
        ext.main()


def test_extension_refuses_without_reason(monkeypatch):
    ext = _load("ext", "17_extension.py")
    monkeypatch.setattr(sys, "argv", ["17_extension.py"])
    monkeypatch.setattr(ext, "prereg_committed", lambda p: True)
    monkeypatch.setattr(ext, "PREREG_MARKER", "")  # coi như mục 9 đã có
    with pytest.raises(SystemExit, match="--reason"):
        ext.main()


def test_extension_comparisons_use_known_models():
    ext = _load("ext", "17_extension.py")
    known = set(ext.MODELS) | {"NeuMF-Scratch", "NeuMF-Pretrained", "GMF", "MLP", "BPR-MF"}
    assert all(a in known and b in known for a, b in ext.EXT_COMPARISONS)
    assert len(ext.EXT_COMPARISONS) == 7
