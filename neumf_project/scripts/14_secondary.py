"""Phân tích phụ trên TEST từ checkpoint của 11_final.py (PREREG mục 2: metric phụ, mô tả, không kết luận).

    python scripts/14_secondary.py --reason "Phân tích phụ: long-tail, cold/warm, beyond-accuracy, Sampled-99, độ trễ"

Không train lại: nạp checkpoint outputs/final/seed<N>/ (*.pt, bpr.npz) với cấu hình trong results.json.
Khoá test: cần audit/PREREG.md đã commit, --reason, và code/cấu hình không có thay đổi chưa commit (cho phép
outputs/ và audit/test_access_log.csv — do 11/12/13 vừa ghi). Chạy được trước hoặc sau 12_significance.py. Ghi 1 dòng test_access_log.csv trước khi chấm.

Ra outputs/final/:
  stratified.csv        model, seed, subset (all/head/tail/cold/warm), n_users, NDCG@10, Recall@10, HR@10, Precision@10
  beyond_accuracy.csv   model, seed, coverage, novelty, ARP, HRR (top-10)
  sampled99.csv         model, seed, n_cases, HR@10, NDCG@10 — 1 item đúng + 99 item âm (protocol NCF gốc)
  latency.csv           model, n_requests, p50_ms, p95_ms, mean_ms — chấm toàn bộ candidate + lấy top-10 cho 1 user, CPU

Random không có trong phân tích phụ: điểm Random tính từng cặp bằng Python (hàng chục triệu lời gọi mỗi lượt) và
kết quả không mang thông tin (xem kết quả chính).
"""
from __future__ import annotations

import os

os.environ.setdefault("TQDM_DISABLE", "1")

import argparse
import importlib.util
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.baselines import BPRMFBaseline, MostPopularBaseline
from src.data_pipeline.negative_sampling import build_user_positive_sets
from src.evaluation.beyond_accuracy import (average_recommendation_popularity, catalog_coverage,
                                            head_recommendation_rate, novelty_score)
from src.evaluation.cold_start import define_cold_users
from src.evaluation.full_ranking import EvalRecord, evaluate_score_function, evaluate_torch_model
from src.evaluation.long_tail import define_head_items, split_records_head_tail
from src.utils.io import log_test_access, prereg_committed, run_provenance

_spec = importlib.util.spec_from_file_location("tune", PROJECT_ROOT / "scripts" / "10_tune.py")
tune = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tune)

AUDIT_DIR = tune.AUDIT_DIR
MODELS = ["MostPopular", "BPR-MF", "GMF", "MLP", "NeuMF-Scratch", "NeuMF-Pretrained"]
TORCH_KEYS = {"GMF": "gmf", "MLP": "mlp", "NeuMF-Scratch": "neumf_scratch", "NeuMF-Pretrained": "neumf_pretrained"}
METRICS = ["NDCG@10", "Recall@10", "HR@10", "Precision@10"]
K = 10
SAMPLED_SEED = 2026  # tập item âm cố định, không phụ thuộc seed huấn luyện
ALLOWED_DIRTY = {"audit/test_access_log.csv"}


def dirty_code_files() -> set[str]:
    """File code/cấu hình đã theo dõi bị sửa (kể cả đã stage) trong neumf_project/.

    Được phép sửa: outputs/ (kết quả của 11/12/13) và audit/test_access_log.csv (11 vừa ghi thêm).
    """
    out = subprocess.run(["git", "diff", "HEAD", "--name-only", "--relative"], cwd=PROJECT_ROOT,
                         capture_output=True, text=True).stdout
    files = {line.strip() for line in out.splitlines() if line.strip()}
    return {f for f in files if not f.startswith("outputs/") and f not in ALLOWED_DIRTY}


def load_models(seed_dir: Path, D, device):
    """Nạp lại đúng các mô hình mà 11_final.py đã lưu cho seed này."""
    configs = json.loads((seed_dir / "results.json").read_text(encoding="utf-8"))["configs"]
    models = {"MostPopular": MostPopularBaseline(D.trva, D.n_items), "BPR-MF": BPRMFBaseline.load(seed_dir / "bpr.npz")}
    for name, key in TORCH_KEYS.items():
        net = tune.build_net(key, configs[name], D)
        net.load_state_dict(torch.load(seed_dir / f"{key}.pt", map_location="cpu"))
        models[name] = net.to(device).eval()
    return models


