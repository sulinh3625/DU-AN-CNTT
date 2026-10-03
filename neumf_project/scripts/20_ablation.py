"""Ablation trên VALIDATION (đề cương chi tiết mục 4.5 và 5.3): ảnh hưởng của số chiều embedding, số tầng ẩn của
tháp MLP và tỉ lệ mẫu âm tới mô hình lai NeuMF-Scratch.

    python scripts/20_ablation.py              # 12 cấu hình, khoảng 45–60 phút trên RTX 3050
    python scripts/20_ablation.py --resume     # chạy tiếp, bỏ qua cấu hình đã có trong file kết quả

Mỗi lần chỉ đổi MỘT yếu tố quanh cấu hình đã chọn của NeuMF-Scratch (audit/best_configs.json):
  - embedding_dim ∈ {8, 16, 32, 64, 128} (số chiều mỗi bảng embedding của cả hai nhánh);
  - n_hidden ∈ {0, 1, 2, 3, 4}: số tầng ẩn của tháp MLP, mỗi tầng giảm một nửa [2d → d → d/2 → ...]; 0 tầng = nối hai
    embedding rồi đưa thẳng vào lớp dự đoán, như "MLP-0" trong He et al. (2017); 3 tầng là tháp của mọi mô hình chính;
  - negative_ratio ∈ {1, 2, 4, 8}.
Seed 42, cùng quy trình huấn luyện như tuning (Adam, tối đa 20 epoch, dừng sớm patience 5 theo NDCG@10 validation).

Chỉ dùng validation: không dựng test records, không ghi test_access_log, không đổi cấu hình của đánh giá cuối — kết quả là
phân tích mô tả cho ablation, KHÔNG dùng để chọn lại mô hình. Ra: outputs/ablation/ablation_val.csv (ghi dần từng dòng).
"""
from __future__ import annotations

import os

os.environ.setdefault("TQDM_DISABLE", "1")

import argparse
import csv
import importlib.util
import json
import sys
import time
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_pipeline.dataset import TrainDataset  # noqa: E402
from src.evaluation.full_ranking import evaluate_torch_model  # noqa: E402
from src.models.neumf import NeuMF  # noqa: E402
from src.training.trainer import get_device, make_optimizer, train_one_model  # noqa: E402
from src.utils.io import ensure_dir, run_provenance  # noqa: E402
from src.utils.seed import seed_everything  # noqa: E402

_spec = importlib.util.spec_from_file_location("tune", PROJECT_ROOT / "scripts" / "10_tune.py")
tune = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tune)

OUT = PROJECT_ROOT / "outputs" / "ablation" / "ablation_val.csv"
FACTORS = {"embedding_dim": [8, 16, 32, 64, 128], "n_hidden": [0, 1, 2, 3, 4], "negative_ratio": [1, 2, 4, 8]}
BASE_HIDDEN = 3  # tháp [2d, d, d/2, d/4] của mọi mô hình chính (10_tune.mlp_layers)
METRICS = ["NDCG@10", "Recall@10", "HR@10", "Precision@10", "NDCG@5"]


