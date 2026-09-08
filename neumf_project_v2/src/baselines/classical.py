from __future__ import annotations

import numpy as np
from tqdm import tqdm

from src.data.negative_sampling import available_negatives


class RandomBaseline:
    def __init__(self, seed: int = 42):
        self.seed = int(seed)

    def score(self, user: int, item: int) -> float:
        # Deterministic across processes; không dùng Python built-in hash.
        s = (self.seed * 1000003 + int(user) * 9176 + int(item) * 6361) & 0xFFFFFFFF
        return float(np.random.default_rng(s).random())


class MostPopularBaseline:
    def __init__(self, train_df, n_items: int):
        self.pop_score = np.zeros(n_items, dtype=np.float64)
        counts = train_df["item"].value_counts()
        for item, count in counts.items():
            self.pop_score[int(item)] = float(count)

    def score(self, user: int, item: int) -> float:
        return float(self.pop_score[int(item)])


class ItemKNNBaseline:
    """Item-based CF cosine. Chỉ nên dùng khi catalog đủ nhỏ (DataCo)."""

    def __init__(self, train_df, n_users: int, n_items: int):
        from scipy.sparse import csr_matrix

        rows = train_df["user"].to_numpy(dtype=np.int64)
        cols = train_df["item"].to_numpy(dtype=np.int64)
        data = np.ones(len(train_df), dtype=np.float32)
        ui = csr_matrix((data, (rows, cols)), shape=(n_users, n_items))
        item_user = ui.T.tocsr()
        norms = np.sqrt(item_user.multiply(item_user).sum(axis=1)).A1
        norms[norms == 0] = 1e-12
        sim = item_user @ item_user.T
        sim = sim.toarray().astype(np.float32)
        sim /= norms[:, None]
        sim /= norms[None, :]
        np.fill_diagonal(sim, 0.0)
        self.sim = sim
        self.user_items = ui.tolil().rows

    def score(self, user: int, item: int) -> float:
        interacted = self.user_items[int(user)]
        if not interacted:
            return 0.0
        return float(self.sim[int(item), interacted].sum())


class BPRMFBaseline:
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
                x = np.clip(x, -35.0, 35.0)
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
