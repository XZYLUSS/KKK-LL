#!/usr/bin/env python3
"""Build a deterministic ZIP of the authenticated P01B2A.1.3 root."""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZIP_TIMESTAMP = (2026, 8, 10, 0, 0, 0)


def payload_binding(files: list[Path]) -> tuple[str, int]:
    excluded = {"SOURCE_MANIFEST.sha256", "FREEZE_TRANSCRIPT.json"}
    digest = hashlib.sha256()
    total = 0
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        if relative in excluded:
            continue
        size = path.stat().st_size
        total += size
        digest.update(
            relative.encode("utf-8") + b"\0"
            + hashlib.sha256(path.read_bytes()).hexdigest().encode("ascii") + b"\0"
        )
    return digest.hexdigest(), total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError("archive output must lie outside the release root")
    output.parent.mkdir(parents=True, exist_ok=True)
    files = [path for path in sorted(ROOT.rglob("*")) if path.is_file()]
    if any("__pycache__" in path.parts or path.suffix == ".pyc" for path in files):
        raise RuntimeError("bytecode artifacts are forbidden")
    content_sha256, content_bytes = payload_binding(files)
    with zipfile.ZipFile(
        output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for path in files:
            relative = Path(ROOT.name) / path.relative_to(ROOT)
            info = zipfile.ZipInfo(relative.as_posix(), ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            executable = path.suffix == ".py"
            info.external_attr = ((0o100755 if executable else 0o100644) & 0xFFFF) << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    print(json.dumps({
        "status": "PASS",
        "files": len(files),
        "root": ROOT.name,
        "content_sha256": content_sha256,
        "content_bytes": content_bytes,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
