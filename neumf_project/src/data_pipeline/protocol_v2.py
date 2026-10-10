"""Giao thức đánh giá v2 (audit/PREREG_v2.md).

Khác giao thức cũ:
1. Lọc k-core chỉ trên các cặp (user, item) có lần mua đầu TRƯỚC mốc kiểm thử — không dùng thông tin của giai đoạn
   kiểm thử để chọn dữ liệu.
2. Mỗi giai đoạn (xác thực: mốc val_start; kiểm thử: mốc test_start) có:
   - tập huấn luyện = các cặp đã lọc k-core có ngày mua đầu < mốc cắt;
   - sản phẩm "chấm được" (scoreable) = sản phẩm có ít nhất một cặp huấn luyện;
   - ứng viên của một người dùng = sản phẩm chấm được, trừ sản phẩm người dùng đã mua trước mốc;
   - sản phẩm đúng = các cặp mua lần đầu trong cửa sổ sau mốc cắt của người dùng đã có lịch sử, sản phẩm chấm được.
   Sản phẩm chưa có người mua trước mốc cắt không nằm trong tập ứng viên lẫn đáp án.

Dữ liệu đi qua một file chung để mọi mô hình đọc cùng dữ liệu (scripts/02_prepare_data.py, kiểm bằng MD5):
- prepare_pairs: sự kiện theo schema DatasetAdapter -> mọi cặp đã gộp kèm cờ in_kcore (không riêng H&M);
- save_pairs / load_pairs: ghi / đọc file cặp, cùng dữ liệu ra cùng bytes;
- build_from_pairs: file cặp + catalog/doanh số đã gộp theo sản phẩm -> DataV2.
build_v2 làm cả ba bước trong bộ nhớ cho H&M (HMAdapter, gộp màu theo product_code).
"""
from __future__ import annotations

import gzip
import hashlib
import io
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from src.evaluation.full_ranking import EvalRecord, build_full_ranking_records_multi

from .adapters import HMAdapter
from .features import (Catalog, DailySales, build_user_profile, group_by_product, item_time_features, product_code_of,
                       to_day, user_time_features)
from .kcore import iterative_k_core
from .negative_sampling import build_user_positive_sets
from .preprocessing import aggregate_unique_user_item

PAIR_COLUMNS = ["user_id", "item_id", "first_day", "in_kcore"]


@dataclass
class Stage:
    name: str
    cutoff: int  # chỉ số ngày của mốc cắt
    train: pd.DataFrame  # user, item, day, sample_weight
    train_pos: list
    scoreable: np.ndarray  # bool [n_items]
    targets: pd.DataFrame  # user, item, day — cặp mua lần đầu trong cửa sổ đánh giá
    records: list[EvalRecord]
    user_time: np.ndarray  # float32 [n_users, USER_TIME_DIM] tại mốc cắt

    @property
    def pool(self) -> np.ndarray:
        return np.flatnonzero(self.scoreable)


@dataclass
class DataV2:
    n_users: int
    n_items: int
    n_id_items: int  # = n_items: mọi sản phẩm đều có cặp trong dữ liệu đã lọc k-core
    user_raw: np.ndarray
    item_product: np.ndarray  # mã sản phẩm theo chỉ số item (H&M: product_code, int64)
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


def prepare_pairs(events: pd.DataFrame, test_start: str, k_core: int, item_map=None) -> pd.DataFrame:
    """Mọi cặp (khách, sản phẩm) đã gộp từ sự kiện theo schema DatasetAdapter (user_raw, item_raw, timestamp,
    value_raw, source_order), cột PAIR_COLUMNS, sắp xếp ổn định theo (user_id, item_id).

    item_map (nếu có) đổi mã sản phẩm TRƯỚC khi gộp cặp — với H&M là product_code_of: hai màu của cùng một mẫu do một
    khách mua chỉ còn một cặp, first_day là lần mua sớm nhất. k-core lặp chỉ trên các cặp có ngày mua đầu < test_start;
    in_kcore = cặp nằm trong kết quả k-core."""
    if item_map is not None:
        events = events.assign(item_raw=item_map(events["item_raw"]))
    agg = aggregate_unique_user_item(events)
    agg["day"] = to_day(agg["first_timestamp"].to_numpy())
    kept = iterative_k_core(agg[agg["day"] < int(to_day(np.datetime64(test_start)))], k_core)
    if kept.empty:
        raise ValueError(f"Không còn dữ liệu sau k-core={k_core}")
    key = ["user_raw", "item_raw"]
    in_core = pd.MultiIndex.from_frame(agg[key]).isin(pd.MultiIndex.from_frame(kept[key]))
    out = pd.DataFrame({"user_id": agg["user_raw"], "item_id": agg["item_raw"], "first_day": agg["day"],
                        "in_kcore": in_core})
    return out.sort_values(["user_id", "item_id"], kind="mergesort").reset_index(drop=True)


def save_pairs(pairs: pd.DataFrame, path: str | Path) -> str:
    """Ghi file cặp (CSV nén gzip) sao cho cùng dữ liệu luôn ra cùng bytes; trả về MD5 của CSV chưa nén."""
    data = (pairs[PAIR_COLUMNS].astype({"first_day": "int64", "in_kcore": "bool"})
            .to_csv(index=False, lineterminator="\n").encode("utf-8"))
    with gzip.GzipFile(path, "wb", mtime=0) as f:
        f.write(data)
    return hashlib.md5(data).hexdigest()


