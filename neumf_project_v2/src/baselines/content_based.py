from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack

from src.evaluation.metrics import ndcg_at_k
from src.evaluation.ranking_utils import rank_positive


def _popularity(train_df, n_items: int) -> np.ndarray:
    pop = np.zeros(n_items, dtype=np.float64)
    counts = train_df["item"].value_counts()
    pop[counts.index.to_numpy(dtype=np.int64)] = counts.to_numpy(dtype=np.float64)
    return pop


class CategoryPopularityBaseline:
    """Baseline content-based dùng Category (danh mục sản phẩm) làm đặc
    trưng nội dung phụ trợ, thử nghiệm như một giải pháp giảm nhẹ Cold-start
    (mục 5.4 đề cương chi tiết + phản hồi GVHD): thay vì gợi ý mù quáng theo
    độ phổ biến toàn cục (MostPopularBaseline thuần ID), với mỗi user, ưu
    tiên sản phẩm phổ biến TRONG CÙNG danh mục user đã từng mua trong train.

    Trực giác: một user ít lịch sử tương tác (cold) vẫn để lộ TÍN HIỆU về
    sở thích qua (các) danh mục đã mua, dù số lượng giao dịch quá ít để mô
    hình Collaborative Filtering thuần ID (GMF/MLP/NeuMF) học được vector
    Embedding tốt cho user đó.

    off_category_penalty: hệ số nhân cho sản phẩm KHÁC danh mục user đã mua
    (không phải 0 tuyệt đối -- vẫn cần một điểm số fallback có ý nghĩa để
    xếp hạng phần candidate còn lại, tránh hoà điểm hàng loạt khi đánh giá
    Full Ranking).

    profile_df: tương tác dùng để xác định danh mục của user (mặc định =
    train_df). Tách riêng để đánh giá cold-start tuyệt đối: độ phổ biến vẫn
    lấy từ TRAIN, còn danh mục lấy từ vài giao dịch ít ỏi của user mới.
    """

    def __init__(self, train_df, item_category: dict[int, str], n_items: int,
                 off_category_penalty: float = 0.1, profile_df=None):
        self.item_category = item_category
        self.off_category_penalty = float(off_category_penalty)
        self.pop_score = _popularity(train_df, n_items)

        codes = {}
        self.item_cat_code = np.full(n_items, -1, dtype=np.int64)
        for item, cat in item_category.items():
            if cat is not None and not pd.isna(cat):
                self.item_cat_code[int(item)] = codes.setdefault(cat, len(codes))

        profile_df = train_df if profile_df is None else profile_df
        self.user_categories: dict[int, set[str]] = {}
        self.user_cat_codes: dict[int, np.ndarray] = {}
        for u, i in zip(profile_df["user"].to_numpy(), profile_df["item"].to_numpy()):
            cat = item_category.get(int(i))
            if cat is not None and not pd.isna(cat):
                self.user_categories.setdefault(int(u), set()).add(cat)
        for u, cats in self.user_categories.items():
            self.user_cat_codes[u] = np.array([codes[c] for c in cats], dtype=np.int64)

    def score(self, user: int, item: int) -> float:
        base = float(self.pop_score[int(item)])
        cat = self.item_category.get(int(item))
        known_cats = self.user_categories.get(int(user))
        if known_cats and cat is not None and cat in known_cats:
            return base
        return base * self.off_category_penalty

    __call__ = score

    def score_items(self, user: int, items: np.ndarray) -> np.ndarray:
        items = np.asarray(items, dtype=np.int64)
        base = self.pop_score[items]
        known = self.user_cat_codes.get(int(user))
        if known is None:
            return base * self.off_category_penalty
        in_cat = np.isin(self.item_cat_code[items], known) & (self.item_cat_code[items] >= 0)
        return np.where(in_cat, base, base * self.off_category_penalty)


class AgeGroupPopularityBaseline:
    """Độ phổ biến theo nhóm tuổi (customers.csv): gợi ý item được mua nhiều
    nhất bởi những khách hàng CÙNG nhóm tuổi trong TRAIN.

    Là tín hiệu nhân khẩu học duy nhất dùng được với user hoàn toàn mới (chưa
    có giao dịch nào); cộng thêm một lượng nhỏ độ phổ biến toàn cục để phá hoà
    điểm ở item chưa xuất hiện trong nhóm tuổi đó.
    """

    GLOBAL_WEIGHT = 1e-3

    def __init__(self, train_df, n_items: int, user_group: dict[int, str]):
        self.user_group = user_group
        global_pop = _popularity(train_df, n_items)
        self.global_pop = global_pop / max(global_pop.max(), 1.0)
        self.group_pop: dict[str, np.ndarray] = {}
        groups = train_df["user"].map(lambda u: user_group.get(int(u)))
        for group, part in train_df.groupby(groups):
            pop = _popularity(part, n_items)
            self.group_pop[group] = pop / max(pop.max(), 1.0)

    def score_items(self, user: int, items: np.ndarray) -> np.ndarray:
        items = np.asarray(items, dtype=np.int64)
        group_pop = self.group_pop.get(self.user_group.get(int(user)))
        base = self.global_pop[items] * self.GLOBAL_WEIGHT
        if group_pop is None:
            return self.global_pop[items]
        return group_pop[items] + base

    def __call__(self, user: int, item: int) -> float:
        return float(self.score_items(user, np.array([item]))[0])


