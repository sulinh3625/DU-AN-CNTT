"""Nạp dữ liệu H&M, tái tạo đúng split và ánh xạ ID khớp với checkpoint của một run.

Chỉ import hàm từ src/ và scripts/common.py, không sửa code huấn luyện.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEMO_ROOT = PROJECT_ROOT / "demo"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.common import build_adapter  # noqa: E402
from src.data_pipeline.negative_sampling import build_user_positive_sets  # noqa: E402
from src.data_pipeline.preprocessing import build_interactions  # noqa: E402
from src.data_pipeline.splitting import assert_disjoint_splits, temporal_leave_one_out  # noqa: E402
from src.evaluation.long_tail import define_head_items  # noqa: E402
from src.models.early_fusion import EarlyFusionModel  # noqa: E402
from src.models.neumf import GMF, MLP, NeuMF  # noqa: E402

CONFIG_PATH = os.environ.get("DEMO_CONFIG", "configs/hm_subset.yaml")
RUN_PREFIX = "hm_"
EXPERIMENTS_DIR = PROJECT_ROOT / "outputs" / "experiments"
CHECKPOINTS_DIR = PROJECT_ROOT / "outputs" / "checkpoints"
ARTICLES_PATH = PROJECT_ROOT / "data" / "raw" / "hm" / "articles.csv"
CUSTOMERS_PATH = PROJECT_ROOT / "data" / "raw" / "hm" / "customers.csv"

NEURAL_CHECKPOINTS = {
    "NeuMF-Pretrained": "neumf_pretrained.pt",
    "NeuMF-Scratch": "neumf_scratch.pt",
    "GMF": "gmf.pt",
    "MLP": "mlp.pt",
    "EarlyFusion": "early_fusion.pt",
}
BPR_CHECKPOINT = "bpr.npz"  # mảng P (users x d), Q (items x d)
MODEL_ORDER = [*NEURAL_CHECKPOINTS, "MostPopular", "BPR-MF"]
ARTICLE_COLUMNS = [
    "article_id", "prod_name", "product_type_name", "product_group_name",
    "colour_group_name", "perceived_colour_master_name", "index_group_name", "garment_group_name",
]


def resolve_latest_run_tag(prefix: str = RUN_PREFIX) -> str:
    """Run mới nhất có results.json và checkpoint .pt (bỏ qua run bị ngắt giữa chừng)."""
    candidates = []
    if EXPERIMENTS_DIR.exists():
        for d in EXPERIMENTS_DIR.iterdir():
            if not d.is_dir() or not d.name.startswith(prefix):
                continue
            results_path = d / "results.json"
            ckpt = CHECKPOINTS_DIR / d.name
            if results_path.exists() and ckpt.exists() and any(ckpt.glob("*.pt")):
                candidates.append((results_path.stat().st_mtime, d.name))
    if not candidates:
        raise FileNotFoundError(
            f"Không có run nào hoàn chỉnh với tiền tố '{prefix}' trong outputs/experiments/. "
            f"Chạy scripts/run_all.py cho H&M trước."
        )
    return max(candidates)[1]


def _build_model(name: str, n_users: int, n_items: int, cfg) -> torch.nn.Module:
    d, layers, dropout = cfg.model.embedding_dim, list(cfg.model.mlp_layers), cfg.model.dropout
    if name == "GMF":
        return GMF(n_users, n_items, d)
    if name == "MLP":
        return MLP(n_users, n_items, d, layers, dropout)
    if name == "EarlyFusion":
        return EarlyFusionModel(n_users, n_items, d, layers, dropout)
    return NeuMF(n_users, n_items, d, layers, dropout)


class DataContext:
    def __init__(self, run_tag: str | None = None, load_customers: bool = True):
        self.run_tag = run_tag or os.environ.get("DEMO_RUN_TAG") or resolve_latest_run_tag()
        self.config_path = CONFIG_PATH
        cfg, adapter = build_adapter(CONFIG_PATH)
        self.cfg = cfg
        self.k_values = [int(k) for k in cfg.evaluation.k_values]
        self.tie_seed = cfg.evaluation.tie_break_seed
        print(f"[demo] Nạp dữ liệu theo {CONFIG_PATH}, run_tag = {self.run_tag}")

        data = build_interactions(adapter.load_events(), cfg.dataset.k_core)
        # Giống scripts/03_run_experiment.py: temporal LOO + kiểm tra không giao nhau.
        train_df, val_df, test_df = temporal_leave_one_out(data.df, cfg.dataset.min_interactions_for_loo)
        assert_disjoint_splits(train_df, val_df, test_df)
        self.data_df, self.train_df, self.val_df, self.test_df = data.df, train_df, val_df, test_df
        self.n_users, self.n_items = data.n_users, data.n_items
        self.run_metadata = self._check_run_metadata()

        self.customer_ids = np.empty(self.n_users, dtype=object)
        for customer_id, idx in data.user2idx.items():
            self.customer_ids[idx] = str(customer_id)
        self.user2idx = {cid: int(i) for i, cid in enumerate(self.customer_ids)}
        self.article_ids = np.empty(self.n_items, dtype=object)
        for article_id, idx in data.item2idx.items():
            self.article_ids[idx] = str(article_id)

        # Tập loại trừ đúng như src/evaluation/full_ranking.py (test dùng train ∪ val).
        self.train_pos = build_user_positive_sets(train_df, self.n_users)
        self.train_val_pos = build_user_positive_sets(pd.concat([train_df, val_df], ignore_index=True), self.n_users)
        self.test_item = dict(zip(test_df["user"].astype(int), test_df["item"].astype(int)))
        self.val_item = dict(zip(val_df["user"].astype(int), val_df["item"].astype(int)))
        self.head_items = define_head_items(train_df, self.n_items, cfg.evaluation.head_fraction)
        self.train_item_counts = np.bincount(train_df["item"].to_numpy(), minlength=self.n_items)
        self.train_user_counts = np.bincount(train_df["user"].to_numpy(), minlength=self.n_users)
        self.test_users = np.array(sorted(self.test_item), dtype=np.int64)

        self.articles = self._load_articles()
        self.user_age = self._load_ages() if load_customers else pd.Series(dtype=float)
        self.models, self.bpr, self.unavailable = self._load_models()

    # ------------------------------------------------------------------ setup
    def _check_run_metadata(self) -> dict:
        """Dữ liệu tái tạo phải khớp đúng run đã train, nếu không thì ID lệch checkpoint."""
        path = EXPERIMENTS_DIR / self.run_tag / "metadata.json"
        meta = json.loads(path.read_text(encoding="utf-8"))
        expected = {
            "n_users": self.n_users, "n_items": self.n_items, "n_interactions": len(self.data_df),
            "train": len(self.train_df), "validation": len(self.val_df), "test": len(self.test_df),
        }
        diff = {k: (meta.get(k), v) for k, v in expected.items() if meta.get(k) != v}
        if diff:
            raise ValueError(
                f"Dữ liệu tái tạo từ {CONFIG_PATH} không khớp run '{self.run_tag}' "
                f"(metadata, tái tạo): {diff}. Kiểm tra lại config (nrows, k_core) hoặc đặt DEMO_RUN_TAG/DEMO_CONFIG."
            )
        return meta

    def _load_articles(self) -> pd.DataFrame:
        arts = pd.read_csv(ARTICLES_PATH, dtype={"article_id": "string"}, usecols=ARTICLE_COLUMNS)
        arts["article_id"] = arts["article_id"].str.zfill(10)
        arts = arts.drop_duplicates("article_id").set_index("article_id")
        out = arts.reindex(self.article_ids).reset_index()
        out.index.name = "item"
        return out.fillna("Unknown")

    def _load_ages(self) -> pd.Series:
        """Tuổi theo user idx (chỉ user có trong dữ liệu); thiếu file thì trả rỗng."""
        if not CUSTOMERS_PATH.exists():
            return pd.Series(dtype=float)
        with CUSTOMERS_PATH.open(encoding="utf-8") as f:
            first = f.readline()
        # Bản customers.csv trong repo có thêm dòng "Column1;..." phía trên header và phân cách bằng ';'.
        sep = ";" if ";" in first else ","
        skip = 1 if first.startswith("Column1") else 0
        cust = pd.read_csv(CUSTOMERS_PATH, sep=sep, skiprows=skip, usecols=["customer_id", "age"])
        cust = cust.dropna(subset=["age"])
        cust = cust[cust["customer_id"].isin(self.user2idx)]
        return pd.Series(cust["age"].to_numpy(dtype=float), index=cust["customer_id"].map(self.user2idx).to_numpy())

    def _load_models(self):
        ckpt_dir = CHECKPOINTS_DIR / self.run_tag
        models, unavailable = {}, {}
        for name, fname in NEURAL_CHECKPOINTS.items():
            path = ckpt_dir / fname
            if not path.exists():
                unavailable[name] = f"Thiếu checkpoint {path.relative_to(PROJECT_ROOT).as_posix()}"
                continue
            model = _build_model(name, self.n_users, self.n_items, self.cfg)
            model.load_state_dict(torch.load(path, map_location="cpu"))
            models[name] = model.eval()
        bpr = None
        bpr_path = ckpt_dir / BPR_CHECKPOINT
        if bpr_path.exists():
            npz = np.load(bpr_path)
            bpr = (npz["P"], npz["Q"])
        else:
            unavailable["BPR-MF"] = (
                f"Chưa có checkpoint {bpr_path.relative_to(PROJECT_ROOT).as_posix()}: scripts/03_run_experiment.py "
                f"hiện không lưu trạng thái BPR-MF. Demo không tự train lại."
            )
        return models, bpr, unavailable

    # ------------------------------------------------------------- accessors
    @property
    def available_models(self) -> list[str]:
        out = [m for m in NEURAL_CHECKPOINTS if m in self.models] + ["MostPopular"]
        return out + (["BPR-MF"] if self.bpr is not None else [])

    def resolve_user(self, customer_id: str) -> int:
        idx = self.user2idx.get(customer_id.strip())
        if idx is None:
            raise KeyError(customer_id)
        return idx

    def item_info(self, item: int) -> dict:
        a = self.articles.iloc[int(item)]
        return {
            "item_idx": int(item),
            "article_id": a["article_id"],
            "prod_name": a["prod_name"],
            "product_type_name": a["product_type_name"],
            "product_group_name": a["product_group_name"],
            "colour_group_name": a["colour_group_name"],
            "index_group_name": a["index_group_name"],
            "is_head": int(item) in self.head_items,
            "train_count": int(self.train_item_counts[int(item)]),
        }

    def history(self, u: int) -> list[dict]:
        """Chỉ item trong TRAIN, sắp theo thời gian mua (last_timestamp của cặp user-item)."""
        rows = self.train_df[self.train_df["user"] == u].sort_values(["last_timestamp", "last_source_order"])
        return [
            {**self.item_info(r.item), "t_dat": r.last_timestamp.date().isoformat(),
             "interaction_count": int(r.interaction_count)}
            for r in rows.itertuples(index=False)
        ]

    def summary(self) -> dict:
        ds = self.cfg.dataset
        return {
            "dataset": "H&M Personalized Fashion Recommendations",
            "config": self.config_path,
            "nrows": ds.nrows,
            "k_core": ds.k_core,
            "date_min": self.data_df["last_timestamp"].min().date().isoformat(),
            "date_max": self.data_df["last_timestamp"].max().date().isoformat(),
            "run_tag": self.run_tag,
            "n_users": self.n_users,
            "n_items": self.n_items,
            "n_interactions": int(len(self.data_df)),
            "k_values": self.k_values,
            "models": self.available_models,
            "unavailable_models": self.unavailable,
        }
