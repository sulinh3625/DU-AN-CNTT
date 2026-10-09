"""run.py: chạy từng bước có thanh tiến trình, dừng ở bước lỗi đầu tiên và báo lệnh chạy lại; menu chọn lệnh bằng số."""
from __future__ import annotations

import sys

import pytest

import run


def test_run_steps_stops_at_first_failure_and_reports_it(tmp_path, capsys):
    marker = tmp_path / "buoc3"
    steps = [["-c", "pass"], ["-c", "import sys; sys.exit(3)"], ["-c", f"open(r'{marker}', 'w')"]]
    assert run.run_steps("thu", steps) == 3
    out = capsys.readouterr().out
    assert not marker.exists()  # bước sau bước lỗi không chạy
    assert "bước 2/3" in out and "mã thoát 3" in out and "chưa chạy" in out
    assert 'Chạy lại riêng bước này:  python -c "import sys; sys.exit(3)"' in out
    assert run.run_steps("thu", [["-c", "pass"]] * 2) == 0


def test_v2_data_runs_sample_features_then_prepare():
    assert run.cmd_v2_data(None) == [["scripts/00_sample_hm.py", "--block", "2"], ["scripts/21_build_features.py"],
                                     ["scripts/02_prepare_data.py"]]


def test_all_tunes_then_dry_run_and_opens_test_only_with_final(monkeypatch):
    overnight = [["scripts/02_prepare_data.py"], ["scripts/22_tune_v2.py", "--model", "all", "--resume"],
                 ["scripts/23_final_v2.py", "--dry-run", "--max-epochs", "1", "--seeds", "42"],
                 ["scripts/24_report_v2.py", "--final-dir", "outputs/v2/dry_run", "--report-dir", ""]]
    ns = run.argparse.Namespace
    assert run.cmd_all(ns(final=False, reason="")) == overnight  # mặc định không chấm tập kiểm thử
    assert run.cmd_all(ns(final=True, reason="đêm")) == overnight + [
        ["scripts/23_final_v2.py", "--reason", "đêm"], ["scripts/24_report_v2.py"]]
    with pytest.raises(SystemExit, match="--reason"):
        run.cmd_all(ns(final=True, reason=" "))


def _menu(monkeypatch, answers):
    """Chạy `python run.py` không tham số trên terminal với các câu trả lời cho input(); trả về các bước đã chạy."""
    ran, it = [], iter(answers)
    monkeypatch.setattr(sys, "argv", ["run.py"])
    monkeypatch.setattr(sys, "stdin", type("Tty", (), {"isatty": lambda self: True})())
    monkeypatch.setattr("builtins.input", lambda prompt="": next(it))
    monkeypatch.setattr(run, "run_steps", lambda name, steps: ran.append(steps) or 0)
    try:
        run.main()
    except SystemExit as e:
        assert e.code == 0
    return ran


def test_menu_asks_required_args_and_defaults_to_no_for_test_commands(monkeypatch, capsys):
    pick = run.MENU[1][1].index("v2-final") + len(run.MENU[0][1]) + 1
    assert _menu(monkeypatch, ["0", str(pick), "lý do thử", "--seeds 42", ""]) == []  # Enter = Không chạy
    out = capsys.readouterr().out
    assert "Không có lựa chọn '0'" in out
    assert 'scripts/23_final_v2.py --reason "lý do thử" --seeds 42' in out and "chấm tập kiểm thử" in out


def test_menu_runs_command_with_extra_options(monkeypatch):
    pick = run.MENU[0][1].index("prepare") + 1
    assert _menu(monkeypatch, [str(pick), "--sample holdout", ""]) == [  # Enter = Có chạy
        [["scripts/02_prepare_data.py", "--sample", "holdout"]]]
    assert _menu(monkeypatch, [""]) == []  # Enter ở menu = thoát (hỏi thêm sẽ hết câu trả lời -> lỗi)
