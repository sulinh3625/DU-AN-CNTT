"""Mô hình lai truyền thống Hybrid-CBCF (src/baselines/hybrid.py) và đánh giá bổ sung (scripts/25_bosung.py,
audit/PREREG_bosung.md): chuẩn hoá trên tập ứng viên, bốn cách kết hợp, học trọng số theo cặp, khớp chéo theo khách,
khoá kiểm thử."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from src.baselines.hybrid import TraditionalHybrid, combine, crossfit_scores, fit_weights, pair_differences

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


class Table:
    """Thành phần giả: điểm lấy từ bảng khách × sản phẩm."""

    def __init__(self, rows):
        self.rows = np.asarray(rows, dtype=float)

    def score_items(self, user, items):
        return self.rows[int(user), np.asarray(items, dtype=np.int64)]


def test_features_are_minmax_on_the_candidate_set():
    h = TraditionalHybrid([Table([[1, 2, 3, 5]]), Table([[0, 0, 4, 2]]), Table([[7, 7, 7, 7]])], "mean")
    x = h.features(0, [0, 1, 3])  # chuẩn hoá trên chính tập ứng viên, không phải trên mọi sản phẩm
    assert np.allclose(x[:, 0], [0, 0.25, 1])
    assert np.allclose(x[:, 1], [0, 0, 1])
    assert np.allclose(x[:, 2], 0)  # điểm như nhau -> không mang thông tin
    assert np.allclose(h.score_items(0, [0, 1, 3]), x.mean(axis=1))


def test_four_fusions():
    x = np.array([[0.2, 0.8, 0.5], [1.0, 0.0, 0.3]])
    assert np.allclose(combine(x, "mean"), [0.5, 1.3 / 3])
    assert np.allclose(combine(x, "max"), [0.8, 1.0])
    assert np.allclose(combine(x, "min"), [0.2, 0.0])
    assert np.allclose(combine(x, "lr", [1.0, 2.0, 0.0]), [1.8, 1.0])
    with pytest.raises(ValueError):
        combine(x, "vote")
    with pytest.raises(ValueError):
        TraditionalHybrid([Table([[0]])] * 3, "lr")  # cách 'lr' cần trọng số


def _synthetic(n_users=60, n_items=80, seed=1):
    """Thành phần 0 là nhiễu, thành phần 1 đẩy sản phẩm đúng lên mạnh, thành phần 2 yếu hơn."""
    rng = np.random.default_rng(seed)
    feats, labels = [], []
    for _ in range(n_users):
        y = np.zeros(n_items, dtype=bool)
        y[rng.choice(n_items, 3, replace=False)] = True
        feats.append(np.column_stack([rng.random(n_items), 0.6 * y + 0.4 * rng.random(n_items),
                                      0.2 * y + 0.8 * rng.random(n_items)]))
        labels.append(y)
    return feats, labels


def test_pairwise_weights_rank_informative_components_and_are_deterministic():
    feats, labels = _synthetic()
    w = fit_weights(feats, labels)
    assert w[1] > w[2] > abs(w[0])
    assert np.array_equal(w, fit_weights(feats, labels))  # mẫu âm rút bằng seed cố định
    X, y = pair_differences(feats, labels, n_neg=5)
    assert X.shape == (2 * 60 * 3 * 5, 3) and y.sum() == len(y) // 2
    assert np.allclose(X[: len(X) // 2], -X[len(X) // 2:])  # mỗi cặp có cả hai chiều


def test_crossfit_scores_use_weights_learned_on_other_users():
    feats, labels = _synthetic()
    users = np.arange(len(feats))
    scores, w = crossfit_scores(feats, labels, users)
    odd = [i for i in users if i % 2 == 1]
    assert np.allclose(w[0], fit_weights([feats[i] for i in odd], [labels[i] for i in odd]))
    assert np.allclose(scores[0], feats[0] @ w[0]) and np.allclose(scores[1], feats[1] @ w[1])


# ------------------------------------------------------------------ 25_bosung.py: khoá kiểm thử
def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bosung = _load("bosung", "25_bosung.py")


def _args(**kw):
    return SimpleNamespace(**{**dict(reason="phân tích bổ sung", allow_rerun=False, allow_code_change=False), **kw})


def test_bosung_lock_lists_every_violation(monkeypatch):
    monkeypatch.setattr(bosung, "prereg_committed", lambda p: False)
    monkeypatch.setattr(bosung.F, "dirty_files", lambda: ["neumf_project/src/models/neumf.py"])
    monkeypatch.setattr(bosung.F, "git", lambda *a: "src/moi.py\nscripts/ghi_chu.txt\n")
    monkeypatch.setattr(bosung, "opened_tags", lambda: {bosung.RUN_TAG})
    errs = "\n".join(bosung.lock_errors(_args(reason=" "), {"code_hash": "b"}, None))
    for frag in ("PREREG_bosung.md chưa commit", "--reason", "chưa commit", "src/moi.py", "chưa tinh chỉnh",
                 bosung.RUN_TAG):
        assert frag in errs
    assert "ghi_chu.txt" not in errs


def test_bosung_lock_passes_and_overrides_are_explicit(monkeypatch):
    monkeypatch.setattr(bosung, "prereg_committed", lambda p: True)
    monkeypatch.setattr(bosung.F, "dirty_files", lambda: [])
    monkeypatch.setattr(bosung.F, "git", lambda *a: "")
    monkeypatch.setattr(bosung, "opened_tags", lambda: set())
    hb, ok = {"code_hash": "abc"}, {"code_hash": "abc"}
    assert bosung.lock_errors(_args(), ok, hb) == []
    if bosung.V.TUNED_HERE:  # H&M: mã nguồn phải trùng lúc tinh chỉnh
        assert bosung.lock_errors(_args(), {"code_hash": "khac"}, hb)
        assert bosung.lock_errors(_args(allow_code_change=True), {"code_hash": "khac"}, hb) == []
    monkeypatch.setattr(bosung, "opened_tags", lambda: {bosung.RUN_TAG})  # đã mở tập kiểm thử với run_tag này
    assert bosung.lock_errors(_args(), ok, hb)
    assert bosung.lock_errors(_args(allow_rerun=True), ok, hb) == []
    monkeypatch.setattr(bosung, "prereg_committed", lambda p: p != bosung.BEST)  # kết quả tinh chỉnh chưa commit
    assert any("chưa commit" in e for e in bosung.lock_errors(_args(allow_rerun=True), ok, hb))
