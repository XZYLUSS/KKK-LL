#!/usr/bin/env python3
"""Fresh-extraction and complete deterministic freeze replay for P01B2A.1.3."""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import stat
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256(path)
        for path in sorted(root.rglob("*")) if path.is_file()
    }


def run_json(command: list[str], cwd: Path) -> tuple[dict, float]:
    started = time.monotonic()
    completed = subprocess.run(
        command, cwd=cwd, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=False,
    )
    elapsed = time.monotonic() - started
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"non-JSON command output: {' '.join(command)}\n{completed.stdout}"
        ) from error
    return value, elapsed


def internal_replay(root: Path) -> dict:
    before = tree_hashes(root)
    stages = {}

    verify, elapsed = run_json([
        sys.executable, "-B", str(root / "verification/verify_release.py")
    ], root)
    stages["full_verifier"] = {"seconds": elapsed, "result": verify}

    optimized, elapsed = run_json([
        sys.executable, "-O", "-B",
        str(root / "verification/verify_release.py"), "--fast"
    ], root)
    stages["optimized_python_fast_verifier"] = {
        "seconds": elapsed, "result": optimized
    }

    with tempfile.TemporaryDirectory(prefix="p01b2a13-evidence-") as temporary:
        output = Path(temporary)
        regenerated, elapsed = run_json([
            sys.executable, "-B", str(root / "verification/regenerate_evidence.py"),
            "--output-dir", str(output), "--samples", "4000000",
        ], root)
        expected = root / "evidence"
        files = (
            "g01_exact.json",
            "p01b2_equal_radius_rho1_audit.json",
            "p01b2_full_acceleration_spectrum.json",
        )
        for name in files:
            if (output / name).read_bytes() != (expected / name).read_bytes():
                raise RuntimeError(f"regenerated evidence differs: {name}")
        stages["evidence_regeneration"] = {
            "seconds": elapsed, "result": regenerated, "byte_identical_files": len(files)
        }

    with tempfile.TemporaryDirectory(prefix="p01b2a13-presentation-") as temporary:
        output = Path(temporary)
        rebuilt, elapsed = run_json([
            sys.executable, "-B", str(root / "verification/build_presentation.py"),
            "--output-dir", str(output),
        ], root)
        comparisons = (
            (output / "TOP00_G01_P01B2_CURV_Stage_A_1_2.html", root / "docs/TOP00_G01_P01B2_CURV_Stage_A_1_2.html"),
            (output / "TOP00_G01_P01B2_CURV_Stage_A_1_2.pdf", root / "docs/TOP00_G01_P01B2_CURV_Stage_A_1_2.pdf"),
            (output / "presentation_contract.json", root / "contracts/presentation_contract.json"),
        )
        for generated, stored in comparisons:
            if generated.read_bytes() != stored.read_bytes():
                raise RuntimeError(f"rebuilt presentation differs: {stored.name}")
        stages["presentation_rebuild"] = {
            "seconds": elapsed, "result": rebuilt,
            "byte_identical_files": len(comparisons),
        }

    negative, elapsed = run_json([
        sys.executable, "-B", str(root / "verification/negative_tests.py")
    ], root)
    stages["negative_tests"] = {"seconds": elapsed, "result": negative}

    mutations, elapsed = run_json([
        sys.executable, "-B", str(root / "verification/mutation_tests.py")
    ], root)
    stages["mutation_tests"] = {"seconds": elapsed, "result": mutations}

    with tempfile.TemporaryDirectory(prefix="p01b2a13-archive-build-") as temporary:
        output = Path(temporary)
        archive_a = output / "build_a.zip"
        archive_b = output / "build_b.zip"
        built_a, elapsed_a = run_json([
            sys.executable, "-B", str(root / "verification/build_archive.py"),
            "--output", str(archive_a),
        ], root)
        built_b, elapsed_b = run_json([
            sys.executable, "-B", str(root / "verification/build_archive.py"),
            "--output", str(archive_b),
        ], root)
        if archive_a.read_bytes() != archive_b.read_bytes():
            raise RuntimeError("deterministic archive rebuild differs")
        stages["deterministic_archive_rebuild"] = {
            "seconds": elapsed_a + elapsed_b,
            "result_a": built_a,
            "result_b": built_b,
            "byte_identical": True,
            "content_sha256": built_a["content_sha256"],
            "content_bytes": built_a["content_bytes"],
            "entries": built_a["files"],
        }

    after = tree_hashes(root)
    if before != after:
        raise RuntimeError("verification mutated the authenticated release tree")
    return {
        "status": "PASS",
        "root": root.name,
        "tree_files": len(before),
        "tree_unchanged": True,
        "stages": stages,
    }


def validate_archive_namespace(archive: Path) -> list[str]:
    """Authenticate the entire outer ZIP namespace before extraction."""
    expected_root = "KKK_LL_TOP00_G01_P01B2A_1_3"
    with zipfile.ZipFile(archive) as handle:
        infos = handle.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)):
            raise RuntimeError("archive contains duplicate paths")
        for item in infos:
            path = Path(item.filename)
            mode = (item.external_attr >> 16) & 0xFFFF
            if (not item.filename or item.is_dir() or item.flag_bits & 0x1
                    or path.is_absolute() or ".." in path.parts
                    or stat.S_ISLNK(mode) or not path.parts
                    or path.parts[0] != expected_root):
                raise RuntimeError(f"unsafe or unauthenticated archive member: {item.filename}")
        manifest_name = f"{expected_root}/SOURCE_MANIFEST.sha256"
        if manifest_name not in names:
            raise RuntimeError("rooted archive manifest is missing")
        payloads = set()
        for line in handle.read(manifest_name).decode("utf-8").splitlines():
            if not line.strip():
                continue
            parts = line.split("  ", 1)
            if len(parts) != 2:
                raise RuntimeError("malformed rooted archive manifest row")
            payloads.add(parts[1])
        expected = {manifest_name} | {f"{expected_root}/{name}" for name in payloads}
        if set(names) != expected:
            raise RuntimeError("outer archive namespace differs from the rooted manifest set")
        if handle.testzip() is not None:
            raise RuntimeError("archive CRC failure")
    return names


def safe_extract_and_replay(archive: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="p01b2a13-fresh-extract-") as temporary:
        destination = Path(temporary)
        names = validate_archive_namespace(archive)
        with zipfile.ZipFile(archive) as handle:
            handle.extractall(destination)
        roots = list(destination.iterdir())
        if len(roots) != 1 or not roots[0].is_dir() or roots[0].name != "KKK_LL_TOP00_G01_P01B2A_1_3":
            raise RuntimeError("archive must contain exactly the declared release root")
        replay = internal_replay(roots[0])
        return {
            "status": "PASS",
            "archive": archive.name,
            "archive_sha256": sha256(archive),
            "archive_entries": len(names),
            "fresh_extraction": True,
            "replay": replay,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    args = parser.parse_args()
    result = safe_extract_and_replay(args.archive.resolve())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
