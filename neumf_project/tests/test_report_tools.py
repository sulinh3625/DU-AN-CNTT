"""Đối chiếu báo cáo với số liệu (scripts/19_check_report.py)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


check = _load("check_report", "19_check_report.py")


@pytest.fixture(scope="module")
def data():
    d = check.Data()
    if d.S2 is None:
        pytest.skip("Chưa có outputs/v2/final/summary.csv")
    return d


def test_report_claims_hold_on_committed_results(data):
    failed = []
    for _, _, desc, pred, needs in check.claims(data):
        if any(getattr(data, n) is None for n in needs):
            continue
        try:
            ok = pred()
        except (KeyError, ValueError) as exc:  # cột không còn trong file kết quả: câu trong báo cáo đã lỗi thời
            ok, desc = False, f"{desc} [{exc!r}]"
        if not ok:
            failed.append(desc)
    assert failed == []


def test_report_claims_detect_changed_results(data):
    """NDCG@10 cao nhất vượt 0,05 -> câu 'Thang giá trị tuyệt đối thấp' phải bị báo sai."""
    s = data.S2.copy()
    data.S2 = s.assign(**{"NDCG@10_mean": s["NDCG@10_mean"] + 0.05})
    try:
        failed = {desc for _, _, desc, pred, needs in check.claims(data)
                  if desc == "v2: NDCG@10 cao nhất < 0,05" and not pred()}
    finally:
        data.S2 = s
    assert failed == {"v2: NDCG@10 cao nhất < 0,05"}


def test_check_flags_missing_generated_tables_and_figures(tmp_path, monkeypatch):
    report = tmp_path / "report"
    tables = report / "content" / "tables"
    tables.mkdir(parents=True)
    (report / "content" / "C4.tex").write_text(
        r"\bangketqua{tab_x.tex}{a} \hinhketqua{media/figures/v2/x.png}{\textwidth}{c}{fig:x}{b}", encoding="utf-8")
    monkeypatch.setattr(check, "REPORT", report)
    monkeypatch.setattr(check, "TABLES", tables)
    assert check.check_macros_and_tables() == 2
    (tables / "tab_x.tex").write_text("", encoding="utf-8")
    (report / "media" / "figures" / "v2").mkdir(parents=True)
    (report / "media" / "figures" / "v2" / "x.png").write_bytes(b"")
    assert check.check_macros_and_tables() == 0


def test_report_claim_anchors_exist_in_report():
    missing = [(rel, anchor) for rel, anchor, *_ in check.claims(check.Data()) if check.find_line(rel, anchor) is None]
    assert missing == []
