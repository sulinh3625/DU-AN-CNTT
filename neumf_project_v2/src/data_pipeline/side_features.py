"""Đọc thông tin phụ trợ (side information) của H&M: articles.csv và customers.csv.

Pipeline tương tác (adapter + build_interactions) chỉ làm việc với transactions;
module này ánh xạ thuộc tính sản phẩm/khách hàng về đúng chỉ số item/user đã
re-index để các mô hình Content-based dùng được.

item_raw/user_raw có 2 dạng tuỳ nguồn:
  - Đọc thẳng CSV (hm_subset.yaml): chuỗi article_id / customer_id gốc.
  - Đọc cache Parquet (hm.yaml): mã int32 -> cần item_id_map / user_id_map
    do scripts/00_prepare_hm_cache.py sinh ra để tra ngược ID gốc.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

AGE_BINS = [0, 25, 35, 45, 55, 200]
AGE_LABELS = ["<25", "25-34", "35-44", "45-54", "55+"]
UNKNOWN_AGE = "unknown"


def _raw_keys_to_original(raw_keys: list, id_map_path: Path | None, id_col: str, raw_col: str) -> pd.Series:
    """Trả về Series: raw key -> ID gốc (chuỗi)."""
    raw = pd.Series(raw_keys, dtype="object")
    if len(raw) and isinstance(raw.iloc[0], str):
        return pd.Series(raw.values, index=raw.values, dtype="object")
    if id_map_path is None or not Path(id_map_path).exists():
        raise FileNotFoundError(
            f"{raw_col} là mã số (cache Parquet) nhưng không tìm thấy bảng ánh xạ {id_map_path}. "
            f"Chạy scripts/00_prepare_hm_cache.py trước."
        )
    id_map = pd.read_parquet(id_map_path, columns=[id_col, raw_col])
    lookup = dict(zip(id_map[raw_col].astype(np.int64), id_map[id_col].astype(str)))
    return pd.Series([lookup.get(int(k)) for k in raw_keys], index=raw_keys, dtype="object")


def load_hm_item_features(
    item2idx: dict,
    articles_path: str | Path,
    columns: list[str],
    item_id_map_path: str | Path | None = None,
) -> pd.DataFrame:
    """DataFrame index = item idx (0..n_items-1), cột = thuộc tính articles.csv.

    Item không tìm thấy trong articles.csv giữ giá trị NaN (mô hình CBF coi như
    không có đặc trưng, không gây lỗi).
    """
    articles_path = Path(articles_path)
    if not articles_path.exists():
        raise FileNotFoundError(f"Không tìm thấy articles.csv: {articles_path}")
    usecols = ["article_id"] + [c for c in columns if c != "article_id"]
    articles = pd.read_csv(articles_path, usecols=usecols, dtype=str)
    articles["article_id"] = articles["article_id"].str.zfill(10)
    articles = articles.drop_duplicates("article_id").set_index("article_id")

    raw_keys = list(item2idx.keys())
    original = _raw_keys_to_original(raw_keys, item_id_map_path, "article_id", "item_raw")
    original = original.astype(str).str.zfill(10)

    out = articles.reindex(original.values)
    out.index = [item2idx[k] for k in raw_keys]
    return out.sort_index()


def age_bucket(age) -> str:
    if age is None or pd.isna(age):
        return UNKNOWN_AGE
    idx = np.searchsorted(AGE_BINS, float(age), side="right") - 1
    if idx < 0 or idx >= len(AGE_LABELS):
        return UNKNOWN_AGE
    return AGE_LABELS[idx]


def load_hm_user_age_groups(
    user_raws: list,
    customers_path: str | Path,
    user_id_map_path: str | Path | None = None,
) -> dict:
    """Ánh xạ user_raw -> nhóm tuổi (chuỗi) từ customers.csv.

    Chỉ dùng cột age: FN/Active phần lớn là NaN, postal_code là hash không
    mang ngữ nghĩa, nên không đưa vào mô hình.
    """
    customers_path = Path(customers_path)
    if not customers_path.exists():
        raise FileNotFoundError(f"Không tìm thấy customers.csv: {customers_path}")
    customers = pd.read_csv(customers_path, usecols=["customer_id", "age"], dtype={"customer_id": str})
    age_by_customer = dict(zip(customers["customer_id"], customers["age"]))

    original = _raw_keys_to_original(list(user_raws), user_id_map_path, "customer_id", "user_raw")
    return {raw: age_bucket(age_by_customer.get(orig)) for raw, orig in original.items()}
