from __future__ import annotations

import numpy as np
from tqdm import tqdm

def kth_available(sorted_positives: np.ndarray, k: int) -> int:
    """Item thứ k (0-based) trong các item KHÔNG thuộc sorted_positives.

    Bằng available_negatives(...)[k] nhưng không cấp phát mảng dài n_items.
    """
    shifted = sorted_positives - np.arange(len(sorted_positives))
    return int(k + np.searchsorted(shifted, k, side="right"))


_U32, _U64 = np.uint32, np.uint64
_M32 = 0xFFFFFFFF
_PCG_MULT_HI, _PCG_MULT_LO = 0x2360ED051FC65DA4, 0x4385DF649FCCF645


def _mul64(a, b):
    """a*b (uint64) -> (hi, lo) đủ 128 bit."""
    a0, a1 = a & _U64(_M32), a >> _U64(32)
    b0, b1 = b & _U64(_M32), b >> _U64(32)
    p00, p01, p10, p11 = a0 * b0, a0 * b1, a1 * b0, a1 * b1
    mid = (p00 >> _U64(32)) + (p01 & _U64(_M32)) + (p10 & _U64(_M32))
    lo = (p00 & _U64(_M32)) | (mid << _U64(32))
    hi = p11 + (p01 >> _U64(32)) + (p10 >> _U64(32)) + (mid >> _U64(32))
    return hi, lo


def _add128(a_hi, a_lo, b_hi, b_lo):
    lo = a_lo + b_lo
    return a_hi + b_hi + (lo < a_lo).astype(_U64), lo


def _pcg_step(hi, lo, inc_hi, inc_lo):
    m_hi, m_lo = _U64(_PCG_MULT_HI), _U64(_PCG_MULT_LO)
    p_hi, p_lo = _mul64(lo, np.full_like(lo, m_lo))
    p_hi = p_hi + hi * m_lo + lo * m_hi
    return _add128(p_hi, p_lo, inc_hi, inc_lo)


def first_uniform(seeds) -> np.ndarray:
    """== np.random.default_rng(s).random() cho từng s trong [0, 2**32), vector hoá.

    Tái hiện SeedSequence -> PCG64 -> random() của numpy để RandomBaseline chấm
    điểm cả mảng mà vẫn ra đúng số cũ (tạo default_rng cho từng cặp rất chậm).
    Kiểm chứng bằng tests/test_baselines.py.
    """
    seeds = np.asarray(seeds, dtype=np.int64).astype(_U32)
    hc = [0x43B0D7E5]

    def hashmix(v):
        v = v ^ _U32(hc[0])
        hc[0] = (hc[0] * 0x931E8875) & _M32
        v = v * _U32(hc[0])
        return v ^ (v >> _U32(16))

    def mix(x, y):
        r = _U32(0xCA01F9DD) * x - _U32(0x4973F715) * y
        return r ^ (r >> _U32(16))

    # SeedSequence.mix_entropy: pool 4 từ uint32, entropy = [s]
    pool = [hashmix(seeds)] + [hashmix(np.zeros_like(seeds)) for _ in range(3)]
    for i_src in range(4):
        for i_dst in range(4):
            if i_src != i_dst:
                pool[i_dst] = mix(pool[i_dst], hashmix(pool[i_src]))

    # SeedSequence.generate_state(4, uint64)
    hb, words = 0x8B51F9DD, []
    for i in range(8):
        v = pool[i % 4] ^ _U32(hb)
        hb = (hb * 0x58F38DED) & _M32
        v = v * _U32(hb)
        words.append((v ^ (v >> _U32(16))).astype(_U64))
    s_hi, s_lo, q_hi, q_lo = (words[2 * k] | (words[2 * k + 1] << _U64(32)) for k in range(4))

    # PCG64 srandom: inc = (seq << 1) | 1; state = inc + initstate; step
    inc_hi = (q_hi << _U64(1)) | (q_lo >> _U64(63))
    inc_lo = (q_lo << _U64(1)) | _U64(1)
    hi, lo = _add128(inc_hi, inc_lo, s_hi, s_lo)
    hi, lo = _pcg_step(hi, lo, inc_hi, inc_lo)
    # next64: step rồi xuất XSL-RR
    hi, lo = _pcg_step(hi, lo, inc_hi, inc_lo)
    x, rot = hi ^ lo, hi >> _U64(58)
    out = (x >> rot) | (x << ((_U64(64) - rot) & _U64(63)))
    return (out >> _U64(11)).astype(np.float64) / float(1 << 53)


