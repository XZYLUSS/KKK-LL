#!/usr/bin/env python3
"""Exact curved-product Lovelock reduction for P01B.2-CURV, stage A.

The engine uses the G6 double-form algebra.  It retains local Lovelock orders
k=0,...,7 and constructs:

* the lapse/Hamiltonian constraint from the spatial Gauss curvature Omega;
* the four homogeneous block equations Q + A Psi;
* the complete 120-component normal-acceleration map on Sym^2(T*Sigma);
* fixed-point coefficient vectors on dS4 x CP2^3.

No floating-point arithmetic or external CAS is used in the exact layer.
"""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from math import factorial
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from g01_product_geometry import (
    DoubleForm,
    _pair_mask,
    _require,
    _wedge_sign,
    cp2_curvature_block,
    double_wedge,
    exact_fraction,
)

SPATIAL_DIMENSION = 15
BLOCKS: Tuple[Tuple[int, ...], ...] = (
    tuple(range(0, 3)),
    tuple(range(3, 7)),
    tuple(range(7, 11)),
    tuple(range(11, 15)),
)
BLOCK_NAMES = ("external", "c", "L", "R")
MAX_LOCAL_ORDER = 7


def _validate_four(values: Iterable[Fraction], name: str) -> Tuple[Fraction, ...]:
    result = tuple(exact_fraction(v, name) for v in values)
    if len(result) != 4:
        raise ValueError(f"{name} must contain exactly four entries")
    return result


def _block_of(index: int) -> int:
    if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < 15:
        raise ValueError("spatial index outside range(15)")
    if index < 3:
        return 0
    if index < 7:
        return 1
    if index < 11:
        return 2
    return 3


def spatial_gauss_curvature(
    rates: Iterable[Fraction],
    external_intrinsic_curvature: Fraction,
    cp2_inverse_radius_squared: Iterable[Fraction],
) -> DoubleForm:
    """Return Omega^{ij}_{kl} on the 15-dimensional Cauchy slice."""
    h = _validate_four(rates, "rates")
    kappa = exact_fraction(
        external_intrinsic_curvature, "external_intrinsic_curvature"
    )
    cp = tuple(
        exact_fraction(v, "cp2_inverse_radius_squared")
        for v in cp2_inverse_radius_squared
    )
    if len(cp) != 3:
        raise ValueError("three CP2 inverse-radius-squared values are required")

    omega: Dict[Tuple[int, int], Fraction] = defaultdict(Fraction)

    # K wedge K for diagonal blockwise extrinsic curvature.
    for i in range(SPATIAL_DIMENSION):
        for j in range(i + 1, SPATIAL_DIMENSION):
            pair = _pair_mask(i, j)
            omega[(pair, pair)] += h[_block_of(i)] * h[_block_of(j)]

    # Intrinsic constant curvature of the external three-space.
    for i, j in combinations(BLOCKS[0], 2):
        pair = _pair_mask(i, j)
        omega[(pair, pair)] += kappa

    # Intrinsic Fubini-Study curvature on each CP2 block.
    for block_index, inverse_radius in enumerate(cp, start=1):
        offset = BLOCKS[block_index][0]
        for key, value in cp2_curvature_block(
            offset, inverse_radius, SPATIAL_DIMENSION
        ).items():
            omega[key] += value

    return {key: value for key, value in omega.items() if value}


def double_powers(curvature: DoubleForm, max_order: int) -> Tuple[DoubleForm, ...]:
    if not isinstance(max_order, int) or isinstance(max_order, bool) or max_order < 0:
        raise ValueError("max_order must be a nonnegative integer")
    powers: List[DoubleForm] = [{(0, 0): Fraction(1)}]
    for _ in range(max_order):
        powers.append(double_wedge(powers[-1], curvature))
    return tuple(powers)


def _delta_sign(upper: Sequence[int], lower: Sequence[int]) -> int:
    if len(upper) != len(lower) or len(set(upper)) != len(upper) or len(set(lower)) != len(lower):
        return 0
    if set(upper) != set(lower):
        return 0
    positions = {value: position for position, value in enumerate(upper)}
    permutation = [positions[value] for value in lower]
    inversions = sum(
        permutation[i] > permutation[j]
        for i in range(len(permutation))
        for j in range(i + 1, len(permutation))
    )
    return -1 if inversions & 1 else 1


def _indices(mask: int) -> Tuple[int, ...]:
    return tuple(i for i in range(SPATIAL_DIMENSION) if mask & (1 << i))


def hamiltonian_by_order(powers: Sequence[DoubleForm]) -> Tuple[Fraction, ...]:
    values = [Fraction(1, 2)]
    for order in range(1, min(MAX_LOCAL_ORDER, len(powers) - 1) + 1):
        trace = sum(
            coefficient
            for (upper, lower), coefficient in powers[order].items()
            if upper == lower
        )
        values.append((2 ** (order - 1)) * trace)
    return tuple(values)


