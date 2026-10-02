"""Nạp dữ liệu H&M, tái tạo đúng split và ánh xạ ID khớp với checkpoint của một lần chạy.

Hai chế độ (biến môi trường DEMO_MODE, mặc định tự chọn "final" nếu có checkpoint):

- "final": checkpoint của đánh giá cuối (outputs/final/seed<DEMO_FINAL_SEED, mặc định 42>/) — đúng các mô hình của
  Chương 4: chia theo mốc thời gian chung, mô hình đã huấn luyện lại trên train ∪ val, chấm các sản phẩm đích của tập
  test (một khách có thể có nhiều sản phẩm đích). Số per-user khớp outputs/final/seed42/results_per_user.csv. Có thêm
  các mô hình mở rộng (late fusion, ItemKNN, UserKNN) nếu audit/best_configs.json có tham số của chúng.
- "explore": run khám phá leave-one-out (outputs/experiments/hm500k_seed42, cấu hình mặc định, sản phẩm đích lấy từ
  validation) — hành vi cũ, giữ để đối chiếu.

Chỉ import hàm từ src/ và scripts/, không sửa code huấn luyện.
"""
from __future__ import annotations

import importlib.util
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
from src.baselines import BPRMFBaseline, ItemKNNBaseline, MostPopularBaseline, UserKNNBaseline  # noqa: E402
from src.data_pipeline.negative_sampling import build_user_positive_sets  # noqa: E402
from src.data_pipeline.preprocessing import build_interactions  # noqa: E402
from src.data_pipeline.splitting import (assert_disjoint_splits, global_temporal_split, refit_data,  # noqa: E402
                                         temporal_leave_one_out)
from src.evaluation.long_tail import define_head_items  # noqa: E402
from src.models.late_fusion import LateFusion  # noqa: E402
from src.models.neumf import GMF, MLP, NeuMF  # noqa: E402

CONFIG_PATH = os.environ.get("DEMO_CONFIG", "configs/hm500k.yaml")  # chế độ explore
FINAL_CONFIG = "configs/hm500k_global.yaml"                           # chế độ final (protocol chính)
RUN_PREFIX = f"{Path(CONFIG_PATH).stem}_seed"  # run tag = <tên file config>_seed<seed>
EXPERIMENTS_DIR = PROJECT_ROOT / "outputs" / "experiments"
CHECKPOINTS_DIR = PROJECT_ROOT / "outputs" / "checkpoints"
FINAL_DIR = PROJECT_ROOT / "outputs" / "final"
FINAL_SEED = int(os.environ.get("DEMO_FINAL_SEED", "42"))
BEST_CONFIGS = PROJECT_ROOT / "audit" / "best_configs.json"
ARTICLES_PATH = PROJECT_ROOT / "data" / "raw" / "hm" / "articles.csv"
CUSTOMERS_PATH = PROJECT_ROOT / "data" / "raw" / "hm" / "customers.csv"

NEURAL_CHECKPOINTS = {
    "NeuMF-Pretrained": "neumf_pretrained.pt",
    "NeuMF-Scratch": "neumf_scratch.pt",
    "GMF": "gmf.pt",
    "MLP": "mlp.pt",
    # EarlyFusionModel không đưa vào demo: kiến trúc trùng hệt MLP, không phải mô hình hợp nhất MF + DNN.
}
TUNE_KEYS = {"NeuMF-Pretrained": "neumf_pretrained", "NeuMF-Scratch": "neumf_scratch", "GMF": "gmf", "MLP": "mlp"}
BPR_CHECKPOINT = "bpr.npz"  # mảng P (users x d), Q (items x d)
EXTENSION_MODELS = ["LateFusion-GMF-MLP", "LateFusion-BPR-MLP", "ItemKNN", "UserKNN"]
ARTICLE_COLUMNS = [
    "article_id", "prod_name", "product_type_name", "product_group_name",
    "colour_group_name", "perceived_colour_master_name", "index_group_name", "garment_group_name",
]


