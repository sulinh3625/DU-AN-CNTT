"""Dữ liệu huấn luyện cho mô hình có đặc trưng (NeuMF-F, giao thức v2).

Mỗi cặp dương (u, i) có ngày mua đầu t. Mẫu âm được lấy đều trong các sản phẩm của tập huấn luyện ĐÃ ra mắt trước hoặc
trong ngày t (sản phẩm chưa bán lần nào trước t không thể là mẫu âm của lượt mua ở t), trừ sản phẩm u đã mua; lấy lại
mỗi epoch. Mỗi mẫu mang ngày t để mô hình tính đặc trưng thời gian của item tại t, và đặc trưng thời gian của u tính từ
các cặp TRƯỚC t — mô hình không thấy thông tin sau thời điểm của từng lượt mua.
"""
from __future__ import annotations

import numpy as np

from .features import user_time_features


class FeatureTrainDataset:
    MAX_REDRAW = 20

    def __init__(self, train_df, n_items: int, item_first_day, neg_ratio: int, seed: int = 42):
        self.n_items, self.neg_ratio = int(n_items), int(neg_ratio)
        self.pos_u = train_df["user"].to_numpy(np.int64)
        self.pos_i = train_df["item"].to_numpy(np.int64)
        self.pos_d = train_df["day"].to_numpy(np.int64)
        self.pos_w = train_df["sample_weight"].to_numpy(np.float32)
        self.pos_ut = user_time_features(self.pos_u, self.pos_d, self.pos_u, self.pos_d)
        cand = np.unique(self.pos_i)
        first = np.asarray(item_first_day, dtype=np.int64)[cand]
        order = np.argsort(first, kind="stable")
        self.cand, self.cand_first = cand[order], first[order]
        self.n_avail = np.maximum(np.searchsorted(self.cand_first, self.pos_d, side="right"), 1)
        self.pos_keys = np.unique(self.pos_u * self.n_items + self.pos_i)
        self.rng = np.random.default_rng(seed)
        self.users = self.items = self.labels = self.sample_weights = None
        self.extras = {}
        self.resample()

    def _draw(self, rows: np.ndarray) -> np.ndarray:
        r = (self.rng.random(len(rows)) * self.n_avail[rows]).astype(np.int64)
        return self.cand[r]

    def resample(self):
        n, m = len(self.pos_u), self.neg_ratio
        rows = np.repeat(np.arange(n), m)
        neg = self._draw(rows)
        for _ in range(self.MAX_REDRAW):
            bad = np.isin(self.pos_u[rows] * self.n_items + neg, self.pos_keys)
            if not bad.any():
                break
            neg[bad] = self._draw(rows[bad])
        self.users = np.concatenate([self.pos_u, self.pos_u[rows]])
        self.items = np.concatenate([self.pos_i, neg])
        self.labels = np.concatenate([np.ones(n, np.float32), np.zeros(len(rows), np.float32)])
        self.sample_weights = np.concatenate([self.pos_w, np.ones(len(rows), np.float32)])
        self.extras = {"day": np.concatenate([self.pos_d, self.pos_d[rows]]),
                       "utime": np.concatenate([self.pos_ut, self.pos_ut[rows]])}

    def __len__(self):
        return len(self.users)
