"""Vẽ biểu đồ kết quả cuối (test, 3 seed) từ outputs/final/ — dùng cho báo cáo.

    python scripts/12_significance.py && python scripts/13_plot_final.py

Ra outputs/figures/: final_metrics.png (3 metric, mean ± std + điểm từng seed), final_significance.png (chênh lệch
NDCG@10 + CI 95% bootstrap, p Holm), final_val_vs_test.png (NDCG@10 trên val lúc tuning vs test),
final_training_curves.png (đường hội tụ seed 42, cần history.csv của 11_final.py), final_ablation_val.png (ablation
trên validation, cần outputs/ablation/ablation_val.csv của 20_ablation.py). Tiêu đề hình sinh theo số liệu.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FINAL = PROJECT_ROOT / "outputs" / "final"
FIG = PROJECT_ROOT / "outputs" / "figures"
BEST = PROJECT_ROOT / "audit" / "best_configs.json"

# Bảng màu tham chiếu (skill dataviz), 3 slot đầu — đã chạy validate_palette.js --pairs all: PASS.
GROUP = {"Mô hình đề tài (NeuMF)": "#2a78d6", "Ablation (GMF, MLP)": "#eb6834", "Baseline": "#1baf7a"}
MODEL_GROUP = {"NeuMF-Pretrained": "Mô hình đề tài (NeuMF)", "NeuMF-Scratch": "Mô hình đề tài (NeuMF)",
               "GMF": "Ablation (GMF, MLP)", "MLP": "Ablation (GMF, MLP)",
               "BPR-MF": "Baseline", "MostPopular": "Baseline", "Random": "Baseline"}
TUNE_KEY = {"BPR-MF": "bpr", "GMF": "gmf", "MLP": "mlp", "NeuMF-Scratch": "neumf_scratch",
            "NeuMF-Pretrained": "neumf_pretrained"}
DISPLAY = {"MostPopular": "Most Popular"}  # cùng tên hiển thị với bảng của 15_export_report.py


def show(m: str) -> str:
    return DISPLAY.get(m, m)
INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"


def vn(x, nd=4):
    return f"{x:.{nd}f}".replace(".", ",")


def style(ax, xfmt=4):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=INK2, labelsize=9, length=0)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: vn(v, xfmt)))


def plot_metrics(per: pd.DataFrame, order: list[str]):
    metrics = ["NDCG@10", "Recall@10", "HR@10"]
    by_seed = per.groupby(["model", "seed"])[metrics].mean().reset_index()
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True, facecolor=SURFACE)
    y = range(len(order))
    for ax, m in zip(axes, metrics):
        stat = by_seed.groupby("model")[m].agg(["mean", "std"]).loc[order]
        ax.barh(list(y), stat["mean"], height=0.62, color=[GROUP[MODEL_GROUP[o]] for o in order],
                edgecolor=SURFACE, linewidth=2)
        ax.errorbar(stat["mean"], list(y), xerr=stat["std"], fmt="none", ecolor=INK2, elinewidth=1.2, capsize=3)
        for i, o in enumerate(order):
            pts = by_seed.loc[by_seed["model"] == o, m]
            ax.scatter(pts, [i] * len(pts), s=14, color=INK, zorder=3, linewidths=0)
            ax.text(stat["mean"][o] + stat["std"].fillna(0)[o] + stat["mean"].max() * 0.02, i,
                    vn(stat["mean"][o]), va="center", fontsize=8.5, color=INK)
        ax.set_xlim(0, stat["mean"].max() * 1.28)
        ax.set_title(m, fontsize=11, color=INK, loc="left")
        style(ax, 3)
    axes[0].set_yticks(list(y), [show(o) for o in order], fontsize=10, color=INK)
    axes[0].invert_yaxis()
    handles = [Patch(color=c, label=g) for g, c in GROUP.items()]
    handles.append(Line2D([], [], marker="o", color=INK, linestyle="none", markersize=4, label="Từng seed"))
    fig.legend(handles=handles, loc="upper center", ncol=4, frameon=False, fontsize=9, bbox_to_anchor=(0.5, 1.0))
    n_users = f"{per['user'].nunique():,}".replace(",", ".")
    fig.suptitle(f"Kết quả trên tập kiểm thử — trung bình ± độ lệch chuẩn qua {per['seed'].nunique()} seed "
                 f"(Full Ranking, {n_users} người dùng)", fontsize=12, color=INK, y=1.08)
    fig.savefig(FIG / "final_metrics.png", dpi=200, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


def plot_significance(sig: pd.DataFrame):
    sig = sig.iloc[::-1].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(9, 4.4), facecolor=SURFACE)
    y = range(len(sig))
    ax.axvline(0, color=INK2, linewidth=1)
    ax.hlines(list(y), sig["ci_low"], sig["ci_high"], color="#2a78d6", linewidth=2)
    ax.scatter(sig["diff"], list(y), s=40, color="#2a78d6", zorder=3, edgecolors=SURFACE, linewidths=2)
    ax.set_yticks(list(y), [f"{show(a)}  vs  {show(b)}" for a, b in zip(sig["A"], sig["B"])], fontsize=9.5, color=INK)
    right = max(sig["ci_high"].max(), 0) * 1.05
    for i, r in sig.iterrows():
        ax.text(1.02, i, f"{r['rel_diff'] * 100:+.1f}%".replace(".", ",") + f"   p Holm = {vn(r['p_holm'], 3)}",
                transform=ax.get_yaxis_transform(), va="center", fontsize=8.5, color=INK2)
    ax.set_xlim(sig["ci_low"].min() * 1.1, right)
    ax.set_xlabel("Chênh lệch NDCG@10 (A − B), khoảng tin cậy 95% (bootstrap theo người dùng)", fontsize=9, color=INK2)
    n_sig = int((sig["verdict"] != "không khác biệt có ý nghĩa").sum())
    verdict = "không so sánh nào có ý nghĩa" if n_sig == 0 else f"{n_sig}/{len(sig)} so sánh có ý nghĩa"
    ax.set_title(f"Kiểm định cặp: {verdict} (Wilcoxon + Holm, α = 0,05)", fontsize=11, color=INK, loc="left")
    style(ax, 4)
    fig.savefig(FIG / "final_significance.png", dpi=200, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


def plot_val_vs_test(per: pd.DataFrame, order: list[str]):
    best = json.loads(BEST.read_text(encoding="utf-8"))
    test = per.groupby(["model", "seed"])["NDCG@10"].mean().groupby("model").mean()
    models = [m for m in order if m in TUNE_KEY]
    fig, ax = plt.subplots(figsize=(7.5, 3.8), facecolor=SURFACE)
    for i, m in enumerate(models):
        v, t = best[TUNE_KEY[m]]["val"]["NDCG@10"], test[m]
        ax.plot([v, t], [i, i], color=GRID, linewidth=2, zorder=1)
        ax.scatter([v], [i], s=46, color="#eb6834", zorder=3, edgecolors=SURFACE, linewidths=2)
        ax.scatter([t], [i], s=46, color="#2a78d6", zorder=3, edgecolors=SURFACE, linewidths=2)
    ax.set_yticks(range(len(models)), models, fontsize=10, color=INK)
    ax.invert_yaxis()
    ax.legend(handles=[Line2D([], [], marker="o", color=c, linestyle="none", markersize=7, label=lab)
                       for c, lab in (("#eb6834", "Tập xác thực (seed 42, cấu hình tốt nhất)"),
                                      ("#2a78d6", "Tập kiểm thử (trung bình 3 seed)"))],
              loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2, frameon=False, fontsize=9)
    val_rank = sorted(models, key=lambda m: -best[TUNE_KEY[m]]["val"]["NDCG@10"])
    test_rank = sorted(models, key=lambda m: -test[m])
    kept = "giữ nguyên" if val_rank == test_rank else "không giữ nguyên"
    ax.set_title(f"NDCG@10: thứ hạng trên tập xác thực {kept} trên tập kiểm thử", fontsize=11, color=INK, loc="left")
    style(ax, 4)
    fig.savefig(FIG / "final_val_vs_test.png", dpi=200, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


NEURAL_COLOR = {"GMF": "#eb6834", "MLP": "#f2b134", "NeuMF-Scratch": "#2a78d6", "NeuMF-Pretrained": "#173f7a"}


def style_lines(ax, yfmt=4):
    """Kiểu cho biểu đồ đường: trục x là epoch/số nguyên, trục y định dạng số kiểu Việt Nam."""
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=INK2, labelsize=9, length=0)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: vn(v, yfmt)))


def plot_training_curves(seed_dir: Path):
    """Đường hội tụ của 4 mạng nơ-ron (seed 42): NDCG@10 validation và loss huấn luyện theo epoch, phase chọn epoch."""
    path = seed_dir / "history.csv"
    if not path.exists():
        print(f"Bỏ qua đường hội tụ: chưa có {path.relative_to(PROJECT_ROOT).as_posix()} (11_final.py bản mới ghi file này)")
        return
    h = pd.read_csv(path)
    sel = h[h["phase"] == "select"]
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.2), facecolor=SURFACE)
    for m, c in NEURAL_COLOR.items():
        d = sel[sel["model"] == m]
        if d.empty:
            continue
        axes[0].plot(d["epoch"], d["NDCG@10"], color=c, linewidth=1.8, marker="o", markersize=3, label=m)
        b = d.loc[d["NDCG@10"].idxmax()]
        axes[0].scatter([b["epoch"]], [b["NDCG@10"]], s=90, facecolors="none", edgecolors=c, linewidths=1.8, zorder=3)
        axes[1].plot(d["epoch"], d["loss"], color=c, linewidth=1.8, label=m)
    axes[0].set_title("NDCG@10 trên tập xác thực theo epoch (vòng tròn: epoch tốt nhất)", fontsize=11, color=INK,
                      loc="left")
    axes[1].set_title("Hàm mất mát BCE trên tập huấn luyện theo epoch", fontsize=11, color=INK, loc="left")
    for ax, fmt in zip(axes, (4, 3)):
        style_lines(ax, fmt)
        ax.set_xlabel("Epoch", fontsize=9, color=INK2)
        ax.xaxis.get_major_locator().set_params(integer=True)
    axes[0].legend(loc="lower right", frameon=False, fontsize=9)
    fig.suptitle(f"Đường hội tụ khi chọn số epoch (seed {seed_dir.name.removeprefix('seed')}; NeuMF-Pretrained: giai "
                 "đoạn tinh chỉnh sau tiền huấn luyện)", fontsize=12, color=INK, y=1.03)
    fig.savefig(FIG / "final_training_curves.png", dpi=200, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


ABLATION = PROJECT_ROOT / "outputs" / "ablation" / "ablation_val.csv"
ABLATION_FACTORS = [("embedding_dim", "Số chiều Embedding d"), ("n_hidden", "Số tầng ẩn của tháp MLP"),
                    ("negative_ratio", "Số mẫu âm cho mỗi mẫu dương")]


def plot_ablation():
    """Ablation trên validation (scripts/20_ablation.py): NDCG@10 khi đổi từng yếu tố, cột đậm = cấu hình đã chọn."""
    if not ABLATION.exists():
        print("Bỏ qua hình ablation: chưa có outputs/ablation/ablation_val.csv (chạy scripts/20_ablation.py)")
        return
    a = pd.read_csv(ABLATION, dtype={"value": str}, keep_default_na=False)
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.9), sharey=True, facecolor=SURFACE)
    for ax, (factor, label) in zip(axes, ABLATION_FACTORS):
        rows = a[a["factor"].isin([factor, "base"])].sort_values(factor)
        xs = rows[factor].astype(int).astype(str).tolist()
        colors = ["#2a78d6" if f == "base" else "#a9c4e8" for f in rows["factor"]]
        ax.bar(xs, rows["NDCG@10"], color=colors, width=0.62)
        for x, v in zip(xs, rows["NDCG@10"]):
            ax.text(x, v, vn(v, 4), ha="center", va="bottom", fontsize=8, color=INK)
        ax.set_xlabel(label, fontsize=9.5, color=INK2)
        style_lines(ax, 4)
    axes[0].set_ylabel("NDCG@10 (tập xác thực)", fontsize=9.5, color=INK2)
    fig.suptitle("Ablation NeuMF-Scratch trên tập xác thực — đổi từng yếu tố quanh cấu hình đã chọn (cột đậm), "
                 "seed 42", fontsize=12, color=INK, y=1.04)
    fig.savefig(FIG / "final_ablation_val.png", dpi=200, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    per = pd.concat([pd.read_csv(f) for f in sorted(FINAL.glob("seed*/results_per_user.csv"))], ignore_index=True)
    order = per.groupby(["model", "seed"])["NDCG@10"].mean().groupby("model").mean().sort_values(ascending=False).index.tolist()
    plot_metrics(per, order)
    plot_significance(pd.read_csv(FINAL / "significance.csv"))
    plot_val_vs_test(per, order)
    plot_training_curves(FINAL / "seed42")
    plot_ablation()
    print("Đã ghi:", *sorted(p.name for p in FIG.glob("final_*.png")))


if __name__ == "__main__":
    main()
