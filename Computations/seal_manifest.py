#!/usr/bin/env python3
"""Regenerate the exact release-tree SHA-256 manifest."""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "SOURCE_MANIFEST.sha256"


def main() -> int:
    rows = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == MANIFEST:
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            raise RuntimeError(f"bytecode artifact forbidden: {path}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(f"{digest}  {path.relative_to(ROOT).as_posix()}")
    MANIFEST.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "manifest_files": len(rows)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
