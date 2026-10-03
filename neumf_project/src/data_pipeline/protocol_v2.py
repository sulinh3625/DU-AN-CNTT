"""Giao thức đánh giá v2 (audit/PREREG_v2.md).

Khác giao thức cũ:
1. Lọc k-core chỉ trên các cặp (user, item) có lần mua đầu TRƯỚC mốc kiểm thử — không dùng thông tin của giai đoạn
   kiểm thử để chọn dữ liệu.
2. Mỗi giai đoạn (xác thực: mốc val_start; kiểm thử: mốc test_start) có:
   - tập huấn luyện = các cặp đã lọc k-core có ngày mua đầu < mốc cắt;
   - sản phẩm "chấm được bằng ID" (scoreable) = sản phẩm có ít nhất một cặp huấn luyện;
   - sản phẩm mới = sản phẩm trong catalogue chưa từng bán (toàn bộ H&M) trước mốc cắt — giả định doanh nghiệp biết
     trước danh mục sắp bán, nhưng không biết sản phẩm nào sẽ bán được;
   - ứng viên của một người dùng = scoreable ∪ sản phẩm mới, trừ sản phẩm người dùng đã mua trước mốc;
   - sản phẩm đúng = các cặp mua lần đầu trong cửa sổ sau mốc cắt của người dùng đã có lịch sử, sản phẩm thuộc ứng viên.
Mô hình chỉ dùng ID không chấm được sản phẩm mới -> chúng bị xếp cuối (MaskedScorer); mô hình có đặc trưng chấm được.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from src.evaluation.full_ranking import EvalRecord, build_full_ranking_records_multi

from .adapters import HMAdapter
from .features import (Catalog, DailySales, build_user_profile, item_time_features, to_day,
                       user_time_features)
from .kcore import iterative_k_core
from .negative_sampling import build_user_positive_sets
from .preprocessing import aggregate_unique_user_item


@dataclass
class Stage:
    name: str
    cutoff: int  # chỉ số ngày của mốc cắt
    train: pd.DataFrame  # user, item, day, sample_weight
    train_pos: list
    scoreable: np.ndarray  # bool [n_items]
    new: np.ndarray  # bool [n_items]
    targets: pd.DataFrame  # user, item, day — cặp mua lần đầu trong cửa sổ đánh giá
    records: list[EvalRecord]
    user_time: np.ndarray  # float32 [n_users, USER_TIME_DIM] tại mốc cắt

    @property
    def pool(self) -> np.ndarray:
        return np.flatnonzero(self.scoreable | self.new)


@dataclass
class DataV2:
    n_users: int
    n_items: int
    n_id_items: int  # item [0, n_id_items) có trong dữ liệu đã lọc k-core; phần sau chỉ là sản phẩm mới
    user_raw: np.ndarray
    item_article: np.ndarray  # article_id (int64) theo chỉ số item
    kept: pd.DataFrame  # mọi cặp đã lọc k-core (trước mốc kiểm thử)
    item_cats: np.ndarray
    item_text: np.ndarray
    item_cum: np.ndarray  # doanh số cộng dồn toàn H&M [n_items, n_days + 1]
    item_first_day: np.ndarray
    item_cards: list
    user_cats: np.ndarray | None
    user_cards: list
    val: Stage
    test: Stage | None = None
    meta: dict = field(default_factory=dict)

    def item_time(self, items, day) -> np.ndarray:
        return item_time_features(self.item_cum, self.item_first_day, items, day)


def build_v2(sample_path: str | Path, val_start: str, test_start: str, k_core: int, catalog: Catalog,
             sales: DailySales, customers_path: str | Path | None = None, with_test: bool = False) -> DataV2:
    events = HMAdapter(sample_path).load_events()
    agg = aggregate_unique_user_item(events)
    agg["article"] = agg["item_raw"].astype("int64")
    agg["day"] = to_day(agg["first_timestamp"].to_numpy())
    vd, td = int(to_day(np.datetime64(val_start))), int(to_day(np.datetime64(test_start)))
    if not vd < td:
        raise ValueError(f"Cần val_start < test_start, nhận {val_start} / {test_start}")

    kept = iterative_k_core(agg[agg["day"] < td], k_core)
    if kept.empty:
        raise ValueError(f"Không còn dữ liệu sau k-core={k_core}")
    users = np.array(sorted(kept["user_raw"].unique(), key=str), dtype=object)
    id_articles = np.sort(kept["article"].unique())
    cat_new = catalog.article_ids[(sales.first_day >= vd) & ~np.isin(catalog.article_ids, id_articles)]
    item_article = np.concatenate([id_articles, np.sort(cat_new)]).astype(np.int64)
    n_users, n_items, n_id = len(users), len(item_article), len(id_articles)

    user_index = pd.Series(np.arange(n_users), index=pd.Index(users))
    item_index = pd.Series(np.arange(n_items), index=pd.Index(item_article))
    rows = catalog.rows(item_article)

    def index_pairs(df: pd.DataFrame) -> pd.DataFrame:
        out = df[df["user_raw"].isin(user_index.index) & df["article"].isin(item_index.index)].copy()
        out["user"] = user_index.loc[out["user_raw"]].to_numpy(np.int64)
        out["item"] = item_index.loc[out["article"]].to_numpy(np.int64)
        out["sample_weight"] = 1.0
        return out.reset_index(drop=True)

    kept_i = index_pairs(kept)
    pairs = index_pairs(agg)
    data = DataV2(
        n_users=n_users, n_items=n_items, n_id_items=n_id, user_raw=users, item_article=item_article, kept=kept_i,
        item_cats=catalog.cats[rows], item_text=catalog.text[rows], item_cum=sales.cumulative(rows),
        item_first_day=sales.first_day[rows], item_cards=list(catalog.cardinalities),
        user_cats=None, user_cards=[], val=None,  # type: ignore[arg-type]
        meta=dict(val_day=vd, test_day=td, k_core=k_core, n_days=sales.n_days, sample=str(sample_path)))
    if customers_path is not None:
        prof = build_user_profile(customers_path, users)
        data.user_cats, data.user_cards = prof.cats, prof.cardinalities
    end_day = sales.n_days
    data.val = make_stage("val", vd, td, kept_i, pairs, data)
    if with_test:
        data.test = make_stage("test", td, end_day, kept_i, pairs, data)
    return data


def make_stage(name: str, cutoff: int, window_end: int, kept: pd.DataFrame, pairs: pd.DataFrame,
               data: DataV2) -> Stage:
    train = kept[kept["day"] < cutoff].reset_index(drop=True)
    scoreable = np.zeros(data.n_items, dtype=bool)
    scoreable[train["item"].unique()] = True
    new = data.item_first_day >= cutoff
    pool = scoreable | new
    users = np.unique(train["user"].to_numpy())
    t = pairs[(pairs["day"] >= cutoff) & (pairs["day"] < window_end) & pairs["user"].isin(users)]
    targets = t[pool[t["item"].to_numpy()]][["user", "item", "day"]].reset_index(drop=True)
    train_pos = build_user_positive_sets(train, data.n_users)
    records = build_full_ranking_records_multi(targets, data.n_items, train_pos, item_pool=np.flatnonzero(pool))
    utime = user_time_features(train["user"].to_numpy(), train["day"].to_numpy(), np.arange(data.n_users), cutoff)
    return Stage(name, cutoff, train, train_pos, scoreable, new, targets, records, utime)


def describe(data: DataV2) -> dict:
    out = dict(n_users=data.n_users, n_items=data.n_items, n_id_items=data.n_id_items, n_kept_pairs=len(data.kept))
    for st in (data.val, data.test):
        if st is None:
            continue
        new_targets = st.new[st.targets["item"].to_numpy()]
        out[st.name] = dict(train_pairs=len(st.train), scoreable=int(st.scoreable.sum()), new_items=int(st.new.sum()),
                            users=len(st.records), targets=len(st.targets), new_item_targets=int(new_targets.sum()),
                            candidates_mean=float(np.mean([len(r.candidates) for r in st.records])))
    return out
