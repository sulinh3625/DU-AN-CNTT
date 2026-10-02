from __future__ import annotations

import numpy as np
from tqdm import tqdm

from src.data_pipeline.negative_sampling import available_negatives


class RandomBaseline:
    def __init__(self, seed: int = 42):
        self.seed = int(seed)

    def score(self, user: int, item: int) -> float:
        return float(self.score_items(user, [item])[0])

    __call__ = score

    def score_items(self, user: int, items) -> np.ndarray:
        # Deterministic across processes; không dùng Python built-in hash.
        # Hash splitmix64 vector hoá — tạo default_rng cho từng item thì full ranking mất hàng giờ.
        with np.errstate(over="ignore"):
            x = (np.uint64(self.seed) * np.uint64(1000003) + np.uint64(int(user)) * np.uint64(9176)
                 + np.asarray(items, dtype=np.uint64) * np.uint64(6361))
            x = (x ^ (x >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
            x = (x ^ (x >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
            x ^= x >> np.uint64(31)
        return (x >> np.uint64(11)).astype(np.float64) / float(1 << 53)


class MostPopularBaseline:
    """Số user mua mỗi item trong train."""

    def __init__(self, train_df, n_items: int):
        self.pop_score = np.zeros(n_items, dtype=np.float64)
        counts = train_df["item"].value_counts()
        for item, count in counts.items():
            self.pop_score[int(item)] = float(count)

    def score(self, user: int, item: int) -> float:
        return float(self.pop_score[int(item)])

    __call__ = score

    def score_items(self, user: int, items) -> np.ndarray:
        return self.pop_score[np.asarray(items, dtype=np.int64)]


class BPRMFBaseline:
    # Clip trước sigmoid để tránh overflow của np.exp(); 35 đủ lớn để
    # sigmoid(-35) ~ 0 về mặt số học, không ảnh hưởng gradient thực tế.
    SIGMOID_CLIP = 35.0

    def __init__(self, n_users: int, n_items: int, embedding_dim: int = 32, seed: int = 42):
        rng = np.random.default_rng(seed)
        self.P = rng.normal(0, 0.01, size=(n_users, embedding_dim)).astype(np.float64)
        self.Q = rng.normal(0, 0.01, size=(n_items, embedding_dim)).astype(np.float64)
        self.n_items = int(n_items)

    def fit(self, train_df, epochs: int = 30, lr: float = 0.03, reg: float = 0.005, seed: int = 42):
        rng = np.random.default_rng(seed)
        users = train_df["user"].to_numpy(dtype=np.int64)
        items = train_df["item"].to_numpy(dtype=np.int64)
        positives = {}
        for u, i in zip(users, items):
            positives.setdefault(int(u), set()).add(int(i))
        neg_pool = {u: available_negatives(pos, self.n_items) for u, pos in positives.items()}

        epoch_bar = tqdm(
            range(int(epochs)),
            desc="    [BPR-MF] Epochs",
            unit="epoch",
            ncols=90,
            leave=True,
        )

        for ep in epoch_bar:
            n_updates = 0
            for idx in rng.permutation(len(users)):
                u, i = int(users[idx]), int(items[idx])
                pool = neg_pool[u]
                if len(pool) == 0:
                    continue
                j = int(rng.choice(pool))

                pu = self.P[u].copy()
                qi = self.Q[i].copy()
                qj = self.Q[j].copy()
                x = float(pu @ (qi - qj))
                # sigmoid(-x), stable enough with clipping.
                x = np.clip(x, -self.SIGMOID_CLIP, self.SIGMOID_CLIP)
                grad_factor = 1.0 / (1.0 + np.exp(x))

                self.P[u] += lr * (grad_factor * (qi - qj) - reg * pu)
                self.Q[i] += lr * (grad_factor * pu - reg * qi)
                self.Q[j] += lr * (-grad_factor * pu - reg * qj)
                n_updates += 1

            epoch_bar.set_postfix_str(f"updates={n_updates:,}")
        epoch_bar.close()
        return self

    def score(self, user: int, item: int) -> float:
        return float(self.P[int(user)] @ self.Q[int(item)])

    __call__ = score

    def score_items(self, user: int, items) -> np.ndarray:
        return self.Q[np.asarray(items, dtype=np.int64)] @ self.P[int(user)]

    def save(self, path) -> None:
        """Checkpoint: mảng P (users x d), Q (items x d)."""
        np.savez(path, P=self.P, Q=self.Q)

    @classmethod
    def load(cls, path) -> "BPRMFBaseline":
        npz = np.load(path)
        model = cls.__new__(cls)
        model.P, model.Q = npz["P"], npz["Q"]
        model.n_items = int(model.Q.shape[0])
        return model

