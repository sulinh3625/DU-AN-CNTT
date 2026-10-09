"""Tinh chỉnh CHỈ trên tập xác thực của mẫu phát triển hm500k theo giao thức v2 (audit/PREREG_v2.md).

    python scripts/22_tune_v2.py                       # mọi mô hình, theo thứ tự ORDER
    python scripts/22_tune_v2.py --model neumf_f --resume

- Mô hình có học: 6 cấu hình mỗi mô hình (cấu hình mặc định + 5 cấu hình rút cố định từ lưới), seed 42, tối đa 20
  epoch, dừng sớm sau 5 epoch không cải thiện NDCG@10 trên tập xác thực. Most Popular gần đây, gợi ý theo nội dung và
  Late Fusion-F chỉ có một tham số nên thử đủ lưới.
- Mỗi cấu hình ghi một dòng vào audit/v2/tuning_log.csv; cấu hình tốt nhất theo NDCG@10 vào audit/v2/best_configs.json
  (kèm checkpoint của GMF-F, MLP-F tốt nhất cho Late Fusion-F). --resume bỏ qua cấu hình đã có trong nhật ký.
- Không dựng tập kiểm thử của bất kỳ mẫu nào.
"""
from __future__ import annotations

import os

os.environ.setdefault("TQDM_DISABLE", "1")

import argparse
import csv
import hashlib
import json
import time
from datetime import datetime
from pathlib import Path

import torch

import v2_common as V
from src.utils.io import ensure_dir

ORDER = ["popularity", "recent_pop", "content", "itemknn", "userknn", "bpr", "gmf", "mlp", "neumf",
         "gmf_f", "mlp_f", "neumf_f", "late_f"]
CKPT = V.PROJECT_ROOT / "outputs" / "v2" / "tuning"


def log_row(path: Path, row: dict) -> None:
    new = not path.exists()
    if not new:  # nhật ký cũ thiếu/thừa cột (vd. trước khi có data_md5) -> ghi nối sẽ lệch cột
        with path.open(encoding="utf-8") as f:
            header = next(csv.reader(f), [])
        if header != list(row):
            raise SystemExit(f"{path} có cột {header}, khác dòng sắp ghi {list(row)} — chuyển nhật ký cũ đi rồi "
                             "chạy lại.")
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        if new:
            w.writeheader()
        w.writerow(row)