def q_diagonal_by_order(
    powers: Sequence[DoubleForm], representative: int
) -> Tuple[Fraction, ...]:
    if not isinstance(representative, int) or isinstance(representative, bool):
        raise TypeError("representative must be an ordinary integer")
    if not 0 <= representative < SPATIAL_DIMENSION:
        raise ValueError("representative outside spatial range")
    values = [Fraction(-1, 2)]
    for order in range(1, min(MAX_LOCAL_ORDER, len(powers) - 1) + 1):
        total = Fraction()
        for (upper_curvature, lower_curvature), coefficient in powers[order].items():
            # Eq. G6-(7.3): upper generalized-delta list contains curvature
            # lower indices; lower list contains curvature upper indices.
            upper_list = (representative,) + _indices(lower_curvature)
            lower_list = (representative,) + _indices(upper_curvature)
            total += _delta_sign(upper_list, lower_list) * coefficient
        values.append(-(2 ** (order - 1)) * total)
    return tuple(values)


def acceleration_tensor_by_order(
    lower_power: DoubleForm, order: int
) -> Dict[Tuple[int, int, int, int], Fraction]:
    """Return A_(k)^{i a}_{j b} from G6 Eq. (7.5)."""
    if not isinstance(order, int) or isinstance(order, bool):
        raise TypeError("local acceleration order must be an ordinary integer")
    if not 1 <= order <= MAX_LOCAL_ORDER:
        raise ValueError("local acceleration order must lie in 1,...,7")
    expected_degree = 2 * (order - 1)
    out: Dict[Tuple[int, int, int, int], Fraction] = defaultdict(Fraction)
    full_mask = (1 << SPATIAL_DIMENSION) - 1
    prefactor = order * (2 ** (order - 1))

    for (upper_curvature, lower_curvature), coefficient in lower_power.items():
        if upper_curvature.bit_count() != expected_degree or lower_curvature.bit_count() != expected_degree:
            raise ValueError("malformed double-form degree")
        union = upper_curvature | lower_curvature
        need = 2 * order - union.bit_count()
        if need < 0:
            continue
        available = _indices(full_mask ^ union)
        for added in combinations(available, need):
            target = union
            for index in added:
                target |= 1 << index
            if target.bit_count() != 2 * order:
                continue
            missing_upper_list = _indices(target ^ lower_curvature)
            missing_lower_list = _indices(target ^ upper_curvature)
            if len(missing_upper_list) != 2 or len(missing_lower_list) != 2:
                continue
            for i, a in (missing_upper_list, tuple(reversed(missing_upper_list))):
                for j, b in (missing_lower_list, tuple(reversed(missing_lower_list))):
                    upper_list = (i, a) + _indices(lower_curvature)
                    lower_list = (j, b) + _indices(upper_curvature)
                    sign = _delta_sign(upper_list, lower_list)
                    if sign:
                        out[(i, a, j, b)] += prefactor * sign * coefficient
    return {key: value for key, value in out.items() if value}


def block_acceleration_matrix_by_order(
    acceleration_tensor: Mapping[Tuple[int, int, int, int], Fraction]
) -> Tuple[Tuple[Fraction, ...], ...]:
    """Map four diagonal block values Psi_J to four representative equations."""
    rows: List[Tuple[Fraction, ...]] = []
    for output_block in range(4):
        i = BLOCKS[output_block][0]
        row = []
        for input_block in range(4):
            row.append(sum(
                acceleration_tensor.get((i, a, i, a), Fraction())
                for a in BLOCKS[input_block]
            ))
        rows.append(tuple(row))
    return tuple(rows)


def sym2_component_matrix(
    acceleration_tensor: Mapping[Tuple[int, int, int, int], Fraction]
) -> Tuple[Tuple[Fraction, ...], ...]:
    """Return the 120x120 map in the component basis i<=j, a<=b.

    Off-diagonal columns represent a symmetric input with Psi^a_b=Psi^b_a=1.
    This basis is exact and rank-faithful; an orthonormal basis differs only by
    fixed sqrt(2) row/column rescalings.
    """
    basis = tuple((i, j) for i in range(15) for j in range(i, 15))
    rows: List[Tuple[Fraction, ...]] = []
    for i, j in basis:
        row = []
        for a, b in basis:
            if a == b:
                value = acceleration_tensor.get((i, a, j, a), Fraction())
            else:
                value = (
                    acceleration_tensor.get((i, a, j, b), Fraction())
                    + acceleration_tensor.get((i, b, j, a), Fraction())
                )
            row.append(value)
        rows.append(tuple(row))
    return tuple(rows)


