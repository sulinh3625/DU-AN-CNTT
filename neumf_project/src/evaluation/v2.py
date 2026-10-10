"""Đánh giá Full Ranking cho giao thức v2: như full_ranking.py nhưng ghi hạng của TỪNG sản phẩm đúng, để tính mọi chỉ số
@K từ một lần xếp hạng và lưu được hạng theo từng người dùng."""
from __future__ import annotations

import numpy as np
import torch

from .full_ranking import EvalRecord
from .metrics import multi_ranking_metrics
from .ranking_utils import deterministic_tie_key

K_VALUES = (5, 10, 20)
NAMES = ("NDCG", "HR", "Recall", "Precision")


@torch.no_grad()
def _torch_scores(model, records, device, batch_size=16384) -> list[np.ndarray]:
    model.eval()
    lengths = np.fromiter((len(r.candidates) for r in records), dtype=np.int64, count=len(records))
    offsets = np.concatenate(([0], np.cumsum(lengths)))
    users = np.repeat(np.fromiter((r.user for r in records), dtype=np.int64, count=len(records)), lengths)
    items = np.concatenate([r.candidates for r in records]) if records else np.empty(0, np.int64)
    out = np.empty(len(items), dtype=np.float32)
    for s in range(0, len(items), batch_size):
        e = min(s + batch_size, len(items))
        out[s:e] = model(torch.from_numpy(users[s:e]).to(device), torch.from_numpy(items[s:e]).to(device)).cpu().numpy()
    return [out[offsets[k]:offsets[k + 1]] for k in range(len(records))]


def positive_ranks(scores, record: EvalRecord, tie_seed: int):
    """Hạng của từng sản phẩm đúng và danh sách đã xếp; thứ tự xếp hạng: điểm giảm dần, hoà thì theo khoá giả ngẫu nhiên
    tất định."""
    cand = record.candidates
    order = np.lexsort((deterministic_tie_key(record.user, cand, tie_seed), -np.asarray(scores, dtype=np.float64)))
    ordered = cand[order]
    return np.flatnonzero(np.isin(ordered, record.positives)) + 1, ordered


def evaluate_v2(scorer, records, device="cpu", tie_seed: int = 2026, k_values=K_VALUES,
                per_user: list | None = None, topk: dict | None = None, max_k: int = 20):
    """scorer: nn.Module (gọi (users, items)) hoặc đối tượng có score_items(user, items).
    Trả về dict trung bình theo người dùng "{NDCG,HR,Recall,Precision}@K" và "users" = số người dùng được chấm."""
    if isinstance(scorer, torch.nn.Module):
        all_scores = _torch_scores(scorer, records, device)
    else:
        all_scores = (np.asarray(scorer.score_items(r.user, r.candidates), dtype=np.float64) for r in records)
    acc = {f"{n}@{k}": [] for n in NAMES for k in k_values}
    for rec, scores in zip(records, all_scores):
        ranks, ordered = positive_ranks(scores, rec, tie_seed)
        row = {"user": int(rec.user), "n_candidates": len(rec.candidates), "n_positives": len(ranks),
               "ranks": ";".join(map(str, ranks))}
        for k in k_values if len(ranks) else ():  # người dùng không có sản phẩm đúng: không tính vào trung bình
            m = multi_ranking_metrics(ranks, k)
            for n in NAMES:
                acc[f"{n}@{k}"].append(m[n])
                row[f"{n}@{k}"] = m[n]
        if per_user is not None:
            per_user.append(row)
        if topk is not None:
            topk[int(rec.user)] = ordered[:max_k].tolist()
    out = {name: float(np.mean(v)) if v else float("nan") for name, v in acc.items()}
    out["users"] = len(acc[f"NDCG@{k_values[0]}"])
    return out
