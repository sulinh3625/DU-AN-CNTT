"""Phân tích kết quả giao thức v2 và xuất sang báo cáo (audit/PREREG_v2.md mục 6–7).

    python scripts/24_report_v2.py                     # sau scripts/23_final_v2.py
    python scripts/24_report_v2.py --final-dir outputs/v2/dry_run --report-dir <thư mục tạm>   # thử trên bản chạy thử

Đọc outputs/v2/final/ (23_final_v2.py) và audit/v2/best_configs.json (tinh chỉnh trên mẫu phát triển). Tính:
- trung bình ± độ lệch chuẩn qua seed của mọi chỉ số;
- họ 10 so sánh đã đăng ký: NDCG@10 theo người dùng trung bình qua seed, Wilcoxon signed-rank, khoảng tin cậy bootstrap
  ghép cặp 95% (10.000 lần, seed 0), hiệu chỉnh Holm; "tốt hơn" khi p Holm < 0,05, CI không chứa 0 và chênh lệch tương
  đối >= 5%;
- NDCG/Recall/HR/Precision@K với K = 5, 10, 15, 20, tính lại từ hạng của từng sản phẩm đúng đã lưu (cột ranks của
  per_user.csv.gz) — không chấm lại tập kiểm thử; @5/@10/@20 trùng khớp số của lần đánh giá cuối (kiểm tra khi chạy);
- ablation NeuMF-F (seed 42), mô tả top-10 (độ phủ), số epoch và thời gian huấn luyện.
Không còn sản phẩm mới (một sản phẩm = product_code, ứng viên chỉ gồm sản phẩm đã có cặp huấn luyện) nên không còn phân
tích theo nhóm sản phẩm cũ/mới.
Ghi: <final-dir>/{summary,significance,ablation,beyond,by_k}.csv, hình <final-dir>/figures/*.png; nếu có
--report-dir (mặc định: Report DACNTT) thì chép hình sang media/figures/v2/ và ghi bảng + macro LaTeX vào content/tables/v2/.
Mọi số trong báo cáo lấy từ các file này, không gõ tay.
Amazon Beauty (NEUMF_CONFIG=configs/amazon.yaml, `python run.py amazon-report`): đọc outputs/amazon/final/, ghi bảng +
macro (\\ARes, \\ASig, ...) vào content/tables/amazon/ và hình vào media/figures/amazon/ — không đụng bảng của H&M.
Bổ sung sau đánh giá cuối (audit/PREREG_bosung.md): nếu có <final-dir>/bosung/ (scripts/25_bosung.py) thì thêm mô hình lai
truyền thống Hybrid-CBCF (đánh dấu †) vào bảng kết quả theo ba nhóm baseline, bảng theo K, bảng độ phủ và bảng tinh
chỉnh, và kiểm định riêng họ bổ sung B1–B2 (Holm trong họ) -> <final-dir>/bosung/{summary,significance,by_k,beyond}.csv,
bảng tab_*_sigbs.tex, macro \\VSig{B1}{...}, \\VRes{Hyb}{...}. Các tệp, thứ hạng và họ 10 so sánh của 14 mô hình đăng ký
trước giữ nguyên.
"""
from __future__ import annotations

import argparse
import json
import re
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

import v2_common as V
from src.evaluation.metrics import multi_ranking_metrics  # noqa: E402  (đường dẫn src do v2_common thêm)

PROJECT_ROOT = V.PROJECT_ROOT
AUDIT = V.AUDIT  # audit/v2 (H&M) hoặc audit/amazon
REPORT = PROJECT_ROOT.parent / "Report DACNTT"

MODELS = ["neumf_f", "late_f", "gmf_f", "mlp_f", "neumf", "gmf", "mlp", "bpr", "itemknn", "userknn", "content",
          "recent_pop", "popularity", "random"]
NAME = {"random": "Random", "popularity": "Most Popular", "recent_pop": "MostPopular-Recent", "content": "Content",
        "itemknn": "ItemKNN", "userknn": "UserKNN", "bpr": "BPR-MF", "gmf": "GMF", "mlp": "MLP", "neumf": "NeuMF",
        "gmf_f": "GMF-F", "mlp_f": "MLP-F", "neumf_f": "NeuMF-F", "late_f": "LateFusion-F", "hybrid": "Hybrid-CBCF"}
KEY = {"random": "Rand", "popularity": "Pop", "recent_pop": "RecPop", "content": "Cont", "itemknn": "IKNN",
       "userknn": "UKNN", "bpr": "BPR", "gmf": "GMF", "mlp": "MLP", "neumf": "NeuMF", "gmf_f": "GMFF",
       "mlp_f": "MLPF", "neumf_f": "NeuMFF", "late_f": "LateF", "hybrid": "Hyb"}
ABL = {"neumf_f-text": ("AblText", "Bỏ vector văn bản"), "neumf_f-time": ("AblTime", "Bỏ đặc trưng thời gian"),
       "neumf_f-user": ("AblUser", "Bỏ thông tin khách hàng"), "neumf_f-attr": ("AblAttr", "Bỏ thuộc tính sản phẩm"),
       "neumf_f-iddrop": ("AblIdDrop", "Không bỏ ID ngẫu nhiên")}
# Bổ sung sau đánh giá cuối (audit/PREREG_bosung.md, scripts/25_bosung.py): mô hình lai truyền thống, đánh dấu † trong
# bảng; kiểm định trong họ riêng B1–B2 (Holm trong họ) — họ 10 so sánh đăng ký trước không đổi.
SUP = ("hybrid",)
DAGGER = r"\textsuperscript{*}"
COMPARISONS_BS = [("neumf_f", "hybrid"), ("hybrid", "userknn")]
# Ba nhóm baseline theo góp ý của GVHD (PREREG_bosung mục 5; cách xếp chờ GVHD xác nhận). Trong mỗi nhóm, bảng xếp theo
# NDCG@10 giảm dần.
GROUPS = [("Mô hình đề xuất", ("neumf_f",)),
          ("Nhóm 1: mô hình đơn lẻ", ("gmf_f", "mlp_f", "gmf", "mlp")),
          ("Nhóm 2: học máy truyền thống", ("hybrid", "userknn", "itemknn", "bpr", "content")),
          ("Nhóm 3: chuyên biệt cho gợi ý", ("late_f", "neumf", "recent_pop", "popularity")),
          ("Cận dưới", ("random",))]
GROUP_COLOR = dict(zip([g for g, _ in GROUPS], ["#2a78d6", "#8fb8ea", "#1baf7a", "#eb6834", "#898781"]))
GROUP_OF = {m: g for g, ms in GROUPS for m in ms}
# Họ so sánh cố định (PREREG_v2 mục 7), theo đúng thứ tự đăng ký.
COMPARISONS = [("neumf_f", "neumf"), ("neumf_f", "gmf_f"), ("neumf_f", "mlp_f"), ("neumf_f", "late_f"),
               ("neumf_f", "bpr"), ("neumf_f", "itemknn"), ("neumf_f", "userknn"), ("neumf_f", "recent_pop"),
               ("neumf_f", "content"), ("neumf", "bpr")]
