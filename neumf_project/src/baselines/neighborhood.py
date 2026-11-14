"""Lọc cộng tác dựa trên láng giềng (memory-based) cho phản hồi ẩn nhị phân: ItemKNN và UserKNN."""
from __future__ import annotations

import numpy as np
from scipy.sparse import csr_matrix


def interaction_matrix(train_df, n_users: int, n_items: int) -> csr_matrix:
    """Ma trận user × item nhị phân (1 = đã mua trong dữ liệu huấn luyện)."""
    rows = train_df["user"].to_numpy(dtype=np.int64)
    cols = train_df["item"].to_numpy(dtype=np.int64)
    X = csr_matrix((np.ones(len(rows), dtype=np.float32), (rows, cols)), shape=(n_users, n_items))
    X.data[:] = 1.0
    return X


def topk_cosine(M: csr_matrix, k: int, shrink: float = 0.0, block: int = 1024) -> csr_matrix:
    """Ma trận n × n giữ top-k láng giềng cosine (sim > 0) của mỗi hàng của M, bỏ chính nó."""
    M = M.tocsr().astype(np.float32)
    n = M.shape[0]
    k = int(min(k, n - 1))
    norms = np.sqrt(np.asarray(M.multiply(M).sum(axis=1)).ravel()).astype(np.float32)
    MT = M.T.tocsc()
    rows, cols, vals = [], [], []
    for start in range(0, n, block):
        stop = min(start + block, n)
        co = (M[start:stop] @ MT).toarray()
        denom = norms[start:stop, None] * norms[None, :] + np.float32(shrink)
        sim = np.divide(co, denom, out=np.zeros_like(co), where=denom > 0)
        sim[np.arange(stop - start), np.arange(start, stop)] = 0.0
        idx = np.argsort(-sim, axis=1, kind="stable")[:, :k]
        top = np.take_along_axis(sim, idx, axis=1)
        keep = top > 0
        rows.append(np.repeat(np.arange(start, stop), k).reshape(-1, k)[keep])
        cols.append(idx[keep])
        vals.append(top[keep])
    return csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n))


class ItemKNNBaseline:
    """Item-based CF: top-K láng giềng cosine của từng item, điểm = tổng độ tương đồng tới các item đã mua."""

    def __init__(self, train_df, n_users: int, n_items: int, k: int = 100, shrink: float = 0.0):
        self.k, self.shrink = int(k), float(shrink)
        self.X = interaction_matrix(train_df, n_users, n_items)
        S = topk_cosine(self.X.T.tocsr(), self.k, self.shrink)
        self.ST = S.T.tocsr()

    def _items_of(self, user: int) -> np.ndarray:
        u = int(user)
        return self.X.indices[self.X.indptr[u]:self.X.indptr[u + 1]]

    def score_items(self, user: int, items) -> np.ndarray:
        liked = self._items_of(user)
        if len(liked) == 0:
            return np.zeros(len(items), dtype=np.float64)
        scores = np.asarray(self.ST[liked].sum(axis=0), dtype=np.float64).ravel()
        return scores[np.asarray(items, dtype=np.int64)]

    def score(self, user: int, item: int) -> float:
        return float(self.score_items(user, [item])[0])

    __call__ = score


class UserKNNBaseline:
    """User-based CF: top-K user tương đồng (cosine trên lịch sử mua), điểm = tổng độ tương đồng của láng giềng đã mua."""

    def __init__(self, train_df, n_users: int, n_items: int, k: int = 100, shrink: float = 0.0):
        self.k, self.shrink = int(k), float(shrink)
        self.X = interaction_matrix(train_df, n_users, n_items)
        self.T = topk_cosine(self.X, self.k, self.shrink)

    def score_items(self, user: int, items) -> np.ndarray:
        scores = np.asarray((self.T[int(user)] @ self.X).todense(), dtype=np.float64).ravel()
        return scores[np.asarray(items, dtype=np.int64)]

    def score(self, user: int, item: int) -> float:
        return float(self.score_items(user, [item])[0])

    __call__ = score

    def neighbors(self, user: int, top: int = 10) -> list[dict]:
        """Các user tương đồng nhất của `user`: mã user, độ tương đồng, số item mua chung."""
        row = self.T[int(user)]
        order = np.lexsort((row.indices, -row.data))[:top]
        mine = set(self.X.indices[self.X.indptr[int(user)]:self.X.indptr[int(user) + 1]].tolist())
        out = []
        for v, s in zip(row.indices[order], row.data[order]):
            theirs = self.X.indices[self.X.indptr[v]:self.X.indptr[v + 1]]
            out.append({"user": int(v), "similarity": float(s), "n_common": len(mine.intersection(theirs.tolist()))})
        return out
