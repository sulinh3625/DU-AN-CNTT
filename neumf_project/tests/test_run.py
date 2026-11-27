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
    assert not marker.exists()
    assert "bước 2/3" in out and "mã thoát 3" in out and "chưa chạy" in out
    assert 'Chạy lại riêng bước này:  python -c "import sys; sys.exit(3)"' in out
    assert run.run_steps("thu", [["-c", "pass"]] * 2) == 0


def test_v2_data_runs_sample_features_then_prepare():
    assert run.cmd_v2_data(None) == [["scripts/1_sample.py", "--block", "2"], ["scripts/3_features.py"],
                                     ["scripts/2_prepare.py"]]


def test_all_tunes_then_dry_run_and_opens_test_only_with_final(monkeypatch):
    overnight = [["scripts/2_prepare.py"], ["scripts/4_tune.py", "--model", "all", "--resume"],
                 ["scripts/5_final.py", "--dry-run", "--max-epochs", "1", "--seeds", "42"],
                 ["scripts/7_report.py", "--final-dir", "outputs/v2/dry_run", "--report-dir", ""]]
    ns = run.argparse.Namespace
    assert run.cmd_all(ns(final=False, reason="")) == overnight
    assert run.cmd_all(ns(final=True, reason="đêm")) == overnight + [
        ["scripts/5_final.py", "--reason", "đêm"], ["scripts/7_report.py"]]
    with pytest.raises(SystemExit, match="--reason"):
        run.cmd_all(ns(final=True, reason=" "))


def _menu(monkeypatch, answers):
    """Chạy `python run.py` không tham số trên terminal với các câu trả lời cho input(); trả về các bước đã chạy."""
    ran, it = [], iter(answers)
    monkeypatch.setattr(sys, "argv", ["run.py"])
    monkeypatch.setattr(sys, "stdin", type("Tty", (), {"isatty": lambda self: True})())
    monkeypatch.setattr("builtins.input", lambda prompt="": next(it))
    monkeypatch.setattr(run, "run_steps", lambda name, steps, config=None: ran.append(steps) or 0)
    try:
        run.main()
    except SystemExit as e:
        assert e.code == 0
    return ran


def test_menu_asks_required_args_and_defaults_to_no_for_test_commands(monkeypatch, capsys):
    pick = run.MENU[1][1].index("v2-final") + len(run.MENU[0][1]) + 1
    assert _menu(monkeypatch, ["0", str(pick), "lý do thử", "--seeds 42", ""]) == []
    out = capsys.readouterr().out
    assert "Không có lựa chọn '0'" in out
    assert 'scripts/5_final.py --reason "lý do thử" --seeds 42' in out and "chấm tập kiểm thử" in out


def test_menu_runs_command_with_extra_options(monkeypatch):
    pick = run.MENU[0][1].index("prepare") + 1
    assert _menu(monkeypatch, [str(pick), "--sample holdout", ""]) == [
        [["scripts/2_prepare.py", "--sample", "holdout"]]]
    assert _menu(monkeypatch, [""]) == []