def tower(d: int, n_hidden: int) -> list[int]:
    """Kích thước các tầng của nhánh MLP: [2d] rồi n_hidden tầng ẩn, mỗi tầng giảm một nửa (n_hidden = 3 -> đúng
    10_tune.mlp_layers(d)); n_hidden = 0 -> [2d], nhánh MLP chỉ nối hai embedding."""
    return [2 * d] + [max(1, d // 2 ** k) for k in range(n_hidden)]


def ablation_configs(base: dict) -> list[dict]:
    """Cấu hình gốc + đổi từng yếu tố một (bỏ giá trị trùng cấu hình gốc)."""
    out = [{"factor": "base", "value": "", **base}]
    for factor, values in FACTORS.items():
        out.extend({"factor": factor, "value": v, **{**base, factor: v}} for v in values if v != base[factor])
    return out


def base_config(best: dict) -> dict:
    p = best["neumf_scratch"]["params"]
    return dict(embedding_dim=int(p["embedding_dim"]), n_hidden=BASE_HIDDEN, negative_ratio=int(p["negative_ratio"]),
                lr=float(p["lr"]), weight_decay=float(p["weight_decay"]), dropout=float(p["dropout"]))


def run_one(cfg, D, p: dict, device, seed: int, max_epochs: int, patience: int):
    """Huấn luyện một NeuMF-Scratch giống Tuner.fit_torch của 10_tune.py, chỉ khác tháp MLP."""
    seed_everything(seed)
    d = p["embedding_dim"]
    net = NeuMF(D.n_users, D.n_items, d, tower(d, p["n_hidden"]), p["dropout"]).to(device)
    ds = TrainDataset(D.tr, D.n_items, D.train_pos, p["negative_ratio"], seed=seed)
    opt = make_optimizer("adam", net.parameters(), p["lr"], p["weight_decay"])
    kw = dict(k_values=cfg.evaluation.k_values, tie_seed=cfg.evaluation.tie_break_seed, include_redundant=True)
    evaluate = lambda m, r: evaluate_torch_model(m, r, device=device, **kw)  # noqa: E731
    net, _, meta = train_one_model(net, ds, D.val, evaluate, opt, device, max_epochs, patience,
                                   cfg.training.batch_size, "NDCG@10", seed, "NeuMF-Scratch")
    return evaluate(net, D.val), meta


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default="configs/hm500k_global.yaml")
    ap.add_argument("--resume", action="store_true", help="giữ file kết quả cũ, bỏ qua cấu hình đã chạy")
    ap.add_argument("--seed", type=int, default=tune.SEED)
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--max-configs", type=int, default=None, help="chỉ chạy N cấu hình đầu (kiểm tra nhanh)")
    ap.add_argument("--max-epochs", type=int, default=tune.MAX_EPOCHS)
    args = ap.parse_args()

    out = Path(args.out)
    ensure_dir(out.parent)
    done = set()
    if out.exists():
        if args.resume:
            prev = pd.read_csv(out, dtype={"value": str}, keep_default_na=False)
            done = set(zip(prev["factor"], prev["value"]))
        else:
            out.unlink()

    cfg, D = tune.load_data(args.config)  # chỉ train + validation, không dựng test records
    best = json.loads((tune.AUDIT_DIR / "best_configs.json").read_text(encoding="utf-8"))
    base = base_config(best)
    prov = run_provenance(cfg, args.config, cwd=PROJECT_ROOT)
    device = get_device(cfg.training.device)
    todo = [p for p in ablation_configs(base) if (p["factor"], str(p["value"])) not in done][:args.max_configs]
    print(f"Cấu hình gốc NeuMF-Scratch: {base} | còn {len(todo)} cấu hình | commit {prov['git_commit']}", flush=True)

    t_all = time.perf_counter()
    for idx, p in enumerate(todo, start=1):
        t0 = time.perf_counter()
        metrics, meta = run_one(cfg, D, p, device, args.seed, args.max_epochs, tune.PATIENCE)
        row = dict(factor=p["factor"], value=p["value"], embedding_dim=p["embedding_dim"], n_hidden=p["n_hidden"],
                   negative_ratio=p["negative_ratio"], **{m: metrics[m] for m in METRICS},
                   best_epoch=meta["best_epoch"], n_params=meta["n_parameters"],
                   time_s=round(time.perf_counter() - t0, 1), seed=args.seed, git_commit=prov["git_commit"],
                   git_dirty=prov["git_dirty"])
        new = not out.exists()
        with out.open("a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(row))
            if new:
                w.writeheader()
            w.writerow(row)
        print(f"[{idx}/{len(todo)}] {p['factor']}={p['value']} (d={p['embedding_dim']}, tầng ẩn={p['n_hidden']}, "
              f"neg={p['negative_ratio']}) -> val NDCG@10 {metrics['NDCG@10']:.5f}, epoch {meta['best_epoch']} "
              f"({row['time_s']:.0f}s)", flush=True)
    print(f"Xong ({(time.perf_counter() - t_all) / 60:.1f} phút) -> {out}")


if __name__ == "__main__":
    main()