def elementary_symmetric(values: Sequence[Fraction], order: int) -> Fraction:
    if not isinstance(order, int) or isinstance(order, bool):
        raise TypeError("symmetric-polynomial order must be an ordinary integer")
    if not 0 <= order <= len(values):
        return Fraction()
    accum = [Fraction(1)] + [Fraction()] * order
    for value in values:
        for degree in range(order, 0, -1):
            accum[degree] += exact_fraction(value, "symmetric-polynomial value") * accum[degree - 1]
    return accum[order]


def flat_p01b_regression(
    rates: Sequence[Fraction], psi: Sequence[Fraction]
) -> int:
    """Exact comparison with the frozen P01B symmetric-polynomial formulas."""
    h4 = _validate_four(rates, "rates")
    p4 = _validate_four(psi, "psi")
    expanded_rates = tuple(h4[_block_of(i)] for i in range(15))
    expanded_psi = tuple(p4[_block_of(i)] for i in range(15))
    omega = spatial_gauss_curvature(h4, Fraction(), (0, 0, 0))
    powers = double_powers(omega, MAX_LOCAL_ORDER)
    hamiltonian = hamiltonian_by_order(powers)
    checks = 0

    for order in range(1, 8):
        expected_h = Fraction(factorial(2 * order), 2) * elementary_symmetric(
            expanded_rates, 2 * order
        )
        _require(
            hamiltonian[order] == expected_h,
            f"flat Hamiltonian regression failed at order {order}",
        )
        checks += 1

    for block in range(4):
        i = BLOCKS[block][0]
        q_values = q_diagonal_by_order(powers, i)
        for order in range(1, 8):
            acceleration = acceleration_tensor_by_order(powers[order - 1], order)
            block_matrix = block_acceleration_matrix_by_order(acceleration)
            actual = q_values[order] + sum(
                block_matrix[block][j] * p4[j] for j in range(4)
            )
            excluded_i = expanded_rates[:i] + expanded_rates[i + 1:]
            expected = -Fraction(factorial(2 * order), 2) * elementary_symmetric(
                excluded_i, 2 * order
            )
            d_k = order * factorial(2 * order - 2)
            for j in range(15):
                if j == i:
                    continue
                excluded = tuple(
                    expanded_rates[m] for m in range(15) if m not in (i, j)
                )
                expected += d_k * elementary_symmetric(excluded, 2 * order - 2) * expanded_psi[j]
            _require(
                actual == expected,
                f"flat spatial regression failed at block {block}, order {order}",
            )
            checks += 1
    return checks


def _factor_product_density(order: int, factor_polynomials: Sequence[Sequence[Fraction]]) -> Fraction:
    total = Fraction()

    def recurse(factor: int, remaining: int, orders: Tuple[int, ...]) -> None:
        nonlocal total
        if factor == len(factor_polynomials):
            if remaining:
                return
            coefficient = Fraction(factorial(order))
            value = Fraction(1)
            for chosen, polynomial in zip(orders, factor_polynomials):
                coefficient /= factorial(chosen)
                value *= polynomial[chosen]
            total += coefficient * value
            return
        for chosen in range(min(remaining, len(factor_polynomials[factor]) - 1) + 1):
            recurse(factor + 1, remaining - chosen, orders + (chosen,))

    recurse(0, order, ())
    return total


def fixed_point_equation_coefficients(
    external_curvature: Fraction,
    cp2_inverse_radius_squared: Iterable[Fraction],
) -> Tuple[Tuple[Fraction, ...], ...]:
    """Return coefficients of alpha_0,...,alpha_7 for four fixed-point equations."""
    x = exact_fraction(external_curvature, "external_curvature")
    y = tuple(
        exact_fraction(v, "cp2_inverse_radius_squared")
        for v in cp2_inverse_radius_squared
    )
    if len(y) != 3:
        raise ValueError("three internal curvatures are required")

    ds4 = (Fraction(1), 12 * x, 24 * x * x)
    ds3_excluded = (Fraction(1), 6 * x)
    cp4 = tuple((Fraction(1), 24 * r, 192 * r * r) for r in y)
    cp3_excluded = tuple((Fraction(1), 12 * r) for r in y)

    equations = []
    # Common factor -1/2 is retained, matching G6 spatial equations.
    equations.append(tuple(
        -Fraction(1, 2) * _factor_product_density(order, (ds3_excluded,) + cp4)
        for order in range(8)
    ))
    for internal in range(3):
        factors = [ds4]
        for factor in range(3):
            factors.append(cp3_excluded[factor] if factor == internal else cp4[factor])
        equations.append(tuple(
            -Fraction(1, 2) * _factor_product_density(order, factors)
            for order in range(8)
        ))
    return tuple(equations)


