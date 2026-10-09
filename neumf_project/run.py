"""Entry point tổng hợp cho pipeline NeuMF — gom các lệnh trong scripts/ lại một chỗ.

Giao thức v2 (audit/PREREG_v2.md) — kết quả chính của báo cáo:
    python run.py sample-hm                  # mẫu phát triển (khối 0) -> data/processed/hm/mau_phat_trien.csv (chạy 1 lần)
    python run.py v2-data                    # mẫu kiểm định (khối 2) + đặc trưng + prepare (1 lần, cần dữ liệu gốc)
    python run.py prepare                    # gộp màu theo product_code, k-core -> outputs/data/<mẫu>.csv.gz + MD5
    python run.py v2-tune --resume           # tinh chỉnh trên tập xác thực của mẫu A (5–6 giờ CPU)
    python run.py v2-dry-run                 # thử trọn đường ống đánh giá cuối trên tập xác thực của A (không chấm test)
    python run.py v2-final --reason "..."    # đánh giá cuối trên tập kiểm thử của mẫu B (mở đúng một lần) + xuất báo cáo
    python run.py v2-report                  # chỉ tính lại kiểm định, bảng, hình, macro từ outputs/v2/final/

Giao thức v1 (lịch sử phát triển; config mặc định: configs/hm500k.yaml, run tag mặc định: hm500k_seed<seed>):
    python run.py all                       # audit + train + evaluate, trọn gói (khám phá, bảng trên validation);
                                             #   xong thì hỏi y/N chạy tiếp multi-seed + aggregate (--multi-seed / --no-multi-seed để khỏi hỏi)
    python run.py preflight                  # kiểm tra sẵn sàng trước khi chạy lại (tree sạch, PREREG, dữ liệu, tái lập tuning)
    python run.py final --reason "..."       # chạy lại TOÀN BỘ số liệu báo cáo: 18 → 20 → 11 → 12 → 17 → 16 → 13 → 14 → 15 → 19
    python run.py ablation                   # chỉ ablation trên validation (số chiều, số tầng MLP, mẫu âm) — không chấm test
    python run.py extension --reason "..."   # chỉ phần mở rộng PREREG mục 9 trên checkpoint đã có: 18 → 17 → 16 → 15 → 19
    python run.py check-report               # đối chiếu câu chữ báo cáo + tài liệu với số liệu hiện có
    python run.py train --run-tag my_tag
    python run.py multi-seed --seeds 42 2024 2025 2026 3407 7
    python run.py aggregate --seeds 42 2024 2025 2026 3407 7
    python run.py demo

Mỗi lệnh chỉ gọi thẳng script tương ứng trong scripts/ (chi tiết từng bước: README.md mục 3 cho v2, mục 7 cho v1)
— file này không chứa logic huấn luyện/đánh giá.
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
    _run("00_sample_hm.py", "--block", str(args.block))


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
    """Audit + train + evaluate trọn gói (khám phá, giao thức v1 — bảng trên validation)."""
    cmd_audit(args)
    extra = (["--run-tag", args.run_tag] if args.run_tag else []) + _final(args)
    _run("run_all.py", "--config", args.config, *extra)
    if args.multi_seed is None:  # không truyền cờ -> hỏi (chỉ khi chạy tay trên terminal)
        args.multi_seed = sys.stdin.isatty() and input(
            f"Chạy tiếp multi-seed + aggregate với seeds {args.seeds}? [y/N] ").strip().lower() in ("y", "yes")
    if args.multi_seed:
        cmd_multi_seed(args)
        cmd_aggregate(args)


def cmd_preflight(args):
    _run("18_preflight.py", *(["--quick"] if args.quick else []))


def cmd_final(args):
    """Giao thức v1: chạy lại toàn bộ số liệu v1 (README mục 7), dùng best_configs.json đã tune — không tune lại.

    18 kiểm tra sẵn sàng → 20 ablation chỉ trên validation → 11 chấm test 3 seed (chọn epoch trên val, train lại trên
    train ∪ val) → 12 kiểm định → 17 mở rộng PREREG mục 9 → 16 chỉ số @20 → 13 biểu đồ → 14 phân tích phụ → 15 xuất
    báo cáo → 19 đối chiếu. Mỗi bước chấm test (11, 17, 14) ghi một dòng audit/test_access_log.csv; 18 và 20 không
    chấm test nên nếu chúng lỗi thì tập test chưa bị đụng tới."""
    if not args.skip_preflight:
        _run("18_preflight.py", *(["--quick"] if args.quick_preflight else []))
    if not args.skip_ablation:
        _run("20_ablation.py", "--resume")
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


def cmd_v2_data(args):
    """Mẫu kiểm định (khối 2, khách khác hẳn mẫu phát triển), đặc trưng danh mục/doanh số theo ngày, rồi file dữ liệu
    đã lọc của mọi mẫu."""
    _run("00_sample_hm.py", "--block", "2")
    _run("21_build_features.py")
    cmd_prepare(args)


def cmd_prepare(args):
    """File dữ liệu đã lọc (gộp màu theo product_code, k-core trước mốc kiểm thử) + MD5 cho mọi mô hình v2."""
    _run("02_prepare_data.py", *(["--sample", args.sample] if getattr(args, "sample", None) else []))


def cmd_v2_tune(args):
    _run("22_tune_v2.py", "--model", *args.model, *(["--resume"] if args.resume else []))


def cmd_v2_dry_run(args):
    """Chạy thử 23_final_v2.py trên tập xác thực của A (1 epoch) rồi 24_report_v2.py, không ghi vào báo cáo."""
    _run("23_final_v2.py", "--dry-run", "--max-epochs", str(args.max_epochs), "--seeds", *map(str, args.seeds))
    _run("24_report_v2.py", "--final-dir", "outputs/v2/dry_run", "--report-dir", "")


def cmd_v2_final(args):
    """Đánh giá cuối trên tập kiểm thử của mẫu B (khoá kiểm thử v2), rồi kiểm định + xuất báo cáo."""
    _run("23_final_v2.py", "--reason", args.reason, *(["--seeds", *map(str, args.seeds)] if args.seeds else []))
    _run("24_report_v2.py")


def cmd_v2_report(args):
    _run("24_report_v2.py")


def cmd_ablation(args):
    """Ablation trên validation theo đề cương 5.3 (scripts/20_ablation.py) rồi vẽ lại hình và xuất báo cáo."""
    _run("20_ablation.py", *(["--resume"] if args.resume else []))
    _run("13_plot_final.py")
    _run("15_export_report.py")


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

    p = with_final(with_dataset(sub.add_parser("all", help="Audit + train + evaluate trọn gói, rồi (tuỳ chọn) multi-seed + aggregate")))
    p.add_argument("--run-tag", default=None)
    p.add_argument("--multi-seed", action=argparse.BooleanOptionalAction, default=None,
                   help="chạy/bỏ multi-seed + aggregate sau khi train xong (không truyền: hỏi y/N)")
    p.add_argument("--seeds", nargs="+", type=int, default=DEFAULT_SEEDS)
    with_dataset(sub.add_parser("audit", help="Audit dữ liệu — bắt buộc trước khi train"))
    with_dataset(sub.add_parser("preprocess", help="Sinh splits độc lập"))
    with_final(with_dataset(sub.add_parser("train", help="Chỉ huấn luyện, không vẽ biểu đồ"))).add_argument("--run-tag", default=None)
    sub.add_parser("evaluate", help="Đánh giá + xuất biểu đồ cho 1 run-tag").add_argument("--run-tag", default=None, help="Mặc định: run mới nhất")
    with_final(with_dataset(sub.add_parser("multi-seed", help="Lặp lại train trên nhiều seed"))).add_argument("--seeds", nargs="+", type=int, default=DEFAULT_SEEDS)
    with_dataset(sub.add_parser("aggregate", help="Tổng hợp mean/std + Wilcoxon từ multi-seed")).add_argument("--seeds", nargs="+", type=int, default=DEFAULT_SEEDS)
    pre = sub.add_parser("preflight", help="Kiểm tra sẵn sàng trước khi chạy lại (không chấm test)")
    pre.add_argument("--quick", action="store_true", help="bỏ dựng lại dữ liệu và kiểm tra tái lập tuning mở rộng")
    for name, text in (("final", "Chạy lại toàn bộ: 18 → 20 → 11 → 12 → 17 → 16 → 13 → 14 → 15 → 19"),
                       ("extension", "Chỉ mở rộng PREREG mục 9 trên checkpoint đã có: 18 → 17 → 16 → 15 → 19")):
        p = sub.add_parser(name, help=text)
        p.add_argument("--reason", required=True, help="Lý do chấm test (ghi vào test_access_log.csv)")
        p.add_argument("--skip-preflight", action="store_true", help="bỏ bước 18_preflight.py")
        p.add_argument("--quick-preflight", action="store_true", help="18_preflight.py --quick")
        if name == "final":
            p.add_argument("--skip-ablation", action="store_true",
                           help="bỏ bước 20_ablation.py (ablation trên validation, ~45–60 phút GPU)")
    sub.add_parser("ablation", help="Ablation trên validation (20) rồi vẽ hình (13) và xuất báo cáo (15)") \
        .add_argument("--resume", action="store_true", help="chạy tiếp, bỏ qua cấu hình đã có")
    sub.add_parser("check-report", help="Đối chiếu câu chữ báo cáo/tài liệu với số liệu hiện có (19)") \
        .add_argument("--strict", action="store_true", help="trả mã lỗi nếu có khẳng định sai")
    sub.add_parser("sample-hm", help="Lấy mẫu khách theo khối từ transactions_train.csv gốc (chạy 1 lần)") \
        .add_argument("--block", type=int, default=0, help="0 = mẫu phát triển (mặc định), 2 = mẫu kiểm định")
    sub.add_parser("v2-data", help="v2: mẫu kiểm định (khối 2) + đặc trưng + dữ liệu đã lọc (00 --block 2, 21, 02)")
    sub.add_parser("prepare", help="v2: gộp màu theo product_code, k-core, xuất outputs/data/*.csv.gz + MD5 (02)") \
        .add_argument("--sample", choices=["dev", "holdout"], help="chỉ một mẫu (mặc định: mọi mẫu)")
    p = sub.add_parser("v2-tune", help="v2: tinh chỉnh trên tập xác thực của mẫu A (22)")
    p.add_argument("--model", nargs="+", default=["all"], help="mặc định: mọi mô hình")
    p.add_argument("--resume", action="store_true", help="bỏ qua cấu hình đã có trong audit/v2/tuning_log.csv")
    p = sub.add_parser("v2-dry-run", help="v2: chạy thử đánh giá cuối trên tập xác thực của A (không chấm test)")
    p.add_argument("--max-epochs", type=int, default=1)
    p.add_argument("--seeds", nargs="+", type=int, default=[42])
    p = sub.add_parser("v2-final", help="v2: đánh giá cuối trên tập kiểm thử của mẫu B (23) + báo cáo (24)")
    p.add_argument("--reason", required=True, help="Lý do chấm test (ghi vào audit/test_access_log.csv)")
    p.add_argument("--seeds", nargs="+", type=int, default=None, help="mặc định: 5 seed của configs/v2.yaml")
    sub.add_parser("v2-report", help="v2: kiểm định, bảng, hình, macro LaTeX từ outputs/v2/final (24)")
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
        "ablation": cmd_ablation,
        "check-report": cmd_check_report,
        "sample-hm": cmd_sample_hm,
        "v2-data": cmd_v2_data,
        "prepare": cmd_prepare,
        "v2-tune": cmd_v2_tune,
        "v2-dry-run": cmd_v2_dry_run,
        "v2-final": cmd_v2_final,
        "v2-report": cmd_v2_report,
        "demo": cmd_demo,
    }[args.command](args)


if __name__ == "__main__":
    main()
