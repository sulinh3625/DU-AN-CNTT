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
        """Sinh lại negative cho mỗi epoch.

        Vẫn lặp theo user (sample_train_negatives loại trừ đúng tập positive
        của từng user, không thể vector hoá triệt để nếu muốn giữ đúng ngữ
        nghĩa "loại trừ theo user"), nhưng gom kết quả bằng mảng NumPy có sẵn
        kích thước thay vì list.append() + tuple-của-Python cho từng phần tử
        — giảm overhead đáng kể khi neg_ratio và số dòng train lớn (VD H&M).
        """
        n_pos = len(self.pos_users)
        max_total = n_pos * (1 + self.neg_ratio)  # cận trên; catalog nhỏ có thể sinh ít negative hơn

        users = np.empty(max_total, dtype=np.int64)
        items = np.empty(max_total, dtype=np.int64)
        labels = np.zeros(max_total, dtype=np.float32)
        weights = np.ones(max_total, dtype=np.float32)

        cursor = 0  # con trỏ ghi — chỉ tăng, không bao giờ resize mảng giữa chừng
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
            # labels/weights của negative đã đúng mặc định (0.0 / 1.0)
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