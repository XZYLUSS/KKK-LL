#!/usr/bin/env python3
"""Explicit fail-closed verifier for the P01B2A.1.3 resealed release."""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import ast
import hashlib
import json
import math
import platform
import stat
import subprocess
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import pypdf
from pypdf import PdfReader

from release_integrity import (
    active_text_control_characters,
    payload_tree_bytes,
    payload_tree_sha256,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "SOURCE_MANIFEST.sha256"


class VerificationError(RuntimeError):
    pass


def check(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def first_version_line(args: list[str]) -> str:
    completed = subprocess.run(args, text=True, capture_output=True, check=True)
    return (completed.stdout or completed.stderr).splitlines()[0].strip()


def verify_runtime() -> int:
    lock = json.loads((ROOT / "verification/runtime_lock.json").read_text(encoding="utf-8"))
    actual = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pypdf": pypdf.__version__,
        "pandoc": first_version_line(["pandoc", "--version"]).removeprefix("pandoc "),
        "pdflatex": first_version_line(["pdflatex", "--version"]),
        "pdfinfo": first_version_line(["pdfinfo", "-v"]).removeprefix("pdfinfo version "),
        "pdftoppm": first_version_line(["pdftoppm", "-v"]).removeprefix("pdftoppm version "),
    }
    check(platform.python_implementation() == "CPython", "CPython runtime is required")
    for name, value in actual.items():
        check(lock.get(name) == value, f"runtime mismatch for {name}: {value!r}")
    check(lock.get("source_date_epoch") == 1786320000, "SOURCE_DATE_EPOCH lock changed")
    check(lock.get("bytecode_policy") == "disabled for verification", "bytecode policy changed")
    return len(actual) + 2


def verify_manifest() -> int:
    check(MANIFEST.is_file(), "SOURCE_MANIFEST.sha256 is required")
    expected = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split("  ", 1)
        check(len(parts) == 2, "malformed manifest row")
        checksum, relative = parts
        check(relative not in expected, f"duplicate manifest path: {relative}")
        check(len(checksum) == 64 and all(c in "0123456789abcdef" for c in checksum),
              f"malformed manifest checksum: {relative}")
        expected[relative] = checksum
    actual = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and path != MANIFEST
    }
    check(actual == set(expected),
          f"manifest tree mismatch missing={sorted(set(expected)-actual)} extra={sorted(actual-set(expected))}")
    for relative, checksum in expected.items():
        path = ROOT / relative
        check(not path.is_symlink(), f"manifested symbolic link forbidden: {relative}")
        check(sha256(path) == checksum, f"manifest hash mismatch: {relative}")
    check(not any(
        "__pycache__" in path.parts or path.suffix == ".pyc"
        for path in ROOT.rglob("*")
    ), "bytecode artifacts are forbidden")
    return len(expected)


def verify_p01b1_ancestor_semantics() -> None:
    archive = ROOT / (
        "provenance/ancestors/"
        "KKK_LL_P01B_1_3_Fully_Anisotropic_Homogeneous_Full_Rank_Regularity_No_Go_Release_Harness_Resealed.zip"
    )
    with tempfile.TemporaryDirectory(prefix="p01b11-semantic-gate-") as temporary:
        destination = Path(temporary)
        with zipfile.ZipFile(archive) as handle:
            infos = handle.infolist()
            names = [item.filename for item in infos]
            check(len(names) == len(set(names)), "P01B.1.3 ancestor has duplicate paths")
            for item in infos:
                path = Path(item.filename)
                mode = (item.external_attr >> 16) & 0xFFFF
                check(not path.is_absolute() and ".." not in path.parts,
                      f"unsafe P01B.1.3 path: {item.filename}")
                check(not stat.S_ISLNK(mode), f"P01B.1.3 symlink forbidden: {item.filename}")
                check(not (item.flag_bits & 0x1), f"encrypted P01B.1.3 member: {item.filename}")
            check(handle.testzip() is None, "P01B.1.3 CRC failure")
            handle.extractall(destination)

        manifest = destination / "SOURCE_MANIFEST.sha256"
        check(manifest.is_file(), "P01B.1.3 mandatory manifest missing")
        expected = {}
        for line in manifest.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            parts = line.split("  ", 1)
            check(len(parts) == 2, "P01B.1.3 malformed manifest row")
            digest, relative = parts
            check(relative not in expected, "P01B.1.3 duplicate manifest path")
            expected[relative] = digest
        actual = {
            path.relative_to(destination).as_posix()
            for path in destination.rglob("*")
            if path.is_file() and path != manifest
        }
        check(set(expected) == actual, "P01B.1.3 exact-tree mismatch")
        check(not any(
            "__pycache__" in path.parts or path.suffix == ".pyc"
            for path in destination.rglob("*")
        ), "P01B.1.3 contains bytecode residue")
        for relative, digest in expected.items():
            check(sha256(destination / relative) == digest,
                  f"P01B.1.3 manifest mismatch: {relative}")

        record = json.loads((destination / "RESEAL_RECORD.json").read_text(encoding="utf-8"))
        check(record["release_revision"] == "P01B.1.3", "P01B.1.3 reseal record changed")
        transcript = json.loads((destination / "FREEZE_TRANSCRIPT.json").read_text(encoding="utf-8"))
        check(transcript["status"] == "PASS" and transcript["release_revision"] == "P01B.1.3",
              "P01B.1.3 transcript invalid")
        completed = subprocess.run(
            [sys.executable, "-B", str(destination / "verify_P01B.py")],
            cwd=destination, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, check=False,
        )
        check(completed.returncode == 0,
              f"P01B.1.3 semantic verifier failed: {completed.stdout}\n{completed.stderr}")
        result = json.loads(completed.stdout)
        check(result == {
            "status": "PASS", "release_revision": "P01B.1.3",
            "scientific_calculation": "P01B.1", "runtime_checks": 10,
            "checks": 295, "manifest_files": 33,
            "transcript_semantic_checks": 18,
        }, "P01B.1.3 semantic verifier result changed")


