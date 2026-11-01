#!/usr/bin/env python3
"""Deterministically regenerate all active P01B2A.1.2 scientific evidence files."""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "calculations"))

import g01_product_geometry as g01
import p01b2_equal_radius_search as search


def encoded(value: dict) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=4_000_000)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    g01_result = g01.exact_self_check()
    audit, spectrum = search.generate_result(args.samples)
    outputs = {
        "g01_exact.json": g01_result,
        "p01b2_equal_radius_rho1_audit.json": audit,
        "p01b2_full_acceleration_spectrum.json": spectrum,
    }
    for name, value in outputs.items():
        (args.output_dir / name).write_text(encoded(value), encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "samples": args.samples,
        "files": sorted(outputs),
        "trace_inertia_pass_points": audit["joint_scan"]["trace_inertia_pass_points"],
        "stable_joint_points_found": audit["joint_scan"]["stable_joint_points_found"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
