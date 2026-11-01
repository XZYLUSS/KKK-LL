"""Shared fail-closed release-integrity predicates."""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import hashlib
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def payload_tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    excluded = {"SOURCE_MANIFEST.sha256", "FREEZE_TRANSCRIPT.json"}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if not path.is_file() or relative in excluded:
            continue
        digest.update(
            relative.encode("utf-8") + b"\0" + sha256(path).encode("ascii") + b"\0"
        )
    return digest.hexdigest()


def payload_tree_bytes(root: Path) -> int:
    """Byte count of the canonically bound, non-self-referential payload."""
    excluded = {"SOURCE_MANIFEST.sha256", "FREEZE_TRANSCRIPT.json"}
    return sum(
        path.stat().st_size
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.relative_to(root).as_posix() not in excluded
    )


def active_text_control_characters(root: Path) -> dict[str, list[int]]:
    bad: dict[str, list[int]] = {}
    active_prefixes = (
        "calculations/", "contracts/", "docs/", "verification/",
        "provenance/source_ledger.md", "provenance/P01B1_ANCESTRY_SUPERSESSION.md",
        "FREEZE_TRANSCRIPT.json",
    )
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if not any(relative == prefix or relative.startswith(prefix) for prefix in active_prefixes):
            continue
        if path.suffix.lower() in {".pdf", ".png", ".zip", ".pyc"}:
            continue
        positions = [
            index for index, byte in enumerate(path.read_bytes())
            if byte < 32 and byte not in (9, 10)
        ]
        if positions:
            bad[relative] = positions
    return bad