METRICS = ["NDCG@10", "Recall@10", "HR@10", "Precision@10", "NDCG@5", "NDCG@20"]
TABLE_METRICS = ["NDCG@10", "Recall@10", "HR@10", "Precision@10", "NDCG@5", "NDCG@20"]
# Bảng theo K: tính lại từ hạng đã lưu của đánh giá cuối (by_k), không chấm lại tập kiểm thử.
K_ALL = (5, 10, 15, 20)
K_METRICS = ("NDCG", "Recall", "HR", "Precision")
NOT_SIG = "không khác biệt có ý nghĩa"
N_BOOT, BOOT_SEED, ALPHA, MIN_REL = 10_000, 0, 0.05, 0.05
INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"
HEADER = "% Sinh tự động bởi neumf_project/scripts/24_report_v2.py — KHÔNG sửa tay."
# Chữ, tên file và macro theo bộ dữ liệu. H&M: kết luận trên tập kiểm thử của mẫu kiểm định; Amazon Beauty: dữ liệu kiểm
# chứng (một bộ, chia theo thời gian, cấu hình chọn trên H&M — audit/PREREG_amazon.md), macro \ARes, \ASig, ... riêng.
TEXT = {
    "hm": dict(test="tập kiểm thử của mẫu kiểm định", test_fig="Tập kiểm thử của mẫu kiểm định H&M",
               test_cap="tập kiểm thử của mẫu kiểm định H\\&M", short="H\\&M",
               sel="tập xác thực của mẫu kiểm định", where="mẫu kiểm định H\\&M", subdir="v2", tab="tab_v2_",
               label="tab:v2", macro="v", macros_file="results_v2_macros.tex"),
    "amazon": dict(test="tập kiểm thử Amazon Beauty", test_fig="Tập kiểm thử Amazon Beauty",
                   test_cap="tập kiểm thử Amazon Beauty", short="Amazon Beauty",
                   sel="tập xác thực Amazon Beauty", where="Amazon Beauty", subdir="amazon", tab="tab_amz_",
                   label="tab:amz", macro="a", macros_file="results_amazon_macros.tex"),
}[V.DATASET]


def group(m: str) -> str:
    return GROUP_OF.get(m, GROUPS[-1][0])


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


def load_supplement(final_dir: Path, seeds, res: dict):
    """Kết quả bổ sung của scripts/25_bosung.py trong <final-dir>/bosung/. Mô hình tất định, chấm một lần: per_user có
    một bản cho mỗi seed của đánh giá cuối. Trả về (results.json bổ sung hoặc None, per_user, res có thêm mô hình bổ sung
    ở mọi seed — chỉ để dựng bảng hiển thị chung với 14 mô hình)."""
    d = final_dir / "bosung"
    if not (d / "results.json").exists():
        return None, pd.DataFrame(), res
    sup = json.loads((d / "results.json").read_text(encoding="utf-8"))
    per = pd.read_csv(d / "per_user.csv.gz")
    if sorted(per["seed"].unique()) != sorted(seeds):
        raise SystemExit(f"{d}/per_user.csv.gz có seed {sorted(per['seed'].unique())} khác đánh giá cuối {seeds}")
    if sup.get("provenance", {}).get("data_md5") != res[seeds[0]].get("provenance", {}).get("data_md5"):
        raise SystemExit(f"{d} được chấm trên dữ liệu khác lần đánh giá cuối (data_md5) — không ghép vào bảng.")
    merged = {s: {**res[s], "results": {**res[s]["results"], **sup["results"]},
                  "beyond": {**res[s].get("beyond", {}), **sup.get("beyond", {})},
                  "train_meta": {**res[s].get("train_meta", {}), **sup.get("train_meta", {})}} for s in seeds}
    return sup, per, merged


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


def significance(um: pd.DataFrame, comparisons=COMPARISONS, prefix: str = "") -> pd.DataFrame:
    """Kiểm định một họ so sánh (mặc định họ 10 so sánh đăng ký trước; họ bổ sung: COMPARISONS_BS, prefix "B"), hiệu
    chỉnh Holm trong họ."""
    rows = []
    for i, (a, b) in enumerate(comparisons, 1):
        i = f"{prefix}{i}" if prefix else i
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


def by_k(per: pd.DataFrame, models: list[str], summary: pd.DataFrame, ks=K_ALL) -> pd.DataFrame:
    """NDCG/Recall/HR/Precision@K cho mọi K trong ks, tính lại từ hạng của từng sản phẩm đúng mà đánh giá cuối đã lưu
    (cột ranks của per_user.csv.gz, cùng hàm multi_ranking_metrics lúc chấm) — không chấm lại tập kiểm thử. Mỗi seed:
    trung bình theo người dùng; rồi trung bình ± độ lệch chuẩn qua seed như summary.csv. Cột @K đã có trong summary.csv
    phải trùng khớp, nếu không thì dừng (hạng đã lưu không phải hạng đã chấm). Không có cột ranks: bảng rỗng."""
    if "ranks" not in per.columns:
        return pd.DataFrame()
    p = per[per["model"].isin(models) & per["ranks"].notna()]
    names = [f"{n}@{k}" for n in K_METRICS for k in ks]
    vals = []
    for r in p["ranks"]:
        ranks = [int(x) for x in str(r).split(";")]
        res = {k: multi_ranking_metrics(ranks, k) for k in ks}
        vals.append([res[k][n] for n in K_METRICS for k in ks])
    vals = np.asarray(vals, dtype=float).reshape(len(p), len(names))
    per_seed = pd.DataFrame(vals, columns=names).assign(model=p["model"].to_numpy(), seed=p["seed"].to_numpy())
    per_seed = per_seed.groupby(["model", "seed"])[names].mean()
    rows = []
    for m in summary["model"]:
        if m not in per_seed.index.get_level_values(0):
            continue
        s = per_seed.loc[m]
        row = {"model": m, "name": NAME[m], "n_seeds": len(s)}
        for c in names:
            row[f"{c}_mean"] = float(s[c].mean())
            row[f"{c}_std"] = float(s[c].std(ddof=1)) if len(s) > 1 else 0.0
        rows.append(row)
    out = pd.DataFrame(rows)
    shared = [c for c in out.columns if c.endswith("_mean") and c in summary.columns]
    gap = (out.set_index("model")[shared] - summary.set_index("model").loc[out["model"], shared]).abs().max().max()
    if gap > 1e-9:
        raise SystemExit(f"Chỉ số tính lại từ cột ranks lệch summary.csv ({gap:.3g}) — per_user.csv.gz không khớp "
                         "results.json, không xuất bảng theo K.")
    return out


def dev_info() -> dict:
    """Mô tả mẫu A ở giai đoạn xác thực (lưu đệm audit/v2/data_dev.json; không dựng tập kiểm thử của A)."""
    path = AUDIT / "data_dev.json"
    if not path.exists():
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


HYBRID_FUSION = {"mean": "bỏ phiếu: trung bình", "max": "bỏ phiếu: lớn nhất", "min": "bỏ phiếu: nhỏ nhất",
                 "lr": "tổng có trọng số học theo cặp"}


