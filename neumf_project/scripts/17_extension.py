"""Mở rộng sau khi đã xem test (PREREG mục 9): late fusion MF + DNN, ItemKNN, UserKNN trên tập test.

    python scripts/17_extension.py --reason "Mở rộng PREREG mục 9"

Khoá test: PREREG.md đã commit và có mục 9, có --reason, code/cấu hình/audit không có thay đổi chưa commit (kể cả
file mới) — chỉ cho phép outputs/ và audit/test_access_log.csv. Ghi 1 dòng vào audit/test_access_log.csv trước khi chấm.

- Late fusion: nạp GMF, MLP, BPR-MF mà 11_final.py đã huấn luyện lại trên train ∪ val cho từng seed
  (outputs/final/seed*/) — không huấn luyện lại mạng nào; trọng số w lấy từ audit/best_configs.json (chọn trên val).
- ItemKNN, UserKNN: tính trên train ∪ val với (k, shrink) chọn trên val; tất định nên giống nhau ở mọi seed.
- Kiểm định: họ 7 so sánh riêng của mục 9 (EXT_COMPARISONS), cùng quy tắc với 12_significance.py
  (Wilcoxon theo user + bootstrap CI 95% + Holm; "tốt hơn" khi p_Holm < 0,05, CI không chứa 0, chênh ≥ 5%).
Ra: outputs/final/extension/{seed*/results_per_user.csv, seed*/results.json, summary.csv, significance.csv}.
"""
from __future__ import annotations

import os

os.environ.setdefault("TQDM_DISABLE", "1")

import argparse
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from scipy.stats import wilcoxon

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.baselines import ItemKNNBaseline, UserKNNBaseline  # noqa: E402
from src.evaluation.full_ranking import evaluate_score_function  # noqa: E402
from src.models.late_fusion import LateFusion  # noqa: E402
from src.utils.io import ensure_dir, log_test_access, prereg_committed, run_provenance  # noqa: E402


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, PROJECT_ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tune = _load("tune", "10_tune.py")
secondary = _load("secondary", "14_secondary.py")
sig = _load("sig", "12_significance.py")

AUDIT_DIR = tune.AUDIT_DIR
PREREG_MARKER = "## 9. Mở rộng sau khi xem test"
METRIC = "NDCG@10"
SUMMARY_METRICS = ["NDCG@10", "Recall@10", "HR@10", "Precision@10", "NDCG@5"]
MODELS = ["LateFusion-GMF-MLP", "LateFusion-BPR-MLP", "ItemKNN", "UserKNN"]
# Họ so sánh của mục 9 — cố định trước khi chấm test, hiệu chỉnh Holm riêng (không gộp với họ 8 so sánh chính).
EXT_COMPARISONS = [
    ("LateFusion-GMF-MLP", "NeuMF-Scratch"),     # late fusion vs early fusion (mô hình lai chọn theo val)
    ("LateFusion-GMF-MLP", "NeuMF-Pretrained"),  # late fusion vs early fusion (biến thể pre-training)
    ("LateFusion-GMF-MLP", "GMF"),               # sau khi lai (late) vs trước khi lai: nhánh MF
    ("LateFusion-GMF-MLP", "MLP"),               # sau khi lai (late) vs trước khi lai: nhánh DNN
    ("LateFusion-BPR-MLP", "BPR-MF"),            # thêm DNN vào MF đã tinh chỉnh
    ("ItemKNN", "NeuMF-Scratch"),                # baseline láng giềng (đề cương) vs mô hình lai
    ("UserKNN", "NeuMF-Scratch"),
]
ALLOWED_DIRTY = ("audit/test_access_log.csv",)


def uncommitted_code() -> list[str]:
    """File code/cấu hình/audit bị sửa HOẶC mới chưa theo dõi (git diff HEAD không thấy file mới)."""
    out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "--",
                          "src", "scripts", "configs", "audit", "demo", "run.py"],
                         cwd=PROJECT_ROOT, capture_output=True, text=True).stdout
    paths = [line[3:].strip().strip('"') for line in out.splitlines() if line.strip()]
    return [p for p in paths if not p.endswith(ALLOWED_DIRTY) and "/outputs/" not in f"/{p}"
            and "__pycache__" not in p]


def check_lock(reason: str) -> None:
    prereg = AUDIT_DIR / "PREREG.md"
    if not prereg_committed(prereg):
        raise SystemExit("Khoá test: audit/PREREG.md chưa commit (hoặc đang bị sửa).")
    if PREREG_MARKER not in prereg.read_text(encoding="utf-8"):
        raise SystemExit(f"Khoá test: PREREG.md chưa có '{PREREG_MARKER}' — đăng ký mở rộng trước khi chấm test.")
    if not reason.strip():
        raise SystemExit("Khoá test: cần --reason (ghi vào test_access_log.csv).")
    dirty = uncommitted_code()
    if dirty:
        raise SystemExit("Khoá test: code/cấu hình/audit chưa commit: " + ", ".join(dirty[:8]))


def ext_params(best: dict) -> dict:
    missing = [k for k in tune.EXTENSION if k not in best]
    if missing:
        raise SystemExit(f"Thiếu cấu hình chọn trên val cho {missing} — chạy 10_tune.py --model extension trước.")
    return {k: best[k]["params"] for k in tune.EXTENSION}


