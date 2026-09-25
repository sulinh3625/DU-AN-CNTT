from __future__ import annotations

import math

import numpy as np
import pandas as pd


def define_cold_users(train_df: pd.DataFrame, n_users: int, cold_fraction: float = 0.20) -> set[int]:
    """User 'cold' = nhóm cold_fraction% có ÍT tương tác nhất trong TRAIN.

    Đối xứng với define_head_items (long_tail.py) nhưng áp dụng cho USER thay
    vì ITEM — trả lời câu hỏi "mô hình gợi ý kém hơn bao nhiêu cho người dùng
    ít dữ liệu?" (mục 5.4 đề cương chi tiết).

    Lưu ý phạm vi: đây là cold-start THEO NGƯỠNG TƯƠNG ĐỐI trong tập user đã
    qua lọc k-core (mọi user còn lại đều có >= k_core tương tác TỔNG, tức
    >= k_core-2 tương tác TRAIN sau khi trừ val/test) — KHÔNG phải cold-start
    tuyệt đối (user hoàn toàn chưa có tương tác nào, chưa từng vào ma trận
    User-Item). Cold-start tuyệt đối nằm ngoài khả năng của mọi mô hình
    collaborative filtering thuần ID, kể cả NeuMF — đây là giới hạn lý
    thuyết cố hữu đã nêu ở "Đề cương chi tiết" mục 3.5, không phải thứ có
    thể "đo" bằng thực nghiệm trên chính tập dữ liệu đó.

    Item cold-start (item ít tương tác) đã được bao phủ bởi phân tích
    Long-tail sẵn có (định nghĩa theo popularity trong TRAIN, xem
    long_tail.py) — không lặp lại metric tương đương ở đây để tránh 2 bảng
    số liệu đo cùng một hiện tượng dưới 2 tên khác nhau.
    """
    counts = train_df["user"].value_counts()
    all_counts = [(u, int(counts.get(u, 0))) for u in range(n_users)]
    all_counts.sort(key=lambda pair: pair[1])  # tăng dần theo số tương tác train
    n_cold = max(1, int(math.ceil(n_users * cold_fraction)))
    return set(u for u, _ in all_counts[:n_cold])


def split_records_by_coldness(records, cold_users: set[int]):
    cold, warm = [], []
    for record in records:
        (cold if record.user in cold_users else warm).append(record)
    return cold, warm


def build_strict_cold_start(events: pd.DataFrame, data, max_users: int | None = 5000, seed: int = 42):
    """Cold-start TUYỆT ĐỐI: user bị k-core loại vì quá ít giao dịch.

    Những user này không có trong ma trận User-Item nên mọi mô hình CF thuần
    ID (GMF/MLP/NeuMF/BPR) KHÔNG có embedding để chấm điểm — chỉ các phương
    pháp dựa trên nội dung/độ phổ biến mới gợi ý được. Giao thức:
      - chỉ giữ tương tác với item nằm trong catalog đã train (item2idx);
      - user cần >= 2 item khác nhau: item cuối (theo thời gian) = test,
        phần còn lại = hồ sơ (profile) mà mô hình content-based được thấy;
      - user được gán chỉ số mới n_users + j (không trùng user train).

    Trả về (profile_df, test_df, user_raw_by_idx).
    """
    from src.data_pipeline.preprocessing import aggregate_unique_user_item

    known_users = set(data.user2idx)
    subset = events[~events["user_raw"].isin(known_users) & events["item_raw"].isin(set(data.item2idx))]
    empty = pd.DataFrame(columns=["user", "item", "last_timestamp", "last_source_order"])
    if subset.empty:
        return empty, empty.copy(), {}

    agg = aggregate_unique_user_item(subset)
    counts = agg.groupby("user_raw")["item_raw"].transform("size")
    agg = agg[counts >= 2].copy()
    if agg.empty:
        return empty, empty.copy(), {}

    users = sorted(agg["user_raw"].unique().tolist(), key=lambda x: str(x))
    if max_users is not None and len(users) > max_users:
        rng = np.random.default_rng(seed)
        users = sorted(rng.choice(np.array(users, dtype=object), size=max_users, replace=False).tolist(),
                       key=lambda x: str(x))
        agg = agg[agg["user_raw"].isin(set(users))].copy()

    user_raw_by_idx = {data.n_users + j: u for j, u in enumerate(users)}
    idx_by_raw = {u: idx for idx, u in user_raw_by_idx.items()}
    agg["user"] = agg["user_raw"].map(idx_by_raw).astype(np.int64)
    agg["item"] = agg["item_raw"].map(data.item2idx).astype(np.int64)
    agg = agg.sort_values(["user", "last_timestamp", "last_source_order", "item"], kind="mergesort")

    is_last = ~agg["user"].duplicated(keep="last")
    test_df = agg[is_last].reset_index(drop=True)
    profile_df = agg[~is_last].reset_index(drop=True)
    return profile_df, test_df, user_raw_by_idx
