"""Đặc trưng cho mô hình lai có đặc trưng (giao thức v2, audit/PREREG_v2.md).

Ba nguồn, đều KHÔNG dùng nhãn của giai đoạn được đánh giá:
- Danh mục sản phẩm (articles.csv): 11 thuộc tính mã hoá thành chỉ số (0 = không biết) và vector mô tả văn bản
  (TF-IDF trên tên + mô tả, giảm chiều bằng SVD). Đây là thông tin tĩnh của catalogue, không dùng tương tác.
- Doanh số theo ngày của toàn bộ H&M (transactions_train.csv): đếm giao dịch mỗi (sản phẩm, ngày), lưu cộng dồn.
  Đặc trưng thời gian tại ngày t chỉ dùng các ngày < t (item_time_features).
- Thông tin khách (customers.csv): nhóm tuổi, trạng thái hội viên, tần suất nhận tin, FN, Active.

Cache (bị .gitignore): data/processed/hm/catalog_v2.npz, data/processed/hm/daily_sales_v2.npz — tạo bằng
`python scripts/21_build_features.py`. Cache theo article_id; mô hình dùng bản đã gộp mọi màu của một mẫu thành một sản
phẩm (product_code = article_id // 1000) bằng group_by_product.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse

DAY0 = np.datetime64("2018-09-20")  # ngày đầu của transactions_train.csv
ITEM_CAT_COLS = ["product_type_no", "product_group_name", "graphical_appearance_no", "colour_group_code",
                 "perceived_colour_value_id", "perceived_colour_master_id", "department_no", "index_code",
                 "index_group_no", "section_no", "garment_group_no"]
COLOUR_COLS = ("colour_group_code", "perceived_colour_value_id", "perceived_colour_master_id")  # hằng số sau khi gộp
USER_CAT_COLS = ["age_bucket", "club_member_status", "fashion_news_frequency", "FN", "Active"]
AGE_EDGES = [20, 25, 30, 35, 45, 55, 65]  # nhóm tuổi: <20, 20–24, ..., 55–64, 65+
SALES_WINDOWS = (7, 28, 91)
ITEM_TIME_DIM = len(SALES_WINDOWS) + 2  # log1p(doanh số 7/28/91 ngày), log1p(tuổi sản phẩm), cờ chưa từng bán
USER_TIME_DIM = 2  # log1p(số ngày từ lần mua gần nhất), log1p(số cặp đã mua)
LOG_SCALE = 10.0  # chia log1p(·) cho hằng số để đặc trưng số nằm cỡ [0, 1]


def to_day(ts) -> np.ndarray:
    """Chỉ số ngày (0 = 2018-09-20) của một mảng thời điểm."""
    return (np.asarray(ts, dtype="datetime64[D]") - DAY0).astype(np.int64)


# ------------------------------------------------------------------ catalogue
@dataclass
class Catalog:
    article_ids: np.ndarray  # int64, tăng dần
    cats: np.ndarray  # int32 [n_articles, len(ITEM_CAT_COLS)], 0 = không biết
    cardinalities: list[int]  # số giá trị mỗi thuộc tính, gồm cả 0
    text: np.ndarray  # float32 [n_articles, text_dim], chuẩn hoá L2

    def rows(self, article_ids) -> np.ndarray:
        """Vị trí trong catalogue của các article_id (int); lỗi nếu có mã không thuộc catalogue."""
        ids = np.asarray(article_ids, dtype=np.int64)
        pos = np.searchsorted(self.article_ids, ids)
        pos = np.clip(pos, 0, len(self.article_ids) - 1)
        if not np.array_equal(self.article_ids[pos], ids):
            missing = ids[self.article_ids[pos] != ids][:5]
            raise KeyError(f"article_id không có trong articles.csv: {missing.tolist()}")
        return pos


def build_catalog(articles_path: str | Path, text_dim: int = 64, seed: int = 0) -> Catalog:
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import normalize

    a = pd.read_csv(articles_path, dtype={"article_id": "int64"}).sort_values("article_id").reset_index(drop=True)
    cats, cards = [], []
    for col in ITEM_CAT_COLS:
        values = a[col].astype("string").fillna("")
        vocab = sorted(set(values) - {""})
        code = {v: k + 1 for k, v in enumerate(vocab)}
        cats.append(values.map(lambda v: code.get(v, 0)).to_numpy(dtype=np.int32))
        cards.append(len(vocab) + 1)
    corpus = (a["prod_name"].fillna("") + " " + a["detail_desc"].fillna("")).str.lower()
    tfidf = TfidfVectorizer(min_df=3, max_features=30_000, ngram_range=(1, 2), sublinear_tf=True,
                            stop_words="english", dtype=np.float32)
    svd = TruncatedSVD(n_components=text_dim, random_state=seed, n_iter=7)
    text = normalize(svd.fit_transform(tfidf.fit_transform(corpus))).astype(np.float32)
    return Catalog(a["article_id"].to_numpy(np.int64), np.stack(cats, axis=1), cards, text)


def save_catalog(cat: Catalog, path: str | Path) -> None:
    np.savez_compressed(path, article_ids=cat.article_ids, cats=cat.cats,
                        cardinalities=np.asarray(cat.cardinalities, dtype=np.int64), text=cat.text)


def load_catalog(path: str | Path) -> Catalog:
    z = np.load(path)
    return Catalog(z["article_ids"], z["cats"], z["cardinalities"].tolist(), z["text"])


# --------------------------------------------------------------- doanh số
@dataclass
class DailySales:
    """Số giao dịch mỗi (sản phẩm, ngày) của toàn bộ H&M; hàng theo thứ tự Catalog.article_ids."""
    counts: sparse.csr_matrix  # int32 [n_articles, n_days]
    first_day: np.ndarray  # int64 [n_articles], ngày bán đầu tiên; n_days nếu chưa từng bán trong dữ liệu

    @property
    def n_days(self) -> int:
        return int(self.counts.shape[1])

    def cumulative(self, rows: np.ndarray) -> np.ndarray:
        """Doanh số cộng dồn [len(rows), n_days + 1]: cột d = tổng các ngày < d (cột 0 = 0)."""
        dense = self.counts[rows].toarray()
        out = np.zeros((len(rows), self.n_days + 1), dtype=np.int32)
        np.cumsum(dense, axis=1, out=out[:, 1:])
        return out


def build_daily_sales(transactions_path: str | Path, catalog: Catalog, chunksize: int = 2_000_000) -> DailySales:
    keys, vals = [], []
    n_days = 0
    for chunk in pd.read_csv(transactions_path, usecols=["t_dat", "article_id"], dtype={"article_id": "int64"},
                             chunksize=chunksize):
        day = to_day(pd.to_datetime(chunk["t_dat"], format="%Y-%m-%d").to_numpy())
        row = catalog.rows(chunk["article_id"].to_numpy())
        n_days = max(n_days, int(day.max()) + 1)
        k = pd.Series(row.astype(np.int64) * 10_000 + day).value_counts()
        keys.append(k.index.to_numpy(np.int64))
        vals.append(k.to_numpy(np.int64))
    s = pd.Series(np.concatenate(vals)).groupby(np.concatenate(keys)).sum()
    rows, days = np.divmod(s.index.to_numpy(np.int64), 10_000)
    counts = sparse.csr_matrix((s.to_numpy(np.int32), (rows, days)), shape=(len(catalog.article_ids), n_days),
                               dtype=np.int32)
    first_day = np.full(len(catalog.article_ids), n_days, dtype=np.int64)
    first = pd.Series(days).groupby(rows).min()
    first_day[first.index.to_numpy()] = first.to_numpy()
    return DailySales(counts, first_day)


def save_daily_sales(ds: DailySales, path: str | Path) -> None:
    c = ds.counts
    np.savez_compressed(path, data=c.data, indices=c.indices, indptr=c.indptr, shape=np.asarray(c.shape),
                        first_day=ds.first_day)


def load_daily_sales(path: str | Path) -> DailySales:
    z = np.load(path)
    counts = sparse.csr_matrix((z["data"], z["indices"], z["indptr"]), shape=tuple(z["shape"]))
    return DailySales(counts, z["first_day"])


def item_time_features(cum: np.ndarray, first_day: np.ndarray, items: np.ndarray, day) -> np.ndarray:
    """Đặc trưng thời gian của item tại ngày `day` (scalar hoặc mảng cùng cỡ items), chỉ dùng các ngày < day:
    log1p(doanh số trong 7/28/91 ngày trước), log1p(tuổi sản phẩm tính từ ngày bán đầu), cờ "chưa từng bán trước day".
    `cum` là ma trận cộng dồn của DailySales.cumulative (hàng theo chỉ số item của mô hình)."""
    items = np.asarray(items, dtype=np.int64)
    day = np.broadcast_to(np.asarray(day, dtype=np.int64), items.shape)
    now = cum[items, np.clip(day, 0, cum.shape[1] - 1)].astype(np.float32)
    cols = [np.log1p(now - cum[items, np.clip(day - w, 0, cum.shape[1] - 1)]) for w in SALES_WINDOWS]
    fd = first_day[items]
    cols.append(np.log1p(np.clip(day - fd, 0, None)).astype(np.float32))
    cols.append((fd >= day).astype(np.float32))
    out = np.stack(cols, axis=-1).astype(np.float32)
    out[..., :-1] /= LOG_SCALE
    return out


# ---------------------------------------------------- gộp màu theo product_code
def product_code_of(article_ids) -> np.ndarray:
    """product_code của H&M = article_id // 1000 (3 chữ số cuối là biến thể màu)."""
    return np.asarray(article_ids, dtype=np.int64) // 1000