def score(name, model, records, kw, seed, rows):
    per: list[dict] = []
    res = evaluate_score_function(model, records, per_user=per, **kw)
    rows.extend({"model": name, "seed": seed, **r} for r in per)
    print(f"[seed {seed}] {name:19s} test NDCG@10 {res['NDCG@10']:.5f}  Recall@10 {res['Recall@10']:.5f}", flush=True)
    return res


def analyse(final_dir: Path, ext_dir: Path):
    main = pd.concat([pd.read_csv(f) for f in sorted(final_dir.glob("seed*/results_per_user.csv"))], ignore_index=True)
    ext = pd.concat([pd.read_csv(f) for f in sorted(ext_dir.glob("seed*/results_per_user.csv"))], ignore_index=True)
    by_seed = ext.groupby(["model", "seed"])[SUMMARY_METRICS].mean()
    summary = by_seed.groupby("model").agg(["mean", "std"])
    summary.columns = [f"{m}_{s}" for m, s in summary.columns]
    user_mean = pd.concat([main, ext]).groupby(["model", "user"])[METRIC].mean().unstack("model")
    rows = []
    for a, b in EXT_COMPARISONS:
        pair = user_mean[[a, b]].dropna()
        diff = (pair[a] - pair[b]).to_numpy()
        ma, mb = pair[a].mean(), pair[b].mean()
        lo, hi = sig.bootstrap_ci(diff)
        rows.append(dict(A=a, B=b, mean_A=ma, mean_B=mb, diff=diff.mean(), rel_diff=(ma - mb) / mb,
                         ci_low=lo, ci_high=hi, n_users=len(diff),
                         p_wilcoxon=wilcoxon(diff).pvalue if np.any(diff) else 1.0))
    s = pd.DataFrame(rows)
    s["p_holm"] = sig.holm(s["p_wilcoxon"])
    better = (s["p_holm"] < 0.05) & ((s["ci_low"] > 0) | (s["ci_high"] < 0)) & (s["rel_diff"].abs() >= 0.05)
    s["verdict"] = np.where(~better, "không khác biệt có ý nghĩa", np.where(s["diff"] > 0, "A tốt hơn", "B tốt hơn"))
    return summary.sort_values(f"{METRIC}_mean", ascending=False), s


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default="configs/hm500k_global.yaml")
    ap.add_argument("--reason", default="")
    ap.add_argument("--final-dir", default=str(PROJECT_ROOT / "outputs" / "final"))
    args = ap.parse_args()
    check_lock(args.reason)
    best = json.loads((AUDIT_DIR / "best_configs.json").read_text(encoding="utf-8"))
    p = ext_params(best)
    final_dir = Path(args.final_dir)
    seed_dirs = sorted(final_dir.glob("seed*"))
    if not seed_dirs:
        raise SystemExit(f"Không có {final_dir}/seed*/ — cần checkpoint của 11_final.py.")

    cfg, D = tune.load_data(args.config, with_test=True)
    prov = run_provenance(cfg, args.config, cwd=PROJECT_ROOT)
    log_test_access(AUDIT_DIR / "test_access_log.csv", "extension", prov, MODELS, args.reason)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    kw = dict(k_values=cfg.evaluation.k_values, tie_seed=cfg.evaluation.tie_break_seed, include_redundant=True)
    ext_dir = ensure_dir(final_dir / "extension")
    print(f"test users {len(D.test)} | commit {prov['git_commit']} | params {json.dumps(p)}", flush=True)

    # Baseline láng giềng: tất định -> chấm một lần, dùng cho mọi seed.
    knn_rows, knn_res = [], {}
    for name, cls, key in (("ItemKNN", ItemKNNBaseline, "itemknn"), ("UserKNN", UserKNNBaseline, "userknn")):
        t0 = time.perf_counter()
        model = cls(D.trva, D.n_users, D.n_items, k=p[key]["k"], shrink=p[key]["shrink"])
        knn_res[name] = score(name, model, D.test, kw, "all", knn_rows)
        print(f"   {name} xong ({time.perf_counter() - t0:.0f} s)", flush=True)

    for seed_dir in seed_dirs:
        seed = int(seed_dir.name.removeprefix("seed"))
        models = secondary.load_models(seed_dir, D, device)
        rows = [{**r, "seed": seed} for r in knn_rows]
        results = dict(knn_res)
        results["LateFusion-GMF-MLP"] = score("LateFusion-GMF-MLP", LateFusion(models["GMF"], models["MLP"],
                                              p["late_gmf_mlp"]["w"]), D.test, kw, seed, rows)
        results["LateFusion-BPR-MLP"] = score("LateFusion-BPR-MLP", LateFusion(models["BPR-MF"], models["MLP"],
                                              p["late_bpr_mlp"]["w"]), D.test, kw, seed, rows)
        out = ensure_dir(ext_dir / f"seed{seed}")
        pd.DataFrame(rows).to_csv(out / "results_per_user.csv", index=False)
        (out / "results.json").write_text(json.dumps(dict(
            seed=seed, evaluated_on="test", provenance=prov, n_test_users=len(D.test),
            n_candidate_items=len(D.test_pool), results=results, params=p), indent=2, ensure_ascii=False),
            encoding="utf-8")

    summary, significance = analyse(final_dir, ext_dir)
    summary.to_csv(ext_dir / "summary.csv")
    significance.to_csv(ext_dir / "significance.csv", index=False)
    pd.set_option("display.width", 200)
    print(f"\n{summary.round(5)}\n\n{significance.round(5).to_string(index=False)}")


if __name__ == "__main__":
    main()
