"""Đánh giá cuối giao thức v2 trên tập kiểm thử của mẫu kiểm định B (audit/PREREG_v2.md mục 5).

    python scripts/23_final_v2.py --reason "Đánh giá cuối v2 theo PREREG_v2"
    python scripts/23_final_v2.py --reason "..." --seeds 2026 3407     # chạy tiếp các seed chưa chạy (bị ngắt giữa chừng)
    python scripts/23_final_v2.py --dry-run --max-epochs 1             # thử toàn bộ đường ống trên tập xác thực của A

Khoá kiểm thử (bỏ qua khi --dry-run): audit/PREREG_v2.md đã commit; có --reason; không có file đã theo dõi bị sửa (trừ
outputs/ và audit/test_access_log.csv — do chính đánh giá cuối ghi, để chạy tiếp seed còn thiếu sau khi bị ngắt); không
có file mã nguồn chưa theo dõi trong src/, scripts/, configs/; audit/v2/best_configs.json đủ mọi mô hình; mã băm mã nguồn
hiện tại trùng mã băm ghi trong audit/v2/tuning_log.csv (cùng mã nguồn với lúc tinh chỉnh); seed chưa có trong
audit/test_access_log.csv (trừ khi --allow-rerun). Mỗi seed ghi một dòng nhật ký TRƯỚC khi chấm.

Mỗi seed: mạng nơ-ron chọn số epoch trên tập xác thực của B (dừng sớm như lúc tinh chỉnh) rồi huấn luyện lại từ đầu
trên mọi cặp trước mốc kiểm thử đúng số epoch đó; BPR-MF và các mô hình không phải mạng nơ-ron khớp trên mọi cặp trước
mốc kiểm thử; LateFusion-F trộn GMF-F và MLP-F của cùng seed. Ablation NeuMF-F chỉ chạy ở seed 42 (mô tả). Mỗi mô hình
được chấm hai lần: tập ứng viên đầy đủ (kết quả chính) và chỉ sản phẩm cũ (phân tích độ nhạy).

Ra outputs/v2/final/: data.json, items.csv.gz và seed<N>/{results.json, per_user.csv.gz, per_user_old.csv.gz,
history.csv}; seed 42 thêm topk.json.gz và checkpoint mạng nơ-ron (*.pt).
--dry-run dùng mẫu A, giai đoạn xác thực đóng cả vai chọn epoch lẫn chấm, ghi ra outputs/v2/dry_run/, không ghi nhật ký
kiểm thử: chỉ để kiểm tra đường ống chạy trọn vẹn, số liệu không có ý nghĩa.
"""
from __future__ import annotations

import os

os.environ.setdefault("TQDM_DISABLE", "1")

import argparse
import csv
import gzip
import json
import platform
import re
import subprocess
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

import v2_common as V
from src.baselines import RandomBaseline
from src.data_pipeline.protocol_v2 import describe
from src.evaluation.full_ranking import build_full_ranking_records_multi
from src.evaluation.v2 import evaluate_v2
from src.utils.io import ensure_dir, log_test_access, prereg_committed

MODELS = ["random", "popularity", "recent_pop", "content", "itemknn", "userknn", "bpr",
          "gmf", "mlp", "neumf", "gmf_f", "mlp_f", "neumf_f", "late_f"]
STATIC = ("popularity", "recent_pop", "content", "itemknn", "userknn")  # tất định: khớp một lần, dùng cho mọi seed
NEURAL = V.TORCH_ID + V.TORCH_FEAT
TUNED = [m for m in MODELS if m != "random"]
ABLATION_SEED = TOPK_SEED = 42
PER_USER_COLS = ["user", "n_candidates", "n_positives", "n_new", "ranks", "new_flags", "NDCG@10", "Recall@10", "HR@10",
                 "Precision@10", "NDCG@5", "NDCG@20", "NDCG@10_old", "NDCG@10_new"]
PER_USER_OLD_COLS = ["user", "n_positives", "ranks", "NDCG@10", "Recall@10", "HR@10"]
PREREG = V.PROJECT_ROOT / "audit" / "PREREG_v2.md"
TEST_LOG = V.PROJECT_ROOT / "audit" / "test_access_log.csv"
RUN_TAG = "v2_final_seed"


