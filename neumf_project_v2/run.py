"""Entry point tổng hợp cho pipeline NeuMF — gom các lệnh trong scripts/ lại một chỗ.

Ví dụ (config mặc định: configs/hm500k.yaml, run tag mặc định: hm500k_seed<seed>):
    python run.py sample-hm                  # tạo data/processed/hm/hm500k_transactions.csv (chạy 1 lần)
    python run.py all                        # audit + train + evaluate, trọn gói
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


def cmd_train(args):
    extra = ["--run-tag", args.run_tag] if args.run_tag else []
    _run("03_run_experiment.py", "--config", args.config, *extra)


def cmd_evaluate(args):
    extra = ["--run-tag", args.run_tag] if args.run_tag else []
    _run("05_evaluate.py", *extra)


def cmd_multi_seed(args):
    _run("04_multi_seed.py", "--config", args.config, "--seeds", *map(str, args.seeds))


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
    extra = ["--run-tag", args.run_tag] if args.run_tag else []
    _run("run_all.py", "--config", args.config, *extra)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    def with_dataset(p):
        p.add_argument("--config", default=DEFAULT_CONFIG, help=f"File config (mặc định: {DEFAULT_CONFIG})")
        return p

    with_dataset(sub.add_parser("all", help="Audit + train + evaluate trọn gói cho 1 dataset")).add_argument("--run-tag", default=None)
    with_dataset(sub.add_parser("audit", help="Audit dữ liệu — bắt buộc trước khi train"))
    with_dataset(sub.add_parser("preprocess", help="Sinh splits độc lập"))
    with_dataset(sub.add_parser("train", help="Chỉ huấn luyện, không vẽ biểu đồ")).add_argument("--run-tag", default=None)
    sub.add_parser("evaluate", help="Đánh giá + xuất biểu đồ cho 1 run-tag").add_argument("--run-tag", default=None, help="Mặc định: run mới nhất")
    with_dataset(sub.add_parser("multi-seed", help="Lặp lại train trên nhiều seed")).add_argument("--seeds", nargs="+", type=int, default=DEFAULT_SEEDS)
    with_dataset(sub.add_parser("aggregate", help="Tổng hợp mean/std + Wilcoxon từ multi-seed")).add_argument("--seeds", nargs="+", type=int, default=DEFAULT_SEEDS)
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
        "sample-hm": cmd_sample_hm,
        "demo": cmd_demo,
    }[args.command](args)


if __name__ == "__main__":
    main()