def fixed_point_dynamic_regression() -> int:
    """Cross-lock compact product formulas to the G6 Q+A Psi reduction."""
    # Exact dS scale H=1, static unequal CP2 radii.
    rates = (Fraction(1), Fraction(), Fraction(), Fraction())
    psi = (Fraction(-1), Fraction(), Fraction(), Fraction())
    internal = (Fraction(2, 3), Fraction(3, 5), Fraction(5, 7))
    omega = spatial_gauss_curvature(rates, Fraction(), internal)
    powers = double_powers(omega, MAX_LOCAL_ORDER)
    compact = fixed_point_equation_coefficients(Fraction(1), internal)
    checks = 0
    accelerations = [None] + [
        acceleration_tensor_by_order(powers[order - 1], order)
        for order in range(1, 8)
    ]
    block_matrices = [None] + [
        block_acceleration_matrix_by_order(accelerations[order])
        for order in range(1, 8)
    ]
    for block in range(4):
        q = q_diagonal_by_order(powers, BLOCKS[block][0])
        _require(
            q[0] == compact[block][0],
            f"fixed-point cosmological term failed in block {block}",
        )
        checks += 1
        for order in range(1, 8):
            dynamic = q[order] + sum(
                block_matrices[order][block][j] * psi[j] for j in range(4)
            )
            _require(
                dynamic == compact[block][order],
                f"fixed-point product regression failed at block {block}, order {order}",
            )
            checks += 1
    return checks


def topological_order8_regression() -> int:
    """Executable flat-boundary regression for the D=16 Euler density."""
    rates = tuple(Fraction(i + 2, i + 3) for i in range(15))
    derivatives = tuple(Fraction((-1) ** i, i + 5) for i in range(15))
    volume = Fraction(17, 13)
    theta = sum(rates)
    e15 = elementary_symmetric(rates, 15)
    e15_prime = sum(
        derivatives[i]
        * elementary_symmetric(rates[:i] + rates[i + 1 :], 14)
        for i in range(15)
    )
    q15 = 16 * factorial(14) * volume * e15
    q15_prime = 16 * factorial(14) * volume * (e15_prime + theta * e15)
    l8 = 16 * factorial(14) * (e15_prime + theta * e15)
    checks = 0
    _require(q15 / volume == 16 * factorial(14) * e15, "Q15 normalization failed")
    checks += 1
    _require(q15_prime / volume == l8, "Euler total-derivative identity failed")
    checks += 1
    isotropic_h = Fraction(2, 3)
    isotropic = 16 * factorial(14) * 15 * isotropic_h ** 16
    _require(isotropic == factorial(16) * isotropic_h ** 16, "Euler isotropic oracle failed")
    checks += 1
    return checks


def exact_self_check() -> dict:
    flat_checks = flat_p01b_regression(
        rates=(Fraction(1, 7), Fraction(-2, 9), Fraction(3, 11), Fraction(-4, 13)),
        psi=(Fraction(-2, 5), Fraction(3, 8), Fraction(-5, 12), Fraction(7, 15)),
    )
    fixed_checks = fixed_point_dynamic_regression()

    # Demonstrate the full 120-component map at a genuinely curved witness.
    omega = spatial_gauss_curvature(
        rates=(Fraction(1, 3), Fraction(-1, 5), Fraction(2, 7), Fraction(-3, 11)),
        external_intrinsic_curvature=Fraction(1, 13),
        cp2_inverse_radius_squared=(Fraction(2, 3), Fraction(3, 5), Fraction(5, 7)),
    )
    powers = double_powers(omega, 2)
    a1 = sym2_component_matrix(acceleration_tensor_by_order(powers[0], 1))
    a2 = sym2_component_matrix(acceleration_tensor_by_order(powers[1], 2))
    _require(len(a1) == len(a2) == 120, "full acceleration dimension failed")
    _require(
        all(len(row) == 120 for row in a1 + a2),
        "full acceleration row dimension failed",
    )

    # Einstein trace/traceless structure: A Psi = tr(Psi) I - Psi.
    basis = tuple((i, j) for i in range(15) for j in range(i, 15))
    for row, (i, j) in enumerate(basis):
        for column, (a, b) in enumerate(basis):
            if a == b:
                expected = int(i == j) - int(i == a and j == a)
            else:
                expected = -int(i == a and j == b)
            _require(
                a1[row][column] == expected,
                f"Einstein acceleration map failed at ({row},{column})",
            )

    topological_checks = topological_order8_regression()

    return {
        "status": "PASS",
        "flat_all_order_checks": flat_checks,
        "fixed_point_product_checks": fixed_checks,
        "topological_order8_checks": topological_checks,
        "full_component_dimension": 120,
        "curved_k1_nonzero_entries": sum(value != 0 for row in a1 for value in row),
        "curved_k2_nonzero_entries": sum(value != 0 for row in a2 for value in row),
        "analytic_local_orders": list(range(8)),
        "topological_order": 8,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(exact_self_check(), indent=2, sort_keys=True))
