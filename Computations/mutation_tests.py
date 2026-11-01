#!/usr/bin/env python3
"""Destructive release and transcript-semantic mutations for P01B2A.1.3."""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

from freeze_wrapper import validate_archive_namespace

SOURCE = Path(__file__).resolve().parents[1]


def _manifest(root: Path) -> None:
    rows = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == "SOURCE_MANIFEST.sha256":
            continue
        rows.append(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  "
            f"{path.relative_to(root).as_posix()}"
        )
    (root / "SOURCE_MANIFEST.sha256").write_text(
        "\n".join(rows) + "\n", encoding="utf-8"
    )


def _append(path: Path) -> None:
    with path.open("ab") as handle:
        handle.write(b"\nMUTATION\n")


def _replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"mutation target not unique in {path}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _mutate_json(path: Path, transform) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    transform(data)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _semantic_scan_count(root: Path) -> None:
    path = root / "evidence/p01b2_equal_radius_rho1_audit.json"
    _mutate_json(path, lambda data: data["joint_scan"].__setitem__(
        "joint_necessary_condition_points_tested", 249574
    ))
    _manifest(root)


def _semantic_correction_count(root: Path) -> None:
    path = root / "evidence/p01b2_equal_radius_rho1_audit.json"
    _mutate_json(path, lambda data: data["joint_scan"]["legacy_trace_algorithm_correction"].__setitem__(
        "count", 26
    ))
    _manifest(root)


def _semantic_scope(root: Path) -> None:
    path = root / "evidence/p01b2_equal_radius_rho1_audit.json"
    _mutate_json(path, lambda data: data.__setitem__(
        "classification", "complete equal-radius branch audit"
    ))
    _manifest(root)


def _semantic_memory(root: Path) -> None:
    path = root / "docs/PROJECT_MEMORY_ROADMAP_v3_TOP00_G01_P01B2A_1_3.md"
    _replace(path, "P01C-CURV remains blocked", "P01C-CURV is open")
    _manifest(root)


def _active_control_character(root: Path) -> None:
    path = root / "docs/P01B2A_1_3_RELEASE_HARNESS_HOTFIX_LEDGER.md"
    with path.open("ab") as handle:
        handle.write(b"\r")
    _manifest(root)


def _old_p01b1_ancestor(root: Path) -> None:
    active = root / (
        "provenance/ancestors/"
        "KKK_LL_P01B_1_3_Fully_Anisotropic_Homogeneous_Full_Rank_Regularity_No_Go_Release_Harness_Resealed.zip"
    )
    old = root / (
        "provenance/ancestors/historical_hold/"
        "KKK_LL_P01B_1_Fully_Anisotropic_Homogeneous_Full_Rank_Regularity_No_Go_Complete.zip"
    )
    shutil.copyfile(old, active)
    _manifest(root)


def _ancestry_disposition(root: Path) -> None:
    path = root / "provenance/source_ledger.md"
    _replace(path, "P01B.1 scoped scientific theorem: accepted.",
             "P01B.1 scoped scientific theorem: rejected.")
    _manifest(root)


def _source_replace(root: Path, relative: str, old: str, new: str) -> None:
    _replace(root / relative, old, new)
    _manifest(root)


