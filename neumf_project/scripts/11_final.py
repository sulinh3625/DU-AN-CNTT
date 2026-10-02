"""Đánh giá cuối trên TEST (PREREG mục 5): cấu hình tốt nhất trên val (audit/best_configs.json), 3 seed.

    python scripts/11_final.py --reason "P4b: đánh giá cuối theo PREREG"

Khoá test: từ chối nếu audit/PREREG.md chưa commit, thiếu --reason, hoặc working tree có file đã theo dõi bị sửa.
Mỗi seed ghi 1 dòng audit/test_access_log.csv TRƯỚC khi chấm test. Mỗi mô hình train trên train, early stopping
trên val (giống tuning) để lấy best_epoch, rồi train lại từ đầu trên train ∪ val đúng best_epoch epoch và chấm test
(MostPopular, BPR-MF cũng fit trên train ∪ val). Ra: outputs/final/seed<N>/{results.json, results_per_user.csv, topk.json, *.pt}.
"""
from __future__ import annotations

import os

os.environ.setdefault("TQDM_DISABLE", "1")

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import pandas as pd
import torch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.baselines import BPRMFBaseline, MostPopularBaseline, RandomBaseline
from src.data_pipeline.dataset import TrainDataset
from src.evaluation.full_ranking import evaluate_score_function, evaluate_torch_model
from src.training.trainer import get_device, make_optimizer, train_one_model
from src.utils.io import ensure_dir, log_test_access, prereg_committed, run_provenance
from src.utils.seed import seed_everything

_spec = importlib.util.spec_from_file_location("tune", PROJECT_ROOT / "scripts" / "10_tune.py")
tune = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tune)

AUDIT_DIR = tune.AUDIT_DIR
SEEDS = [42, 2024, 2025]
MODELS = ["Random", "MostPopular", "BPR-MF", "GMF", "MLP", "NeuMF-Scratch", "NeuMF-Pretrained"]
TORCH_KEYS = {"GMF": "gmf", "MLP": "mlp", "NeuMF-Scratch": "neumf_scratch", "NeuMF-Pretrained": "neumf_pretrained"}