def hybrid_weights(p: dict) -> np.ndarray:
    """Trọng số của Hybrid-CBCF chia cho tổng (cùng thứ tự xếp hạng với trọng số gốc)."""
    w = np.asarray(p["weights"], dtype=float)
    return w / w.sum()


def params_text(m: str, p: dict) -> str:
    if not p:
        return "---"
    if m == "hybrid":
        if p["fusion"] != "lr":
            return HYBRID_FUSION[p["fusion"]]
        return HYBRID_FUSION["lr"] + ": " + "; ".join(
            f"{n} {vn(x, 2)}" for n, x in zip(("Content", "UserKNN", "ItemKNN"), hybrid_weights(p)))
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


def grid(colspec: str) -> str:
    """Khai báo cột kẻ lưới đầy đủ: "lrr" -> "|l|r|r|" (giữ nguyên cột p{...} kèm >{...})."""
    cols = re.findall(r">\{[^{}]*\}[pmb]\{[^{}]*\}|[pmb]\{[^{}]*\}|[lcr]", colspec)
    assert "".join(cols) == colspec.replace(" ", ""), colspec
    return "|" + "|".join(cols) + "|"


def table(label: str, caption: str, colspec: str, header: list[str] | str, rows: list[list[str]],
          colsep: str = "", size: str = "\\small") -> str:
    """Bảng kẻ lưới đầy đủ: | giữa mọi cột, \\hline sau mọi hàng. header: danh sách ô của một hàng tiêu đề, hoặc chuỗi
    LaTeX của nhiều hàng tiêu đề (tự kết thúc bằng \\hline). colsep: \\tabcolsep riêng cho bảng rộng (vd. "4pt");
    size: cỡ chữ của bảng (không nhỏ hơn \\footnotesize, tức 10,8pt ở cỡ chữ 13pt của báo cáo)."""
    body = "\n".join("        " + " & ".join(r) + r" \\ \hline" for r in rows)
    head = header if isinstance(header, str) else f"        {' & '.join(header)} \\\\ \\hline"
    sep = f"\\setlength{{\\tabcolsep}}{{{colsep}}}" if colsep else ""
    return (f"{HEADER}\n\\begin{{table}}[H]\n    \\centering{size}{sep}\n"
            f"    \\caption{{{caption}}}\n    \\label{{{label}}}\n"
            # [H] đặt bảng đúng chỗ trong văn bản, nên bảng cao hơn trang (kết quả chính) phải tự thu nhỏ cho vừa
            "    \\begin{adjustbox}{max width=\\textwidth, max totalheight=0.85\\textheight}\n"
            f"    \\begin{{tabular}}{{{grid(colspec)}}}\n        \\hline\n"
            f"{head}\n{body}\n"
            f"    \\end{{tabular}}\n    \\end{{adjustbox}}\n\\end{{table}}\n")


class Macros:
    """Macro số liệu \\<P>Res{mô hình}{chỉ số}, ... với P = V (H&M: vres-..., \\VRes) hoặc A (Amazon: ares-..., \\ARes)."""
    FAMILIES = ("res", "sd", "val", "rank", "sig", "abl", "bey", "data", "cfg")

    def __init__(self, prefix: str = "v"):
        self.prefix = prefix
        self.values: dict[str, str] = {}
        self.lines = [HEADER, r"\providecommand{\resultmacro}[3]{\ifcsname #1-#2-#3\endcsname\csname #1-#2-#3\endcsname"
                              r"\else\textbf{[chưa có]}\fi}"]
        self.lines += [rf"\providecommand{{\{prefix.upper()}{fam.capitalize()}}}[2]"
                       rf"{{\resultmacro{{{prefix}{fam}}}{{#1}}{{#2}}}}" for fam in self.FAMILIES]

    def add(self, family: str, a: str, b: str, value: str):
        """Một macro chỉ được định nghĩa một lần; định nghĩa lại cùng giá trị (vd. NDCG@10 từ summary và từ bảng theo K)
        thì bỏ qua, khác giá trị thì dừng."""
        if family not in self.FAMILIES:
            raise KeyError(family)
        name = f"{self.prefix}{family}-{a}-{b}"
        if name in self.values:
            if self.values[name] != value:
                raise ValueError(f"Macro {name} có hai giá trị: {self.values[name]} và {value}")
            return
        self.values[name] = value
        self.lines.append(rf"\expandafter\def\csname {name}\endcsname{{{value}}}")

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


def phrase_en(r) -> str:
    """Như phrase(), cho tóm tắt tiếng Anh."""
    if r["verdict"] == NOT_SIG:
        return "not significantly different"
    winner = r["A"] if r["verdict"] == "A tốt hơn" else r["B"]
    return f"{NAME[winner]} significantly better"


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


def cell(t, *keys, fmt=thousands):
    v = t
    for k in keys:
        if not isinstance(v, dict) or k not in v:
            return "---"
        v = v[k]
    return fmt(v)


def vn_date(iso: str) -> str:
    y, mth, d = str(iso).split("-")
    return f"{d}/{mth}/{y}"


def export_data_amazon(m: Macros, tables: Path, info: dict, entry: dict) -> None:
    """Quy mô dữ liệu Amazon Beauty: một bộ, chia theo thời gian (xác thực chỉ để chọn số epoch). info: data.json của
    đánh giá cuối; entry: mục của file đã lọc trong manifest.json (số dòng gốc, số liệu trước mốc kiểm thử)."""
    before = entry.get("before_test_start", {})
    k, vs, ts = V.CFG["k_core"], vn_date(V.CFG["val_start"]), vn_date(V.CFG["test_start"])
    rows = [
        ["Đánh giá trong bộ 5-core gốc (mỗi đánh giá là một tương tác)", cell(entry, "rows")],
        [f"Sản phẩm có đánh giá trước {ts}", cell(before, "products")],
        [f"Cặp (khách, sản phẩm) trước {ts}", cell(before, "product_pairs")],
        [f"Khách sau lọc {k}-core", cell(info, "n_users")],
        [f"Sản phẩm (\\texttt{{asin}}) sau lọc {k}-core", cell(info, "n_items")],
        [f"Cặp sau lọc {k}-core", cell(info, "n_kept_pairs")],
        [f"Xác thực: cặp huấn luyện (trước {vs})", cell(info, "val", "train_pairs")],
        ["Xác thực: khách được đánh giá", cell(info, "val", "users")],
        ["Xác thực: cặp đúng", cell(info, "val", "targets")],
        [f"Kiểm thử: cặp huấn luyện (trước {ts})", cell(info, "test", "train_pairs")],
        ["Kiểm thử: khách được đánh giá", cell(info, "test", "users")],
        ["Kiểm thử: cặp đúng", cell(info, "test", "targets")],
        ["Kiểm thử: số ứng viên trung bình mỗi khách", cell(info, "test", "candidates_mean",
                                                          fmt=lambda v: thousands(round(v)))],
    ]
    for key in ("rows",):
        if key in entry:
            m.add("data", "all", key, thousands(entry[key]))
    for key, name in (("products", "itemsbefore"), ("product_pairs", "pairsbefore")):
        if key in before:
            m.add("data", "all", name, thousands(before[key]))
    for key in ("n_users", "n_items", "n_kept_pairs"):
        m.add("data", "all", key.replace("_", ""), thousands(info[key]))
    for st in ("val", "test"):
        for key in ("users", "targets", "train_pairs", "scoreable"):
            if key in info.get(st, {}):
                m.add("data", st, key.replace("_", ""), thousands(info[st][key]))
        if st in info:
            m.add("data", st, "cand", thousands(round(info[st]["candidates_mean"])))
    (tables / f"{TEXT['tab']}data.tex").write_text(table(
        f"{TEXT['label']}data", "Quy mô dữ liệu Amazon Beauty", "lr", ["", "Amazon Beauty"], rows),
        encoding="utf-8")