def verify_provenance() -> int:
    expected = {
        "provenance/roadmap_v3/KKK_LL_Dependency_Matrix_P01B1_NoGo_v3.csv": "b3965b03a0373b11a086dcbc6be4b126fddd5868964b538342a0a83fe908c0c8",
        "provenance/roadmap_v3/KKK_LL_Dependency_Matrix_P01B1_NoGo_v3.md": "3f7822963a8ec5b4410d5c89a6b7aaae4cabdc079122204e97957eb8a20d782b",
        "provenance/roadmap_v3/KKK_LL_Dependency_Registry_P01B1_NoGo_v3.json": "5df094e221c70465c5641e2682b198b2988eb73f4140efaf41f6a393cfda53ca",
        "provenance/roadmap_v3/KKK_LL_Master_Roadmap_P01B1_NoGo_v3.svg": "6a578d48d0d4cdfee9a56c87bff414682e61bdc321d9344dd27e2348fd15bb1f",
        "provenance/roadmap_v3/KKK_LL_Master_Roadmap_P01B1_NoGo_v3.png": "b2c79072281539748ebb6829f282213ad6c4cfe7e808381a1d71b8b00c28870a",
        "provenance/roadmap_v3/KKK_LL_Master_Roadmap_and_Dependency_Matrix_P01B1_NoGo_v3.html": "d9cfc752c453227b165e00e095005defe8eb03f72486a5d9ca057d34d2f611a3",
        "provenance/roadmap_v3/KKK_LL_Roadmap_Change_Log_P01B1_NoGo_v3.md": "b87e99bb57617385a7207359dc6aa18641b51f4019ae1ddc855e01fad7e7061a",
        "provenance/roadmap_v3/KKK_LL_P01B_1_Deep_Technical_Audit.md": "3610ad87b6c9b431f091bf54b2757f9d9a506ad4791a15e6cc58c2287da06fbb",
        "provenance/ancestors/KKK_LL_P01A_G6_1_1_Final_Tensor_Index_Notation_Presentation_Corrected_One_Plus_Fifteen_Constraint_Evolution_Complete_Freeze_Grade_Final.zip": "a82794364017ad89df2016efd844a52db2378bc18cfc353cf18c3d52b3177b94",
        "provenance/ancestors/KKK_LL_P01B_1_3_Fully_Anisotropic_Homogeneous_Full_Rank_Regularity_No_Go_Release_Harness_Resealed.zip": "d29c052f922164361317c1be3f1556f64da628903ab726aff9963c13929892be",
        "provenance/ancestors/historical_hold/KKK_LL_P01B_1_Fully_Anisotropic_Homogeneous_Full_Rank_Regularity_No_Go_Complete.zip": "036849552f35048fe88bc753850a3566801a30821f1e4bad1f24337cf30787f2",
        "provenance/ancestors/P01B_1_3_EXTERNAL_VERIFICATION_ATTESTATION.json": "39da5752a531e0c0f456ace02e74010c1d529b2bfe2ff7929b69723e1e1f2c8a",
        "provenance/peer_review_p01b2a1_2_hold/Final_Deep_Technical_Freeze_Audit_2026-08-10.md": "f7c4057781ddfdb8dd31d0fe9f19e84f8672aaba97a14d3eecd37682cecc1a16",
        "provenance/peer_review_p01b2a1_2_hold/PDF_contact.png": "9d99fc33f54fa1bf9381d3550983de91d3d7b65a079628924fc4292abe265680",
        "provenance/peer_review_p01b2a1_2_hold/PDF_inspect.txt": "63da221ee1ad8cf41212bf88c06a6f1acbdaab6ceeb8b748ecc6ffaedbf20e8d",
        "provenance/peer_review_p01b2a1_2_hold/Peer_Review_Summary.md": "80c5cd34b2b2a1d5e2fe3f7c1912209678f951368b11f8df72c7826f1d3fcc72",
        "provenance/peer_review_p01b2a1_2_hold/controlled_transcript_mutations.json": "d691e5e912cd18efbc049e8a623e708732d67465f79f89d1bdff7bf55885f7f1",
        "provenance/peer_review_p01b2a1_2_hold/external_independent_audit.json": "41ff7f58c436fea3c016a2a4ef6783a4f11d6a167ac4904bcbd2783310d5ead7",
        "provenance/peer_review_p01b2a1_2_hold/independent_math_checks.json": "6342103e2f828c772edcc037ce93683965fcf94acd432c21059a0b6f21b58c3c",
        "provenance/peer_review_p01b2a1_2_hold/release_harness_reproduction.txt": "ff99012cbfb01c37c7234abf21e700819a1011b1789a03b7b7b48036119c3cf6",
        "provenance/P01B1_ANCESTRY_SUPERSESSION.md": "f2f1d96353ec65d2cdb1921b66923138776a8b914088a5f1decfa2339b2fa61e",
        "provenance/peer_review_p01b2a1_hold/Peer_Review_Summary.md": "1a98aada345e25f099977f990351f2a39685b75274d391abad55c83b40362c10",
        "provenance/peer_review_p01b2a1_hold/Final_Deep_Technical_Freeze_Audit_2026-08-10.md": "1accfbd118c5a191407d65f9b2c4ea72025293fc815af9ca63d83ac07a054132",
        "provenance/peer_review_p01b2a1_hold/external_independent_audit.json": "3e11c6264021337ad104a52c0c38ba3068b1ad00e19f579222a2c2e2ae6a62b4",
        "provenance/peer_review_p01b2a1_hold/external_independent_audit.py": "be72976f0e1bdafce389dbe9a55721077f30ea3bd6fd620cc1a533d19633276c",
        "provenance/peer_review_p01b2a1_hold/external_independent_audit.txt": "c67d131e92a305449fbd00ba8a5fa472cc16e2d54a27d672a2e946b03a806f93",
        "provenance/peer_review_p01b2a1_hold/control_verify_full.json": "2131716b7c057b062c815cb6e73c818c95b67a515ccfe25e99ecb56f7e7f67db",
        "provenance/peer_review_p01b2a1_hold/p01b1_ancestor_release_defect_reproduction.txt": "42d2bbadaaadd80ff63f388e49fb07140d8808f1f39cefee6b1cbdf22a5209bc",
        "provenance/peer_review_p01b2a1_hold/page-09.png": "98ab2cdc8f10b3b367f8ceb979412c97dbad4c549fc591dc6e46937d076aeb71",
        "provenance/peer_review_p01b2a1_hold/page-12.png": "d5c1bc6f2abfc4fd5011884081ad2410cefa21331b40079caa4ea9b9adf790bf",
        "provenance/peer_review_p01b2a1_hold/PDF_contact_montage.png": "8b146514d1cf76a93eee6805ca3a2b61520cbfa26cfe86b85b721d5941a84048",
        "provenance/peer_review_v1_hold/Peer_Review_Summary.md": "7bc35515f6b77416002b28980067641aea664171585a7cebaac519b458c1f9e3",
        "provenance/peer_review_v1_hold/Final_Deep_Technical_Freeze_Audit_2026-08-10.md": "36db1a92ea9262d9f2ece1392518250d662f4f3e59baf09baa79cfc5afca4fee",
        "provenance/peer_review_v1_hold/assert_optimization_reproduction.txt": "7ad02e2fbed61e635f46091ebd9c9b54a290486c38f6a707f163d69f38985371",
        "provenance/peer_review_v1_hold/PDF_contact_montage.png": "1a4b70980c5833ce92313eb1d470fda3f9c946f5bdc71cbbce57f0b30151d925",
        "provenance/peer_review_v1_hold/exact_linearization_results.json": "79e67d4f0a5ae633a477a9976cd788d86b7a6f386a478c7ab6065bf1f47bcc03",
        "provenance/peer_review_v1_hold/external_independent_audit.json": "8350f11952fee47109b2e438c8bc1c3ded368c9153d646876516b34c24fb93ad",
        "provenance/peer_review_v1_hold/external_independent_audit.py": "871cae34199dc072cdf5fae08ba7fddf31a2e5f3a66bb1981eba356db0f34fd4",
        "provenance/peer_review_v1_hold/external_independent_audit.txt": "e64e6e785846b5a016499ae71fa526267dd240983a4d7016fd485fdc671ced28",
        "provenance/peer_review_v1_hold/full_acceleration_spectrum_check.json": "f83f0519bd2f17fc7eed35f982461a5df1db31b41ccd5d4ad644c1f241bf0937",
        "provenance/peer_review_v1_hold/trace_block_scan_selection.json": "d77ca535f0c2c98a97a65af0521903d497fd698f023f4262e434257a1da0e076",
    }
    for relative, checksum in expected.items():
        check((ROOT / relative).is_file(), f"missing provenance: {relative}")
        check(sha256(ROOT / relative) == checksum, f"provenance hash mismatch: {relative}")
    ledger_text = (ROOT / "provenance/roadmap_v3/KKK_LL_Master_Roadmap_P01B1_NoGo_v3_SHA256SUMS.txt").read_text(encoding="utf-8")
    declared_png = "c62ec372b21918c1c8557e43a22f285a6626e2263367a3edafbeb4dabb12688d"
    check(declared_png in ledger_text, "historical PNG checksum disappeared")
    check(declared_png != expected["provenance/roadmap_v3/KKK_LL_Master_Roadmap_P01B1_NoGo_v3.png"],
          "roadmap PNG discrepancy was silently erased")
    source_ledger = (ROOT / "provenance/source_ledger.md").read_text(encoding="utf-8")
    required_disposition = (
        "P01B.1 scoped scientific theorem: accepted.",
        "not release-freeze-grade; historical HOLD",
        "P01B.1.2 archive 02c716...: historical HOLD after coordinated-metadata audit.",
        "P01B.1.3 archive d29c052...: active fail-closed reseal.",
    )
    for marker in required_disposition:
        check(marker in source_ledger, f"ancestry disposition missing: {marker}")
    verify_p01b1_ancestor_semantics()
    return len(expected) + 2 + len(required_disposition) + 1


