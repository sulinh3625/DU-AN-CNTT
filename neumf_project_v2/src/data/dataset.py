from __future__ import annotations

import numpy as np
import torch
from torch.utils.data import Dataset

from .negative_sampling import sample_train_negatives


class TrainDataset(Dataset):
    """Dynamic negative sampling cho implicit feedback.

    Quan trọng: exclude_set phải lấy từ TRAIN positives, không dùng validation/test
    để tránh future-information leakage vào quá trình huấn luyện.
    """

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
        users, items, labels, weights = [], [], [], []
        for u, i, w in zip(self.pos_users, self.pos_items, self.pos_weights):
            users.append(int(u)); items.append(int(i)); labels.append(1.0); weights.append(float(w))
            negs = sample_train_negatives(
                self.train_positive_sets[int(u)], self.n_items, self.neg_ratio, self.rng
            )
            for j in negs:
                users.append(int(u)); items.append(int(j)); labels.append(0.0); weights.append(1.0)

        self.users = np.asarray(users, dtype=np.int64)
        self.items = np.asarray(items, dtype=np.int64)
        self.labels = np.asarray(labels, dtype=np.float32)
        self.sample_weights = np.asarray(weights, dtype=np.float32)

    def __len__(self):
        return len(self.users)

    def __getitem__(self, idx):
        return (
            torch.tensor(self.users[idx], dtype=torch.long),
            torch.tensor(self.items[idx], dtype=torch.long),
            torch.tensor(self.labels[idx], dtype=torch.float32),
            torch.tensor(self.sample_weights[idx], dtype=torch.float32),
        )
