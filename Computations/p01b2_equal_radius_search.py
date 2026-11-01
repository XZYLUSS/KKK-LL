#!/usr/bin/env python3
"""Deterministic P01B.2 audit on the equal-internal-radius, rho=1 slice.

The fixed point is H_*^2=y_c=y_L=y_R=1, hence rho=H_*^2/y=1.  This is
one controlled slice of the equal-radius branch, not the complete branch.  The
calculation retains alpha_0,...,alpha_7, uses the full 120-component homogeneous
acceleration map, normalizes the four trace blocks with D=diag(3,4,4,4), and
constructs first derivatives exactly from

    d(Omega^k)=k Omega^(k-1) wedge dOmega.

Only the final matrix spectra use floating-point arithmetic.
"""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np

from g01_product_geometry import (
    DoubleForm,
    _pair_mask,
    cp2_curvature_block,
    double_wedge,
    exact_fraction,
    local_product_formula,
)
from p01b2_curved_doubleform import (
    BLOCKS,
    MAX_LOCAL_ORDER,
    SPATIAL_DIMENSION,
    acceleration_tensor_by_order,
    block_acceleration_matrix_by_order,
    double_powers,
    fixed_point_equation_coefficients,
    hamiltonian_by_order,
    q_diagonal_by_order,
    spatial_gauss_curvature,
    sym2_component_matrix,
)


DERIVATIVE_METHOD = "exact_double_form_product_rule"
BLOCK_DIMENSIONS = np.array([3.0, 4.0, 4.0, 4.0])
SQRT_BLOCK_DIMENSIONS = np.sqrt(BLOCK_DIMENSIONS)
TRACE_INERTIA_TOLERANCE = 1.0e-7
NONTRACE_MARGIN = 1.0e-6
STABILITY_TOLERANCE = 1.0e-9
MAX_BLOCK_CONDITION_NUMBER = 1.0e10
MIN_CONSTRAINT_GRADIENT_NORM = 1.0e-10
MAX_CONSTRAINT_TANGENT_LEAKAGE = 1.0e-8


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def solve_exact_couplings(higher: Iterable[Fraction]) -> Tuple[Fraction, ...]:
    """Fix alpha1=1, accept nonzero alpha3,...,alpha7, solve alpha2,alpha0."""
    high = tuple(exact_fraction(value, "higher Lovelock coupling") for value in higher)
    if len(high) != 5 or any(value == 0 for value in high):
        raise ValueError("five nonzero exact values alpha3,...,alpha7 are required")
    equations = fixed_point_equation_coefficients(Fraction(1), (1, 1, 1))
    difference = tuple(equations[0][k] - equations[1][k] for k in range(8))
    alpha = [Fraction()] * 8
    alpha[1] = Fraction(1)
    alpha[3:] = high
    alpha[2] = -sum(
        difference[k] * alpha[k] for k in range(1, 8) if k != 2
    ) / difference[2]
    alpha[0] = -sum(
        equations[0][k] * alpha[k] for k in range(1, 8)
    ) / equations[0][0]
    return tuple(alpha)


STABLE_BUT_EINSTEIN_INERTIA_INVALID = solve_exact_couplings((
    Fraction(268949941, 10**11),
    -Fraction(745204243, 10**13),
    Fraction(147371652, 10**14),
    Fraction(282742108, 10**16),
    -Fraction(359113011, 10**17),
))

EINSTEIN_INERTIA_PASS_BUT_UNSTABLE = solve_exact_couplings((
    Fraction(1, 10),
    Fraction(1, 100),
    Fraction(1, 1000),
    Fraction(37411087, 10**12),
    -Fraction(1, 100000),
))


def _block_lookup() -> Tuple[int, ...]:
    lookup = [-1] * SPATIAL_DIMENSION
    for block, indices in enumerate(BLOCKS):
        for index in indices:
            lookup[index] = block
    _require(all(value >= 0 for value in lookup), "incomplete block lookup")
    return tuple(lookup)


