from __future__ import annotations

import json
import subprocess
from pathlib import Path


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def prereg_committed(prereg_path: str | Path) -> bool:
    """PREREG.md phải nằm trong git (đã commit) trước lần đánh giá test đầu tiên."""
    p = Path(prereg_path)
    if not p.exists():
        return False
    res = subprocess.run(["git", "ls-files", "--error-unmatch", p.name], cwd=p.parent, capture_output=True, text=True)
    dirty = subprocess.run(["git", "status", "--porcelain", "--", p.name], cwd=p.parent, capture_output=True, text=True)
    return res.returncode == 0 and not dirty.stdout.strip()


def log_test_access(log_path: str | Path, run_tag: str, provenance: dict, models: list[str], reason: str) -> None:
    """Ghi 1 dòng mỗi lần đánh giá trên tập test (khoá tập test)."""
    import csv
    from datetime import datetime

    p = Path(log_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    new = not p.exists()
    with p.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time", "git_commit", "git_dirty", "config_hash", "config_path", "run_tag", "models", "reason"])
        w.writerow([datetime.now().isoformat(timespec="seconds"), provenance.get("git_commit"), provenance.get("git_dirty"),
                    provenance.get("config_hash"), provenance.get("config_path"), run_tag, ";".join(models), reason])


def write_json(path: str | Path, payload):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