def verify_freeze_transcript() -> int:
    path = ROOT / "FREEZE_TRANSCRIPT.json"
    semantic_checks = 0

    def semantic(condition: bool, message: str) -> None:
        nonlocal semantic_checks
        semantic_checks += 1
        if not condition:
            raise VerificationError(message)

    semantic(path.is_file(), "authenticated freeze transcript is mandatory")
    transcript = json.loads(path.read_text(encoding="utf-8"))
    semantic(transcript["schema"] == "KKK-LL-P01B2A.1.3-Freeze-Transcript-v3",
             "wrong freeze transcript schema")
    semantic(transcript["release_revision"] == "TOP00-G01-P01B2A.1.3",
             "wrong freeze transcript revision")
    semantic(transcript["status"] == "PASS", "stored freeze transcript is not PASS")
    semantic(transcript["payload_tree_sha256"] == payload_tree_sha256(ROOT),
             "stored transcript does not authenticate the current payload tree")
    semantic(transcript["candidate_content_bytes"] == payload_tree_bytes(ROOT),
             "stored transcript content byte count is not independently bound")
    semantic(transcript["runtime"] == json.loads(
        (ROOT / "verification/runtime_lock.json").read_text(encoding="utf-8")
    ), "stored transcript runtime differs from the runtime lock")
    required_stages = {
        "full_verifier", "optimized_python_fast_verifier",
        "evidence_regeneration", "presentation_rebuild",
        "negative_tests", "mutation_tests", "deterministic_archive_rebuild",
    }
    semantic(required_stages == set(transcript["stages"]),
             "stored freeze transcript stage set is not exact")
    semantic(transcript["tree_unchanged"] is True, "stored replay changed the release tree")
    semantic(transcript["candidate_archive_entries"] == 83,
             "wrong candidate archive entry count")
    semantic(transcript["candidate_content_sha256"] == payload_tree_sha256(ROOT),
             "candidate content hash is not independently bound")
    semantic(transcript["candidate_archive"] ==
             "KKK_LL_TOP00_G01_P01B2A_1_3_candidate.zip",
             "candidate archive name is not exact")
    semantic(transcript["replay_mode"] == "archive-level fresh extraction",
             "freeze transcript replay mode changed")

    stages = transcript["stages"]
    expected_full = {
        "status": "PASS", "mode": "full", "runtime_checks": 9,
        "manifest_files": 82, "provenance_checks": 48,
        "freeze_transcript_checks": 29, "source_contract_checks": 29,
        "contract_evidence_checks": 52, "presentation_memory_checks": 22,
        "g01_exact_checks": 69, "curved_exact_regressions": 70,
        "full_spectrum_cases": 8, "negative_tests": 43,
    }
    expected_fast = {
        "status": "PASS", "mode": "fast", "runtime_checks": 9,
        "manifest_files": 82, "provenance_checks": 48,
        "freeze_transcript_checks": 29, "source_contract_checks": 29,
        "contract_evidence_checks": 52, "presentation_memory_checks": 22,
    }
    semantic(stages["full_verifier"]["result"] == expected_full,
             "full-verifier transcript result changed")
    semantic(stages["optimized_python_fast_verifier"]["result"] == expected_fast,
             "optimized-verifier transcript result changed")
    semantic(stages["evidence_regeneration"]["byte_identical_files"] == 3,
             "evidence byte-identity count changed")
    semantic(stages["evidence_regeneration"]["result"] == {
        "status": "PASS",
        "files": ["g01_exact.json", "p01b2_equal_radius_rho1_audit.json",
                  "p01b2_full_acceleration_spectrum.json"],
        "samples": 4_000_000, "trace_inertia_pass_points": 249_573,
        "stable_joint_points_found": 0,
    }, "evidence-regeneration transcript result changed")
    presentation_contract = json.loads(
        (ROOT / "contracts/presentation_contract.json").read_text(encoding="utf-8")
    )
    semantic(stages["presentation_rebuild"]["byte_identical_files"] == 3,
             "presentation byte-identity count changed")
    semantic(stages["presentation_rebuild"]["result"] == presentation_contract,
             "presentation transcript result/hashes changed")
    semantic(stages["negative_tests"]["result"] == {
        "status": "PASS", "negative_tests": 43,
    }, "negative-test transcript result changed")
    semantic(stages["mutation_tests"]["result"] == {
        "status": "PASS", "mutation_tests": 27, "unmodified_baselines": 2,
    }, "mutation-test transcript result changed")

    archive_stage = stages["deterministic_archive_rebuild"]
    semantic(archive_stage["byte_identical"] is True,
             "deterministic archive builds differ")
    semantic(archive_stage["content_sha256"] == payload_tree_sha256(ROOT),
             "archive content hash is not independently bound")
    semantic(archive_stage["content_bytes"] == payload_tree_bytes(ROOT),
             "archive content byte count is not independently bound")
    semantic(archive_stage["entries"] == transcript["candidate_archive_entries"],
             "candidate entry count is not independently bound")
    expected_build = {
        "status": "PASS", "files": 83, "root": ROOT.name,
        "content_sha256": payload_tree_sha256(ROOT),
        "content_bytes": payload_tree_bytes(ROOT),
    }
    semantic(archive_stage["result_a"] == expected_build,
             "archive build A result changed")
    semantic(archive_stage["result_b"] == expected_build,
             "archive build B result changed")
    semantic(transcript["outer_final_archive_sha256"] ==
             "recorded in the external final attestation to avoid a self-hash cycle",
             "final-hash self-cycle policy changed")
    semantic(archive_stage["result_a"] == archive_stage["result_b"],
             "deterministic archive build metadata disagree")
    return semantic_checks


