"""Entry point tổng hợp cho pipeline NeuMF — gom các lệnh trong scripts/ lại một chỗ.

Ví dụ (config mặc định: configs/hm500k.yaml, run tag mặc định: hm500k_seed<seed>):
    python run.py sample-hm                  # tạo data/processed/hm/hm500k_transactions.csv (chạy 1 lần)
    python run.py all                        # audit + train + evaluate, trọn gói (khám phá, bảng trên validation)
    python run.py preflight                  # kiểm tra sẵn sàng trước khi chạy lại (tree sạch, PREREG, dữ liệu, tái lập tuning)
    python run.py final --reason "..."       # chạy lại TOÀN BỘ số liệu báo cáo: 18 → 11 → 12 → 17 → 16 → 13 → 14 → 15 → 19
    python run.py extension --reason "..."   # chỉ phần mở rộng PREREG mục 9 trên checkpoint đã có: 18 → 17 → 16 → 15 → 19
    python run.py check-report               # đối chiếu câu chữ báo cáo + tài liệu với số liệu hiện có
    python run.py train --run-tag my_tag
    python run.py multi-seed --seeds 42 2024 2025 2026 3407 7
    python run.py aggregate --seeds 42 2024 2025 2026 3407 7
    python run.py demo

Mỗi lệnh chỉ gọi thẳng script tương ứng trong scripts/ (xem README mục 3-8
để biết chi tiết từng bước) — file này không chứa logic huấn luyện/đánh giá.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Console Windows mặc định dùng codepage (vd. cp1258) không encode được tiếng
# Việt -> crash khi in --help hoặc thông báo lỗi. Ép UTF-8 cho tiến trình này
# và các script con được gọi bên dưới.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}

ROOT = Path(__file__).resolve().parent

DEFAULT_CONFIG = "configs/hm500k.yaml"
# >= 6 seed: Wilcoxon theo seed mới có thể đạt p < 0.05 (5 seed thì p nhỏ nhất = 0.0625).
DEFAULT_SEEDS = [42, 2024, 2025, 2026, 3407, 7]


def _run(script: str, *args: str) -> None:
    cmd = [sys.executable, str(ROOT / "scripts" / script), *args]
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, env=_ENV, check=True)


def cmd_sample_hm(args):
    _run("00_sample_hm.py")


def cmd_audit(args):
    _run("01_data_audit.py", "--config", args.config)


def cmd_preprocess(args):
    _run("02_preprocess.py", "--config", args.config)


def _final(args):
    return ["--final", "--reason", args.reason] if getattr(args, "final", False) else []


def cmd_train(args):
    extra = (["--run-tag", args.run_tag] if args.run_tag else []) + _final(args)
    _run("03_run_experiment.py", "--config", args.config, *extra)


def cmd_evaluate(args):
    extra = ["--run-tag", args.run_tag] if args.run_tag else []
    _run("05_evaluate.py", *extra)


def cmd_multi_seed(args):
    _run("04_multi_seed.py", "--config", args.config, "--seeds", *map(str, args.seeds), *_final(args))


def cmd_aggregate(args):
    _run("06_aggregate_seeds.py", "--config-name", Path(args.config).stem, "--seeds", *map(str, args.seeds))


def cmd_demo(args):
    subprocess.run(
        [sys.executable, "-m", "demo"],
        cwd=ROOT, env=_ENV, check=True,
    )


def cmd_all(args):
    """Audit + train + evaluate trọn gói (tương đương README mục 3)."""
    cmd_audit(args)
    extra = (["--run-tag", args.run_tag] if args.run_tag else []) + _final(args)
    _run("run_all.py", "--config", args.config, *extra)


def cmd_preflight(args):
    _run("18_preflight.py", *(["--quick"] if args.quick else []))


def cmd_final(args):
    """Chạy lại toàn bộ số liệu báo cáo (README mục 5), dùng best_configs.json đã tune — không tune lại.

    18 kiểm tra sẵn sàng → 11 chấm test 3 seed (chọn epoch trên val, train lại trên train ∪ val) → 12 kiểm định →
    17 mở rộng PREREG mục 9 → 16 chỉ số @20 → 13 biểu đồ → 14 phân tích phụ → 15 xuất báo cáo → 19 đối chiếu.
    Mỗi bước chấm test (11, 17, 14) ghi một dòng audit/test_access_log.csv."""
    if not args.skip_preflight:
        _run("18_preflight.py", *(["--quick"] if args.quick_preflight else []))
    _run("11_final.py", "--reason", args.reason)
    _run("12_significance.py")
    _run("17_extension.py", "--reason", f"{args.reason} — mở rộng PREREG mục 9")
    _run("16_extra_k.py")
    _run("13_plot_final.py")
    _run("14_secondary.py", "--reason", f"{args.reason} — phân tích phụ")
    _run("15_export_report.py")
    _run("19_check_report.py")


def cmd_extension(args):
    """Chỉ phần mở rộng PREREG mục 9 trên checkpoint của lần chạy 11_final.py đã có (không chạy lại 11)."""
    if not args.skip_preflight:
        _run("18_preflight.py", "--extension-only", *(["--quick"] if args.quick_preflight else []))
    _run("17_extension.py", "--reason", args.reason)
    _run("16_extra_k.py")
    _run("15_export_report.py")
    _run("19_check_report.py")


def cmd_check_report(args):
    _run("19_check_report.py", *(["--strict"] if args.strict else []))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    def with_dataset(p):
        p.add_argument("--config", default=DEFAULT_CONFIG, help=f"File config (mặc định: {DEFAULT_CONFIG})")
        return p

    def with_final(p):
        p.add_argument("--final", action="store_true", help="Đánh giá trên TEST (cần audit/PREREG.md đã commit)")
        p.add_argument("--reason", default="", help="Lý do đánh giá test (ghi vào test_access_log.csv)")
        return p

    with_final(with_dataset(sub.add_parser("all", help="Audit + train + evaluate trọn gói"))).add_argument("--run-tag", default=None)
    with_dataset(sub.add_parser("audit", help="Audit dữ liệu — bắt buộc trước khi train"))
    with_dataset(sub.add_parser("preprocess", help="Sinh splits độc lập"))
    with_final(with_dataset(sub.add_parser("train", help="Chỉ huấn luyện, không vẽ biểu đồ"))).add_argument("--run-tag", default=None)
    sub.add_parser("evaluate", help="Đánh giá + xuất biểu đồ cho 1 run-tag").add_argument("--run-tag", default=None, help="Mặc định: run mới nhất")
    with_final(with_dataset(sub.add_parser("multi-seed", help="Lặp lại train trên nhiều seed"))).add_argument("--seeds", nargs="+", type=int, default=DEFAULT_SEEDS)
    with_dataset(sub.add_parser("aggregate", help="Tổng hợp mean/std + Wilcoxon từ multi-seed")).add_argument("--seeds", nargs="+", type=int, default=DEFAULT_SEEDS)
    pre = sub.add_parser("preflight", help="Kiểm tra sẵn sàng trước khi chạy lại (không chấm test)")
    pre.add_argument("--quick", action="store_true", help="bỏ dựng lại dữ liệu và kiểm tra tái lập tuning mở rộng")
    for name, text in (("final", "Chạy lại toàn bộ: 18 → 11 → 12 → 17 → 16 → 13 → 14 → 15 → 19"),
                       ("extension", "Chỉ mở rộng PREREG mục 9 trên checkpoint đã có: 18 → 17 → 16 → 15 → 19")):
        p = sub.add_parser(name, help=text)
        p.add_argument("--reason", required=True, help="Lý do chấm test (ghi vào test_access_log.csv)")
        p.add_argument("--skip-preflight", action="store_true", help="bỏ bước 18_preflight.py")
        p.add_argument("--quick-preflight", action="store_true", help="18_preflight.py --quick")
    sub.add_parser("check-report", help="Đối chiếu câu chữ báo cáo/tài liệu với số liệu hiện có (19)") \
        .add_argument("--strict", action="store_true", help="trả mã lỗi nếu có khẳng định sai")
    sub.add_parser("sample-hm", help="Tạo bộ dữ liệu hm500k từ transactions_train.csv gốc (chạy 1 lần)")
    sub.add_parser("demo", help="Chạy giao diện demo (http://localhost:8000)")

    args = parser.parse_args()
    {
        "all": cmd_all,
        "audit": cmd_audit,
        "preprocess": cmd_preprocess,
        "train": cmd_train,
        "evaluate": cmd_evaluate,
        "multi-seed": cmd_multi_seed,
        "aggregate": cmd_aggregate,
        "preflight": cmd_preflight,
        "final": cmd_final,
        "extension": cmd_extension,
        "check-report": cmd_check_report,
        "sample-hm": cmd_sample_hm,
        "demo": cmd_demo,
    }[args.command](args)


if __name__ == "__main__":
    main()