def build_item_feature_matrix(
    item_df: pd.DataFrame,
    categorical_cols: list[str],
    text_cols: list[str],
    block_weights: dict[str, float] | None = None,
    text_weight: float = 1.0,
    text_max_features: int = 5000,
) -> csr_matrix:
    """Ma trận đặc trưng item (n_items x d), thưa, mỗi hàng chuẩn hoá L2.

    Mỗi thuộc tính phân loại là một khối one-hot; văn bản (prod_name +
    detail_desc) là một khối TF-IDF. Từng khối được nhân sqrt(weight) nên tích
    vô hướng giữa hai item = tổng có trọng số độ tương đồng của từng khối.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer

    block_weights = block_weights or {}
    n_items = len(item_df)
    blocks = []
    for col in categorical_cols:
        if col not in item_df.columns:
            continue
        codes, _ = pd.factorize(item_df[col], use_na_sentinel=True)
        rows = np.flatnonzero(codes >= 0)
        if len(rows) == 0:
            continue
        w = float(np.sqrt(block_weights.get(col, 1.0)))
        blocks.append(csr_matrix(
            (np.full(len(rows), w), (rows, codes[rows])), shape=(n_items, int(codes.max()) + 1)
        ))

    text_cols = [c for c in text_cols if c in item_df.columns]
    if text_cols and text_weight > 0:
        text = item_df[text_cols].fillna("").astype(str).agg(" ".join, axis=1)
        if text.str.strip().astype(bool).any():
            tfidf = TfidfVectorizer(
                max_features=text_max_features, stop_words="english",
                min_df=2 if n_items >= 50 else 1, sublinear_tf=True,
            )
            try:
                blocks.append(tfidf.fit_transform(text) * float(np.sqrt(text_weight)))
            except ValueError:  # vocabulary rỗng (toàn stop-words)
                pass

    if not blocks:
        raise ValueError("Không có đặc trưng nội dung nào cho item.")
    X = hstack(blocks).tocsr().astype(np.float64)
    norms = np.sqrt(np.asarray(X.multiply(X).sum(axis=1)).ravel())
    norms[norms == 0] = 1.0
    return csr_matrix(X.multiply(1.0 / norms[:, None]))


class ContentBasedBaseline:
    """Content-based Filtering: hồ sơ user = trung bình (có trọng số thời gian)
    vector đặc trưng các item user đã mua; điểm = cosine(hồ sơ user, item).

    recency_decay: item mua gần nhất có trọng số 1, item trước đó decay^1,
    decay^2, ... (1.0 = trung bình đều). Thời trang có tính mùa vụ/xu hướng
    nên các giao dịch gần đây phản ánh sở thích hiện tại tốt hơn.
    Hồ sơ chỉ xây từ profile_df (TRAIN) -> không rò rỉ val/test.
    """

    def __init__(self, item_matrix: csr_matrix, profile_df, recency_decay: float = 1.0):
        self.X = item_matrix
        self.XT = item_matrix.T.tocsr()
        self.recency_decay = float(recency_decay)
        order_cols = [c for c in ("user", "last_timestamp", "last_source_order", "item") if c in profile_df.columns]
        ordered = profile_df.sort_values(order_cols, kind="mergesort")

        users = ordered["user"].to_numpy(dtype=np.int64)
        items = ordered["item"].to_numpy(dtype=np.int64)
        # vị trí tính từ cuối trong lịch sử từng user (0 = gần nhất)
        pos_from_end = ordered.groupby("user", sort=False).cumcount(ascending=False).to_numpy()
        weights = np.power(self.recency_decay, pos_from_end.astype(np.float64))

        self.user_index = {int(u): idx for idx, u in enumerate(pd.unique(users))}
        rows = np.fromiter((self.user_index[int(u)] for u in users), dtype=np.int64, count=len(users))
        W = csr_matrix((weights, (rows, items)), shape=(len(self.user_index), item_matrix.shape[0]))
        profiles = W @ item_matrix
        norms = np.sqrt(np.asarray(profiles.multiply(profiles).sum(axis=1)).ravel())
        norms[norms == 0] = 1.0
        self.profiles = csr_matrix(profiles.multiply(1.0 / norms[:, None]))

    def score_items(self, user: int, items: np.ndarray) -> np.ndarray:
        items = np.asarray(items, dtype=np.int64)
        idx = self.user_index.get(int(user))
        if idx is None:
            return np.zeros(len(items), dtype=np.float64)
        scores = (self.profiles[idx] @ self.XT).toarray().ravel()
        return scores[items]

    def __call__(self, user: int, item: int) -> float:
        return float(self.score_items(user, np.array([item]))[0])


def tune_recency_decay(item_matrix, train_df, val_records, decays, k: int = 10, tie_seed: int = 2026):
    """Chọn recency_decay theo NDCG@k trên VALIDATION (không chạm test)."""
    results = {}
    for decay in decays:
        model = ContentBasedBaseline(item_matrix, train_df, recency_decay=decay)
        vals = [
            ndcg_at_k(rank_positive(model.score_items(r.user, r.candidates), r.candidates,
                                    r.positive_item, r.user, tie_seed), k)
            for r in val_records
        ]
        results[float(decay)] = float(np.mean(vals)) if vals else 0.0
    best = max(results, key=lambda d: (results[d], -abs(d - 1.0)))
    return best, results
