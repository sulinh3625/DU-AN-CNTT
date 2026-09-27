"""Vẽ biểu đồ kết quả cuối (test, 3 seed) từ outputs/final/ — dùng cho báo cáo.

    python scripts/12_significance.py && python scripts/13_plot_final.py

Ra outputs/figures/: final_metrics.png (3 metric, mean ± std + điểm từng seed), final_significance.png (chênh lệch
NDCG@10 + CI 95% bootstrap, p Holm), final_val_vs_test.png (NDCG@10 trên val lúc tuning vs test).
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
BEST = PROJECT_ROOT.parent / "docs" / "audit" / "best_configs.json"

# Bảng màu tham chiếu (skill dataviz), 3 slot đầu — đã chạy validate_palette.js --pairs all: PASS.
GROUP = {"Mô hình đề tài (NeuMF)": "#2a78d6", "Ablation (GMF, MLP)": "#eb6834", "Baseline": "#1baf7a"}
MODEL_GROUP = {"NeuMF-Pretrained": "Mô hình đề tài (NeuMF)", "NeuMF-Scratch": "Mô hình đề tài (NeuMF)",
               "GMF": "Ablation (GMF, MLP)", "MLP": "Ablation (GMF, MLP)",
               "BPR-MF": "Baseline", "MostPopular": "Baseline", "Random": "Baseline"}
TUNE_KEY = {"BPR-MF": "bpr", "GMF": "gmf", "MLP": "mlp", "NeuMF-Scratch": "neumf_scratch",
            "NeuMF-Pretrained": "neumf_pretrained"}
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
    axes[0].set_yticks(list(y), order, fontsize=10, color=INK)
    axes[0].invert_yaxis()
    handles = [Patch(color=c, label=g) for g, c in GROUP.items()]
    handles.append(Line2D([], [], marker="o", color=INK, linestyle="none", markersize=4, label="Từng seed"))
    fig.legend(handles=handles, loc="upper center", ncol=4, frameon=False, fontsize=9, bbox_to_anchor=(0.5, 1.0))
    fig.suptitle("Kết quả trên tập test — trung bình ± độ lệch chuẩn qua 3 seed (Full Ranking, 2.893 user)",
                 fontsize=12, color=INK, y=1.08)
    fig.savefig(FIG / "final_metrics.png", dpi=200, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


def plot_significance(sig: pd.DataFrame):
    sig = sig.iloc[::-1].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(9, 4.4), facecolor=SURFACE)
    y = range(len(sig))
    ax.axvline(0, color=INK2, linewidth=1)
    ax.hlines(list(y), sig["ci_low"], sig["ci_high"], color="#2a78d6", linewidth=2)
    ax.scatter(sig["diff"], list(y), s=40, color="#2a78d6", zorder=3, edgecolors=SURFACE, linewidths=2)
    ax.set_yticks(list(y), [f"{a}  vs  {b}" for a, b in zip(sig["A"], sig["B"])], fontsize=9.5, color=INK)
    right = max(sig["ci_high"].max(), 0) * 1.05
    for i, r in sig.iterrows():
        ax.text(1.02, i, f"{r['rel_diff'] * 100:+.1f}%".replace(".", ",") + f"   p Holm = {vn(r['p_holm'], 3)}",
                transform=ax.get_yaxis_transform(), va="center", fontsize=8.5, color=INK2)
    ax.set_xlim(sig["ci_low"].min() * 1.1, right)
    ax.set_xlabel("Chênh lệch NDCG@10 (A − B), CI 95% bootstrap theo user", fontsize=9, color=INK2)
    ax.set_title("Kiểm định cặp: không so sánh nào có ý nghĩa (Wilcoxon + Holm, α = 0,05)",
                 fontsize=11, color=INK, loc="left")
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
                       for c, lab in (("#eb6834", "Validation (seed 42, cấu hình tốt nhất)"),
                                      ("#2a78d6", "Test (trung bình 3 seed)"))],
              loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2, frameon=False, fontsize=9)
    ax.set_title("NDCG@10: thứ hạng trên validation không giữ nguyên trên test", fontsize=11, color=INK, loc="left")
    style(ax, 4)
    fig.savefig(FIG / "final_val_vs_test.png", dpi=200, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    per = pd.concat([pd.read_csv(f) for f in sorted(FINAL.glob("seed*/results_per_user.csv"))], ignore_index=True)
    order = per.groupby(["model", "seed"])["NDCG@10"].mean().groupby("model").mean().sort_values(ascending=False).index.tolist()
    plot_metrics(per, order)
    plot_significance(pd.read_csv(FINAL / "significance.csv"))
    plot_val_vs_test(per, order)
    print("Đã ghi:", *sorted(p.name for p in FIG.glob("final_*.png")))


if __name__ == "__main__":
    main()