def final_available(seed: int = FINAL_SEED) -> bool:
    d = FINAL_DIR / f"seed{seed}"
    need = [*NEURAL_CHECKPOINTS.values(), BPR_CHECKPOINT, "results.json"]
    return all((d / f).exists() for f in need)


def resolve_mode() -> str:
    mode = os.environ.get("DEMO_MODE", "").strip().lower()
    if mode in ("final", "explore"):
        return mode
    return "final" if final_available() else "explore"


def resolve_latest_run_tag(prefix: str = RUN_PREFIX) -> str:
    """Run khám phá mới nhất có results.json và checkpoint .pt (bỏ qua run bị ngắt giữa chừng)."""
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


def resolve_run_tag(mode: str | None = None) -> str:
    mode = mode or resolve_mode()
    if mode == "final":
        return f"final_seed{FINAL_SEED}"
    return os.environ.get("DEMO_RUN_TAG") or resolve_latest_run_tag()


def _build_model(name: str, n_users: int, n_items: int, cfg) -> torch.nn.Module:
    """Chế độ explore: mọi mô hình dùng cấu hình mặc định trong config."""
    d, layers, dropout = cfg.model.embedding_dim, list(cfg.model.mlp_layers), cfg.model.dropout
    if name == "GMF":
        return GMF(n_users, n_items, d)
    if name == "MLP":
        return MLP(n_users, n_items, d, layers, dropout)
    return NeuMF(n_users, n_items, d, layers, dropout)