def fixed_point_curvature_and_derivatives() -> Tuple[DoubleForm, Tuple[DoubleForm, ...]]:
    """Return Omega and its seven exact state derivatives at the rho=1 point."""
    rates = (Fraction(1), Fraction(), Fraction(), Fraction())
    omega = spatial_gauss_curvature(rates, Fraction(), (1, 1, 1))
    block_of = _block_lookup()
    derivatives = []

    for variable in range(4):
        derivative: Dict[Tuple[int, int], Fraction] = {}
        for i in range(SPATIAL_DIMENSION):
            for j in range(i + 1, SPATIAL_DIMENSION):
                bi, bj = block_of[i], block_of[j]
                value = (
                    int(bi == variable) * rates[bj]
                    + rates[bi] * int(bj == variable)
                )
                if value:
                    pair = _pair_mask(i, j)
                    derivative[(pair, pair)] = value
        derivatives.append(derivative)

    for internal in range(3):
        offset = BLOCKS[internal + 1][0]
        derivatives.append(
            cp2_curvature_block(offset, Fraction(1), SPATIAL_DIMENSION)
        )

    _require([len(item) for item in derivatives] == [3, 12, 12, 12, 12, 12, 12],
             "unexpected first-curvature derivative sparsity")
    return omega, tuple(derivatives)


@lru_cache(maxsize=1)
def build_exact_linearization_cache() -> Dict[str, np.ndarray | dict]:
    """Construct exact first derivatives before conversion to NumPy arrays."""
    omega, derivative_omega = fixed_point_curvature_and_derivatives()
    powers = double_powers(omega, MAX_LOCAL_ORDER)
    derivative_powers = []
    for direction in derivative_omega:
        rows = [{}]
        for order in range(1, MAX_LOCAL_ORDER + 1):
            rows.append({
                key: order * value
                for key, value in double_wedge(powers[order - 1], direction).items()
            })
        derivative_powers.append(tuple(rows))

    h0 = np.array([float(value) for value in hamiltonian_by_order(powers)])
    q0 = np.array([
        [float(value) for value in q_diagonal_by_order(powers, BLOCKS[i][0])]
        for i in range(4)
    ]).T
    m0 = np.zeros((8, 4, 4))
    for order in range(1, 8):
        tensor = acceleration_tensor_by_order(powers[order - 1], order)
        m0[order] = np.array(block_acceleration_matrix_by_order(tensor), dtype=float)

    dh = np.zeros((7, 8))
    dq = np.zeros((7, 8, 4))
    dm = np.zeros((7, 8, 4, 4))
    for variable, dpowers in enumerate(derivative_powers):
        dh[variable, 1:] = [
            float(value) for value in hamiltonian_by_order(dpowers)[1:]
        ]
        for block in range(4):
            dq[variable, 1:, block] = [
                float(value)
                for value in q_diagonal_by_order(dpowers, BLOCKS[block][0])[1:]
            ]
        for order in range(2, 8):
            tensor = acceleration_tensor_by_order(dpowers[order - 1], order)
            dm[variable, order] = np.array(
                block_acceleration_matrix_by_order(tensor), dtype=float
            )

    metadata = {
        "derivative_method": DERIVATIVE_METHOD,
        "omega_entries": len(omega),
        "power_entries": [len(power) for power in powers],
        "derivative_power_entries": [
            [len(power) for power in rows] for rows in derivative_powers
        ],
    }
    return {
        "h0": h0,
        "q0": q0,
        "m0": m0,
        "dh": dh,
        "dq": dq,
        "dm": dm,
        "metadata": metadata,
    }