def check_product_code(articles_path: str | Path) -> None:
    """Dừng nếu articles.csv có dòng mà article_id // 1000 khác cột product_code (không tự đổi sang cột đó)."""
    a = pd.read_csv(articles_path, usecols=["article_id", "product_code"],
                    dtype={"article_id": "int64", "product_code": "int64"})
    bad = int((product_code_of(a["article_id"]) != a["product_code"].to_numpy()).sum())
    if bad:
        raise ValueError(f"{articles_path}: {bad:,}/{len(a):,} dòng có article_id // 1000 khác product_code — dừng")


def group_by_product(catalog: Catalog, sales: DailySales) -> tuple[Catalog, DailySales]:
    """Gộp mọi màu của cùng một mẫu thành một sản phẩm (product_code_of).

    Catalog mới giữ tên trường article_ids nhưng giá trị là product_code (tăng dần, duy nhất). Thuộc tính lấy theo biến
    thể có article_id nhỏ nhất; 3 cột màu (COLOUR_COLS) đặt về 0, cardinality 1 — số cột vẫn là len(ITEM_CAT_COLS) nên
    NeuMFF không phải đổi. Văn bản = trung bình các biến thể rồi chuẩn hoá L2 (hàng toàn 0 giữ 0). Doanh số theo ngày =
    tổng các biến thể; ngày bán đầu = ngày sớm nhất. Dùng ma trận thưa chỉ báo (sản phẩm × biến thể)."""
    # article_ids tăng dần -> lần xuất hiện đầu của mỗi product_code là biến thể có article_id nhỏ nhất
    codes, first, inv = np.unique(product_code_of(catalog.article_ids), return_index=True, return_inverse=True)
    n_var = len(catalog.article_ids)
    onehot = sparse.csr_matrix((np.ones(n_var, dtype=np.int32), (inv, np.arange(n_var))), shape=(len(codes), n_var))
    cats, cards = catalog.cats[first].copy(), list(catalog.cardinalities)
    for col in COLOUR_COLS:
        k = ITEM_CAT_COLS.index(col)
        cats[:, k], cards[k] = 0, 1
    text = (onehot @ catalog.text) / np.bincount(inv)[:, None]
    norm = np.linalg.norm(text, axis=1, keepdims=True)
    text = (text / np.where(norm > 0, norm, 1.0)).astype(np.float32)
    counts = (onehot @ sales.counts).astype(np.int32).tocsr()
    first_day = np.full(len(codes), np.iinfo(np.int64).max, dtype=np.int64)
    np.minimum.at(first_day, inv, sales.first_day)
    return Catalog(codes, cats, cards, text), DailySales(counts, first_day)


