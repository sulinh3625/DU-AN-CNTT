"""Phần dùng chung của giao thức v2 (audit/PREREG_v2.md): nạp dữ liệu, dựng mô hình, huấn luyện, chấm điểm.

Mọi mô hình được huấn luyện và đánh giá bằng cùng các hàm ở đây, cả khi tinh chỉnh (22_tune_v2.py) lẫn khi đánh giá
cuối (23_final_v2.py). Mô hình chỉ dùng ID được bọc MaskedScorer/MaskedScoreFn: sản phẩm không có dữ liệu huấn luyện
của giai đoạn (gồm sản phẩm mới) nhận điểm -inf, tức bị xếp cuối.
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np
import torch
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.baselines import BPRMFBaseline, ItemKNNBaseline, MostPopularBaseline, RandomBaseline, UserKNNBaseline  # noqa: E402
from src.data_pipeline.dataset import TrainDataset  # noqa: E402
from src.data_pipeline.feature_dataset import FeatureTrainDataset  # noqa: E402
from src.data_pipeline.features import load_catalog, load_daily_sales  # noqa: E402
from src.data_pipeline.protocol_v2 import DataV2, Stage, build_v2  # noqa: E402
from src.evaluation.full_ranking import evaluate_score_function, evaluate_torch_model  # noqa: E402
from src.evaluation.v2 import evaluate_v2  # noqa: E402
from src.models.hybrid_features import (ContentProfile, MaskedScoreFn, MaskedScorer, NeuMFF,  # noqa: E402
                                        RecentPopularity)
from src.models.late_fusion import LateFusion  # noqa: E402
from src.models.neumf import GMF, MLP, NeuMF  # noqa: E402
from src.training.trainer import get_device, make_optimizer, train_one_model  # noqa: E402
from src.utils.seed import seed_everything  # noqa: E402

CFG = yaml.safe_load((PROJECT_ROOT / "configs" / "v2.yaml").read_text(encoding="utf-8"))
AUDIT = PROJECT_ROOT / "audit" / "v2"
METRICS = ["NDCG@10", "Recall@10", "HR@10", "Precision@10", "NDCG@5", "NDCG@20", "NDCG@10_old", "NDCG@10_new"]

DISPLAY = {"random": "Random", "popularity": "MostPopular", "recent_pop": "MostPopular-Recent", "content": "Content",
           "itemknn": "ItemKNN", "userknn": "UserKNN", "bpr": "BPR-MF", "gmf": "GMF", "mlp": "MLP", "neumf": "NeuMF",
           "gmf_f": "GMF-F", "mlp_f": "MLP-F", "neumf_f": "NeuMF-F", "late_f": "LateFusion-F"}
TORCH_ID = ("gmf", "mlp", "neumf")
TORCH_FEAT = ("gmf_f", "mlp_f", "neumf_f")
# Ablation của NeuMF-F (cùng siêu tham số với NeuMF-F, tắt một thành phần) — chỉ mô tả.
ABLATIONS = {"neumf_f-text": dict(use_text=False), "neumf_f-time": dict(use_time=False),
             "neumf_f-user": dict(use_user=False), "neumf_f-attr": dict(use_attr=False),
             "neumf_f-iddrop": dict(id_dropout=0.0)}
ABLATION_DISPLAY = {"neumf_f-text": "NeuMF-F − văn bản", "neumf_f-time": "NeuMF-F − thời gian",
                    "neumf_f-user": "NeuMF-F − thông tin khách", "neumf_f-attr": "NeuMF-F − thuộc tính SP",
                    "neumf_f-iddrop": "NeuMF-F − bỏ ID ngẫu nhiên"}

NEURAL = dict(lr=[1e-3, 5e-4], negative_ratio=[4, 8], embedding_dim=[32, 64], weight_decay=[0.0, 1e-6],
              dropout=[0.0, 0.2])
FEAT = {**NEURAL, "id_dropout": [0.0, 0.25, 0.5]}
W_GRID = [round(0.1 * i, 1) for i in range(11)]
GRIDS = {
    "recent_pop": dict(window=[7, 14, 28, 56, 91]),
    "content": dict(half_life=[None, 30, 90, 180, 365]),
    "itemknn": dict(k=[20, 50, 100, 200, 500], shrink=[0.0, 10.0, 50.0]),
    "userknn": dict(k=[20, 50, 100, 200, 500], shrink=[0.0, 10.0, 50.0]),
    "bpr": dict(embedding_dim=[32, 64, 128], lr=[0.01, 0.03, 0.05], reg=[0.001, 0.005, 0.01], epochs=[20, 40]),
    "gmf": {k: v for k, v in NEURAL.items() if k != "dropout"},
    "mlp": NEURAL,
    "neumf": NEURAL,
    "gmf_f": {k: v for k, v in FEAT.items() if k != "dropout"},
    "mlp_f": FEAT,
    "neumf_f": FEAT,
    "late_f": dict(w=W_GRID),
}
FULL_GRID = ("recent_pop", "content", "late_f")  # một tham số, thử đủ mọi giá trị của lưới
_NEURAL_DEFAULT = dict(lr=1e-3, negative_ratio=4, embedding_dim=32, weight_decay=1e-6, dropout=0.2)
DEFAULTS = {
    "recent_pop": dict(window=7), "content": dict(half_life=None),
    "itemknn": dict(k=100, shrink=0.0), "userknn": dict(k=100, shrink=0.0),
    "bpr": dict(embedding_dim=32, lr=0.03, reg=0.005, epochs=20),
    "gmf": {k: v for k, v in _NEURAL_DEFAULT.items() if k != "dropout"},
    "mlp": dict(_NEURAL_DEFAULT), "neumf": dict(_NEURAL_DEFAULT),
    "gmf_f": {**{k: v for k, v in _NEURAL_DEFAULT.items() if k != "dropout"}, "id_dropout": 0.25},
    "mlp_f": {**_NEURAL_DEFAULT, "id_dropout": 0.25}, "neumf_f": {**_NEURAL_DEFAULT, "id_dropout": 0.25},
    "late_f": dict(w=0.5),
}
LATE_PARTS = ("gmf_f", "mlp_f")  # Late Fusion-F = trộn điểm GMF-F và MLP-F huấn luyện riêng


def sample_configs(grid: dict, default: dict, n: int, seed: int = CFG["tuning"]["grid_seed"]) -> list[dict]:
    """default + (n-1) cấu hình rút không lặp từ lưới bằng numpy seed cố định (lưới nhỏ hơn n -> lấy hết)."""
    combos = [dict(zip(grid, vals)) for vals in itertools.product(*grid.values())]
    if default not in combos:
        raise ValueError(f"Cấu hình mặc định {default} không nằm trong lưới")
    others = [c for c in combos if c != default]
    pick = np.random.default_rng(seed).choice(len(others), size=min(n - 1, len(others)), replace=False)
    return [default] + [others[i] for i in sorted(pick)]


def configs_for(model: str, n: int) -> list[dict]:
    if model not in GRIDS:  # Random, Most Popular: không có tham số
        return [{}]
    if model in FULL_GRID:
        g = GRIDS[model]
        return [dict(zip(g, vals)) for vals in itertools.product(*g.values())]
    return sample_configs(GRIDS[model], DEFAULTS[model], n)


# ------------------------------------------------------------------ dữ liệu
def load_data(sample: str, with_test: bool = False) -> DataV2:
    f = CFG["features"]
    for p in (f["catalog"], f["sales"]):
        if not (PROJECT_ROOT / p).exists():
            raise SystemExit(f"Thiếu {p} — chạy `python scripts/21_build_features.py` trước.")
    return build_v2(PROJECT_ROOT / CFG["samples"][sample], CFG["val_start"], CFG["test_start"], CFG["k_core"],
                    load_catalog(PROJECT_ROOT / f["catalog"]), load_daily_sales(PROJECT_ROOT / f["sales"]),
                    PROJECT_ROOT / f["customers"], with_test=with_test)


def device():
    return get_device(CFG["training"]["device"])


def provenance() -> dict:
    """Truy vết một lần chạy: mã băm configs/v2.yaml + commit git + có thay đổi chưa commit (file đã theo dõi)."""
    import hashlib
    import subprocess

    def git(*a):
        try:
            return subprocess.run(["git", *a], cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return ""

    blob = (PROJECT_ROOT / "configs" / "v2.yaml").read_bytes()
    return {"config_path": "configs/v2.yaml", "config_hash": hashlib.sha256(blob).hexdigest()[:16],
            "code_hash": code_hash(), "git_commit": git("rev-parse", "HEAD") or None,
            "git_dirty": bool(git("status", "--porcelain", "--untracked-files=no"))}


CODE_FILES = ["src", "scripts/v2_common.py", "scripts/22_tune_v2.py", "configs/v2.yaml"]


def code_hash() -> str:
    """Mã băm nội dung mã nguồn ảnh hưởng tới kết quả v2 (src/*.py, script v2, cấu hình) — truy vết được cả khi
    chạy trước lúc commit: cùng mã băm = cùng mã nguồn."""
    import hashlib

    h = hashlib.sha256()
    for rel in CODE_FILES:
        p = PROJECT_ROOT / rel
        files = sorted(p.rglob("*.py")) if p.is_dir() else ([p] if p.exists() else [])
        for f in files:
            h.update(f.relative_to(PROJECT_ROOT).as_posix().encode())
            h.update(f.read_bytes().replace(b"\r\n", b"\n"))
    return h.hexdigest()[:16]


def eval_kw():
    return dict(k_values=CFG["evaluation"]["k_values"], tie_seed=CFG["evaluation"]["tie_break_seed"])


# ---------------------------------------------------------------- mô hình
def mlp_layers(d: int) -> list[int]:
    return [2 * d, d, d // 2, d // 4]


def base_key(key: str) -> str:
    return key.split("-")[0]


def is_feature(key: str) -> bool:
    return base_key(key) in TORCH_FEAT


def build_torch(key: str, p: dict, D: DataV2, dev) -> torch.nn.Module:
    d = int(p["embedding_dim"])
    if key == "gmf":
        return GMF(D.n_users, D.n_id_items, d).to(dev)
    if key == "mlp":
        return MLP(D.n_users, D.n_id_items, d, mlp_layers(d), p["dropout"]).to(dev)
    if key == "neumf":
        return NeuMF(D.n_users, D.n_id_items, d, mlp_layers(d), p["dropout"]).to(dev)
    base = base_key(key)
    flags = dict(use_gmf=base != "mlp_f", use_mlp=base != "gmf_f", **ABLATIONS.get(key, {}))
    id_drop = flags.pop("id_dropout", p.get("id_dropout", 0.0))
    net = NeuMFF(D.n_users, D.n_id_items, D.item_cards, D.user_cards, D.item_text.shape[1], gmf_dim=d, mlp_dim=d,
                 layers=mlp_layers(d), dropout=p.get("dropout", 0.0), id_dropout=id_drop, **flags).to(dev)
    return net.attach(D.item_cats, D.item_text, D.item_cum, D.item_first_day, D.user_cats)


def torch_scorer(key: str, net: torch.nn.Module, stage: Stage, D: DataV2, dev) -> torch.nn.Module:
    """Bộ chấm điểm cho một giai đoạn: mô hình có đặc trưng nhận ngữ cảnh giai đoạn; mô hình chỉ dùng ID được che."""
    if is_feature(key):
        return net.set_stage(stage.cutoff, stage.user_time, stage.scoreable)
    return MaskedScorer(net, stage.scoreable, D.n_id_items).to(dev)


def fit_torch(key: str, p: dict, D: DataV2, train_stage: Stage, val_stage: Stage | None, epochs: int, patience: int,
              seed: int, dev):
    """Huấn luyện trên train_stage.train; có val_stage thì dừng sớm theo NDCG@10 của giai đoạn đó (chọn số epoch),
    không có thì chạy đúng `epochs` epoch (huấn luyện lại trước khi đánh giá cuối)."""
    seed_everything(seed)
    net = build_torch(key, p, D, dev)
    if is_feature(key):
        data = FeatureTrainDataset(train_stage.train, D.n_items, D.item_first_day, p["negative_ratio"], seed=seed)
    else:
        data = TrainDataset(train_stage.train, D.n_id_items, train_stage.train_pos, p["negative_ratio"], seed=seed)
    opt = make_optimizer("adam", net.parameters(), p["lr"], p["weight_decay"])
    records = None
    if val_stage is not None:
        records = val_stage.records
        scorer = torch_scorer(key, net, val_stage, D, dev)
        eval_fn = lambda m, r: evaluate_torch_model(scorer, r, k_values=[10], device=dev,  # noqa: E731
                                                    tie_seed=CFG["evaluation"]["tie_break_seed"])
    else:
        eval_fn = None
    net, hist, meta = train_one_model(net, data, records, eval_fn, opt, dev, epochs, patience,
                                      CFG["training"]["batch_size"], "NDCG@10", seed, key)
    return net, hist, meta


def score_fn(key: str, p: dict, D: DataV2, stage: Stage, seed: int = 42):
    """Mô hình không phải mạng nơ-ron, khớp trên tập huấn luyện của giai đoạn."""
    tr = stage.train
    if key == "random":
        return RandomBaseline(seed=seed)
    if key == "popularity":
        return MaskedScoreFn(MostPopularBaseline(tr, D.n_id_items), stage.scoreable, D.n_id_items)
    if key == "recent_pop":
        return RecentPopularity(D.item_cum, stage.cutoff, p["window"])
    if key == "content":
        return ContentProfile(D.item_text, D.item_cats, D.item_cards, tr, D.n_users, stage.cutoff, p["half_life"])
    if key in ("itemknn", "userknn"):
        cls = ItemKNNBaseline if key == "itemknn" else UserKNNBaseline
        return MaskedScoreFn(cls(tr, D.n_users, D.n_id_items, k=p["k"], shrink=p["shrink"]), stage.scoreable,
                             D.n_id_items)
    if key == "bpr":
        m = BPRMFBaseline(D.n_users, D.n_id_items, p["embedding_dim"], seed=seed)
        m.fit(tr, epochs=p["epochs"], lr=p["lr"], reg=p["reg"], seed=seed)
        return MaskedScoreFn(m, stage.scoreable, D.n_id_items)
    raise ValueError(key)


def late_fusion(parts: dict, w: float) -> LateFusion:
    return LateFusion(parts[LATE_PARTS[0]], parts[LATE_PARTS[1]], w)


def evaluate(scorer, stage: Stage, dev, per_user=None, topk=None) -> dict:
    return evaluate_v2(scorer, stage.records, stage.new, device=dev, per_user=per_user, topk=topk, **eval_kw())


__all__ = ["CFG", "AUDIT", "METRICS", "DISPLAY", "GRIDS", "DEFAULTS", "ABLATIONS", "ABLATION_DISPLAY", "TORCH_ID",
           "TORCH_FEAT", "LATE_PARTS", "configs_for", "load_data", "device", "build_torch", "torch_scorer",
           "fit_torch", "score_fn", "late_fusion", "evaluate", "is_feature", "evaluate_score_function"]
