"""Bổ sung sau đánh giá cuối: mô hình lai truyền thống Hybrid-CBCF (audit/PREREG_bosung.md).

    python scripts/25_bosung.py tune                     # H&M: chọn cách kết hợp trên tập xác thực của mẫu phát triển
    python scripts/25_bosung.py final --dry-run          # thử đường ống trên tập xác thực của mẫu phát triển
    python scripts/25_bosung.py final --reason "..."     # chấm tập kiểm thử một lần (H&M: mẫu kiểm định)
    NEUMF_CONFIG=configs/amazon.yaml python scripts/25_bosung.py final --reason "..."   # Amazon: cách chọn trên H&M

Theo góp ý của GVHD (họp 04/10/2026: baseline ba nhóm), một mô hình lai truyền thống được thêm vào nhóm học máy truyền
thống sau khi đánh giá cuối của 14 mô hình đã xong. Hybrid-CBCF kết hợp ba baseline đã tinh chỉnh — Content, UserKNN,
ItemKNN, cấu hình giữ nguyên như audit/v2/best_configs.json — theo mô hình lai trong luận án của GVHD
(src/baselines/hybrid.py).

tune (chỉ H&M): thử 4 cách kết hợp trên tập xác thực của mẫu phát triển — trung bình, max, min, trọng số học bằng hồi quy
logistic theo cặp (khớp chéo hai phần theo khách để số xác thực không lạc quan; trọng số dùng về sau học trên toàn bộ tập
xác thực) — ghi audit/v2/bosung_tuning_log.csv và cách có NDCG@10 cao nhất vào audit/v2/bosung_best_configs.json. Không
dựng tập kiểm thử.

final: mô hình tất định nên chấm một lần, dùng cho mọi seed. Khoá kiểm thử như 23_final_v2.py: audit/PREREG_bosung.md đã
commit; có --reason; không có file đã theo dõi bị sửa (trừ outputs/ và audit/test_access_log.csv); không có file mã nguồn
chưa theo dõi trong src/, scripts/, configs/; đã tinh chỉnh; mã băm mã nguồn trùng lúc tinh chỉnh (H&M); run_tag
bosung_hybrid_<bộ dữ liệu> chưa có trong audit/test_access_log.csv (trừ khi --allow-rerun). Ghi nhật ký TRƯỚC khi chấm.
Ba thành phần được chấm lại cùng lúc để đối chiếu với lần đánh giá cuối đã đăng ký (hạng từng khách trong
seed42/per_user.csv.gz).
Ra <out_dir>/final/bosung/ (dry-run: <out_dir>/dry_run/bosung/): results.json, per_user.csv.gz (cột như 23_final_v2.py,
một bản cho mỗi seed của đánh giá cuối vì mô hình tất định), topk.json.gz.
"""
from __future__ import annotations

import os

os.environ.setdefault("TQDM_DISABLE", "1")

import argparse
import csv
import gzip
import hashlib
import importlib.util
import json
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

import v2_common as V
from src.baselines.hybrid import (C_REG, COMPONENTS, FUSIONS, N_NEG, PAIR_SEED, TraditionalHybrid, combine,
                                  crossfit_scores, fit_weights)
from src.evaluation.v2 import evaluate_v2
from src.utils.io import ensure_dir, log_test_access, prereg_committed


