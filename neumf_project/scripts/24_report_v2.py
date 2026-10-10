"""Phân tích kết quả giao thức v2 và xuất sang báo cáo (audit/PREREG_v2.md mục 6–7).

    python scripts/24_report_v2.py                     # sau scripts/23_final_v2.py
    python scripts/24_report_v2.py --final-dir outputs/v2/dry_run --report-dir <thư mục tạm>   # thử trên bản chạy thử

Đọc outputs/v2/final/ (23_final_v2.py) và audit/v2/best_configs.json (tinh chỉnh trên mẫu A). Tính:
- trung bình ± độ lệch chuẩn qua seed của mọi chỉ số;
- họ 10 so sánh đã đăng ký: NDCG@10 theo người dùng trung bình qua seed, Wilcoxon signed-rank, khoảng tin cậy bootstrap
  ghép cặp 95% (10.000 lần, seed 0), hiệu chỉnh Holm; "tốt hơn" khi p Holm < 0,05, CI không chứa 0 và chênh lệch tương
  đối >= 5%;
- ablation NeuMF-F (seed 42), mô tả top-10 (độ phủ), số epoch và thời gian huấn luyện.
Không còn sản phẩm mới (một sản phẩm = product_code, ứng viên chỉ gồm sản phẩm đã có cặp huấn luyện) nên không còn phân
tích theo nhóm sản phẩm cũ/mới.
Ghi: <final-dir>/{summary,significance,ablation,beyond}.csv, hình <final-dir>/figures/*.png; nếu có
--report-dir (mặc định: Report DACNTT) thì chép hình sang media/figures/v2/ và ghi bảng + macro LaTeX vào content/tables/v2/.
Mọi số của giao thức v2 trong báo cáo lấy từ các file này, không gõ tay.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MaxNLocator
from scipy.stats import wilcoxon

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUDIT = PROJECT_ROOT / "audit" / "v2"
REPORT = PROJECT_ROOT.parent / "Report DACNTT"

MODELS = ["neumf_f", "late_f", "gmf_f", "mlp_f", "neumf", "gmf", "mlp", "bpr", "itemknn", "userknn", "content",
          "recent_pop", "popularity", "random"]
NAME = {"random": "Random", "popularity": "Most Popular", "recent_pop": "MostPopular-Recent", "content": "Content",
        "itemknn": "ItemKNN", "userknn": "UserKNN", "bpr": "BPR-MF", "gmf": "GMF", "mlp": "MLP", "neumf": "NeuMF",
        "gmf_f": "GMF-F", "mlp_f": "MLP-F", "neumf_f": "NeuMF-F", "late_f": "LateFusion-F"}
KEY = {"random": "Rand", "popularity": "Pop", "recent_pop": "RecPop", "content": "Cont", "itemknn": "IKNN",
       "userknn": "UKNN", "bpr": "BPR", "gmf": "GMF", "mlp": "MLP", "neumf": "NeuMF", "gmf_f": "GMFF",
       "mlp_f": "MLPF", "neumf_f": "NeuMFF", "late_f": "LateF"}
ABL = {"neumf_f-text": ("AblText", "Bỏ vector văn bản"), "neumf_f-time": ("AblTime", "Bỏ đặc trưng thời gian"),
       "neumf_f-user": ("AblUser", "Bỏ thông tin khách hàng"), "neumf_f-attr": ("AblAttr", "Bỏ thuộc tính sản phẩm"),
       "neumf_f-iddrop": ("AblIdDrop", "Không bỏ ID ngẫu nhiên")}
GROUP_COLOR = {"Mô hình đề tài (NeuMF-F)": "#2a78d6", "Có đặc trưng: thành phần, Late Fusion": "#8fb8ea",
               "Chỉ dùng ID (NCF)": "#eb6834", "Baseline": "#1baf7a"}
GROUP_OF = {"neumf_f": "Mô hình đề tài (NeuMF-F)", **dict.fromkeys(("gmf_f", "mlp_f", "late_f"),
                                                                  "Có đặc trưng: thành phần, Late Fusion"),
            **dict.fromkeys(("gmf", "mlp", "neumf"), "Chỉ dùng ID (NCF)")}
# Họ so sánh cố định (PREREG_v2 mục 7), theo đúng thứ tự đăng ký.
COMPARISONS = [("neumf_f", "neumf"), ("neumf_f", "gmf_f"), ("neumf_f", "mlp_f"), ("neumf_f", "late_f"),
               ("neumf_f", "bpr"), ("neumf_f", "itemknn"), ("neumf_f", "userknn"), ("neumf_f", "recent_pop"),
               ("neumf_f", "content"), ("neumf", "bpr")]
METRICS = ["NDCG@10", "Recall@10", "HR@10", "Precision@10", "NDCG@5", "NDCG@20"]
TABLE_METRICS = ["NDCG@10", "Recall@10", "HR@10", "Precision@10", "NDCG@5", "NDCG@20"]
NOT_SIG = "không khác biệt có ý nghĩa"
N_BOOT, BOOT_SEED, ALPHA, MIN_REL = 10_000, 0, 0.05, 0.05
INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"
HEADER = "% Sinh tự động bởi neumf_project/scripts/24_report_v2.py — KHÔNG sửa tay."


def group(m: str) -> str:
    return GROUP_OF.get(m, "Baseline")


def mk(metric: str) -> str:
    return metric.replace("@", "").replace("_", "")


# ------------------------------------------------------------------ thống kê
def holm(p) -> np.ndarray:
    p = np.asarray(p, dtype=float)
    order = np.argsort(p)
    adj = np.maximum.accumulate((len(p) - np.arange(len(p))) * p[order]).clip(max=1.0)
    out = np.empty_like(adj)
    out[order] = adj
    return out


def bootstrap_ci(x: np.ndarray, n: int = N_BOOT, seed: int = BOOT_SEED) -> tuple[float, float]:
    """Khoảng tin cậy 95% của trung bình (x là hiệu ghép cặp theo người dùng, hoặc giá trị của một mô hình)."""
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    if len(x) == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    means = np.array([x[rng.integers(0, len(x), len(x))].mean() for _ in range(n)])
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(lo), float(hi)


def verdict(p_holm: float, lo: float, hi: float, rel: float, diff: float) -> str:
    if p_holm < ALPHA and (lo > 0 or hi < 0) and abs(rel) >= MIN_REL:
        return "A tốt hơn" if diff > 0 else "B tốt hơn"
    return NOT_SIG


# --------------------------------------------------------------------- dữ liệu
def load(final_dir: Path):
    seeds = sorted(int(p.name[4:]) for p in final_dir.glob("seed*") if (p / "results.json").exists())
    if not seeds:
        raise SystemExit(f"Chưa có kết quả trong {final_dir} — chạy scripts/23_final_v2.py trước.")
    res = {s: json.loads((final_dir / f"seed{s}" / "results.json").read_text(encoding="utf-8")) for s in seeds}
    per = pd.concat([pd.read_csv(final_dir / f"seed{s}" / "per_user.csv.gz") for s in seeds], ignore_index=True)
    parts = []
    for s in seeds:
        try:
            parts.append(pd.read_csv(final_dir / f"seed{s}" / "history.csv").assign(seed=s))
        except (FileNotFoundError, pd.errors.EmptyDataError):
            pass
    hist = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    models = [m for m in MODELS if all(m in res[s]["results"] for s in seeds)]
    return seeds, res, per, hist, models


def summarize(seeds, res, models, best) -> pd.DataFrame:
    rows = []
    for m in models:
        row = {"model": m, "name": NAME[m], "n_seeds": len(seeds)}
        for metric in METRICS:
            v = np.array([res[s]["results"][m][metric] for s in seeds], dtype=float)
            row[f"{metric}_mean"], row[f"{metric}_std"] = float(np.mean(v)), float(np.std(v, ddof=1)) if len(v) > 1 else 0.0
        row["val_NDCG@10"] = best.get(m, {}).get("val", {}).get("NDCG@10", np.nan)
        rows.append(row)
    return pd.DataFrame(rows).sort_values("NDCG@10_mean", ascending=False).reset_index(drop=True)


def user_matrix(per: pd.DataFrame, models: list[str], metric: str = "NDCG@10") -> pd.DataFrame:
    """Người dùng × mô hình: chỉ số trung bình qua seed (mô hình tất định: giá trị như nhau ở mọi seed)."""
    return per[per["model"].isin(models)].groupby(["model", "user"])[metric].mean().unstack("model")


def significance(um: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for i, (a, b) in enumerate(COMPARISONS, 1):
        if a not in um or b not in um:
            continue
        d = (um[a] - um[b]).to_numpy()
        ma, mb = float(um[a].mean()), float(um[b].mean())
        lo, hi = bootstrap_ci(d)
        p = float(wilcoxon(d).pvalue) if np.any(d != 0) else 1.0
        rows.append(dict(id=i, A=a, B=b, mean_A=ma, mean_B=mb, diff=float(d.mean()),
                         rel_diff=(ma - mb) / mb if mb else np.nan, ci_low=lo, ci_high=hi, n_users=len(d),
                         n_nonzero=int(np.count_nonzero(d)), p_wilcoxon=p))
    sig = pd.DataFrame(rows)
    if sig.empty:
        return sig
    sig["p_holm"] = holm(sig["p_wilcoxon"])
    sig["verdict"] = [verdict(r.p_holm, r.ci_low, r.ci_high, r.rel_diff, r.diff) for r in sig.itertuples()]
    return sig


def ablation(per: pd.DataFrame, res: dict) -> pd.DataFrame:
    s = 42 if 42 in res else min(res)
    present = [k for k in ABL if k in res[s]["results"]]
    if "neumf_f" not in res[s]["results"] or not present:
        return pd.DataFrame()
    p = per[per["seed"] == s]
    um = p[p["model"].isin(["neumf_f", *present])].pivot(index="user", columns="model", values="NDCG@10")
    full = res[s]["results"]["neumf_f"]
    rows = [dict(variant="neumf_f", seed=s, **{"NDCG@10": full["NDCG@10"]}, rel=0.0, ci_low=0.0, ci_high=0.0)]
    for k in present:
        r = res[s]["results"][k]
        lo, hi = bootstrap_ci((um[k] - um["neumf_f"]).to_numpy())
        rows.append(dict(variant=k, seed=s, **{"NDCG@10": r["NDCG@10"]},
                         rel=(r["NDCG@10"] - full["NDCG@10"]) / full["NDCG@10"], ci_low=lo, ci_high=hi))
    return pd.DataFrame(rows)


def beyond(seeds, res, models) -> pd.DataFrame:
    s = 42 if 42 in res else seeds[0]
    rows = []
    for m in models:
        meta = [res[x]["train_meta"].get(m, {}) for x in seeds]
        ep = [d["best_epoch"] for d in meta if "best_epoch" in d]
        t = [d.get("select_time_s", 0) + d.get("refit_time_s", 0) + d.get("fit_time_s", 0) for d in meta]
        b = res[s].get("beyond", {}).get(m, {})
        rows.append(dict(model=m, coverage10=b.get("coverage@10", np.nan),
                         best_epoch_mean=float(np.mean(ep)) if ep else np.nan,
                         best_epochs=";".join(map(str, ep)), train_min=float(np.mean(t)) / 60))
    return pd.DataFrame(rows)


def dev_info() -> dict:
    """Mô tả mẫu A ở giai đoạn xác thực (lưu đệm audit/v2/data_dev.json; không dựng tập kiểm thử của A)."""
    path = AUDIT / "data_dev.json"
    if not path.exists():
        import v2_common as V
        from src.data_pipeline.protocol_v2 import describe

        D = V.load_data("dev", with_test=False)
        path.write_text(json.dumps(dict(sample=D.meta["sample"], **describe(D)), indent=2, ensure_ascii=False),
                        encoding="utf-8")
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------- LaTeX
def vn(x: float, nd: int = 5, sign: bool = False) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "---"
    text = f"{abs(x):.{nd}f}".replace(".", "{,}")
    return ("$-$" if x < 0 else "+" if sign else "") + text


def pct(x: float, nd: int = 1) -> str:
    return vn(x * 100, nd, sign=True) + r"\%"


def thousands(n: int) -> str:
    return f"{int(n):,}".replace(",", ".")


def pval(p: float) -> str:
    return "$<$ 0{,}001" if p < 0.001 else vn(p, 3)


def num(x) -> str:
    if x is None:
        return "không trọng số"
    if isinstance(x, float) and x and abs(x) < 1e-4:
        return f"$10^{{{int(round(np.log10(abs(x))))}}}$"
    return f"{x:g}".replace(".", "{,}")


def params_text(m: str, p: dict) -> str:
    if not p:
        return "---"
    if m == "recent_pop":
        return f"cửa sổ {p['window']} ngày"
    if m == "content":
        return "không trọng số theo thời gian" if p["half_life"] is None else f"chu kỳ bán rã {p['half_life']} ngày"
    if m in ("itemknn", "userknn"):
        return f"k={p['k']}; shrink={num(p['shrink'])}"
    if m == "bpr":
        return f"d={p['embedding_dim']}; lr={num(p['lr'])}; reg={num(p['reg'])}; {p['epochs']} epoch"
    if m == "late_f":
        return f"$w$={num(p['w'])} (GMF-F), $1-w$={num(round(1 - p['w'], 1))} (MLP-F)"
    parts = [f"d={p['embedding_dim']}", f"lr={num(p['lr'])}", f"neg={p['negative_ratio']}",
             f"wd={num(p['weight_decay'])}"]
    if "dropout" in p:
        parts.append(f"dropout={num(p['dropout'])}")
    if "id_dropout" in p:
        parts.append(f"bỏ ID={num(p['id_dropout'])}")
    return "; ".join(parts)


def table(label: str, caption: str, colspec: str, header: list[str], rows: list[list[str]], note: str = "") -> str:
    body = "\n".join("        " + " & ".join(r) + r" \\" for r in rows)
    note_tex = f"\n    \\par\\smallskip{{\\footnotesize {note}}}" if note else ""
    return (f"{HEADER}\n\\begin{{table}}[htbp]\n    \\centering\\small\n"
            f"    \\caption{{{caption}}}\n    \\label{{{label}}}\n"
            "    \\begin{adjustbox}{max width=\\textwidth}\n"
            f"    \\begin{{tabular}}{{{colspec}}}\n        \\toprule\n"
            f"        {' & '.join(header)} \\\\\n        \\midrule\n{body}\n        \\bottomrule\n"
            f"    \\end{{tabular}}\n    \\end{{adjustbox}}{note_tex}\n\\end{{table}}\n")


class Macros:
    # vonly, vgrp (phân tích cũ/mới) không còn được ghi — giữ lệnh \VOnly, \VGrp để báo cáo cũ vẫn biên dịch được
    FAMILIES = {"vres": "VRes", "vsd": "VSd", "vonly": "VOnly", "vval": "VVal", "vrank": "VRank", "vsig": "VSig",
                "vgrp": "VGrp", "vabl": "VAbl", "vbey": "VBey", "vdata": "VData", "vcfg": "VCfg"}

    def __init__(self):
        self.lines = [HEADER, r"\providecommand{\resultmacro}[3]{\ifcsname #1-#2-#3\endcsname\csname #1-#2-#3\endcsname"
                              r"\else\textbf{[chưa có]}\fi}"]
        self.lines += [rf"\providecommand{{\{cmd}}}[2]{{\resultmacro{{{fam}}}{{#1}}{{#2}}}}"
                       for fam, cmd in self.FAMILIES.items()]

    def add(self, family: str, a: str, b: str, value: str):
        if family not in self.FAMILIES:
            raise KeyError(family)
        self.lines.append(rf"\expandafter\def\csname {family}-{a}-{b}\endcsname{{{value}}}")

    def write(self, path: Path):
        path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")


ORDINAL = {1: "thứ nhất", 2: "thứ hai", 3: "thứ ba", 4: "thứ tư", 5: "thứ năm", 6: "thứ sáu", 7: "thứ bảy",
           8: "thứ tám", 9: "thứ chín", 10: "thứ mười", 11: "thứ mười một", 12: "thứ mười hai", 13: "thứ mười ba",
           14: "thứ mười bốn"}


def phrase(r) -> str:
    if r["verdict"] == NOT_SIG:
        return NOT_SIG
    winner = r["A"] if r["verdict"] == "A tốt hơn" else r["B"]
    return f"{NAME[winner]} tốt hơn có ý nghĩa"


def family_summary(sig: pd.DataFrame) -> tuple[str, str]:
    hits = sig[sig["verdict"] != NOT_SIG]
    n = len(sig)
    if hits.empty:
        return (f"Không so sánh nào trong {n} so sánh đã đăng ký đạt tiêu chí ``tốt hơn''.",
                f"none of the {n} comparisons meets the criterion")
    vn_parts = [f"{NAME[r.A]} {'cao' if r.diff > 0 else 'thấp'} hơn {NAME[r.B]} {vn(abs(r.rel_diff) * 100, 1)}\\% "
                f"($p_{{Holm}}$ {pval(r.p_holm) if r.p_holm < 0.001 else '= ' + pval(r.p_holm)})"
                for r in hits.itertuples()]
    en_parts = [f"{NAME[r.A]} {'outperforms' if r.diff > 0 else 'underperforms'} {NAME[r.B]}"
                for r in hits.itertuples()]
    return (f"{len(hits)}/{n} so sánh đã đăng ký đạt tiêu chí ``tốt hơn'': " + "; ".join(vn_parts) + ".",
            f"{len(hits)} of the {n} comparisons meet the criterion: " + "; ".join(en_parts))


def export_data(m: Macros, tables: Path, info_a: dict, info_b: dict | None) -> None:
    """Quy mô dữ liệu. info_b = None trước đánh giá cuối (mẫu B chưa được dựng)."""
    ta, tb = info_a, info_b or {}

    def cell(t, *keys, fmt=thousands):
        v = t
        for k in keys:
            if not isinstance(v, dict) or k not in v:
                return "---"
            v = v[k]
        return fmt(v)

    rows = [
        ["Người dùng sau lọc 10-core", cell(ta, "n_users"), cell(tb, "n_users")],
        ["Sản phẩm (product\\_code) sau lọc 10-core", cell(ta, "n_items"), cell(tb, "n_items")],
        ["Cặp (khách, sản phẩm) trước mốc kiểm thử", cell(ta, "n_kept_pairs"), cell(tb, "n_kept_pairs")],
        ["Xác thực: cặp huấn luyện (trước 01/07/2020)", cell(ta, "val", "train_pairs"), cell(tb, "val", "train_pairs")],
        ["Xác thực: người dùng được đánh giá", cell(ta, "val", "users"), cell(tb, "val", "users")],
        ["Xác thực: cặp đúng", cell(ta, "val", "targets"), cell(tb, "val", "targets")],
        ["Kiểm thử: người dùng được đánh giá", "---", cell(tb, "test", "users")],
        ["Kiểm thử: cặp đúng", "---", cell(tb, "test", "targets")],
        ["Kiểm thử: số ứng viên trung bình mỗi người dùng", "---",
         cell(tb, "test", "candidates_mean", fmt=lambda v: thousands(round(v)))],
    ]
    for nm, t in (("A", ta), ("B", tb)):
        for k in ("n_users", "n_items", "n_id_items", "n_kept_pairs"):
            if k in t:
                m.add("vdata", nm, k.replace("_", ""), thousands(t[k]))
        if "val" in t:
            for k in ("users", "targets", "train_pairs"):
                m.add("vdata", f"{nm}val", k.replace("_", ""), thousands(t["val"][k]))
            m.add("vdata", f"{nm}val", "cand", thousands(round(t["val"]["candidates_mean"])))
    if "test" in tb:
        for k in ("users", "targets", "scoreable", "train_pairs"):
            m.add("vdata", "Btest", k.replace("_", ""), thousands(tb["test"][k]))
        m.add("vdata", "Btest", "cand", thousands(round(tb["test"]["candidates_mean"])))
    note = ("Một sản phẩm = một product\\_code (gộp mọi màu). Lọc 10-core chỉ trên các cặp trước mốc kiểm thử "
            "29/07/2020. Ứng viên và cặp đúng chỉ gồm sản phẩm đã có cặp huấn luyện trước mốc của giai đoạn. Tập "
            "kiểm thử của mẫu A không được dựng.")
    if not tb:
        note += " Mẫu B chỉ được dựng ở lần đánh giá cuối."
    (tables / "tab_v2_data.tex").write_text(table(
        "tab:v2data", "Quy mô dữ liệu theo giao thức v2: mẫu phát triển A (chỉ dùng tập xác thực) và mẫu kiểm định B "
        "(khách hàng khác hẳn A)", "lrr", ["", "Mẫu A (phát triển)", "Mẫu B (kiểm định)"], rows, note),
        encoding="utf-8")


def export_tuning(m: Macros, tables: Path, best: dict) -> None:
    """Cấu hình tốt nhất trên tập xác thực của mẫu A + thống kê nhật ký tinh chỉnh."""
    rows = []
    for mm in [x for x in MODELS if x in best]:
        v = best[mm]["val"]
        rows.append([NAME[mm], params_text(mm, best[mm]["params"]), vn(v["NDCG@10"]), vn(v.get("HR@10"))])
        for c in ("NDCG@10", "Recall@10", "HR@10"):
            if c in v:
                m.add("vval", KEY[mm], mk(c), vn(v[c]))
        m.add("vcfg", KEY[mm], "params", params_text(mm, best[mm]["params"]))
        if best[mm].get("best_epoch") is not None:
            m.add("vcfg", KEY[mm], "epoch", str(best[mm]["best_epoch"]))
    log = AUDIT / "tuning_log.csv"
    if log.exists():
        t = pd.read_csv(log)
        m.add("vcfg", "all", "nconfigs", str(len(t)))
        m.add("vcfg", "all", "hours", vn(t["time_s"].sum() / 3600, 1))
        m.add("vcfg", "all", "codehashes", str(t["code_hash"].nunique()))
        neural = t[t["best_epoch"].notna()]
        if len(neural):
            m.add("vcfg", "all", "nneural", str(len(neural)))
            m.add("vcfg", "all", "epochmax", str(int(neural["best_epoch"].max())))
            m.add("vcfg", "all", "epochmedian", vn(float(neural["best_epoch"].median()), 0))
    (tables / "tab_v2_tuning.tex").write_text(table(
        "tab:v2tuning", "Cấu hình tốt nhất của từng mô hình trên tập xác thực của mẫu A (seed 42; 6 cấu hình mỗi mô "
        "hình có học, mô hình một tham số thử đủ lưới)", "llrr",
        ["Mô hình", "Cấu hình chọn", "NDCG@10", "HR@10"], rows,
        "d: số chiều embedding; neg: số mẫu âm mỗi mẫu dương; wd: weight decay; bỏ ID: xác suất bỏ embedding ID của "
        "sản phẩm khi huấn luyện. Số trên tập xác thực dùng để chọn cấu hình, không dùng để kết luận."),
        encoding="utf-8")


def tex_escape(text: str) -> str:
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("_", r"\_"), ("#", r"\#"),
                 ("(R)", ""), ("(TM)", "")):
        text = text.replace(a, b)
    return " ".join(text.split())


def export_run(m: Macros, seeds, res) -> None:
    """Thông tin lần đánh giá cuối: máy, phiên bản, thời gian chạy, commit."""
    first = res[seeds[0]]
    mach, prov = first.get("machine", {}), first.get("provenance", {})
    m.add("vdata", "run", "cpu", tex_escape(str(mach.get("cpu", ""))))
    m.add("vdata", "run", "gpu", tex_escape(str(mach.get("gpu") or "không có")))
    m.add("vdata", "run", "device", "GPU" if "cuda" in str(mach.get("device", "")) else "CPU")
    m.add("vdata", "run", "torch", tex_escape(str(mach.get("torch", ""))))
    m.add("vdata", "run", "python", tex_escape(str(mach.get("python", ""))))
    m.add("vdata", "run", "hours", vn(sum(res[s].get("elapsed_min", 0) for s in seeds) / 60, 1))
    m.add("vdata", "run", "commit", str(prov.get("git_commit") or "")[:7])
    m.add("vdata", "run", "codehash", str(prov.get("code_hash", "")))
    m.add("vdata", "run", "seedlist", ", ".join(map(str, seeds)))


def export_results(m: Macros, tables: Path, seeds, summary, sig, abl, bey, info_b) -> None:
    n_seed = len(seeds)
    models = summary["model"].tolist()
    by = summary.set_index("model")
    rank = {mm: i + 1 for i, mm in enumerate(models)}

    # Kết quả chính
    best_val = {c: by[f"{c}_mean"].max() for c in TABLE_METRICS}
    rows = []
    for mm in models:
        r = [NAME[mm]]
        for c in TABLE_METRICS:
            mean, sd = by.loc[mm, f"{c}_mean"], by.loc[mm, f"{c}_std"]
            cell = vn(mean)
            if mean == best_val[c]:
                cell = rf"\textbf{{{cell}}}"
            r.append(cell + rf"\,{{\scriptsize$\pm$\,{vn(sd)}}}")
        rows.append(r)
        for c in METRICS:
            m.add("vres", KEY[mm], mk(c), vn(by.loc[mm, f"{c}_mean"]))
            m.add("vsd", KEY[mm], mk(c), vn(by.loc[mm, f"{c}_std"]))
        m.add("vrank", KEY[mm], "NDCG10", ORDINAL.get(rank[mm], str(rank[mm])))
    n_users = info_b.get("test", info_b["val"])["users"]
    (tables / "tab_v2_main.tex").write_text(table(
        "tab:v2main", f"Kết quả trên tập kiểm thử của mẫu B: trung bình $\\pm$ độ lệch chuẩn qua {n_seed} seed "
        f"(xếp hạng trên toàn bộ tập ứng viên; {thousands(n_users)} người dùng)",
        "l" + "r" * len(TABLE_METRICS), ["Mô hình", *TABLE_METRICS], rows,
        "In đậm: trung bình cao nhất mỗi cột. Mô hình tất định (Most Popular, MostPopular-Recent, Content, ItemKNN, "
        "UserKNN) cho cùng kết quả ở mọi seed."), encoding="utf-8")
    m.add("vdata", "run", "seeds", str(n_seed))

    # Kiểm định
    if not sig.empty:
        rows = []
        for r in sig.itertuples():
            rows.append([str(r.id), NAME[r.A], NAME[r.B], vn(r.mean_A), vn(r.mean_B), pct(r.rel_diff),
                         f"[{vn(r.ci_low, sign=True)}; {vn(r.ci_high, sign=True)}]", pval(r.p_holm),
                         "---" if r.verdict == NOT_SIG else r.verdict])
            for k, v in (("rel", pct(r.rel_diff)), ("diff", vn(r.diff, sign=True)), ("lo", vn(r.ci_low, sign=True)),
                         ("hi", vn(r.ci_high, sign=True)), ("pholm", pval(r.p_holm)), ("p", pval(r.p_wilcoxon)),
                         ("verdict", r.verdict), ("phrase", phrase(r._asdict()))):
                m.add("vsig", str(r.id), k, v)
        s_vn, s_en = family_summary(sig)
        m.add("vsig", "all", "summary", s_vn)
        m.add("vsig", "all", "summaryEN", s_en)
        m.add("vsig", "all", "nsig", str(int((sig["verdict"] != NOT_SIG).sum())))
        m.add("vsig", "all", "n", str(len(sig)))
        (tables / "tab_v2_sig.tex").write_text(table(
            "tab:v2sig", f"Kiểm định họ {len(sig)} so sánh đã đăng ký trước trên NDCG@10 (mẫu B, mỗi người dùng lấy "
            f"trung bình qua {n_seed} seed): Wilcoxon signed-rank, hiệu chỉnh Holm, khoảng tin cậy bootstrap 95\\%",
            "rllrrrcrc", ["\\#", "A", "B", "NDCG@10 A", "NDCG@10 B", "(A$-$B)/B", "CI 95\\% của A$-$B", "p Holm",
                          "Kết luận"], rows,
            "---: không khác biệt có ý nghĩa. ``A tốt hơn'' (hoặc ``B tốt hơn'') chỉ khi đồng thời p Holm $<$ 0,05, "
            "CI không chứa 0 và chênh lệch tương đối $\\geq$ 5\\%."), encoding="utf-8")

    # Ablation
    if not abl.empty:
        rows = []
        for _, r in abl.iterrows():
            full = r["variant"] == "neumf_f"
            name = "NeuMF-F (đầy đủ)" if full else ABL[r["variant"]][1]
            ci = "---" if full else f"[{vn(r['ci_low'], sign=True)}; {vn(r['ci_high'], sign=True)}]"
            rows.append([name, vn(r["NDCG@10"]), "---" if full else pct(r["rel"]), ci])
            if not full:
                key = ABL[r["variant"]][0]
                m.add("vabl", key, "NDCG10", vn(r["NDCG@10"]))
                m.add("vabl", key, "rel", pct(r["rel"]))
                m.add("vabl", key, "lo", vn(r["ci_low"], sign=True))
                m.add("vabl", key, "hi", vn(r["ci_high"], sign=True))
        m.add("vabl", "Full", "NDCG10", vn(abl.iloc[0]["NDCG@10"]))
        (tables / "tab_v2_ablation.tex").write_text(table(
            "tab:v2ablation", f"Ablation của NeuMF-F trên tập kiểm thử của mẫu B (seed {int(abl.iloc[0]['seed'])}; "
            "cùng siêu tham số, tắt một thành phần)", "lrrc",
            ["Biến thể", "NDCG@10", "Thay đổi", "CI 95\\% của hiệu"], rows,
            "Thay đổi: (biến thể $-$ đầy đủ)/đầy đủ. CI: bootstrap theo người dùng của hiệu biến thể $-$ đầy đủ. Chỉ "
            "mô tả, không kiểm định. Biến thể trùng NeuMF-F (vd. không bỏ ID ngẫu nhiên khi cấu hình chọn đã có "
            "tỉ lệ bỏ ID bằng 0) không chạy."), encoding="utf-8")

    # Mô tả top-10 và thời gian
    b = bey.set_index("model")
    rows = []
    for mm in models:
        ep = b.loc[mm, "best_epoch_mean"]
        rows.append([NAME[mm], vn(b.loc[mm, "coverage10"] * 100, 1) + r"\%",
                     "---" if np.isnan(ep) else vn(ep, 1), vn(b.loc[mm, "train_min"], 1)])
        m.add("vbey", KEY[mm], "cov", vn(b.loc[mm, "coverage10"] * 100, 1) + r"\%")
        m.add("vbey", KEY[mm], "time", vn(b.loc[mm, "train_min"], 1))
        if not np.isnan(ep):
            m.add("vbey", KEY[mm], "epoch", vn(ep, 1))
    (tables / "tab_v2_beyond.tex").write_text(table(
        "tab:v2beyond", "Mô tả danh sách gợi ý top-10 (seed 42) và chi phí huấn luyện (trung bình qua seed)", "lrrr",
        ["Mô hình", "Độ phủ ứng viên", "Số epoch chọn", "Thời gian (phút)"], rows,
        "Độ phủ: tỉ lệ sản phẩm của không gian ứng viên xuất hiện trong top-10 của ít nhất một người dùng. Số epoch "
        "chọn trên tập xác thực của B trước khi huấn luyện lại. Thời gian: chọn epoch + huấn luyện lại (mạng nơ-ron) "
        "hoặc khớp mô hình, không gồm thời gian chấm."), encoding="utf-8")


def ensure(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


# --------------------------------------------------------------------- hình
def vn_plain(x, nd=4):
    return f"{x:.{nd}f}".replace(".", ",")


def tick_decimals(locs) -> int:
    """Số chữ số thập phân vừa đủ để hai vạch chia liên tiếp khác nhau (0,0005 -> 4; 0,025 -> 3; 0,01 -> 2)."""
    locs = np.asarray(locs, dtype=float)
    step = float(np.min(np.diff(np.sort(locs)))) if len(locs) > 1 else 0.0
    if step <= 0:
        return 3
    for nd in range(0, 8):
        if abs(round(step, nd) - step) <= step * 1e-6:
            return nd
    return 8


def style(ax, axis="x", fmt=None):
    """Kiểu chung của hình; trục số định dạng kiểu Việt Nam với số chữ số thập phân theo bước chia."""
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left" if axis == "x" else "bottom"].set_visible(axis != "x")
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=INK2, labelsize=9, length=0)
    ax.grid(axis=axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    target = ax.xaxis if axis == "x" else ax.yaxis
    target.set_major_locator(MaxNLocator(nbins=5))
    target.set_major_formatter(FuncFormatter(
        lambda v, _: vn_plain(v, fmt if fmt is not None else tick_decimals(target.get_majorticklocs()))))


def plot_metrics(res, seeds, summary, fig_dir: Path, n_users: int):
    models = summary["model"].tolist()
    metrics = ["NDCG@10", "Recall@10", "HR@10"]
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 5.2), sharey=True, facecolor=SURFACE)
    y = np.arange(len(models))
    for ax, c in zip(axes, metrics):
        mean = summary[f"{c}_mean"].to_numpy()
        sd = summary[f"{c}_std"].fillna(0).to_numpy()
        ax.barh(y, mean, height=0.62, color=[GROUP_COLOR[group(mm)] for mm in models], edgecolor=SURFACE, linewidth=2)
        ax.errorbar(mean, y, xerr=sd, fmt="none", ecolor=INK2, elinewidth=1.1, capsize=3)
        for i, mm in enumerate(models):
            pts = [res[s]["results"][mm][c] for s in seeds]
            ax.scatter(pts, [i] * len(pts), s=12, color=INK, zorder=3, linewidths=0)
            ax.text(mean[i] + sd[i] + mean.max() * 0.02, i, vn_plain(mean[i]), va="center", fontsize=8, color=INK)
        ax.set_xlim(0, mean.max() * 1.3)
        ax.set_title(c, fontsize=11, color=INK, loc="left")
        style(ax, "x")
    axes[0].set_yticks(y, [NAME[mm] for mm in models], fontsize=9.5, color=INK)
    axes[0].invert_yaxis()
    handles = [Patch(color=col, label=gname) for gname, col in GROUP_COLOR.items()]
    handles.append(Line2D([], [], marker="o", color=INK, linestyle="none", markersize=4, label="Từng seed"))
    fig.legend(handles=handles, loc="upper center", ncol=5, frameon=False, fontsize=9, bbox_to_anchor=(0.5, 1.0))
    fig.suptitle(f"Tập kiểm thử của mẫu B — trung bình ± độ lệch chuẩn qua {len(seeds)} seed "
                 f"({thousands(n_users)} người dùng)", fontsize=12, color=INK, y=1.07)
    fig.savefig(fig_dir / "v2_metrics.png", dpi=200, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


def plot_significance(sig: pd.DataFrame, fig_dir: Path):
    if sig.empty:
        return
    s = sig.iloc[::-1].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(10, 5), facecolor=SURFACE)
    y = np.arange(len(s))
    colors = ["#2a78d6" if v == "A tốt hơn" else "#eb6834" if v == "B tốt hơn" else MUTED for v in s["verdict"]]
    ax.axvline(0, color=INK2, linewidth=1)
    ax.hlines(y, s["ci_low"], s["ci_high"], color=colors, linewidth=2.2)
    ax.scatter(s["diff"], y, s=42, color=colors, zorder=3, edgecolors=SURFACE, linewidths=2)
    ax.set_yticks(y, [f"{r.id}. {NAME[r.A]}  vs  {NAME[r.B]}" for r in s.itertuples()], fontsize=9.5, color=INK)
    for i, r in s.iterrows():
        p = "< 0,001" if r["p_holm"] < 0.001 else "= " + vn_plain(r["p_holm"], 3)
        ax.text(1.02, i, f"{r['rel_diff'] * 100:+.1f}%".replace(".", ",") + f"   p Holm {p}",
                transform=ax.get_yaxis_transform(), va="center", fontsize=8.5, color=INK2)
    span = max(abs(s["ci_low"].min()), abs(s["ci_high"].max()))
    ax.set_xlim(min(s["ci_low"].min(), 0) - span * 0.08, max(s["ci_high"].max(), 0) + span * 0.08)
    ax.set_xlabel("Hiệu NDCG@10 (A − B), CI 95% bootstrap theo người dùng; xanh: A tốt hơn, cam: B tốt hơn, xám: "
                  "không khác biệt có ý nghĩa", fontsize=8.5, color=INK2)
    n_sig = int((s["verdict"] != NOT_SIG).sum())
    ax.set_title(f"Họ {len(s)} so sánh đã đăng ký: {n_sig} so sánh đạt tiêu chí (Wilcoxon + Holm, α = 0,05, "
                 "chênh lệch ≥ 5%)", fontsize=11, color=INK, loc="left")
    style(ax, "x")
    fig.savefig(fig_dir / "v2_significance.png", dpi=200, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


def plot_ablation(abl: pd.DataFrame, fig_dir: Path):
    if abl.empty:
        return
    names = ["NeuMF-F (đầy đủ)" if v == "neumf_f" else ABL[v][1] for v in abl["variant"]]
    fig, ax = plt.subplots(figsize=(8, 3.8), facecolor=SURFACE)
    y = np.arange(len(abl))
    v = abl["NDCG@10"].to_numpy(dtype=float)
    ax.barh(y, v, height=0.62, color=["#2a78d6"] + ["#8fb8ea"] * (len(abl) - 1), edgecolor=SURFACE, linewidth=2)
    for i in range(len(abl)):
        ax.text(v[i] + np.nanmax(v) * 0.02, i, vn_plain(v[i]), va="center", fontsize=8, color=INK)
    ax.set_xlim(0, np.nanmax(v) * 1.25 if np.nanmax(v) > 0 else 0.001)
    ax.set_title("NDCG@10", fontsize=10.5, color=INK, loc="left")
    style(ax, "x")
    ax.set_yticks(y, names, fontsize=9.5, color=INK)
    ax.invert_yaxis()
    fig.suptitle(f"Ablation của NeuMF-F trên tập kiểm thử của mẫu B (seed {int(abl.iloc[0]['seed'])})", fontsize=12,
                 color=INK, y=1.04)
    fig.savefig(fig_dir / "v2_ablation.png", dpi=200, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


CURVE_COLOR = {"neumf_f": "#2a78d6", "gmf_f": "#8fb8ea", "mlp_f": "#173f7a", "neumf": "#eb6834", "gmf": "#f2b134",
               "mlp": "#b2462a"}


def plot_curves(hist: pd.DataFrame, fig_dir: Path, seed: int = 42):
    if hist.empty or "NDCG@10" not in hist:
        return
    h = hist[(hist["seed"] == (seed if seed in set(hist["seed"]) else hist["seed"].min())) & (hist["phase"] == "select")]
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.2), facecolor=SURFACE)
    for mm, col in CURVE_COLOR.items():
        d = h[h["model"] == mm]
        if d.empty:
            continue
        axes[0].plot(d["epoch"], d["NDCG@10"], color=col, linewidth=1.8, marker="o", markersize=3, label=NAME[mm])
        b = d.loc[d["NDCG@10"].idxmax()]
        axes[0].scatter([b["epoch"]], [b["NDCG@10"]], s=90, facecolors="none", edgecolors=col, linewidths=1.8, zorder=3)
        axes[1].plot(d["epoch"], d["loss"], color=col, linewidth=1.8, marker="o", markersize=3, label=NAME[mm])
    axes[0].set_title("NDCG@10 trên tập xác thực của B theo epoch (vòng tròn: epoch chọn)", fontsize=10.5, color=INK,
                      loc="left")
    axes[1].set_title("Hàm mất mát BCE trên tập huấn luyện theo epoch", fontsize=10.5, color=INK, loc="left")
    for ax, fmt in zip(axes, (4, 3)):
        style(ax, "y")
        ax.set_xlabel("Epoch", fontsize=9, color=INK2)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    axes[0].legend(loc="lower right", frameon=False, fontsize=8.5, ncol=2)
    fig.savefig(fig_dir / "v2_curves.png", dpi=200, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


def plot_val_vs_test(summary: pd.DataFrame, fig_dir: Path):
    s = summary.dropna(subset=["val_NDCG@10"])
    s = s[s["model"] != "random"]
    if s.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 4.8), facecolor=SURFACE)
    y = np.arange(len(s))
    for i, (_, r) in enumerate(s.iterrows()):
        v, t = r["val_NDCG@10"], r["NDCG@10_mean"]
        ax.plot([v, t], [i, i], color=GRID, linewidth=2, zorder=1)
        ax.scatter([v], [i], s=46, color="#eb6834", zorder=3, edgecolors=SURFACE, linewidths=2)
        ax.scatter([t], [i], s=46, color="#2a78d6", zorder=3, edgecolors=SURFACE, linewidths=2)
    ax.set_yticks(y, [NAME[mm] for mm in s["model"]], fontsize=9.5, color=INK)
    ax.invert_yaxis()
    ax.legend(handles=[Line2D([], [], marker="o", color=c, linestyle="none", markersize=7, label=lab)
                       for c, lab in (("#eb6834", "Mẫu A, tập xác thực (tinh chỉnh, seed 42)"),
                                      ("#2a78d6", "Mẫu B, tập kiểm thử (trung bình qua seed)"))],
              loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False, fontsize=9)
    ax.set_title("NDCG@10 lúc tinh chỉnh (mẫu A) và lúc đánh giá cuối (mẫu B)", fontsize=11, color=INK, loc="left")
    style(ax, "x")
    fig.savefig(fig_dir / "v2_val_vs_test.png", dpi=200, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


# ------------------------------------------------------------------ ket_qua.txt
def text_report(seeds, summary, sig, abl, bey, info_b) -> str:
    """Bản tóm tắt dễ đọc (<final-dir>/ket_qua.txt): cùng số với các file CSV, không tính lại gì."""
    f = lambda x, nd=5: "—" if pd.isna(x) else vn_plain(x, nd)  # noqa: E731
    pc = lambda x: "—" if pd.isna(x) else f"{x * 100:+.1f}%".replace(".", ",")  # noqa: E731
    s = summary.set_index("model")
    ms = lambda m, c: f"{f(s.loc[m, f'{c}_mean'])} ± {f(s.loc[m, f'{c}_std'])}"  # noqa: E731
    stage = info_b.get("test", info_b["val"])
    out = [f"KẾT QUẢ ĐÁNH GIÁ CUỐI — GIAO THỨC V2 ({len(seeds)} seed: {', '.join(map(str, seeds))})",
           f"{thousands(stage['users'])} khách được đánh giá, trung bình {thousands(round(stage['candidates_mean']))} "
           "ứng viên mỗi khách. Xếp theo NDCG@10 (độ đo chính); ± là độ lệch chuẩn qua seed.", ""]

    def block(title, header, rows, notes=()):
        w = [max(len(str(r[i])) for r in [header, *rows]) for i in range(len(header))]
        line = lambda r: "  ".join(str(c).ljust(n) for c, n in zip(r, w)).rstrip()  # noqa: E731
        out.extend([title, "", line(header), "-" * len(line(header)), *map(line, rows), *notes, "", ""])

    block("1. Kết quả chính trên tập kiểm thử", ["Mô hình", "NDCG@10", "Recall@10", "HR@10", "Precision@10",
                                                "NDCG@10 lúc tinh chỉnh"],
          [[NAME[m], *(ms(m, c) for c in TABLE_METRICS[:4]), f(s.loc[m, "val_NDCG@10"])] for m in s.index],
          ["NDCG@10: món đúng càng ở trên trong top-10 càng được nhiều điểm. Recall@10: số món đúng trong top-10 / "
           "tổng số món đúng.", "HR@10: tỉ lệ khách có ít nhất một món đúng trong top-10. Precision@10: số món đúng "
           "trong top-10 / 10.", "NDCG@10 lúc tinh chỉnh: tập xác thực của mẫu phát triển (seed 42), chỉ để đối chiếu."])
    block("2. NDCG theo K", ["Mô hình", "NDCG@5", "NDCG@10", "NDCG@20"],
          [[NAME[m], *(ms(m, c) for c in ("NDCG@5", "NDCG@10", "NDCG@20"))] for m in s.index])
    if not sig.empty:
        block("3. Kiểm định 10 so sánh đã đăng ký (NDCG@10; Wilcoxon, hiệu chỉnh Holm, CI bootstrap 95%)",
              ["#", "A", "B", "Chênh (A−B)/B", "CI 95% của A−B", "p Holm", "Kết luận"],
              [[r.id, NAME[r.A], NAME[r.B], pc(r.rel_diff), f"[{f(r.ci_low)}; {f(r.ci_high)}]",
                "< 0,001" if r.p_holm < 0.001 else f(r.p_holm, 3), phrase(r._asdict())] for r in sig.itertuples()],
              ["\"Tốt hơn có ý nghĩa\" khi đồng thời p Holm < 0,05, CI không chứa 0 và chênh lệch ≥ 5%."])
    if not abl.empty:
        block(f"4. Ablation NeuMF-F (seed {int(abl.iloc[0]['seed'])}; cùng siêu tham số, tắt một thành phần)",
              ["Biến thể", "NDCG@10", "Thay đổi", "CI 95% của hiệu"],
              [["NeuMF-F (đầy đủ)", f(r["NDCG@10"]), "—", "—"] if r["variant"] == "neumf_f" else
               [ABL[r["variant"]][1], f(r["NDCG@10"]), pc(r["rel"]), f"[{f(r['ci_low'])}; {f(r['ci_high'])}]"]
               for _, r in abl.iterrows()],
              ["Chỉ mô tả, không kiểm định."])
    b = bey.set_index("model")
    block("5. Độ phủ top-10 (seed 42), số epoch chọn và thời gian huấn luyện", ["Mô hình", "Độ phủ ứng viên",
                                                                           "Epoch chọn theo seed", "Phút / seed"],
          [[NAME[m], f(b.loc[m, "coverage10"] * 100, 1) + "%", str(b.loc[m, "best_epochs"] or "—").replace(";", ", "),
            f(b.loc[m, "train_min"], 1)] for m in s.index if m in b.index],
          ["Độ phủ: tỉ lệ sản phẩm ứng viên xuất hiện trong top-10 của ít nhất một khách. Epoch chọn = 1 ở một seed: "
           "seed đó dừng ngay, thường chỉ gợi ý sản phẩm phổ biến."])
    out.append("Nguồn: summary.csv, significance.csv, ablation.csv, beyond.csv cùng thư mục (scripts/24_report_v2.py).")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--final-dir", default=str(PROJECT_ROOT / "outputs" / "v2" / "final"))
    ap.add_argument("--report-dir", default=str(REPORT), help="'' để không ghi vào báo cáo")
    ap.add_argument("--tuning-only", action="store_true",
                    help="trước đánh giá cuối: chỉ xuất bảng dữ liệu mẫu A và kết quả tinh chỉnh (không đọc mẫu B)")
    args = ap.parse_args()
    best = json.loads((AUDIT / "best_configs.json").read_text(encoding="utf-8"))
    if args.tuning_only:
        tables = ensure(Path(args.report_dir or REPORT) / "content" / "tables" / "v2")
        m = Macros()
        export_data(m, tables, dev_info(), None)
        export_tuning(m, tables, best)
        m.write(tables / "results_v2_macros.tex")
        print(f"Đã ghi bảng dữ liệu (mẫu A) và kết quả tinh chỉnh vào {tables}")
        return
    final_dir = Path(args.final_dir)
    seeds, res, per, hist, models = load(final_dir)

    summary = summarize(seeds, res, models, best)
    sig = significance(user_matrix(per, models))
    abl = ablation(per, res)
    bey = beyond(seeds, res, models)
    summary.to_csv(final_dir / "summary.csv", index=False)
    sig.to_csv(final_dir / "significance.csv", index=False)
    abl.to_csv(final_dir / "ablation.csv", index=False)
    bey.to_csv(final_dir / "beyond.csv", index=False)

    info_b = json.loads((final_dir / "data.json").read_text(encoding="utf-8"))
    n_users = info_b.get("test", info_b["val"])["users"]
    (final_dir / "ket_qua.txt").write_text(text_report(seeds, summary, sig, abl, bey, info_b), encoding="utf-8")
    fig_dir = ensure(final_dir / "figures")
    plot_metrics(res, seeds, summary, fig_dir, n_users)
    plot_significance(sig, fig_dir)
    plot_ablation(abl, fig_dir)
    plot_curves(hist, fig_dir)
    plot_val_vs_test(summary, fig_dir)

    pd.set_option("display.width", 220)
    cols = ["name", "NDCG@10_mean", "NDCG@10_std", "Recall@10_mean", "HR@10_mean", "val_NDCG@10"]
    print(f"Seed: {seeds}\n\n{summary[cols].round(5).to_string(index=False)}\n")
    if not sig.empty:
        print(sig[["id", "A", "B", "mean_A", "mean_B", "rel_diff", "ci_low", "ci_high", "p_holm", "verdict"]]
              .round(5).to_string(index=False))
    if not abl.empty:
        print("\n" + abl.round(5).to_string(index=False))

    if args.report_dir:
        report = Path(args.report_dir)
        tables = ensure(report / "content" / "tables" / "v2")
        m = Macros()
        export_data(m, tables, dev_info(), info_b)
        export_tuning(m, tables, best)
        export_results(m, tables, seeds, summary, sig, abl, bey, info_b)
        export_run(m, seeds, res)
        m.write(tables / "results_v2_macros.tex")
        fig_out = ensure(report / "media" / "figures" / "v2")
        for f in fig_dir.glob("*.png"):
            shutil.copy2(f, fig_out / f.name)
        print(f"\nĐã ghi bảng/macro vào {tables} và hình vào {fig_out}")


if __name__ == "__main__":
    main()