def trace_symmetric_representative(matrix: np.ndarray) -> np.ndarray:
    """Convert the D-self-adjoint block-value map to a Euclidean symmetric map."""
    matrix = np.asarray(matrix, dtype=float)
    if matrix.shape != (4, 4) or not np.all(np.isfinite(matrix)):
        raise ValueError("trace block must be a finite 4 x 4 matrix")
    weighted = BLOCK_DIMENSIONS[:, None] * matrix
    if not np.allclose(weighted, weighted.T, rtol=2.0e-12, atol=1.0e-9):
        raise ValueError("trace block violates D M = M^T D")
    symmetric = (
        matrix
        * SQRT_BLOCK_DIMENSIONS[:, None]
        / SQRT_BLOCK_DIMENSIONS[None, :]
    )
    if not np.allclose(symmetric, symmetric.T, rtol=2.0e-12, atol=1.0e-9):
        raise ValueError("normalized trace block is not Euclidean symmetric")
    return 0.5 * (symmetric + symmetric.T)


def trace_inertia(matrix: np.ndarray) -> Tuple[np.ndarray, bool]:
    eigenvalues = np.linalg.eigvalsh(trace_symmetric_representative(matrix))
    passed = (
        np.count_nonzero(eigenvalues > TRACE_INERTIA_TOLERANCE) == 1
        and np.count_nonzero(eigenvalues < -TRACE_INERTIA_TOLERANCE) == 3
    )
    return eigenvalues, bool(passed)


def legacy_lower_triangle_spectrum_for_certificate(matrix: np.ndarray) -> np.ndarray:
    """Reproduce v1's invalid lower-triangle interpretation without gating on it."""
    matrix = np.asarray(matrix, dtype=float)
    if matrix.shape != (4, 4):
        raise ValueError("legacy certificate requires a 4 x 4 matrix")
    lower = np.tril(matrix)
    symmetric_triangle_interpretation = lower + np.tril(matrix, -1).T
    return np.linalg.eigvalsh(symmetric_triangle_interpretation)


def tangent_spectrum(alpha: np.ndarray, cache: Dict[str, np.ndarray | dict]):
    """Return the exact-first-derivative constraint-tangent spectrum and gates."""
    alpha = np.asarray(alpha, dtype=float)
    if alpha.shape != (8,) or not np.all(np.isfinite(alpha)):
        raise ValueError("alpha must be a finite eight-vector")
    psi0 = np.array([-1.0, 0.0, 0.0, 0.0])
    matrix = np.tensordot(alpha, cache["m0"], axes=(0, 0))
    singular = np.linalg.svd(matrix, compute_uv=False)
    if singular[-1] <= 0:
        raise np.linalg.LinAlgError("singular four-scale acceleration block")
    condition = float(singular[0] / singular[-1])
    if not math.isfinite(condition) or condition > MAX_BLOCK_CONDITION_NUMBER:
        raise np.linalg.LinAlgError("four-scale acceleration block exceeds condition cutoff")

    sources = np.empty((4, 7))
    for variable in range(7):
        sources[:, variable] = (
            alpha @ cache["dq"][variable]
            + np.tensordot(alpha, cache["dm"][variable], axes=(0, 0)) @ psi0
        )
    derivative_psi = -np.linalg.solve(matrix, sources)
    jacobian = np.zeros((7, 7))
    jacobian[:4] = -derivative_psi
    jacobian[0, 0] -= 2.0
    jacobian[4, 1] = -2.0
    jacobian[5, 2] = -2.0
    jacobian[6, 3] = -2.0

    constraint_gradient = cache["dh"] @ alpha
    gradient_norm = float(np.linalg.norm(constraint_gradient))
    if gradient_norm < MIN_CONSTRAINT_GRADIENT_NORM:
        raise ValueError("constraint gradient is zero or below the declared margin")
    tangent_basis = np.linalg.svd(constraint_gradient.reshape(1, -1))[2][1:].T
    tangent_jacobian = tangent_basis.T @ jacobian @ tangent_basis
    leakage = float(np.linalg.norm(
        (np.eye(7) - tangent_basis @ tangent_basis.T) @ jacobian @ tangent_basis
    ))
    if leakage > MAX_CONSTRAINT_TANGENT_LEAKAGE:
        raise ValueError("constraint-tangent leakage exceeds the declared cutoff")
    return np.linalg.eigvals(tangent_jacobian), matrix, {
        "matrix_condition_number": condition,
        "constraint_gradient_norm": gradient_norm,
        "constraint_tangent_leakage": leakage,
    }


