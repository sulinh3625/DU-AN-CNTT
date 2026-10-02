from __future__ import annotations

import math


def define_head_items(train_df, n_items: int, head_fraction: float = 0.10) -> set[int]:
    n_head = max(1, int(math.ceil(n_items * head_fraction)))
    counts = train_df["item"].value_counts().sort_values(ascending=False)
    return set(int(i) for i in counts.index[:n_head])


def split_records_head_tail(records, head_items: set[int]):
    """Chia record theo item đúng thuộc head hay tail.

    Record có cả hai loại item đúng được tách làm hai: mỗi phần chỉ giữ item đúng của nhóm
    mình và bỏ item đúng của nhóm kia khỏi candidates (không tính chúng là item sai).
    Với 1 item đúng, record giữ nguyên.
    """
    from dataclasses import replace

    import numpy as np

    head, tail = [], []
    for record in records:
        pos = record.positives
        in_head = np.isin(pos, list(head_items))
        if in_head.all() or (~in_head).all():
            (head if in_head.all() else tail).append(record)
            continue
        for group, keep in ((head, pos[in_head]), (tail, pos[~in_head])):
            drop = np.setdiff1d(pos, keep)
            group.append(replace(record, positive_item=int(keep[0]), positive_items=keep,
                                 candidates=record.candidates[~np.isin(record.candidates, drop)]))
    return head, tail
