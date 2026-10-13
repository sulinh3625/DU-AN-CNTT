from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

from .base import DatasetAdapter


class HMAdapter(DatasetAdapter):
    """Adapter H&M Personalized Fashion Recommendations.

    Không chấp nhận .xlsx làm raw source vì Excel cắt tại 1,048,576 dòng,
    trong khi transactions_train.csv gốc lớn hơn rất nhiều.
    """

    def __init__(self, path: Path, encoding: str = "utf-8"):
        self.path = Path(path)
        self.encoding = encoding

    def load_events(self) -> pd.DataFrame:
        if self.path.suffix.lower() in {".xlsx", ".xls"}:
            raise ValueError(
                "Không dùng transactions_train.xlsx làm dữ liệu H&M chính thức: "
                "Excel bị giới hạn 1,048,576 dòng. Hãy dùng transactions_train.csv gốc."
            )
        if not self.path.exists():
            raise FileNotFoundError(f"Không tìm thấy H&M transactions: {self.path}")

        raw = pd.read_csv(
            self.path,
            encoding=self.encoding,
            usecols=["t_dat", "customer_id", "article_id", "price", "sales_channel_id"],
            dtype={"customer_id": "string", "article_id": "string"},
        )
        raw["source_order"] = np.arange(len(raw), dtype=np.int64)
        raw["t_dat"] = pd.to_datetime(raw["t_dat"], errors="coerce")
        raw["article_id"] = raw["article_id"].astype("string").str.zfill(10)
        raw["price"] = pd.to_numeric(raw["price"], errors="coerce").fillna(0.0)

        raw = raw.dropna(subset=["customer_id", "article_id", "t_dat"]).copy()
        raw = raw.rename(columns={
            "customer_id": "user_raw",
            "article_id": "item_raw",
            "t_dat": "timestamp",
            "price": "value_raw",
        })
        return raw[["user_raw", "item_raw", "timestamp", "value_raw", "source_order"]]
