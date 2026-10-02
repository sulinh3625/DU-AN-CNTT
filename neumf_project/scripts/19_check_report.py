"""Đối chiếu báo cáo và tài liệu với số liệu hiện có — bước cuối của `python run.py final`; không chấm test.

    python scripts/19_check_report.py            # in kết quả, luôn trả mã 0
    python scripts/19_check_report.py --strict   # trả mã 1 nếu có khẳng định sai / macro, bảng thiếu

Bốn phần:
  1. Tái lập: outputs/final/{summary,significance,stratified,beyond_accuracy,sampled99}.csv so với bản đã commit
     (git HEAD) — độ lệch tuyệt đối lớn nhất. Chạy lại trên cùng máy kỳ vọng lệch 0 (PREREG mục 8, 02/10/2026).
  2. Khẳng định bằng chữ trong báo cáo (Chương 1, 4, 5, tóm tắt) mà macro số liệu không tự cập nhật — mỗi khẳng định
     là một điều kiện trên CSV; sai thì in tệp:dòng cần sửa.
  3. Số chép tay trong van_dap.md, pham_vi_du_an.md, README.md, notebook Colab: nếu số trong CSV khác bản đã commit,
     liệt kê các dòng còn ghi số cũ.
  4. Mọi macro (\\Res, \\Sig, \\Ext, ...) và mọi bảng \\bangketqua{...} mà báo cáo dùng đều đã được 15_export_report.py
     sinh (nếu không, PDF hiện "[chưa có]" / khung "Chưa có số liệu").
"""
from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parent
FINAL = PROJECT_ROOT / "outputs" / "final"
REPORT = REPO_ROOT / "Report DACNTT"
TABLES = REPORT / "content" / "tables"
MAIN = ["NeuMF-Pretrained", "NeuMF-Scratch", "GMF", "MLP", "BPR-MF", "MostPopular", "Random"]
LEARNED = ["NeuMF-Pretrained", "NeuMF-Scratch", "GMF", "MLP", "BPR-MF"]
NEURAL = ["NeuMF-Pretrained", "NeuMF-Scratch", "GMF", "MLP"]
SECONDARY = ["NeuMF-Pretrained", "NeuMF-Scratch", "GMF", "MLP", "BPR-MF", "MostPopular"]
METRICS = ["NDCG@10", "Recall@10", "HR@10", "Precision@10", "NDCG@5"]
NOT_SIG = "không khác biệt có ý nghĩa"
DOCS = [REPO_ROOT / "van_dap.md", PROJECT_ROOT / "pham_vi_du_an.md", PROJECT_ROOT / "README.md",
        REPO_ROOT / "README.md", PROJECT_ROOT / "notebooks" / "colab_final.ipynb"]


# ---------------------------------------------------------------- dữ liệu
def read_csv(name: str, committed: bool = False, **kw) -> pd.DataFrame | None:
    if not committed:
        path = FINAL / name
        return pd.read_csv(path, **kw) if path.exists() else None
    res = subprocess.run(["git", "show", f"HEAD:./outputs/final/{name}"], cwd=PROJECT_ROOT, capture_output=True)
    return pd.read_csv(io.BytesIO(res.stdout), **kw) if res.returncode == 0 else None


class Data:
    def __init__(self):
        self.S = read_csv("summary.csv", index_col=0)
        g = read_csv("significance.csv")
        self.G = None if g is None else g.set_index(["A", "B"])
        st = read_csv("stratified.csv")
        self.ST = None if st is None else st.groupby(["model", "subset"])["NDCG@10"].mean()
        b = read_csv("beyond_accuracy.csv")
        self.B = None if b is None else b.groupby("model").mean(numeric_only=True)
        sp = read_csv("sampled99.csv")
        self.SP = None if sp is None else sp.groupby("model").mean(numeric_only=True)
        self.K20 = read_csv("extra_k20.csv", index_col=0)
        self.epochs = []
        for p in sorted(FINAL.glob("seed*/results.json")):
            meta = json.loads(p.read_text(encoding="utf-8")).get("train_meta", {})
            self.epochs += [int(meta[m]["best_epoch"]) for m in NEURAL if m in meta and meta[m].get("best_epoch")]

    # tiện ích cho các khẳng định
    def ndcg(self, models=MAIN) -> dict:
        return {m: self.S.loc[m, "NDCG@10_mean"] for m in models}

    def rank(self, model, models=MAIN) -> int:
        v = self.ndcg(models)
        return 1 + sum(x > v[model] for x in v.values())

    def not_sig(self, *pairs) -> bool:
        return all(self.G.loc[p, "verdict"] == NOT_SIG for p in pairs)