# ---------------------------------------------------------------- khách hàng
@dataclass
class UserProfile:
    cats: np.ndarray  # int32 [n_users, len(USER_CAT_COLS)], 0 = không biết
    cardinalities: list[int]


def build_user_profile(customers_path: str | Path, user_raw_ids) -> UserProfile:
    """Thuộc tính tĩnh của khách, theo đúng thứ tự user_raw_ids (chỉ số user của mô hình)."""
    c = pd.read_csv(customers_path, dtype={"customer_id": "string"}).set_index("customer_id")
    if len(c) < 1_200_000:
        raise ValueError(f"customers.csv chỉ có {len(c):,} khách — bản đầy đủ có 1.371.980 (có thể đã bị Excel cắt)")
    c = c.reindex(pd.Index(user_raw_ids, dtype="string"))
    age = pd.to_numeric(c["age"], errors="coerce")
    cols = {
        "age_bucket": np.where(age.isna(), 0, np.searchsorted(AGE_EDGES, age.fillna(0), side="right") + 1),
        "club_member_status": _codes(c["club_member_status"], ["ACTIVE", "PRE-CREATE", "LEFT CLUB"]),
        "fashion_news_frequency": _codes(c["fashion_news_frequency"].replace({"None": "NONE"}),
                                         ["NONE", "Regularly", "Monthly"]),
        "FN": np.where(pd.to_numeric(c["FN"], errors="coerce") == 1, 2, 1),
        "Active": np.where(pd.to_numeric(c["Active"], errors="coerce") == 1, 2, 1),
    }
    cards = [len(AGE_EDGES) + 2, 4, 4, 3, 3]
    return UserProfile(np.stack([np.asarray(cols[k], dtype=np.int32) for k in USER_CAT_COLS], axis=1), cards)


