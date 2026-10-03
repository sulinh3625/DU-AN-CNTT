"""Giao thức v2: đặc trưng không rò rỉ thời gian, mẫu âm hợp lệ, k-core trước mốc kiểm thử, ứng viên có sản phẩm mới,
NeuMF-F nhất quán giữa lúc huấn luyện và lúc đánh giá, mô hình chỉ dùng ID xếp sản phẩm mới cuối cùng."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import torch
from scipy import sparse

from src.data_pipeline.feature_dataset import FeatureTrainDataset
from src.data_pipeline.features import (Catalog, DailySales, ITEM_TIME_DIM, item_time_features, to_day,
                                        user_time_features)
from src.data_pipeline.protocol_v2 import build_v2
from src.models.hybrid_features import ContentProfile, MaskedScoreFn, MaskedScorer, NeuMFF, RecentPopularity


def _sales(counts: np.ndarray) -> DailySales:
    c = sparse.csr_matrix(counts.astype(np.int32))
    first = np.full(counts.shape[0], counts.shape[1], dtype=np.int64)
    for r in range(counts.shape[0]):
        nz = np.flatnonzero(counts[r])
        if len(nz):
            first[r] = nz[0]
    return DailySales(c, first)


# ---------------------------------------------------------------- đặc trưng
def test_item_time_features_use_only_days_before_t():
    counts = np.zeros((2, 20), dtype=np.int64)
    counts[0, 5], counts[0, 10] = 3, 100  # bán ngày 5 và ngày 10
    ds = _sales(counts)
    cum = ds.cumulative(np.arange(2))
    f10 = item_time_features(cum, ds.first_day, np.array([0]), 10)[0]
    assert np.isclose(f10[0], np.log1p(3) / 10)  # 7 ngày trước ngày 10 = ngày 3..9: chỉ 3 giao dịch của ngày 5
    f11 = item_time_features(cum, ds.first_day, np.array([0]), 11)[0]
    assert np.isclose(f11[0], np.log1p(103) / 10)  # 100 giao dịch của ngày 10 chỉ được thấy từ ngày 11
    assert np.isclose(f10[3], np.log1p(5) / 10)  # tuổi sản phẩm: bán lần đầu ngày 5
    new = item_time_features(cum, ds.first_day, np.array([1]), 10)[0]  # sản phẩm chưa từng bán
    assert new[-1] == 1.0 and np.allclose(new[:-1], 0.0)
    launch = item_time_features(cum, ds.first_day, np.array([0]), 5)[0]  # đúng ngày ra mắt: chưa có doanh số
    assert launch[-1] == 1.0 and np.allclose(launch[:-1], 0.0)


def test_user_time_features_strictly_before_day():
    pu, pdays = np.array([0, 0, 0, 1]), np.array([3, 7, 7, 2])
    f = user_time_features(pu, pdays, np.array([0, 0, 0, 1]), np.array([3, 7, 8, 2]))
    n_before = np.expm1(f[:, 1] * 10)
    assert np.allclose(n_before, [0, 1, 3, 0])
    gap = np.expm1(f[:, 0] * 10)
    assert np.allclose(gap[[1, 2]], [4, 1]) and np.isclose(gap[0], 730)


# ------------------------------------------------------------ dữ liệu huấn luyện
def test_feature_dataset_negatives_launched_and_not_positive():
    train = pd.DataFrame({"user": [0, 0, 1, 2], "item": [0, 1, 2, 3], "day": [10, 50, 50, 50],
                          "sample_weight": 1.0})
    first = np.array([0, 40, 5, 45, 1000])  # item 4 không có trong tập huấn luyện
    ds = FeatureTrainDataset(train, n_items=5, item_first_day=first, neg_ratio=8, seed=0)
    neg = ds.labels == 0
    assert set(ds.items[neg]) <= {0, 1, 2, 3}
    assert np.all(first[ds.items[neg]] <= ds.extras["day"][neg])  # sản phẩm đã ra mắt tại ngày của mẫu
    pos = set(zip(train["user"], train["item"]))
    assert not any((int(u), int(i)) in pos for u, i in zip(ds.users[neg], ds.items[neg]))
    assert len(ds.extras["day"]) == len(ds.users) == len(ds.extras["utime"])
    early = neg & (ds.extras["day"] == 10)
    assert set(ds.items[early]) <= {0, 2}  # tại ngày 10 chỉ item 0 (ngày 0) và 2 (ngày 5) đã ra mắt; item 0 là của u0


# ------------------------------------------------------------------ giao thức
def _write_sample(path, rows):
    pd.DataFrame(rows, columns=["t_dat", "customer_id", "article_id", "price", "sales_channel_id"]).to_csv(path, index=False)


def _catalog(ids):
    ids = np.asarray(sorted(ids), dtype=np.int64)
    return Catalog(ids, np.ones((len(ids), 11), dtype=np.int32), [2] * 11, np.eye(len(ids), 4, dtype=np.float32))


def test_v2_kcore_before_test_and_new_item_candidates(tmp_path):
    day = lambda s: str(np.datetime64("2018-09-20") + np.timedelta64(s, "D"))  # noqa: E731
    rows = []
    for u in ("a", "b", "c"):
        rows += [(day(1), u, 101, 1, 1), (day(2), u, 102, 1, 1), (day(30), u, 103, 1, 1)]
    rows += [(day(61), "a", 104, 1, 1), (day(62), "b", 105, 1, 1), (day(62), "c", 101, 1, 1)]
    rows += [(day(70), "z", 106, 1, 1)] * 5  # khách z chỉ mua trong giai đoạn kiểm thử
    sample = tmp_path / "s.csv"
    _write_sample(sample, rows)
    ids = [101, 102, 103, 104, 105, 106, 107]
    counts = np.zeros((len(ids), 100), dtype=np.int64)
    for a, d in ((101, 1), (102, 2), (103, 30), (104, 61), (105, 55), (106, 70)):  # 107 chưa từng bán
        counts[ids.index(a), d] = 1
    data = build_v2(sample, day(40), day(60), 2, _catalog(ids), _sales(counts), with_test=True)
    assert "z" not in set(data.user_raw)  # k-core chỉ trên dữ liệu trước mốc kiểm thử
    art = lambda i: int(data.item_article[i])  # noqa: E731
    st = data.test
    assert {art(i) for i in np.flatnonzero(st.new)} == {104, 106, 107}  # chưa bán (toàn H&M) trước mốc
    assert {art(i) for i in np.flatnonzero(st.scoreable)} == {101, 102, 103}
    tg = {(data.user_raw[u], art(i)) for u, i in zip(st.targets["user"], st.targets["item"])}
    assert tg == {("a", 104)}  # 105 đã bán trước mốc nhưng không có trong dữ liệu huấn luyện; 101 của c là mua lại
    rec = st.records[0]
    assert {art(i) for i in rec.candidates} == {104, 106, 107}  # a đã mua 101-103
    assert set(data.val.train["day"]) == {1, 2, 30} and data.val.cutoff == 40


# ---------------------------------------------------------------- mô hình
def _toy_model(**kw):
    torch.manual_seed(0)
    m = NeuMFF(n_users=3, n_id_items=4, item_cards=[3] * 11, user_cards=[9, 4, 4, 3, 3], text_dim=4, gmf_dim=8,
               mlp_dim=8, **kw)
    n_items = 6
    cum = np.cumsum(np.random.default_rng(0).integers(0, 5, size=(n_items, 31)), axis=1)
    cum = np.concatenate([np.zeros((n_items, 1)), cum], axis=1)
    m.attach(np.random.default_rng(1).integers(0, 3, size=(n_items, 11)), np.random.default_rng(2).random((n_items, 4)),
             cum, np.array([0, 3, 5, 9, 31, 40]), np.ones((3, 5), dtype=np.int64))
    return m, cum


def test_neumff_eval_matches_training_path_and_time_features():
    m, cum = _toy_model()
    first = np.array([0, 3, 5, 9, 31, 40])
    items = torch.arange(6)
    np_feat = item_time_features(cum, first, np.arange(6), 20)
    assert np.allclose(m.item_time(items, torch.full((6,), 20)).numpy(), np_feat, atol=1e-6)
    assert np_feat.shape[1] == ITEM_TIME_DIM
    utime = np.random.default_rng(3).random((3, 2)).astype(np.float32)
    m.set_stage(20, utime, np.array([True, True, True, True, False, False]))
    m.eval()
    users = torch.tensor([0, 1, 2, 0, 1, 2])
    ev = m(users, items)
    tr = m(users, items, day=torch.full((6,), 20), utime=torch.as_tensor(utime[[0, 1, 2, 0, 1, 2]]))
    assert torch.allclose(ev, tr, atol=1e-5)  # sản phẩm 4, 5 (>= n_id) không có ID ở cả hai đường


def test_neumff_branch_flags_and_new_items_scored():
    for kw in (dict(use_gmf=False), dict(use_mlp=False), dict(use_text=False, use_time=False), dict(id_dropout=0.5)):
        m, _ = _toy_model(**kw)
        m.set_stage(20, np.zeros((3, 2), np.float32), np.ones(6, dtype=bool))
        m.eval()
        s = m(torch.zeros(6, dtype=torch.long), torch.arange(6))
        assert torch.isfinite(s).all() and s.shape == (6,)
    with pytest.raises(ValueError):
        NeuMFF(3, 4, [3] * 11, [9, 4, 4, 3, 3], 4, use_gmf=False, use_mlp=False)


def test_masked_scorer_puts_unscoreable_items_last():
    class Const(torch.nn.Module):
        def forward(self, u, i):
            return i.float()
    sc = MaskedScorer(Const(), np.array([True, False, True, False, False]), n_model_items=3)
    s = sc(torch.zeros(5, dtype=torch.long), torch.arange(5))
    assert torch.isinf(s[[1, 3, 4]]).all() and s[0] == 0 and s[2] == 2

    class ConstNp:
        def score_items(self, u, items):
            return np.asarray(items, dtype=float)
    f = MaskedScoreFn(ConstNp(), np.array([True, False, True, False]), n_model_items=3)
    assert np.isneginf(f.score_items(0, [1, 3])).all() and f.score_items(0, [2])[0] == 2


def test_recent_popularity_and_content_profile():
    cum = np.cumsum(np.array([[0, 5, 5, 5], [0, 0, 0, 9]]), axis=1)
    cum = np.concatenate([np.zeros((2, 1)), cum], axis=1)
    rp = RecentPopularity(cum, cutoff=3, window=2)
    assert list(rp.score_items(0, [0, 1])) == [10.0, 0.0]  # ngày 3 (9 giao dịch của item 1) chưa được thấy
    text = np.eye(3, 4, dtype=np.float32)
    cats = np.zeros((3, 11), dtype=np.int64)
    cp = ContentProfile(text, cats, [2] * 11, pd.DataFrame({"user": [0], "item": [0], "day": [1]}), n_users=1,
                        cutoff=5)
    s = cp.score_items(0, [0, 1, 2])
    assert s[0] > s[1] and s[0] > s[2]  # sản phẩm giống lịch sử nhất được chấm cao nhất, kể cả sản phẩm chưa có ID
