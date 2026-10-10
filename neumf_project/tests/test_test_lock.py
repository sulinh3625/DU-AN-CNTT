"""Khoá tập kiểm thử (src/utils/io.py, dùng trong scripts/23_final_v2.py): kế hoạch phải đã commit; mỗi lần chấm tập
kiểm thử ghi một dòng audit/test_access_log.csv. Phần còn lại của khoá: tests/test_v2_final.py."""
from __future__ import annotations

import csv

from src.utils.io import log_test_access, prereg_committed


def test_prereg_missing_means_not_committed(tmp_path):
    assert prereg_committed(tmp_path / "PREREG_v2.md") is False


def test_log_test_access_appends_rows(tmp_path):
    log = tmp_path / "audit" / "test_access_log.csv"
    prov = {"git_commit": "abc", "git_dirty": False, "config_hash": "h1", "config_path": "c.yaml"}
    log_test_access(log, "run1", prov, ["GMF", "NeuMF"], "lần 1")
    log_test_access(log, "run2", prov, ["MLP"], "lần 2")
    rows = list(csv.DictReader(log.open(encoding="utf-8")))
    assert [r["run_tag"] for r in rows] == ["run1", "run2"]
    assert rows[0]["models"] == "GMF;NeuMF" and rows[0]["config_hash"] == "h1" and rows[1]["reason"] == "lần 2"
