"""Tuning CHỈ trên validation theo audit/PREREG.md mục 4 (script nhẹ, không dựng test records).

    python scripts/10_tune.py --model all          # 5 mô hình chính: bpr | gmf | mlp | neumf_scratch | neumf_pretrained
    python scripts/10_tune.py --model extension    # mở rộng (PREREG mục 9): itemknn | userknn | late_gmf_mlp | late_bpr_mlp

Mỗi cấu hình ghi 1 dòng vào audit/tuning_log.csv (config hash, git commit, val metrics, thời gian).
Cấu hình tốt nhất theo val NDCG@10 ghi vào audit/best_configs.json; checkpoint ở outputs/tuning/.
Late fusion cần GMF, MLP, BPR-MF tốt nhất đã huấn luyện trên train: nếu checkpoint không còn, script huấn luyện lại
đúng cấu hình đó (seed 42) và ghi số val của bản dựng lại vào audit/rebuilt_checkpoints.json để đối chiếu.
"""
from __future__ import annotations

import os

os.environ.setdefault("TQDM_DISABLE", "1")  # log nền gọn; phải đặt trước khi import tqdm

import argparse
import copy
import csv
import hashlib
import itertools
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.common import build_adapter
from src.baselines import BPRMFBaseline, ItemKNNBaseline, UserKNNBaseline
from src.data_pipeline.dataset import TrainDataset
from src.data_pipeline.negative_sampling import build_user_positive_sets
from src.data_pipeline.preprocessing import apply_feedback_weights, build_interactions
from src.data_pipeline.splitting import assert_disjoint_splits, global_temporal_split, refit_data
from src.evaluation.full_ranking import build_full_ranking_records_multi, evaluate_score_function, evaluate_torch_model
from src.models.late_fusion import CachedLateFusion, fusion_cache
from src.models.neumf import GMF, MLP, NeuMF
from src.training.trainer import get_device, make_optimizer, train_one_model
from src.utils.io import ensure_dir, run_provenance
from src.utils.seed import seed_everything

AUDIT_DIR = PROJECT_ROOT / "audit"
SEED, GRID_SEED, MAX_EPOCHS, PATIENCE = 42, 0, 20, 5
METRICS = ["NDCG@10", "Recall@10", "HR@10", "Precision@10", "NDCG@5"]

NEURAL = dict(lr=[1e-3, 5e-4], negative_ratio=[4, 8], embedding_dim=[32, 64], weight_decay=[0.0, 1e-6],
              dropout=[0.0, 0.2])
GRIDS = {
    "bpr": dict(embedding_dim=[32, 64, 128], lr=[0.01, 0.03, 0.05], reg=[0.001, 0.005, 0.01], epochs=[20, 40]),
    "gmf": {k: v for k, v in NEURAL.items() if k != "dropout"},
    "mlp": NEURAL,
    "neumf_scratch": NEURAL,
    "neumf_pretrained": dict(lr=[1e-3, 5e-4, 1e-4], alpha=[0.3, 0.5, 0.7]),
}
ORDER = list(GRIDS)  # 5 mô hình chính, thứ tự chạy: neumf_pretrained cần gmf+mlp
TORCH_MODELS = {"gmf", "mlp", "neumf_scratch", "neumf_pretrained"}
# EarlyFusionModel không tune: kiến trúc trùng hệt MLP. iALS, MostPopular-Recent, CFNet, trộn điểm iALS + NeuMF
# đã gỡ theo quyết định người dùng (loop 14) — xem PREREG mục 8.

# Mở rộng sau khi xem test (PREREG mục 9): baseline láng giềng và late fusion MF + DNN.
W_GRID = [round(0.1 * i, 1) for i in range(11)]
GRIDS.update({
    "itemknn": dict(k=[20, 50, 100, 200, 500], shrink=[0.0, 10.0, 50.0]),
    "userknn": dict(k=[20, 50, 100, 200, 500], shrink=[0.0, 10.0, 50.0]),
    "late_gmf_mlp": dict(w=W_GRID),   # w·minmax(GMF) + (1−w)·minmax(MLP)
    "late_bpr_mlp": dict(w=W_GRID),   # w·minmax(BPR-MF) + (1−w)·minmax(MLP)
})
EXTENSION = ["itemknn", "userknn", "late_gmf_mlp", "late_bpr_mlp"]
FUSION_PARTS = {"late_gmf_mlp": ("gmf", "mlp"), "late_bpr_mlp": ("bpr", "mlp")}