def verify_source_contract() -> int:
    active_python = [
        path for path in ROOT.rglob("*.py")
        if "provenance" not in path.relative_to(ROOT).parts
    ]
    assertion_nodes = []
    for path in active_python:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        assertion_nodes.extend(
            (path.relative_to(ROOT).as_posix(), node.lineno)
            for node in ast.walk(tree) if isinstance(node, ast.Assert)
        )
    check(not assertion_nodes, f"bare assert nodes are forbidden: {assertion_nodes}")
    controls = active_text_control_characters(ROOT)
    check(not controls, f"active text contains forbidden C0 controls: {controls}")

    search_text = (ROOT / "calculations/p01b2_equal_radius_search.py").read_text(encoding="utf-8")
    curved_text = (ROOT / "calculations/p01b2_curved_doubleform.py").read_text(encoding="utf-8")
    required_search = (
        'DERIVATIVE_METHOD = "exact_double_form_product_rule"',
        "BLOCK_DIMENSIONS = np.array([3.0, 4.0, 4.0, 4.0])",
        "expected = np.array([-1.0, -1.0, -1.0, 14.0])",
        "NONTRACE_MULTIPLICITIES = (5, 18, 36, 48, 9)",
        "/ SQRT_BLOCK_DIMENSIONS[None, :]",
        "trace_symmetric_representative",
        "legacy_lower_triangle_spectrum_for_certificate",
    )
    for marker in required_search:
        check(marker in search_text, f"scientific source marker missing: {marker}")
    check("np.linalg.eigvalsh(trace_matrix)" not in search_text,
          "invalid eigvalsh(trace_matrix) operation reintroduced")
    check("finite_difference" not in search_text.lower(),
          "finite-difference linearization reintroduced")
    check("MAX_LOCAL_ORDER = 7" in curved_text, "local Lovelock order ledger changed")
    check("ds4 = (Fraction(1), 12 * x, 24 * x * x)" in curved_text,
          "dS4 fixed-point factor changed")
    check("def topological_order8_regression()" in curved_text,
          "order-eight executable regression removed")

    sys.path.insert(0, str(ROOT / "calculations"))
    import p01b2_equal_radius_search as search
    expected_nontrace = np.array([
        [-1, -144, -12096, -663552, -23224320, -477757440, -4459069440],
        [-1, -124, -8928, -423936, -13271040, -252149760, -2229534720],
        [-1, -124, -8784, -396288, -11059200, -172523520, -1114767360],
        [-1, -108, -6624, -255744, -5806080, -59719680, 0],
        [-1, -100, -5040, -119808, 0, 66355200, 1114767360],
    ], dtype=float)
    check(np.array_equal(search.NONTRACE_COEFFICIENTS, expected_nontrace),
          "nontrace coefficient ledger changed")
    check(search.NONTRACE_MULTIPLICITIES == (5, 18, 36, 48, 9),
          "120-mode multiplicity ledger changed")
    return len(active_python) + len(required_search) + 9


