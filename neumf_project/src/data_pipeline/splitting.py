from __future__ import annotations

import pandas as pd


def temporal_leave_one_out(df: pd.DataFrame, min_interactions: int = 3):
    """Temporal LOO trên unique user-item interactions.

    test = item cuối, validation = item áp chót, train = phần trước đó.
    Với timestamp bằng nhau, last_source_order và item index là tie-breaker ổn định.
    """
    ordered = df.sort_values(
        ["user", "last_timestamp", "last_source_order", "item"], kind="mergesort"
    )
    train_parts, val_parts, test_parts = [], [], []

    for _, g in ordered.groupby("user", sort=False):
        if len(g) < min_interactions:
            train_parts.append(g)
            continue
        train_parts.append(g.iloc[:-2])
        val_parts.append(g.iloc[-2:-1])
        test_parts.append(g.iloc[-1:])

    train = pd.concat(train_parts, ignore_index=True) if train_parts else ordered.iloc[0:0].copy()
    val = pd.concat(val_parts, ignore_index=True) if val_parts else ordered.iloc[0:0].copy()
    test = pd.concat(test_parts, ignore_index=True) if test_parts else ordered.iloc[0:0].copy()
    return train, val, test


def global_temporal_split(df: pd.DataFrame, val_start: str, test_start: str):
    """Chia theo MỘT mốc thời gian chung cho mọi user (Meng et al. 2020; Ji et al. 2023).

    Mỗi cặp user-item được xếp theo lần mua ĐẦU TIÊN (first_timestamp):
      train < val_start <= val < test_start <= test.
    CF thuần ID không chấm được user/item mới, nên val chỉ giữ user/item đã có trong train; test chỉ giữ
    user/item đã có trước test_start (train ∪ toàn bộ val), vì trước khi chấm test mô hình được train lại
    trên mọi cặp < test_start (refit_data). Mỗi user có thể có nhiều item đúng.
    """
    vs, ts = pd.Timestamp(val_start), pd.Timestamp(test_start)
    if not vs < ts:
        raise ValueError(f"Cần val_start < test_start, nhận {val_start} / {test_start}")
    ft = df["first_timestamp"]
    train, known = df[ft < vs], df[ft < ts]
    val, test = df[(ft >= vs) & (ft < ts)], df[ft >= ts]

    def warm(x, seen):
        return x[x["user"].isin(set(seen["user"])) & x["item"].isin(set(seen["item"]))].reset_index(drop=True)

    return train.reset_index(drop=True), warm(val, train), warm(test, known)


def refit_data(df: pd.DataFrame, test_start: str) -> pd.DataFrame:
    """Dữ liệu train lại trước khi chấm test: mọi cặp có lần mua đầu < test_start (train ∪ toàn bộ val,
    kể cả cặp val của user/item chưa có trong train)."""
    return df[df["first_timestamp"] < pd.Timestamp(test_start)].reset_index(drop=True)


def user_item_pairs(df: pd.DataFrame) -> set[tuple[int, int]]:
    return set(zip(df["user"].astype(int), df["item"].astype(int)))


def assert_disjoint_splits(train: pd.DataFrame, val: pd.DataFrame, test: pd.DataFrame) -> None:
    t, v, s = user_item_pairs(train), user_item_pairs(val), user_item_pairs(test)
    tv = t & v
    ts = t & s
    vs = v & s
    if tv or ts or vs:
        raise AssertionError(
            f"User-item leakage giữa splits: train∩val={len(tv)}, "
            f"train∩test={len(ts)}, val∩test={len(vs)}"
        )