def evaluate(model, records, device, per_user=None, topk=False):
    kw = dict(k_values=[K], tie_seed=2026, include_redundant=True, return_topk=topk, per_user=per_user)
    if isinstance(model, torch.nn.Module):
        return evaluate_torch_model(model, records, device=device, **kw)
    return evaluate_score_function(model, records, **kw)


def sampled_records(D, n_neg: int) -> list[EvalRecord]:
    """Mỗi cặp (user, item) test: 1 item đúng + n_neg item âm lấy từ pool (item có trong train ∪ val),
    loại mọi item user đã có trước test (train ∪ val) và trong test."""
    known = build_user_positive_sets(pd.concat([D.trva, D.te], ignore_index=True), D.n_users)
    rng = np.random.default_rng(SAMPLED_SEED)
    pool = np.asarray(D.test_pool, dtype=np.int64)
    records = []
    for u, i in zip(D.te["user"].to_numpy(), D.te["item"].to_numpy()):
        u, i = int(u), int(i)
        negs: list[int] = []
        while len(negs) < n_neg:
            for j in rng.choice(pool, size=2 * n_neg):
                j = int(j)
                if j not in known[u] and j not in negs:
                    negs.append(j)
                    if len(negs) == n_neg:
                        break
        records.append(EvalRecord(u, i, np.array([i, *negs], dtype=np.int64)))
    return records