def export_data(m: Macros, tables: Path, info_a: dict, info_b: dict | None) -> None:
    """Quy mô dữ liệu H&M. info_b = None trước đánh giá cuối (mẫu kiểm định chưa được dựng). Khoá macro: A = mẫu phát
    triển, B = mẫu kiểm định (\\VData{A}{nusers}, \\VData{Btest}{cand}, ...)."""
    ta, tb = info_a, info_b or {}

    rows = [
        ["Người dùng sau lọc 10-core", cell(ta, "n_users"), cell(tb, "n_users")],
        ["Sản phẩm (\\texttt{product\\_code}) sau lọc 10-core", cell(ta, "n_items"), cell(tb, "n_items")],
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
                m.add("data", nm, k.replace("_", ""), thousands(t[k]))
        if "val" in t:
            for k in ("users", "targets", "train_pairs"):
                m.add("data", f"{nm}val", k.replace("_", ""), thousands(t["val"][k]))
            m.add("data", f"{nm}val", "cand", thousands(round(t["val"]["candidates_mean"])))
    if "test" in tb:
        for k in ("users", "targets", "scoreable", "train_pairs"):
            m.add("data", "Btest", k.replace("_", ""), thousands(tb["test"][k]))
        m.add("data", "Btest", "cand", thousands(round(tb["test"]["candidates_mean"])))
    (tables / "tab_v2_data.tex").write_text(table(
        "tab:v2data", "Quy mô dữ liệu H\\&M", "lrr",
        ["", "Mẫu phát triển", "Mẫu kiểm định"], rows),
        encoding="utf-8")


def export_tuning(m: Macros, tables: Path, best: dict, bs: dict | None = None) -> None:
    """Cấu hình tốt nhất trên tập xác thực của mẫu A + thống kê nhật ký tinh chỉnh. bs: bosung_best_configs.json (mô
    hình bổ sung, dòng đánh dấu †; nhật ký riêng bosung_tuning_log.csv -> bảng các cách kết hợp)."""
    rows = []
    bs = bs or {}
    for mm in [x for x in MODELS if x in best] + [x for x in SUP if x in bs]:
        cfg = best.get(mm) or bs[mm]
        v = cfg["val"]
        # trong ô bảng "bỏ ID" không bị ngắt giữa hai dòng (macro \VCfg giữ nguyên chuỗi)
        rows.append([NAME[mm] + (DAGGER if mm in SUP else ""), params_text(mm, cfg["params"]).replace("bỏ ID", "bỏ~ID"),
                     vn(v["NDCG@10"]), vn(v.get("HR@10"))])
        for c in ("NDCG@10", "Recall@10", "HR@10"):
            if c in v:
                m.add("val", KEY[mm], mk(c), vn(v[c]))
        m.add("cfg", KEY[mm], "params", params_text(mm, cfg["params"]))
        if cfg.get("best_epoch") is not None:
            m.add("cfg", KEY[mm], "epoch", str(cfg["best_epoch"]))
    if "hybrid" in bs:
        export_hybrid_tuning(m, tables, best, bs["hybrid"])
    log = AUDIT / "tuning_log.csv"
    if log.exists():
        t = pd.read_csv(log)
        m.add("cfg", "all", "nconfigs", str(len(t)))
        m.add("cfg", "all", "hours", vn(t["time_s"].sum() / 3600, 1))
        m.add("cfg", "all", "codehashes", str(t["code_hash"].nunique()))
        neural = t[t["best_epoch"].notna()]
        if len(neural):
            m.add("cfg", "all", "nneural", str(len(neural)))
            m.add("cfg", "all", "epochmax", str(int(neural["best_epoch"].max())))
            m.add("cfg", "all", "epochmedian", vn(float(neural["best_epoch"].median()), 0))
    (tables / "tab_v2_tuning.tex").write_text(table(
        "tab:v2tuning", "Cấu hình tốt nhất trên tập xác thực",
        "l>{\\raggedright\\arraybackslash}p{6.8cm}rr",
        ["Mô hình", "Cấu hình chọn", "NDCG@10", "HR@10"], rows),
        encoding="utf-8")


def export_hybrid_tuning(m: Macros, tables: Path, best: dict, hb: dict) -> None:
    """Bảng các cách kết hợp của Hybrid-CBCF trên tập xác thực của mẫu phát triển (nhật ký bosung_tuning_log.csv), đặt
    cạnh ba thành phần đứng riêng — như bảng so sánh mô hình đơn lẻ và mô hình lai trong luận án của GVHD."""
    log = AUDIT / "bosung_tuning_log.csv"
    if not log.exists():
        return
    t = pd.read_csv(log)
    t = t[t["model"] == "hybrid"].drop_duplicates("params", keep="last")
    chosen = json.dumps(hb["params"], sort_keys=True)
    parts = hb.get("components_val") or {k: best[k]["val"] for k in ("content", "userknn", "itemknn")}
    # (nhãn, NDCG@10, HR@10): ba thành phần đứng riêng rồi bốn cách kết hợp; in đậm số cao nhất mỗi cột như các bảng khác
    comp = [(NAME[k], parts[k]["NDCG@10"], parts[k]["HR@10"]) for k in ("content", "userknn", "itemknn")]
    for k in ("content", "userknn", "itemknn"):
        m.add("val", "Hyb" + KEY[k], "NDCG10", vn(parts[k]["NDCG@10"]))
    fus = []
    for _, r in t.iterrows():
        p = json.loads(r["params"])
        label = HYBRID_FUSION[p["fusion"]].capitalize()
        if json.dumps(p, sort_keys=True) == chosen:
            label += " (được chọn)"
        fus.append((label, r["val_NDCG@10"], r["val_HR@10"]))
        m.add("val", "Hyb" + p["fusion"].capitalize(), "NDCG10", vn(r["val_NDCG@10"]))
    top = [max(x[i] for x in comp + fus) for i in (1, 2)]
    bold = lambda v, i: rf"\textbf{{{vn(v)}}}" if v == top[i] else vn(v)  # noqa: E731
    rows = [[r"\multicolumn{3}{|l|}{\textit{Thành phần đứng riêng}}"]]
    rows += [[lab, bold(a, 0), bold(b, 1)] for lab, a, b in comp]
    rows += [[r"\multicolumn{3}{|l|}{\textit{Hybrid-CBCF theo cách kết hợp}}"]]
    rows += [[lab, bold(a, 0), bold(b, 1)] for lab, a, b in fus]
    w = hybrid_weights(hb["params"]) if hb["params"]["fusion"] == "lr" else None
    if w is not None:
        for name, x in zip(("wCont", "wUKNN", "wIKNN"), w):
            m.add("cfg", "Hyb", name, vn(x, 2))
    m.add("cfg", "Hyb", "fusion", HYBRID_FUSION[hb["params"]["fusion"]])
    m.add("cfg", "Hyb", "nneg", str(hb.get("pairwise", {}).get("n_neg", "")))
    (tables / "tab_v2_hybrid.tex").write_text(table(
        "tab:v2hybrid", "Các cách kết hợp của Hybrid-CBCF", "lrr",
        ["Mô hình", "NDCG@10", "HR@10"], rows), encoding="utf-8")


def tex_escape(text: str) -> str:
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("_", r"\_"), ("#", r"\#"),
                 ("(R)", ""), ("(TM)", "")):
        text = text.replace(a, b)
    return " ".join(text.split())


