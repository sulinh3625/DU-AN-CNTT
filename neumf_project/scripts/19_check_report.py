"""Đối chiếu báo cáo và tài liệu với số liệu hiện có — chạy sau scripts/24_report_v2.py; không chấm test.

    python scripts/19_check_report.py            # in kết quả, luôn trả mã 0
    python scripts/19_check_report.py --strict   # trả mã 1 nếu có khẳng định sai / macro, bảng, hình thiếu

Bốn phần:
  1. Tái lập: outputs/v2/final/{summary,significance,groups,ablation,beyond}.csv so với bản đã commit (git HEAD) — độ
     lệch tuyệt đối lớn nhất (chạy lại đánh giá cuối trên cùng máy kỳ vọng lệch 0).
  2. Khẳng định bằng chữ trong báo cáo mà macro số liệu không tự cập nhật — mỗi khẳng định là một điều kiện trên CSV;
     sai thì in tệp:dòng cần sửa. Gồm khẳng định về kết quả giao thức v2 (outputs/v2/final/) và về lịch sử phát triển
     giao thức v1 (outputs/final/, không còn thay đổi).
  3. Số chép tay trong van_dap.md, pham_vi_du_an.md, README.md, notebook: nếu số v2 khác bản đã commit, liệt kê các dòng
     còn ghi số cũ.
  4. Mọi macro (\\VRes, \\VSig, ... của v2; \\Res, \\Sig, ... của v1), mọi bảng \\bangketqua / \\bangketquaV và hình
     \\hinhketqua mà báo cáo dùng đều đã được sinh (nếu không, PDF hiện "[chưa có]" / khung "Chưa có số liệu").
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
FINAL = PROJECT_ROOT / "outputs" / "final"           # giao thức v1 (lịch sử phát triển)
FINAL_V2 = PROJECT_ROOT / "outputs" / "v2" / "final"  # giao thức v2 (kết quả chính)
REPORT = REPO_ROOT / "Report DACNTT"
TABLES = REPORT / "content" / "tables"
NOT_SIG = "không khác biệt có ý nghĩa"
# v1
MAIN = ["NeuMF-Pretrained", "NeuMF-Scratch", "GMF", "MLP", "BPR-MF", "MostPopular", "Random"]
NEURAL = ["NeuMF-Pretrained", "NeuMF-Scratch", "GMF", "MLP"]
SECONDARY = ["NeuMF-Pretrained", "NeuMF-Scratch", "GMF", "MLP", "BPR-MF", "MostPopular"]
# v2 (mã mô hình của scripts/v2_common.py)
ID_ONLY = ["popularity", "itemknn", "userknn", "bpr", "gmf", "mlp", "neumf", "recent_pop"]
PERSONALIZED = ["neumf_f", "late_f", "gmf_f", "mlp_f", "neumf", "gmf", "mlp", "bpr", "itemknn", "userknn", "content"]
DOCS = [REPO_ROOT / "van_dap.md", PROJECT_ROOT / "pham_vi_du_an.md", PROJECT_ROOT / "README.md",
        REPO_ROOT / "README.md", PROJECT_ROOT / "notebooks" / "colab_final.ipynb"]
V2_FILES = (("summary.csv", ["model"]), ("significance.csv", ["A", "B"]),
            ("ablation.csv", ["variant"]), ("beyond.csv", ["model"]))


# ---------------------------------------------------------------- dữ liệu
def read_csv(name: str, committed: bool = False, root: Path = FINAL, **kw) -> pd.DataFrame | None:
    if not committed:
        path = root / name
        if not path.exists():
            return None
        try:
            return pd.read_csv(path, **kw)
        except pd.errors.EmptyDataError:
            return None
    rel = (root / name).relative_to(PROJECT_ROOT).as_posix()
    res = subprocess.run(["git", "show", f"HEAD:./{rel}"], cwd=PROJECT_ROOT, capture_output=True)
    return pd.read_csv(io.BytesIO(res.stdout), **kw) if res.returncode == 0 and res.stdout.strip() else None


class Data:
    def __init__(self):
        # v1 — lịch sử phát triển
        self.S = read_csv("summary.csv", index_col=0)
        g = read_csv("significance.csv")
        self.G = None if g is None else g.set_index(["A", "B"])
        st = read_csv("stratified.csv")
        self.ST = None if st is None else st.groupby(["model", "subset"])["NDCG@10"].mean()
        sp = read_csv("sampled99.csv")
        self.SP = None if sp is None else sp.groupby("model").mean(numeric_only=True)
        # v2 — kết quả chính
        s2 = read_csv("summary.csv", root=FINAL_V2)
        self.S2 = None if s2 is None else s2.set_index("model")
        g2 = read_csv("significance.csv", root=FINAL_V2)
        self.G2 = None if g2 is None or g2.empty else g2.set_index(["A", "B"])
        b2 = read_csv("beyond.csv", root=FINAL_V2)
        self.B2 = None if b2 is None else b2.set_index("model")
        info = FINAL_V2 / "data.json"
        self.info2 = json.loads(info.read_text(encoding="utf-8")) if info.exists() else None

    def ndcg(self, models=MAIN) -> dict:
        return {m: self.S.loc[m, "NDCG@10_mean"] for m in models}

    def not_sig(self, *pairs) -> bool:
        return all(self.G.loc[p, "verdict"] == NOT_SIG for p in pairs)


def argmax(d: dict):
    return max(d, key=d.get)


def curves(H: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Phase chọn epoch của từng mạng nơ-ron trong history.csv."""
    sel = H[H["phase"] == "select"]
    return {m: g.sort_values("epoch") for m, g in sel.groupby("model")}