def full_acceleration_orders() -> Tuple[np.ndarray, ...]:
    omega = spatial_gauss_curvature((1, 0, 0, 0), 0, (1, 1, 1))
    powers = double_powers(omega, 6)
    orders = []
    for order in range(1, 8):
        tensor = acceleration_tensor_by_order(powers[order - 1], order)
        matrix = np.array(sym2_component_matrix(tensor), dtype=float)
        _require(np.allclose(matrix, matrix.T, rtol=0.0, atol=0.0),
                 f"full acceleration order {order} is not symmetric")
        orders.append(matrix)
    return tuple(orders)


NONTRACE_COEFFICIENTS = np.array([
    [-1, -144, -12096, -663552, -23224320, -477757440, -4459069440],
    [-1, -124, -8928, -423936, -13271040, -252149760, -2229534720],
    [-1, -124, -8784, -396288, -11059200, -172523520, -1114767360],
    [-1, -108, -6624, -255744, -5806080, -59719680, 0],
    [-1, -100, -5040, -119808, 0, 66355200, 1114767360],
], dtype=float)
NONTRACE_MULTIPLICITIES = (5, 18, 36, 48, 9)


def planck_coefficient(alpha: np.ndarray) -> float:
    alpha = np.asarray(alpha, dtype=float)
    if alpha.shape != (8,):
        raise ValueError("alpha must contain eight couplings")
    return sum(
        (order + 1) * alpha[order + 1]
        * float(local_product_formula(order, (1, 1, 1)))
        for order in range(7)
    )


def einstein_trace_regression(cache: Dict[str, np.ndarray | dict]) -> dict:
    matrix = np.array(cache["m0"][1], copy=True)
    symmetric = trace_symmetric_representative(matrix)
    eigenvalues = np.linalg.eigvalsh(symmetric)
    expected = np.array([-1.0, -1.0, -1.0, 14.0])
    _require(np.allclose(eigenvalues, expected, rtol=0.0, atol=2.0e-12),
             "Einstein normalized trace spectrum is not {-1,-1,-1,14}")
    return {
        "D": BLOCK_DIMENSIONS.tolist(),
        "M": matrix.tolist(),
        "D_self_adjoint": bool(np.allclose(
            BLOCK_DIMENSIONS[:, None] * matrix,
            (BLOCK_DIMENSIONS[:, None] * matrix).T,
            rtol=0.0,
            atol=0.0,
        )),
        "B": symmetric.tolist(),
        "B_symmetric": bool(np.allclose(symmetric, symmetric.T)),
        "eigenvalues": eigenvalues.tolist(),
    }


