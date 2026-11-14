from __future__ import annotations

import numpy as np
import torch
from torch.utils.data import Dataset

from .negative_sampling import sample_train_negatives


class TrainDataset(Dataset):
    """Dynamic negative sampling cho implicit feedback."""

    def __init__(self, train_df, n_items, train_positive_sets, neg_ratio: int, seed: int = 42):
        self.n_items = int(n_items)
        self.neg_ratio = int(neg_ratio)
        self.train_positive_sets = train_positive_sets
        self.pos_users = train_df["user"].to_numpy(dtype=np.int64)
        self.pos_items = train_df["item"].to_numpy(dtype=np.int64)
        self.pos_weights = train_df["sample_weight"].to_numpy(dtype=np.float32)
        self.rng = np.random.default_rng(seed)
        self.users = self.items = self.labels = self.sample_weights = None
        self.resample()

    def resample(self):
        """Sinh lại negative cho mỗi epoch."""
        n_pos = len(self.pos_users)
        max_total = n_pos * (1 + self.neg_ratio)

        users = np.empty(max_total, dtype=np.int64)
        items = np.empty(max_total, dtype=np.int64)
        labels = np.zeros(max_total, dtype=np.float32)
        weights = np.ones(max_total, dtype=np.float32)

        cursor = 0
        for u, i, w in zip(self.pos_users, self.pos_items, self.pos_weights):
            users[cursor] = u
            items[cursor] = i
            labels[cursor] = 1.0
            weights[cursor] = w
            cursor += 1

            negs = sample_train_negatives(
                self.train_positive_sets[int(u)], self.n_items, self.neg_ratio, self.rng
            )
            n_neg = len(negs)
            users[cursor : cursor + n_neg] = u
            items[cursor : cursor + n_neg] = negs
            cursor += n_neg

        self.users = users[:cursor]
        self.items = items[:cursor]
        self.labels = labels[:cursor]
        self.sample_weights = weights[:cursor]

    def __len__(self):
        return len(self.users)

    def __getitem__(self, idx):
        return (
            torch.tensor(self.users[idx], dtype=torch.long),
            torch.tensor(self.items[idx], dtype=torch.long),
            torch.tensor(self.labels[idx], dtype=torch.float32),
            torch.tensor(self.sample_weights[idx], dtype=torch.float32),
        )