def run_seed(seed, cfg, D, best, device, out_root, prov, reason):
    log_test_access(AUDIT_DIR / "test_access_log.csv", f"final_seed{seed}", prov, MODELS, reason)
    out = ensure_dir(out_root / f"seed{seed}")
    kw = dict(k_values=cfg.evaluation.k_values, tie_seed=cfg.evaluation.tie_break_seed, include_redundant=True)
    rows, results, topk, train_meta = [], {}, {}, {}

    def score(name, obj):
        per = []
        if isinstance(obj, torch.nn.Module):
            res, top = evaluate_torch_model(obj, D.test, device=device, return_topk=True, per_user=per, **kw)
        else:
            res, top = evaluate_score_function(obj, D.test, return_topk=True, per_user=per, **kw)
        results[name], topk[name] = res, {str(u): items for u, items in top.items()}
        rows.extend({"model": name, "seed": seed, **r} for r in per)
        print(f"[seed {seed}] {name:17s} test NDCG@10 {res['NDCG@10']:.5f}  Recall@10 {res['Recall@10']:.5f}", flush=True)

    def fit(key, p, data, pos, records, epochs, patience, init):
        seed_everything(seed)
        net = tune.build_net(key, p, D)
        if init is not None:
            net.load_pretrained(*init, alpha=p["alpha"])
        net = net.to(device)
        ds = TrainDataset(data, D.n_items, pos, p["negative_ratio"], seed=seed)
        opt = make_optimizer("adam", net.parameters(), p["lr"], p["weight_decay"])
        return train_one_model(
            net, ds, records, lambda m, r: evaluate_torch_model(m, r, device=device, **kw), opt, device,
            epochs, patience, cfg.training.batch_size, "NDCG@10", seed, key)

    def train_net(name, init=None):
        """B1: train trên train, early stopping trên val -> best_epoch (như tuning).
        B2: train lại từ đầu trên train ∪ val đúng best_epoch epoch (không còn val để dừng; test không được
        dùng để dừng) -> mô hình chấm test. NeuMF-Pretrained: B1 nạp GMF/MLP của B1, B2 nạp GMF/MLP của B2."""
        key = TORCH_KEYS[name]
        p = best[key]["params"]
        sel_init, refit_init = init or (None, None)
        sel, _, meta = fit(key, p, D.tr, D.train_pos, D.val, tune.MAX_EPOCHS, tune.PATIENCE, sel_init)
        net, _, refit = fit(key, p, D.trva, D.trva_pos, None, meta["best_epoch"], meta["best_epoch"], refit_init)
        train_meta[name] = {**meta, "refit_train_time_s": refit["train_time_s"]}
        torch.save(net.state_dict(), out / f"{key}.pt")
        return sel, net

    score("Random", RandomBaseline(seed=seed))
    score("MostPopular", MostPopularBaseline(D.trva, D.n_items))
    p = best["bpr"]["params"]
    t0 = time.perf_counter()
    bpr = BPRMFBaseline(D.n_users, D.n_items, p["embedding_dim"], seed=seed)
    bpr.fit(D.trva, epochs=p["epochs"], lr=p["lr"], reg=p["reg"], seed=seed)
    train_meta["BPR-MF"] = {"train_time_s": time.perf_counter() - t0}
    bpr.save(out / "bpr.npz")
    score("BPR-MF", bpr)
    pairs = {name: train_net(name) for name in ("GMF", "MLP", "NeuMF-Scratch")}
    (g_sel, g_net), (m_sel, m_net) = pairs["GMF"], pairs["MLP"]
    pairs["NeuMF-Pretrained"] = train_net("NeuMF-Pretrained", init=((g_sel, m_sel), (g_net, m_net)))
    for name, (_, net) in pairs.items():
        score(name, net)

    pd.DataFrame(rows).to_csv(out / "results_per_user.csv", index=False)
    (out / "topk.json").write_text(json.dumps(topk), encoding="utf-8")
    (out / "results.json").write_text(json.dumps(dict(
        seed=seed, evaluated_on="test", provenance=prov, n_test_users=len(D.test),
        n_candidate_items=len(D.test_pool), results=results,
        train_meta=train_meta, configs={m: best[k]["params"] for m, k in {**TORCH_KEYS, "BPR-MF": "bpr"}.items()},
    ), indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default="configs/hm500k_global.yaml")
    ap.add_argument("--seeds", type=int, nargs="+", default=SEEDS)
    ap.add_argument("--reason", default="")
    ap.add_argument("--out", default=str(PROJECT_ROOT / "outputs" / "final"))
    args = ap.parse_args()
    if not prereg_committed(AUDIT_DIR / "PREREG.md"):
        raise SystemExit("Khoá test: audit/PREREG.md chưa commit.")
    if not args.reason.strip():
        raise SystemExit("Khoá test: cần --reason (ghi vào test_access_log.csv).")
    cfg, D = tune.load_data(args.config, with_test=True)
    prov = run_provenance(cfg, args.config, cwd=PROJECT_ROOT)
    if prov["git_dirty"]:
        raise SystemExit("Khoá test: có file đã theo dõi chưa commit — commit trước để kết quả truy vết được.")
    best = json.loads((AUDIT_DIR / "best_configs.json").read_text(encoding="utf-8"))
    device = get_device(cfg.training.device)
    print(f"test users {len(D.test)} | commit {prov['git_commit']}", flush=True)
    for seed in args.seeds:
        t0 = time.perf_counter()
        run_seed(seed, cfg, D, best, device, Path(args.out), prov, args.reason)
        print(f"==> seed {seed} xong ({(time.perf_counter() - t0) / 60:.1f} phút)", flush=True)


if __name__ == "__main__":
    main()