def audit_witness(
    name: str,
    exact_alpha: Tuple[Fraction, ...],
    cache: Dict[str, np.ndarray | dict],
    acceleration_orders: Tuple[np.ndarray, ...],
) -> dict:
    equations = fixed_point_equation_coefficients(Fraction(1), (1, 1, 1))
    residuals = [sum(row[k] * exact_alpha[k] for k in range(8)) for row in equations]
    _require(not any(residuals), f"{name}: exact fixed-point residual")
    alpha = np.array([float(value) for value in exact_alpha])
    tangent, trace_matrix, diagnostics = tangent_spectrum(alpha, cache)
    full = sum(
        alpha[order] * acceleration_orders[order - 1]
        for order in range(1, 8)
    )
    _require(np.allclose(full, full.T, rtol=1.0e-13, atol=1.0e-10),
             f"{name}: full acceleration matrix is not symmetric")
    eigenvalues = np.linalg.eigvalsh(full)
    singular = np.linalg.svd(full, compute_uv=False)
    sign, logdet = np.linalg.slogdet(full)
    trace_eigenvalues, trace_pass = trace_inertia(trace_matrix)
    nontrace = NONTRACE_COEFFICIENTS @ alpha[1:]
    return {
        "name": name,
        "alpha_exact": [str(value) for value in exact_alpha],
        "alpha_float": alpha.tolist(),
        "fixed_point_residuals_exact": [str(value) for value in residuals],
        "planck_coefficient": planck_coefficient(alpha),
        "full_rank": int(np.linalg.matrix_rank(full, tol=1.0e-9)),
        "full_smallest_singular_value": float(singular[-1]),
        "full_condition_number": float(singular[0] / singular[-1]),
        "full_slogdet": [float(sign), float(logdet)],
        "full_inertia": {
            "positive": int(np.count_nonzero(eigenvalues > 1.0e-8)),
            "negative": int(np.count_nonzero(eigenvalues < -1.0e-8)),
            "zero": int(np.count_nonzero(np.abs(eigenvalues) <= 1.0e-8)),
        },
        "trace_block_eigenvalues": trace_eigenvalues.tolist(),
        "trace_block_einstein_inertia_pass": trace_pass,
        "nontrace_residues": [
            {"multiplicity": multiplicity, "value": float(value)}
            for multiplicity, value in zip(NONTRACE_MULTIPLICITIES, nontrace)
        ],
        "constraint_tangent_eigenvalues": [
            [float(value.real), float(value.imag)] for value in tangent
        ],
        "maximum_constraint_tangent_growth_rate": float(max(tangent.real)),
        **diagnostics,
        "physical_ghost_verdict": "deferred_to_constraint_gauge_reduced_residues",
    }


def full_acceleration_spectrum_regression(
    cache: Dict[str, np.ndarray | dict],
    acceleration_orders: Tuple[np.ndarray, ...],
) -> dict:
    cases = []
    coefficient_cases = []
    for order in range(1, 8):
        alpha = np.zeros(8)
        alpha[order] = 1.0
        coefficient_cases.append((f"order_{order}", alpha))
    coefficient_cases.append((
        "generic_all_order_combination",
        np.array([0.0, 1.0, -0.37, 0.021, -0.0017, 0.00013, -8.0e-6, 3.0e-7]),
    ))
    for name, alpha in coefficient_cases:
        full = sum(
            alpha[order] * acceleration_orders[order - 1]
            for order in range(1, 8)
        )
        full_eigenvalues = np.linalg.eigvalsh(full)
        trace_matrix = np.tensordot(alpha, cache["m0"], axes=(0, 0))
        trace_eigenvalues = np.linalg.eigvalsh(
            trace_symmetric_representative(trace_matrix)
        )
        residues = NONTRACE_COEFFICIENTS @ alpha[1:]
        expected = list(trace_eigenvalues)
        for multiplicity, value in zip(NONTRACE_MULTIPLICITIES, residues):
            expected.extend([float(value)] * multiplicity)
        expected = np.sort(np.array(expected))
        absolute_error = float(np.max(np.abs(np.sort(full_eigenvalues) - expected)))
        scale = max(1.0, float(np.max(np.abs(expected))))
        relative_error = absolute_error / scale
        _require(relative_error < 1.0e-12,
                 f"120-mode spectrum decomposition failed for {name}")
        cases.append({
            "case": name,
            "full_rank": int(np.linalg.matrix_rank(full, tol=1.0e-8)),
            "trace_eigenvalues": trace_eigenvalues.tolist(),
            "nontrace_residues": residues.tolist(),
            "maximum_absolute_multiset_error": absolute_error,
            "maximum_relative_multiset_error": relative_error,
        })
    return {
        "status": "PASS",
        "full_dimension": 120,
        "trace_dimension": 4,
        "nontrace_multiplicities": list(NONTRACE_MULTIPLICITIES),
        "multiplicity_sum": sum(NONTRACE_MULTIPLICITIES),
        "cases": cases,
    }


