"""Đánh giá cuối v2 (scripts/23_final_v2.py) và phân tích (scripts/24_report_v2.py): khoá kiểm thử, phân tích độ nhạy
"chỉ sản phẩm cũ", tiêu chí kết luận và họ so sánh đã đăng ký."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


final = _load("final_v2", "23_final_v2.py")
report = _load("report_v2", "24_report_v2.py")


def _args(**kw):
    base = dict(reason="đánh giá cuối", seeds=[42], allow_rerun=False, allow_code_change=False,
                max_epochs=final.V.CFG["training"]["max_epochs"], models=None, skip_ablation=False)
    return SimpleNamespace(**{**base, **kw})


# ------------------------------------------------------------------ khoá kiểm thử
def test_opened_seeds_reads_only_v2_final_tags(tmp_path, monkeypatch):
    log = tmp_path / "test_access_log.csv"
    log.write_text("time,git_commit,git_dirty,config_hash,config_path,run_tag,models,reason\n"
                   "t,c,False,h,p,final_seed2025,M,r\n"          # nhật ký của giao thức v1: không tính
                   "t,c,False,h,p,v2_final_seed2024,M,r\n"
                   "t,c,False,h,p,v2_final_seed42_rerun,M,r\n", encoding="utf-8")
    monkeypatch.setattr(final, "TEST_LOG", log)
    assert final.opened_seeds() == {2024, 42}


def test_lock_lists_every_violation(monkeypatch):
    monkeypatch.setattr(final, "prereg_committed", lambda p: False)
    monkeypatch.setattr(final, "git", lambda *a: "src/new_model.py\nscripts/ghi_chu.txt\n")
    monkeypatch.setattr(final, "tuning_code_hashes", lambda: {"aaa"})
    monkeypatch.setattr(final, "opened_seeds", lambda: {42})
    monkeypatch.setattr(final, "dirty_files", lambda: ["neumf_project/src/models/neumf.py"])
    errs = "\n".join(final.lock_errors(_args(reason=" ", seeds=[42, 2024], max_epochs=1),
                                       {"git_dirty": True, "code_hash": "bbb"}, best={"bpr": {}}))
    for frag in ("PREREG_v2.md chưa commit", "--reason", "chưa commit", "src/new_model.py", "chưa tinh chỉnh xong",
                 "mã nguồn khác lúc tinh chỉnh", "seed [42]", "--max-epochs"):
        assert frag in errs
    assert "ghi_chu.txt" not in errs  # chỉ chặn file mã nguồn chưa theo dõi


def test_lock_passes_and_overrides_are_explicit(monkeypatch):
    monkeypatch.setattr(final, "prereg_committed", lambda p: True)
    monkeypatch.setattr(final, "git", lambda *a: "")
    monkeypatch.setattr(final, "tuning_code_hashes", lambda: {"abc"})
    monkeypatch.setattr(final, "opened_seeds", lambda: {42})
    monkeypatch.setattr(final, "dirty_files", lambda: [])
    best = {m: {} for m in final.TUNED}
    ok = {"git_dirty": False, "code_hash": "abc"}
    assert final.lock_errors(_args(seeds=[2024]), ok, best) == []
    assert final.lock_errors(_args(seeds=[42]), ok, best)                      # seed đã mở tập kiểm thử
    assert final.lock_errors(_args(seeds=[42], allow_rerun=True), ok, best) == []
    changed = {"git_dirty": False, "code_hash": "khac"}
    assert final.lock_errors(_args(seeds=[2024]), changed, best)
    assert final.lock_errors(_args(seeds=[2024], allow_code_change=True), changed, best) == []


def test_dirty_files_ignores_outputs_and_test_log(monkeypatch):
    status = (' M neumf_project/audit/test_access_log.csv\n M neumf_project/outputs/v2/final/summary.csv\n'
              ' M neumf_project/scripts/v2_common.py\n M "Report DACNTT/content/C4.tex"\n D .vscode/settings.json\n')
    monkeypatch.setattr(final, "git", lambda *a: "neumf_project/\n" if a[0] == "rev-parse" else status)
    assert final.dirty_files() == ["neumf_project/scripts/v2_common.py", "Report DACNTT/content/C4.tex",
                                   ".vscode/settings.json"]


def test_final_runs_every_registered_model():
    assert final.MODELS[0] == "random" and set(final.TUNED) == set(final.MODELS) - {"random"}
    assert {"neumf_f", "late_f", "gmf_f", "mlp_f", "neumf", "bpr", "itemknn", "userknn", "recent_pop",
            "content"} <= set(final.MODELS)
    assert set(report.MODELS) == set(final.MODELS)


# ---------------------------------------------------------- độ nhạy: chỉ sản phẩm cũ
def test_old_only_records_drop_new_items_from_candidates_and_targets():
    stage = SimpleNamespace(targets=pd.DataFrame({"user": [0, 0, 1], "item": [1, 3, 3], "day": [5, 5, 5]}),
                            scoreable=np.array([True, True, True, False]), train_pos=[{0}, {2}])
    recs = final.old_only_records(stage, SimpleNamespace(n_items=4))
    assert [r.user for r in recs] == [0]  # user 1 chỉ có sản phẩm đúng mới -> ra khỏi phân tích
    assert recs[0].positives.tolist() == [1]
    assert sorted(recs[0].candidates.tolist()) == [1, 2]  # bỏ item 3 (mới) và item 0 (đã mua)


def test_beyond_counts_coverage_and_new_share():
    stage = SimpleNamespace(scoreable=np.array([1, 1, 1, 0, 0], bool), new=np.array([0, 0, 0, 1, 1], bool))
    out = final.beyond({0: [0, 3], 1: [0, 1]}, stage, k=2)
    assert out["coverage@2"] == 3 / 5 and out["new_share@2"] == 0.25


# ------------------------------------------------------------------ kiểm định
def test_verdict_requires_all_three_conditions():
    assert report.verdict(0.01, 0.001, 0.002, 0.10, 0.0015) == "A tốt hơn"
    assert report.verdict(0.01, -0.002, -0.001, -0.10, -0.0015) == "B tốt hơn"
    assert report.verdict(0.10, 0.001, 0.002, 0.10, 0.0015) == report.NOT_SIG   # p Holm quá lớn
    assert report.verdict(0.01, -0.001, 0.002, 0.10, 0.0005) == report.NOT_SIG  # CI chứa 0
    assert report.verdict(0.01, 0.001, 0.002, 0.03, 0.0015) == report.NOT_SIG   # chênh lệch < 5%


def test_holm_adjustment():
    assert np.allclose(report.holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])


def test_significance_uses_registered_family_and_detects_clear_winner():
    rng = np.random.default_rng(0)
    base = rng.random(300) * 0.1
    um = pd.DataFrame({m: base + rng.normal(0, 1e-3, len(base)) for m in report.MODELS})
    um["neumf_f"] = base + 0.05
    sig = report.significance(um)
    assert list(zip(sig["A"], sig["B"])) == report.COMPARISONS and sig["id"].tolist() == list(range(1, 11))
    assert (sig.loc[sig["A"] == "neumf_f", "verdict"] == "A tốt hơn").all()
    assert sig.iloc[-1]["verdict"] == report.NOT_SIG  # NeuMF vs BPR-MF: chỉ khác nhau do nhiễu
    assert (sig["p_holm"] >= sig["p_wilcoxon"]).all()
