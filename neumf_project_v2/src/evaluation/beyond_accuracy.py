from __future__ import annotations

import numpy as np


def catalog_coverage(recommendations: dict[int, list[int]], n_items: int) -> float:
    if n_items <= 0 or not recommendations:
        return 0.0
    unique = {item for recs in recommendations.values() for item in recs}
    return len(unique) / n_items


def average_recommendation_popularity(recommendations: dict[int, list[int]], item_counts) -> float:
    values = []
    for recs in recommendations.values():
        values.extend(float(item_counts.get(item, 0.0)) for item in recs)
    return float(np.mean(values)) if values else 0.0