def stopped_early(H: pd.DataFrame) -> bool:
    """Mỗi mô hình: epoch tốt nhất (NDCG@10 val cao nhất) nằm trước epoch cuối của bước chọn — tức đã dừng sớm."""
    return all(int(g.loc[g["NDCG@10"].idxmax(), "epoch"]) < int(g["epoch"].max()) for g in curves(H).values())


def loss_keeps_falling(H: pd.DataFrame) -> bool:
    """Mỗi mô hình: loss huấn luyện ở epoch cuối thấp hơn ở epoch tốt nhất (vẫn giảm sau đỉnh NDCG@10 val)."""
    return all(float(g["loss"].iloc[-1]) < float(g.loc[g["NDCG@10"].idxmax(), "loss"]) for g in curves(H).values())


# ---------------------------------------------------------- khẳng định
# (tệp, đoạn văn bản neo để tìm dòng, mô tả, điều kiện, các nguồn dữ liệu cần có)
def claims(d: Data):
    S, G, ST, SP, S2, B2, info = d.S, d.G, d.ST, d.SP, d.S2, d.B2, d.info2
    main_pairs = list(G.index) if G is not None else []
    id_new_zero = lambda: all(S2.loc[m, "NDCG@10_new_mean"] == 0 for m in ID_ONLY if m in S2.index)  # noqa: E731
    v1_no_neumf_win = lambda: (all(G.loc[p, "verdict"] != "A tốt hơn"  # noqa: E731
                                   for p in (("NeuMF-Pretrained", "BPR-MF"), ("NeuMF-Scratch", "BPR-MF")))
                               and argmax(d.ndcg()) == "BPR-MF")
    return [
        # ---- giao thức v2 (kết quả chính)
        ("content/C4.tex", "các mô hình chỉ dùng ID đạt NDCG@10 bằng 0 theo cấu tạo",
         "v2: mọi mô hình chỉ dùng ID có NDCG@10 = 0 trên sản phẩm mới", id_new_zero, ["S2"]),
        ("frontmatter/abstract.tex", "trong khi mọi mô hình chỉ dùng ID bằng 0 theo cấu tạo",
         "v2: mọi mô hình chỉ dùng ID có NDCG@10 = 0 trên sản phẩm mới", id_new_zero, ["S2"]),
        ("frontmatter/abstract_english.tex", "whereas every ID-only model scores zero by construction",
         "v2: mọi mô hình chỉ dùng ID có NDCG@10 = 0 trên sản phẩm mới", id_new_zero, ["S2"]),
        ("content/C4.tex", "Most Popular và MLP-F có độ phủ thấp nhất",
         "v2: Most Popular và MLP-F có độ phủ top-10 thấp nhất (so với các mô hình cá nhân hoá)",
         lambda: set(B2.loc[[m for m in ["popularity", *PERSONALIZED] if m in B2.index], "coverage10"]
                     .nsmallest(2).index) == {"popularity", "mlp_f"}, ["B2"]),
        ("content/C4.tex", "Thang giá trị tuyệt đối thấp", "v2: NDCG@10 cao nhất < 0,05",
         lambda: S2["NDCG@10_mean"].max() < 0.05, ["S2"]),
        ("content/C4.tex", "mỗi khách có vài sản phẩm đúng giữa khoảng",
         "v2: trung bình số sản phẩm đúng mỗi khách < 10",
         lambda: info["test"]["targets"] / info["test"]["users"] < 10, ["info2"]),
        # ---- giao thức v1 (lịch sử phát triển, mục Lịch sử phát triển của Chương 4)
        ("content/C4.tex", "BPR-MF có NDCG@10 trung bình cao nhất", "BPR-MF cao nhất NDCG@10",
         lambda: argmax(d.ndcg()) == "BPR-MF", ["S"]),
        ("content/C4.tex", "đăng ký trước đạt tiêu chí", "v1: mọi so sánh chính không có ý nghĩa",
         lambda: d.not_sig(*main_pairs), ["G"]),
        ("content/C4.tex", "Tiền huấn luyện không mang lại lợi ích đo được",
         "v1: NeuMF-Pretrained vs NeuMF-Scratch không có ý nghĩa",
         lambda: d.not_sig(("NeuMF-Pretrained", "NeuMF-Scratch")), ["G"]),
        ("content/C4.tex", "Gần như toàn bộ độ chính xác đến từ nhóm sản phẩm phổ biến nhất",
         "v1: NDCG@10 nhóm head trong [0,02; 0,04], nhóm tail < 0,0003",
         lambda: all(0.02 <= ST[(m, "head")] <= 0.04 for m in SECONDARY)
         and max(ST[(m, "tail")] for m in SECONDARY) < 0.0003, ["ST"]),
        ("content/C4.tex", "Most Popular đứng đầu", "v1: Most Popular cao nhất theo Sampled-99",
         lambda: SP["NDCG@10"].idxmax() == "MostPopular", ["SP"]),
        ("content/C1.tex", "NeuMF chỉ dùng mã ID không vượt được MF được tinh chỉnh tốt",
         "v1: BPR-MF cao nhất và không biến thể NeuMF nào tốt hơn có ý nghĩa BPR-MF", v1_no_neumf_win, ["S", "G"]),
        ("frontmatter/abstract.tex", "NeuMF không vượt MF đã tinh chỉnh",
         "v1: BPR-MF cao nhất và không biến thể NeuMF nào tốt hơn có ý nghĩa BPR-MF", v1_no_neumf_win, ["S", "G"]),
        ("frontmatter/abstract_english.tex", "NeuMF did not outperform a tuned MF baseline",
         "v1: BPR-MF cao nhất và không biến thể NeuMF nào tốt hơn có ý nghĩa BPR-MF", v1_no_neumf_win, ["S", "G"]),
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
    print(f"   {total - bad}/{total} khẳng định còn đúng (hoặc chưa có dữ liệu)." if not bad
          else f"   => {bad} khẳng định cần sửa.")
    return bad, total


# ------------------------------------------------------------- tái lập
def compare_with_committed() -> dict[str, float]:
    print("1. Tái lập (giao thức v2): so với bản đã commit (git HEAD)")
    out = {}
    for name, key in V2_FILES:
        new, old = read_csv(name, root=FINAL_V2), read_csv(name, committed=True, root=FINAL_V2)
        if new is None or old is None:
            print(f"   {name}: {'chưa có file mới' if new is None else 'chưa có bản commit'} — bỏ qua")
            continue
        num = [c for c in new.columns if c not in key and pd.api.types.is_numeric_dtype(new[c])]
        m = new.merge(old, on=key, suffixes=("", "_old"), how="outer", indicator=True)
        if (m["_merge"] != "both").any():
            print(f"   {name}: tập dòng khác bản commit ({int((m['_merge'] != 'both').sum())} dòng lệch)")
            out[name] = float("inf")
            continue
        gap = max(((m[c] - m[f"{c}_old"]).abs().max() for c in num if f"{c}_old" in m), default=0.0)
        out[name] = float(gap)
        print(f"   {name}: lệch tuyệt đối lớn nhất {gap:.3g}" + ("  (trùng khớp)" if gap == 0 else ""))
    return out


# ------------------------------------------------------- số chép tay
def vn(x: float, nd: int) -> str:
    return f"{x:.{nd}f}".replace(".", ",")


def key_numbers(S2, G2) -> dict[str, str]:
    """Các con số v2 hay được chép tay vào tài liệu, định dạng như trong tài liệu."""
    out = {}
    if S2 is not None:
        for m in S2.index:
            out[f"{m} NDCG@10"] = vn(S2.loc[m, "NDCG@10_mean"], 5)
    if G2 is not None:
        for (a, b), r in G2.iterrows():
            out[f"{a} vs {b} p Holm"] = vn(r["p_holm"], 3)
            out[f"{a} vs {b} chênh"] = ("+" if r["rel_diff"] >= 0 else "−") + vn(abs(100 * r["rel_diff"]), 1) + "%"
    return out


def stale_doc_numbers() -> int:
    print("\n3. Số chép tay trong tài liệu (giao thức v2)")

    def load(committed):
        s = read_csv("summary.csv", committed, root=FINAL_V2)
        g = read_csv("significance.csv", committed, root=FINAL_V2)
        return key_numbers(None if s is None else s.set_index("model"),
                           None if g is None or g.empty else g.set_index(["A", "B"]))
    new, old = load(False), load(True)
    changed = {k: (old[k], new[k]) for k in new if k in old and old[k] != new[k]}
    if not changed:
        print("   Số liệu chính không đổi so với bản đã commit (hoặc chưa có bản commit) — không cần sửa số chép tay.")
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
MACRO_RE = re.compile(r"\\(Res|Sd|Sig|Strat|Beyond|Samp|Lat|Val|Kx|Ext|Esig|Abl|VRes|VSd|VOnly|VVal|VRank|VSig|"
                      r"VGrp|VAbl|VBey|VData|VCfg)\{([^{}]*)\}\{([^{}]*)\}")


def defined_macros() -> set[str]:
    out = set()
    for f in (TABLES / "results_macros.tex", TABLES / "v2" / "results_v2_macros.tex"):
        if f.exists():
            out |= set(re.findall(r"\\csname ([^\\]+)\\endcsname", f.read_text(encoding="utf-8")))
    return out


def check_macros_and_tables() -> int:
    print("\n4. Macro, bảng và hình mà báo cáo dùng")
    defined = defined_macros()
    missing_m, missing_t, missing_f = set(), set(), set()
    for tex in [*REPORT.glob("content/*.tex"), *REPORT.glob("frontmatter/*.tex")]:
        text = tex.read_text(encoding="utf-8")
        for fam, a, b in MACRO_RE.findall(text):
            if f"{fam.lower()}-{a}-{b}" not in defined:
                missing_m.add(f"\\{fam}{{{a}}}{{{b}}} ({tex.name})")
        for t in re.findall(r"\\bangketqua\{([^}]+)\}", text):
            if not (TABLES / t).exists():
                missing_t.add(f"{t} ({tex.name})")
        for t in re.findall(r"\\bangketquaV\{([^}]+)\}", text):
            if not (TABLES / "v2" / t).exists():
                missing_t.add(f"v2/{t} ({tex.name})")
        for f in re.findall(r"\\hinhketqua\{([^}]+)\}", text):
            if not (REPORT / f).exists():
                missing_f.add(f"{f} ({tex.name})")
    for x in sorted(missing_m):
        print(f"   [THIẾU MACRO] {x} — PDF hiện [chưa có]")
    for x in sorted(missing_t):
        print(f"   [THIẾU BẢNG]  {x} — PDF hiện khung 'Chưa có số liệu'")
    for x in sorted(missing_f):
        print(f"   [THIẾU HÌNH]  {x} — PDF hiện khung 'Chưa có số liệu'")
    if not missing_m and not missing_t and not missing_f:
        print("   Đủ mọi macro, bảng và hình.")
    return len(missing_m) + len(missing_t) + len(missing_f)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    d = Data()
    compare_with_committed()
    bad, _ = check_claims(d)
    stale = stale_doc_numbers()
    missing = check_macros_and_tables()
    print("\nTóm tắt: " + ("mọi thứ khớp." if not (bad or stale or missing) else
                         f"{bad} khẳng định sai, {stale} dòng tài liệu ghi số cũ, {missing} macro/bảng/hình thiếu."))
    print("Sau khi sửa: biên dịch lại báo cáo (Report DACNTT/compile.bat) rồi commit.")
    if args.strict and (bad or missing):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