def argmax(d: dict):
    return max(d, key=d.get)


def argmin(d: dict):
    return min(d, key=d.get)


# ---------------------------------------------------------- khẳng định
# (tệp, đoạn văn bản neo để tìm dòng, mô tả, điều kiện, các nguồn dữ liệu cần có)
def claims(d: Data):
    S, G, ST, B, SP, K20 = d.S, d.G, d.ST, d.B, d.SP, d.K20
    neural_spread = lambda: (max(d.ndcg(NEURAL).values()) - min(d.ndcg(NEURAL).values())
                             <= max(S.loc[m, "NDCG@10_std"] for m in NEURAL))
    main_pairs = list(G.index) if G is not None else []
    return [
        ("content/C4.tex", "NDCG@10 cao nhất khoảng 0,01", "NDCG@10 cao nhất làm tròn bằng 0,01",
         lambda: round(max(d.ndcg().values()), 2) == 0.01, ["S"]),
        ("content/C4.tex", "BPR-MF có trung bình cao nhất trên mọi độ đo", "BPR-MF cao nhất ở cả 5 độ đo",
         lambda: all(argmax({m: S.loc[m, f"{mt}_mean"] for m in MAIN}) == "BPR-MF" for mt in METRICS), ["S"]),
        ("content/C4.tex", "NeuMF-Pretrained ngang Most Popular", "NeuMF-Pretrained vs Most Popular không có ý nghĩa",
         lambda: d.not_sig(("NeuMF-Pretrained", "MostPopular")), ["G"]),
        ("content/C4.tex", "GMF, MLP và hai biến thể NeuMF nằm sát nhau",
         "Trong GMF, MLP, 2 NeuMF: thấp nhất GMF, cao nhất NeuMF-Pretrained, khoảng cách ≤ độ lệch chuẩn lớn nhất",
         lambda: argmin(d.ndcg(NEURAL)) == "GMF" and argmax(d.ndcg(NEURAL)) == "NeuMF-Pretrained"
         and neural_spread(), ["S"]),
        ("content/C4.tex", "Mọi mô hình có học đều vượt xa Random", "mọi mô hình có học ≥ 5 lần Random",
         lambda: min(d.ndcg(LEARNED).values()) >= 5 * S.loc["Random", "NDCG@10_mean"], ["S"]),
        ("content/C4.tex", "BPR-MF vẫn có trung bình cao nhất", "@20: BPR-MF cao nhất trong 7 mô hình chính; "
         "Most Popular và MLP > NeuMF-Pretrained",
         lambda: argmax({m: K20.loc[m, "NDCG@20_mean"] for m in MAIN}) == "BPR-MF"
         and K20.loc["MostPopular", "NDCG@20_mean"] > K20.loc["NeuMF-Pretrained", "NDCG@20_mean"]
         and K20.loc["MLP", "NDCG@20_mean"] > K20.loc["NeuMF-Pretrained", "NDCG@20_mean"], ["K20"]),
        ("content/C4.tex", "mọi khoảng tin cậy đều chứa 0", "mọi CI chính chứa 0 và mọi p Holm ≥ 0,05",
         lambda: all((G["ci_low"] <= 0) & (G["ci_high"] >= 0) & (G["p_holm"] >= 0.05)), ["G"]),
        ("content/C4.tex", "So sánh gần ngưỡng nhất là NeuMF-Pretrained với GMF",
         "p Wilcoxon nhỏ nhất ở (NeuMF-Pretrained, GMF), < 0,05 trước hiệu chỉnh, CI chứa 0",
         lambda: G["p_wilcoxon"].idxmin() == ("NeuMF-Pretrained", "GMF")
         and G.loc[("NeuMF-Pretrained", "GMF"), "p_wilcoxon"] < 0.05
         and G.loc[("NeuMF-Pretrained", "GMF"), "ci_low"] <= 0, ["G"]),
        ("content/C4.tex", "NeuMF không vượt BPR-MF, không vượt Most Popular",
         "mọi so sánh chính không có ý nghĩa", lambda: d.not_sig(*main_pairs), ["G"]),
        ("content/C4.tex", "dưới cả BPR-MF, NeuMF-Pretrained, MLP và Most Popular",
         "4 mô hình xếp trên NeuMF-Scratch đúng là BPR-MF, NeuMF-Pretrained, MLP, Most Popular",
         lambda: {m for m in MAIN if S.loc[m, "NDCG@10_mean"] > S.loc["NeuMF-Scratch", "NDCG@10_mean"]}
         == {"BPR-MF", "NeuMF-Pretrained", "MLP", "MostPopular"}, ["S"]),
        ("content/C4.tex", "cả bốn so sánh đều không có ý nghĩa thống kê", "NeuMF vs GMF/MLP không có ý nghĩa",
         lambda: d.not_sig(("NeuMF-Pretrained", "GMF"), ("NeuMF-Pretrained", "MLP"), ("NeuMF-Scratch", "GMF"),
                           ("NeuMF-Scratch", "MLP")), ["G"]),
        ("content/C4.tex", "trên validation thì ngược lại", "NeuMF-Pretrained vs NeuMF-Scratch không có ý nghĩa",
         lambda: d.not_sig(("NeuMF-Pretrained", "NeuMF-Scratch")), ["G"]),
        ("content/C4.tex", "mọi mô hình đạt NDCG@10 khoảng 0,03", "NDCG@10 nhóm head của mọi mô hình trong [0,02; 0,04]",
         lambda: all(0.02 <= ST[(m, "head")] <= 0.04 for m in SECONDARY), ["ST"]),
        ("content/C4.tex", "không mô hình nào vượt quá 0,0003", "tail: max < 0,0003; GMF, MLP, Most Popular = 0; "
         "cao nhất NeuMF-Scratch",
         lambda: max(ST[(m, "tail")] for m in SECONDARY) < 0.0003
         and all(ST[(m, "tail")] == 0 for m in ("GMF", "MLP", "MostPopular"))
         and argmax({m: ST[(m, "tail")] for m in SECONDARY}) == "NeuMF-Scratch", ["ST"]),
        ("content/C4.tex", "cao nhất trong mọi mô hình và cao hơn chính nó ở nhóm warm",
         "Most Popular cao nhất ở nhóm cold và cold > warm",
         lambda: argmax({m: ST[(m, "cold")] for m in SECONDARY}) == "MostPopular"
         and ST[("MostPopular", "cold")] > ST[("MostPopular", "warm")], ["ST"]),
        ("content/C4.tex", "chỉ BPR-MF và NeuMF-Scratch thấp hơn ở nhóm cold",
         "đúng BPR-MF và NeuMF-Scratch có cold < warm",
         lambda: {m for m in SECONDARY if ST[(m, "cold")] < ST[(m, "warm")]} == {"BPR-MF", "NeuMF-Scratch"}, ["ST"]),
        ("content/C4.tex", "NeuMF-Scratch đa dạng nhất", "NeuMF-Scratch: coverage và novelty cao nhất, HRR thấp nhất",
         lambda: B["coverage"].idxmax() == "NeuMF-Scratch" and B["novelty"].idxmax() == "NeuMF-Scratch"
         and B["HRR"].idxmin() == "NeuMF-Scratch", ["B"]),
        ("content/C4.tex", "MLP gần như chỉ gợi ý sản phẩm phổ biến",
         "MLP: coverage thấp nhất trong các mô hình cá nhân hoá, HRR ≥ 99%",
         lambda: B.drop("MostPopular")["coverage"].idxmin() == "MLP" and B.loc["MLP", "HRR"] >= 0.99, ["B"]),
        ("content/C4.tex", "NeuMF-Pretrained và GMF cũng có HRR trên 98", "HRR của NeuMF-Pretrained và GMF > 98%",
         lambda: B.loc["NeuMF-Pretrained", "HRR"] > 0.98 and B.loc["GMF", "HRR"] > 0.98, ["B"]),
        ("content/C4.tex", "vừa đa dạng thứ hai", "BPR-MF: coverage cao thứ hai, HRR thấp thứ hai",
         lambda: list(B["coverage"].sort_values(ascending=False).index[:2]) == ["NeuMF-Scratch", "BPR-MF"]
         and list(B["HRR"].sort_values().index[:2]) == ["NeuMF-Scratch", "BPR-MF"], ["B"]),
        ("content/C4.tex", "Most Popular chỉ xếp thứ tư theo Full Ranking nhưng đứng đầu theo Sampled-99",
         "Most Popular hạng 4/6 theo Full Ranking, hạng 1 theo Sampled-99",
         lambda: d.rank("MostPopular", SECONDARY) == 4 and SP["NDCG@10"].idxmax() == "MostPopular", ["S", "SP"]),
        ("content/C4.tex", "chỉ sau 1--9 epoch", "best_epoch của mô hình nơ-ron trong 11_final nằm trong 1–9",
         lambda: d.epochs and min(d.epochs) >= 1 and max(d.epochs) <= 9, ["S"]),
        ("content/C5.tex", "BPR-MF đạt NDCG@10 trung bình cao nhất", "BPR-MF cao nhất NDCG@10",
         lambda: argmax(d.ndcg()) == "BPR-MF", ["S"]),
        ("content/C5.tex", "pre-training không mang lại lợi ích đo được", "NeuMF-Pretrained vs Scratch không có ý nghĩa",
         lambda: d.not_sig(("NeuMF-Pretrained", "NeuMF-Scratch")), ["G"]),
        ("content/C5.tex", "đạt đỉnh sau 1--9 epoch", "best_epoch trong 1–9",
         lambda: d.epochs and min(d.epochs) >= 1 and max(d.epochs) <= 9, ["S"]),
        ("content/C5.tex", "cùng cỡ với chênh lệch giữa các mô hình", "khoảng cách giữa 4 mô hình nơ-ron ≤ độ lệch chuẩn",
         neural_spread, ["S"]),
        ("frontmatter/abstract.tex", "BPR-MF đạt NDCG@10 trung bình cao nhất", "BPR-MF cao nhất NDCG@10",
         lambda: argmax(d.ndcg()) == "BPR-MF", ["S"]),
        ("frontmatter/abstract.tex", "ngang Most Popular", "NeuMF-Pretrained vs Most Popular không có ý nghĩa",
         lambda: d.not_sig(("NeuMF-Pretrained", "MostPopular")), ["G"]),
        ("frontmatter/abstract.tex", "Không so sánh nào trong", "0 so sánh chính đạt tiêu chí",
         lambda: d.not_sig(*main_pairs), ["G"]),
        ("frontmatter/abstract_english.tex", "tuned BPR-MF has the highest mean NDCG@10", "BPR-MF cao nhất NDCG@10",
         lambda: argmax(d.ndcg()) == "BPR-MF", ["S"]),
        ("frontmatter/abstract_english.tex", "scores lower still", "NeuMF-Scratch < NeuMF-Pretrained và < Most Popular",
         lambda: S.loc["NeuMF-Scratch", "NDCG@10_mean"] < min(S.loc["NeuMF-Pretrained", "NDCG@10_mean"],
                                                                S.loc["MostPopular", "NDCG@10_mean"]), ["S"]),
        ("frontmatter/abstract_english.tex", "None of the pre-registered comparisons reaches significance",
         "0 so sánh chính đạt tiêu chí", lambda: d.not_sig(*main_pairs), ["G"]),
        ("content/C1.tex", "Kết quả (không vượt)", "NeuMF không tốt hơn có ý nghĩa BPR-MF, GMF, MLP",
         lambda: d.not_sig(*[p for p in main_pairs if p[1] in ("BPR-MF", "GMF", "MLP")]), ["G"]),
    ]