def export_run(m: Macros, seeds, res) -> None:
    """Thông tin lần đánh giá cuối: máy, phiên bản, thời gian chạy, commit."""
    first = res[seeds[0]]
    mach, prov = first.get("machine", {}), first.get("provenance", {})
    m.add("data", "run", "cpu", tex_escape(str(mach.get("cpu", ""))))
    m.add("data", "run", "gpu", tex_escape(str(mach.get("gpu") or "không có")))
    m.add("data", "run", "device", "GPU" if "cuda" in str(mach.get("device", "")) else "CPU")
    m.add("data", "run", "torch", tex_escape(str(mach.get("torch", ""))))
    m.add("data", "run", "python", tex_escape(str(mach.get("python", ""))))
    m.add("data", "run", "hours", vn(sum(res[s].get("elapsed_min", 0) for s in seeds) / 60, 1))
    m.add("data", "run", "commit", str(prov.get("git_commit") or "")[:7])
    m.add("data", "run", "codehash", str(prov.get("code_hash", "")))
    m.add("data", "run", "seedlist", ", ".join(map(str, seeds)))


# Bảng kiểm định: mỗi so sánh một hàng hai dòng (dòng trên A, dòng dưới B) để bảng vừa khổ trang ở cỡ chữ \small;
# khoảng tin cậy cũng xuống dòng (cận dưới; cận trên).
SIG_COLS = "rlrrcrc"
SIG_HEADER = ["\\#", r"\tbl{Mô hình A}{Mô hình B}", r"\tbc{NDCG@10}{của A, B}", "(A$-$B)/B",
              r"\tbc{CI 95\%}{của A$-$B}", "p Holm", "Kết luận"]


def sig_rows(m: Macros, sig: pd.DataFrame) -> list[list[str]]:
    """Dòng bảng kiểm định + macro \\<P>Sig{id}{rel, diff, lo, hi, pholm, p, verdict, phrase} của một họ so sánh."""
    rows = []
    for r in sig.itertuples():
        rows.append([str(r.id), rf"\tbl{{{NAME[r.A]}}}{{{NAME[r.B]}}}", rf"\tbr{{{vn(r.mean_A)}}}{{{vn(r.mean_B)}}}",
                     pct(r.rel_diff), rf"\tbc{{[{vn(r.ci_low, sign=True)};}}{{{vn(r.ci_high, sign=True)}]}}",
                     pval(r.p_holm), "---" if r.verdict == NOT_SIG else r.verdict])
        for k, v in (("rel", pct(r.rel_diff)), ("diff", vn(r.diff, sign=True)), ("lo", vn(r.ci_low, sign=True)),
                     ("hi", vn(r.ci_high, sign=True)), ("pholm", pval(r.p_holm)), ("p", pval(r.p_wilcoxon)),
                     ("verdict", r.verdict), ("phrase", phrase(r._asdict())), ("phraseEN", phrase_en(r._asdict()))):
            m.add("sig", str(r.id), k, v)
    return rows


def export_supplement(m: Macros, tables: Path, sig_bs: pd.DataFrame, sup: dict, n_seed: int) -> None:
    """Phân tích bổ sung (audit/PREREG_bosung.md): kiểm định họ B1–B2 (Holm trong họ), thông tin lần chấm bổ sung và đối
    chiếu ba thành phần của Hybrid-CBCF với lần đánh giá cuối đã đăng ký."""
    tab, lab = TEXT["tab"], TEXT["label"]
    if not sig_bs.empty:
        rows = sig_rows(m, sig_bs)
        m.add("sig", "bs", "n", str(len(sig_bs)))
        m.add("sig", "bs", "nsig", str(int((sig_bs["verdict"] != NOT_SIG).sum())))
        (tables / f"{tab}sigbs.tex").write_text(table(
            f"{lab}sigbs", f"Kiểm định bổ sung với Hybrid-CBCF trên {TEXT['short']}",
            SIG_COLS, SIG_HEADER, rows), encoding="utf-8")
    prov, mach = sup.get("provenance", {}), sup.get("machine", {})
    m.add("data", "bs", "commit", str(prov.get("git_commit") or "")[:7])
    m.add("data", "bs", "cpu", tex_escape(str(mach.get("cpu", ""))))
    m.add("data", "bs", "date", vn_date(str(sup.get("date", "")).split("T")[0]) if sup.get("date") else "---")
    m.add("data", "bs", "minutes", vn(float(sup.get("elapsed_min", 0)), 1))
    for k, c in sup.get("components_check", {}).items():
        key = KEY[k]
        m.add("data", f"bs{key}", "now", vn(c["NDCG@10"]))
        if "users" in c:
            m.add("data", f"bs{key}", "reg", vn(c["registered_NDCG10"]))
            m.add("data", f"bs{key}", "same", f"{thousands(c['users_same_ranks'])}/{thousands(c['users'])}")