def verify_contracts_and_evidence() -> int:
    checks = []
    def q(condition: bool, message: str) -> None:
        check(condition, message)
        checks.append(message)

    top00 = json.loads((ROOT / "contracts/top00_contract.json").read_text(encoding="utf-8"))
    q(top00["status"] == "COMPLETE", "TOP00 status")
    q(top00["local_lovelock_orders"] == list(range(8)), "TOP00 local orders")
    q(top00["topological_lovelock_order"] == 8, "TOP00 order eight")

    release = json.loads((ROOT / "contracts/release_record.json").read_text(encoding="utf-8"))
    q(release["revision"] == "TOP00-G01-P01B2A.1.3", "release revision")
    q("P01B2A.1.1" in release["supersedes"] and "P01B2A.1.2" in release["supersedes"],
      "release supersession chain")
    q(release["controlled_audit"]["verdict"] == "NO PASS FOUND IN DECLARED FINITE SAMPLE", "release verdict")
    q(release["controlled_audit"]["necessary_condition_points_tested"] == 249573, "release corrected count")
    q(release["blocked"] == ["P01C-CURV"], "release block")
    q("arbitrary-rho" in release["authorized_next_calculation"], "release handoff")
    q(release["ancestor_chain"]["active_p01b1_sha256"] ==
      "d29c052f922164361317c1be3f1556f64da628903ab726aff9963c13929892be",
      "active P01B.1.3 ancestor")
    q(release["freeze_transcript"] == "FREEZE_TRANSCRIPT.json", "freeze transcript contract")

    g01 = json.loads((ROOT / "evidence/g01_exact.json").read_text(encoding="utf-8"))
    q(g01 == {
        "direct_product_orders": list(range(7)),
        "equal_radius_coefficients_over_pi6": ["1/8", "9", "504", "20736", "580608", "9953280", "79626240"],
        "euler_characteristic_y": 27,
        "exact_checks": 69,
        "single_factor_lovelock": ["1", "24", "192"],
        "status": "PASS",
    }, "G01 evidence")

    audit = json.loads((ROOT / "evidence/p01b2_equal_radius_rho1_audit.json").read_text(encoding="utf-8"))
    q(audit["status"] == "PASS", "rho1 evidence status")
    q(audit["classification"] == "equal-internal-radius, rho=1 controlled-slice audit", "rho1 classification")
    q(audit["analytic_local_orders"] == list(range(8)) and audit["topological_order"] == 8, "rho1 order ledger")
    q(audit["derivative_method"] == "exact_double_form_product_rule", "exact derivative method")
    q(audit["fixed_point"] == {"H2": 1, "rho_H2_over_y": 1, "yL": 1, "yR": 1, "yc": 1}, "rho1 fixed point")
    einstein = audit["einstein_trace_regression"]
    q(einstein["D"] == [3.0, 4.0, 4.0, 4.0], "trace dimensions")
    q(einstein["D_self_adjoint"] and einstein["B_symmetric"], "weighted trace symmetry")
    q(np.allclose(einstein["eigenvalues"], [-1, -1, -1, 14], rtol=0.0, atol=2e-12), "Einstein trace spectrum")
    scan = audit["joint_scan"]
    q(scan["seed"] == 731923 and scan["samples"] == 4_000_000, "scan seed and size")
    q(scan["nontrace_inertia_feasible_points"] == 249_706, "nontrace count")
    q(scan["trace_inertia_pass_points"] == 249_573, "trace count")
    q(scan["joint_necessary_condition_points_tested"] == 249_573, "tested count")
    q(scan["numerical_gate_rejections"] == 0, "numerical gate rejections")
    q(scan["stable_joint_points_found"] == 0, "stable count")
    q(math.isclose(scan["best"]["growth"], 0.6440821660663996, rel_tol=0.0, abs_tol=2e-13), "best growth")
    q("rho=H_star^2/y=1 slice" in scan["scope"] and "not the full equal-radius branch" in scan["scope"], "scan scope")
    correction = scan["legacy_trace_algorithm_correction"]
    q(correction["count"] == 27 and correction["stable_count"] == 0, "27-point correction")
    q(correction["global_indices"] == [57675,519697,703577,965515,1097325,1735480,1930101,2065464,2350580,2473140,2672082,2794618,2899776,2923947,2929570,3006503,3025164,3078379,3091426,3168986,3181889,3230524,3262324,3498616,3512958,3589550,3699961], "27-point indices")
    q(math.isclose(correction["minimum_growth"], 1.6151308422809392, rel_tol=0.0, abs_tol=5e-13), "corrected minimum growth")
    q(math.isclose(correction["maximum_growth"], 1.8686083465648167, rel_tol=0.0, abs_tol=5e-12), "corrected maximum growth")
    q(audit["physical_residue_verdict"] == "deferred_to_constraint_gauge_reduced_analysis", "physical residue scope")
    stable, inertia_pass = audit["witnesses"]
    q(all(value == "0" for value in stable["fixed_point_residuals_exact"]), "stable witness on shell")
    q(stable["full_inertia"] == {"negative": 60, "positive": 60, "zero": 0}, "stable witness inertia")
    q(stable["maximum_constraint_tangent_growth_rate"] < 0, "stable witness stability")
    q(not stable["trace_block_einstein_inertia_pass"], "stable witness trace fail")
    q(all(value == "0" for value in inertia_pass["fixed_point_residuals_exact"]), "inertia-pass witness on shell")
    q(inertia_pass["full_inertia"] == {"negative": 119, "positive": 1, "zero": 0}, "inertia-pass witness full inertia")
    q(inertia_pass["maximum_constraint_tangent_growth_rate"] > 0, "inertia-pass witness instability")
    q(inertia_pass["trace_block_einstein_inertia_pass"], "inertia-pass witness trace pass")
    for witness in audit["witnesses"]:
        q(witness["matrix_condition_number"] <= audit["numerical_gates"]["maximum_block_condition_number"], "witness condition gate")
        q(witness["constraint_gradient_norm"] >= audit["numerical_gates"]["minimum_constraint_gradient_norm"], "witness constraint-gradient gate")
        q(witness["constraint_tangent_leakage"] <= audit["numerical_gates"]["maximum_constraint_tangent_leakage"], "witness leakage gate")

    spectrum = json.loads((ROOT / "evidence/p01b2_full_acceleration_spectrum.json").read_text(encoding="utf-8"))
    q(spectrum["status"] == "PASS", "spectrum status")
    q(spectrum["full_dimension"] == 120 and spectrum["trace_dimension"] == 4, "spectrum dimensions")
    q(spectrum["nontrace_multiplicities"] == [5, 18, 36, 48, 9] and spectrum["multiplicity_sum"] == 116, "spectrum multiplicities")
    q([item["case"] for item in spectrum["cases"]] == [f"order_{i}" for i in range(1,8)] + ["generic_all_order_combination"], "spectrum cases")
    q(max(item["maximum_relative_multiset_error"] for item in spectrum["cases"]) < 1e-12, "spectrum multiset error")
    return len(checks)