def _codes(s: pd.Series, vocab: list[str]) -> np.ndarray:
    m = {v: k + 1 for k, v in enumerate(vocab)}
    return s.map(lambda v: m.get(v, 0)).fillna(0).to_numpy(dtype=np.int32)


def user_time_features(pair_users: np.ndarray, pair_days: np.ndarray, users: np.ndarray, days) -> np.ndarray:
    """Đặc trưng thời gian của user tại ngày `days`, từ các cặp (user, ngày mua đầu) TRƯỚC ngày đó:
    log1p(số ngày từ lần mua gần nhất; 730 nếu chưa mua) và log1p(số cặp đã mua)."""
    users = np.asarray(users, dtype=np.int64)
    days = np.broadcast_to(np.asarray(days, dtype=np.int64), users.shape)
    order = np.lexsort((pair_days, pair_users))
    pu, pd_ = np.asarray(pair_users)[order], np.asarray(pair_days)[order]
    key = pu * 100_000 + pd_
    q = users * 100_000 + days
    n_before = np.searchsorted(key, q, side="left") - np.searchsorted(pu, users, side="left")
    last_idx = np.searchsorted(key, q, side="left") - 1
    has = n_before > 0
    gap = np.where(has, days - pd_[np.clip(last_idx, 0, None)], 730)
    out = np.stack([np.log1p(np.clip(gap, 0, 730)), np.log1p(n_before)], axis=-1).astype(np.float32)
    return out / LOG_SCALE
