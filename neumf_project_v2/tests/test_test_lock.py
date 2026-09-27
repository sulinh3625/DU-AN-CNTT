"""Khoá tập test: --final cần PREREG.md đã commit; mỗi lần đánh giá test ghi test_access_log.csv."""
from __future__ import annotations

import csv
import importlib

import pytest

from src.utils.io import log_test_access, prereg_committed

run_experiment = importlib.import_module("scripts.03_run_experiment")


def test_prereg_missing_means_not_committed(tmp_path):
    assert prereg_committed(tmp_path / "PREREG.md") is False


def test_final_refused_without_committed_prereg(monkeypatch, tmp_path):
    monkeypatch.setattr(run_experiment, "PREREG_PATH", tmp_path / "PREREG.md")
    with pytest.raises(SystemExit, match="--final bị khoá"):
        run_experiment.run("configs/hm500k_global.yaml", final=True, reason="thử")


def test_final_requires_reason(monkeypatch):
    monkeypatch.setattr(run_experiment, "prereg_committed", lambda p: True)
    with pytest.raises(SystemExit, match="--reason"):
        run_experiment.run("configs/hm500k_global.yaml", final=True, reason=" ")


def test_log_test_access_appends_rows(tmp_path):
    log = tmp_path / "audit" / "test_access_log.csv"
    prov = {"git_commit": "abc", "git_dirty": False, "config_hash": "h1", "config_path": "c.yaml"}
    log_test_access(log, "run1", prov, ["GMF", "NeuMF"], "lần 1")
    log_test_access(log, "run2", prov, ["MLP"], "lần 2")
    rows = list(csv.DictReader(log.open(encoding="utf-8")))
    assert [r["run_tag"] for r in rows] == ["run1", "run2"]
    assert rows[0]["models"] == "GMF;NeuMF" and rows[0]["config_hash"] == "h1" and rows[1]["reason"] == "lần 2"
