from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict
from pathlib import Path


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def run_provenance(cfg, config_path: str | Path, cwd: str | Path | None = None) -> dict:
    """Truy vết một lần chạy: hash của config đã nạp (sau khi điền mặc định) + git commit/dirty."""
    blob = json.dumps(asdict(cfg), sort_keys=True, default=str, ensure_ascii=False)

    def git(*args):
        try:
            return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=10).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return ""

    return {
        "config_path": str(config_path),
        "config_hash": hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16],
        "git_commit": git("rev-parse", "HEAD") or None,
        "git_dirty": bool(git("status", "--porcelain", "--untracked-files=no")),
    }


def write_json(path: str | Path, payload):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
