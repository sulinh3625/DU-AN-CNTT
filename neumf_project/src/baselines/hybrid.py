"""Mô hình lai truyền thống Hybrid-CBCF (audit/PREREG_bosung.md): kết hợp ở mức điểm dự đoán ba mô hình gợi ý truyền
thống — lọc nội dung (Content), lọc cộng tác theo người dùng (UserKNN) và theo sản phẩm (ItemKNN) — theo mô hình lai
của Hồ Thị Linh (2023, chương 3), điều chỉnh cho phản hồi ẩn và xếp hạng Top-K:

    x_ui = [minmax(s_Content(u, C_u))_i, minmax(s_UserKNN(u, C_u))_i, minmax(s_ItemKNN(u, C_u))_i]

- điểm của từng thành phần được chuẩn hoá min–max trên tập ứng viên C_u của khách (như LateFusion-F) để ba thang điểm
  so sánh được với nhau;
- bỏ phiếu (voted-based): điểm lai = trung bình, max hoặc min của ba điểm đã chuẩn hoá;
- trọng số (weighted-based): điểm lai = w · x_ui. Luận án học w bằng mạng truyền thẳng f(x) = Σ w_i x_i trên điểm đánh
  giá (rating). Phản hồi ẩn không có điểm đánh giá, nên w được học theo cặp: với sản phẩm đúng p và sản phẩm không đúng j
  trong tập ứng viên của cùng một khách, P(p xếp trên j) = σ(w · (x_up − x_uj)) — hồi quy logistic trên hiệu đặc trưng,
  không hệ số chặn (tiêu chí BPR với hàm điểm tuyến tính). Học theo từng cặp (khách, ứng viên) độc lập thì không được:
  gộp mọi khách vào một hồi quy logistic, trọng số bị chi phối bởi khác biệt giữa các khách chứ không phải thứ tự trong
  danh sách của từng khách.
Không có khởi tạo ngẫu nhiên; mẫu âm của bước học trọng số rút bằng numpy seed cố định — cùng dữ liệu cho cùng kết quả.
"""
from __future__ import annotations

import numpy as np

from src.models.late_fusion import minmax

COMPONENTS = ("content", "userknn", "itemknn")  # thứ tự cột của x và của w
FUSIONS = ("mean", "max", "min", "lr")  # ba cách bỏ phiếu + trọng số học bằng hồi quy logistic theo cặp
N_NEG, PAIR_SEED, C_REG = 50, 0, 1.0  # số sản phẩm không đúng mỗi sản phẩm đúng, seed rút mẫu, hệ số điều chuẩn 1/λ


def combine(x: np.ndarray, fusion: str, weights=None) -> np.ndarray:
    """Điểm lai từ ma trận điểm đã chuẩn hoá x (số ứng viên × số thành phần)."""
    if fusion == "mean":
        return x.mean(axis=1)
    if fusion == "max":
        return x.max(axis=1)
    if fusion == "min":
        return x.min(axis=1)
    if fusion == "lr":
        return x @ np.asarray(weights, dtype=np.float64)
    raise ValueError(f"fusion phải thuộc {FUSIONS}, nhận {fusion!r}")


class TraditionalHybrid:
    """score_items(u, items): điểm lai trên `items` — tập ứng viên của u; chuẩn hoá min–max lấy trên chính tập này, như
    LateFusion-F lúc chấm. components: ba đối tượng có score_items, theo thứ tự COMPONENTS."""

    def __init__(self, components, fusion: str, weights=None):
        if fusion not in FUSIONS:
            raise ValueError(f"fusion phải thuộc {FUSIONS}, nhận {fusion!r}")
        components = list(components)
        if fusion == "lr" and (weights is None or len(weights) != len(components)):
            raise ValueError("fusion='lr' cần đúng một trọng số cho mỗi thành phần")
        self.components, self.fusion = components, fusion
        self.weights = None if weights is None else np.asarray(weights, dtype=np.float64)

    def features(self, user: int, items) -> np.ndarray:
        """Ma trận len(items) × số thành phần: điểm của từng thành phần, chuẩn hoá min–max trên `items`."""
        return np.stack([minmax(np.asarray(c.score_items(user, items), dtype=np.float64)) for c in self.components],
                        axis=1)

    def score_items(self, user: int, items) -> np.ndarray:
        return combine(self.features(user, items), self.fusion, self.weights)


def pair_differences(features: list[np.ndarray], labels: list[np.ndarray], n_neg: int = N_NEG,
                     seed: int = PAIR_SEED) -> tuple[np.ndarray, np.ndarray]:
    """Mẫu học trọng số: với mỗi khách (theo thứ tự danh sách) và mỗi sản phẩm đúng p, rút n_neg sản phẩm không đúng j
    trong tập ứng viên (không lặp). Hiệu x_p − x_j mang nhãn 1, x_j − x_p nhãn 0 (đối xứng, nên không cần hệ số chặn)."""
    rng = np.random.default_rng(seed)
    diffs = []
    for x, y in zip(features, labels):
        y = np.asarray(y, dtype=bool)
        pos, neg = np.flatnonzero(y), np.flatnonzero(~y)
        if len(pos) == 0 or len(neg) == 0:
            continue
        for p in pos:
            j = rng.choice(neg, size=min(n_neg, len(neg)), replace=False)
            diffs.append(x[p] - x[j])
    if not diffs:
        raise ValueError("Cần khách có cả sản phẩm đúng lẫn sản phẩm không đúng để học trọng số")
    d = np.concatenate(diffs)
    return np.concatenate([d, -d]), np.concatenate([np.ones(len(d), np.int8), np.zeros(len(d), np.int8)])


def fit_weights(features: list[np.ndarray], labels: list[np.ndarray], n_neg: int = N_NEG, seed: int = PAIR_SEED,
                C: float = C_REG) -> np.ndarray:
    """Trọng số w của cách kết hợp 'lr': hồi quy logistic (scikit-learn, lbfgs — tất định) trên hiệu đặc trưng theo cặp
    (pair_differences), không hệ số chặn."""
    from sklearn.linear_model import LogisticRegression

    X, y = pair_differences(features, labels, n_neg, seed)
    return LogisticRegression(C=C, fit_intercept=False, max_iter=1000).fit(X, y).coef_.ravel().astype(np.float64)


def crossfit_scores(features: list[np.ndarray], labels: list[np.ndarray], users, n_folds: int = 2):
    """Điểm 'lr' khớp chéo theo khách: khách u thuộc phần u mod n_folds và được chấm bằng w học trên các phần còn lại,
    để số trên tập xác thực không lạc quan vì w học trên chính khách được chấm. Trả về (điểm của từng khách theo thứ tự
    đầu vào, {phần: w})."""
    fold = np.asarray(users, dtype=np.int64) % n_folds
    w = {f: fit_weights([features[i] for i in np.flatnonzero(fold != f)],
                        [labels[i] for i in np.flatnonzero(fold != f)]) for f in range(n_folds)}
    return [x @ w[int(f)] for x, f in zip(features, fold)], w