def _transcript_semantic_matrix() -> None:
    """Independently require every decisive stored transcript field to fail closed."""
    mutations = (
        ("outer_status", lambda x: x.__setitem__("status", "FAIL")),
        ("tree_unchanged", lambda x: x.__setitem__("tree_unchanged", False)),
        ("full_status", lambda x: x["stages"]["full_verifier"]["result"].__setitem__("status", "FAIL")),
        ("full_manifest_count", lambda x: x["stages"]["full_verifier"]["result"].__setitem__("manifest_files", 69)),
        ("optimized_status", lambda x: x["stages"]["optimized_python_fast_verifier"]["result"].__setitem__("status", "FAIL")),
        ("evidence_identity", lambda x: x["stages"]["evidence_regeneration"].__setitem__("byte_identical_files", 2)),
        ("evidence_samples", lambda x: x["stages"]["evidence_regeneration"]["result"].__setitem__("samples", 3_999_999)),
        ("evidence_trace_count", lambda x: x["stages"]["evidence_regeneration"]["result"].__setitem__("trace_inertia_pass_points", 249_572)),
        ("evidence_stable_count", lambda x: x["stages"]["evidence_regeneration"]["result"].__setitem__("stable_joint_points_found", 1)),
        ("presentation_identity", lambda x: x["stages"]["presentation_rebuild"].__setitem__("byte_identical_files", 2)),
        ("presentation_pages", lambda x: x["stages"]["presentation_rebuild"]["result"].__setitem__("pdf_pages", 11)),
        ("presentation_pdf_hash", lambda x: x["stages"]["presentation_rebuild"]["result"].__setitem__("pdf_sha256", "0" * 64)),
        ("negative_count", lambda x: x["stages"]["negative_tests"]["result"].__setitem__("negative_tests", 42)),
        ("mutation_count", lambda x: x["stages"]["mutation_tests"]["result"].__setitem__("mutation_tests", 25)),
        ("archive_identity", lambda x: x["stages"]["deterministic_archive_rebuild"].__setitem__("byte_identical", False)),
        ("candidate_entries", lambda x: x.__setitem__("candidate_archive_entries", 82)),
        ("candidate_content_hash", lambda x: x.__setitem__("candidate_content_sha256", "1" * 64)),
        ("stage_content_hash", lambda x: x["stages"]["deterministic_archive_rebuild"].__setitem__("content_sha256", "2" * 64)),
        ("coordinated_content_hash", lambda x: (
            x.__setitem__("candidate_content_sha256", "3" * 64),
            x["stages"]["deterministic_archive_rebuild"].__setitem__("content_sha256", "3" * 64),
            x["stages"]["deterministic_archive_rebuild"]["result_a"].__setitem__("content_sha256", "3" * 64),
            x["stages"]["deterministic_archive_rebuild"]["result_b"].__setitem__("content_sha256", "3" * 64),
        )),
        ("coordinated_content_bytes", lambda x: (
            x.__setitem__("candidate_content_bytes", x["candidate_content_bytes"] + 1),
            x["stages"]["deterministic_archive_rebuild"].__setitem__("content_bytes", x["stages"]["deterministic_archive_rebuild"]["content_bytes"] + 1),
            x["stages"]["deterministic_archive_rebuild"]["result_a"].__setitem__("content_bytes", x["stages"]["deterministic_archive_rebuild"]["result_a"]["content_bytes"] + 1),
            x["stages"]["deterministic_archive_rebuild"]["result_b"].__setitem__("content_bytes", x["stages"]["deterministic_archive_rebuild"]["result_b"]["content_bytes"] + 1),
        )),
        ("candidate_name", lambda x: x.__setitem__("candidate_archive", "arbitrary.zip")),
    )
    for name, transform in mutations:
        with tempfile.TemporaryDirectory(prefix=f"p01b2a13-transcript-{name}-") as temporary:
            target = Path(temporary) / SOURCE.name
            shutil.copytree(SOURCE, target)
            path = target / "FREEZE_TRANSCRIPT.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            transform(data)
            path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            _manifest(target)
            completed = subprocess.run(
                [sys.executable, "-B", str(target / "verification/verify_release.py"), "--fast"],
                cwd=target, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, check=False,
            )
            if completed.returncode == 0:
                raise RuntimeError(f"transcript semantic mutation escaped verification: {name}")


def require_unmodified_baselines() -> None:
    """Require a clean copied tree and clean archive namespace to pass first."""
    with tempfile.TemporaryDirectory(prefix="p01b2a13-baseline-") as temporary:
        temporary_path = Path(temporary)
        target = temporary_path / SOURCE.name
        shutil.copytree(SOURCE, target)
        completed = subprocess.run(
            [sys.executable, "-B", str(target / "verification/verify_release.py"), "--fast"],
            cwd=target, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"unmodified copied specimen failed:\n{completed.stdout}")
        archive = temporary_path / "baseline.zip"
        built = subprocess.run(
            [sys.executable, "-B", str(target / "verification/build_archive.py"),
             "--output", str(archive)],
            cwd=target, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, check=False,
        )
        if built.returncode != 0:
            raise RuntimeError(f"unmodified archive baseline failed:\n{built.stdout}")
        validate_archive_namespace(archive)