def logged(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", nargs="+", default=["all"], choices=["all", *ORDER])
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--log-dir", default=str(V.AUDIT))
    ap.add_argument("--max-epochs", type=int, default=V.CFG["training"]["max_epochs"])
    args = ap.parse_args()
    log_dir = ensure_dir(Path(args.log_dir))
    log_path, best_path = log_dir / "tuning_log.csv", log_dir / "best_configs.json"
    ensure_dir(CKPT)

    t0 = time.time()
    D = V.load_data("dev", with_test=False)
    other = [r for r in logged(log_path) if r.get("data_md5") != D.meta["data_md5"]]
    if other:  # nhật ký của dữ liệu khác (vd. trước bản cuối): --resume sẽ bỏ qua nhầm, best_configs.json cũng cũ
        raise SystemExit(f"{log_path} có {len(other)} dòng tinh chỉnh trên dữ liệu khác (data_md5) — chuyển "
                         f"tuning_log.csv và best_configs.json trong {log_dir} sang chỗ khác rồi chạy lại.")
    st, dev, seed = D.val, V.device(), V.CFG["tuning"]["seed"]
    prov = V.provenance()
    print(f"mẫu phát triển: {D.n_users:,} người dùng, {D.n_items:,} sản phẩm ({D.n_id_items:,} có ID), "
          f"{len(st.records):,} người dùng xác thực, {len(st.targets):,} cặp đúng "
          f"({int(st.new[st.targets['item']].sum()):,} sản phẩm mới) | commit {prov['git_commit']} "
          f"dirty={prov['git_dirty']} code {prov['code_hash']} ({time.time() - t0:.0f}s)", flush=True)
    best = json.loads(best_path.read_text(encoding="utf-8")) if best_path.exists() else {}
    models = ORDER if "all" in args.model else [m for m in ORDER if m in args.model]
    late_parts = {}

    for model in models:
        configs = V.configs_for(model, V.CFG["tuning"]["n_configs"])
        done = {r["params"] for r in logged(log_path) if r["model"] == model} if args.resume else set()
        if model == "late_f":
            late_parts = {k: load_best(k, best, D, st, dev) for k in V.LATE_PARTS}
        for cid, p in enumerate(configs):
            key = json.dumps(p, sort_keys=True)
            if key in done:
                continue
            t1 = time.time()
            best_epoch, state = None, None
            if model in V.TORCH_ID or model in V.TORCH_FEAT:
                net, _, meta = V.fit_torch(model, p, D, st, st, args.max_epochs, V.CFG["training"]["patience"],
                                           seed, dev)
                metrics = V.evaluate(V.torch_scorer(model, net, st, D, dev), st, dev)
                best_epoch, state = meta["best_epoch"], {k: v.cpu() for k, v in net.state_dict().items()}
            elif model == "late_f":
                metrics = V.evaluate(V.late_fusion(late_parts, p["w"]), st, dev)
            else:
                metrics = V.evaluate(V.score_fn(model, p, D, st, seed), st, dev)
            row = dict(timestamp=datetime.now().isoformat(timespec="seconds"), model=model, config_id=cid,
                       params=key, config_hash=hashlib.sha256(f"{model}{key}{seed}".encode()).hexdigest()[:16],
                       git_commit=prov["git_commit"], git_dirty=prov["git_dirty"], code_hash=prov["code_hash"],
                       data_md5=D.meta["data_md5"], seed=seed, best_epoch=best_epoch,
                       time_s=round(time.time() - t1, 1), **{f"val_{k}": round(metrics[k], 6) for k in V.METRICS})
            log_row(log_path, row)
            print(f"[{model} {cid + 1}/{len(configs)}] {key} -> NDCG@10 {metrics['NDCG@10']:.5f} "
                  f"(cũ {metrics['NDCG@10_old']:.5f} / mới {metrics['NDCG@10_new']:.5f}), epoch {best_epoch}, "
                  f"{row['time_s']:.0f}s", flush=True)
            if state is not None and model in V.LATE_PARTS:
                prev = best.get(model, {}).get("val", {}).get("NDCG@10", -1.0)
                if metrics["NDCG@10"] > prev:  # giữ checkpoint của cấu hình tốt nhất cho Late Fusion-F
                    torch.save(state, CKPT / f"{model}_best.pt")
                    best[model] = dict(params=p, val={k: metrics[k] for k in V.METRICS}, best_epoch=best_epoch)
                    best_path.write_text(json.dumps(best, indent=2, ensure_ascii=False), encoding="utf-8")
        rows = [r for r in logged(log_path) if r["model"] == model]
        top = max(rows, key=lambda r: float(r["val_NDCG@10"]))
        best[model] = dict(params=json.loads(top["params"]), config_hash=top["config_hash"],
                           best_epoch=None if top["best_epoch"] in ("", "None") else int(float(top["best_epoch"])),
                           val={k: float(top[f"val_{k}"]) for k in V.METRICS},
                           checkpoint=(CKPT / f"{model}_best.pt").relative_to(V.PROJECT_ROOT).as_posix()
                           if model in V.LATE_PARTS else None)
        best_path.write_text(json.dumps(best, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"==> {model} tốt nhất: {best[model]['params']} NDCG@10 {best[model]['val']['NDCG@10']:.5f} "
              f"({(time.time() - t0) / 60:.0f} phút)", flush=True)


def load_best(key: str, best: dict, D, st, dev):
    """GMF-F / MLP-F tốt nhất (checkpoint lúc tinh chỉnh) cho Late Fusion-F."""
    if key not in best:
        raise SystemExit(f"Chưa tinh chỉnh {key} — chạy --model {key} trước late_f")
    net = V.build_torch(key, best[key]["params"], D, dev)
    net.load_state_dict(torch.load(CKPT / f"{key}_best.pt", map_location=dev))
    return V.torch_scorer(key, net, st, D, dev)


if __name__ == "__main__":
    main()
