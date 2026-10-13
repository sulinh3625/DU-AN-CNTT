from __future__ import annotations

import pandas as pd


def aggregate_unique_user_item(events: pd.DataFrame) -> pd.DataFrame:
    """Gộp transaction lặp trước khi k-core.

    Giữ cả số lần tương tác, tổng value và mốc thời gian đầu/cuối.
    last_source_order là tie-breaker deterministic khi nhiều item cùng timestamp.
    """
    required = {"user_raw", "item_raw", "timestamp", "value_raw", "source_order"}
    missing = required - set(events.columns)
    if missing:
        raise ValueError(f"Thiếu cột chuẩn hóa: {sorted(missing)}")

    ordered = events.sort_values(["timestamp", "source_order"], kind="mergesort")
    agg = (
        ordered.groupby(["user_raw", "item_raw"], sort=False)
        .agg(
            interaction_count=("item_raw", "size"),
            value_sum=("value_raw", "sum"),
            first_timestamp=("timestamp", "first"),
            last_timestamp=("timestamp", "last"),
            last_source_order=("source_order", "last"),
        )
        .reset_index()
    )
    return agg