def git(*a) -> str:
    try:
        return subprocess.run(["git", *a], cwd=V.PROJECT_ROOT, capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def cpu_name() -> str:
    """Tên thương mại của CPU (platform.processor() trên Windows chỉ cho dạng 'Intel64 Family 6 ...')."""
    try:
        if platform.system() == "Windows":
            import winreg

            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as k:
                return str(winreg.QueryValueEx(k, "ProcessorNameString")[0]).strip()
        info = Path("/proc/cpuinfo")
        if info.exists():
            for line in info.read_text(encoding="utf-8", errors="ignore").splitlines():
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine()


def machine_info(dev) -> dict:
    gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    return dict(device=str(dev), cpu=cpu_name(), gpu=gpu, cpu_count=os.cpu_count(), python=platform.python_version(),
                torch=torch.__version__, os=platform.platform())


def dirty_files() -> list[str]:
    """File đã theo dõi đang bị sửa/xoá mà chưa commit, trừ outputs/ và audit/test_access_log.csv của dự án (do chính
    đánh giá cuối ghi ra) — mã nguồn, cấu hình, kế hoạch, báo cáo đều phải sạch."""
    prefix = git("rev-parse", "--show-prefix").strip()  # vd. "neumf_project/"
    allowed = (prefix + "outputs/", prefix + "audit/test_access_log.csv")
    out = []
    for line in git("status", "--porcelain", "--untracked-files=no").splitlines():
        path = line[3:].split(" -> ")[-1].strip().strip('"')
        if path and not path.startswith(allowed):
            out.append(path)
    return out


def opened_seeds() -> set[int]:
    """Seed đã mở tập kiểm thử v2 (theo audit/test_access_log.csv)."""
    if not TEST_LOG.exists():
        return set()
    with TEST_LOG.open(encoding="utf-8") as f:
        tags = [r.get("run_tag", "") for r in csv.DictReader(f)]
    return {int(m.group(1)) for t in tags if (m := re.match(rf"^{RUN_TAG}(\d+)", t))}


def tuning_code_hashes() -> set[str]:
    p = V.AUDIT / "tuning_log.csv"
    if not p.exists():
        return set()
    with p.open(encoding="utf-8") as f:
        return {r.get("code_hash", "") for r in csv.DictReader(f)}


def lock_errors(args, prov: dict, best: dict) -> list[str]:
    errs = []
    if not prereg_committed(PREREG):
        errs.append("audit/PREREG_v2.md chưa commit (hoặc đang bị sửa)")
    if not args.reason.strip():
        errs.append("thiếu --reason (ghi vào audit/test_access_log.csv)")
    dirty = dirty_files()
    if dirty:
        errs.append("có file đã theo dõi chưa commit — commit trước để kết quả truy vết được: "
                    + ", ".join(dirty[:8]) + (" ..." if len(dirty) > 8 else ""))
    untracked = [f for f in git("ls-files", "--others", "--exclude-standard", "--", "src", "scripts", "configs").split()
                 if f.endswith((".py", ".yaml", ".yml"))]
    if untracked:
        errs.append("file mã nguồn chưa theo dõi: " + ", ".join(untracked))
    missing = [m for m in TUNED if m not in best]
    if missing:
        errs.append("chưa tinh chỉnh xong: " + ", ".join(missing))
    hashes = tuning_code_hashes()
    if hashes != {prov["code_hash"]} and not args.allow_code_change:
        errs.append(f"mã nguồn khác lúc tinh chỉnh (tinh chỉnh: {sorted(hashes)}, hiện tại: {prov['code_hash']}); "
                    "nếu thay đổi không ảnh hưởng kết quả, chạy với --allow-code-change và ghi lý do vào PREREG_v2 mục 10")
    again = sorted(set(args.seeds) & opened_seeds())
    if again and not args.allow_rerun:
        errs.append(f"seed {again} đã mở tập kiểm thử v2 — chỉ chạy lại với --allow-rerun và ghi vào PREREG_v2 mục 10")
    if args.max_epochs != V.CFG["training"]["max_epochs"] or args.models or args.skip_ablation:
        errs.append("--max-epochs/--models/--skip-ablation chỉ dùng với --dry-run")
    return errs


def old_only_records(stage, D):
    """Phân tích độ nhạy: ứng viên và sản phẩm đúng chỉ gồm sản phẩm cũ (có dữ liệu huấn luyện của giai đoạn)."""
    t = stage.targets[stage.scoreable[stage.targets["item"].to_numpy()]]
    return build_full_ranking_records_multi(t, D.n_items, stage.train_pos, item_pool=np.flatnonzero(stage.scoreable))


def beyond(top: dict, stage, k: int = 10) -> dict:
    """Mô tả danh sách top-k: độ phủ tập ứng viên và tỉ lệ sản phẩm mới trong top-k."""
    lists = [np.asarray(v[:k], dtype=np.int64) for v in top.values()]
    shown = np.unique(np.concatenate(lists)) if lists else np.empty(0, np.int64)
    return {f"coverage@{k}": len(shown) / max(int((stage.scoreable | stage.new).sum()), 1),
            f"new_share@{k}": float(np.mean([stage.new[v].mean() for v in lists])) if lists else float("nan")}


class Runner:
    def __init__(self, args, D, sel, ev, best, prov, root, dev):
        self.args, self.D, self.sel, self.ev, self.best, self.prov, self.root, self.dev = \
            args, D, sel, ev, best, prov, root, dev
        self.old_records = old_only_records(ev, D)
        self.kw = V.eval_kw()
        self.static = {}

    def params(self, model: str) -> dict:
        if model in self.best:
            return self.best[model]["params"]
        if not self.args.dry_run:
            raise SystemExit(f"Thiếu cấu hình của {model} trong audit/v2/best_configs.json")
        return dict(V.DEFAULTS.get(model, {}))  # chạy thử khi tinh chỉnh chưa xong

    def evaluate(self, scorer, want_top: bool):
        per, per_old, top = [], [], ({} if want_top else None)
        t0 = time.perf_counter()
        res = evaluate_v2(scorer, self.ev.records, self.ev.new, device=self.dev, per_user=per, topk=top, **self.kw)
        res_old = evaluate_v2(scorer, self.old_records, self.ev.new, device=self.dev, per_user=per_old, **self.kw)
        return dict(res=res, res_old=res_old, per=per, per_old=per_old, top=top,
                    eval_time_s=time.perf_counter() - t0)

    def static_scores(self, model: str) -> dict:
        if model not in self.static:  # tất định -> tính một lần cho mọi seed của lần chạy này
            t0 = time.perf_counter()
            scorer = V.score_fn(model, self.params(model), self.D, self.ev)
            fit_s = time.perf_counter() - t0
            self.static[model] = {**self.evaluate(scorer, want_top=True), "fit_time_s": fit_s}
        return self.static[model]

    def run_seed(self, seed: int, models: list[str]):
        a = self.args
        if not a.dry_run:
            tag = f"{RUN_TAG}{seed}" + ("_rerun" if seed in opened_seeds() else "")
            names = [V.DISPLAY[m] for m in models]
            if seed == ABLATION_SEED and not a.skip_ablation and "neumf_f" in models:
                names += [V.ABLATION_DISPLAY[k] for k in V.ABLATIONS]
            log_test_access(TEST_LOG, tag, self.prov, names, a.reason)
            if a.mirror_log:  # bản sao nhật ký ngoài máy chạy (vd. Google Drive) phòng máy ảo bị ngắt
                log_test_access(Path(a.mirror_log), tag, self.prov, names, a.reason)
        out = ensure_dir(self.root / f"seed{seed}")
        want_top = seed == TOPK_SEED
        results, results_old, rows, rows_old, topk, meta, hist, beyond_k = {}, {}, [], [], {}, {}, [], {}
        nets = {}
        t_seed = time.perf_counter()

        def record(name: str, r: dict, extra: dict):
            results[name], results_old[name] = r["res"], r["res_old"]
            rows.extend({"model": name, "seed": seed, **{c: u.get(c) for c in PER_USER_COLS}} for u in r["per"])
            rows_old.extend({"model": name, "seed": seed, **{c: u.get(c) for c in PER_USER_OLD_COLS}}
                            for u in r["per_old"])
            if want_top and r["top"] is not None:
                topk[name] = {str(u): items for u, items in r["top"].items()}
                beyond_k[name] = beyond(r["top"], self.ev)
            meta[name] = {**meta.get(name, {}), **extra, "eval_time_s": round(r["eval_time_s"], 1)}
            res = r["res"]
            print(f"[seed {seed}] {V.DISPLAY.get(name, name):26s} NDCG@10 {res['NDCG@10']:.5f} "
                  f"(cũ {res['NDCG@10_old']:.5f} / mới {res['NDCG@10_new']:.5f}) | chỉ SP cũ "
                  f"{r['res_old']['NDCG@10']:.5f}", flush=True)

        def score(name: str, scorer, **extra):
            record(name, self.evaluate(scorer, want_top), extra)

        def select_refit(key: str, p: dict):
            """Chọn số epoch e* trên tập xác thực (dừng sớm), rồi huấn luyện lại từ đầu trên mọi cặp trước mốc chấm."""
            _, h_sel, m_sel = V.fit_torch(key, p, self.D, self.sel, self.sel, a.max_epochs,
                                          V.CFG["training"]["patience"], seed, self.dev)
            e = int(m_sel["best_epoch"])
            net, h_ref, m_ref = V.fit_torch(key, p, self.D, self.ev, None, e, e, seed, self.dev)
            hist.extend({"model": key, "phase": "select", **h} for h in h_sel)
            hist.extend({"model": key, "phase": "refit", **h} for h in h_ref)
            if want_top and key in NEURAL:  # checkpoint của seed 42 cho demo và phân tích lại
                torch.save({k: v.cpu() for k, v in net.state_dict().items()}, out / f"{key}.pt")
            return net, dict(best_epoch=e, select_val_ndcg10=m_sel["best_metric"],
                             select_time_s=round(m_sel["train_time_s"], 1), refit_time_s=round(m_ref["train_time_s"], 1),
                             n_parameters=m_ref["n_parameters"])

        for m in models:
            if m in STATIC:
                s = self.static_scores(m)
                record(m, s, dict(fit_time_s=round(s["fit_time_s"], 1)))
            elif m == "random":
                score(m, RandomBaseline(seed=seed))
            elif m == "bpr":
                t0 = time.perf_counter()
                bpr = V.score_fn("bpr", self.params("bpr"), self.D, self.ev, seed=seed)
                fit_s = round(time.perf_counter() - t0, 1)
                if want_top:  # checkpoint của seed 42 cho demo (MaskedScoreFn bọc BPRMFBaseline ở thuộc tính fn)
                    bpr.fn.save(out / "bpr.npz")
                score(m, bpr, fit_time_s=fit_s)
            elif m in NEURAL:
                net, info = select_refit(m, self.params(m))
                nets[m] = V.torch_scorer(m, net, self.ev, self.D, self.dev)
                score(m, nets[m], **info)
            elif m == "late_f":
                missing = [k for k in V.LATE_PARTS if k not in nets]
                if missing:
                    raise SystemExit(f"late_f cần {missing} trong cùng lần chạy")
                score(m, V.late_fusion(nets, self.params("late_f")["w"]), w=self.params("late_f")["w"])
        if seed == ABLATION_SEED and not a.skip_ablation and "neumf_f" in models:
            for key in V.ABLATIONS:  # cùng siêu tham số với NeuMF-F, tắt một thành phần
                net, info = select_refit(key, self.params("neumf_f"))
                score(key, V.torch_scorer(key, net, self.ev, self.D, self.dev), **info)

        pd.DataFrame(rows).to_csv(out / "per_user.csv.gz", index=False)
        pd.DataFrame(rows_old).to_csv(out / "per_user_old.csv.gz", index=False)
        pd.DataFrame(hist).to_csv(out / "history.csv", index=False)
        if want_top:
            with gzip.open(out / "topk.json.gz", "wt", encoding="utf-8") as f:
                json.dump(topk, f)
        payload = dict(
            seed=seed, evaluated_on="dry-run: tập xác thực của mẫu A" if a.dry_run else "tập kiểm thử của mẫu B",
            reason=a.reason, provenance={**self.prov, "tuning_code_hashes": sorted(tuning_code_hashes())},
            machine=machine_info(self.dev),
            elapsed_min=round((time.perf_counter() - t_seed) / 60, 1),
            results=results, results_old_only=results_old, beyond=beyond_k, train_meta=meta,
            configs={m: self.params(m) for m in models if m != "random"})
        (out / "results.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=float),
                                          encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reason", default="")
    ap.add_argument("--seeds", type=int, nargs="+", default=V.CFG["final"]["seeds"])
    ap.add_argument("--out", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-epochs", type=int, default=V.CFG["training"]["max_epochs"])
    ap.add_argument("--models", nargs="+", choices=MODELS, help="chỉ với --dry-run")
    ap.add_argument("--skip-ablation", action="store_true", help="chỉ với --dry-run")
    ap.add_argument("--allow-rerun", action="store_true", help="chạy lại seed đã mở tập kiểm thử (lệch kế hoạch)")
    ap.add_argument("--allow-code-change", action="store_true", help="mã nguồn khác lúc tinh chỉnh (lệch kế hoạch)")
    ap.add_argument("--mirror-log", default="", help="ghi thêm mỗi dòng nhật ký truy cập test vào file này (vd. Drive)")
    args = ap.parse_args()

    best_path = V.AUDIT / "best_configs.json"
    best = json.loads(best_path.read_text(encoding="utf-8")) if best_path.exists() else {}
    prov = V.provenance()
    if not args.dry_run:
        errs = lock_errors(args, prov, best)
        if errs:
            raise SystemExit("Khoá kiểm thử v2 — không chạy:\n  - " + "\n  - ".join(errs))
    models = [m for m in MODELS if not args.models or m in args.models]
    if "late_f" in models:
        models += [k for k in V.LATE_PARTS if k not in models]
        models = [m for m in MODELS if m in models]

    t0 = time.time()
    if args.dry_run:
        D = V.load_data("dev")
        sel = ev = D.val
        root = ensure_dir(Path(args.out or V.PROJECT_ROOT / "outputs" / "v2" / "dry_run"))
    else:
        D = V.load_data("holdout", with_test=True)
        sel, ev = D.val, D.test
        root = ensure_dir(Path(args.out or V.PROJECT_ROOT / "outputs" / "v2" / "final"))
    dev = V.device()
    info = describe(D)
    (root / "data.json").write_text(json.dumps(dict(sample=D.meta["sample"], **info), indent=2, ensure_ascii=False),
                                    encoding="utf-8")
    pd.DataFrame(dict(item=np.arange(D.n_items), article_id=D.item_article, has_id=np.arange(D.n_items) < D.n_id_items,
                      scoreable=ev.scoreable, new=ev.new)).to_csv(root / "items.csv.gz", index=False)
    print(f"{'CHẠY THỬ (A, xác thực)' if args.dry_run else 'ĐÁNH GIÁ CUỐI (B, kiểm thử)'}: {D.n_users:,} người dùng, "
          f"{D.n_items:,} sản phẩm | chấm {len(ev.records):,} người dùng, {len(ev.targets):,} cặp đúng "
          f"({int(ev.new[ev.targets['item'].to_numpy()].sum()):,} sản phẩm mới) | commit {prov['git_commit']} "
          f"code {prov['code_hash']} ({time.time() - t0:.0f}s)", flush=True)

    runner = Runner(args, D, sel, ev, best, prov, root, dev)
    for seed in args.seeds:
        t1 = time.time()
        runner.run_seed(seed, models)
        print(f"==> seed {seed} xong ({(time.time() - t1) / 60:.1f} phút)", flush=True)


if __name__ == "__main__":
    main()
