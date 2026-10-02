"""Late fusion — hợp nhất ở mức quyết định/điểm dự đoán (Hồ Thị Linh, 2023, mục 1.1.2.2; Atrey et al., 2010).

    p = F(h_A(u, i), h_B(u, i)),   F = w · minmax(điểm A) + (1 − w) · minmax(điểm B)

Hai mô hình thành phần được huấn luyện RIÊNG; min-max lấy trên tập ứng viên của từng user (đưa hai thang điểm về
[0, 1]); w chọn trên validation. Với A = GMF (MF) và B = MLP (DNN) đây là late fusion MF + DNN dùng đúng hai thành
phần của NeuMF — NeuMF là early fusion của cùng hai nhánh (nối vector rồi một lớp dự đoán, học chung).
w = 1 cho đúng thứ hạng của A, w = 0 cho đúng thứ hạng của B.
"""
from __future__ import annotations

import numpy as np
import torch


def model_scores(model, user: int, items) -> np.ndarray:
    """Điểm của một mô hình cho (user, items): logit với mạng PyTorch, score_items với baseline."""
    items = np.asarray(items, dtype=np.int64)
    if isinstance(model, torch.nn.Module):
        device = next(model.parameters()).device
        with torch.no_grad():
            u = torch.full((len(items),), int(user), dtype=torch.long, device=device)
            out = model(u, torch.as_tensor(items, dtype=torch.long, device=device))
        return out.float().cpu().numpy().astype(np.float64)
    return np.asarray(model.score_items(user, items), dtype=np.float64)


def minmax(x: np.ndarray) -> np.ndarray:
    lo, hi = float(np.min(x)), float(np.max(x))
    return (x - lo) / (hi - lo) if hi > lo else np.zeros_like(x, dtype=np.float64)


class LateFusion:
    """score_items(u, items) = w · minmax(A) + (1 − w) · minmax(B). Dùng với evaluate_score_function."""

    def __init__(self, model_a, model_b, w: float):
        if not 0.0 <= w <= 1.0:
            raise ValueError("w phải nằm trong [0, 1]")
        self.a, self.b, self.w = model_a, model_b, float(w)
        for m in (model_a, model_b):
            if isinstance(m, torch.nn.Module):
                m.eval()

    def score_items(self, user: int, items) -> np.ndarray:
        a = minmax(model_scores(self.a, user, items))
        b = minmax(model_scores(self.b, user, items))
        return self.w * a + (1.0 - self.w) * b


def fusion_cache(model_a, model_b, records) -> dict[int, tuple[np.ndarray, np.ndarray]]:
    """Điểm đã chuẩn hoá của hai thành phần trên candidates của từng record — tính một lần, dùng cho mọi w."""
    for m in (model_a, model_b):
        if isinstance(m, torch.nn.Module):
            m.eval()
    return {int(r.user): (minmax(model_scores(model_a, r.user, r.candidates)),
                          minmax(model_scores(model_b, r.user, r.candidates))) for r in records}


class CachedLateFusion:
    """Như LateFusion nhưng đọc điểm đã tính sẵn (candidates phải đúng thứ tự của record đã dùng khi tạo cache)."""

    def __init__(self, cache: dict, w: float):
        if not 0.0 <= w <= 1.0:
            raise ValueError("w phải nằm trong [0, 1]")
        self.cache, self.w = cache, float(w)

    def score_items(self, user: int, items) -> np.ndarray:
        a, b = self.cache[int(user)]
        if len(a) != len(items):
            raise ValueError("candidates khác với lúc tạo cache")
        return self.w * a + (1.0 - self.w) * b
