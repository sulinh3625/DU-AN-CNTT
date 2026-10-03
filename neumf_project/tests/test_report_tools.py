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
ablation = _load("ablation", "20_ablation.py")
NOT_SIG = "không khác biệt có ý nghĩa"


# ---------------------------------------------------------------- ablation (20_ablation.py, 15_export_report.py)
def test_ablation_tower_matches_main_models_and_mlp0():
    assert ablation.tower(64, 3) == ablation.tune.mlp_layers(64) == [128, 64, 32, 16]
    assert ablation.tower(64, 0) == [128]          # MLP-0: chỉ nối hai embedding
    assert ablation.tower(8, 4) == [16, 8, 4, 2, 1]


def test_ablation_configs_change_one_factor_at_a_time():
    base = dict(embedding_dim=64, n_hidden=3, negative_ratio=4, lr=5e-4, weight_decay=1e-6, dropout=0.2)
    cfgs = ablation.ablation_configs(base)
    assert len(cfgs) == 1 + 4 + 4 + 3
    for c in cfgs[1:]:
        changed = [k for k in ("embedding_dim", "n_hidden", "negative_ratio") if c[k] != base[k]]
        assert changed == [c["factor"]] and c[c["factor"]] == c["value"]
        assert (c["lr"], c["weight_decay"], c["dropout"]) == (base["lr"], base["weight_decay"], base["dropout"])


def _ablation_frame(layer_scores: dict[int, float]) -> pd.DataFrame:
    rows = [dict(factor="base", value="", embedding_dim=64, n_hidden=3, negative_ratio=4)]
    rows += [dict(factor="embedding_dim", value=str(v), embedding_dim=v, n_hidden=3, negative_ratio=4) for v in (8, 16, 32, 128)]
    rows += [dict(factor="n_hidden", value=str(v), embedding_dim=64, n_hidden=v, negative_ratio=4) for v in (0, 1, 2, 4)]
    rows += [dict(factor="negative_ratio", value=str(v), embedding_dim=64, n_hidden=3, negative_ratio=v) for v in (1, 2, 8)]
    df = pd.DataFrame(rows)
    df["NDCG@10"] = [layer_scores.get(r.n_hidden, 0.009) if r.factor in ("n_hidden", "base") else 0.009
                     for r in df.itertuples()]
    for col in ("Recall@10", "HR@10"):
        df[col] = 0.01
    df["best_epoch"], df["n_params"] = 3, 1000
    return df


@pytest.mark.parametrize("scores,phrase", [
    ({0: 0.012, 1: 0.010, 2: 0.010, 3: 0.009, 4: 0.008}, "Bỏ hẳn các tầng ẩn"),
    ({0: 0.008, 1: 0.012, 2: 0.010, 3: 0.009, 4: 0.008}, "Tháp nông với 1 tầng ẩn"),
    ({0: 0.006, 1: 0.007, 2: 0.008, 3: 0.009, 4: 0.012}, "Tháp sâu nhất (4 tầng ẩn)"),
])
def test_ablation_summary_describes_layer_trend(scores, phrase):
    text = export.ablation_summary(_ablation_frame(scores))
    assert phrase in text and "cấu hình đã chọn" in text
    # tài liệu tham khảo chỉ là cơ sở phương pháp: câu tự sinh không so với số liệu/xu hướng của bài báo
    assert not any(w in text for w in ("NCF", "MovieLens", "Pinterest", "bài gốc"))


def test_export_ablation_table_and_macros(tmp_path, monkeypatch):
    path = tmp_path / "ablation_val.csv"
    _ablation_frame({0: 0.008, 1: 0.012, 2: 0.010, 3: 0.009, 4: 0.008}).to_csv(path, index=False)
    monkeypatch.setattr(export, "ABLATION", path)
    m = export.Macros()
    files = dict(export.export_ablation(m))
    text = "\n".join(m.lines)
    assert "tab:ablation" in files["tab_ablation.tex"] and "(chọn)" in files["tab_ablation.tex"]
    assert r"\csname abl-layers-best\endcsname{1}" in text
    assert "abl-all-summary" in text and "abl-base-NDCG10" in text