def measure_latency(model, records, n_requests=200, warmup=20, seed=0) -> dict:
    """Thời gian phục vụ 1 yêu cầu: chấm toàn bộ candidate của 1 user rồi lấy top-10, trên CPU."""
    rng = np.random.default_rng(seed)
    picks = rng.choice(len(records), size=warmup + n_requests, replace=True)
    times = []
    for n, idx in enumerate(picks):
        r = records[int(idx)]
        t0 = time.perf_counter()
        if isinstance(model, torch.nn.Module):
            with torch.no_grad():
                items = torch.from_numpy(r.candidates)
                users = torch.full_like(items, r.user)
                scores = model(users, items)
                top = torch.topk(scores, K).indices.numpy()
        else:
            scores = np.asarray(model.score_items(r.user, r.candidates))
            top = np.argpartition(-scores, K)[:K]
        _ = r.candidates[top]
        if n >= warmup:
            times.append((time.perf_counter() - t0) * 1000)
    t = np.array(times)
    return dict(n_requests=len(t), n_candidates_mean=float(np.mean([len(r.candidates) for r in records])),
                p50_ms=float(np.percentile(t, 50)), p95_ms=float(np.percentile(t, 95)), mean_ms=float(t.mean()))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default="configs/hm500k_global.yaml")
    ap.add_argument("--final-dir", default=str(PROJECT_ROOT / "outputs" / "final"))
    ap.add_argument("--reason", default="")
    ap.add_argument("--latency-requests", type=int, default=200)
    args = ap.parse_args()
    final_dir = Path(args.final_dir)
    seed_dirs = sorted(p for p in final_dir.glob("seed*") if (p / "results.json").exists())
    if not seed_dirs:
        raise SystemExit(f"Chưa có checkpoint trong {final_dir}/seed*/ — chạy scripts/11_final.py trước.")
    if not prereg_committed(AUDIT_DIR / "PREREG.md"):
        raise SystemExit("Khoá test: audit/PREREG.md chưa commit.")
    if not args.reason.strip():
        raise SystemExit("Khoá test: cần --reason (ghi vào test_access_log.csv).")
    extra = dirty_code_files()
    if extra:
        raise SystemExit(f"Khoá test: có file đã theo dõi chưa commit: {sorted(extra)}")

    cfg, D = tune.load_data(args.config, with_test=True)
    prov = run_provenance(cfg, args.config, cwd=PROJECT_ROOT)
    log_test_access(AUDIT_DIR / "test_access_log.csv", "secondary", prov, MODELS, args.reason)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    head = define_head_items(D.trva, D.n_items, cfg.evaluation.head_fraction)
    cold = define_cold_users(D.trva, D.n_users, cfg.evaluation.cold_fraction)
    head_recs, tail_recs = split_records_head_tail(D.test, head)
    item_counts = D.trva["item"].value_counts().to_dict()
    sampled = sampled_records(D, cfg.evaluation.sampled_negatives)
    print(f"test users {len(D.test)} (head {len(head_recs)}, tail {len(tail_recs)}) | cold users "
          f"{sum(r.user in cold for r in D.test)} | sampled cases {len(sampled)} | device {device}", flush=True)

    strat, beyond, samp = [], [], []
    for seed_dir in seed_dirs:
        seed = int(seed_dir.name.removeprefix("seed"))
        reported = json.loads((seed_dir / "results.json").read_text(encoding="utf-8"))["results"]
        models = load_models(seed_dir, D, device)
        for name, model in models.items():
            t0 = time.perf_counter()
            per: list[dict] = []
            res, top = evaluate(model, D.test, device, per_user=per, topk=True)
            gap = abs(res["NDCG@10"] - reported[name]["NDCG@10"])
            if gap > 1e-6:
                print(f"  CẢNH BÁO {name} seed {seed}: NDCG@10 lệch {gap:.2e} so với results.json "
                      "(GPU/CPU khác nhau có thể lệch nhỏ)", flush=True)
            per_df = pd.DataFrame(per)
            subsets = {"all": per_df,
                       "cold": per_df[per_df["user"].isin(cold)], "warm": per_df[~per_df["user"].isin(cold)]}
            for label, recs in (("head", head_recs), ("tail", tail_recs)):
                sub: list[dict] = []
                evaluate(model, recs, device, per_user=sub)
                subsets[label] = pd.DataFrame(sub)
            for label, df in subsets.items():
                strat.append(dict(model=name, seed=seed, subset=label, n_users=len(df), **df[METRICS].mean().to_dict()))
            recs10 = {u: items[:K] for u, items in top.items()}
            beyond.append(dict(model=name, seed=seed, coverage=catalog_coverage(recs10, len(D.test_pool)),
                               novelty=novelty_score(recs10, item_counts, len(D.trva)),
                               ARP=average_recommendation_popularity(recs10, item_counts),
                               HRR=head_recommendation_rate(recs10, head)))
            s = evaluate(model, sampled, device)
            samp.append(dict(model=name, seed=seed, n_cases=len(sampled), **{m: s[m] for m in ("HR@10", "NDCG@10")}))
            print(f"[seed {seed}] {name:17s} xong ({time.perf_counter() - t0:.0f} s)", flush=True)

    # Độ trễ: seed đầu, mọi mô hình trên CPU (máy phục vụ phổ thông không có GPU).
    torch_threads = torch.get_num_threads()
    models = load_models(seed_dirs[0], D, torch.device("cpu"))
    lat = []
    for name, model in models.items():
        lat.append(dict(model=name, **measure_latency(model, D.test, args.latency_requests),
                        device="cpu", cpu=platform.processor() or platform.machine(), cpu_count=os.cpu_count(),
                        torch_threads=torch_threads))
        print(f"latency {name:17s} p50 {lat[-1]['p50_ms']:.1f} ms  p95 {lat[-1]['p95_ms']:.1f} ms", flush=True)

    pd.DataFrame(strat).to_csv(final_dir / "stratified.csv", index=False)
    pd.DataFrame(beyond).to_csv(final_dir / "beyond_accuracy.csv", index=False)
    pd.DataFrame(samp).to_csv(final_dir / "sampled99.csv", index=False)
    pd.DataFrame(lat).to_csv(final_dir / "latency.csv", index=False)
    print("Đã ghi:", *(f"{final_dir.name}/{f}" for f in
                       ("stratified.csv", "beyond_accuracy.csv", "sampled99.csv", "latency.csv")))


if __name__ == "__main__":
    main()