def export_results(m: Macros, tables: Path, seeds, summary, sig, abl, bey, display=None,
                   bey_display=None) -> None:
    """summary, sig, abl, bey: 14 mô hình đăng ký trước (thứ hạng \\<P>Rank tính trên đây). display, bey_display: thêm mô
    hình bổ sung (SUP, đánh dấu †) — dùng cho bảng kết quả theo ba nhóm và bảng độ phủ."""
    n_seed = len(seeds)
    models = summary["model"].tolist()
    rank = {mm: i + 1 for i, mm in enumerate(models)}
    display = summary if display is None else display
    bey = bey if bey_display is None else bey_display
    shown = display["model"].tolist()  # NDCG@10 giảm dần
    by = display.set_index("model")
    tab, lab = TEXT["tab"], TEXT["label"]

    # Kết quả chính, xếp theo ba nhóm mô hình đối chứng; trong nhóm theo NDCG@10 giảm dần
    best_val = {c: by[f"{c}_mean"].max() for c in TABLE_METRICS}
    rows = []
    for gname, members in GROUPS:
        ms = [mm for mm in shown if mm in members]
        if not ms:
            continue
        rows.append([rf"\multicolumn{{{1 + len(TABLE_METRICS)}}}{{|l|}}{{\textit{{{gname}}}}}"])
        for mm in ms:
            r = [NAME[mm] + (DAGGER if mm in SUP else "")]
            for c in TABLE_METRICS:
                mean, sd = by.loc[mm, f"{c}_mean"], by.loc[mm, f"{c}_std"]
                cell = vn(mean)
                if mean == best_val[c]:
                    cell = rf"\textbf{{{cell}}}"
                r.append(rf"\tbsd{{{cell}}}{{{vn(sd)}}}")  # độ lệch chuẩn ở dòng dưới, cùng cỡ chữ
            rows.append(r)
    for mm in shown:
        for c in METRICS:
            m.add("res", KEY[mm], mk(c), vn(by.loc[mm, f"{c}_mean"]))
            m.add("sd", KEY[mm], mk(c), vn(by.loc[mm, f"{c}_std"]))
        if mm in rank:
            m.add("rank", KEY[mm], "NDCG10", ORDINAL.get(rank[mm], str(rank[mm])))
        else:  # mô hình bổ sung: thứ hạng trong toàn bộ mô hình của bảng (14 + bổ sung)
            k = shown.index(mm) + 1
            m.add("rank", KEY[mm], "all", ORDINAL.get(k, str(k)))
    m.add("rank", "all", "n", str(len(shown)))
    (tables / f"{tab}main.tex").write_text(table(
        f"{lab}main", f"Kết quả trên tập kiểm thử {TEXT['short']}",
        "l" + "r" * len(TABLE_METRICS),
        ["Mô hình", *[rf"\tbc{{{c.split('@')[0]}}}{{@{c.split('@')[1]}}}" for c in TABLE_METRICS]], rows,
        colsep="5pt", size="\\footnotesize"), encoding="utf-8")  # 7 cột hai dòng: vừa khổ trang không cần thu nhỏ
    m.add("data", "run", "seeds", str(n_seed))
    models = shown  # bảng độ phủ: mọi mô hình của bảng chính

    # Kiểm định
    if not sig.empty:
        rows = sig_rows(m, sig)
        s_vn, s_en = family_summary(sig)
        m.add("sig", "all", "summary", s_vn)
        m.add("sig", "all", "summaryEN", s_en)
        m.add("sig", "all", "nsig", str(int((sig["verdict"] != NOT_SIG).sum())))
        m.add("sig", "all", "n", str(len(sig)))
        (tables / f"{tab}sig.tex").write_text(table(
            f"{lab}sig", f"Kiểm định họ {len(sig)} so sánh trên {TEXT['short']}",
            SIG_COLS, SIG_HEADER, rows), encoding="utf-8")

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
                m.add("abl", key, "NDCG10", vn(r["NDCG@10"]))
                m.add("abl", key, "rel", pct(r["rel"]))
                m.add("abl", key, "lo", vn(r["ci_low"], sign=True))
                m.add("abl", key, "hi", vn(r["ci_high"], sign=True))
        m.add("abl", "Full", "NDCG10", vn(abl.iloc[0]["NDCG@10"]))
        (tables / f"{tab}ablation.tex").write_text(table(
            f"{lab}ablation", f"Phân tích bóc tách NeuMF-F trên {TEXT['short']}", "lrrc",
            ["Biến thể", "NDCG@10", "Thay đổi", "CI 95\\% của hiệu"], rows), encoding="utf-8")

    # Mô tả top-10 và thời gian
    b = bey.set_index("model")
    rows = []
    for mm in models:
        ep = b.loc[mm, "best_epoch_mean"]
        rows.append([NAME[mm] + (DAGGER if mm in SUP else ""), vn(b.loc[mm, "coverage10"] * 100, 1) + r"\%",
                     "---" if np.isnan(ep) else vn(ep, 1), vn(b.loc[mm, "train_min"], 1)])
        m.add("bey", KEY[mm], "cov", vn(b.loc[mm, "coverage10"] * 100, 1) + r"\%")
        m.add("bey", KEY[mm], "time", vn(b.loc[mm, "train_min"], 1))
        if not np.isnan(ep):
            m.add("bey", KEY[mm], "epoch", vn(ep, 1))
    (tables / f"{tab}beyond.tex").write_text(table(
        f"{lab}beyond", f"Độ phủ top-10 và chi phí huấn luyện trên {TEXT['short']}", "lrrr",
        ["Mô hình", "Độ phủ ứng viên", "Số epoch chọn", "Thời gian (phút)"], rows), encoding="utf-8")


