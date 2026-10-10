"""Mô hình lai MF + DNN có đặc trưng (NeuMF-F) và các thành phần cho giao thức v2 (audit/PREREG_v2.md).

NeuMF-F giữ cấu trúc hai nhánh của NeuMF (He et al., 2017) — nhánh GMF (tích từng phần tử, tuyến tính) và nhánh MLP
(phi tuyến) hợp nhất ở lớp dự đoán chung (Early Fusion) — nhưng vector user/item của mỗi nhánh là
    embedding ID  +  phép chiếu tuyến tính của đặc trưng:
  - item: 11 thuộc tính danh mục (embedding), vector mô tả văn bản, đặc trưng thời gian tại ngày t (doanh số toàn H&M
    trong 7/28/91 ngày trước t, tuổi sản phẩm, cờ chưa từng bán);
  - user: 5 thuộc tính tĩnh (embedding) và đặc trưng thời gian (khoảng cách tới lần mua gần nhất, số cặp đã mua).
Item có chỉ số >= n_id_items không có embedding ID, chỉ dùng đặc trưng (với dữ liệu hiện tại mọi sản phẩm đều có ID);
khi huấn luyện, ID của item bị bỏ ngẫu nhiên với xác suất id_dropout để mô hình học được cách chấm khi thiếu ID.
Các cờ use_* tắt từng nhánh/nhóm đặc trưng cho ablation (GMF-F, MLP-F, bỏ văn bản, ...).
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn

from src.data_pipeline.features import ITEM_TIME_DIM, LOG_SCALE, SALES_WINDOWS, USER_TIME_DIM


class NeuMFF(nn.Module):
    def __init__(self, n_users: int, n_id_items: int, item_cards: list[int], user_cards: list[int], text_dim: int,
                 gmf_dim: int = 32, mlp_dim: int = 32, layers: list[int] | None = None, dropout: float = 0.2,
                 cat_dim: int = 8, id_dropout: float = 0.0, use_gmf: bool = True, use_mlp: bool = True,
                 use_attr: bool = True, use_text: bool = True, use_time: bool = True, use_user: bool = True):
        super().__init__()
        if not (use_gmf or use_mlp):
            raise ValueError("Cần ít nhất một nhánh (GMF hoặc MLP)")
        layers = layers or [2 * mlp_dim, mlp_dim, mlp_dim // 2, mlp_dim // 4]
        if layers[0] != 2 * mlp_dim:
            raise ValueError(f"layers[0] phải bằng 2*mlp_dim = {2 * mlp_dim}")
        self.n_id = int(n_id_items)
        self.id_dropout = float(id_dropout)
        self.flags = dict(use_gmf=use_gmf, use_mlp=use_mlp, use_attr=use_attr, use_text=use_text, use_time=use_time,
                          use_user=use_user)
        self.use_gmf, self.use_mlp = use_gmf, use_mlp
        self.use_attr, self.use_text, self.use_time, self.use_user = use_attr, use_text, use_time, use_user

        def id_emb(n, d):
            return nn.Embedding(n + 1, d, padding_idx=n)  # hàng cuối = "không có ID" (vector 0, không được cập nhật)

        self.item_attr = nn.ModuleList(nn.Embedding(c, cat_dim) for c in item_cards) if use_attr else None
        self.user_attr = nn.ModuleList(nn.Embedding(c, cat_dim) for c in user_cards) if use_user else None
        item_in = (len(item_cards) * cat_dim if use_attr else 0) + (text_dim if use_text else 0) + \
            (ITEM_TIME_DIM if use_time else 0)
        user_in = (len(user_cards) * cat_dim + (USER_TIME_DIM if use_time else 0)) if use_user else 0

        def branch(d):
            return nn.ModuleDict(dict(
                u=nn.Embedding(n_users, d), i=id_emb(self.n_id, d),
                fi=nn.Linear(item_in, d, bias=False) if item_in else nn.Identity(),
                fu=nn.Linear(user_in, d, bias=False) if user_in else nn.Identity()))

        self.item_in, self.user_in = item_in, user_in
        self.gmf = branch(gmf_dim) if use_gmf else None
        self.mlp = branch(mlp_dim) if use_mlp else None
        if use_mlp:
            mods = []
            for a, b in zip(layers[:-1], layers[1:]):
                mods += [nn.Linear(a, b), nn.ReLU(), nn.Dropout(dropout)]
            self.tower = nn.Sequential(*mods)
        out_dim = (gmf_dim if use_gmf else 0) + (layers[-1] if use_mlp else 0)
        self.output_layer = nn.Linear(out_dim, 1, bias=False)
        self._init_weights()
        self._cache = None
        self.eval_day = None

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Embedding):
                nn.init.normal_(m.weight, std=0.01)
                if m.padding_idx is not None:
                    with torch.no_grad():
                        m.weight[m.padding_idx].zero_()
            elif isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    # ------------------------------------------------------------ dữ liệu ngoài
    def attach(self, item_cats, item_text, item_cum, item_first_day, user_cats=None):
        """Gắn bảng đặc trưng (không lưu trong state_dict — dựng lại từ cache khi nạp mô hình)."""
        dev = self.output_layer.weight.device
        self.register_buffer("item_cats", torch.as_tensor(np.asarray(item_cats), dtype=torch.long, device=dev),
                             persistent=False)
        self.register_buffer("item_text", torch.as_tensor(np.asarray(item_text), dtype=torch.float32, device=dev),
                             persistent=False)
        self.register_buffer("item_cum", torch.as_tensor(np.asarray(item_cum), dtype=torch.float32, device=dev),
                             persistent=False)
        self.register_buffer("item_first", torch.as_tensor(np.asarray(item_first_day), dtype=torch.long, device=dev),
                             persistent=False)
        uc = np.zeros((1, 1), dtype=np.int64) if user_cats is None else np.asarray(user_cats)
        self.register_buffer("user_cats", torch.as_tensor(uc, dtype=torch.long, device=dev), persistent=False)
        if self.use_user and user_cats is None:
            raise ValueError("use_user=True cần user_cats (customers.csv)")
        self._cache = None
        return self

    def set_stage(self, cutoff: int, user_time, scoreable):
        """Ngữ cảnh đánh giá: ngày mốc cắt, đặc trưng thời gian của user tại mốc, item có ID (dữ liệu huấn luyện)."""
        dev = self.output_layer.weight.device
        self.eval_day = int(cutoff)
        self.register_buffer("eval_utime", torch.as_tensor(np.asarray(user_time), dtype=torch.float32, device=dev),
                             persistent=False)
        self.register_buffer("id_mask", torch.as_tensor(np.asarray(scoreable), dtype=torch.bool, device=dev),
                             persistent=False)
        self._cache = None
        return self

    def train(self, mode: bool = True):
        self._cache = None  # trọng số sắp đổi -> bỏ vector đã tính sẵn cho đánh giá
        return super().train(mode)

    # ------------------------------------------------------------- đặc trưng
    def item_time(self, items, day):
        cum = self.item_cum
        last = cum.shape[1] - 1
        d = day.clamp(0, last)
        now = cum[items, d]
        cols = [torch.log1p(now - cum[items, (day - w).clamp(0, last)]) / LOG_SCALE for w in SALES_WINDOWS]
        fd = self.item_first[items]
        cols.append(torch.log1p((day - fd).clamp(min=0).float()) / LOG_SCALE)
        cols.append((fd >= day).float())
        return torch.stack(cols, dim=-1)

    def item_features(self, items, day):
        parts = []
        if self.use_attr:
            cats = self.item_cats[items]
            parts += [emb(cats[..., k]) for k, emb in enumerate(self.item_attr)]
        if self.use_text:
            parts.append(self.item_text[items])
        if self.use_time:
            parts.append(self.item_time(items, day))
        return torch.cat(parts, dim=-1) if parts else None

    def user_features(self, users, utime):
        if not self.use_user:
            return None
        cats = self.user_cats[users]
        parts = [emb(cats[..., k]) for k, emb in enumerate(self.user_attr)]
        if self.use_time:
            parts.append(utime)
        return torch.cat(parts, dim=-1)

    def _vectors(self, br, users, items, has_id, fi, fu):
        id_idx = torch.where(has_id, items, torch.full_like(items, self.n_id))
        q = br["i"](id_idx)
        p = br["u"](users)
        if fi is not None:
            q = q + br["fi"](fi)
        if fu is not None:
            p = p + br["fu"](fu)
        return p, q

    def _head(self, pg, qg, pm, qm):
        out = []
        if self.use_gmf:
            out.append(pg * qg)
        if self.use_mlp:
            out.append(self.tower(torch.cat([pm, qm], dim=-1)))
        return self.output_layer(torch.cat(out, dim=-1)).squeeze(-1)

    # ---------------------------------------------------------------- forward
    def forward(self, users, items, day=None, utime=None):
        if day is None:  # đánh giá tại mốc cắt của giai đoạn (set_stage)
            return self._forward_eval(users, items)
        has_id = items < self.n_id
        if self.training and self.id_dropout > 0:
            has_id = has_id & (torch.rand(items.shape, device=items.device) >= self.id_dropout)
        fi, fu = self.item_features(items, day), self.user_features(users, utime)
        pg = qg = pm = qm = None
        if self.use_gmf:
            pg, qg = self._vectors(self.gmf, users, items, has_id, fi, fu)
        if self.use_mlp:
            pm, qm = self._vectors(self.mlp, users, items, has_id, fi, fu)
        return self._head(pg, qg, pm, qm)

    @torch.no_grad()
    def _build_cache(self):
        if self.eval_day is None:
            raise RuntimeError("Gọi set_stage(...) trước khi đánh giá")
        dev = self.output_layer.weight.device
        n_items, n_users = self.item_cats.shape[0], self.eval_utime.shape[0]
        items = torch.arange(n_items, device=dev)
        users = torch.arange(n_users, device=dev)
        day = torch.full((n_items,), self.eval_day, dtype=torch.long, device=dev)
        has_id = (items < self.n_id) & self.id_mask
        fi, fu = self.item_features(items, day), self.user_features(users, self.eval_utime)
        cache = {}
        for name, br in (("g", self.gmf), ("m", self.mlp)):
            if br is not None:
                p, _ = self._vectors(br, users, users.new_zeros(n_users), users.new_ones(n_users, dtype=torch.bool),
                                     None, fu)
                _, q = self._vectors(br, items.new_zeros(n_items), items, has_id, fi, None)
                cache[name] = (p, q)
        self._cache = cache

    def _forward_eval(self, users, items):
        if self._cache is None:
            self._build_cache()
        pg, qg = self._cache.get("g", (None, None))
        pm, qm = self._cache.get("m", (None, None))
        return self._head(pg[users] if pg is not None else None, qg[items] if qg is not None else None,
                          pm[users] if pm is not None else None, qm[items] if qm is not None else None)


class MaskedScorer(nn.Module):
    """Bọc mô hình PyTorch chỉ dùng ID: item không có dữ liệu huấn luyện của giai đoạn (scoreable = False) nhận điểm -inf,
    tức bị xếp cuối (thứ tự giữa chúng do khoá phá hoà quyết định). Chỉ số item vượt bảng embedding của mô hình được kẹp
    về 0 trước khi gọi mô hình (điểm đó bị thay bằng -inf)."""

    def __init__(self, model: nn.Module, scoreable, n_model_items: int):
        super().__init__()
        self.model = model
        self.n = int(n_model_items)
        self.register_buffer("mask", torch.as_tensor(np.asarray(scoreable), dtype=torch.bool))

    def forward(self, users, items):
        safe = torch.where(items < self.n, items, torch.zeros_like(items))
        s = self.model(users, safe)
        return torch.where(self.mask[items], s, torch.full_like(s, float("-inf")))


class MaskedScoreFn:
    """Như MaskedScorer, cho baseline chấm điểm bằng NumPy (score_items)."""

    def __init__(self, fn, scoreable, n_model_items: int):
        self.fn, self.mask, self.n = fn, np.asarray(scoreable, dtype=bool), int(n_model_items)

    def score_items(self, user: int, items) -> np.ndarray:
        items = np.asarray(items, dtype=np.int64)
        s = np.asarray(self.fn.score_items(user, np.where(items < self.n, items, 0)), dtype=np.float64)
        return np.where(self.mask[items], s, -np.inf)

    def score(self, user: int, item: int) -> float:
        return float(self.score_items(user, [item])[0])

    __call__ = score


class RecentPopularity:
    """Most Popular theo thời gian: số giao dịch của sản phẩm trên toàn H&M trong `window` ngày trước mốc cắt.
    Sản phẩm mới có doanh số 0 -> xếp sau mọi sản phẩm đã bán."""

    def __init__(self, item_cum: np.ndarray, cutoff: int, window: int):
        cum = np.asarray(item_cum)
        self.pop = (cum[:, cutoff] - cum[:, max(cutoff - int(window), 0)]).astype(np.float64)

    def score_items(self, user: int, items) -> np.ndarray:
        return self.pop[np.asarray(items, dtype=np.int64)]

    def score(self, user: int, item: int) -> float:
        return float(self.pop[int(item)])

    __call__ = score


# Không có màu: sau khi gộp mọi màu của một mẫu (features.group_by_product), cột màu là hằng số.
CONTENT_ONEHOT = {"product_group_name": 1, "index_group_no": 8, "garment_group_no": 10}


class ContentProfile:
    """Gợi ý theo nội dung (không dùng ID, không cần lấy mẫu âm): vector sản phẩm = [vector văn bản ; one-hot nhóm sản
    phẩm, nhóm chỉ mục, nhóm may mặc], chuẩn hoá L2; hồ sơ user = trung bình (có trọng số theo độ mới nếu đặt
    half_life ngày) vector các sản phẩm đã mua trong tập huấn luyện; điểm = cosine. Chấm được cả sản phẩm mới."""

    def __init__(self, item_text, item_cats, item_cards, train_df, n_users: int, cutoff: int,
                 half_life: float | None = None):
        parts = [np.asarray(item_text, dtype=np.float32)]
        for col_idx in CONTENT_ONEHOT.values():
            card = int(item_cards[col_idx])
            oh = np.zeros((len(item_text), card), dtype=np.float32)
            oh[np.arange(len(item_text)), np.asarray(item_cats)[:, col_idx]] = 1.0
            oh[:, 0] = 0.0  # "không biết" không mang thông tin
            parts.append(oh / np.sqrt(len(CONTENT_ONEHOT)))
        x = np.concatenate(parts, axis=1)
        self.X = x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-12)
        u = train_df["user"].to_numpy(np.int64)
        i = train_df["item"].to_numpy(np.int64)
        w = np.ones(len(u), dtype=np.float32) if half_life is None else \
            np.power(0.5, (cutoff - train_df["day"].to_numpy(np.float64)) / float(half_life)).astype(np.float32)
        prof = np.zeros((n_users, self.X.shape[1]), dtype=np.float32)
        np.add.at(prof, u, self.X[i] * w[:, None])
        self.P = prof / np.maximum(np.linalg.norm(prof, axis=1, keepdims=True), 1e-12)

    def score_items(self, user: int, items) -> np.ndarray:
        return self.X[np.asarray(items, dtype=np.int64)] @ self.P[int(user)]

    def score(self, user: int, item: int) -> float:
        return float(self.score_items(user, [item])[0])

    __call__ = score