def find_line(rel: str, anchor: str) -> int | None:
    path = REPORT / rel
    if not path.exists():
        return None
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if anchor in line:
            return i
    return None


def check_claims(d: Data) -> tuple[int, int]:
    print("\n2. Khẳng định bằng chữ trong báo cáo")
    bad = 0
    for rel, anchor, desc, pred, needs in claims(d):
        if any(getattr(d, n) is None for n in needs):
            print(f"   [BỎ QUA] {desc} — chưa có dữ liệu ({', '.join(needs)})")
            continue
        line = find_line(rel, anchor)
        where = f"{rel}:{line}" if line else f"{rel} (không còn câu chứa '{anchor}')"
        try:
            ok = bool(pred())
        except (KeyError, ValueError) as exc:
            ok, desc = False, f"{desc} [lỗi đọc dữ liệu: {exc}]"
        if line is None:
            print(f"   [CHÚ Ý] {where}: câu đã đổi — cập nhật danh sách khẳng định trong 19_check_report.py")
        if not ok:
            bad += 1
            print(f"   [SAI]    {where}: {desc} — sửa câu này theo số mới")
    total = len(claims(d))
    print(f"   {total - bad}/{total} khẳng định còn đúng." if not bad else f"   => {bad} khẳng định cần sửa.")
    return bad, total