def default_config(model: str, cfg) -> dict:
    """Cấu hình mặc định hiện tại (configs/hm500k_global.yaml) — PREREG: luôn là 1 trong các cấu hình thử."""
    t, m, b = cfg.training, cfg.model, cfg.baselines
    neural = dict(lr=t.finetune_lr if model == "neumf_scratch" else t.pretrain_lr, negative_ratio=t.negative_ratio,
                  embedding_dim=m.embedding_dim, weight_decay=t.weight_decay, dropout=m.dropout)
    return {
        "bpr": dict(embedding_dim=b.bpr.embedding_dim, lr=b.bpr.lr, reg=b.bpr.reg, epochs=b.bpr.epochs),
        "gmf": {k: v for k, v in neural.items() if k != "dropout"},
        "neumf_pretrained": dict(lr=t.finetune_lr, alpha=m.pretrain_alpha),
        "itemknn": dict(k=100, shrink=0.0),
        "userknn": dict(k=100, shrink=0.0),
        "late_gmf_mlp": dict(w=0.5),
        "late_bpr_mlp": dict(w=0.5),
    }.get(model, neural)


def sample_configs(grid: dict, default: dict, n: int, seed: int = GRID_SEED) -> list[dict]:
    """default + (n-1) cấu hình rút không lặp từ lưới bằng numpy seed cố định (lưới nhỏ hơn n -> lấy hết)."""
    combos = [dict(zip(grid, vals)) for vals in itertools.product(*grid.values())]
    if default not in combos:
        raise ValueError(f"Cấu hình mặc định {default} không nằm trong lưới")
    others = [c for c in combos if c != default]
    pick = np.random.default_rng(seed).choice(len(others), size=min(n - 1, len(others)), replace=False)
    return [default] + [others[i] for i in sorted(pick)]


