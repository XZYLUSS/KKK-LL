#!/usr/bin/env python3
"""Fail-closed type, domain, and numerical-gate controls."""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "calculations"))

import g01_product_geometry as g01
import p01b2_curved_doubleform as curv
import p01b2_equal_radius_search as search
from release_integrity import active_text_control_characters


def _must_raise(error, function, *args) -> None:
    try:
        function(*args)
    except error:
        return
    raise RuntimeError(f"{function.__name__} did not raise {error.__name__}")


def _fake_cache(matrix: np.ndarray, gradient: np.ndarray | None = None) -> dict:
    m0 = np.zeros((8, 4, 4))
    m0[1] = matrix
    dh = np.zeros((7, 8))
    if gradient is not None:
        dh[:, 1] = gradient
    return {
        "m0": m0,
        "dq": np.zeros((7, 8, 4)),
        "dm": np.zeros((7, 8, 4, 4)),
        "dh": dh,
    }


def _excessive_leakage_cache() -> dict:
    cache = _fake_cache(np.eye(4), np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]))
    cache["dq"][1, 1, 0] = -1.0
    return cache


def run() -> int:
    alpha1 = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    nonsymmetric_trace = np.array([
        [1.0, 2.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ])
    cases = (
        (ValueError, g01._pair_mask, 1, 1),
        (TypeError, g01._pair_mask, True, 1),
        (ValueError, g01.cp2_curvature_block, -1, 1, 4),
        (TypeError, g01.cp2_curvature_block, 0, 1.0, 4),
        (ValueError, g01.cp2_curvature_block, 2, 1, 4),
        (ValueError, g01.cp2_riemann_unit, 0, 1, 2, 4),
        (TypeError, g01.cp2_riemann_unit, True, 1, 2, 3),
        (ValueError, g01.lovelock_densities, {}, -1),
        (ValueError, g01.product_integral_polynomial, 7),
        (ValueError, g01.evaluate_polynomial, {}, (1, 2)),
        (TypeError, g01.evaluate_polynomial, {}, (1.0, 2, 3)),
        (TypeError, g01.single_factor_integral, True, (0, 0, 0), 0),
        (TypeError, g01.single_factor_integral, 0, (0, 0, 0), False),
        (TypeError, g01.local_product_formula, True, (1, 1, 1)),
        (TypeError, g01.local_product_formula, 1, (1.0, 1, 1)),
        (ValueError, curv._validate_four, (1, 2, 3), "test"),
        (TypeError, curv._validate_four, (1, 2, 3, 4.0), "test"),
        (ValueError, curv._block_of, 15),
        (ValueError, curv._block_of, True),
        (ValueError, curv.spatial_gauss_curvature, (1, 2, 3, 4), 0, (1, 2)),
        (TypeError, curv.spatial_gauss_curvature, (1, 2, 3, 4), 0.0, (1, 2, 3)),
        (TypeError, curv.spatial_gauss_curvature, (1, 2, 3, 4), 0, (1, 2, 3.0)),
        (ValueError, curv.double_powers, {}, -1),
        (ValueError, curv.double_powers, {}, True),
        (ValueError, curv.q_diagonal_by_order, ({},), 15),
        (TypeError, curv.q_diagonal_by_order, ({},), True),
        (ValueError, curv.acceleration_tensor_by_order, {}, 0),
        (ValueError, curv.acceleration_tensor_by_order, {}, 8),
        (TypeError, curv.acceleration_tensor_by_order, {}, True),
        (ValueError, curv.fixed_point_equation_coefficients, 1, (1, 2)),
        (TypeError, curv.fixed_point_equation_coefficients, 1.0, (1, 2, 3)),
        (TypeError, curv.fixed_point_equation_coefficients, 1, (1, 2.0, 3)),
        (ValueError, search.solve_exact_couplings, (1, 2, 3, 4)),
        (ValueError, search.solve_exact_couplings, (1, 2, 3, 4, 0)),
        (TypeError, search.solve_exact_couplings, (1, 2, 3, 4, 5.0)),
        (ValueError, search.deterministic_joint_scan, {}, 0),
        (TypeError, search.deterministic_joint_scan, {}, True),
        (ValueError, search.trace_symmetric_representative, nonsymmetric_trace),
        (
            np.linalg.LinAlgError,
            search.tangent_spectrum,
            alpha1,
            _fake_cache(np.zeros((4, 4)), np.ones(7)),
        ),
        (
            np.linalg.LinAlgError,
            search.tangent_spectrum,
            alpha1,
            _fake_cache(np.diag([1.0, 1.0, 1.0, 1.0e-12]), np.ones(7)),
        ),
        (
            ValueError,
            search.tangent_spectrum,
            alpha1,
            _fake_cache(np.eye(4), np.zeros(7)),
        ),
        (
            ValueError,
            search.tangent_spectrum,
            alpha1,
            _excessive_leakage_cache(),
        ),
    )
    for error, function, *args in cases:
        _must_raise(error, function, *args)
    with tempfile.TemporaryDirectory(prefix="p01b2a11-control-negative-") as temporary:
        root = Path(temporary)
        (root / "docs").mkdir()
        (root / "docs/bad.md").write_bytes(b"valid\ninvalid\rtext\n")
        detected = active_text_control_characters(root)
        if detected != {"docs/bad.md": [13]}:
            raise RuntimeError(f"control-character detector failed: {detected}")
    return len(cases) + 1


if __name__ == "__main__":
    import json
    print(json.dumps({"status": "PASS", "negative_tests": run()}, sort_keys=True))