def combined_markdown() -> str:
    sources = (
        ROOT / "docs/TOP00_Topology_and_Scope_Lock.md",
        ROOT / "docs/G01_CP2_Cubed_Product_Geometry_Lock.md",
        ROOT / "docs/P01B2_CURV_Stage_A_Exact_Reduction.md",
        ROOT / "docs/PROJECT_MEMORY_ROADMAP_v3_TOP00_G01_P01B2A_1_2.md",
    )
    sections = []
    for source in sources:
        text = source.read_text(encoding="utf-8")
        sections.append(text if text.endswith("\n") else text + "\n")
    return "\n\\newpage\n\n".join(sections)


def verify_presentation_and_memory() -> int:
    contract = json.loads((ROOT / "contracts/presentation_contract.json").read_text(encoding="utf-8"))
    pdf = ROOT / "docs/TOP00_G01_P01B2_CURV_Stage_A_1_2.pdf"
    html = ROOT / "docs/TOP00_G01_P01B2_CURV_Stage_A_1_2.html"
    check(contract["status"] == "PASS", "presentation contract is not PASS")
    check(contract["revision"] == "TOP00-G01-P01B2A.1.2", "presentation revision mismatch")
    check(sha256(pdf) == contract["pdf_sha256"], "PDF hash mismatch")
    check(sha256(html) == contract["html_sha256"], "HTML hash mismatch")
    check(len(PdfReader(str(pdf), strict=True).pages) == contract["pdf_pages"], "PDF page count mismatch")
    combined = combined_markdown()
    combined_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()
    check(combined_hash == contract["combined_source_sha256"], "combined source hash mismatch")
    for name, checksum in contract["sources"].items():
        check(sha256(ROOT / "docs" / name) == checksum, f"presentation source hash mismatch: {name}")
    html_text = html.read_text(encoding="utf-8")
    check("<script src=\"http" not in html_text.lower() and "<link href=\"http" not in html_text.lower(), "HTML remote dependency")
    check(combined_hash in html_text, "HTML combined-source hash absent")
    active_text = combined + html_text
    check("\\!-!" not in active_text, "invalid branch hyphen notation remains")
    check("249,546" not in active_text and "249546" not in active_text, "stale trace count remains")
    memory = (ROOT / "docs/PROJECT_MEMORY_ROADMAP_v3_TOP00_G01_P01B2A_1_3.md").read_text(encoding="utf-8")
    required = (
        "Immutable parent",
        "P01B.1.3: active fail-closed ancestor",
        "P01B2A.1.3: active immutable parent",
        "4{,}000{,}000",
        "249{,}706",
        "249{,}573",
        "0.644082166066",
        "arbitrary-}\\rho",
        "unequal-radius continuation",
        "P01C-CURV remains blocked",
    )
    for marker in required:
        check(marker in memory, f"canonical memory marker missing: {marker}")
    check((ROOT / "docs/P01B2A_1_3_RELEASE_HARNESS_HOTFIX_LEDGER.md").is_file(), "hotfix ledger missing")
    return 12 + len(required)