def export_by_k(m: Macros, tables: Path, bk: pd.DataFrame) -> None:
    """Hai bảng theo K = 5, 10, 15, 20 (NDCG và Recall; HR và Precision) + macro \\<P>Res{mô hình}{NDCG15}, ...
    Thứ tự dòng như bảng kết quả chính (NDCG@10 giảm dần)."""
    if bk.empty:
        return
    by = bk.set_index("model")
    for mm in by.index:
        for n in K_METRICS:
            for k in K_ALL:
                m.add("res", KEY[mm], f"{n}{k}", vn(by.loc[mm, f"{n}@{k}_mean"]))
                m.add("sd", KEY[mm], f"{n}{k}", vn(by.loc[mm, f"{n}@{k}_std"]))
    tab, lab = TEXT["tab"], TEXT["label"]
    for part, pair in ((1, ("NDCG", "Recall")), (2, ("HR", "Precision"))):
        cols = [f"{n}@{k}" for n in pair for k in K_ALL]
        best = {c: by[f"{c}_mean"].max() for c in cols}
        rows = []
        for mm in by.index:
            r = [NAME[mm] + (DAGGER if mm in SUP else "")]
            for c in cols:
                v = by.loc[mm, f"{c}_mean"]
                r.append(rf"\textbf{{{vn(v, 4)}}}" if v == best[c] else vn(v, 4))
            rows.append(r)
        nk = len(K_ALL)
        header = (rf"        \multirow{{2}}{{*}}{{Mô hình}} & \multicolumn{{{nk}}}{{c|}}{{{pair[0]}@K}} & "
                  rf"\multicolumn{{{nk}}}{{c|}}{{{pair[1]}@K}} \\ \cline{{2-{1 + 2 * nk}}}" + "\n"
                  + "         & " + " & ".join(f"@{k}" for _ in pair for k in K_ALL) + r" \\ \hline")
        text = table(f"{lab}k{part}", f"{pair[0]}@K và {pair[1]}@K trên {TEXT['short']}", "l" + "r" * len(cols), header, rows, colsep="4pt")
        (tables / f"{tab}k{part}.tex").write_text(text, encoding="utf-8")


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
    axes[0].set_yticks(y, [NAME[mm] + ("†" if mm in SUP else "") for mm in models], fontsize=9.5, color=INK)
    axes[0].invert_yaxis()
    handles = [Patch(color=col, label=gname) for gname, col in GROUP_COLOR.items()]
    handles.append(Line2D([], [], marker="o", color=INK, linestyle="none", markersize=4, label="Từng seed"))
    fig.legend(handles=handles, loc="upper center", ncol=len(handles), frameon=False, fontsize=9, bbox_to_anchor=(0.5, 1.0))
    fig.suptitle(f"{TEXT['test_fig']} — trung bình ± độ lệch chuẩn qua {len(seeds)} seed "
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
    ax.invert_yaxis()  # không đặt suptitle: chú thích LaTeX đã là tiêu đề của hình
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
    axes[0].set_title("NDCG@10 trên tập xác thực theo epoch (vòng tròn: epoch chọn)", fontsize=10.5, color=INK,
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
    ax.set_yticks(y, [NAME[mm] + ("†" if mm in SUP else "") for mm in s["model"]], fontsize=9.5, color=INK)
    ax.invert_yaxis()
    ax.legend(handles=[Line2D([], [], marker="o", color=c, linestyle="none", markersize=7, label=lab)
                       for c, lab in (("#eb6834", "Mẫu phát triển, tập xác thực (tinh chỉnh, seed 42)"),
                                      ("#2a78d6", "Mẫu kiểm định, tập kiểm thử (trung bình qua seed)"))],
              loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False, fontsize=9)
    ax.set_title("NDCG@10 lúc tinh chỉnh (mẫu phát triển) và lúc đánh giá cuối (mẫu kiểm định)", fontsize=11,
                 color=INK, loc="left")
    style(ax, "x")
    fig.savefig(fig_dir / "v2_val_vs_test.png", dpi=200, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


# ------------------------------------------------------------------ ket_qua.txt
def text_report(seeds, summary, sig, abl, bey, info_b, bk: pd.DataFrame | None = None, sup: dict | None = None,
                display: pd.DataFrame | None = None, sig_bs: pd.DataFrame | None = None,
                bk_all: pd.DataFrame | None = None) -> str:
    """Bản tóm tắt dễ đọc (<final-dir>/ket_qua.txt): cùng số với các file CSV, không tính lại gì. sup, display, sig_bs,
    bk_all: phân tích bổ sung (mục 6), nếu có."""
    f = lambda x, nd=5: "—" if pd.isna(x) else vn_plain(x, nd)  # noqa: E731
    pc = lambda x: "—" if pd.isna(x) else f"{x * 100:+.1f}%".replace(".", ",")  # noqa: E731
    s = summary.set_index("model")
    ms = lambda m, c: f"{f(s.loc[m, f'{c}_mean'])} ± {f(s.loc[m, f'{c}_std'])}"  # noqa: E731
    stage = info_b.get("test", info_b["val"])
    out = [f"KẾT QUẢ ĐÁNH GIÁ CUỐI — {V.NAME.upper()} — {TEXT['test'].upper()} ({len(seeds)} seed: "
           f"{', '.join(map(str, seeds))})",
           f"{thousands(stage['users'])} khách được đánh giá, trung bình {thousands(round(stage['candidates_mean']))} "
           "ứng viên mỗi khách. Xếp theo NDCG@10 (độ đo chính); ± là độ lệch chuẩn qua seed.", ""]

    def block(title, header, rows, notes=()):
        w = [max(len(str(r[i])) for r in [header, *rows]) for i in range(len(header))]
        line = lambda r: "  ".join(str(c).ljust(n) for c, n in zip(r, w)).rstrip()  # noqa: E731
        out.extend([title, "", line(header), "-" * len(line(header)), *map(line, rows), *notes, "", ""])

    tuned = bool(s["val_NDCG@10"].notna().any())
    block("1. Kết quả chính trên tập kiểm thử", ["Mô hình", "NDCG@10", "Recall@10", "HR@10", "Precision@10",
                                                *(["NDCG@10 lúc tinh chỉnh"] if tuned else [])],
          [[NAME[m], *(ms(m, c) for c in TABLE_METRICS[:4]), *([f(s.loc[m, "val_NDCG@10"])] if tuned else [])]
           for m in s.index],
          ["NDCG@10: món đúng càng ở trên trong top-10 càng được nhiều điểm. Recall@10: số món đúng trong top-10 / "
           "tổng số món đúng.", "HR@10: tỉ lệ khách có ít nhất một món đúng trong top-10. Precision@10: số món đúng "
           "trong top-10 / 10.",
           "NDCG@10 lúc tinh chỉnh: tập xác thực của mẫu phát triển (seed 42), chỉ để đối chiếu." if tuned else
           f"Không tinh chỉnh trên {V.NAME}: cấu hình lấy từ {V.CFG.get('best_configs')} (chọn trên H&M); số epoch "
           "chọn trên tập xác thực của bộ này."])
    if bk is None or bk.empty:
        block("2. NDCG theo K", ["Mô hình", "NDCG@5", "NDCG@10", "NDCG@20"],
              [[NAME[m], *(ms(m, c) for c in ("NDCG@5", "NDCG@10", "NDCG@20"))] for m in s.index])
    else:
        b = bk.set_index("model")
        mk_ = lambda m, c: f"{f(b.loc[m, f'{c}_mean'])} ± {f(b.loc[m, f'{c}_std'])}"  # noqa: E731
        for i, n in enumerate(K_METRICS):
            block(f"2{'abcd'[i]}. {n}@K với K = {', '.join(map(str, K_ALL))}", ["Mô hình", *(f"{n}@{k}" for k in K_ALL)],
                  [[NAME[m], *(mk_(m, f"{n}@{k}") for k in K_ALL)] for m in b.index],
                  ["Tính lại từ hạng đã lưu của lần đánh giá cuối (by_k.csv), không chấm lại tập kiểm thử."]
                  if i == len(K_METRICS) - 1 else ())
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
    if sup is not None and display is not None:
        d = display.set_index("model")
        md = lambda m, c: f"{f(d.loc[m, f'{c}_mean'])} ± {f(d.loc[m, f'{c}_std'])}"  # noqa: E731
        groups = [[g, NAME[m] + ("†" if m in SUP else ""), *(md(m, c) for c in TABLE_METRICS[:4])]
                  for g, ms in GROUPS for m in display["model"] if m in ms]
        block("6. Bổ sung sau đánh giá cuối: mô hình lai truyền thống Hybrid-CBCF (audit/PREREG_bosung.md) — kết quả "
              "theo ba nhóm mô hình đối chứng", ["Nhóm", "Mô hình", "NDCG@10", "Recall@10", "HR@10", "Precision@10"],
              groups, ["† Bổ sung: kết hợp Content, UserKNN, ItemKNN theo mô hình lai trong luận án của GVHD; cách "
                       f"kết hợp chọn trên tập xác thực của mẫu phát triển H&M: {sup['config']['params']}.",
                       "Chấm một lần trên cùng tập kiểm thử (tất định, dùng cho mọi seed); không thuộc họ 10 so sánh "
                       "đăng ký trước."])
        if bk_all is not None and not bk_all.empty and "hybrid" in set(bk_all["model"]):
            b = bk_all.set_index("model")
            block("6a. Hybrid-CBCF theo K", ["Độ đo", *(f"@{k}" for k in K_ALL)],
                  [[n, *(f(b.loc["hybrid", f"{n}@{k}_mean"]) for k in K_ALL)] for n in K_METRICS])
        if sig_bs is not None and not sig_bs.empty:
            block("6b. Kiểm định họ bổ sung (NDCG@10; Wilcoxon, hiệu chỉnh Holm trong họ, CI bootstrap 95%)",
                  ["#", "A", "B", "Chênh (A−B)/B", "CI 95% của A−B", "p Holm", "Kết luận"],
                  [[r.id, NAME[r.A], NAME[r.B], pc(r.rel_diff), f"[{f(r.ci_low)}; {f(r.ci_high)}]",
                    "< 0,001" if r.p_holm < 0.001 else f(r.p_holm, 3), phrase(r._asdict())] for r in sig_bs.itertuples()])
        check = sup.get("components_check", {})
        if check:
            block("6c. Ba thành phần chấm lại cùng lần chấm bổ sung, so với đánh giá cuối đã đăng ký",
                  ["Thành phần", "NDCG@10 (lần bổ sung)", "NDCG@10 (đã đăng ký)", "Khách trùng hạng"],
                  [[NAME[k], f(c["NDCG@10"]), f(c.get("registered_NDCG10", np.nan)),
                    f"{c['users_same_ranks']}/{c['users']}" if "users" in c else "—"] for k, c in check.items()],
                  [f"Máy chạy bổ sung: {sup.get('machine', {}).get('cpu', '')}; commit "
                   f"{str(sup.get('provenance', {}).get('git_commit') or '')[:7]}. Tệp đặc trưng văn bản không nằm trong "
                   "git, mỗi máy tự dựng, nên Content có thể lệch nhẹ; UserKNN, ItemKNN không dùng đặc trưng."])
    out.append("Nguồn: summary.csv, significance.csv, ablation.csv, beyond.csv"
               f"{'' if bk is None or bk.empty else ', by_k.csv'} cùng thư mục (scripts/24_report_v2.py)"
               + ("; phân tích bổ sung: bosung/." if sup is not None else "."))
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--final-dir", default=str(V.OUT / "final"))
    ap.add_argument("--report-dir", default=str(REPORT),
                    help="'' để không ghi vào báo cáo. H&M ghi vào content/tables/v2/, Amazon vào content/tables/amazon/")
    ap.add_argument("--tuning-only", action="store_true",
                    help="trước đánh giá cuối: chỉ xuất bảng dữ liệu mẫu phát triển và kết quả tinh chỉnh (không đọc "
                         "mẫu kiểm định)")
    args = ap.parse_args()
    # NDCG@10 lúc tinh chỉnh chỉ có khi tinh chỉnh trên chính bộ này (Amazon dùng cấu hình H&M: không có cột đó)
    best = json.loads(V.BEST_CONFIGS.read_text(encoding="utf-8")) if V.TUNED_HERE else {}
    bs_path = V.BEST_CONFIGS.with_name("bosung_best_configs.json")  # mô hình bổ sung (25_bosung.py tune)
    bs_best = json.loads(bs_path.read_text(encoding="utf-8")) if V.TUNED_HERE and bs_path.exists() else {}
    if args.tuning_only:
        if not V.TUNED_HERE:  # Amazon không tinh chỉnh: không có bảng tinh chỉnh, không được ghi đè bảng của H&M
            raise SystemExit(f"{V.NAME} không tinh chỉnh — --tuning-only chỉ dùng cho H&M")
        if not args.report_dir:
            raise SystemExit("--tuning-only ghi bảng vào báo cáo — cần --report-dir")
        tables = ensure(Path(args.report_dir) / "content" / "tables" / "v2")
        m = Macros()
        export_data(m, tables, dev_info(), None)
        export_tuning(m, tables, best, bs_best)
        m.write(tables / "results_v2_macros.tex")
        print(f"Đã ghi bảng dữ liệu (mẫu A) và kết quả tinh chỉnh vào {tables}")
        return
    final_dir = Path(args.final_dir)
    seeds, res, per, hist, models = load(final_dir)

    summary = summarize(seeds, res, models, best)
    sig = significance(user_matrix(per, models))
    abl = ablation(per, res)
    bey = beyond(seeds, res, models)
    bk = by_k(per, models, summary)
    summary.to_csv(final_dir / "summary.csv", index=False)
    sig.to_csv(final_dir / "significance.csv", index=False)
    abl.to_csv(final_dir / "ablation.csv", index=False)
    bey.to_csv(final_dir / "beyond.csv", index=False)
    if not bk.empty:
        bk.to_csv(final_dir / "by_k.csv", index=False)

    # Phân tích bổ sung (audit/PREREG_bosung.md): bảng hiển thị gồm 14 mô hình + mô hình bổ sung; họ kiểm định riêng
    sup, sup_per, res_all = load_supplement(final_dir, seeds, res)
    models_all = models + [mm for mm in SUP if sup is not None and mm in sup["results"]]
    per_all, display, bey_all, bk_all, sig_bs = per, summary, bey, bk, pd.DataFrame()
    if sup is not None:
        per_all = pd.concat([per, sup_per], ignore_index=True)
        display = summarize(seeds, res_all, models_all, {**best, **bs_best})
        bey_all = beyond(seeds, res_all, models_all)
        bk_all = by_k(per_all, models_all, display)
        sig_bs = significance(user_matrix(per_all, models_all), COMPARISONS_BS, "B")
        out_bs = final_dir / "bosung"
        display.assign(supplementary=display["model"].isin(SUP)).to_csv(out_bs / "summary.csv", index=False)
        sig_bs.to_csv(out_bs / "significance.csv", index=False)
        bey_all.to_csv(out_bs / "beyond.csv", index=False)
        if not bk_all.empty:
            bk_all.to_csv(out_bs / "by_k.csv", index=False)

    info_b = json.loads((final_dir / "data.json").read_text(encoding="utf-8"))
    n_users = info_b.get("test", info_b["val"])["users"]
    (final_dir / "ket_qua.txt").write_text(text_report(seeds, summary, sig, abl, bey, info_b, bk, sup, display, sig_bs,
                                                       bk_all), encoding="utf-8")
    fig_dir = ensure(final_dir / "figures")
    plot_metrics(res_all, seeds, display, fig_dir, n_users)
    plot_significance(sig, fig_dir)
    plot_ablation(abl, fig_dir)
    plot_curves(hist, fig_dir)
    plot_val_vs_test(display, fig_dir)

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
        tables = ensure(report / "content" / "tables" / TEXT["subdir"])
        m = Macros(TEXT["macro"])
        if V.TUNED_HERE:
            export_data(m, tables, dev_info(), info_b)
            export_tuning(m, tables, best, bs_best)
        else:  # Amazon: một bộ dữ liệu, không tinh chỉnh
            manifest = json.loads(V.MANIFEST.read_text(encoding="utf-8")) if V.MANIFEST.exists() else {}
            export_data_amazon(m, tables, info_b, manifest.get(V.data_name("holdout"), {}))
        export_results(m, tables, seeds, summary, sig, abl, bey, display, bey_all)
        export_by_k(m, tables, bk_all)
        export_run(m, seeds, res)
        if sup is not None:
            export_supplement(m, tables, sig_bs, sup, len(seeds))
        m.write(tables / TEXT["macros_file"])
        fig_out = ensure(report / "media" / "figures" / TEXT["subdir"])
        for f in fig_dir.glob("*.png"):
            shutil.copy2(f, fig_out / f.name)
        print(f"\nĐã ghi bảng/macro vào {tables} và hình vào {fig_out}")


if __name__ == "__main__":
    main()
