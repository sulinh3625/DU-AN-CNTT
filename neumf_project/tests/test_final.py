"""P4b: 11_final.py bị khoá khi thiếu --reason; 12_significance.py (Holm, verdict) đúng trên dữ liệu giả."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


final = _load("final", "11_final.py")
sig = _load("sig", "12_significance.py")


def test_final_refuses_without_reason(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["11_final.py"])
    monkeypatch.setattr(final, "prereg_committed", lambda p: True)
    with pytest.raises(SystemExit, match="--reason"):
        final.main()


def test_final_refuses_without_committed_prereg(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["11_final.py", "--reason", "x"])
    monkeypatch.setattr(final, "prereg_committed", lambda p: False)
    with pytest.raises(SystemExit, match="PREREG"):
        final.main()


def test_holm_matches_hand_computation():
    assert np.allclose(sig.holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])


def test_analyse_verdicts(tmp_path):
    rng = np.random.default_rng(0)
    users = np.arange(400)
    base = rng.random(400) * 0.1
    models = {"BPR-MF": base, "MostPopular": base * 0.5, "GMF": base, "MLP": base,
              "NeuMF-Scratch": base, "NeuMF-Pretrained": base + 0.05}
    for seed in (42, 2024):
        d = tmp_path / f"seed{seed}"
        d.mkdir()
        pd.DataFrame([{"model": m, "seed": seed, "user": u, "NDCG@10": v[u]} for m, v in models.items() for u in users]
                     ).to_csv(d / "results_per_user.csv", index=False)
    seeds, summary, res = sig.analyse(tmp_path)
    assert seeds == [42, 2024]
    v = res.set_index(["A", "B"])["verdict"]
    assert v[("NeuMF-Pretrained", "BPR-MF")] == "A tốt hơn"
    assert v[("NeuMF-Scratch", "GMF")] == "không khác biệt có ý nghĩa"