# ------------------------------------------------------------- tái lập
def compare_with_committed() -> dict[str, float]:
    print("1. Tái lập: so với bản đã commit (git HEAD)")
    out = {}
    for name, key in (("summary.csv", ["model"]), ("significance.csv", ["A", "B"]),
                      ("stratified.csv", ["model", "seed", "subset"]), ("beyond_accuracy.csv", ["model", "seed"]),
                      ("sampled99.csv", ["model", "seed"])):
        new, old = read_csv(name), read_csv(name, committed=True)
        if new is None or old is None:
            print(f"   {name}: {'chưa có file mới' if new is None else 'chưa có bản commit'} — bỏ qua")
            continue
        if new.columns[0].startswith("Unnamed"):
            new, old = new.rename(columns={new.columns[0]: "model"}), old.rename(columns={old.columns[0]: "model"})
        num = [c for c in new.columns if c not in key and pd.api.types.is_numeric_dtype(new[c])]
        m = new.merge(old, on=key, suffixes=("", "_old"), how="outer", indicator=True)
        if (m["_merge"] != "both").any():
            print(f"   {name}: tập dòng khác bản commit ({int((m['_merge'] != 'both').sum())} dòng lệch)")
            out[name] = float("inf")
            continue
        gap = max((m[c] - m[f"{c}_old"]).abs().max() for c in num) if num else 0.0
        out[name] = float(gap)
        print(f"   {name}: lệch tuyệt đối lớn nhất {gap:.3g}" + ("  (trùng khớp)" if gap == 0 else ""))
    return out