def test_training_curve_claims():
    rows = []
    for model, ndcg, loss in (("GMF", [0.008, 0.009, 0.0085], [0.5, 0.4, 0.35]),
                              ("MLP", [0.007, 0.0072, 0.0071], [0.6, 0.5, 0.45])):
        rows += [dict(model=model, phase="select", epoch=e + 1, loss=l, **{"NDCG@10": n})
                 for e, (n, l) in enumerate(zip(ndcg, loss))]
    H = pd.DataFrame(rows)
    assert check.stopped_early(H) and check.loss_keeps_falling(H)
    H.loc[(H["model"] == "MLP") & (H["epoch"] == 3), "NDCG@10"] = 0.01   # đỉnh ở epoch cuối -> chưa dừng sớm
    assert not check.stopped_early(H)


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
    assert r"& A tốt hơn \\" in files["tab_ext_significance.tex"]          # ô "Kết luận" gọn; "---" khi không ý nghĩa
    assert "---: không khác biệt có ý nghĩa" in files["tab_ext_significance.tex"]
    assert r"\csname ext-UKNN-rank\endcsname{thứ nhất}" in text  # 0,0130 cao nhất trong 11 mô hình
    assert r"\csname ext-all-best\endcsname{UserKNN}" in text
    assert r"\csname esig-UKNNScr-verdict\endcsname{UserKNN tốt hơn có ý nghĩa}" in text
    assert "esig-all-summary" in text and "esig-all-summaryen" in text


def test_preflight_git_status_keeps_first_file_name(monkeypatch):
    monkeypatch.setattr(preflight, "git", lambda *a: " M README.md\n M neumf_project/run.py")
    r = preflight.Report()
    preflight.check_git(r)
    assert r.errors and "README.md, neumf_project/run.py" in r.errors[0]


def _tuning_log(rows):
    return pd.DataFrame([dict(model=m, params=p, **{f"val_{k}": v for k in preflight.METRICS}) for m, p, v in rows])


def test_preflight_extension_recheck_tolerates_float_noise_only():
    key = "late_bpr_mlp"
    old = _tuning_log([(key, '{"w": 0.3}', 0.009721), (key, '{"w": 0.5}', 0.009708)])
    best = {key: {"params": {"w": 0.3}, "val": {k: 0.009721 for k in preflight.METRICS}}}
    assert preflight.compare_extension(old, old, best, best, key)[0] == "ok"
    # sai khác số học giữa máy đảo thứ tự w = 0,3 / 0,5 (chênh 1,3e-5) -> chỉ cảnh báo, giữ tham số đã đăng ký
    noisy = _tuning_log([(key, '{"w": 0.3}', 0.009700), (key, '{"w": 0.5}', 0.009712)])
    again = {key: {"params": {"w": 0.5}, "val": {k: 0.009712 for k in preflight.METRICS}}}
    status, msg = preflight.compare_extension(old, noisy, best, again, key)
    assert status == "warn" and "{'w': 0.3}" in msg
    drift = _tuning_log([(key, '{"w": 0.3}', 0.0080), (key, '{"w": 0.5}', 0.009708)])
    assert preflight.compare_extension(old, drift, best, best, key)[0] == "fail"
    fewer = _tuning_log([(key, '{"w": 0.3}', 0.009721)])
    assert preflight.compare_extension(old, fewer, best, best, key)[0] == "fail"


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
        failed = {desc for _, _, desc, pred, needs in check.claims(data)
                  if all(getattr(data, n) is not None for n in needs) and not pred()}
    finally:
        data.S = check.Data().S
    assert "BPR-MF cao nhất NDCG@10" in failed
    assert "v1: BPR-MF cao nhất và không biến thể NeuMF nào tốt hơn có ý nghĩa BPR-MF" in failed


def test_check_flags_missing_generated_tables_and_figures(tmp_path, monkeypatch):
    report = tmp_path / "report"
    tables = report / "content" / "tables"
    tables.mkdir(parents=True)
    (report / "content" / "C4.tex").write_text(
        r"\bangketqua{tab_x.tex}{a} \hinhketqua{media/figures/final/x.png}{\textwidth}{c}{fig:x}{b}", encoding="utf-8")
    monkeypatch.setattr(check, "REPORT", report)
    monkeypatch.setattr(check, "TABLES", tables)
    assert check.check_macros_and_tables() == 2
    (tables / "tab_x.tex").write_text("", encoding="utf-8")
    (report / "media" / "figures" / "final").mkdir(parents=True)
    (report / "media" / "figures" / "final" / "x.png").write_bytes(b"")
    assert check.check_macros_and_tables() == 0


def test_report_claim_anchors_exist_in_report():
    missing = [(rel, anchor) for rel, anchor, *_ in check.claims(check.Data()) if check.find_line(rel, anchor) is None]
    assert missing == []