def reject_extra_outer_member() -> None:
    with tempfile.TemporaryDirectory(prefix="p01b2a13-outer-member-") as temporary:
        archive = Path(temporary) / "mutated.zip"
        completed = subprocess.run(
            [sys.executable, "-B", str(SOURCE / "verification/build_archive.py"),
             "--output", str(archive)],
            cwd=SOURCE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(f"archive construction failed:\n{completed.stdout}")
        with zipfile.ZipFile(archive, "a", compression=zipfile.ZIP_DEFLATED) as handle:
            handle.writestr("UNAUTHENTICATED_TOP_LEVEL.txt", b"mutation")
        try:
            validate_archive_namespace(archive)
        except RuntimeError:
            return
        raise RuntimeError("extra outer archive member survived namespace validation")


def run() -> int:
    require_unmodified_baselines()
    cases = (
        ("manifested_file_byte", lambda root: _append(root / "evidence/g01_exact.json"), False),
        ("unexpected_file", lambda root: (root / "UNEXPECTED.txt").write_text("x", encoding="utf-8"), False),
        ("missing_file", lambda root: (root / "contracts/top00_contract.json").unlink(), False),
        ("missing_manifest", lambda root: (root / "SOURCE_MANIFEST.sha256").unlink(), False),
        ("missing_manifest_optimized", lambda root: (root / "SOURCE_MANIFEST.sha256").unlink(), True),
        ("semantic_scan_count", _semantic_scan_count, False),
        ("semantic_scan_count_optimized_python", _semantic_scan_count, True),
        ("semantic_correction_count", _semantic_correction_count, False),
        ("semantic_rho_scope", _semantic_scope, False),
        ("semantic_memory", _semantic_memory, False),
        ("active_control_character", _active_control_character, False),
        ("old_fail_open_p01b1_ancestor", _old_p01b1_ancestor, False),
        ("ancestry_disposition", _ancestry_disposition, False),
        ("semantic_roadmap", lambda root: (_append(root / "provenance/roadmap_v3/KKK_LL_Master_Roadmap_P01B1_NoGo_v3.svg"), _manifest(root)), False),
        ("semantic_pdf", lambda root: (_append(root / "docs/TOP00_G01_P01B2_CURV_Stage_A_1_2.pdf"), _manifest(root)), False),
        ("trace_block_dimensions", lambda root: _source_replace(
            root, "calculations/p01b2_equal_radius_search.py",
            "BLOCK_DIMENSIONS = np.array([3.0, 4.0, 4.0, 4.0])",
            "BLOCK_DIMENSIONS = np.array([4.0, 4.0, 4.0, 4.0])",
        ), False),
        ("trace_normalization_removed", lambda root: _source_replace(
            root, "calculations/p01b2_equal_radius_search.py",
            "/ SQRT_BLOCK_DIMENSIONS[None, :]",
            "* SQRT_BLOCK_DIMENSIONS[None, :]",
        ), False),
        ("einstein_trace_oracle", lambda root: _source_replace(
            root, "calculations/p01b2_equal_radius_search.py",
            "expected = np.array([-1.0, -1.0, -1.0, 14.0])",
            "expected = np.array([-1.0, -1.0, -1.0, 13.0])",
        ), False),
        ("drop_alpha7_local_order", lambda root: _source_replace(
            root, "calculations/p01b2_curved_doubleform.py",
            "MAX_LOCAL_ORDER = 7", "MAX_LOCAL_ORDER = 6",
        ), False),
        ("introduce_local_alpha8", lambda root: _source_replace(
            root, "calculations/p01b2_curved_doubleform.py",
            "MAX_LOCAL_ORDER = 7", "MAX_LOCAL_ORDER = 8",
        ), False),
        ("alpha7_nontrace_coefficient", lambda root: _source_replace(
            root, "calculations/p01b2_equal_radius_search.py",
            "-4459069440", "-4459069439",
        ), False),
        ("mode_multiplicity_ledger", lambda root: _source_replace(
            root, "calculations/p01b2_equal_radius_search.py",
            "NONTRACE_MULTIPLICITIES = (5, 18, 36, 48, 9)",
            "NONTRACE_MULTIPLICITIES = (5, 18, 36, 48, 8)",
        ), False),
        ("exact_derivative_method", lambda root: _source_replace(
            root, "calculations/p01b2_equal_radius_search.py",
            'DERIVATIVE_METHOD = "exact_double_form_product_rule"',
            'DERIVATIVE_METHOD = "unverified_finite_difference"',
        ), False),
        ("fixed_point_ds4_factor", lambda root: _source_replace(
            root, "calculations/p01b2_curved_doubleform.py",
            "ds4 = (Fraction(1), 12 * x, 24 * x * x)",
            "ds4 = (Fraction(1), 12 * x, 23 * x * x)",
        ), False),
        ("topological_regression_removed", lambda root: _source_replace(
            root, "calculations/p01b2_curved_doubleform.py",
            "def topological_order8_regression()", "def removed_order8_regression()",
        ), False),
    )
    for name, mutate, optimized in cases:
        with tempfile.TemporaryDirectory(prefix=f"p01b2a1_{name}_") as temporary:
            target = Path(temporary) / SOURCE.name
            shutil.copytree(SOURCE, target)
            mutate(target)
            command = [sys.executable]
            if optimized:
                command.append("-O")
            command.extend([
                "-B", str(target / "verification/verify_release.py"), "--fast"
            ])
            completed = subprocess.run(
                command,
                cwd=target,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
            if completed.returncode == 0:
                raise RuntimeError(f"mutation escaped verification: {name}")
    _transcript_semantic_matrix()
    reject_extra_outer_member()
    return len(cases) + 2


if __name__ == "__main__":
    print(json.dumps({
        "status": "PASS", "mutation_tests": run(), "unmodified_baselines": 2
    }, sort_keys=True))
