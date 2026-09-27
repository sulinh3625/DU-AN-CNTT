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
    Val/test chỉ giữ user và item đã có trong train (CF thuần ID không chấm được user/item mới);
    mỗi user có thể có nhiều item đúng. Mô hình không thấy tương tác nào sau val_start khi train.
    """
    vs, ts = pd.Timestamp(val_start), pd.Timestamp(test_start)
    if not vs < ts:
        raise ValueError(f"Cần val_start < test_start, nhận {val_start} / {test_start}")
    ft = df["first_timestamp"]
    train = df[ft < vs]
    val, test = df[(ft >= vs) & (ft < ts)], df[ft >= ts]
    users, items = set(train["user"]), set(train["item"])

    def warm(x):
        return x[x["user"].isin(users) & x["item"].isin(items)].reset_index(drop=True)

    return train.reset_index(drop=True), warm(val), warm(test)


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