# ------------------------------------------------------- số chép tay
def vn(x: float, nd: int) -> str:
    return f"{x:.{nd}f}".replace(".", ",")


def key_numbers(S, G, ST) -> dict[str, str]:
    """Các con số hay được chép tay vào tài liệu, định dạng như trong tài liệu."""
    out = {}
    if S is not None:
        for m in S.index:
            out[f"{m} NDCG@10"] = vn(S.loc[m, "NDCG@10_mean"], 5)
            out[f"{m} HR@10 (%)"] = vn(100 * S.loc[m, "HR@10_mean"], 2) + "%"
    if G is not None:
        for (a, b), r in G.iterrows():
            out[f"{a} vs {b} p Holm"] = vn(r["p_holm"], 3)
            out[f"{a} vs {b} chênh"] = ("+" if r["rel_diff"] >= 0 else "−") + vn(abs(100 * r["rel_diff"]), 1) + "%"
    if ST is not None and ("MostPopular", "cold") in ST.index:
        out["Most Popular nhóm cold"] = vn(ST[("MostPopular", "cold")], 5)
    return out


def stale_doc_numbers() -> int:
    print("\n3. Số chép tay trong tài liệu")
    def load(committed):
        S = read_csv("summary.csv", committed, index_col=0)
        g = read_csv("significance.csv", committed)
        st = read_csv("stratified.csv", committed)
        return key_numbers(S, None if g is None else g.set_index(["A", "B"]),
                           None if st is None else st.groupby(["model", "subset"])["NDCG@10"].mean())
    new, old = load(False), load(True)
    changed = {k: (old[k], new[k]) for k in new if k in old and old[k] != new[k]}
    if not changed:
        print("   Số liệu chính không đổi so với bản đã commit — không cần sửa số chép tay.")
        return 0
    hits = 0
    for label, (o, n) in changed.items():
        print(f"   {label}: {o} → {n}")
        for doc in DOCS:
            if not doc.exists():
                continue
            for i, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), start=1):
                if o in line:
                    hits += 1
                    print(f"      {doc.relative_to(REPO_ROOT).as_posix()}:{i}")
    return hits