# Mọi baseline: score(user, items) nhận mảng item, trả mảng điểm cùng độ dài.


class RandomBaseline:
    def __init__(self, seed: int = 42):
        self.seed = int(seed)

    def score(self, user: int, items) -> np.ndarray:
        # Deterministic across processes; không dùng Python built-in hash.
        items = np.asarray(items, dtype=np.int64)
        s = (self.seed * 1000003 + int(user) * 9176 + items * 6361) & 0xFFFFFFFF
        return first_uniform(s)


class MostPopularBaseline:
    def __init__(self, train_df, n_items: int):
        self.pop_score = np.zeros(n_items, dtype=np.float64)
        counts = train_df["item"].value_counts()
        for item, count in counts.items():
            self.pop_score[int(item)] = float(count)

    def score(self, user: int, items) -> np.ndarray:
        return self.pop_score[np.asarray(items, dtype=np.int64)]


class ItemKNNBaseline:
    """Item-based CF cosine. Chỉ nên dùng khi catalog đủ nhỏ (VD hm_subset).

    Similarity matrix là DENSE n_items x n_items (self.sim.toarray()) — với
    catalog lớn (VD H&M, hàng chục nghìn item) việc này cấp phát bộ nhớ
    O(n_items^2), có thể vượt RAM. ITEMKNN_MAX_ITEMS chặn cứng trường hợp
    này thay vì để nó âm thầm treo máy.
    """

    ITEMKNN_MAX_ITEMS = 5000

    def __init__(self, train_df, n_users: int, n_items: int):
        from scipy.sparse import csr_matrix

        if n_items > self.ITEMKNN_MAX_ITEMS:
            raise ValueError(
                f"ItemKNNBaseline dùng dense similarity O(n_items^2); "
                f"n_items={n_items:,} vượt ngưỡng an toàn {self.ITEMKNN_MAX_ITEMS:,}. "
                f"Dùng trên catalog nhỏ (VD hm_subset) hoặc cài bản sparse top-N trước khi chạy trên catalog lớn."
            )

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

    def score(self, user: int, items) -> np.ndarray:
        items = np.asarray(items, dtype=np.int64)
        interacted = self.user_items[int(user)]
        if not interacted:
            return np.zeros(len(items), dtype=np.float64)
        # Cộng float32 theo từng hàng như bản chấm từng cặp -> điểm (và thứ tự hoà) không đổi.
        return self.sim[np.ix_(items, interacted)].sum(axis=1).astype(np.float64)


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
        # Chỉ giữ positive đã sắp xếp; item âm thứ k tính bằng kth_available thay
        # vì giữ sẵn mảng available_negatives dài n_items cho mọi user.
        sorted_pos = {u: np.array(sorted(pos), dtype=np.int64) for u, pos in positives.items()}

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
                pos = sorted_pos[u]
                n_avail = self.n_items - len(pos)
                if n_avail == 0:
                    continue
                # == rng.choice(available_negatives(pos)) — cùng luồng RNG, cùng item.
                j = kth_available(pos, int(rng.integers(0, n_avail)))

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

    def score(self, user: int, items) -> np.ndarray:
        return self.Q[np.asarray(items, dtype=np.int64)] @ self.P[int(user)]