def deterministic_joint_scan(
    cache: Dict[str, np.ndarray | dict], sample_count: int, seed: int = 731923
) -> dict:
    if not isinstance(sample_count, int) or isinstance(sample_count, bool):
        raise TypeError("sample_count must be an ordinary integer")
    if sample_count < 1:
        raise ValueError("sample_count must be positive")
    equations = np.array([
        [float(value) for value in row]
        for row in fixed_point_equation_coefficients(Fraction(1), (1, 1, 1))
    ])
    difference = equations[0] - equations[1]
    rng = np.random.default_rng(seed)
    scales = np.array([0.2, 0.02, 0.002, 0.0002, 0.00002])
    batch_size = 20000
    best = None
    nontrace_feasible = 0
    trace_passed = 0
    tested = 0
    stable = 0
    numerical_gate_rejections = 0
    corrected_only = []

    for start in range(0, sample_count, batch_size):
        size = min(batch_size, sample_count - start)
        higher = rng.uniform(-1.0, 1.0, (size, 5)) * scales
        alpha2 = -(difference[1] + higher @ difference[3:]) / difference[2]
        local = np.column_stack([alpha2, higher])
        nontrace = -1.0 + local @ NONTRACE_COEFFICIENTS[:, 1:].T
        indices = np.flatnonzero(np.all(nontrace < -NONTRACE_MARGIN, axis=1))
        nontrace_feasible += len(indices)
        for index in indices:
            alpha = np.r_[0.0, 1.0, local[index]]
            alpha[0] = -sum(
                equations[0, order] * alpha[order] for order in range(1, 8)
            ) / equations[0, 0]
            trace_matrix = np.tensordot(alpha, cache["m0"], axes=(0, 0))
            trace_eigenvalues, trace_pass = trace_inertia(trace_matrix)
            if not trace_pass:
                continue
            trace_passed += 1
            planck = planck_coefficient(alpha)
            _require(planck > 0, "nontrace gate did not imply positive Planck coefficient")
            try:
                tangent, _, diagnostics = tangent_spectrum(alpha, cache)
            except (ValueError, np.linalg.LinAlgError):
                numerical_gate_rejections += 1
                continue
            tested += 1
            growth = float(max(tangent.real))
            stable += int(growth < -STABILITY_TOLERANCE)
            wrong_eigenvalues = legacy_lower_triangle_spectrum_for_certificate(
                trace_matrix
            )
            old_pass = (
                np.count_nonzero(wrong_eigenvalues > TRACE_INERTIA_TOLERANCE) == 1
                and np.count_nonzero(wrong_eigenvalues < -TRACE_INERTIA_TOLERANCE) == 3
            )
            record = {
                "global_index": start + int(index),
                "growth": growth,
                "alpha": alpha.tolist(),
                "tangent_eigenvalues": [
                    [float(value.real), float(value.imag)] for value in tangent
                ],
                "trace_eigenvalues": trace_eigenvalues.tolist(),
                "planck_coefficient": planck,
                "nontrace_residues": nontrace[index].tolist(),
                **diagnostics,
            }
            if best is None or growth < best["growth"]:
                best = record
            if not old_pass:
                corrected_only.append({
                    **record,
                    "invalid_legacy_eigvalsh_M": wrong_eigenvalues.tolist(),
                })

    _require(best is not None, "scan produced no fully tested point")
    corrected_alpha_bytes = json.dumps(
        [item["alpha"] for item in corrected_only],
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")
    correction_certificate = {
        "count": len(corrected_only),
        "global_indices": [item["global_index"] for item in corrected_only],
        "alpha_rows_sha256": hashlib.sha256(corrected_alpha_bytes).hexdigest(),
        "minimum_growth": (
            min(item["growth"] for item in corrected_only)
            if corrected_only else None
        ),
        "maximum_growth": (
            max(item["growth"] for item in corrected_only)
            if corrected_only else None
        ),
        "stable_count": sum(
            item["growth"] < -STABILITY_TOLERANCE for item in corrected_only
        ),
        "records": corrected_only,
    }
    return {
        "seed": seed,
        "samples": sample_count,
        "domain": {
            "alpha3": [-0.2, 0.2],
            "alpha4": [-0.02, 0.02],
            "alpha5": [-0.002, 0.002],
            "alpha6": [-0.0002, 0.0002],
            "alpha7": [-0.00002, 0.00002],
            "alpha1": 1.0,
            "alpha2_alpha0": "solved from the exact rho=1 fixed-point equations",
        },
        "nontrace_inertia_feasible_points": nontrace_feasible,
        "trace_inertia_pass_points": trace_passed,
        "joint_necessary_condition_points_tested": tested,
        "numerical_gate_rejections": numerical_gate_rejections,
        "stable_joint_points_found": stable,
        "best": best,
        "legacy_trace_algorithm_correction": correction_certificate,
        "scope": (
            "finite deterministic coupling scan on the equal-internal-radius, "
            "rho=H_star^2/y=1 slice; not a no-go proof, not the full equal-radius "
            "branch, and not an unequal-radius scan"
        ),
    }


def generate_result(sample_count: int = 4_000_000) -> Tuple[dict, dict]:
    cache = build_exact_linearization_cache()
    acceleration_orders = full_acceleration_orders()
    spectrum = full_acceleration_spectrum_regression(cache, acceleration_orders)
    result = {
        "status": "PASS",
        "classification": "equal-internal-radius, rho=1 controlled-slice audit",
        "fixed_point": {
            "H2": 1,
            "yc": 1,
            "yL": 1,
            "yR": 1,
            "rho_H2_over_y": 1,
        },
        "analytic_local_orders": list(range(8)),
        "topological_order": 8,
        "derivative_method": DERIVATIVE_METHOD,
        "linearization_cache_metadata": cache["metadata"],
        "numerical_gates": {
            "trace_inertia_tolerance": TRACE_INERTIA_TOLERANCE,
            "nontrace_negative_margin": NONTRACE_MARGIN,
            "stability_tolerance": STABILITY_TOLERANCE,
            "maximum_block_condition_number": MAX_BLOCK_CONDITION_NUMBER,
            "minimum_constraint_gradient_norm": MIN_CONSTRAINT_GRADIENT_NORM,
            "maximum_constraint_tangent_leakage": MAX_CONSTRAINT_TANGENT_LEAKAGE,
        },
        "einstein_trace_regression": einstein_trace_regression(cache),
        "witnesses": [
            audit_witness(
                "stable_but_fails_necessary_Einstein_inertia_condition",
                STABLE_BUT_EINSTEIN_INERTIA_INVALID,
                cache,
                acceleration_orders,
            ),
            audit_witness(
                "passes_necessary_Einstein_inertia_but_is_constraint_tangent_unstable",
                EINSTEIN_INERTIA_PASS_BUT_UNSTABLE,
                cache,
                acceleration_orders,
            ),
        ],
        "joint_scan": deterministic_joint_scan(cache, sample_count),
        "physical_residue_verdict": "deferred_to_constraint_gauge_reduced_analysis",
    }
    return result, spectrum


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=4_000_000)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--spectrum-output", type=Path)
    args = parser.parse_args()
    result, spectrum = generate_result(args.samples)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    spectrum_encoded = json.dumps(spectrum, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    if args.spectrum_output:
        args.spectrum_output.write_text(spectrum_encoded, encoding="utf-8")
    print(encoded, end="")


if __name__ == "__main__":
    main()
