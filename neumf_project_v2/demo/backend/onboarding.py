"""Gợi ý rule-based cho khách hàng mới: lọc theo lựa chọn + độ phổ biến trong TRAIN.

Đây KHÔNG phải mô hình NeuMF (mô hình không có embedding cho user mới).
Không lưu thông tin người dùng, không học trong phiên.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

CONFIG_PATH = Path(__file__).with_name("onboarding_config.yaml")


def load_onboarding_config(path: Path = CONFIG_PATH) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


class Onboarding:
    def __init__(self, train_df: pd.DataFrame, articles: pd.DataFrame, user_age: pd.Series, config: dict):
        """train_df: chỉ train split (cột user, item, last_timestamp).
        articles: index = item idx của catalog sau k-core.
        user_age: tuổi theo user idx (có thể rỗng)."""
        self.cfg = config
        self.articles = articles
        self.areas = {a["key"]: a for a in config["areas"]}
        self.window_days = int(config["popularity_window_days"])
        end = train_df["last_timestamp"].max()
        start = max(end - pd.Timedelta(days=self.window_days - 1), train_df["last_timestamp"].min())
        window = train_df.loc[train_df["last_timestamp"] >= start, ["user", "item"]].copy()
        window["age"] = window["user"].map(user_age)
        self.window = window
        self.window_range = (start.date().isoformat(), end.date().isoformat())
        self.has_age = bool(window["age"].notna().any())

    # ----------------------------------------------------------------- options
    def age_groups(self) -> list[dict]:
        if not self.has_age:
            return []
        out = []
        for lo, hi in self.cfg["age_groups"]:
            n = int(self.window["age"].between(lo, hi).sum())
            out.append({"key": f"{lo}-{hi}", "label": f"{lo}–{hi}", "n_transactions": n})
        return out

    def options(self) -> dict:
        arts = self.articles
        areas = []
        for a in self.cfg["areas"]:
            sub = arts[arts["index_group_name"].isin(a["index_group_names"])]
            areas.append({
                "key": a["key"], "label": a["label"], "index_group_names": a["index_group_names"],
                "n_items": int(len(sub)),
                "product_groups": sorted(sub["product_group_name"].unique().tolist()),
                "colours": sorted(sub["perceived_colour_master_name"].unique().tolist()),
            })
        return {
            "areas": areas,
            "age_groups": self.age_groups(),
            "min_age_group_transactions": int(self.cfg["min_age_group_transactions"]),
            "popularity_window_days": self.window_days,
            "popularity_window": self.window_range,
            "age_coverage": float(self.window["age"].notna().mean()),
        }

    # --------------------------------------------------------------- ranking
    def _popularity(self, age_group: str | None) -> tuple[pd.Series, list[str], str | None]:
        """Số khách mua mỗi item trong cửa sổ train; trả thêm nhãn nhóm tuổi nếu thực sự đã lọc."""
        notes, rows, applied = [], self.window, None
        if age_group:
            lo, hi = (int(x) for x in age_group.split("-"))
            sub = rows[rows["age"].between(lo, hi)]
            threshold = int(self.cfg["min_age_group_transactions"])
            if len(sub) < threshold:
                notes.append(
                    f"Nhóm tuổi {lo}–{hi} chỉ có {len(sub)} giao dịch train trong cửa sổ "
                    f"(< ngưỡng {threshold}), đã bỏ lọc theo tuổi."
                )
            else:
                rows, applied = sub, f"{lo}–{hi}"
                notes.append(f"Độ phổ biến tính riêng trong nhóm tuổi {lo}–{hi} ({len(sub)} giao dịch train).")
        return rows["item"].value_counts(), notes, applied

    def _ranked(self, pop: pd.Series, mask: pd.Series) -> list[int]:
        cand = pop[pop.index.isin(self.articles.index[mask.to_numpy()])]
        cand = cand[cand > 0]
        # Tie-break ổn định theo article_id.
        df = pd.DataFrame({"count": cand, "aid": self.articles.loc[cand.index, "article_id"]})
        return df.sort_values(["count", "aid"], ascending=[False, True]).index.astype(int).tolist()

    def recommend(self, area: str, product_groups=(), colours=(), age_group: str | None = None, k: int = 10) -> dict:
        if area not in self.areas:
            raise KeyError(area)
        arts = self.articles
        area_cfg = self.areas[area]
        pop, notes, age_applied = self._popularity(age_group)
        m_area = arts["index_group_name"].isin(area_cfg["index_group_names"])
        m_type = arts["product_group_name"].isin(product_groups)
        m_col = arts["perceived_colour_master_name"].isin(colours)

        levels = [("Khớp mọi lựa chọn", m_area & (m_type if product_groups else True) & (m_col if colours else True))]
        if colours:
            levels.append(("Đã bỏ điều kiện màu", m_area & (m_type if product_groups else True)))
        if product_groups:
            levels.append(("Đã bỏ điều kiện loại sản phẩm (chỉ giữ khu vực)", m_area))

        picked, relaxed, seen = [], [], set()
        for level, (label, mask) in enumerate(levels):
            if len(picked) >= k:
                break
            if level > 0:  # tới đây nghĩa là bậc trước chưa đủ K item
                relaxed.append(label)
            for i in self._ranked(pop, pd.Series(mask, index=arts.index)):
                if len(picked) >= k:
                    break
                if i not in seen:
                    seen.add(i)
                    picked.append((i, level, label))

        hot = [i for i in self._ranked(pop, m_area) if i not in seen][:k]
        age_note = f", nhóm tuổi {age_applied}" if age_applied else ""

        def item(i: int, level: int = 0, match: str | None = None) -> dict:
            a = arts.loc[i]
            return {
                "item_idx": int(i),
                "count": int(pop.get(i, 0)),
                "reason": f"Bán chạy trong nhóm {a['index_group_name']} · {a['product_type_name']}",
                "detail": f"{int(pop.get(i, 0))} khách mua trong train ({self.window_range[0]} → {self.window_range[1]}){age_note}",
                "relax_level": level,
                "match": match,
            }

        return {
            "area": area_cfg["label"],
            "preferred": [item(i, lv, lb) for i, lv, lb in picked],
            "hot_in_area": [item(i) for i in hot],
            "relaxations": relaxed,
            "notes": notes,
            "popularity_window": self.window_range,
            "age_coverage": float(self.window["age"].notna().mean()),
        }
