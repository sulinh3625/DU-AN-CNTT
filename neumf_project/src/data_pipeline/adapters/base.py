from __future__ import annotations

from abc import ABC, abstractmethod
import pandas as pd


class DatasetAdapter(ABC):
    """Chuẩn hóa dataset nguồn về schema sự kiện chung."""

    @abstractmethod
    def load_events(self) -> pd.DataFrame:
        raise NotImplementedError