def verify_exact_engines() -> tuple[int, int, int, int]:
    sys.path.insert(0, str(ROOT / "calculations"))
    sys.path.insert(0, str(ROOT / "verification"))
    import g01_product_geometry as g01
    import negative_tests
    import p01b2_curved_doubleform as curv
    import p01b2_equal_radius_search as search

    g01_result = g01.exact_self_check()
    curved_result = curv.exact_self_check()
    check(g01_result["status"] == "PASS" and g01_result["exact_checks"] == 69,
          "G01 exact engine failed")
    expected_curved = {
        "status": "PASS",
        "flat_all_order_checks": 35,
        "fixed_point_product_checks": 32,
        "topological_order8_checks": 3,
        "full_component_dimension": 120,
        "curved_k1_nonzero_entries": 315,
        "curved_k2_nonzero_entries": 327,
        "analytic_local_orders": list(range(8)),
        "topological_order": 8,
    }
    check(curved_result == expected_curved, "curved exact engine result changed")
    cache = search.build_exact_linearization_cache()
    einstein = search.einstein_trace_regression(cache)
    check(np.allclose(einstein["eigenvalues"], [-1,-1,-1,14], rtol=0.0, atol=2e-12),
          "exact-cache Einstein regression failed")
    spectrum = search.full_acceleration_spectrum_regression(
        cache, search.full_acceleration_orders()
    )
    check(spectrum["status"] == "PASS" and spectrum["full_dimension"] == 120,
          "full acceleration spectrum regression failed")
    negative_count = negative_tests.run()
    return 69, 35 + 32 + 3, len(spectrum["cases"]), negative_count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true", help="skip expensive exact engines")
    args = parser.parse_args()
    result = {
        "runtime_checks": verify_runtime(),
        "manifest_files": verify_manifest(),
        "provenance_checks": verify_provenance(),
        "freeze_transcript_checks": verify_freeze_transcript(),
        "source_contract_checks": verify_source_contract(),
        "contract_evidence_checks": verify_contracts_and_evidence(),
        "presentation_memory_checks": verify_presentation_and_memory(),
        "mode": "fast" if args.fast else "full",
    }
    if not args.fast:
        g01_checks, curved_checks, spectrum_cases, negative_checks = verify_exact_engines()
        result.update({
            "g01_exact_checks": g01_checks,
            "curved_exact_regressions": curved_checks,
            "full_spectrum_cases": spectrum_cases,
            "negative_tests": negative_checks,
        })
    result["status"] = "PASS"
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