# ------------------------------------------------- macro và bảng của báo cáo
MACRO_RE = re.compile(r"\\(Res|Sd|Sig|Strat|Beyond|Samp|Lat|Val|Kx|Ext|Esig)\{([^{}]*)\}\{([^{}]*)\}")


def check_macros_and_tables() -> int:
    print("\n4. Macro và bảng mà báo cáo dùng")
    macros_file = TABLES / "results_macros.tex"
    defined = set(re.findall(r"\\csname ([^\\]+)\\endcsname", macros_file.read_text(encoding="utf-8"))) \
        if macros_file.exists() else set()
    missing_m, missing_t = set(), set()
    for tex in [*REPORT.glob("content/*.tex"), *REPORT.glob("frontmatter/*.tex")]:
        text = tex.read_text(encoding="utf-8")
        for fam, a, b in MACRO_RE.findall(text):
            if f"{fam.lower()}-{a}-{b}" not in defined:
                missing_m.add(f"\\{fam}{{{a}}}{{{b}}} ({tex.name})")
        for t in re.findall(r"\\bangketqua\{([^}]+)\}", text):
            if not (TABLES / t).exists():
                missing_t.add(f"{t} ({tex.name})")
    for x in sorted(missing_m):
        print(f"   [THIẾU MACRO] {x} — PDF hiện [chưa có]")
    for x in sorted(missing_t):
        print(f"   [THIẾU BẢNG]  {x} — PDF hiện khung 'Chưa có số liệu'")
    if not missing_m and not missing_t:
        print("   Đủ mọi macro và bảng.")
    return len(missing_m) + len(missing_t)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    d = Data()
    if d.S is None:
        raise SystemExit("Chưa có outputs/final/summary.csv — chạy 11_final.py và 12_significance.py trước.")
    compare_with_committed()
    bad, _ = check_claims(d)
    stale = stale_doc_numbers()
    missing = check_macros_and_tables()
    print("\nTóm tắt: " + ("mọi thứ khớp." if not (bad or stale or missing) else
                         f"{bad} khẳng định sai, {stale} dòng tài liệu ghi số cũ, {missing} macro/bảng thiếu."))
    print("Sau khi sửa: biên dịch lại báo cáo (Report DACNTT/compile.bat) rồi commit.")
    if args.strict and (bad or missing):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
