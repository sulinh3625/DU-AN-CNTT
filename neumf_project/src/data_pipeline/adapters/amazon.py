"""Amazon review data 2014 (McAuley, Stanford SNAP) — dữ liệu đối chứng của đề tài (configs/amazon.yaml).

- reviews_<Danh mục>_5.json.gz: mỗi dòng một JSON (reviewerID, asin, overall, unixReviewTime, ...). Mỗi đánh giá coi là
  một tương tác ẩn khách–sản phẩm, như một giao dịch H&M (không dùng điểm sao).
- meta_<Danh mục>.json.gz: mỗi dòng một dict Python (nháy đơn, không phải JSON — đọc bằng ast.literal_eval): title,
  description, categories, brand, price, imUrl, ...

Mã sản phẩm: asin đổi sang số nguyên = vị trí trong danh sách asin đã sắp xếp của file đánh giá (asin_list), vì đường ống
v2 (protocol_v2) coi mã sản phẩm là số nguyên. Catalog dùng đúng thứ tự đó nên Catalog.rows(mã) = mã.
"""
from __future__ import annotations

import ast
import gzip
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse

from ..features import Catalog, DailySales, category_codes, text_vectors, to_day
from .base import DatasetAdapter

ITEM_CAT_COLS = ["brand", "category_1", "category_2", "category_3", "price_bucket"]
PRICE_EDGES = [5, 10, 15, 20, 30, 50, 100]  # USD: <5, 5–10, ..., 50–100, >=100; 0 = không có giá
ITEM_INFO_COLS = ["asin", "title", "brand", "category_1", "category_2", "category_3", "price", "imUrl"]
_ASIN = re.compile(r"'asin': '([^']+)'")


def read_reviews(path: str | Path) -> pd.DataFrame:
    """reviewerID, asin, overall, unixReviewTime theo thứ tự dòng trong file."""
    with gzip.open(path, "rt", encoding="utf-8") as f:
        rows = [json.loads(line) for line in f]
    return pd.DataFrame(rows, columns=["reviewerID", "asin", "overall", "unixReviewTime"])


def asin_list(reviews: pd.DataFrame) -> np.ndarray:
    """asin có trong file đánh giá, sắp xếp tăng dần — vị trí trong mảng này là mã sản phẩm."""
    return np.sort(reviews["asin"].astype(str).unique())


class AmazonAdapter(DatasetAdapter):
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load_events(self) -> pd.DataFrame:
        if not self.path.exists():
            raise FileNotFoundError(f"Không tìm thấy file đánh giá Amazon: {self.path}")
        r = read_reviews(self.path)
        return pd.DataFrame({
            "user_raw": r["reviewerID"].astype("string"),
            "item_raw": np.searchsorted(asin_list(r), r["asin"].astype(str).to_numpy()).astype(np.int64),
            "timestamp": pd.to_datetime(r["unixReviewTime"], unit="s"),
            "value_raw": pd.to_numeric(r["overall"], errors="coerce").fillna(0.0),
            "source_order": np.arange(len(r), dtype=np.int64),
        })


def read_meta(path: str | Path, wanted) -> dict[str, dict]:
    """Metadata của các asin trong `wanted` (chỉ literal_eval những dòng cần — file có ~260 nghìn dòng)."""
    wanted, out = set(wanted), {}
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            m = _ASIN.search(line)
            if m and m.group(1) in wanted:
                out[m.group(1)] = ast.literal_eval(line)
    return out


def category_path(meta: dict) -> list[str]:
    """3 cấp danh mục dưới gốc (vd. Skin Care > Face > Creams & Moisturizers), lấy đường đầu tiên; thiếu -> ""."""
    paths = meta.get("categories") or [[]]
    path = next((p for p in paths if p and p[0] == "Beauty"), paths[0])
    return (list(path[1:4]) + ["", "", ""])[:3]


def item_info(reviews_path: str | Path, meta_path: str | Path) -> pd.DataFrame:
    """Một dòng mỗi sản phẩm theo mã (index = mã, đúng thứ tự asin_list): ITEM_INFO_COLS. Thiếu metadata -> trống."""
    ids = asin_list(read_reviews(reviews_path))
    meta = read_meta(meta_path, ids)
    rows = []
    for a in ids:
        m = meta.get(a, {})
        price = m.get("price")
        rows.append(dict(asin=a, title=str(m.get("title") or ""), brand=str(m.get("brand") or "").strip(),
                         **dict(zip(("category_1", "category_2", "category_3"), category_path(m))),
                         price=float(price) if isinstance(price, (int, float)) else np.nan,
                         imUrl=str(m.get("imUrl") or ""), description=str(m.get("description") or "")))
    df = pd.DataFrame(rows)
    df.index.name = "item"
    return df


def build_features(reviews_path: str | Path, meta_path: str | Path, day0, text_dim: int = 64,
                   seed: int = 0) -> tuple[Catalog, DailySales, pd.DataFrame]:
    """Đặc trưng của Amazon theo đúng dạng của H&M (features.py), mã sản phẩm = vị trí trong asin_list:
    - Catalog: ITEM_CAT_COLS (thương hiệu, 3 cấp danh mục, nhóm giá; 0 = không biết) và vector văn bản (title +
      description, cùng TF-IDF + SVD như H&M);
    - DailySales: số đánh giá mỗi (sản phẩm, ngày) của toàn bộ file đánh giá, ngày tính từ day0 — thay cho doanh số
      theo ngày của H&M; đặc trưng thời gian tại ngày t vẫn chỉ đọc các ngày < t;
    - bảng thông tin sản phẩm (item_info, bỏ cột description) cho demo."""
    r = read_reviews(reviews_path)
    info = item_info(reviews_path, meta_path)
    price = info["price"].to_numpy()
    bucket = np.where(np.isnan(price), 0, np.searchsorted(PRICE_EDGES, np.nan_to_num(price), side="right") + 1)
    cats, cards = zip(*(category_codes(info[c]) for c in ITEM_CAT_COLS[:-1]))
    cats, cards = [*cats, bucket.astype(np.int32)], [*cards, len(PRICE_EDGES) + 2]
    text = text_vectors(info["title"] + " " + info["description"], text_dim, seed)

    item = np.searchsorted(info["asin"].to_numpy(), r["asin"].astype(str).to_numpy())
    day = to_day(pd.to_datetime(r["unixReviewTime"], unit="s").to_numpy(), day0)
    if day.min() < 0:
        raise ValueError(f"Có đánh giá trước day0 = {day0} — đặt day0 sớm hơn trong configs/amazon.yaml")
    n_days = int(day.max()) + 1
    counts = sparse.csr_matrix((np.ones(len(day), dtype=np.int32), (item, day)), shape=(len(info), n_days))
    first_day = np.full(len(info), n_days, dtype=np.int64)
    np.minimum.at(first_day, item, day)
    catalog = Catalog(np.arange(len(info), dtype=np.int64), np.stack(cats, axis=1), list(cards), text)
    return catalog, DailySales(counts, first_day), info.drop(columns="description")
