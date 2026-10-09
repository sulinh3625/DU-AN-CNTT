"""Entry point tổng hợp cho pipeline NeuMF — gom các lệnh trong scripts/ lại một chỗ.

    python run.py                            # menu: chọn việc bằng số, nhập tham số, xem trước các bước rồi chạy
    python run.py <lệnh> -h                  # tham số của một lệnh

Giao thức v2 (audit/PREREG_v2.md) — kết quả chính của báo cáo:
    python run.py sample-hm                  # mẫu phát triển (khối 0) -> data/processed/hm/mau_phat_trien.csv (1 lần)
    python run.py v2-data                    # mẫu kiểm định (khối 2) + đặc trưng + prepare (1 lần, cần dữ liệu gốc)
    python run.py prepare                    # gộp màu theo product_code, k-core -> outputs/data/<mẫu>.csv.gz + MD5
    python run.py all                        # chạy qua đêm: prepare -> tinh chỉnh mọi mô hình -> chạy thử đánh giá cuối
    python run.py all --final --reason "..." #   ... rồi chấm luôn tập kiểm thử ở cuối (mở đúng một lần)
    python run.py v2-tune --resume           # chỉ tinh chỉnh trên tập xác thực của mẫu phát triển (5–6 giờ CPU)
    python run.py v2-dry-run                 # thử trọn đường ống đánh giá cuối trên tập xác thực (không chấm test)
    python run.py v2-final --reason "..."    # đánh giá cuối trên tập kiểm thử của mẫu kiểm định (mở đúng một lần)
    python run.py v2-report                  # chỉ tính lại kiểm định, bảng, hình, macro từ outputs/v2/final/
    python run.py check-report               # đối chiếu câu chữ báo cáo + tài liệu với số liệu hiện có
    python run.py demo

Giao thức v1 (lịch sử phát triển) không còn lệnh ở đây — các script v1 vẫn chạy tay được, xem README.md mục 7.

Mỗi lệnh chỉ gọi lần lượt các script tương ứng trong scripts/ (chi tiết: README.md mục 3) — file này không chứa logic
huấn luyện/đánh giá. Trước mỗi bước in thanh tiến trình [████░░░░] k/N kèm thời gian đã chạy; bước nào lỗi thì dừng
ngay, in bảng tóm tắt (✓ xong / ✗ lỗi / ⏹ bị ngắt, thời gian từng bước) và lệnh chạy lại riêng bước đó — thông báo lỗi
của script nằm ngay phía trên bảng.
"""
from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import time
from datetime import timedelta
from pathlib import Path

# Console Windows mặc định dùng codepage (vd. cp1258) không encode được tiếng Việt -> crash khi in --help hoặc thông báo
# lỗi. Ép UTF-8 cho tiến trình này và các script con; line_buffering + PYTHONUNBUFFERED để dòng tiến trình và output của
# script con ra đúng thứ tự, kể cả khi ghi ra file log.
sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUNBUFFERED": "1"}

ROOT = Path(__file__).resolve().parent

# Màu chỉ khi in ra terminal (tắt bằng biến môi trường NO_COLOR); os.system("") bật mã màu ANSI trên console Windows cũ.
_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ
if _COLOR and os.name == "nt":
    os.system("")


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text


def _s(script: str, *args) -> list[str]:
    """Một bước: python scripts/<script> <args>."""
    return [f"scripts/{script}", *map(str, args)]


def _show(step: list[str]) -> str:
    """Dòng lệnh để in và chạy lại tay (tham số có dấu cách đặt trong ngoặc kép)."""
    return "python " + " ".join(f'"{a}"' if " " in a or not a else a for a in step)


def _hms(seconds: float) -> str:
    return str(timedelta(seconds=round(seconds)))


# ------------------------------------------------------------------ chạy các bước
def run_steps(name: str, steps: list[list[str]]) -> int:
    """Chạy lần lượt các bước, in thanh tiến trình trước mỗi bước; dừng ở bước lỗi đầu tiên. Trả về mã thoát."""
    n, t0, done = len(steps), time.monotonic(), []  # done: (giây, mã thoát; None = bị ngắt)
    for i, step in enumerate(steps, 1):
        k = round(20 * (i - 1) / n)
        bar = "█" * k + "░" * (20 - k)
        print(_c(f"\n━━ [{bar}] bước {i}/{n} · {_show(step)} · đã chạy {_hms(time.monotonic() - t0)}", "1;36"))
        t1 = time.monotonic()
        try:
            rc = subprocess.run([sys.executable, *step], cwd=ROOT, env=_ENV).returncode
        except KeyboardInterrupt:
            rc = None
        done.append((time.monotonic() - t1, rc))
        if rc != 0:
            break
        print(_c(f"✓ bước {i}/{n} xong sau {_hms(done[-1][0])}", "32"))

    ok = len(done) == n and done[-1][1] == 0
    if n > 1 or not ok:  # bảng tóm tắt
        state = "xong" if ok else "DỪNG"
        print(_c(f"\n━━ {name}: {state} sau {_hms(time.monotonic() - t0)}", "1;32" if ok else "1;31"))
        for i, step in enumerate(steps, 1):
            if i > len(done):
                print(_c(f"  · {f'{i}/{n}':>5}  {'chưa chạy':>9}  {_show(step)}", "2"))
                continue
            secs, rc = done[i - 1]
            mark = _c("✓", "32") if rc == 0 else _c("⏹", "33") if rc is None else _c("✗", "31")
            print(f"  {mark} {f'{i}/{n}':>5}  {_hms(secs):>9}  {_show(step)}")
    if ok:
        return 0
    rc = done[-1][1]
    why = "bị ngắt (Ctrl+C)" if rc is None else f"lỗi, mã thoát {rc} — thông báo lỗi của script nằm ngay phía trên"
    print(_c(f"\n✗ Dừng ở bước {len(done)}/{n}: {why}.", "1;31"))
    print(f"  Chạy lại riêng bước này:  {_show(steps[len(done) - 1])}")
    return 130 if rc is None else rc


