"""Đối chiếu báo cáo và tài liệu với số liệu hiện có — chạy sau scripts/24_report_v2.py; không chấm test.

    python scripts/19_check_report.py            # in kết quả, luôn trả mã 0
    python scripts/19_check_report.py --strict   # trả mã 1 nếu có khẳng định sai / macro, bảng, hình thiếu

Bốn phần:
  1. Tái lập: outputs/v2/final/{summary,significance,ablation,beyond}.csv so với bản đã commit (git HEAD) — độ
     lệch tuyệt đối lớn nhất (chạy lại đánh giá cuối trên cùng máy kỳ vọng lệch 0).
  2. Khẳng định bằng chữ trong báo cáo mà macro số liệu không tự cập nhật — mỗi khẳng định là một điều kiện trên CSV
     của outputs/v2/final/ (hoặc audit/v2/best_configs.json); sai thì in tệp:dòng cần sửa.
  3. Số chép tay trong van_dap.md, pham_vi_du_an.md, README.md: nếu số v2 khác bản đã commit, liệt kê các dòng còn ghi
     số cũ.
  4. Mọi macro (\\VRes, \\VSig, ... của v2; \\Res, \\Sig của lịch sử v1), mọi bảng \\bangketquaV và hình \\hinhketqua
     mà báo cáo dùng đều đã được sinh (nếu không, PDF hiện "[chưa có]" / khung "Chưa có số liệu").
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
FINAL_V2 = PROJECT_ROOT / "outputs" / "v2" / "final"
REPORT = REPO_ROOT / "Report DACNTT"
TABLES = REPORT / "content" / "tables"
BEST = PROJECT_ROOT / "audit" / "v2" / "best_configs.json"
# mã mô hình của scripts/v2_common.py
FEAT = {"late_f", "neumf_f", "gmf_f", "mlp_f"}  # mô hình có đặc trưng
NEURAL = ["neumf_f", "late_f", "gmf_f", "mlp_f", "neumf", "gmf", "mlp"]
BASELINES = ["popularity", "recent_pop", "content", "itemknn", "userknn", "bpr"]
COMPARED_BASELINES = ["bpr", "itemknn", "userknn", "recent_pop", "content"]  # so sánh 5–9 của họ đăng ký trước
NOT_SIG, BETTER = "không khác biệt có ý nghĩa", "A tốt hơn"
DOCS = [REPO_ROOT / "van_dap.md", PROJECT_ROOT / "pham_vi_du_an.md", PROJECT_ROOT / "README.md",
        REPO_ROOT / "README.md"]
V2_FILES = (("summary.csv", ["model"]), ("significance.csv", ["A", "B"]),
            ("ablation.csv", ["variant"]), ("beyond.csv", ["model"]))


# ---------------------------------------------------------------- dữ liệu
def read_csv(name: str, committed: bool = False, root: Path = FINAL_V2, **kw) -> pd.DataFrame | None:
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
        s2 = read_csv("summary.csv")
        self.S2 = None if s2 is None else s2.set_index("model")
        g2 = read_csv("significance.csv")
        self.G2 = None if g2 is None or g2.empty else g2.set_index(["A", "B"])
        b2 = read_csv("beyond.csv")
        self.B2 = None if b2 is None else b2.set_index("model")
        a2 = read_csv("ablation.csv")
        self.A2 = None if a2 is None or a2.empty else a2.set_index("variant")
        info = FINAL_V2 / "data.json"
        self.info2 = json.loads(info.read_text(encoding="utf-8")) if info.exists() else None
        self.best = json.loads(BEST.read_text(encoding="utf-8")) if BEST.exists() else None


def order(s: pd.Series) -> list:
    """Mã mô hình xếp theo giá trị giảm dần."""
    return list(s.sort_values(ascending=False).index)


# ---------------------------------------------------------- khẳng định
# (tệp, đoạn văn bản neo để tìm dòng, mô tả, điều kiện, các nguồn dữ liệu cần có)
def claims(d: Data):
    S2, G2, B2, A2, info, best = d.S2, d.G2, d.B2, d.A2, d.info2, d.best
    test = lambda: order(S2["NDCG@10_mean"].drop("random", errors="ignore"))  # noqa: E731
    val = lambda: order(S2["val_NDCG@10"].dropna())  # noqa: E731  mô hình có tinh chỉnh (không có Random)
    verdict = lambda a, b: G2.loc[(a, b), "verdict"]  # noqa: E731
    rel = lambda a, b: abs(G2.loc[(a, b), "rel_diff"])  # noqa: E731
    abl = lambda: A2["rel"].drop("neumf_f").sort_values()  # noqa: E731  thay đổi khi tắt từng thành phần, tăng dần
    cov = lambda: B2["coverage10"]  # noqa: E731
    personal = lambda: cov().drop(["random", "popularity", "recent_pop"])  # noqa: E731

    def rank_shift():
        """(hạng lúc tinh chỉnh, hạng ở đánh giá cuối) của từng mô hình có tinh chỉnh."""
        v = val()
        t = [m for m in test() if m in v]
        return {m: (v.index(m) + 1, t.index(m) + 1) for m in v}

    top_late_neumf = lambda: test()[:2] == ["late_f", "neumf_f"]  # noqa: E731
    fusion = lambda: (verdict("neumf_f", "mlp_f") == BETTER and verdict("neumf_f", "gmf_f") == NOT_SIG  # noqa: E731
                      and verdict("neumf_f", "late_f") == NOT_SIG)
    not_gmf_late = lambda: verdict("neumf_f", "gmf_f") == NOT_SIG == verdict("neumf_f", "late_f")  # noqa: E731
    time_most = lambda: abl().index[0] == "neumf_f-time"  # noqa: E731
    rho0 = lambda: best["neumf_f"]["params"].get("id_dropout") == 0  # noqa: E731
    return [
        # ---- C4: kết quả
        ("content/C4.tex", "Thang giá trị tuyệt đối thấp", "v2: NDCG@10 cao nhất < 0,05",
         lambda: S2["NDCG@10_mean"].max() < 0.05, ["S2"]),
        ("content/C4.tex", "mỗi khách có vài sản phẩm đúng giữa khoảng",
         "v2: trung bình số sản phẩm đúng mỗi khách < 10",
         lambda: info["test"]["targets"] / info["test"]["users"] < 10, ["info2"]),
        ("content/C4.tex", "Trên tập xác thực của mẫu A, bốn mô hình có đặc trưng đứng đầu",
         "v2: 4 mô hình có đặc trưng đứng đầu NDCG@10 xác thực", lambda: set(val()[:4]) == FEAT, ["S2"]),
        ("content/C4.tex", "Trong các baseline, cao nhất là UserKNN",
         "v2: baseline cao nhất lúc tinh chỉnh: UserKNN, rồi BPR-MF, ItemKNN",
         lambda: [m for m in val() if m in BASELINES][:3] == ["userknn", "bpr", "itemknn"], ["S2"]),
        ("content/C4.tex", "LateFusion-F đạt NDCG@10 cao nhất", "v2: LateFusion-F cao nhất, NeuMF-F thứ hai",
         top_late_neumf, ["S2"]),
        ("content/C4.tex", "bốn mô hình có đặc trưng đứng đầu, như trên tập xác thực",
         "v2: 4 mô hình có đặc trưng đứng đầu NDCG@10 kiểm thử", lambda: set(test()[:4]) == FEAT, ["S2"]),
        ("content/C4.tex", "khoảng 15\\% số khách", "v2: HR@10 của NeuMF-F làm tròn 15%",
         lambda: round(100 * S2.loc["neumf_f", "HR@10_mean"]) == 15, ["S2"]),
        ("content/C4.tex", "trùng với chính NeuMF-F, vì cấu hình được chọn của NeuMF-F",
         "v2: cấu hình NeuMF-F đã chọn có id_dropout = 0", rho0, ["best"]),
        ("content/C4.tex", "vì vậy đóng góp nhiều nhất", "v2: ablation — bỏ đặc trưng thời gian giảm nhiều nhất",
         time_most, ["A2"]),
        ("content/C4.tex", "Khoảng tin cậy của hiệu khi bỏ thuộc tính sản phẩm hoặc vector văn bản chứa 0",
         "v2: ablation — khoảng tin cậy của bỏ thuộc tính, bỏ văn bản chứa 0",
         lambda: all(A2.loc[v, "ci_low"] < 0 < A2.loc[v, "ci_high"] for v in ("neumf_f-attr", "neumf_f-text")),
         ["A2"]),
        ("content/C4.tex", "tiếp theo là thông tin khách hàng",
         "v2: ablation — bỏ thông tin khách giảm nhiều thứ hai", lambda: abl().index[1] == "neumf_f-user", ["A2"]),
        ("content/C4.tex", "Most Popular và MostPopular-Recent có độ phủ thấp nhất",
         "v2: Most Popular, MostPopular-Recent có độ phủ top-10 thấp nhất",
         lambda: set(cov().nsmallest(2).index) == {"popularity", "recent_pop"}, ["B2"]),
        ("content/C4.tex", "MLP chỉ dùng ID có độ phủ thấp nhất",
         "v2: độ phủ — MLP thấp nhất trong mô hình cá nhân hoá; NeuMF-F cao nhất trong mạng nơ-ron, sau ItemKNN, Content",
         lambda: personal().idxmin() == "mlp" and cov()[NEURAL].idxmax() == "neumf_f"
         and order(personal())[:3] == ["content", "itemknn", "neumf_f"], ["B2"]),
        ("content/C4.tex", "LateFusion-F và NeuMF-F giữ hai vị trí đầu",
         "v2: LateFusion-F, NeuMF-F dẫn đầu cả lúc tinh chỉnh lẫn đánh giá cuối",
         lambda: val()[:2] == ["late_f", "neumf_f"] and top_late_neumf() and set(test()[:4]) == FEAT, ["S2"]),
        ("content/C4.tex", "từ thứ năm và thứ bảy lúc tinh chỉnh",
         "v2: GMF, MLP tụt từ hạng 5, 7 (tinh chỉnh); ItemKNN lên từ hạng 10; đổi hạng lớn nhất; chỉ GMF, MLP giảm",
         lambda: (lambda r: (r["gmf"][0], r["mlp"][0], r["itemknn"][0]) == (5, 7, 10)
                  and {m for m, (a, b) in r.items() if abs(a - b) == max(abs(x - y) for x, y in r.values())}
                  == {"gmf", "mlp", "itemknn"}
                  and set(S2.index[S2["NDCG@10_mean"] < S2["val_NDCG@10"]]) == {"gmf", "mlp"})(rank_shift()),
         ["S2"]),
        ("content/C4.tex", "NeuMF-F vượt cả năm baseline trong họ so sánh",
         "v2: NeuMF-F tốt hơn có ý nghĩa cả 5 baseline; chênh nhỏ nhất UserKNN, lớn nhất Content",
         lambda: all(verdict("neumf_f", b) == BETTER for b in COMPARED_BASELINES)
         and min(COMPARED_BASELINES, key=lambda b: rel("neumf_f", b)) == "userknn"
         and max(COMPARED_BASELINES, key=lambda b: rel("neumf_f", b)) == "content", ["G2"]),
        ("content/C4.tex", "đây là chênh lệch lớn nhất giữa hai mô hình học sâu",
         "v2: NeuMF-F vs NeuMF chênh lớn nhất trong các so sánh 1–4",
         lambda: rel("neumf_f", "neumf") > max(rel("neumf_f", b) for b in ("gmf_f", "mlp_f", "late_f")), ["G2"]),
        ("content/C4.tex", "khi chỉ dùng ID, mô hình lai NeuMF không khác biệt có ý nghĩa với BPR-MF",
         "v2: NeuMF vs BPR-MF không khác biệt có ý nghĩa", lambda: verdict("neumf", "bpr") == NOT_SIG, ["G2"]),
        ("content/C4.tex", "hợp nhất sớm hai nhánh vượt nhánh phi tuyến MLP-F",
         "v2: NeuMF-F tốt hơn MLP-F, không khác biệt với GMF-F và LateFusion-F", fusion, ["G2"]),
        ("content/C4.tex", "LateFusion-F có NDCG@10 trung bình cao nhất nhưng không khác biệt có ý nghĩa",
         "v2: LateFusion-F cao nhất, không khác biệt có ý nghĩa với NeuMF-F",
         lambda: test()[0] == "late_f" and verdict("neumf_f", "late_f") == NOT_SIG, ["S2", "G2"]),
        ("content/C4.tex", "chỉ được ủng hộ so với nhánh MLP-F", "v2: NeuMF-F tốt hơn MLP-F, không khác biệt với GMF-F "
         "và LateFusion-F", fusion, ["G2"]),
        # ---- C3, C5, tóm tắt
        ("content/C3.tex", "cấu hình NeuMF-F được chọn có $\\rho = 0$", "v2: cấu hình NeuMF-F đã chọn có id_dropout = 0",
         rho0, ["best"]),
        ("content/C5.tex", "sau LateFusion-F với", "v2: LateFusion-F cao nhất, NeuMF-F thứ hai", top_late_neumf, ["S2"]),
        ("content/C5.tex", "trong đó đặc trưng thời gian đóng góp nhiều nhất",
         "v2: ablation — bỏ đặc trưng thời gian giảm nhiều nhất", time_most, ["A2"]),
        ("content/C5.tex", "Hợp nhất sớm hai nhánh vượt nhánh MLP-F đứng riêng",
         "v2: NeuMF-F tốt hơn MLP-F, không khác biệt với GMF-F và LateFusion-F", fusion, ["G2"]),
        ("frontmatter/abstract.tex", "trong 14 mô hình, sau LateFusion-F", "v2: LateFusion-F cao nhất, NeuMF-F thứ hai",
         top_late_neumf, ["S2"]),
        ("frontmatter/abstract.tex", "NeuMF-F không khác biệt có ý nghĩa với nhánh GMF-F đứng riêng",
         "v2: NeuMF-F không khác biệt có ý nghĩa với GMF-F và LateFusion-F", not_gmf_late, ["G2"]),
        ("frontmatter/abstract.tex", "đặc trưng thời gian đóng góp nhiều nhất trong ablation",
         "v2: ablation — bỏ đặc trưng thời gian giảm nhiều nhất", time_most, ["A2"]),
        ("frontmatter/abstract_english.tex", "second of 14 models after LateFusion-F",
         "v2: LateFusion-F cao nhất, NeuMF-F thứ hai", top_late_neumf, ["S2"]),
        ("frontmatter/abstract_english.tex", "is not significantly different from its GMF-F branch alone",
         "v2: NeuMF-F không khác biệt có ý nghĩa với GMF-F và LateFusion-F", not_gmf_late, ["G2"]),
        ("frontmatter/abstract_english.tex", "time features matter most in the ablation",
         "v2: ablation — bỏ đặc trưng thời gian giảm nhiều nhất", time_most, ["A2"]),
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
    print("1. Tái lập: so với bản đã commit (git HEAD)")
    out = {}
    for name, key in V2_FILES:
        new, old = read_csv(name), read_csv(name, committed=True)
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
    print("\n3. Số chép tay trong tài liệu")

    def load(committed):
        s = read_csv("summary.csv", committed)
        g = read_csv("significance.csv", committed)
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
MACRO_RE = re.compile(r"\\(Res|Sig|VRes|VSd|VVal|VRank|VSig|VAbl|VBey|VData|VCfg)\{([^{}]*)\}\{([^{}]*)\}")


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
