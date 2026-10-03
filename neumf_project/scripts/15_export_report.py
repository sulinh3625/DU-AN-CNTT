"""Xuất số liệu cuối sang báo cáo LaTeX (Report DACNTT/) — mọi số trong C4/C5/tóm tắt lấy từ đây, không gõ tay.

    python scripts/15_export_report.py

Đọc: audit/best_configs.json, audit/tuning_log.csv, outputs/final/{summary,significance}.csv và (nếu có) các file
của 14_secondary.py, 16_extra_k.py, 17_extension.py.
Ghi:
  Report DACNTT/content/tables/results_macros.tex   macro \\Res{Pre}{NDCG10}, \\Sd, \\Sig, \\Strat, \\Beyond, \\Samp, \\Lat,
                                                    \\Val, \\Kx, \\Ext, \\Esig (kể cả câu kết luận tự sinh \\Esig{all}{summary})
  Report DACNTT/content/tables/tab_*.tex            bảng (table float có caption + label)
  Report DACNTT/media/figures/final/*.png           chép từ outputs/figures/final_*.png
File nguồn nào chưa có thì bảng tương ứng không được sinh; báo cáo hiện ghi chú "chưa có số liệu" ở chỗ đó, macro
chưa có giá trị hiện "[chưa có]".
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FINAL = PROJECT_ROOT / "outputs" / "final"
FIG = PROJECT_ROOT / "outputs" / "figures"
AUDIT = PROJECT_ROOT / "audit"
REPORT = PROJECT_ROOT.parent / "Report DACNTT"
TABLES = REPORT / "content" / "tables"
FIG_OUT = REPORT / "media" / "figures" / "final"

ORDER = ["NeuMF-Pretrained", "NeuMF-Scratch", "GMF", "MLP", "BPR-MF", "MostPopular", "Random"]
EXT_ORDER = ["LateFusion-GMF-MLP", "LateFusion-BPR-MLP", "ItemKNN", "UserKNN"]
KEY = {"NeuMF-Pretrained": "Pre", "NeuMF-Scratch": "Scr", "GMF": "GMF", "MLP": "MLP", "BPR-MF": "BPR",
       "MostPopular": "MostPop", "Random": "Random",
       "LateFusion-GMF-MLP": "LFGM", "LateFusion-BPR-MLP": "LFBM", "ItemKNN": "IKNN", "UserKNN": "UKNN"}
# Tên hiển thị trong bảng/câu chữ (tên kỹ thuật giữ nguyên trong CSV).
DISPLAY = {"LateFusion-GMF-MLP": "Late Fusion GMF + MLP", "LateFusion-BPR-MLP": "Late Fusion BPR-MF + MLP",
           "MostPopular": "Most Popular"}
TUNE_KEY = {"NeuMF-Pretrained": "neumf_pretrained", "NeuMF-Scratch": "neumf_scratch", "GMF": "gmf", "MLP": "mlp",
            "BPR-MF": "bpr", "LateFusion-GMF-MLP": "late_gmf_mlp", "LateFusion-BPR-MLP": "late_bpr_mlp",
            "ItemKNN": "itemknn", "UserKNN": "userknn"}
METRICS = ["NDCG@10", "Recall@10", "HR@10", "Precision@10", "NDCG@5"]
ORDINAL = {1: "thứ nhất", 2: "thứ hai", 3: "thứ ba", 4: "thứ tư", 5: "thứ năm", 6: "thứ sáu", 7: "thứ bảy",
           8: "thứ tám", 9: "thứ chín", 10: "thứ mười", 11: "thứ mười một"}
NOT_SIG = "không khác biệt có ý nghĩa"


def show(model: str) -> str:
    return DISPLAY.get(model, model)


def ranks(values: dict[str, float]) -> dict[str, int]:
    """Thứ hạng giảm dần (1 = cao nhất); hoà thì cùng hạng nhỏ hơn."""
    return {m: 1 + sum(v > values[m] for v in values.values()) for m in values}


def vn(x: float, nd: int = 5, sign: bool = False) -> str:
    """Số kiểu Việt Nam cho LaTeX: 0{,}01062; số âm dùng dấu trừ toán học."""
    text = f"{abs(x):.{nd}f}".replace(".", "{,}")
    return ("$-$" if x < 0 else "+" if sign else "") + text


def num(x: float) -> str:
    """Siêu tham số: 1e-06 -> $10^{-6}$, 0.0005 -> 0{,}0005."""
    if x and abs(x) < 1e-4:
        return f"$10^{{{int(round(__import__('math').log10(abs(x))))}}}$"
    return f"{x:g}".replace(".", "{,}")


def mkey(metric: str) -> str:
    return metric.replace("@", "")


class Macros:
    def __init__(self):
        self.lines = [
            "% Sinh tự động bởi neumf_project/scripts/15_export_report.py — KHÔNG sửa tay.",
            r"\providecommand{\resultmacro}[3]{\ifcsname #1-#2-#3\endcsname\csname #1-#2-#3\endcsname"
            r"\else\textbf{[chưa có]}\fi}",
            *[rf"\providecommand{{\{n.capitalize()}}}[2]{{\resultmacro{{{n}}}{{#1}}{{#2}}}}"
              for n in ("res", "sd", "sig", "strat", "beyond", "samp", "lat", "val", "kx", "ext", "esig", "abl")],
        ]

    def add(self, family: str, a: str, b: str, value: str):
        self.lines.append(rf"\expandafter\def\csname {family}-{a}-{b}\endcsname{{{value}}}")

    def write(self, path: Path):
        path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")


def table(label: str, caption: str, colspec: str, header: list[str], rows: list[list[str]], note: str = "") -> str:
    body = "\n".join("        " + " & ".join(r) + r" \\" for r in rows)
    note_tex = f"\n    \\par\\smallskip{{\\footnotesize {note}}}" if note else ""
    # adjustbox max width: chỉ thu nhỏ bảng rộng hơn trang, không phóng to bảng ít cột (resizebox cũ làm chữ quá to).
    return (
        "% Sinh tự động bởi scripts/15_export_report.py — KHÔNG sửa tay.\n"
        "\\begin{table}[htbp]\n    \\centering\\small\n"
        f"    \\caption{{{caption}}}\n    \\label{{{label}}}\n"
        "    \\begin{adjustbox}{max width=\\textwidth}\n"
        f"    \\begin{{tabular}}{{{colspec}}}\n        \\toprule\n"
        f"        {' & '.join(header)} \\\\\n        \\midrule\n{body}\n        \\bottomrule\n"
        f"    \\end{{tabular}}\n    \\end{{adjustbox}}{note_tex}\n\\end{{table}}\n"
    )


def bold_max(values: dict[str, float], nd: int = 5) -> dict[str, str]:
    best = max(values.values())
    return {m: (rf"\textbf{{{vn(v, nd)}}}" if v == best else vn(v, nd)) for m, v in values.items()}


def params_text(model: str, p: dict) -> str:
    if model == "BPR-MF":
        return f"d={p['embedding_dim']}; lr={num(p['lr'])}; reg={num(p['reg'])}; {p['epochs']} epoch"
    if model == "NeuMF-Pretrained":
        return (f"GMF d={p['gmf_dim']} + MLP d={p['embedding_dim']}; lr={num(p['lr'])}; "
                f"$\\alpha$={num(p['alpha'])}; neg={p['negative_ratio']}; wd={num(p['weight_decay'])}")
    if model in ("ItemKNN", "UserKNN"):
        return f"k={p['k']}; shrink={num(p['shrink'])}"
    if model.startswith("LateFusion"):
        a = "GMF" if model == "LateFusion-GMF-MLP" else "BPR-MF"
        return f"$w$={num(p['w'])} ({a}), $1-w$={num(round(1 - p['w'], 1))} (MLP)"
    parts = [f"d={p['embedding_dim']}", f"lr={num(p['lr'])}", f"neg={p['negative_ratio']}",
             f"wd={num(p['weight_decay'])}"]
    if "dropout" in p:
        parts.append(f"dropout={num(p['dropout'])}")
    return "; ".join(parts)


def _row_value(r: list[str]) -> float:
    return float(r[2].replace("{,}", "."))


def export_tuning(m: Macros) -> str:
    best = json.loads((AUDIT / "best_configs.json").read_text(encoding="utf-8"))
    rows, ext_rows = [], []
    for model in [x for x in [*ORDER, *EXT_ORDER] if x in TUNE_KEY and TUNE_KEY[x] in best]:
        e = best[TUNE_KEY[model]]
        for metric in ("NDCG@10", "Recall@10", "HR@10"):
            m.add("val", KEY[model], mkey(metric), vn(e["val"][metric]))
        row = [show(model), params_text(model, e["params"]),
               vn(e["val"]["NDCG@10"]), vn(e["val"]["Recall@10"]), vn(e["val"]["HR@10"])]
        (ext_rows if model in EXT_ORDER else rows).append(row)
    rows.sort(key=lambda r: -_row_value(r))
    ext_rows.sort(key=lambda r: -_row_value(r))
    export_fusion_parts(m)
    caption = ("Cấu hình tốt nhất của từng mô hình sau tinh chỉnh siêu tham số (chỉ trên tập xác thực, seed 42, chia "
               "theo mốc thời gian chung; 6 cấu hình mỗi mô hình")
    note = ("d: số chiều Embedding; lr: tốc độ học; neg: số mẫu âm cho mỗi mẫu dương; wd: hệ số weight decay (điều "
            "chuẩn $L_2$); reg: hệ số điều chuẩn của BPR-MF; $\\alpha$: trọng số khởi tạo lớp đầu ra của "
            "NeuMF-Pretrained. Số trên tập xác thực của cấu hình tốt nhất là lạc quan (được chọn trên chính tập đó), "
            "không dùng để kết luận.")
    if ext_rows:
        rows.append([r"\midrule\multicolumn{5}{l}{\textit{Mở rộng sau khi đã xem kết quả trên tập kiểm thử "
                     r"(mục~\ref{sec:extension_results})}}"])
        rows.extend(ext_rows)
        caption += ", Late Fusion quét 11 giá trị $w$"
        note += (" k, shrink: số láng giềng và hệ số co (ItemKNN, UserKNN). Late Fusion: $w\\cdot$minmax(điểm thành "
                 "phần thứ nhất) $+ (1-w)\\cdot$minmax(điểm MLP); $w = 1$ và $w = 0$ cho đúng thứ hạng của từng thành "
                 "phần.")
    return table("tab:tuning", caption + ")", "llrrr",
                 ["Mô hình", "Cấu hình tốt nhất", "NDCG@10", "Recall@10", "HR@10"], rows, note)


def export_fusion_parts(m: Macros) -> None:
    """NDCG@10 val của từng thành phần late fusion khi đứng riêng (w = 1 / w = 0 trong tuning_log.csv)."""
    path = AUDIT / "tuning_log.csv"
    if not path.exists():
        return
    log = pd.read_csv(path)
    for model, key in (("late_gmf_mlp", "LFGM"), ("late_bpr_mlp", "LFBM")):
        rows = log[log["model"] == model]
        for w, name in ((1.0, "parta"), (0.0, "partb")):
            hit = rows[rows["params"].map(lambda s: json.loads(s).get("w") == w)]
            if len(hit):
                m.add("val", key, name, vn(float(hit["val_NDCG@10"].iloc[-1])))


SECOND_RUN_COMMIT = "c559c86"  # lần chấm thứ hai (29/09/2026); số của lần này được lưu ở audit/final_2909_*.csv


def run_info(commit: str, s: pd.DataFrame) -> str:
    """Câu mô tả số liệu đang dùng thuộc lần đánh giá nào — tự đổi sau lần chạy lại toàn bộ (PREREG mục 8, 02/10/2026)."""
    if commit.startswith(SECOND_RUN_COMMIT):
        return ("số liệu dưới đây là lần đánh giá thứ hai trên tập kiểm thử (29/09/2026), sau khi bổ sung bước huấn "
                "luyện lại; lần đánh giá đầu tiên cho cùng kết luận (mục~\\ref{sec:protocol}, phần lệch kế hoạch).")
    ref_s, ref_g = AUDIT / "final_2909_summary.csv", AUDIT / "final_2909_significance.csv"
    text = (f"số liệu dưới đây được sinh lại trong một lần chạy toàn bộ trên phiên bản mã nguồn cuối (mã phiên bản "
            f"\\texttt{{{commit[:7]}}}), theo kế hoạch đăng ký trước ở mục~\\ref{{sec:protocol}}")
    if not (ref_s.exists() and ref_g.exists() and (FINAL / "significance.csv").exists()):
        return text + "."
    ref = pd.read_csv(ref_s, index_col=0)
    common = [x for x in ORDER if x in ref.index and x in s.index]
    gap = max(abs(s.loc[x, "NDCG@10_mean"] - ref.loc[x, "NDCG@10_mean"]) for x in common)
    same = ("trùng khớp hoàn toàn" if gap == 0 else
            f"lệch tối đa {vn(gap)} (khác phần cứng hoặc thư viện; bảng dùng số của lần chạy lại)")
    n_new = int((pd.read_csv(FINAL / "significance.csv")["verdict"] != NOT_SIG).sum())
    n_ref = int((pd.read_csv(ref_g)["verdict"] != NOT_SIG).sum())
    verdict = (f"cả ba lần đánh giá cho cùng kết luận ({n_new}/8 so sánh đạt tiêu chí ``tốt hơn'')" if n_new == n_ref
               else f"kết luận kiểm định khác lần đánh giá thứ hai: {n_new}/8 so sánh đạt tiêu chí ``tốt hơn'' (lần thứ "
               f"hai: {n_ref}/8)")
    return f"{text}; so với lần đánh giá thứ hai (29/09/2026), NDCG@10 của 7 mô hình chính {same}, và {verdict}."


def export_final(m: Macros) -> str:
    s = pd.read_csv(FINAL / "summary.csv", index_col=0)
    cols = {}
    for metric in METRICS:
        cols[metric] = bold_max({x: s.loc[x, f"{metric}_mean"] for x in ORDER})
        for x in ORDER:
            m.add("res", KEY[x], mkey(metric), vn(s.loc[x, f"{metric}_mean"]))
            m.add("sd", KEY[x], mkey(metric), vn(s.loc[x, f"{metric}_std"]))
    ndcg = {x: s.loc[x, "NDCG@10_mean"] for x in ORDER}
    for x, r in ranks(ndcg).items():
        m.add("res", KEY[x], "rank", ORDINAL[r])
    m.add("res", "all", "best", show(max(ndcg, key=ndcg.get)))
    rows = [[show(x), *[f"{cols[mt][x]} $\\pm$ {vn(s.loc[x, f'{mt}_std'])}" for mt in METRICS]]
            for x in s.index if x in ORDER]
    r = json.loads(next(FINAL.glob("seed*/results.json")).read_text(encoding="utf-8"))
    m.add("res", "all", "runinfo", run_info(r["provenance"].get("git_commit") or "", s))
    n = lambda x: f"{x:,}".replace(",", ".")
    return table("tab:final", "Kết quả trên tập kiểm thử: trung bình $\\pm$ độ lệch chuẩn qua 3 seed (Full Ranking, "
                 "chia theo mốc thời gian chung, huấn luyện lại trên tập huấn luyện $\\cup$ xác thực; "
                 f"{n(r['n_test_users'])} người dùng, {n(r['n_candidate_items'])} sản phẩm ứng viên)", "lrrrrr",
                 ["Mô hình", *METRICS], rows, "In đậm: giá trị trung bình cao nhất mỗi cột.")


def export_significance(m: Macros) -> str:
    sig = pd.read_csv(FINAL / "significance.csv")
    rows = []
    for _, r in sig.iterrows():
        k = f"{KEY[r['A']]}{KEY[r['B']]}"
        vals = dict(rel=vn(r["rel_diff"] * 100, 1, sign=True) + "\\%", pw=vn(r["p_wilcoxon"], 3),
                    pholm=vn(r["p_holm"], 3), cilo=vn(r["ci_low"]), cihi=vn(r["ci_high"]))
        for name, v in vals.items():
            m.add("sig", k, name, v)
        m.add("sig", k, "verdict", verdict_phrase(r))
        rows.append([show(r["A"]), show(r["B"]), vn(r["mean_A"]), vn(r["mean_B"]), vals["rel"],
                     f"[{vals['cilo']}; {vals['cihi']}]", vals["pw"], vals["pholm"], verdict_cell(r)])
    m.add("sig", "all", "nbetter", str(int((sig["verdict"] != NOT_SIG).sum())))
    m.add("sig", "all", "n", str(len(sig)))
    summary_vn, summary_en = family_summary(sig, "họ so sánh chính")
    m.add("sig", "all", "summary", summary_vn)
    m.add("sig", "all", "summaryen", summary_en)
    m.add("sig", "all", "nusers", f"{int(sig['n_users'].iloc[0]):,}".replace(",", "."))
    return table("tab:significance", "Kiểm định cặp theo người dùng trên NDCG@10 (trung bình qua 3 seed): kiểm định "
                 "Wilcoxon signed-rank, khoảng tin cậy (CI) 95\\% bằng bootstrap cặp, hiệu chỉnh Holm trên họ 8 so "
                 "sánh", "llrrrrrrc",
                 ["A", "B", "NDCG@10 A", "NDCG@10 B", "Chênh", "CI 95\\% (A$-$B)", "p Wilcoxon", "p Holm",
                  "Kết luận"], rows, SIG_NOTE)


def export_secondary(m: Macros) -> list[tuple[str, str]]:
    out = []
    models = [x for x in ORDER if x != "Random"]
    if (FINAL / "stratified.csv").exists():
        st = pd.read_csv(FINAL / "stratified.csv").groupby(["model", "subset"]).mean(numeric_only=True)
        subsets = ["all", "head", "tail", "cold", "warm"]
        for x in models:
            for sub in subsets:
                m.add("strat", KEY[x], sub, vn(st.loc[(x, sub), "NDCG@10"]))
        n_users = {sub: int(st.loc[(models[0], sub), "n_users"]) for sub in subsets}
        for sub, n in n_users.items():
            m.add("strat", "n", sub, f"{n:,}".replace(",", "."))
        rows = [[show(x), *[vn(st.loc[(x, sub), "NDCG@10"]) for sub in subsets]] for x in models]
        out.append(("tab_stratified.tex", table(
            "tab:stratified", "NDCG@10 theo nhóm sản phẩm (head: 10\\% sản phẩm được mua nhiều nhất trong tập huấn "
            "luyện $\\cup$ xác thực) và nhóm người dùng (cold: 20\\% người dùng có ít tương tác nhất); trung bình 3 seed",
            "lrrrrr",
            ["Mô hình", f"Tất cả ({n_users['all']})", f"Head ({n_users['head']})", f"Tail ({n_users['tail']})",
             f"Cold ({n_users['cold']})", f"Warm ({n_users['warm']})"], rows,
            "Số trong ngoặc: số người dùng kiểm thử của nhóm. Người dùng có sản phẩm đúng ở cả head lẫn tail được tính "
            "ở cả hai nhóm, mỗi nhóm chỉ xét sản phẩm đúng của nhóm đó.")))
    if (FINAL / "beyond_accuracy.csv").exists():
        b = pd.read_csv(FINAL / "beyond_accuracy.csv").groupby("model").mean(numeric_only=True)
        rows = []
        for x in models:
            r = b.loc[x]
            vals = dict(coverage=f"{r['coverage'] * 100:.1f}\\%".replace(".", "{,}"), novelty=vn(r["novelty"], 2),
                        ARP=vn(r["ARP"], 1), HRR=f"{r['HRR'] * 100:.1f}\\%".replace(".", "{,}"))
            for k, v in vals.items():
                m.add("beyond", KEY[x], k, v)
            rows.append([show(x), *vals.values()])
        out.append(("tab_beyond.tex", table(
            "tab:beyond", "Chỉ số ngoài độ chính xác của danh sách top-10 trên tập kiểm thử (trung bình 3 seed)",
            "lrrrr", ["Mô hình", "Coverage", "Novelty (bit)", "ARP", "HRR"], rows,
            "Coverage: tỉ lệ sản phẩm xuất hiện trong ít nhất một danh sách top-10. Novelty: giá trị $-\\log_2 P(i)$ "
            "trung bình. ARP: số người dùng đã mua (trong tập huấn luyện $\\cup$ xác thực), tính trung bình trên các "
            "sản phẩm được gợi ý. HRR: tỉ lệ sản phẩm thuộc nhóm head trong top-10.")))
    if (FINAL / "sampled99.csv").exists():
        sp = pd.read_csv(FINAL / "sampled99.csv").groupby("model").mean(numeric_only=True)
        full = pd.read_csv(FINAL / "summary.csv", index_col=0)
        rows = []
        for x in models:
            f, s = full.loc[x, "NDCG@10_mean"], sp.loc[x, "NDCG@10"]
            m.add("samp", KEY[x], "NDCG10", vn(s, 4))
            m.add("samp", KEY[x], "HR10", vn(sp.loc[x, "HR@10"], 4))
            m.add("samp", KEY[x], "ratio", vn(s / f, 1))
            rows.append([show(x), vn(f), vn(s, 4), vn(sp.loc[x, "HR@10"], 4), vn(s / f, 1) + "$\\times$"])
        rank_full = full.loc[models, "NDCG@10_mean"].rank(ascending=False).astype(int)
        rank_samp = sp.loc[models, "NDCG@10"].rank(ascending=False).astype(int)
        m.add("samp", "all", "rankchanged", "có" if (rank_full != rank_samp).any() else "không")
        m.add("samp", "all", "ncases", f"{int(sp['n_cases'].iloc[0]):,}".replace(",", "."))
        out.append(("tab_sampled.tex", table(
            "tab:sampled", "Đối chiếu Full Ranking với Sampled-99 (1 sản phẩm đúng + 99 sản phẩm âm lấy ngẫu nhiên) "
            "trên tập kiểm thử; trung bình 3 seed", "lrrrr",
            ["Mô hình", "NDCG@10 Full", "NDCG@10 Sampled-99", "HR@10 Sampled-99", "Hệ số thổi phồng"], rows,
            "Hệ số thổi phồng = NDCG@10 Sampled-99 / NDCG@10 Full Ranking.")))
    if (FINAL / "latency.csv").exists():
        lat = pd.read_csv(FINAL / "latency.csv").set_index("model")
        rows = []
        for x in models:
            r = lat.loc[x]
            for k in ("p50_ms", "p95_ms", "mean_ms"):
                m.add("lat", KEY[x], k.removesuffix("_ms"), vn(r[k], 1))
            rows.append([show(x), vn(r["p50_ms"], 1), vn(r["p95_ms"], 1), vn(r["mean_ms"], 1)])
        r0 = lat.iloc[0]
        ncand = f"{r0['n_candidates_mean']:,.0f}".replace(",", ".")
        m.add("lat", "all", "cpu", str(r0["cpu"]).replace("_", "\\_"))
        m.add("lat", "all", "threads", str(int(r0["torch_threads"])))
        m.add("lat", "all", "n", str(int(r0["n_requests"])))
        m.add("lat", "all", "ncand", ncand)
        out.append(("tab_latency.tex", table(
            "tab:latency", "Độ trễ phục vụ một yêu cầu gợi ý top-10 trên CPU (tính điểm toàn bộ sản phẩm ứng viên "
            "của một người dùng rồi lấy top-10), tính bằng mili giây", "lrrr",
            ["Mô hình", "p50", "p95", "Trung bình"], rows,
            f"{int(r0['n_requests'])} yêu cầu, người dùng chọn ngẫu nhiên trong tập kiểm thử, trung bình {ncand} "
            f"sản phẩm ứng viên mỗi yêu cầu; CPU: {cpu_name(r0['cpu'])}, {int(r0['torch_threads'])} luồng PyTorch. "
            "p50, p95: trung vị và phân vị 95 của độ trễ.")))
    return out


def cpu_name(raw) -> str:
    """Tên CPU cho chú thích bảng: platform.processor() trên Windows trả về dạng 'AMD64 Family 25 ..., AuthenticAMD'."""
    s = str(raw).replace("_", " ")
    return s.replace(", AuthenticAMD", " (AMD)").replace(", GenuineIntel", " (Intel)")


def export_extra_k(m: Macros, k: int = 20) -> list[tuple[str, str]]:
    """Chỉ số @k tính lại từ hạng đã lưu (scripts/16_extra_k.py) — mô tả, không kết luận."""
    path = FINAL / f"extra_k{k}.csv"
    if not path.exists():
        return []
    df = pd.read_csv(path, index_col=0)
    names = [f"NDCG@{k}", f"Recall@{k}", f"HR@{k}", f"Precision@{k}"]
    models = [x for x in [*ORDER, *EXT_ORDER] if x in df.index]
    cols = {mt: bold_max({x: df.loc[x, f"{mt}_mean"] for x in models}) for mt in names}
    rows = []
    for x in models:
        for mt in names:
            m.add("kx", KEY[x], mkey(mt), vn(df.loc[x, f"{mt}_mean"]))
        rows.append([show(x), *[f"{cols[mt][x]} $\\pm$ {vn(df.loc[x, f'{mt}_std'])}" for mt in names]])
    return [(f"tab_k{k}.tex", table(
        f"tab:k{k}", f"Chỉ số ở K = {k} trên tập kiểm thử, tính lại từ thứ hạng đã lưu của lần đánh giá (không đánh "
        "giá lại mô hình); trung bình $\\pm$ độ lệch chuẩn qua 3 seed", "lrrrr", ["Mô hình", *names], rows,
        "Chỉ số mô tả bổ sung, không dùng để kết luận (chỉ số chính đã đăng ký là NDCG@10)."))]


def verdict_phrase(r) -> str:
    """Kết luận của một cặp (A, B) bằng câu chữ: không có ý nghĩa, hoặc mô hình nào tốt hơn."""
    if r["verdict"] == NOT_SIG:
        return NOT_SIG
    return f"{show(r['A'] if r['verdict'] == 'A tốt hơn' else r['B'])} tốt hơn có ý nghĩa"


def verdict_cell(r) -> str:
    """Ô "Kết luận" trong bảng kiểm định: "---" khi không có ý nghĩa (giải thích ở chú thích) để bảng 9 cột đủ hẹp."""
    return "---" if r["verdict"] == NOT_SIG else r["verdict"]


SIG_NOTE = ("---: không khác biệt có ý nghĩa. ``A tốt hơn'' (hoặc ``B tốt hơn'') chỉ khi đồng thời p Holm $<$ 0,05, "
            "CI không chứa 0 và chênh lệch tương đối $\\geq$ 5\\%.")


def family_summary(s: pd.DataFrame, family: str) -> tuple[str, str]:
    """Câu tóm tắt (tiếng Việt, tiếng Anh) cho một họ so sánh — sinh từ significance.csv để câu chữ trong báo cáo
    luôn khớp số liệu sau mỗi lần chạy lại."""
    sig = s[s["verdict"] != NOT_SIG]
    n = len(s)
    if sig.empty:
        return (f"Không so sánh nào trong {n} so sánh của {family} đạt tiêu chí ``tốt hơn''.",
                f"none of the {n} comparisons meets the pre-specified criterion")
    parts_vn, parts_en = [], []
    for _, r in sig.iterrows():
        higher = r["diff"] > 0
        parts_vn.append(f"{show(r['A'])} {'cao' if higher else 'thấp'} hơn {show(r['B'])} "
                        f"{vn(abs(r['rel_diff']) * 100, 1)}\\% ($p_{{Holm}}$ = {vn(r['p_holm'], 3)})")
        parts_en.append(f"{show(r['A'])} {'outperforms' if higher else 'underperforms'} {show(r['B'])}")
    return (f"{len(sig)}/{n} so sánh của {family} đạt tiêu chí ``tốt hơn'': " + "; ".join(parts_vn) + ".",
            f"{len(sig)} of the {n} comparisons meet the criterion: " + "; ".join(parts_en))


def export_extension(m: Macros) -> list[tuple[str, str]]:
    """Kết quả mở rộng PREREG mục 9 (scripts/17_extension.py): late fusion MF + DNN, ItemKNN, UserKNN."""
    ext_dir = FINAL / "extension"
    if not (ext_dir / "summary.csv").exists():
        return []
    ext = pd.read_csv(ext_dir / "summary.csv", index_col=0)
    main_s = pd.read_csv(FINAL / "summary.csv", index_col=0)
    both = pd.concat([ext, main_s[~main_s.index.isin(ext.index)]])
    models = [x for x in [*EXT_ORDER, *ORDER] if x in both.index]
    models.sort(key=lambda x: -both.loc[x, "NDCG@10_mean"])
    shown = ["NDCG@10", "Recall@10", "HR@10"]
    cols = {mt: bold_max({x: both.loc[x, f"{mt}_mean"] for x in models}) for mt in shown}
    ndcg = {x: both.loc[x, "NDCG@10_mean"] for x in models}
    rank = ranks(ndcg)
    m.add("ext", "all", "best", show(max(ndcg, key=ndcg.get)))
    m.add("ext", "all", "nmodels", str(len(models)))
    rows = []
    for x in models:
        m.add("ext", KEY[x], "rank", ORDINAL[rank[x]])
        if x in ext.index:
            for mt in METRICS:
                m.add("ext", KEY[x], mkey(mt), vn(ext.loc[x, f"{mt}_mean"]))
                m.add("ext", KEY[x], "sd" + mkey(mt), vn(ext.loc[x, f"{mt}_std"]))
        name = f"{show(x)}$^{{\\dagger}}$" if x in EXT_ORDER else show(x)
        rows.append([name, *[f"{cols[mt][x]} $\\pm$ {vn(both.loc[x, f'{mt}_std'])}" for mt in shown]])
    out = [("tab_extension.tex", table(
        "tab:extension", "Mô hình mở rộng (đánh dấu $\\dagger$) đặt cạnh các mô hình chính trên tập kiểm thử, xếp "
        "theo NDCG@10; trung bình $\\pm$ độ lệch chuẩn qua 3 seed", "lrrr",
        ["Mô hình", *shown], rows,
        "$^{\\dagger}$Bổ sung sau khi đã xem kết quả trên tập kiểm thử lần đầu (mục~\\ref{sec:protocol}). Late "
        "Fusion: $w\\cdot$minmax(điểm thành phần thứ nhất) $+ (1-w)\\cdot$minmax(điểm MLP), hai mô hình huấn luyện "
        "riêng, $w$ chọn trên tập xác thực. ItemKNN, UserKNN: $k$ láng giềng gần nhất theo độ tương đồng cosine, tất "
        "định nên độ lệch chuẩn bằng 0."))]
    sig_path = ext_dir / "significance.csv"
    if sig_path.exists():
        s = pd.read_csv(sig_path)
        rows = []
        for _, r in s.iterrows():
            key = f"{KEY[r['A']]}{KEY[r['B']]}"
            vals = dict(rel=vn(r["rel_diff"] * 100, 1, sign=True) + "\\%", pw=vn(r["p_wilcoxon"], 3),
                        pholm=vn(r["p_holm"], 3), cilo=vn(r["ci_low"]), cihi=vn(r["ci_high"]))
            for name, v in vals.items():
                m.add("esig", key, name, v)
            m.add("esig", key, "verdict", verdict_phrase(r))
            rows.append([show(r["A"]), show(r["B"]), vn(r["mean_A"]), vn(r["mean_B"]), vals["rel"],
                         f"[{vals['cilo']}; {vals['cihi']}]", vals["pw"], vals["pholm"], verdict_cell(r)])
        m.add("esig", "all", "nbetter", str(int((s["verdict"] != NOT_SIG).sum())))
        m.add("esig", "all", "n", str(len(s)))
        summary_vn, summary_en = family_summary(s, "họ mở rộng")
        m.add("esig", "all", "summary", summary_vn)
        m.add("esig", "all", "summaryen", summary_en)
        out.append(("tab_ext_significance.tex", table(
            "tab:ext_significance", "Kiểm định cặp theo người dùng trên NDCG@10 cho họ 7 so sánh mở rộng: kiểm định "
            "Wilcoxon signed-rank, khoảng tin cậy (CI) 95\\% bằng bootstrap cặp, hiệu chỉnh Holm riêng trong họ",
            "llrrrrrrc",
            ["A", "B", "NDCG@10 A", "NDCG@10 B", "Chênh", "CI 95\\% (A$-$B)", "p Wilcoxon", "p Holm", "Kết luận"],
            rows, SIG_NOTE + " Cùng tiêu chí với họ so sánh chính; họ này được đăng ký sau khi đã xem kết quả trên tập "
                  "kiểm thử của các mô hình chính và không gộp với họ 8 so sánh chính.")))
    return out


ABLATION = PROJECT_ROOT / "outputs" / "ablation" / "ablation_val.csv"
ABL_FACTORS = [("embedding_dim", "d", "Số chiều Embedding $d$"), ("n_hidden", "layers", "Số tầng ẩn MLP"),
               ("negative_ratio", "neg", "Số mẫu âm / mẫu dương")]


def pct(x: float) -> str:
    return vn(100 * x, 1) + "\\%"


def ablation_summary(a: pd.DataFrame) -> str:
    """Câu mô tả kết quả ablation (sinh theo số liệu — đúng sau mỗi lần chạy lại 20_ablation.py)."""
    base = a[a["factor"] == "base"].iloc[0]
    best, spread = {}, {}
    for factor, key, _ in ABL_FACTORS:
        rows = a[a["factor"].isin([factor, "base"])]
        top, low = rows.loc[rows["NDCG@10"].idxmax()], rows.loc[rows["NDCG@10"].idxmin()]
        best[key] = (int(top[factor]), float(top["NDCG@10"]))
        spread[key] = (float(top["NDCG@10"]) - float(low["NDCG@10"])) / float(low["NDCG@10"])
    text = (f"Trên tập xác thực, NDCG@10 cao nhất khi $d = {best['d'][0]}$ ({vn(best['d'][1])}), khi tháp MLP có "
            f"{best['layers'][0]} tầng ẩn ({vn(best['layers'][1])}) và khi dùng {best['neg'][0]} mẫu âm cho mỗi mẫu "
            f"dương ({vn(best['neg'][1])}); cấu hình đã chọn ($d = {int(base['embedding_dim'])}$, "
            f"{int(base['n_hidden'])} tầng ẩn, {int(base['negative_ratio'])} mẫu âm) đạt {vn(float(base['NDCG@10']))}. ")
    layers = a[a["factor"].isin(["n_hidden", "base"])].set_index("n_hidden")["NDCG@10"]
    n_best, deepest = best["layers"][0], int(layers.index.max())
    # Chỉ mô tả xu hướng trên dữ liệu của đề tài; không so với số liệu công bố của tài liệu tham khảo (khác dữ liệu và
    # giao thức đánh giá — tài liệu chỉ là cơ sở phương pháp).
    if n_best == 0:
        text += ("Bỏ hẳn các tầng ẩn (nhánh MLP chỉ nối hai Embedding) cho kết quả tốt nhất, tức trên dữ liệu này tháp "
                 "sâu hơn không giúp ích. ")
    elif n_best < deepest:
        text += (f"Tháp nông với {n_best} tầng ẩn là tốt nhất; thêm tầng không cải thiện thêm ({deepest} tầng: "
                 f"{vn(float(layers[deepest]))}). ")
    else:
        text += (f"Tháp sâu nhất ({deepest} tầng ẩn) cho kết quả tốt nhất (không có tầng ẩn: {vn(float(layers[0]))}), "
                 "tức trên dữ liệu này tăng độ sâu của tháp MLP có giúp ích. ")
    text += (f"Chênh lệch giữa mức tốt nhất và kém nhất của từng yếu tố lần lượt là {pct(spread['d'])} (số chiều), "
             f"{pct(spread['layers'])} (số tầng) và {pct(spread['neg'])} (số mẫu âm).")
    return text


def export_ablation(m: Macros) -> list[tuple[str, str]]:
    """Ablation trên validation (scripts/20_ablation.py) — đề cương chi tiết mục 5.3; mô tả, không chọn lại mô hình."""
    if not ABLATION.exists():
        return []
    a = pd.read_csv(ABLATION, dtype={"value": str}, keep_default_na=False)
    if "base" not in set(a["factor"]) or not all(f in set(a["factor"]) for f, _, _ in ABL_FACTORS):
        print("Ablation chưa đủ cấu hình (thiếu cấu hình gốc hoặc một yếu tố) — chưa xuất bảng")
        return []
    base = a[a["factor"] == "base"].iloc[0]
    rows = []
    for gi, (factor, key, label) in enumerate(ABL_FACTORS):
        part = a[a["factor"].isin([factor, "base"])].sort_values(factor)
        for ri, (_, r) in enumerate(part.iterrows()):  # iterrows giữ tên cột có "@" (itertuples đổi tên)
            is_base = r["factor"] == "base"
            value = int(r[factor])
            m.add("abl", key, str(value), vn(float(r["NDCG@10"])))
            name = ("\\midrule " if gi and ri == 0 else "") + (label if ri == 0 else "")
            shown = f"\\textbf{{{value}}} (chọn)" if is_base else str(value)
            rows.append([name, shown, vn(float(r["NDCG@10"])), vn(float(r["Recall@10"])), vn(float(r["HR@10"])),
                         str(int(r["best_epoch"])), f"{int(r['n_params']):,}".replace(",", ".")])
        top = part.loc[part["NDCG@10"].idxmax()]
        m.add("abl", key, "best", str(int(top[factor])))
        m.add("abl", key, "bestval", vn(float(top["NDCG@10"])))
    m.add("abl", "base", "NDCG10", vn(float(base["NDCG@10"])))
    m.add("abl", "all", "nconfigs", str(len(a)))
    m.add("abl", "all", "summary", ablation_summary(a))
    return [("tab_ablation.tex", table(
        "tab:ablation", "Ablation NeuMF-Scratch trên tập xác thực: đổi lần lượt từng yếu tố quanh cấu hình đã chọn, "
        "giữ nguyên các siêu tham số còn lại (seed 42)", "llrrrrr",
        ["Yếu tố", "Giá trị", "NDCG@10", "Recall@10", "HR@10", "Epoch tốt nhất", "Số tham số"], rows,
        "Tháp MLP giảm một nửa mỗi tầng ($[2d \\to d \\to d/2 \\to \\dots]$); 0 tầng ẩn = nhánh MLP chỉ nối hai "
        "Embedding. Một seed, chỉ trên tập xác thực: phân tích mô tả, không dùng để chọn lại cấu hình của đánh giá "
        "cuối."))]


def main():
    TABLES.mkdir(parents=True, exist_ok=True)
    m = Macros()
    files = [("tab_tuning.tex", export_tuning(m)), ("tab_final.tex", export_final(m)),
             ("tab_significance.tex", export_significance(m)), *export_secondary(m),
             *export_extra_k(m), *export_extension(m), *export_ablation(m)]
    for name, tex in files:
        (TABLES / name).write_text(tex, encoding="utf-8")
    m.write(TABLES / "results_macros.tex")
    FIG_OUT.mkdir(parents=True, exist_ok=True)
    figs = sorted(FIG.glob("final_*.png"))
    for f in figs:
        shutil.copy(f, FIG_OUT / f.name)
    print("Bảng:", *(n for n, _ in files), "+ results_macros.tex")
    print("Hình:", *(f.name for f in figs) or ["(chưa có — chạy 13_plot_final.py)"])
    missing = [n for n in ("stratified.csv", "beyond_accuracy.csv", "sampled99.csv", "latency.csv")
               if not (FINAL / n).exists()]
    if missing:
        print("Chưa có (chạy 14_secondary.py):", *missing)


if __name__ == "__main__":
    main()