# ------------------------------------------------------------------ các lệnh: trả về danh sách bước
def cmd_sample_hm(args):
    return [_s("00_sample_hm.py", "--block", args.block)]


def cmd_demo(args):
    return [["-m", "demo"]]


def cmd_check_report(args):
    return [_s("19_check_report.py", *(["--strict"] if args.strict else []))]


def cmd_v2_data(args):
    """Mẫu kiểm định (khối 2, khách khác hẳn mẫu phát triển), đặc trưng danh mục/doanh số theo ngày, rồi file dữ liệu
    đã lọc của mọi mẫu."""
    return [_s("00_sample_hm.py", "--block", 2), _s("21_build_features.py"), _s("02_prepare_data.py")]


def cmd_prepare(args):
    """File dữ liệu đã lọc (gộp màu theo product_code, k-core trước mốc kiểm thử) + MD5 cho mọi mô hình v2."""
    return [_s("02_prepare_data.py", *(["--sample", args.sample] if args.sample else []))]


def cmd_v2_tune(args):
    return [_s("22_tune_v2.py", "--model", *args.model, *(["--resume"] if args.resume else []))]


def cmd_v2_dry_run(args):
    """Chạy thử 23_final_v2.py trên tập xác thực của mẫu phát triển (1 epoch) rồi 24_report_v2.py, không ghi vào báo
    cáo."""
    return [_s("23_final_v2.py", "--dry-run", "--max-epochs", args.max_epochs, "--seeds", *args.seeds),
            _s("24_report_v2.py", "--final-dir", "outputs/v2/dry_run", "--report-dir", "")]


def cmd_v2_final(args):
    """Đánh giá cuối trên tập kiểm thử của mẫu kiểm định (khoá kiểm thử v2), rồi kiểm định + xuất báo cáo."""
    return [_s("23_final_v2.py", "--reason", args.reason, *(["--seeds", *args.seeds] if args.seeds else [])),
            _s("24_report_v2.py")]


def cmd_v2_report(args):
    return [_s("24_report_v2.py")]


def cmd_all(args):
    """Chạy qua đêm: file dữ liệu đã lọc -> tinh chỉnh mọi mô hình (--resume: bị ngắt thì chạy lại lệnh là đi tiếp) ->
    chạy thử đánh giá cuối trên tập xác thực (bắt lỗi đường ống, không chấm test). --final: chấm luôn tập kiểm thử ở
    cuối — khoá kiểm thử của 23_final_v2.py vẫn áp dụng (PREREG_v2 đã commit, tree sạch, cùng mã băm lúc tinh chỉnh)."""
    if args.final and not args.reason.strip():
        raise SystemExit("all --final cần --reason (ghi vào audit/test_access_log.csv)")
    ns = argparse.Namespace
    steps = [*cmd_prepare(ns(sample=None)), *cmd_v2_tune(ns(model=["all"], resume=True)),
             *cmd_v2_dry_run(ns(max_epochs=1, seeds=[42]))]
    return steps + (cmd_v2_final(ns(reason=args.reason, seeds=None)) if args.final else [])


COMMANDS = {
    "sample-hm": cmd_sample_hm, "v2-data": cmd_v2_data, "prepare": cmd_prepare, "all": cmd_all,
    "v2-tune": cmd_v2_tune, "v2-dry-run": cmd_v2_dry_run, "v2-final": cmd_v2_final, "v2-report": cmd_v2_report,
    "check-report": cmd_check_report, "demo": cmd_demo,
}

# ------------------------------------------------------------------ menu
MENU = (
    ("Dữ liệu (chạy 1 lần, cần dữ liệu gốc H&M)", ("sample-hm", "v2-data", "prepare")),
    ("Huấn luyện và đánh giá (giao thức v2)",
     ("all", "v2-tune", "v2-dry-run", "v2-final", "v2-report", "check-report")),
    ("Khác", ("demo",)),
)
OPENS_TEST = ("v2-final",)  # chấm tập kiểm thử: menu hỏi lại, mặc định Không (all --final cũng vậy)


