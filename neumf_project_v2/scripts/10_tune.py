"""Tuning CHỈ trên validation theo docs/audit/PREREG.md mục 4 (script nhẹ, không dựng test records).

    python scripts/10_tune.py --model all          # hoặc: ials | bpr | gmf | ... (xem ORDER)

Mỗi cấu hình ghi 1 dòng vào docs/audit/tuning_log.csv (config hash, git commit, val metrics, thời gian).
Cấu hình tốt nhất theo val NDCG@10 ghi vào docs/audit/best_configs.json; checkpoint ở outputs/tuning/.
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
from src.baselines import BPRMFBaseline, IALSBaseline, MostPopularBaseline
from src.data_pipeline.dataset import TrainDataset
from src.data_pipeline.negative_sampling import build_user_positive_sets
from src.data_pipeline.preprocessing import apply_feedback_weights, build_interactions
from src.data_pipeline.splitting import assert_disjoint_splits, global_temporal_split
from src.evaluation.full_ranking import build_full_ranking_records_multi, evaluate_score_function, evaluate_torch_model
from src.models.cfnet import CFNet, interaction_matrix
from src.models.neumf import GMF, MLP, NeuMF
from src.training.trainer import get_device, make_optimizer, train_one_model
from src.utils.io import ensure_dir, run_provenance
from src.utils.seed import seed_everything

AUDIT_DIR = PROJECT_ROOT.parent / "docs" / "audit"
SEED, GRID_SEED, MAX_EPOCHS, PATIENCE = 42, 0, 20, 5
METRICS = ["NDCG@10", "Recall@10", "HR@10", "Precision@10", "NDCG@5"]

NEURAL = dict(lr=[1e-3, 5e-4], negative_ratio=[4, 8], embedding_dim=[32, 64], weight_decay=[0.0, 1e-6],
              dropout=[0.0, 0.2])
GRIDS = {
    "popularity_recent": dict(window_days=[7, 14, 28, 56]),
    "ials": dict(factors=[32, 64, 128, 256], regularization=[0.001, 0.01, 0.1], alpha=[1.0, 10.0, 40.0]),
    "bpr": dict(embedding_dim=[32, 64, 128], lr=[0.01, 0.03, 0.05], reg=[0.001, 0.005, 0.01], epochs=[20, 40]),
    "gmf": {k: v for k, v in NEURAL.items() if k != "dropout"},
    "mlp": NEURAL,
    "neumf_scratch": NEURAL,
    "neumf_pretrained": dict(lr=[1e-3, 5e-4, 1e-4], alpha=[0.3, 0.5, 0.7]),
    "cfnet": {**NEURAL, "rl_layers": [[512, 64], [256, 64]]},
    "fusion_b": dict(w=[round(0.1 * i, 1) for i in range(11)]),
}
ORDER = list(GRIDS)  # thứ tự chạy: neumf_pretrained cần gmf+mlp, fusion_b cần mọi thứ trước nó
TORCH_MODELS = {"gmf", "mlp", "neumf_scratch", "neumf_pretrained", "cfnet"}
# EarlyFusion không tune: kiến trúc trùng hệt MLP (PREREG mục 8, tests/test_tuning.py).


def default_config(model: str, cfg) -> dict:
    """Cấu hình mặc định hiện tại (configs/hm500k_global.yaml) — PREREG: luôn là 1 trong các cấu hình thử."""
    t, m, b = cfg.training, cfg.model, cfg.baselines
    neural = dict(lr=t.finetune_lr if model == "neumf_scratch" else t.pretrain_lr, negative_ratio=t.negative_ratio,
                  embedding_dim=m.embedding_dim, weight_decay=t.weight_decay, dropout=m.dropout)
    return {
        "popularity_recent": dict(window_days=b.popularity_window_days),
        "ials": dict(factors=b.ials.factors, regularization=b.ials.regularization, alpha=b.ials.alpha),
        "bpr": dict(embedding_dim=b.bpr.embedding_dim, lr=b.bpr.lr, reg=b.bpr.reg, epochs=b.bpr.epochs),
        "gmf": {k: v for k, v in neural.items() if k != "dropout"},
        "neumf_pretrained": dict(lr=t.finetune_lr, alpha=m.pretrain_alpha),
        "cfnet": {**neural, "rl_layers": [512, 64]},
        "fusion_b": dict(w=0.5),
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
    if model == "cfnet":
        return CFNet(D.R, d, mlp_layers(d), p["rl_layers"], p["dropout"])
    raise ValueError(model)


def load_data(config_path: str):
    cfg, adapter = build_adapter(config_path)
    if cfg.dataset.split != "global":
        raise SystemExit("PREREG: tuning trên protocol chính (split: global).")
    data = build_interactions(adapter.load_events(), cfg.dataset.k_core)
    tr, va, te = global_temporal_split(data.df, cfg.dataset.val_start, cfg.dataset.test_start)
    assert_disjoint_splits(tr, va, te)
    tr, va, _, _ = apply_feedback_weights(tr, va, te, cfg.feedback.mode, cfg.feedback.confidence_alpha)
    del te  # không dùng test ở bất kỳ đâu trong tuning
    train_pos = build_user_positive_sets(tr, data.n_users)
    val = build_full_ranking_records_multi(va, data.n_items, train_pos, np.unique(tr["item"].to_numpy()))
    return cfg, SimpleNamespace(tr=tr, n_users=data.n_users, n_items=data.n_items, train_pos=train_pos, val=val,
                                R=interaction_matrix(tr, data.n_users, data.n_items))


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
        net = build_net(model, entry["params"], self.D)
        net.load_state_dict(torch.load(PROJECT_ROOT / entry["checkpoint"], map_location="cpu"))
        return net.to(self.device).eval()

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
        if model == "popularity_recent":
            return self.eval_scores(MostPopularBaseline(D.tr, D.n_items, window_days=p["window_days"])), None, None
        if model == "ials":
            m = IALSBaseline(D.n_users, D.n_items, p["factors"], p["regularization"], p["alpha"],
                             self.cfg.baselines.ials.iterations, seed=SEED).fit(D.tr)
            return self.eval_scores(m), None, m
        if model == "bpr":
            m = BPRMFBaseline(D.n_users, D.n_items, p["embedding_dim"], seed=SEED)
            m.fit(D.tr, epochs=p["epochs"], lr=p["lr"], reg=p["reg"], seed=SEED)
            return self.eval_scores(m), None, m
        if model == "fusion_b":
            return self.eval_scores(self._fusion(p["w"])), None, None
        raise ValueError(model)

    def _fusion(self, w):
        """B: w * minmax(điểm MF) + (1-w) * minmax(điểm NeuMF), min-max trên candidate của từng user."""
        if not hasattr(self, "_fusion_cache"):
            best = self.best()
            mf_name = max(("ials", "bpr"), key=lambda k: best[k]["val"]["NDCG@10"])
            nn_name = max(("neumf_scratch", "neumf_pretrained"), key=lambda k: best[k]["val"]["NDCG@10"])
            loader = IALSBaseline if mf_name == "ials" else BPRMFBaseline
            mf, net = loader.load(PROJECT_ROOT / best[mf_name]["checkpoint"]), self.load_net(nn_name)

            def mm(x):
                x = np.asarray(x, dtype=np.float64)
                return (x - x.min()) / (x.max() - x.min() + 1e-12)

            cache = {}
            with torch.no_grad():
                for r in self.D.val:
                    u = torch.full((len(r.candidates),), r.user, dtype=torch.long, device=self.device)
                    i = torch.as_tensor(r.candidates, dtype=torch.long, device=self.device)
                    cache[r.user] = (mm(mf.score_items(r.user, r.candidates)), mm(net(u, i).cpu().numpy()))
            self._fusion_cache, self._fusion_parts = cache, {"mf": mf_name, "neumf": nn_name}
        cache = self._fusion_cache

        class Fused:
            @staticmethod
            def score_items(user, items):  # items = record.candidates (cùng thứ tự với cache)
                a, b = cache[user]
                return w * a + (1 - w) * b

        return Fused()

    # ---------- vòng tuning 1 mô hình
    def tune(self, model: str, n_configs: int):
        fixed = {}
        if model == "neumf_pretrained":  # nhánh GMF/MLP lấy từ pretrain tốt nhất; negative/wd theo MLP tốt nhất
            g, m = self.best()["gmf"]["params"], self.best()["mlp"]["params"]
            fixed = dict(embedding_dim=m["embedding_dim"], gmf_dim=g["embedding_dim"], dropout=m["dropout"],
                         negative_ratio=m["negative_ratio"], weight_decay=m["weight_decay"])
        n = len(GRIDS["fusion_b"]["w"]) if model == "fusion_b" else n_configs
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
        if model == "fusion_b":
            best_row["components"] = self._fusion_parts
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
    ap.add_argument("--model", nargs="+", default=["all"], choices=["all", *ORDER])
    ap.add_argument("--n-configs", type=int, default=6)
    ap.add_argument("--log-dir", default=str(AUDIT_DIR), help="nơi ghi tuning_log.csv + best_configs.json")
    ap.add_argument("--ckpt-dir", default=str(PROJECT_ROOT / "outputs" / "tuning"))
    args = ap.parse_args()
    tuner = Tuner(args.config, Path(args.log_dir), Path(args.ckpt_dir))
    t0 = time.perf_counter()
    for model in ORDER if "all" in args.model else args.model:
        tuner.tune(model, args.n_configs)
        print(f"   (tổng thời gian tuning đến giờ: {(time.perf_counter() - t0) / 3600:.2f} giờ)", flush=True)


if __name__ == "__main__":
    main()
