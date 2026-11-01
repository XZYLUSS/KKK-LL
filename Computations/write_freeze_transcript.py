#!/usr/bin/env python3
"""Write the authenticated P01B2A.1.3 archive-level freeze transcript."""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import json
from pathlib import Path

import freeze_wrapper
from release_integrity import payload_tree_bytes, payload_tree_sha256

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    args = parser.parse_args()
    replay = freeze_wrapper.safe_extract_and_replay(args.archive.resolve())
    record = {
        "schema": "KKK-LL-P01B2A.1.3-Freeze-Transcript-v3",
        "release_revision": "TOP00-G01-P01B2A.1.3",
        "status": "PASS",
        "replay_mode": "archive-level fresh extraction",
        "candidate_archive": replay["archive"],
        "candidate_content_sha256": payload_tree_sha256(ROOT),
        "candidate_content_bytes": payload_tree_bytes(ROOT),
        "candidate_archive_entries": replay["archive_entries"],
        "payload_tree_sha256": payload_tree_sha256(ROOT),
        "runtime": json.loads((ROOT / "verification/runtime_lock.json").read_text(encoding="utf-8")),
        "tree_unchanged": replay["replay"]["tree_unchanged"],
        "stages": replay["replay"]["stages"],
        "outer_final_archive_sha256": "recorded in the external final attestation to avoid a self-hash cycle",
    }
    (ROOT / "FREEZE_TRANSCRIPT.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "status": "PASS",
        "transcript": "FREEZE_TRANSCRIPT.json",
        "payload_tree_sha256": record["payload_tree_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