def load_pairs(path: str | Path, md5: str) -> pd.DataFrame:
    """Đọc file cặp của save_pairs; ValueError nếu MD5 của nội dung đã giải nén khác `md5`."""
    with gzip.open(path, "rb") as f:
        data = f.read()
    got = hashlib.md5(data).hexdigest()
    if got != md5:
        raise ValueError(f"{path}: MD5 {got} khác MD5 đã ghi ({md5})")
    return pd.read_csv(io.BytesIO(data), dtype={"user_id": str, "first_day": "int64", "in_kcore": bool})


def build_from_pairs(pairs: pd.DataFrame, val_start: str, test_start: str, catalog: Catalog, sales: DailySales,
                     customers_path: str | Path | None = None, with_test: bool = False) -> DataV2:
    """Dựng DataV2 từ bảng cặp của prepare_pairs: khách và sản phẩm lấy từ các cặp in_kcore; sản phẩm đúng lấy từ mọi
    cặp của các khách đó. catalog, sales phải là bản đã gộp theo sản phẩm (group_by_product) — mã sản phẩm của chúng
    là item_id."""
    vd, td = int(to_day(np.datetime64(val_start))), int(to_day(np.datetime64(test_start)))
    if not vd < td:
        raise ValueError(f"Cần val_start < test_start, nhận {val_start} / {test_start}")
    core = pairs[pairs["in_kcore"]]
    if core.empty:
        raise ValueError("Không có cặp nào trong k-core (in_kcore)")
    users = np.array(sorted(core["user_id"].unique(), key=str), dtype=object)
    item_product = np.sort(core["item_id"].unique()).astype(np.int64)
    n_users, n_items = len(users), len(item_product)

    user_index = pd.Series(np.arange(n_users), index=pd.Index(users))
    item_index = pd.Series(np.arange(n_items), index=pd.Index(item_product))
    rows = catalog.rows(item_product)

    def index_pairs(df: pd.DataFrame) -> pd.DataFrame:
        out = df[df["user_id"].isin(user_index.index) & df["item_id"].isin(item_index.index)]
        return out.assign(user=user_index.loc[out["user_id"]].to_numpy(np.int64),
                          item=item_index.loc[out["item_id"]].to_numpy(np.int64),
                          day=out["first_day"].to_numpy(np.int64), sample_weight=1.0).reset_index(drop=True)

    kept_i = index_pairs(core)
    all_pairs = index_pairs(pairs)
    data = DataV2(
        n_users=n_users, n_items=n_items, n_id_items=n_items, user_raw=users, item_product=item_product, kept=kept_i,
        item_cats=catalog.cats[rows], item_text=catalog.text[rows], item_cum=sales.cumulative(rows),
        item_first_day=sales.first_day[rows], item_cards=list(catalog.cardinalities),
        user_cats=None, user_cards=[], val=None,  # type: ignore[arg-type]
        meta=dict(val_day=vd, test_day=td, n_days=sales.n_days))
    if customers_path is not None:
        prof = build_user_profile(customers_path, users)
        data.user_cats, data.user_cards = prof.cats, prof.cardinalities
    end_day = sales.n_days
    data.val = make_stage("val", vd, td, kept_i, all_pairs, data)
    if with_test:
        data.test = make_stage("test", td, end_day, kept_i, all_pairs, data)
    return data


def build_v2(sample_path: str | Path, val_start: str, test_start: str, k_core: int, catalog: Catalog,
             sales: DailySales, customers_path: str | Path | None = None, with_test: bool = False) -> DataV2:
    """H&M trong bộ nhớ: HMAdapter -> prepare_pairs (gộp màu theo product_code) -> build_from_pairs. catalog, sales
    là bản theo article_id (cache của 21_build_features.py); hàm tự gộp theo sản phẩm."""
    pairs = prepare_pairs(HMAdapter(sample_path).load_events(), test_start, k_core, item_map=product_code_of)
    data = build_from_pairs(pairs, val_start, test_start, *group_by_product(catalog, sales), customers_path,
                            with_test=with_test)
    data.meta.update(k_core=k_core, sample=str(sample_path))
    return data


def make_stage(name: str, cutoff: int, window_end: int, kept: pd.DataFrame, pairs: pd.DataFrame,
               data: DataV2) -> Stage:
    train = kept[kept["day"] < cutoff].reset_index(drop=True)
    scoreable = np.zeros(data.n_items, dtype=bool)
    scoreable[train["item"].unique()] = True
    pool = scoreable  # tập ứng viên: chỉ sản phẩm có cặp huấn luyện trước mốc cắt
    users = np.unique(train["user"].to_numpy())
    t = pairs[(pairs["day"] >= cutoff) & (pairs["day"] < window_end) & pairs["user"].isin(users)]
    targets = t[pool[t["item"].to_numpy()]][["user", "item", "day"]].reset_index(drop=True)
    train_pos = build_user_positive_sets(train, data.n_users)
    records = build_full_ranking_records_multi(targets, data.n_items, train_pos, item_pool=np.flatnonzero(pool))
    utime = user_time_features(train["user"].to_numpy(), train["day"].to_numpy(), np.arange(data.n_users), cutoff)
    return Stage(name, cutoff, train, train_pos, scoreable, targets, records, utime)


def describe(data: DataV2) -> dict:
    out = dict(n_users=data.n_users, n_items=data.n_items, n_id_items=data.n_id_items, n_kept_pairs=len(data.kept))
    for st in (data.val, data.test):
        if st is None:
            continue
        out[st.name] = dict(train_pairs=len(st.train), scoreable=int(st.scoreable.sum()), users=len(st.records),
                            targets=len(st.targets),
                            candidates_mean=float(np.mean([len(r.candidates) for r in st.records])))
    return out
