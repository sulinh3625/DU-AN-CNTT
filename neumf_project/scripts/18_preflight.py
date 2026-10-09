"""Kiểm tra sẵn sàng TRƯỚC khi chạy lại chuỗi đánh giá cuối v1 (README.md mục 7) — không chấm test.

    python scripts/18_preflight.py                    # đầy đủ (khoảng 3–4 phút)
    python scripts/18_preflight.py --quick            # bỏ dựng lại dữ liệu và kiểm tra tái lập tuning mở rộng
    python scripts/18_preflight.py --extension-only   # trước 17_extension.py khi không chạy lại 11_final.py

Dừng với mã lỗi 1 nếu một điều kiện bắt buộc không đạt (các khoá test của 11/14/17 cũng sẽ từ chối chạy):
  1. Working tree sạch (mọi file đã theo dõi đã commit) — 11_final.py từ chối khi tree bẩn.
  2. audit/PREREG.md đã commit và có mục 9 (mở rộng) — 17_extension.py đòi.
  3. audit/best_configs.json có đủ 5 mô hình chính + 4 mô hình mở rộng; checkpoint train-only của thành phần late
     fusion còn trong outputs/tuning/ (nếu mất, 10_tune.py sẽ dựng lại và làm bẩn tree).
  4. Dữ liệu hm500k dựng lại ra đúng kích thước của lần chạy gốc (201.801 / 7.057 / 9.229 cặp, ...).
  5. Tuning mở rộng chạy lại trên CPU (ghi ra outputs/tuning_recheck/, bị .gitignore) cho cùng tập cấu hình và số val
     như audit/ — lệch NDCG@10 quá TOL_NDCG thì code đã đổi, phải xem lại trước khi chấm test; lệch nhỏ hơn (sai khác
     số học giữa máy) chỉ cảnh báo.
Cảnh báo (không dừng): không có GPU, ít dung lượng đĩa, thiếu thư mục báo cáo.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.io import prereg_committed  # noqa: E402

AUDIT = PROJECT_ROOT / "audit"
PREREG_MARKER = "## 9. Mở rộng sau khi xem test"
MAIN_KEYS = ["bpr", "gmf", "mlp", "neumf_scratch", "neumf_pretrained"]
EXT_KEYS = ["itemknn", "userknn", "late_gmf_mlp", "late_bpr_mlp"]
# Kích thước dữ liệu của lần chạy gốc giao thức v1 (29/09/2026, mẫu A, một mốc thời gian chung).
EXPECTED = {"train": 201_801, "val": 7_057, "test": 9_229, "test_users": 2_996, "train_items": 10_145,
            "trva": 209_212, "trva_items": 10_216}
RECHECK_DIR = PROJECT_ROOT / "outputs" / "tuning_recheck"
ORIGINAL_GPU = "RTX 3050"  # GPU của lần chạy 29/09 (outputs/final/final.log)
METRICS = ["NDCG@10", "Recall@10", "HR@10", "Precision@10", "NDCG@5"]
# Một item đúng đổi hạng một bậc làm NDCG@10 val (2.275 user) lệch từ ~1e-5 (giữa danh sách) tới ~1,6e-4 (hạng 1↔2);
# 5e-4 ≈ 5% của NDCG@10 val (~0,01) — đủ rộng cho sai khác số học giữa máy, đủ hẹp để bắt code đổi.
TOL_NDCG = 5e-4


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def ok(self, msg):
        print(f"  [OK]   {msg}", flush=True)

    def fail(self, msg):
        self.errors.append(msg)
        print(f"  [LỖI]  {msg}", flush=True)

    def warn(self, msg):
        self.warnings.append(msg)
        print(f"  [CHÚ Ý] {msg}", flush=True)


def git(*args) -> str:
    # rstrip, không strip: dòng đầu của `git status --porcelain` bắt đầu bằng dấu cách có nghĩa (" M file").
    return subprocess.run(["git", *args], cwd=PROJECT_ROOT, capture_output=True, text=True).stdout.rstrip()


CODE_PATHS = ["src", "scripts", "configs", "audit", "demo", "run.py"]  # vùng mà khoá test của 17_extension.py kiểm tra


def check_git(r: Report) -> None:
    dirty = git("status", "--porcelain", "--untracked-files=no")
    if dirty:
        files = [line[3:] for line in dirty.splitlines() if line.strip()]
        r.fail(f"Working tree có {len(files)} file chưa commit: {', '.join(files[:6])}"
               f"{' ...' if len(files) > 6 else ''} — commit trước (11_final.py từ chối tree bẩn).")
    else:
        r.ok(f"Working tree sạch, commit {git('rev-parse', '--short', 'HEAD')}")
    # 17_extension.py từ chối cả file MỚI chưa git add trong vùng code/audit — phát hiện ngay, đừng để chuỗi dừng sau
    # khi 11_final.py đã chạy 1,5 giờ.
    untracked = [line[3:] for line in git("status", "--porcelain", "--untracked-files=all", "--", *CODE_PATHS)
                 .splitlines() if line.startswith("??") and "__pycache__" not in line]
    if untracked:
        r.fail(f"Có {len(untracked)} file mới chưa git add trong vùng code/audit: {', '.join(untracked[:6])}"
               f"{' ...' if len(untracked) > 6 else ''} — git add + commit (17_extension.py sẽ từ chối).")
    else:
        r.ok("Không có file mới chưa commit trong src/, scripts/, configs/, audit/, demo/")


def check_prereg(r: Report) -> None:
    prereg = AUDIT / "PREREG.md"
    if not prereg_committed(prereg):
        r.fail("audit/PREREG.md chưa commit hoặc đang bị sửa.")
    elif PREREG_MARKER not in prereg.read_text(encoding="utf-8"):
        r.fail(f"audit/PREREG.md chưa có '{PREREG_MARKER}' — 17_extension.py sẽ từ chối.")
    else:
        r.ok("PREREG.md đã commit, có mục 9 (mở rộng)")


def check_configs(r: Report) -> dict:
    path = AUDIT / "best_configs.json"
    best = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    missing = [k for k in MAIN_KEYS + EXT_KEYS if k not in best]
    if missing:
        r.fail(f"best_configs.json thiếu {missing} — chạy 10_tune.py (--model all / --model extension).")
        return best
    r.ok("best_configs.json đủ 5 mô hình chính + 4 mô hình mở rộng")
    lost = [best[k]["checkpoint"] for k in ("gmf", "mlp", "bpr")
            if best[k].get("checkpoint") and not (PROJECT_ROOT / best[k]["checkpoint"]).exists()]
    if lost:
        r.fail(f"Mất checkpoint train-only {lost}: 10_tune.py sẽ huấn luyện lại và ghi audit/ (làm bẩn tree).")
    else:
        r.ok("Checkpoint train-only của GMF, MLP, BPR-MF (thành phần late fusion) còn đủ trong outputs/tuning/")
    return best


def check_final_checkpoints(r: Report) -> None:
    seeds = sorted((PROJECT_ROOT / "outputs" / "final").glob("seed*/results.json"))
    need = ["bpr.npz", "gmf.pt", "mlp.pt", "neumf_scratch.pt", "neumf_pretrained.pt"]
    bad = [p.parent.name for p in seeds if not all((p.parent / f).exists() for f in need)]
    if len(seeds) < 3 or bad:
        r.fail(f"outputs/final/seed*/ chưa đủ 3 seed kèm checkpoint (thiếu ở {bad or 'mọi seed'}) — "
               "17_extension.py cần checkpoint của 11_final.py.")
    else:
        r.ok(f"Checkpoint của 11_final.py có đủ ở {', '.join(p.parent.name for p in seeds)}")


def check_data(r: Report) -> None:
    spec = importlib.util.spec_from_file_location("tune", PROJECT_ROOT / "scripts" / "10_tune.py")
    tune = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tune)
    try:
        _, D = tune.load_data("configs/hm500k_global.yaml", with_test=True)
    except FileNotFoundError as exc:
        r.fail(f"Không đọc được dữ liệu: {exc} — chạy `python run.py sample-hm`. Máy đã chạy trước 02/10 (thư mục cũ "
               "neumf_project_v2/): data/ bị .gitignore nên không theo khi đổi tên thư mục — chép "
               "neumf_project_v2/data/ sang neumf_project/data/.")
        return
    got = {"train": len(D.tr), "val": len(D.va), "test": len(D.te), "test_users": len(D.test),
           "train_items": len(D.pool), "trva": len(D.trva), "trva_items": len(D.test_pool)}
    diff = {k: (EXPECTED[k], v) for k, v in got.items() if v != EXPECTED[k]}
    if diff:
        r.fail(f"Dữ liệu khác lần chạy gốc (gốc, bây giờ): {diff} — kiểm tra file hm500k_transactions.csv.")
    else:
        r.ok("Dữ liệu khớp lần chạy gốc: train 201.801 / val 7.057 / test 9.229 cặp, 2.996 user test, "
             "10.216 item ứng viên")


def compare_extension(old: pd.DataFrame, new: pd.DataFrame, best: dict, again: dict, key: str) -> tuple[str, str]:
    """So tuning mở rộng chạy lại với audit/ cho một mô hình: ("ok" | "warn" | "fail", thông điệp).

    So TỪNG cấu hình (tuning_log.csv), không chỉ cấu hình tốt nhất. Lệch NDCG@10 ≤ TOL_NDCG là sai khác số học giữa
    máy/thiết bị (thứ tự cộng dấu phẩy động làm vài item đúng đổi hạng một bậc) -> chỉ cảnh báo, kể cả khi lần chạy lại
    chọn tham số khác trong phạm vi sai số; 17_extension.py luôn dùng tham số đã đăng ký trong audit/best_configs.json.
    Khác tập cấu hình hoặc lệch lớn hơn -> code đã đổi."""
    cols = [f"val_{m}" for m in METRICS]
    o = old[old["model"] == key].drop_duplicates("params", keep="last").set_index("params")[cols]
    n = new[new["model"] == key].drop_duplicates("params", keep="last").set_index("params")[cols]
    if set(n.index) != set(o.index):
        return "fail", (f"Tuning mở rộng {key} KHÔNG tái lập: tập cấu hình khác audit/ "
                        f"({sorted(set(n.index) ^ set(o.index))[:3]}) — code đã đổi, xem lại trước khi chấm test.")
    gap = (n - o.loc[n.index]).abs()
    gap_ndcg, gap_all = float(gap["val_NDCG@10"].max()), float(gap.to_numpy().max())
    gap_best = max(abs(again[key]["val"][mt] - best[key]["val"][mt]) for mt in METRICS)
    same = again[key]["params"] == best[key]["params"]
    if same and gap_all == 0 and gap_best == 0:
        return "ok", f"Tuning mở rộng {key}: cùng tham số {best[key]['params']}, val khớp tuyệt đối ({len(n)} cấu hình)"
    if gap_ndcg <= TOL_NDCG:
        picked = "" if same else f"; lần chạy lại chọn {again[key]['params']} (chênh nằm trong sai số)"
        return "warn", (f"Tuning mở rộng {key}: val lệch tối đa {gap_all:.1e} (NDCG@10 {gap_ndcg:.1e} ≤ {TOL_NDCG:.0e})"
                        f" — sai khác số học giữa máy, không phải code đổi{picked}. 17_extension.py dùng tham số đã "
                        f"đăng ký {best[key]['params']}.")
    return "fail", (f"Tuning mở rộng {key} KHÔNG tái lập: NDCG@10 val lệch tới {gap_ndcg:.2e} (> {TOL_NDCG:.0e}) — "
                    "code đã đổi, xem lại trước khi chấm test.")


def check_extension_tuning(r: Report, best: dict) -> None:
    """Chạy lại tuning mở rộng (chỉ val, ~3 phút) vào thư mục bị .gitignore rồi so với audit/. Ép chạy trên CPU như
    lần tính số trong audit/ (02/10/2026) để giảm sai khác số học giữa thiết bị."""
    if RECHECK_DIR.exists():
        shutil.rmtree(RECHECK_DIR)
    RECHECK_DIR.mkdir(parents=True)
    shutil.copy(AUDIT / "best_configs.json", RECHECK_DIR / "best_configs.json")
    cmd = [sys.executable, str(PROJECT_ROOT / "scripts" / "10_tune.py"), "--model", "extension",
           "--log-dir", str(RECHECK_DIR), "--ckpt-dir", str(RECHECK_DIR / "ckpt")]
    print("  ... chạy lại tuning mở rộng trên val, bằng CPU (không ghi audit/):", flush=True)
    res = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                         env={**os.environ, "CUDA_VISIBLE_DEVICES": ""})
    if res.returncode != 0:
        r.fail("10_tune.py --model extension lỗi:\n" + res.stdout[-1500:] + res.stderr[-1500:])
        return
    again = json.loads((RECHECK_DIR / "best_configs.json").read_text(encoding="utf-8"))
    old, new = pd.read_csv(AUDIT / "tuning_log.csv"), pd.read_csv(RECHECK_DIR / "tuning_log.csv")
    for k in EXT_KEYS:
        status, msg = compare_extension(old, new, best, again, k)
        {"ok": r.ok, "warn": r.warn, "fail": r.fail}[status](msg)


def check_environment(r: Report, need_report: bool) -> None:
    try:
        import torch
        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            if ORIGINAL_GPU in name:
                r.ok(f"GPU: {name} — cùng loại GPU với lần chạy 29/09, kỳ vọng ra đúng cùng số")
            else:
                r.warn(f"GPU: {name} — khác GPU của lần chạy 29/09 ({ORIGINAL_GPU}); GMF/MLP/NeuMF có thể lệch nhẹ, "
                       "19_check_report.py sẽ chỉ ra câu chữ cần sửa.")
        else:
            r.warn("Không có GPU CUDA (PyTorch bản CPU hoặc máy không có GPU NVIDIA) — 11_final.py trên CPU chậm hơn "
                   f"nhiều và số GMF/MLP/NeuMF có thể lệch so với lần chạy 29/09 trên {ORIGINAL_GPU}. Nên chạy trên "
                   "máy có GPU đã dùng lần trước hoặc Colab (notebooks/colab_final.ipynb).")
    except ImportError:
        r.fail("Chưa cài PyTorch.")
    free_gb = shutil.disk_usage(PROJECT_ROOT).free / 1e9
    (r.ok if free_gb >= 2 else r.warn)(f"Dung lượng trống {free_gb:.1f} GB")
    report = PROJECT_ROOT.parent / "Report DACNTT" / "content" / "tables"
    if need_report and not report.exists():
        r.warn(f"Không thấy {report} — 15_export_report.py sẽ tạo mới thư mục này.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quick", action="store_true", help="bỏ dựng lại dữ liệu và kiểm tra tái lập tuning mở rộng")
    ap.add_argument("--extension-only", action="store_true", help="kiểm tra trước 17_extension.py (không chạy lại 11)")
    args = ap.parse_args()
    r = Report()
    print("Kiểm tra trước khi chạy lại đánh giá cuối:", flush=True)
    check_git(r)
    check_prereg(r)
    best = check_configs(r)
    if args.extension_only:
        check_final_checkpoints(r)
    check_environment(r, need_report=True)
    if not args.quick and not r.errors:
        check_data(r)
        check_extension_tuning(r, best)
    print()
    if r.errors:
        print(f"CHƯA SẴN SÀNG: {len(r.errors)} lỗi. Sửa rồi chạy lại `python scripts/18_preflight.py`.")
        sys.exit(1)
    plan = ("17 (mở rộng, ~5–10 phút) → 16 → 15 → 19" if args.extension_only else
            "20 (ablation chỉ trên validation, ~45–60 phút) → 11 (3 seed, ~1,5 giờ trên RTX 3050) → 12 → 17 (~5–10 "
            "phút) → 16 → 13 → 14 (~10–15 phút) → 15 → 19")
    print(f"SẴN SÀNG{' (có cảnh báo)' if r.warnings else ''}. Thứ tự chạy: {plan}.")


if __name__ == "__main__":
    main()
