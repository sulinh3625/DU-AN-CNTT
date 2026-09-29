"""Xuất số liệu cuối sang báo cáo LaTeX (Report DACNTT/) — mọi số trong C4/C5/tóm tắt lấy từ đây, không gõ tay.

    python scripts/15_export_report.py

Đọc: audit/best_configs.json, outputs/final/{summary,significance}.csv và (nếu có) các file của 14_secondary.py.
Ghi:
  Report DACNTT/content/tables/results_macros.tex   macro \\Res{Pre}{NDCG10}, \\Sd, \\Sig, \\Strat, \\Beyond, \\Samp, \\Lat, \\Val
  Report DACNTT/content/tables/tab_*.tex            bảng (table float có caption + label)
  Report DACNTT/media/figures/final/*.png           chép từ outputs/figures/final_*.png
File nguồn nào chưa có thì bảng tương ứng không được sinh; báo cáo hiện ghi chú "chưa có số liệu" ở chỗ đó.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FINAL = PROJECT_ROOT / "outputs" / "final"
FIG = PROJECT_ROOT / "outputs" / "figures"
REPORT = PROJECT_ROOT.parent / "Report DACNTT"
TABLES = REPORT / "content" / "tables"
FIG_OUT = REPORT / "media" / "figures" / "final"

ORDER = ["NeuMF-Pretrained", "NeuMF-Scratch", "GMF", "MLP", "BPR-MF", "MostPopular", "Random"]
KEY = {"NeuMF-Pretrained": "Pre", "NeuMF-Scratch": "Scr", "GMF": "GMF", "MLP": "MLP", "BPR-MF": "BPR",
       "MostPopular": "MostPop", "Random": "Random"}
TUNE_KEY = {"NeuMF-Pretrained": "neumf_pretrained", "NeuMF-Scratch": "neumf_scratch", "GMF": "gmf", "MLP": "mlp",
            "BPR-MF": "bpr"}
METRICS = ["NDCG@10", "Recall@10", "HR@10", "Precision@10", "NDCG@5"]


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
            "% Sinh tự động bởi neumf_project_v2/scripts/15_export_report.py — KHÔNG sửa tay.",
            r"\providecommand{\resultmacro}[3]{\ifcsname #1-#2-#3\endcsname\csname #1-#2-#3\endcsname"
            r"\else\textbf{[chưa có]}\fi}",
            *[rf"\providecommand{{\{n.capitalize()}}}[2]{{\resultmacro{{{n}}}{{#1}}{{#2}}}}"
              for n in ("res", "sd", "sig", "strat", "beyond", "samp", "lat", "val")],
        ]

    def add(self, family: str, a: str, b: str, value: str):
        self.lines.append(rf"\expandafter\def\csname {family}-{a}-{b}\endcsname{{{value}}}")

    def write(self, path: Path):
        path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")


def table(label: str, caption: str, colspec: str, header: list[str], rows: list[list[str]], note: str = "") -> str:
    body = "\n".join("        " + " & ".join(r) + r" \\" for r in rows)
    note_tex = f"\n    \\par\\smallskip{{\\footnotesize {note}}}" if note else ""
    return (
        "% Sinh tự động bởi scripts/15_export_report.py — KHÔNG sửa tay.\n"
        "\\begin{table}[htbp]\n    \\centering\n"
        f"    \\caption{{{caption}}}\n    \\label{{{label}}}\n"
        "    \\resizebox{\\textwidth}{!}{%\n"
        f"    \\begin{{tabular}}{{{colspec}}}\n        \\toprule\n"
        f"        {' & '.join(header)} \\\\\n        \\midrule\n{body}\n        \\bottomrule\n"
        f"    \\end{{tabular}}}}{note_tex}\n\\end{{table}}\n"
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
    parts = [f"d={p['embedding_dim']}", f"lr={num(p['lr'])}", f"neg={p['negative_ratio']}",
             f"wd={num(p['weight_decay'])}"]
    if "dropout" in p:
        parts.append(f"dropout={num(p['dropout'])}")
    return "; ".join(parts)


def export_tuning(m: Macros) -> str:
    best = json.loads((PROJECT_ROOT / "audit" / "best_configs.json").read_text(encoding="utf-8"))
    models = [x for x in ORDER if x in TUNE_KEY]
    rows = []
    for model in models:
        e = best[TUNE_KEY[model]]
        for metric in ("NDCG@10", "Recall@10", "HR@10"):
            m.add("val", KEY[model], mkey(metric), vn(e["val"][metric]))
        rows.append([model, params_text(model, e["params"]),
                     vn(e["val"]["NDCG@10"]), vn(e["val"]["Recall@10"]), vn(e["val"]["HR@10"])])
    rows.sort(key=lambda r: -float(r[2].replace("{,}", ".")))
    return table("tab:tuning", "Cấu hình tốt nhất của từng mô hình sau tuning (chỉ trên tập validation, seed 42, "
                 "6 cấu hình/mô hình, protocol mốc thời gian chung)", "llrrr",
                 ["Mô hình", "Cấu hình tốt nhất", "NDCG@10", "Recall@10", "HR@10"], rows,
                 "Số trên validation của cấu hình tốt nhất lạc quan (chọn trên chính tập đó); không dùng để kết luận.")


def export_final(m: Macros) -> str:
    s = pd.read_csv(FINAL / "summary.csv", index_col=0)
    cols = {}
    for metric in METRICS:
        cols[metric] = bold_max({x: s.loc[x, f"{metric}_mean"] for x in ORDER})
        for x in ORDER:
            m.add("res", KEY[x], mkey(metric), vn(s.loc[x, f"{metric}_mean"]))
            m.add("sd", KEY[x], mkey(metric), vn(s.loc[x, f"{metric}_std"]))
    rows = [[x, *[f"{cols[mt][x]} $\\pm$ {vn(s.loc[x, f'{mt}_std'])}" for mt in METRICS]]
            for x in s.index if x in ORDER]
    return table("tab:final", "Kết quả trên tập test: trung bình $\\pm$ độ lệch chuẩn qua 3 seed "
                 "(Full Ranking, protocol mốc thời gian chung, 2.893 user, 10.145 item candidate)", "lrrrrr",
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
        rows.append([r["A"], r["B"], vn(r["mean_A"]), vn(r["mean_B"]), vals["rel"],
                     f"[{vals['cilo']}; {vals['cihi']}]", vals["pw"], vals["pholm"], r["verdict"]])
    m.add("sig", "all", "nbetter", str(int((sig["verdict"] != "không khác biệt có ý nghĩa").sum())))
    m.add("sig", "all", "n", str(len(sig)))
    m.add("sig", "all", "nusers", f"{int(sig['n_users'].iloc[0]):,}".replace(",", "."))
    return table("tab:significance", "Kiểm định cặp theo user trên NDCG@10 (trung bình qua 3 seed): Wilcoxon "
                 "signed-rank, CI 95\\% paired bootstrap, hiệu chỉnh Holm trên họ 8 so sánh", "llrrrrrrl",
                 ["A", "B", "NDCG@10 A", "NDCG@10 B", "Chênh", "CI 95\\% (A$-$B)", "p Wilcoxon", "p Holm",
                  "Kết luận"], rows,
                 "``A tốt hơn B'' chỉ khi đồng thời p Holm $<$ 0,05, CI không chứa 0 và chênh lệch tương đối $\\geq$ 5\\%.")


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
        rows = [[x, *[vn(st.loc[(x, sub), "NDCG@10"]) for sub in subsets]] for x in models]
        out.append(("tab_stratified.tex", table(
            "tab:stratified", "NDCG@10 theo nhóm item (head = 10\\% item phổ biến nhất trong train) và nhóm user "
            "(cold = 20\\% user ít tương tác train nhất); trung bình 3 seed", "lrrrrr",
            ["Mô hình", f"Tất cả ({n_users['all']})", f"Head ({n_users['head']})", f"Tail ({n_users['tail']})",
             f"Cold ({n_users['cold']})", f"Warm ({n_users['warm']})"], rows,
            "Số trong ngoặc: số user test của nhóm. User có item đúng ở cả head lẫn tail được tính ở cả hai nhóm, "
            "mỗi nhóm chỉ xét item đúng của nhóm đó.")))
    if (FINAL / "beyond_accuracy.csv").exists():
        b = pd.read_csv(FINAL / "beyond_accuracy.csv").groupby("model").mean(numeric_only=True)
        rows = []
        for x in models:
            r = b.loc[x]
            vals = dict(coverage=f"{r['coverage'] * 100:.1f}\\%".replace(".", "{,}"), novelty=vn(r["novelty"], 2),
                        ARP=vn(r["ARP"], 1), HRR=f"{r['HRR'] * 100:.1f}\\%".replace(".", "{,}"))
            for k, v in vals.items():
                m.add("beyond", KEY[x], k, v)
            rows.append([x, *vals.values()])
        out.append(("tab_beyond.tex", table(
            "tab:beyond", "Chỉ số ngoài độ chính xác của danh sách top-10 trên tập test (trung bình 3 seed)",
            "lrrrr", ["Mô hình", "Coverage", "Novelty (bit)", "ARP", "HRR"], rows,
            "Coverage: tỉ lệ item xuất hiện trong ít nhất một top-10. Novelty: $-\\log_2 P(i)$ trung bình. "
            "ARP: số tương tác train trung bình của item được gợi ý. HRR: tỉ lệ item head trong top-10.")))
    if (FINAL / "sampled99.csv").exists():
        sp = pd.read_csv(FINAL / "sampled99.csv").groupby("model").mean(numeric_only=True)
        full = pd.read_csv(FINAL / "summary.csv", index_col=0)
        rows = []
        for x in models:
            f, s = full.loc[x, "NDCG@10_mean"], sp.loc[x, "NDCG@10"]
            m.add("samp", KEY[x], "NDCG10", vn(s, 4))
            m.add("samp", KEY[x], "HR10", vn(sp.loc[x, "HR@10"], 4))
            m.add("samp", KEY[x], "ratio", vn(s / f, 1))
            rows.append([x, vn(f), vn(s, 4), vn(sp.loc[x, "HR@10"], 4), vn(s / f, 1) + "$\\times$"])
        rank_full = full.loc[models, "NDCG@10_mean"].rank(ascending=False).astype(int)
        rank_samp = sp.loc[models, "NDCG@10"].rank(ascending=False).astype(int)
        m.add("samp", "all", "rankchanged", "có" if (rank_full != rank_samp).any() else "không")
        m.add("samp", "all", "ncases", f"{int(sp['n_cases'].iloc[0]):,}".replace(",", "."))
        out.append(("tab_sampled.tex", table(
            "tab:sampled", "Đối chiếu Full Ranking với Sampled-99 (1 item đúng + 99 item âm, protocol NCF gốc) "
            "trên tập test; trung bình 3 seed", "lrrrr",
            ["Mô hình", "NDCG@10 Full", "NDCG@10 Sampled-99", "HR@10 Sampled-99", "Hệ số thổi phồng"], rows,
            "Hệ số thổi phồng = NDCG@10 Sampled-99 / NDCG@10 Full Ranking.")))
    if (FINAL / "latency.csv").exists():
        lat = pd.read_csv(FINAL / "latency.csv").set_index("model")
        rows = []
        for x in models:
            r = lat.loc[x]
            for k in ("p50_ms", "p95_ms", "mean_ms"):
                m.add("lat", KEY[x], k.removesuffix("_ms"), vn(r[k], 1))
            rows.append([x, vn(r["p50_ms"], 1), vn(r["p95_ms"], 1), vn(r["mean_ms"], 1)])
        r0 = lat.iloc[0]
        ncand = f"{r0['n_candidates_mean']:,.0f}".replace(",", ".")
        m.add("lat", "all", "cpu", str(r0["cpu"]).replace("_", "\\_"))
        m.add("lat", "all", "threads", str(int(r0["torch_threads"])))
        m.add("lat", "all", "n", str(int(r0["n_requests"])))
        m.add("lat", "all", "ncand", ncand)
        out.append(("tab_latency.tex", table(
            "tab:latency", "Độ trễ phục vụ một yêu cầu gợi ý top-10 trên CPU (chấm toàn bộ candidate của một user "
            "rồi lấy top-10), mili giây", "lrrr", ["Mô hình", "p50", "p95", "Trung bình"], rows,
            f"{int(r0['n_requests'])} yêu cầu, user chọn ngẫu nhiên trong tập test, trung bình {ncand} "
            f"candidate/yêu cầu; CPU: {str(r0['cpu']).replace('_', ' ')}, "
            f"{int(r0['torch_threads'])} luồng PyTorch.")))
    return out


def main():
    TABLES.mkdir(parents=True, exist_ok=True)
    m = Macros()
    files = [("tab_tuning.tex", export_tuning(m)), ("tab_final.tex", export_final(m)),
             ("tab_significance.tex", export_significance(m)), *export_secondary(m)]
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