def menu(sub) -> list[str] | None:
    """`python run.py` không tham số trên terminal: chọn lệnh bằng số rồi nhập tham số; trả về argv (None = thoát)."""
    names = [name for _, group in MENU for name in group]
    print(_c("NeuMF — chọn việc cần chạy", "1"))
    for title, group in MENU:
        print(_c(f"\n {title}", "36"))
        for name in group:
            print(f"  {names.index(name) + 1:>2}  {name:<13} {sub.choices[name].description}")
    while True:
        pick = input("\nChọn số (Enter = thoát): ").strip()
        if not pick:
            return None
        if pick.isdigit() and 1 <= int(pick) <= len(names):
            break
        print(f"Không có lựa chọn '{pick}' — nhập số từ 1 đến {len(names)}.")
    name = names[int(pick) - 1]
    p = sub.choices[name]
    print("\n" + p.format_help())
    argv = [name]
    for a in p._actions:  # tham số bắt buộc (vd. --reason): hỏi riêng từng cái
        if a.required:
            argv += [a.option_strings[0], input(f"{a.option_strings[0]} — {a.help}: ").strip()]
    try:
        return argv + shlex.split(input("Tuỳ chọn thêm (Enter = mặc định): "))
    except ValueError as e:
        raise SystemExit(f"Tuỳ chọn không hợp lệ: {e}") from None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name, text):
        return sub.add_parser(name, help=text, description=text)

    add("sample-hm", "Lấy mẫu khách theo khối từ transactions_train.csv gốc (00)") \
        .add_argument("--block", type=int, default=0, help="0 = mẫu phát triển (mặc định), 2 = mẫu kiểm định")
    add("v2-data", "Mẫu kiểm định (khối 2) + đặc trưng + dữ liệu đã lọc (00 --block 2, 21, 02)")
    add("prepare", "Gộp màu theo product_code, k-core, xuất outputs/data/*.csv.gz + MD5 (02)") \
        .add_argument("--sample", choices=["dev", "holdout"], help="chỉ một mẫu (mặc định: mọi mẫu)")
    p = add("all", "Chạy qua đêm: prepare → tinh chỉnh mọi mô hình → chạy thử đánh giá cuối (02, 22, 23 --dry-run, 24)")
    p.add_argument("--final", action="store_true",
                   help="chấm luôn tập kiểm thử ở cuối (23, 24) — cần --reason và audit/PREREG_v2.md đã commit")
    p.add_argument("--reason", default="", help="lý do chấm test (ghi vào audit/test_access_log.csv), dùng với --final")
    p = add("v2-tune", "Tinh chỉnh trên tập xác thực của mẫu phát triển (22)")
    p.add_argument("--model", nargs="+", default=["all"], help="mặc định: mọi mô hình")
    p.add_argument("--resume", action="store_true", help="bỏ qua cấu hình đã có trong audit/v2/tuning_log.csv")
    p = add("v2-dry-run", "Chạy thử đánh giá cuối trên tập xác thực (23 --dry-run, 24; không chấm test)")
    p.add_argument("--max-epochs", type=int, default=1)
    p.add_argument("--seeds", nargs="+", type=int, default=[42])
    p = add("v2-final", "Đánh giá cuối trên tập kiểm thử của mẫu kiểm định (23) + báo cáo (24)")
    p.add_argument("--reason", required=True, help="Lý do chấm test (ghi vào audit/test_access_log.csv)")
    p.add_argument("--seeds", nargs="+", type=int, default=None, help="mặc định: 5 seed của configs/v2.yaml")
    add("v2-report", "Kiểm định, bảng, hình, macro LaTeX từ outputs/v2/final (24)")
    add("check-report", "Đối chiếu câu chữ báo cáo/tài liệu với số liệu hiện có (19)") \
        .add_argument("--strict", action="store_true", help="trả mã lỗi nếu có khẳng định sai")
    add("demo", "Chạy giao diện demo (http://localhost:8000)")

    argv = sys.argv[1:]
    interactive = not argv and sys.stdin.isatty()
    if interactive:
        argv = menu(sub)
        if argv is None:
            return
    args = parser.parse_args(argv)
    steps = COMMANDS[args.command](args)
    if len(steps) > 1 or interactive:  # xem trước các bước
        print(_c(f"▶ {args.command}: {len(steps)} bước", "1"))
        for i, step in enumerate(steps, 1):
            print(f"  {i}. {_show(step)}")
    if interactive:
        print(f"Lệnh tương đương (chạy thẳng, bỏ qua menu): {_show(['run.py', *argv])}")
        if args.command in OPENS_TEST or getattr(args, "final", False):
            print(_c("⚠ Lệnh này chấm tập kiểm thử — chỉ chạy khi đã sẵn sàng.", "1;33"))
            go = input("Chạy? [y/N] ").strip().lower() in ("y", "yes", "c", "có")
        else:
            go = input("Chạy? [Y/n] ").strip().lower() not in ("n", "no", "k", "không")
        if not go:
            return
    sys.exit(run_steps(args.command, steps))


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):  # Ctrl+C / Ctrl+Z lúc đang ở menu
        print()
        sys.exit(130)
