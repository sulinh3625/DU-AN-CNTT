"""Đánh giá Full Ranking cho giao thức v2: như full_ranking.py nhưng ghi hạng của TỪNG sản phẩm đúng kèm cờ "sản phẩm
mới", để tính chỉ số riêng cho nhóm sản phẩm cũ / mới mà không phải chấm lại mô hình.

Chỉ số của một nhóm (old/new) coi riêng các sản phẩm đúng của nhóm đó là liên quan, với hạng trong cùng danh sách xếp
hạng đầy đủ; người dùng không có sản phẩm đúng thuộc nhóm thì không tính vào trung bình của nhóm.
"""
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
    """(item, hạng) của từng sản phẩm đúng; thứ tự xếp hạng: điểm giảm dần, hoà thì theo khoá giả ngẫu nhiên tất định."""
    cand = record.candidates
    order = np.lexsort((deterministic_tie_key(record.user, cand, tie_seed), -np.asarray(scores, dtype=np.float64)))
    ordered = cand[order]
    hit = np.isin(ordered, record.positives)
    return ordered[hit], np.flatnonzero(hit) + 1, ordered


def evaluate_v2(scorer, records, new_mask, device="cpu", tie_seed: int = 2026, k_values=K_VALUES,
                per_user: list | None = None, topk: dict | None = None, max_k: int = 20):
    """scorer: nn.Module (gọi (users, items)) hoặc đối tượng có score_items(user, items).
    Trả về dict trung bình theo người dùng: "{NDCG,HR,Recall,Precision}@K" (mọi sản phẩm đúng), thêm hậu tố
    "_old"/"_new" cho hai nhóm, và "users_new" = số người dùng có sản phẩm đúng mới."""
    new_mask = np.asarray(new_mask, dtype=bool)
    if isinstance(scorer, torch.nn.Module):
        all_scores = _torch_scores(scorer, records, device)
    else:
        all_scores = (np.asarray(scorer.score_items(r.user, r.candidates), dtype=np.float64) for r in records)
    acc = {f"{n}@{k}{sfx}": [] for n in NAMES for k in k_values for sfx in ("", "_old", "_new")}
    for rec, scores in zip(records, all_scores):
        items, ranks, ordered = positive_ranks(scores, rec, tie_seed)
        is_new = new_mask[items]
        row = {"user": int(rec.user), "n_candidates": len(rec.candidates), "n_positives": len(items),
               "n_new": int(is_new.sum()), "ranks": ";".join(map(str, ranks)),
               "new_flags": "".join("1" if f else "0" for f in is_new)}
        for sfx, sel in (("", slice(None)), ("_old", ~is_new), ("_new", is_new)):
            r = ranks[sel]
            if len(r) == 0:
                continue
            for k in k_values:
                m = multi_ranking_metrics(r, k)
                for n in NAMES:
                    acc[f"{n}@{k}{sfx}"].append(m[n])
                    row[f"{n}@{k}{sfx}"] = m[n]
        if per_user is not None:
            per_user.append(row)
        if topk is not None:
            topk[int(rec.user)] = ordered[:max_k].tolist()
    out = {name: float(np.mean(v)) if v else float("nan") for name, v in acc.items()}
    out["users_new"] = len(acc[f"NDCG@{k_values[0]}_new"])
    out["users"] = len(acc[f"NDCG@{k_values[0]}"])
    return out