def mlp_layers(d: int) -> list[int]:
    return [2 * d, d, d // 2, d // 4]


def build_net(model: str, p: dict, D):
    d = p["embedding_dim"]
    if model == "gmf":
        return GMF(D.n_users, D.n_items, d)
    if model == "mlp":
        return MLP(D.n_users, D.n_items, d, mlp_layers(d), p["dropout"])
    if model in ("neumf_scratch", "neumf_pretrained"):
        return NeuMF(D.n_users, D.n_items, d, mlp_layers(d), p["dropout"], gmf_dim=p.get("gmf_dim"))
    raise ValueError(model)


def load_data(config_path: str, with_test: bool = False):
    cfg, adapter = build_adapter(config_path)
    if cfg.dataset.split != "global":
        raise SystemExit("PREREG: tuning trên protocol chính (split: global).")
    data = build_interactions(adapter.load_events(), cfg.dataset.k_core)
    tr, va, te = global_temporal_split(data.df, cfg.dataset.val_start, cfg.dataset.test_start)
    assert_disjoint_splits(tr, va, te)
    tr, va, _, _ = apply_feedback_weights(tr, va, te, cfg.feedback.mode, cfg.feedback.confidence_alpha)
    train_pos = build_user_positive_sets(tr, data.n_users)
    pool = np.unique(tr["item"].to_numpy())
    val = build_full_ranking_records_multi(va, data.n_items, train_pos, pool)
    D = SimpleNamespace(tr=tr, n_users=data.n_users, n_items=data.n_items, train_pos=train_pos, val=val, pool=pool)
    if with_test:  # chỉ scripts/11_final.py, 14_secondary.py (đã qua khoá test); tuning không bao giờ dựng test records
        # Chấm test sau khi train lại trên train ∪ val: pool, item đã mua và thống kê đều lấy từ trva.
        trva, _, _, _ = apply_feedback_weights(refit_data(data.df, cfg.dataset.test_start), va, te,
                                               cfg.feedback.mode, cfg.feedback.confidence_alpha)
        D.trva, D.trva_pos = trva, build_user_positive_sets(trva, data.n_users)
        D.test_pool = np.unique(trva["item"].to_numpy())
        D.test = build_full_ranking_records_multi(te, data.n_items, D.trva_pos, D.test_pool)
        D.va, D.te = va, te
    return cfg, D


class Tuner:
    def __init__(self, config_path: str, log_dir: Path, ckpt_dir: Path):
        self.cfg, self.D = load_data(config_path)
        self.prov = run_provenance(self.cfg, config_path, cwd=PROJECT_ROOT)
        self.device = get_device(self.cfg.training.device)
        self.kw = dict(k_values=self.cfg.evaluation.k_values, tie_seed=self.cfg.evaluation.tie_break_seed,
                       include_redundant=True)
        log_dir = ensure_dir(log_dir)
        self.log_path, self.best_path = log_dir / "tuning_log.csv", log_dir / "best_configs.json"
        self.ckpt_dir = ensure_dir(ckpt_dir)
        print(f"users {self.D.n_users} items {self.D.n_items} train {len(self.D.tr)} val users {len(self.D.val)} | "
              f"commit {self.prov['git_commit']} dirty={self.prov['git_dirty']}", flush=True)

    # ---------- đánh giá (chỉ val)
    def eval_torch(self, net, records):
        return evaluate_torch_model(net, records, device=self.device, **self.kw)

    def eval_scores(self, fn):
        return evaluate_score_function(fn, self.D.val, **self.kw)

    def best(self) -> dict:
        return json.loads(self.best_path.read_text(encoding="utf-8")) if self.best_path.exists() else {}

    def load_net(self, model: str):
        entry = self.best()[model]
        self.ensure_checkpoint(model)
        net = build_net(model, entry["params"], self.D)
        net.load_state_dict(torch.load(PROJECT_ROOT / entry["checkpoint"], map_location="cpu"))
        return net.to(self.device).eval()

    def ensure_checkpoint(self, model: str) -> None:
        """Checkpoint tốt nhất (train-only) đã mất -> huấn luyện lại đúng cấu hình đó, ghi số val để đối chiếu."""
        entry = self.best()[model]
        path = PROJECT_ROOT / entry["checkpoint"]
        if path.exists():
            return
        t0 = time.perf_counter()
        if model in TORCH_MODELS:
            metrics, best_epoch, state = self.fit_torch(model, entry["params"])
            path.parent.mkdir(parents=True, exist_ok=True)
            torch.save(state, path)
        else:
            metrics, best_epoch, art = self.fit_other(model, entry["params"])
            path.parent.mkdir(parents=True, exist_ok=True)
            art.save(path)
        note_path = self.best_path.parent / "rebuilt_checkpoints.json"
        notes = json.loads(note_path.read_text(encoding="utf-8")) if note_path.exists() else {}
        notes[model] = dict(params=entry["params"], checkpoint=entry["checkpoint"],
                            recorded_val_ndcg10=entry["val"]["NDCG@10"], rebuilt_val_ndcg10=metrics["NDCG@10"],
                            best_epoch=best_epoch, time_s=round(time.perf_counter() - t0, 1),
                            git_commit=self.prov["git_commit"], git_dirty=self.prov["git_dirty"],
                            timestamp=datetime.now().isoformat(timespec="seconds"))
        note_path.write_text(json.dumps(notes, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"   dựng lại checkpoint {model}: val NDCG@10 {metrics['NDCG@10']:.5f} "
              f"(ghi nhận lúc tuning {entry['val']['NDCG@10']:.5f})", flush=True)

    def component(self, model: str):
        """Mô hình thành phần (train-only, cấu hình tốt nhất) cho late fusion."""
        if model in TORCH_MODELS:
            return self.load_net(model)
        self.ensure_checkpoint(model)
        return BPRMFBaseline.load(PROJECT_ROOT / self.best()[model]["checkpoint"])

    def fusion_scores(self, model: str) -> dict:
        if not hasattr(self, "_fusion"):
            self._fusion = {}
        if model not in self._fusion:
            a, b = (self.component(m) for m in FUSION_PARTS[model])
            self._fusion[model] = fusion_cache(a, b, self.D.val)
        return self._fusion[model]

    # ---------- huấn luyện 1 cấu hình -> (metrics, best_epoch, artefact để lưu)
    def fit_torch(self, model, p):
        seed_everything(SEED)
        net = build_net(model, p, self.D)
        if model == "neumf_pretrained":
            net.load_pretrained(self.load_net("gmf").cpu(), self.load_net("mlp").cpu(), alpha=p["alpha"])
        net = net.to(self.device)
        ds = TrainDataset(self.D.tr, self.D.n_items, self.D.train_pos, p["negative_ratio"], seed=SEED)
        opt = make_optimizer("adam", net.parameters(), p["lr"], p["weight_decay"])
        net, _, meta = train_one_model(net, ds, self.D.val, self.eval_torch, opt, self.device, MAX_EPOCHS, PATIENCE,
                                       self.cfg.training.batch_size, "NDCG@10", SEED, model)
        return self.eval_torch(net, self.D.val), meta["best_epoch"], copy.deepcopy(net.cpu().state_dict())

    def fit_other(self, model, p):
        D = self.D
        if model == "bpr":
            m = BPRMFBaseline(D.n_users, D.n_items, p["embedding_dim"], seed=SEED)
            m.fit(D.tr, epochs=p["epochs"], lr=p["lr"], reg=p["reg"], seed=SEED)
            return self.eval_scores(m), None, m
        if model in ("itemknn", "userknn"):
            cls = ItemKNNBaseline if model == "itemknn" else UserKNNBaseline
            m = cls(D.tr, D.n_users, D.n_items, k=p["k"], shrink=p["shrink"])
            return self.eval_scores(m), None, None  # tất định, dựng lại nhanh -> không lưu checkpoint
        if model in FUSION_PARTS:
            return self.eval_scores(CachedLateFusion(self.fusion_scores(model), p["w"])), None, None
        raise ValueError(model)

    # ---------- vòng tuning 1 mô hình
    def tune(self, model: str, n_configs: int):
        fixed = {}
        if model == "neumf_pretrained":  # nhánh GMF/MLP lấy từ pretrain tốt nhất; negative/wd theo MLP tốt nhất
            g, m = self.best()["gmf"]["params"], self.best()["mlp"]["params"]
            fixed = dict(embedding_dim=m["embedding_dim"], gmf_dim=g["embedding_dim"], dropout=m["dropout"],
                         negative_ratio=m["negative_ratio"], weight_decay=m["weight_decay"])
        # Late fusion chỉ có một tham số w: thử đủ 11 giá trị của lưới (như mô hình trộn điểm cũ, PREREG mục 4).
        n = len(GRIDS[model]["w"]) if model in FUSION_PARTS else n_configs
        configs = sample_configs(GRIDS[model], default_config(model, self.cfg), n)
        best_row, best_art = None, None
        for cid, p in enumerate(configs):
            p = {**fixed, **p}
            t0 = time.perf_counter()
            fit = self.fit_torch if model in TORCH_MODELS else self.fit_other
            metrics, best_epoch, art = fit(model, p)
            row = self._log(model, cid, p, metrics, best_epoch, time.perf_counter() - t0)
            print(f"[{model} {cid + 1}/{len(configs)}] {json.dumps(p)} -> val NDCG@10 {metrics['NDCG@10']:.5f} "
                  f"({row['time_s']:.0f}s)", flush=True)
            if best_row is None or metrics["NDCG@10"] > best_row["val"]["NDCG@10"]:
                best_row, best_art = dict(params=p, val={k: metrics[k] for k in METRICS},
                                          config_hash=row["config_hash"]), art
        best_row["checkpoint"] = self._save(model, best_art)
        best = self.best()
        best[model] = best_row
        self.best_path.write_text(json.dumps(best, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"==> {model} tốt nhất: {best_row['params']} val NDCG@10 {best_row['val']['NDCG@10']:.5f}", flush=True)

    def _save(self, model, art):
        if art is None:
            return None
        if isinstance(art, dict):
            path = self.ckpt_dir / f"{model}_best.pt"
            torch.save(art, path)
        else:
            path = self.ckpt_dir / f"{model}_best.npz"
            art.save(path)
        return (path.relative_to(PROJECT_ROOT) if path.is_relative_to(PROJECT_ROOT) else path).as_posix()

    def _log(self, model, cid, p, metrics, best_epoch, secs) -> dict:
        blob = json.dumps(dict(model=model, params=p, base=self.prov["config_hash"], seed=SEED), sort_keys=True)
        row = dict(timestamp=datetime.now().isoformat(timespec="seconds"), model=model, config_id=cid,
                   params=json.dumps(p, sort_keys=True), config_hash=hashlib.sha256(blob.encode()).hexdigest()[:16],
                   base_config_hash=self.prov["config_hash"], git_commit=self.prov["git_commit"],
                   git_dirty=self.prov["git_dirty"], seed=SEED, best_epoch=best_epoch, time_s=round(secs, 1),
                   **{f"val_{k}": round(metrics[k], 6) for k in METRICS})
        new = not self.log_path.exists()
        with self.log_path.open("a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(row))
            if new:
                w.writeheader()
            w.writerow(row)
        return row


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default="configs/hm500k_global.yaml")
    ap.add_argument("--model", nargs="+", default=["all"], choices=["all", "extension", *ORDER, *EXTENSION])
    ap.add_argument("--n-configs", type=int, default=6)
    ap.add_argument("--log-dir", default=str(AUDIT_DIR), help="nơi ghi tuning_log.csv + best_configs.json")
    ap.add_argument("--ckpt-dir", default=str(PROJECT_ROOT / "outputs" / "tuning"))
    args = ap.parse_args()
    tuner = Tuner(args.config, Path(args.log_dir), Path(args.ckpt_dir))
    t0 = time.perf_counter()
    models = ORDER if "all" in args.model else EXTENSION if "extension" in args.model else args.model
    for model in models:
        tuner.tune(model, args.n_configs)
        print(f"   (tổng thời gian tuning đến giờ: {(time.perf_counter() - t0) / 3600:.2f} giờ)", flush=True)


if __name__ == "__main__":
    main()