def _script(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


F = _script("final_v2", "23_final_v2.py")  # khoá kiểm thử, thông tin máy, cột per_user, độ phủ — dùng chung
T = _script("tune_v2", "22_tune_v2.py")  # ghi / đọc nhật ký tinh chỉnh

MODEL = "hybrid"
PREREG = V.PROJECT_ROOT / "audit" / "PREREG_bosung.md"
BEST = V.BEST_CONFIGS.with_name("bosung_best_configs.json")  # audit/v2/ — Amazon dùng đúng file của H&M
LOG = V.AUDIT / "bosung_tuning_log.csv"
RUN_TAG = f"bosung_hybrid_{V.DATASET}"
NAMES = [V.DISPLAY[MODEL], *(V.DISPLAY[k] for k in COMPONENTS)]


class Precomputed:
    """score_items trả điểm đã tính sẵn của khách (cùng thứ tự với record.candidates)."""

    def __init__(self, records, scores):
        self.by_user = {int(r.user): s for r, s in zip(records, scores)}

    def score_items(self, user, items):
        return self.by_user[int(user)]


def file_md5(rel: str) -> str:
    h = hashlib.md5()
    with (V.PROJECT_ROOT / rel).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def provenance() -> dict:
    """V.provenance() + MD5 của tệp đặc trưng (không nằm trong git, mỗi máy tự dựng — Content dùng vector văn bản)."""
    f = V.CFG["features"]
    return {**V.provenance(), "feature_md5": {k: file_md5(f[k]) for k in ("catalog", "sales")}}


# ------------------------------------------------------------------ tinh chỉnh
def tune(args) -> None:
    if not V.TUNED_HERE:
        raise SystemExit(f"{V.NAME} không tinh chỉnh — dùng cách kết hợp chọn trên H&M ({BEST.name}, "
                         "PREREG_bosung mục 3).")
    t0 = time.time()
    D = V.load_data("dev", with_test=False)
    other = [r for r in T.logged(LOG) if r.get("data_md5") != D.meta["data_md5"]]
    if other:
        raise SystemExit(f"{LOG} có {len(other)} dòng trên dữ liệu khác (data_md5) — chuyển đi rồi chạy lại.")
    st, seed = D.val, V.CFG["tuning"]["seed"]
    reg = json.loads(V.BEST_CONFIGS.read_text(encoding="utf-8"))
    prov = provenance()
    hyb = TraditionalHybrid(V.hybrid_components(reg, D, st), "mean")
    feats = [hyb.features(r.user, r.candidates) for r in st.records]
    labels = [np.isin(r.candidates, r.positives) for r in st.records]
    users = [r.user for r in st.records]
    comps = ", ".join(f"{k} {reg[k]['params']}" for k in COMPONENTS)
    print(f"[{V.NAME}] mẫu phát triển, tập xác thực: {len(st.records):,} người dùng, {len(st.targets):,} cặp đúng | "
          f"thành phần {comps} | code {prov['code_hash']} "
          f"({time.time() - t0:.0f}s)", flush=True)
    # Ba thành phần đứng riêng trên cùng máy, cùng tệp đặc trưng (min–max không đổi thứ tự): để đặt cạnh các cách kết
    # hợp; Content có thể lệch nhẹ so với lần tinh chỉnh đã đăng ký (PREREG_bosung mục 3).
    parts = {}
    for j, k in enumerate(COMPONENTS):
        res = V.evaluate(Precomputed(st.records, [x[:, j] for x in feats]), st, "cpu")
        parts[k] = {c: float(res[c]) for c in V.METRICS}
        print(f"    {V.DISPLAY[k]:8s} đứng riêng: NDCG@10 {res['NDCG@10']:.5f} (lần tinh chỉnh đã đăng ký "
              f"{reg[k]['val']['NDCG@10']:.5f})", flush=True)
    rows = []
    for cid, fusion in enumerate(FUSIONS):
        t1 = time.time()
        p = {"fusion": fusion}
        if fusion == "lr":  # số xác thực: khớp chéo theo khách; trọng số lưu lại: học trên toàn bộ tập xác thực
            scores, w_fold = crossfit_scores(feats, labels, users)
            p["weights"] = [round(float(x), 6) for x in fit_weights(feats, labels)]
            print(f"    trọng số theo phần: {({f: np.round(w, 4).tolist() for f, w in w_fold.items()})}", flush=True)
        else:
            scores = [combine(x, fusion) for x in feats]
        metrics = V.evaluate(Precomputed(st.records, scores), st, "cpu")
        key = json.dumps(p, sort_keys=True)
        row = dict(timestamp=datetime.now().isoformat(timespec="seconds"), model=MODEL, config_id=cid, params=key,
                   config_hash=hashlib.sha256(f"{MODEL}{key}{seed}".encode()).hexdigest()[:16],
                   git_commit=prov["git_commit"], git_dirty=prov["git_dirty"], code_hash=prov["code_hash"],
                   data_md5=D.meta["data_md5"], feature_md5=prov["feature_md5"]["catalog"], seed=seed,
                   time_s=round(time.time() - t1, 1), **{f"val_{k}": round(metrics[k], 6) for k in V.METRICS})
        T.log_row(LOG, row)
        rows.append((metrics, p, row))
        print(f"[{MODEL} {cid + 1}/{len(FUSIONS)}] {key} -> NDCG@10 {metrics['NDCG@10']:.5f} ({row['time_s']:.0f}s)",
              flush=True)
    metrics, p, row = max(rows, key=lambda t: t[0]["NDCG@10"])
    best = json.loads(BEST.read_text(encoding="utf-8")) if BEST.exists() else {}
    best[MODEL] = dict(params=p, config_hash=row["config_hash"], code_hash=row["code_hash"],
                       data_md5=row["data_md5"], feature_md5=prov["feature_md5"],
                       val={k: float(metrics[k]) for k in V.METRICS},
                       components={k: reg[k]["params"] for k in COMPONENTS}, components_val=parts,
                       pairwise=dict(n_neg=N_NEG, seed=PAIR_SEED, C=C_REG, folds=2))
    BEST.write_text(json.dumps(best, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"==> {V.DISPLAY[MODEL]} tốt nhất: {p} NDCG@10 {metrics['NDCG@10']:.5f} -> {BEST.name} "
          f"({(time.time() - t0) / 60:.1f} phút)", flush=True)


# ------------------------------------------------------------------ đánh giá cuối
def opened_tags() -> set[str]:
    if not F.TEST_LOG.exists():
        return set()
    with F.TEST_LOG.open(encoding="utf-8") as f:
        return {r.get("run_tag", "") for r in csv.DictReader(f)}


def lock_errors(args, prov: dict, hb: dict | None) -> list[str]:
    errs = []
    if not prereg_committed(PREREG):
        errs.append(f"{PREREG.relative_to(V.PROJECT_ROOT).as_posix()} chưa commit (hoặc đang bị sửa)")
    if not args.reason.strip():
        errs.append("thiếu --reason (ghi vào audit/test_access_log.csv)")
    dirty = F.dirty_files()
    if dirty:
        errs.append("có file đã theo dõi chưa commit — commit trước để kết quả truy vết được: "
                    + ", ".join(dirty[:8]) + (" ..." if len(dirty) > 8 else ""))
    untracked = [f for f in F.git("ls-files", "--others", "--exclude-standard", "--", "src", "scripts", "configs").split()
                 if f.endswith((".py", ".yaml", ".yml"))]
    if untracked:
        errs.append("file mã nguồn chưa theo dõi: " + ", ".join(untracked))
    if hb is None:
        errs.append(f"chưa tinh chỉnh {V.DISPLAY[MODEL]} — chạy `python scripts/25_bosung.py tune` (H&M) trước")
    elif not all(prereg_committed(p) for p in (BEST, *([LOG] if V.TUNED_HERE else []))):
        errs.append(f"kết quả tinh chỉnh ({BEST.name}, {LOG.name}) chưa commit")
    elif V.TUNED_HERE and hb.get("code_hash") != prov["code_hash"] and not args.allow_code_change:
        errs.append(f"mã nguồn khác lúc tinh chỉnh (tinh chỉnh: {hb.get('code_hash')}, hiện tại: {prov['code_hash']}); "
                    f"chỉ chạy với --allow-code-change và ghi vào {PREREG.name} (mục lệch kế hoạch)")
    if RUN_TAG in opened_tags() and not args.allow_rerun:
        errs.append(f"{RUN_TAG} đã mở tập kiểm thử — chỉ chạy lại với --allow-rerun và ghi vào {PREREG.name} (mục lệch "
                    "kế hoạch)")
    return errs


def component_check(comps, ev, old: pd.DataFrame | None) -> dict:
    """Chấm lại ba thành phần trên cùng giai đoạn; so hạng của từng khách với lần đánh giá cuối đã đăng ký (nếu có)."""
    out = {}
    for k, c in zip(COMPONENTS, comps):
        per = []
        res = evaluate_v2(c, ev.records, per_user=per, **V.eval_kw())
        entry = {"NDCG@10": res["NDCG@10"]}
        if old is not None and (old["model"] == k).any():
            o = old[old["model"] == k].set_index("user")
            now = pd.Series({int(u["user"]): str(u["ranks"]) for u in per})
            entry.update(registered_NDCG10=float(o["NDCG@10"].mean()), users=len(now),
                         users_same_ranks=int((o["ranks"].astype(str).reindex(now.index) == now).sum()))
        out[k] = entry
        print(f"    thành phần {V.DISPLAY[k]:8s} NDCG@10 {res['NDCG@10']:.5f}"
              + (f" (đánh giá cuối đã đăng ký {entry['registered_NDCG10']:.5f}; trùng hạng "
                 f"{entry['users_same_ranks']}/{entry['users']} khách)" if "users" in entry else ""), flush=True)
    return out


def final(args) -> None:
    hb = (json.loads(BEST.read_text(encoding="utf-8")) if BEST.exists() else {}).get(MODEL)
    prov = provenance()
    if not args.dry_run:
        errs = lock_errors(args, prov, hb)
        if errs:
            raise SystemExit(f"Khoá kiểm thử ({V.NAME}, bổ sung) — không chạy:\n  - " + "\n  - ".join(errs))
    elif hb is None:
        raise SystemExit(f"chưa tinh chỉnh {V.DISPLAY[MODEL]} — chạy `python scripts/25_bosung.py tune` trước")
    t0 = time.time()
    if args.dry_run:
        D = V.load_data("dev")
        ev, registered = D.val, V.OUT / "dry_run"
    else:
        D = V.load_data("holdout", with_test=True)
        ev, registered = D.test, V.OUT / "final"
        info = json.loads((registered / "data.json").read_text(encoding="utf-8"))
        if info.get("data_md5") != D.meta["data_md5"]:
            raise SystemExit(f"{registered}/data.json là dữ liệu khác (data_md5 {info.get('data_md5')} ≠ "
                             f"{D.meta['data_md5']}) — kết quả bổ sung phải trên đúng tập kiểm thử của đánh giá cuối.")
    root = ensure_dir(Path(args.out) if args.out else registered / "bosung")
    reg = json.loads(V.BEST_CONFIGS.read_text(encoding="utf-8"))
    print(f"[{V.NAME}] {'CHẠY THỬ (phát triển, xác thực)' if args.dry_run else 'BỔ SUNG — ĐÁNH GIÁ CUỐI (kiểm thử)'}: "
          f"{V.DISPLAY[MODEL]} {hb['params']} | chấm {len(ev.records):,} người dùng, {len(ev.targets):,} cặp đúng | "
          f"commit {prov['git_commit']} code {prov['code_hash']} ({time.time() - t0:.0f}s)", flush=True)
    if not args.dry_run:
        tag = RUN_TAG + ("_rerun" if RUN_TAG in opened_tags() else "")
        log_test_access(F.TEST_LOG, tag, prov, NAMES, args.reason)
    t1 = time.perf_counter()
    comps = V.hybrid_components(reg, D, ev)
    fit_s = time.perf_counter() - t1
    model = TraditionalHybrid(comps, hb["params"]["fusion"], hb["params"].get("weights"))
    per, top = [], {}
    t2 = time.perf_counter()
    res = evaluate_v2(model, ev.records, per_user=per, topk=top, **V.eval_kw())
    eval_s = time.perf_counter() - t2
    print(f"    {V.DISPLAY[MODEL]:8s} NDCG@10 {res['NDCG@10']:.5f}  HR@10 {res['HR@10']:.5f}", flush=True)
    old_path = registered / f"seed{F.TOPK_SEED}" / "per_user.csv.gz"
    check = component_check(comps, ev, None if args.dry_run or not old_path.exists() else pd.read_csv(old_path))

    seeds = V.CFG["final"]["seeds"]
    pd.DataFrame([{"model": MODEL, "seed": s, **{c: u.get(c) for c in F.PER_USER_COLS}} for s in seeds for u in per]
                 ).to_csv(root / "per_user.csv.gz", index=False)
    with gzip.open(root / "topk.json.gz", "wt", encoding="utf-8") as f:
        json.dump({str(u): items for u, items in top.items()}, f)
    payload = dict(
        model=MODEL, name=V.DISPLAY[MODEL], dataset=V.DATASET, seeds=seeds,
        evaluated_on="dry-run: tập xác thực của mẫu phát triển" if args.dry_run else (
            "tập kiểm thử của mẫu kiểm định" if V.DATASET == "hm" else f"tập kiểm thử {V.NAME}"),
        reason=args.reason, run_tag=None if args.dry_run else RUN_TAG,
        provenance={**prov, "data_md5": D.meta["data_md5"], "configs_from": BEST.relative_to(V.PROJECT_ROOT).as_posix(),
                    "components_from": V.BEST_CONFIGS.relative_to(V.PROJECT_ROOT).as_posix()},
        machine=F.machine_info("cpu"), date=datetime.now().isoformat(timespec="seconds"),
        elapsed_min=round((time.time() - t0) / 60, 1), config=hb, results={MODEL: res},
        beyond={MODEL: F.beyond(top, ev)}, train_meta={MODEL: dict(fit_time_s=round(fit_s, 1),
                                                                   eval_time_s=round(eval_s, 1))},
        components_check=check)
    (root / "results.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=float),
                                       encoding="utf-8")
    print(f"==> ghi {root} ({(time.time() - t0) / 60:.1f} phút)", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("tune", help="chọn cách kết hợp trên tập xác thực của mẫu phát triển (H&M)")
    p = sub.add_parser("final", help="đánh giá một lần trên tập kiểm thử (hoặc --dry-run trên tập xác thực)")
    p.add_argument("--reason", default="")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--out", default=None)
    p.add_argument("--allow-rerun", action="store_true", help="đã mở tập kiểm thử với run_tag này (lệch kế hoạch)")
    p.add_argument("--allow-code-change", action="store_true", help="mã nguồn khác lúc tinh chỉnh (lệch kế hoạch)")
    args = ap.parse_args()
    (tune if args.cmd == "tune" else final)(args)


if __name__ == "__main__":
    main()
