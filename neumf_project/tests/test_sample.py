"""Lấy mẫu theo khối bucket (scripts/00_sample_hm.py): khối 0/1 trùng mẫu hm500k/hm500k_b cũ; các khối liên tiếp, không
giao nhau, mỗi khối vừa đủ số dòng; hết bucket thì dừng."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("sample_hm", ROOT / "scripts" / "00_sample_hm.py")
sample_hm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sample_hm)


def _old_select_buckets(counts, target_rows, holdout=False):
    """Chép nguyên văn select_buckets trước khi có --block (commit c1603c7) — hàm tham chiếu."""
    def n_needed(c):
        return min(int(np.searchsorted(np.cumsum(c), target_rows)) + 1, len(c))
    n_main = n_needed(counts)
    if not holdout:
        return 0, n_main
    if n_main >= len(counts):
        raise SystemExit("Không còn bucket cho mẫu holdout — giảm --target-rows")
    return n_main, n_needed(counts[n_main:])


def test_blocks_0_and_1_match_old_holdout_logic():
    rng = np.random.default_rng(0)
    for _ in range(300):
        counts = rng.integers(0, 50, size=int(rng.integers(5, 400)))
        target = int(rng.integers(1, 5000))
        assert sample_hm.select_buckets(counts, target, block=0) == _old_select_buckets(counts, target)
        try:
            old = _old_select_buckets(counts, target, holdout=True)
        except SystemExit:
            with pytest.raises(SystemExit):
                sample_hm.select_buckets(counts, target, block=1)
        else:
            assert sample_hm.select_buckets(counts, target, block=1) == old


def test_blocks_are_consecutive_disjoint_and_just_large_enough():
    counts = np.random.default_rng(1).integers(0, 20, size=2000)
    target = 3000
    blocks = [sample_hm.select_buckets(counts, target, block=b) for b in range(3)]
    assert blocks[0][0] == 0
    for (s0, n0), (s1, _) in zip(blocks, blocks[1:]):
        assert s0 + n0 == s1  # khối sau bắt đầu ngay sau khối trước: liên tiếp, không giao nhau
    for s, n in blocks:
        assert counts[s:s + n].sum() >= target
        assert counts[s:s + n - 1].sum() < target  # bỏ bucket cuối thì thiếu: vừa đủ


def test_last_block_may_hit_end_then_runs_out():
    counts = np.full(5, 5)
    blocks = [sample_hm.select_buckets(counts, 10, block=b) for b in range(3)]
    assert blocks == [(0, 2), (2, 2), (4, 1)]  # khối 2 chạm cuối mảng: chỉ còn 5 dòng < 10
    with pytest.raises(SystemExit, match="Hết bucket"):
        sample_hm.select_buckets(counts, 10, block=3)
    with pytest.raises(SystemExit):
        sample_hm.select_buckets(counts, 10, block=-1)
