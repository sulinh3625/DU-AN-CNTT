"""Đối chiếu báo cáo và tài liệu với số liệu hiện có — chạy sau scripts/24_report_v2.py; không chấm test.

    python scripts/19_check_report.py            # in kết quả, luôn trả mã 0
    python scripts/19_check_report.py --strict   # trả mã 1 nếu có khẳng định sai / macro, bảng, hình thiếu

Bốn phần:
  1. Tái lập: outputs/v2/final/{summary,significance,ablation,beyond,by_k}.csv so với bản đã commit (git HEAD) — độ
     lệch tuyệt đối lớn nhất (chạy lại đánh giá cuối trên cùng máy kỳ vọng lệch 0).
  2. Khẳng định bằng chữ trong báo cáo mà macro số liệu không tự cập nhật — mỗi khẳng định là một điều kiện trên CSV
     của outputs/v2/final/ (H&M), outputs/amazon/final/ (Amazon Beauty) hoặc audit/v2/best_configs.json; sai thì in
     tệp:dòng cần sửa.
  3. Số chép tay trong van_dap.md, pham_vi_du_an.md, README.md: nếu số v2 khác bản đã commit, liệt kê các dòng còn ghi
     số cũ.
  4. Mọi macro (\\VRes, \\VSig, ... của H&M; \\ARes, \\ASig, ... của Amazon; \\Res, \\Sig của lịch sử phát triển), mọi
     bảng \\bangketquaV, \\bangketquaA và hình \\hinhketqua mà báo cáo dùng đều đã được sinh (nếu không, PDF hiện
     "[chưa có]" / khung "Chưa có số liệu").
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
FINAL_AMZ = PROJECT_ROOT / "outputs" / "amazon" / "final"  # kiểm chứng Amazon Beauty (audit/PREREG_amazon.md)
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
            ("ablation.csv", ["variant"]), ("beyond.csv", ["model"]), ("by_k.csv", ["model"]))
K_ALL = (5, 10, 15, 20)
K_METRICS = ("NDCG", "Recall", "HR", "Precision")


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
        def load(root: Path):
            s, g, b, a, k = (read_csv(n, root=root) for n in ("summary.csv", "significance.csv", "beyond.csv",
                                                               "ablation.csv", "by_k.csv"))
            return (None if s is None else s.set_index("model"),
                    None if g is None or g.empty else g.set_index(["A", "B"]),
                    None if b is None else b.set_index("model"),
                    None if a is None or a.empty else a.set_index("variant"),
                    None if k is None or k.empty else k.set_index("model"))

        self.S2, self.G2, self.B2, self.A2, self.K2 = load(FINAL_V2)  # H&M
        self.SA, self.GA, self.BA, self.AA, self.KA = load(FINAL_AMZ)  # Amazon Beauty
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
    K2, SA, GA, BA, AA, KA = d.K2, d.SA, d.GA, d.BA, d.AA, d.KA
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

    # ---- theo K (by_k.csv) và Amazon Beauty (outputs/amazon/final/)
    def by_k_order(K, metric, k):
        return order(K[f"{metric}@{k}_mean"].drop("random", errors="ignore"))

    feat_lead_all_k = lambda K: all(by_k_order(K, n, k)[:4] == ["late_f", "neumf_f", "gmf_f", "mlp_f"]  # noqa: E731
                                    for n in K_METRICS for k in K_ALL)
    neumff_k_trend = lambda: (  # noqa: E731
        K2.loc["neumf_f", "HR@5_mean"] < K2.loc["neumf_f", "HR@20_mean"]
        and K2.loc["neumf_f", "Recall@5_mean"] < K2.loc["neumf_f", "Recall@20_mean"]
        and K2.loc["neumf_f", "Precision@5_mean"] > K2.loc["neumf_f", "Precision@20_mean"])
    recpop_over_uknn = lambda: all(K2.loc["recent_pop", f"HR@{k}_mean"] > K2.loc["userknn", f"HR@{k}_mean"]  # noqa: E731
                                   for k in (15, 20))
    a_test = lambda: order(SA["NDCG@10_mean"].drop("random", errors="ignore"))  # noqa: E731
    a_verdict = lambda a, b: GA.loc[(a, b), "verdict"]  # noqa: E731
    a_rel = lambda a, b: abs(GA.loc[(a, b), "rel_diff"])  # noqa: E731
    a_abl = lambda: AA["rel"].drop("neumf_f").sort_values()  # noqa: E731
    a_ci0 = lambda v: AA.loc[v, "ci_low"] < 0 < AA.loc[v, "ci_high"]  # noqa: E731
    a_late_wins = lambda: a_verdict("neumf_f", "late_f") == "B tốt hơn"  # noqa: E731
    a_bpr_weak = lambda: SA.loc["bpr", "NDCG@10_mean"] < min(  # noqa: E731
        SA.loc[m, "NDCG@10_mean"] for m in ("itemknn", "userknn", "recent_pop"))
    a_all_baselines = lambda: (all(a_verdict("neumf_f", b) == BETTER for b in COMPARED_BASELINES)  # noqa: E731
                               and min(COMPARED_BASELINES, key=lambda b: a_rel("neumf_f", b)) == "userknn")
    hm_abstract_family = lambda: (all(verdict("neumf_f", b) == BETTER for b in ["neumf", "mlp_f", *COMPARED_BASELINES])  # noqa: E731
                                  and min(COMPARED_BASELINES, key=lambda b: rel("neumf_f", b)) == "userknn"
                                  and max(COMPARED_BASELINES, key=lambda b: rel("neumf_f", b)) == "content")
    a_gmf_mlp_tie = lambda: (a_verdict("neumf_f", "gmf_f") == NOT_SIG  # noqa: E731
                             and a_verdict("neumf_f", "mlp_f") == NOT_SIG)
    a_mlp_borderline = lambda: (abs(GA.loc[("neumf_f", "mlp_f"), "p_holm"] - 0.05) < 0.01  # noqa: E731
                                and GA.loc[("neumf_f", "mlp_f"), "ci_low"] < 0 < GA.loc[("neumf_f", "mlp_f"), "ci_high"])
    a_k_swap = lambda: (all(KA.loc["gmf_f", f"NDCG@{k}_mean"] > KA.loc["neumf_f", f"NDCG@{k}_mean"]  # noqa: E731
                            for k in K_ALL)
                        and all(KA.loc["neumf_f", f"{n}@{k}_mean"] > KA.loc["gmf_f", f"{n}@{k}_mean"]
                                for n in ("Recall", "HR", "Precision") for k in (10, 15, 20)))
    a_late_top_all_k = lambda: all(by_k_order(KA, n, k)[0] == "late_f" for n in K_METRICS for k in K_ALL)  # noqa: E731
    late_not_worse = lambda: (S2.loc["late_f", "NDCG@10_mean"] >= S2.loc["neumf_f", "NDCG@10_mean"]  # noqa: E731
                              and SA.loc["late_f", "NDCG@10_mean"] >= SA.loc["neumf_f", "NDCG@10_mean"])
    return [
        # ---- C4: kết quả
        ("content/C4.tex", "Thang giá trị tuyệt đối thấp", "v2: NDCG@10 cao nhất < 0,05",
         lambda: S2["NDCG@10_mean"].max() < 0.05, ["S2"]),
        ("content/C4.tex", "mỗi khách có vài sản phẩm đúng giữa khoảng",
         "v2: trung bình số sản phẩm đúng mỗi khách < 10",
         lambda: info["test"]["targets"] / info["test"]["users"] < 10, ["info2"]),
        ("content/C4.tex", "Trên tập xác thực của mẫu phát triển, bốn mô hình có đặc trưng đứng đầu",
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
        # ---- theo K (H&M)
        ("content/C4.tex", "thứ tự của bốn mô hình có đặc trưng giữ nguyên",
         "theo K: ở mọi K và mọi độ đo, thứ tự đầu là LateFusion-F, NeuMF-F, GMF-F, MLP-F",
         lambda: feat_lead_all_k(K2), ["K2"]),
        ("content/C4.tex", "còn Precision@$K$ giảm từ",
         "theo K: HR@K, Recall@K của NeuMF-F tăng, Precision@K giảm từ K = 5 đến 20", neumff_k_trend, ["K2"]),
        ("content/C4.tex", "MostPopular-Recent vượt UserKNN ở HR@15 và HR@20",
         "theo K: MostPopular-Recent cao hơn UserKNN ở HR@15, HR@20", recpop_over_uknn, ["K2"]),
        ("content/C5.tex", "Bốn mô hình có đặc trưng giữ nguyên thứ tự",
         "theo K: ở mọi K và mọi độ đo, thứ tự đầu là LateFusion-F, NeuMF-F, GMF-F, MLP-F",
         lambda: feat_lead_all_k(K2), ["K2"]),
        ("frontmatter/abstract.tex", "Bốn mô hình có đặc trưng giữ nguyên thứ tự",
         "theo K: ở mọi K và mọi độ đo, thứ tự đầu là LateFusion-F, NeuMF-F, GMF-F, MLP-F",
         lambda: feat_lead_all_k(K2), ["K2"]),
        ("frontmatter/abstract_english.tex", "The four feature-based models keep their order",
         "theo K: ở mọi K và mọi độ đo, thứ tự đầu là LateFusion-F, NeuMF-F, GMF-F, MLP-F",
         lambda: feat_lead_all_k(K2), ["K2"]),
        ("frontmatter/abstract.tex", "nhánh MLP-F (\\VSig{3}{rel}) và cả năm baseline",
         "v2: NeuMF-F tốt hơn có ý nghĩa NeuMF, MLP-F và cả 5 baseline; chênh nhỏ nhất UserKNN, lớn nhất Content",
         hm_abstract_family, ["G2"]),
        ("frontmatter/abstract_english.tex", "its MLP-F branch",
         "v2: NeuMF-F tốt hơn có ý nghĩa NeuMF, MLP-F và cả 5 baseline; chênh nhỏ nhất UserKNN, lớn nhất Content",
         hm_abstract_family, ["G2"]),
        # ---- Amazon Beauty
        ("content/C4.tex", "LateFusion-F đạt NDCG@10 cao nhất (\\ARes{LateF}{NDCG10}",
         "Amazon: LateFusion-F cao nhất, rồi GMF-F, NeuMF-F", lambda: a_test()[:3] == ["late_f", "gmf_f", "neumf_f"],
         ["SA"]),
        ("content/C4.tex", "Như trên H\\&M, bốn mô hình có đặc trưng đứng đầu, rồi đến UserKNN",
         "Amazon: 4 mô hình có đặc trưng đứng đầu, rồi UserKNN, ItemKNN",
         lambda: set(a_test()[:4]) == FEAT and a_test()[4:6] == ["userknn", "itemknn"], ["SA"]),
        ("content/C4.tex", "BPR-MF chỉ đạt", "Amazon: BPR-MF thấp hơn ItemKNN, UserKNN và MostPopular-Recent",
         a_bpr_weak, ["SA"]),
        ("content/C4.tex", "Trên Amazon, LateFusion-F cao nhất ở mọi $K$",
         "Amazon theo K: LateFusion-F cao nhất ở mọi K và mọi độ đo", a_late_top_all_k, ["KA"]),
        ("content/C4.tex", "NeuMF-F và GMF-F bám sát nhau và đổi chỗ tùy độ đo",
         "Amazon theo K: GMF-F cao hơn NeuMF-F ở NDCG@K; NeuMF-F cao hơn ở Recall/HR/Precision @10, @15, @20",
         a_k_swap, ["KA"]),
        ("content/C4.tex", "Kết luận (1) -- đặc trưng so với chỉ dùng ID: còn đúng",
         "Amazon: NeuMF-F tốt hơn NeuMF có ý nghĩa, 4 mô hình có đặc trưng đứng đầu, tốt hơn cả 5 baseline",
         lambda: a_verdict("neumf_f", "neumf") == BETTER and set(a_test()[:4]) == FEAT and a_all_baselines(),
         ["SA", "GA"]),
        ("content/C4.tex", "Kết luận (2) -- NeuMF-F so với từng nhánh và với hợp nhất muộn: chỉ đúng một phần",
         "Amazon: NeuMF-F ~ GMF-F, ~ MLP-F; LateFusion-F tốt hơn NeuMF-F có ý nghĩa; trên H&M NeuMF-F tốt hơn MLP-F",
         lambda: a_gmf_mlp_tie() and a_late_wins() and verdict("neumf_f", "mlp_f") == BETTER, ["GA", "G2"]),
        ("content/C4.tex", "giá trị $p$ đã hiệu chỉnh xấp xỉ ngưỡng 0,05",
         "Amazon: NeuMF-F vs MLP-F có p Holm gần 0,05 nhưng CI chứa 0", a_mlp_borderline, ["GA"]),
        ("content/C4.tex", "Kết luận (3) -- NeuMF chỉ dùng ID so với BPR-MF: không đối chiếu được",
         "NeuMF vs BPR-MF: không khác biệt trên H&M, tốt hơn trên Amazon; BPR-MF Amazon yếu hơn ItemKNN, RecPop",
         lambda: verdict("neumf", "bpr") == NOT_SIG and a_verdict("neumf", "bpr") == BETTER and a_bpr_weak(),
         ["G2", "GA", "SA"]),
        ("content/C4.tex", "hai nhánh GMF-F và MLP-F có độ phủ top-10 rất khác nhau",
         "Amazon: độ phủ top-10 của GMF-F gấp hơn 3 lần MLP-F",
         lambda: BA.loc["gmf_f", "coverage10"] > 3 * BA.loc["mlp_f", "coverage10"], ["BA"]),
        ("content/C4.tex", "Như trên H\\&M, bỏ đặc trưng thời gian làm NDCG@10 giảm nhiều nhất",
         "Amazon ablation: bỏ thời gian giảm nhiều nhất; CI của thuộc tính không chứa 0; CI của khách, văn bản chứa 0",
         lambda: a_abl().index[0] == "neumf_f-time" and not a_ci0("neumf_f-attr") and a_ci0("neumf_f-user")
         and a_ci0("neumf_f-text"), ["AA"]),
        ("content/C4.tex", "Most Popular và MostPopular-Recent vẫn thấp nhất",
         "Amazon: Most Popular, MostPopular-Recent có độ phủ top-10 thấp nhất",
         lambda: set(BA["coverage10"].nsmallest(2).index) == {"popularity", "recent_pop"}, ["BA"]),
        ("content/C4.tex", "trên Amazon Beauty, NeuMF-F cũng vượt cả năm baseline",
         "Amazon: NeuMF-F tốt hơn có ý nghĩa cả 5 baseline; chênh nhỏ nhất UserKNN", a_all_baselines, ["GA"]),
        ("content/C4.tex", "Trên Amazon, đặc trưng thời gian cũng đóng góp nhiều nhất",
         "Amazon ablation: bỏ đặc trưng thời gian giảm nhiều nhất", lambda: a_abl().index[0] == "neumf_f-time",
         ["AA"]),
        ("content/C4.tex", "hợp nhất muộn không kém hơn ở dữ liệu nào",
         "LateFusion-F có NDCG@10 trung bình không thấp hơn NeuMF-F trên cả H&M và Amazon", late_not_worse,
         ["S2", "SA"]),
        ("content/C4.tex", "bị bác bỏ ở so sánh với hợp nhất muộn trên Amazon",
         "Amazon: LateFusion-F tốt hơn NeuMF-F có ý nghĩa", a_late_wins, ["GA"]),
        ("content/C5.tex", "NeuMF-F không khác biệt có ý nghĩa với GMF-F lẫn MLP-F",
         "Amazon: NeuMF-F ~ GMF-F, ~ MLP-F; LateFusion-F tốt hơn NeuMF-F có ý nghĩa",
         lambda: a_gmf_mlp_tie() and a_late_wins(), ["GA"]),
        ("frontmatter/abstract.tex", "hợp nhất muộn LateFusion-F tốt hơn NeuMF-F có ý nghĩa",
         "Amazon: NeuMF-F tốt hơn NeuMF; LateFusion-F tốt hơn NeuMF-F có ý nghĩa",
         lambda: a_verdict("neumf_f", "neumf") == BETTER and a_late_wins(), ["GA"]),
        ("frontmatter/abstract_english.tex", "but there late fusion significantly outperforms NeuMF-F",
         "Amazon: NeuMF-F tốt hơn NeuMF; LateFusion-F tốt hơn NeuMF-F có ý nghĩa",
         lambda: a_verdict("neumf_f", "neumf") == BETTER and a_late_wins(), ["GA"]),
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
        # hậu tố riêng: bản commit cũ có thể có cột tên "..._old" (vd. NDCG@10_old của bản có sản phẩm mới)
        m = new.merge(old, on=key, suffixes=("", "@commit"), how="outer", indicator=True)
        if (m["_merge"] != "both").any():
            print(f"   {name}: tập dòng khác bản commit ({int((m['_merge'] != 'both').sum())} dòng lệch)")
            out[name] = float("inf")
            continue
        gap = max(((m[c] - m[f"{c}@commit"]).abs().max() for c in num if f"{c}@commit" in m), default=0.0)
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
MACRO_RE = re.compile(r"\\(Res|Sig|VRes|VSd|VVal|VRank|VSig|VAbl|VBey|VData|VCfg|ARes|ASd|ARank|ASig|AAbl|ABey|AData)"
                      r"\{([^{}]*)\}\{([^{}]*)\}")


def defined_macros() -> set[str]:
    out = set()
    for f in (TABLES / "results_macros.tex", TABLES / "v2" / "results_v2_macros.tex",
              TABLES / "amazon" / "results_amazon_macros.tex"):
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
        for sub, cmd in (("v2", "bangketquaV"), ("amazon", "bangketquaA")):
            for t in re.findall(r"\\" + cmd + r"\{([^}]+)\}", text):
                if not (TABLES / sub / t).exists():
                    missing_t.add(f"{sub}/{t} ({tex.name})")
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
