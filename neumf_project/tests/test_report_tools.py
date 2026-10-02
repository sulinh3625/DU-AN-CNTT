"""Công cụ báo cáo: 15_export_report.py (macro + câu tự sinh), 18_preflight.py, 19_check_report.py."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


export = _load("export_report", "15_export_report.py")
preflight = _load("preflight", "18_preflight.py")
check = _load("check_report", "19_check_report.py")
NOT_SIG = "không khác biệt có ý nghĩa"


def _sig(rows):
    return pd.DataFrame(rows, columns=["A", "B", "diff", "rel_diff", "p_holm", "verdict"])


def test_ranks_ties_share_best_position():
    assert export.ranks({"a": 3.0, "b": 2.0, "c": 3.0, "d": 1.0}) == {"a": 1, "b": 3, "c": 1, "d": 4}


def test_family_summary_none_significant():
    s = _sig([("UserKNN", "NeuMF-Scratch", 0.001, 0.1, 0.2, NOT_SIG)])
    vn, en = export.family_summary(s, "họ mở rộng")
    assert vn.startswith("Không so sánh nào trong 1 so sánh của họ mở rộng")
    assert en.startswith("none of the 1 comparisons")


def test_family_summary_lists_significant_with_direction():
    s = _sig([("UserKNN", "NeuMF-Scratch", 0.003, 0.253, 0.001, "A tốt hơn"),
              ("LateFusion-GMF-MLP", "MLP", -0.001, -0.12, 0.03, "B tốt hơn"),
              ("ItemKNN", "NeuMF-Scratch", 0.0001, 0.01, 0.9, NOT_SIG)])
    vn, en = export.family_summary(s, "họ mở rộng")
    assert vn.startswith("2/3 so sánh")
    assert "UserKNN cao hơn NeuMF-Scratch 25{,}3\\%" in vn
    assert "Late Fusion GMF + MLP thấp hơn MLP 12{,}0\\%" in vn
    assert "UserKNN outperforms NeuMF-Scratch" in en and "underperforms MLP" in en
    assert export.verdict_phrase(s.iloc[1]) == "MLP tốt hơn có ý nghĩa"
    assert export.verdict_phrase(s.iloc[2]) == NOT_SIG


def test_export_extension_tables_and_macros(tmp_path, monkeypatch):
    final = tmp_path / "final"
    (final / "extension").mkdir(parents=True)
    cols = [f"{m}_{s}" for m in export.METRICS for s in ("mean", "std")]
    main = pd.DataFrame([[0.010 - 0.0005 * i, 0.0] * 5 for i in range(len(export.ORDER))],
                        index=export.ORDER, columns=cols)
    main.to_csv(final / "summary.csv")
    ext = pd.DataFrame([[0.0105, 0.0001] * 5, [0.0098, 0.0001] * 5, [0.0120, 0.0] * 5, [0.0130, 0.0] * 5],
                       index=export.EXT_ORDER, columns=cols)
    ext.to_csv(final / "extension" / "summary.csv")
    sig = pd.DataFrame([dict(A="UserKNN", B="NeuMF-Scratch", mean_A=0.013, mean_B=0.0095, diff=0.0035,
                             rel_diff=0.37, ci_low=0.001, ci_high=0.006, n_users=10, p_wilcoxon=0.001,
                             p_holm=0.007, verdict="A tốt hơn")])
    sig.to_csv(final / "extension" / "significance.csv", index=False)
    monkeypatch.setattr(export, "FINAL", final)
    m = export.Macros()
    files = dict(export.export_extension(m))
    text = "\n".join(m.lines)
    assert set(files) == {"tab_extension.tex", "tab_ext_significance.tex"}
    assert r"UserKNN$^{\dagger}$" in files["tab_extension.tex"]
    assert r"\csname ext-UKNN-rank\endcsname{thứ nhất}" in text  # 0,0130 cao nhất trong 11 mô hình
    assert r"\csname ext-all-best\endcsname{UserKNN}" in text
    assert r"\csname esig-UKNNScr-verdict\endcsname{UserKNN tốt hơn có ý nghĩa}" in text
    assert "esig-all-summary" in text and "esig-all-summaryen" in text


def test_preflight_git_status_keeps_first_file_name(monkeypatch):
    monkeypatch.setattr(preflight, "git", lambda *a: " M README.md\n M neumf_project/run.py")
    r = preflight.Report()
    preflight.check_git(r)
    assert r.errors and "README.md, neumf_project/run.py" in r.errors[0]


@pytest.fixture(scope="module")
def data():
    d = check.Data()
    if d.S is None or d.G is None:
        pytest.skip("Chưa có outputs/final/summary.csv, significance.csv")
    return d


def test_report_claims_hold_on_committed_results(data):
    failed = [desc for _, _, desc, pred, needs in check.claims(data)
              if all(getattr(data, n) is not None for n in needs) and not pred()]
    assert failed == []


def test_report_claims_detect_changed_ranking(data):
    """Đổi chỗ BPR-MF và NeuMF-Pretrained -> các câu 'BPR-MF cao nhất' phải bị báo sai."""
    s = data.S.copy()
    s.loc[["BPR-MF", "NeuMF-Pretrained"]] = s.loc[["NeuMF-Pretrained", "BPR-MF"]].to_numpy()
    data.S = s
    try:
        failed = {desc for _, _, desc, pred, needs in check.claims(data) if not pred()}
    finally:
        data.S = check.Data().S
    assert "BPR-MF cao nhất NDCG@10" in failed
    assert "BPR-MF cao nhất ở cả 5 độ đo" in failed


def test_report_claim_anchors_exist_in_report():
    missing = [(rel, anchor) for rel, anchor, *_ in check.claims(check.Data()) if check.find_line(rel, anchor) is None]
    assert missing == []