def _load_tune_module():
    """scripts/10_tune.py (tên bắt đầu bằng số) — dùng đúng build_net của đánh giá cuối."""
    spec = importlib.util.spec_from_file_location("tune", PROJECT_ROOT / "scripts" / "10_tune.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class DataContext:
    def __init__(self, run_tag: str | None = None, load_customers: bool = True, mode: str | None = None):
        self.mode = mode or resolve_mode()
        self.scorers: dict = {}  # mô hình không phải mạng PyTorch: tên -> đối tượng có score_items(user, items)
        self.models: dict[str, torch.nn.Module] = {}
        self.unavailable: dict[str, str] = {}
        if self.mode == "final":
            self._init_final()
        else:
            self._init_explore(run_tag)
        self.target_users = np.array(sorted(self.target_items), dtype=np.int64)
        self.articles = self._load_articles()
        self.user_age = self._load_ages() if load_customers else pd.Series(dtype=float)

    # ------------------------------------------------------------------ chế độ explore (leave-one-out)
    def _init_explore(self, run_tag: str | None) -> None:
        self.run_tag = run_tag or os.environ.get("DEMO_RUN_TAG") or resolve_latest_run_tag()
        self.config_path = CONFIG_PATH
        cfg, adapter = build_adapter(CONFIG_PATH)
        self.cfg = cfg
        self.k_values = [int(k) for k in cfg.evaluation.k_values]
        self.tie_seed = cfg.evaluation.tie_break_seed
        print(f"[demo] chế độ explore: nạp dữ liệu theo {CONFIG_PATH}, run_tag = {self.run_tag}")

        data = build_interactions(adapter.load_events(), cfg.dataset.k_core)
        # Giống scripts/03_run_experiment.py: temporal LOO + kiểm tra không giao nhau.
        train_df, val_df, test_df = temporal_leave_one_out(data.df, cfg.dataset.min_interactions_for_loo)
        assert_disjoint_splits(train_df, val_df, test_df)
        self.data_df, self.train_df, self.val_df, self.test_df = data.df, train_df, val_df, test_df
        self.n_users, self.n_items = data.n_users, data.n_items
        self.run_metadata = self._check_run_metadata()
        self._set_ids(data)

        # Chấm đúng tập mà bảng kết quả của run dùng: 03 không --final chấm validation (khoá test) -> demo cũng
        # chấm item validation và không lộ test. Run cũ (trước khi có khoá test) không ghi evaluated_on -> test.
        # Tập loại trừ đúng như 03: validation loại item train; test loại train ∪ val.
        self.evaluated_on = self.run_metadata.get("evaluated_on", "test")
        self.train_pos = build_user_positive_sets(train_df, self.n_users)
        self.train_val_pos = build_user_positive_sets(pd.concat([train_df, val_df], ignore_index=True), self.n_users)
        target_df, self.seen_pos = (test_df, self.train_val_pos) if self.evaluated_on == "test" else (val_df, self.train_pos)
        self.target_item = dict(zip(target_df["user"].astype(int), target_df["item"].astype(int)))
        self.target_items = {u: [i] for u, i in self.target_item.items()}
        self.val_item = dict(zip(val_df["user"].astype(int), val_df["item"].astype(int)))
        self.pool_mask = np.ones(self.n_items, dtype=bool)  # LOO: ứng viên là mọi item trừ item đã mua
        self.head_items = define_head_items(train_df, self.n_items, cfg.evaluation.head_fraction)
        self.train_item_counts = np.bincount(train_df["item"].to_numpy(), minlength=self.n_items)
        self.train_user_counts = np.bincount(train_df["user"].to_numpy(), minlength=self.n_users)
        self._load_explore_models()
        self.scorers["MostPopular"] = MostPopularBaseline(train_df, self.n_items)

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

    def _load_explore_models(self) -> None:
        ckpt_dir = CHECKPOINTS_DIR / self.run_tag
        for name, fname in NEURAL_CHECKPOINTS.items():
            path = ckpt_dir / fname
            if not path.exists():
                self.unavailable[name] = f"Thiếu checkpoint {path.relative_to(PROJECT_ROOT).as_posix()}"
                continue
            model = _build_model(name, self.n_users, self.n_items, self.cfg)
            model.load_state_dict(torch.load(path, map_location="cpu"))
            self.models[name] = model.eval()
        bpr_path = ckpt_dir / BPR_CHECKPOINT
        if bpr_path.exists():
            self.scorers["BPR-MF"] = BPRMFBaseline.load(bpr_path)
        else:
            self.unavailable["BPR-MF"] = (
                f"Run này chưa có {bpr_path.relative_to(PROJECT_ROOT).as_posix()} (run tạo trước khi 03 lưu "
                f"checkpoint BPR-MF). Chạy lại 03 để có. Demo không tự train lại."
            )

    # ------------------------------------------------------------------ chế độ final (đánh giá cuối)
    def _init_final(self) -> None:
        self.run_tag = f"final_seed{FINAL_SEED}"
        self.config_path = FINAL_CONFIG
        seed_dir = FINAL_DIR / f"seed{FINAL_SEED}"
        results = json.loads((seed_dir / "results.json").read_text(encoding="utf-8"))
        cfg, adapter = build_adapter(FINAL_CONFIG)
        self.cfg = cfg
        self.k_values = [int(k) for k in cfg.evaluation.k_values]
        self.tie_seed = cfg.evaluation.tie_break_seed
        print(f"[demo] chế độ final: checkpoint {seed_dir.relative_to(PROJECT_ROOT).as_posix()} "
              f"(commit {str(results['provenance'].get('git_commit'))[:7]})")

        data = build_interactions(adapter.load_events(), cfg.dataset.k_core)
        tr, va, te = global_temporal_split(data.df, cfg.dataset.val_start, cfg.dataset.test_start)
        assert_disjoint_splits(tr, va, te)
        trva = refit_data(data.df, cfg.dataset.test_start)  # dữ liệu mô hình cuối đã học (train ∪ val)
        self.data_df, self.val_df, self.test_df = data.df, va, te
        self.n_users, self.n_items = data.n_users, data.n_items
        self._set_ids(data)

        self.evaluated_on = "test"
        self.seen_pos = self.train_pos = build_user_positive_sets(trva, self.n_users)
        pool = np.unique(trva["item"].to_numpy())
        self.pool_mask = np.zeros(self.n_items, dtype=bool)
        self.pool_mask[pool] = True
        self.target_items = {int(u): sorted(int(i) for i in g["item"]) for u, g in te.groupby("user")}
        self.target_item = {u: items[0] for u, items in self.target_items.items()}
        self.val_item = {}
        if (len(self.target_items), len(pool)) != (results["n_test_users"], results["n_candidate_items"]):
            raise ValueError(f"Dữ liệu tái tạo ({len(self.target_items)} user test, {len(pool)} item) không khớp "
                             f"{seed_dir.name}/results.json ({results['n_test_users']}, {results['n_candidate_items']}).")
        # Lịch sử hiển thị = đúng dữ liệu mô hình đã học. Ngày hiển thị là ngày mua ĐẦU (luôn trước mốc test);
        # ngày mua cuối và số lần mua có thể gồm lượt mua lặp trong giai đoạn test nên không hiển thị.
        self.train_df = trva.assign(last_timestamp=trva["first_timestamp"], interaction_count=1)
        self.head_items = define_head_items(trva, self.n_items, cfg.evaluation.head_fraction)
        self.train_item_counts = np.bincount(trva["item"].to_numpy(), minlength=self.n_items)
        self.train_user_counts = np.bincount(trva["user"].to_numpy(), minlength=self.n_users)
        self.run_metadata = {"evaluated_on": "test", "provenance": results["provenance"],
                             "n_test_users": results["n_test_users"], "n_candidate_items": results["n_candidate_items"],
                             "train": len(tr), "validation": len(va), "test": len(te), "train_val": len(trva)}

        tune = _load_tune_module()
        D = type("D", (), {"n_users": self.n_users, "n_items": self.n_items})
        for name, fname in NEURAL_CHECKPOINTS.items():
            net = tune.build_net(TUNE_KEYS[name], results["configs"][name], D)
            net.load_state_dict(torch.load(seed_dir / fname, map_location="cpu"))
            self.models[name] = net.eval()
        self.scorers["MostPopular"] = MostPopularBaseline(trva, self.n_items)
        self.scorers["BPR-MF"] = BPRMFBaseline.load(seed_dir / BPR_CHECKPOINT)
        self._load_extension(trva)

    def _load_extension(self, trva: pd.DataFrame) -> None:
        """Mô hình mở rộng (PREREG mục 9) với tham số chọn trên val — như scripts/17_extension.py."""
        best = json.loads(BEST_CONFIGS.read_text(encoding="utf-8")) if BEST_CONFIGS.exists() else {}
        missing = [k for k in ("itemknn", "userknn", "late_gmf_mlp", "late_bpr_mlp") if k not in best]
        if missing:
            for m in EXTENSION_MODELS:
                self.unavailable[m] = f"audit/best_configs.json chưa có tham số mở rộng {missing}"
            return
        knn = {"ItemKNN": (ItemKNNBaseline, best["itemknn"]["params"]),
               "UserKNN": (UserKNNBaseline, best["userknn"]["params"])}
        for name, (cls, p) in knn.items():
            self.scorers[name] = cls(trva, self.n_users, self.n_items, k=p["k"], shrink=p["shrink"])
        self.scorers["LateFusion-GMF-MLP"] = LateFusion(self.models["GMF"], self.models["MLP"],
                                                        best["late_gmf_mlp"]["params"]["w"])
        self.scorers["LateFusion-BPR-MLP"] = LateFusion(self.scorers["BPR-MF"], self.models["MLP"],
                                                        best["late_bpr_mlp"]["params"]["w"])
        self.extension_params = {m: p for m, p in (
            ("ItemKNN", best["itemknn"]["params"]), ("UserKNN", best["userknn"]["params"]),
            ("LateFusion-GMF-MLP", best["late_gmf_mlp"]["params"]),
            ("LateFusion-BPR-MLP", best["late_bpr_mlp"]["params"]))}

    # ------------------------------------------------------------------ chung
    def _set_ids(self, data) -> None:
        self.customer_ids = np.empty(self.n_users, dtype=object)
        for customer_id, idx in data.user2idx.items():
            self.customer_ids[idx] = str(customer_id)
        self.user2idx = {cid: int(i) for i, cid in enumerate(self.customer_ids)}
        self.article_ids = np.empty(self.n_items, dtype=object)
        for article_id, idx in data.item2idx.items():
            self.article_ids[idx] = str(article_id)

    def _load_articles(self) -> pd.DataFrame:
        if not ARTICLES_PATH.exists():
            raise FileNotFoundError(f"Thiếu {ARTICLES_PATH} — chép articles.csv (và customers.csv) của bộ H&M "
                                    "vào data/raw/hm/ cạnh transactions_train.csv (demo/README.md mục 1).")
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

    # ------------------------------------------------------------- accessors
    @property
    def available_models(self) -> list[str]:
        out = [m for m in NEURAL_CHECKPOINTS if m in self.models]
        out += [m for m in ("BPR-MF", "MostPopular") if m in self.scorers]
        return out + [m for m in EXTENSION_MODELS if m in self.scorers]

    @property
    def bpr(self):
        return self.scorers.get("BPR-MF")

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
        """Chỉ item mô hình đã học (train; ở chế độ final là train ∪ val), sắp theo thời gian mua."""
        rows = self.train_df[self.train_df["user"] == u].sort_values(["last_timestamp", "last_source_order"])
        return [
            {**self.item_info(r.item), "t_dat": r.last_timestamp.date().isoformat(),
             "interaction_count": int(r.interaction_count)}
            for r in rows.itertuples(index=False)
        ]

    def neighbors(self, u: int, top: int = 10) -> list[dict] | None:
        """Top-K khách tương đồng nhất theo UserKNN (cosine trên lịch sử mua) — None nếu không có UserKNN."""
        knn = self.scorers.get("UserKNN")
        if knn is None:
            return None
        mine = self.train_pos[u]
        targets = set(self.target_items.get(u, []))
        out = []
        for nb in knn.neighbors(u, top):
            v = nb["user"]
            theirs = self.train_pos[v]
            out.append({
                "customer_id": self.customer_ids[v], "similarity": nb["similarity"], "n_common": nb["n_common"],
                "train_count": int(self.train_user_counts[v]),
                "common_items": [self.item_info(i) for i in sorted(mine & theirs,
                                                                   key=lambda i: -self.train_item_counts[i])[:3]],
                "bought_target": [self.item_info(i) for i in sorted(theirs & targets)],
            })
        return out

    def summary(self) -> dict:
        ds = self.cfg.dataset
        out = {
            "dataset": "H&M Personalized Fashion Recommendations",
            "mode": self.mode,
            "config": self.config_path,
            "nrows": ds.nrows,
            "k_core": ds.k_core,
            "date_min": self.data_df["last_timestamp"].min().date().isoformat(),
            "date_max": self.data_df["last_timestamp"].max().date().isoformat(),
            "run_tag": self.run_tag,
            "evaluated_on": self.evaluated_on,
            "n_users": self.n_users,
            "n_items": self.n_items,
            "n_interactions": int(len(self.data_df)),
            "k_values": self.k_values,
            "models": self.available_models,
            "extension_models": [m for m in EXTENSION_MODELS if m in self.scorers],
            "unavailable_models": self.unavailable,
            "has_neighbors": "UserKNN" in self.scorers,
        }
        if self.mode == "final":
            out.update(val_start=ds.val_start, test_start=ds.test_start,
                       commit=str(self.run_metadata["provenance"].get("git_commit") or "")[:7],
                       n_candidates=int(self.pool_mask.sum()))
        return out
