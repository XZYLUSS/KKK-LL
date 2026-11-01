#!/usr/bin/env python3
"""Dependency-free exact G01 product-geometry engine.

All arithmetic is integer or fractions.Fraction.  The module independently
constructs the real orthonormal CP2 curvature operator, forms Lovelock double
wedge powers, and compares them with the ordinary-multinomial product formula.
"""

from __future__ import annotations

import sys
sys.dont_write_bytecode = True

from collections import defaultdict
from fractions import Fraction
from math import factorial
from typing import Dict, Iterable, Mapping, Tuple

Monomial = Tuple[int, int, int]
Polynomial = Dict[Monomial, Fraction]
DoubleForm = Dict[Tuple[int, int], Fraction]


def _require(condition: bool, message: str) -> None:
    """Fail closed even when CPython is executed with ``-O``."""
    if not condition:
        raise RuntimeError(message)


def exact_fraction(value: object, name: str) -> Fraction:
    """Accept only genuinely exact rational input at public exact boundaries."""
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise TypeError(f"{name} must be an int or fractions.Fraction")
    return Fraction(value)


def _pair_mask(a: int, b: int) -> int:
    if any(not isinstance(i, int) or isinstance(i, bool) for i in (a, b)):
        raise TypeError("pair indices must be ordinary integers")
    if not 0 <= a < b:
        raise ValueError("pair indices must satisfy 0 <= a < b")
    return (1 << a) | (1 << b)


def _wedge_sign(mask_left: int, mask_right: int) -> int:
    if mask_left & mask_right:
        return 0
    inversions = 0
    active = mask_left
    while active:
        low = active & -active
        i = low.bit_length() - 1
        active ^= low
        inversions += (mask_right & ((1 << i) - 1)).bit_count()
    return -1 if inversions & 1 else 1


def cp2_riemann_unit(a: int, b: int, c: int, d: int) -> int:
    """R_abcd for CP2 at inverse-radius-squared one.

    Basis: J e0=e1, J e1=-e0, J e2=e3, J e3=-e2.
    The holomorphic sectional curvature is four and Ricci is 6 g.
    """
    if any(not isinstance(i, int) or isinstance(i, bool) for i in (a, b, c, d)):
        raise TypeError("indices must be ordinary integers")
    if any(i < 0 or i >= 4 for i in (a, b, c, d)):
        raise ValueError("CP2 indices must lie in range(4)")
    j = (
        (0, -1, 0, 0),
        (1, 0, 0, 0),
        (0, 0, 0, -1),
        (0, 0, 1, 0),
    )
    delta = lambda p, q: int(p == q)
    return (
        delta(a, c) * delta(b, d)
        - delta(a, d) * delta(b, c)
        + j[a][c] * j[b][d]
        - j[a][d] * j[b][c]
        + 2 * j[a][b] * j[c][d]
    )


def cp2_curvature_block(
    offset: int,
    inverse_radius_squared: Fraction,
    ambient_dimension: int,
) -> DoubleForm:
    if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
        raise ValueError("offset must be a nonnegative integer")
    if (
        not isinstance(ambient_dimension, int)
        or isinstance(ambient_dimension, bool)
        or ambient_dimension < 4
    ):
        raise ValueError("ambient_dimension must be an integer at least four")
    if offset + 4 > ambient_dimension:
        raise ValueError("CP2 block does not fit inside the declared ambient dimension")
    r = exact_fraction(inverse_radius_squared, "inverse_radius_squared")
    out: DoubleForm = {}
    for a in range(4):
        for b in range(a + 1, 4):
            upper = _pair_mask(offset + a, offset + b)
            for c in range(4):
                for d in range(c + 1, 4):
                    value = r * cp2_riemann_unit(a, b, c, d)
                    if value:
                        lower = _pair_mask(offset + c, offset + d)
                        out[(upper, lower)] = value
    return out


def double_wedge(left: DoubleForm, right: DoubleForm) -> DoubleForm:
    out: Dict[Tuple[int, int], Fraction] = defaultdict(Fraction)
    for (upper_l, lower_l), coeff_l in left.items():
        for (upper_r, lower_r), coeff_r in right.items():
            sign_u = _wedge_sign(upper_l, upper_r)
            if not sign_u:
                continue
            sign_l = _wedge_sign(lower_l, lower_r)
            if not sign_l:
                continue
            out[(upper_l | upper_r, lower_l | lower_r)] += (
                coeff_l * coeff_r * sign_u * sign_l
            )
    return {key: value for key, value in out.items() if value}


def lovelock_densities(curvature: DoubleForm, dimension: int) -> Tuple[Fraction, ...]:
    if not isinstance(dimension, int) or isinstance(dimension, bool) or dimension < 0:
        raise ValueError("dimension must be a nonnegative integer")
    power: DoubleForm = {(0, 0): Fraction(1)}
    values = [Fraction(1)]
    for order in range(1, dimension // 2 + 1):
        power = double_wedge(power, curvature)
        diagonal_trace = sum(
            coeff for (upper, lower), coeff in power.items() if upper == lower
        )
        values.append((2 ** order) * diagonal_trace)
    return tuple(values)


def single_factor_integral(order: int, x: Monomial, factor: int) -> Polynomial:
    """Return I_order/pi^2 for x_A=b_A^2 as an exact polynomial."""
    if any(not isinstance(v, int) or isinstance(v, bool) for v in (order, factor)):
        raise TypeError("order and factor must be ordinary integers")
    if order not in (0, 1, 2) or factor not in (0, 1, 2):
        raise ValueError("order and factor outside the G01 single-factor domain")
    exponent = list(x)
    if any(exponent):
        raise ValueError("base monomial must be (0,0,0)")
    if order == 0:
        exponent[factor] = 2
        coefficient = Fraction(1, 2)
    elif order == 1:
        exponent[factor] = 1
        coefficient = Fraction(12)
    else:
        coefficient = Fraction(96)
    return {tuple(exponent): coefficient}


def poly_add(left: Polynomial, right: Polynomial) -> Polynomial:
    out = dict(left)
    for monomial, coefficient in right.items():
        out[monomial] = out.get(monomial, Fraction()) + coefficient
    return {m: c for m, c in out.items() if c}


def poly_scale(poly: Polynomial, scalar: Fraction) -> Polynomial:
    scalar = exact_fraction(scalar, "scalar")
    return {m: scalar * c for m, c in poly.items() if scalar * c}


def poly_multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    out: Dict[Monomial, Fraction] = defaultdict(Fraction)
    for monomial_l, coefficient_l in left.items():
        for monomial_r, coefficient_r in right.items():
            monomial = tuple(a + b for a, b in zip(monomial_l, monomial_r))
            out[monomial] += coefficient_l * coefficient_r
    return {m: c for m, c in out.items() if c}


def product_integral_polynomial(order: int) -> Polynomial:
    if not isinstance(order, int) or isinstance(order, bool) or not 0 <= order <= 6:
        raise ValueError("G01 product order must lie in 0,...,6")
    answer: Polynomial = {}
    zero = (0, 0, 0)
    for p in range(3):
        for q in range(3):
            for r in range(3):
                if p + q + r != order:
                    continue
                term = poly_multiply(
                    poly_multiply(single_factor_integral(p, zero, 0),
                                  single_factor_integral(q, zero, 1)),
                    single_factor_integral(r, zero, 2),
                )
                multinomial = Fraction(
                    factorial(order), factorial(p) * factorial(q) * factorial(r)
                )
                answer = poly_add(answer, poly_scale(term, multinomial))
    return answer


def evaluate_polynomial(poly: Mapping[Monomial, Fraction], values: Iterable[Fraction]) -> Fraction:
    x = tuple(exact_fraction(v, "polynomial evaluation value") for v in values)
    if len(x) != 3:
        raise ValueError("exactly three radius-squared values are required")
    return sum(
        coefficient * x[0] ** powers[0] * x[1] ** powers[1] * x[2] ** powers[2]
        for powers, coefficient in poly.items()
    )


def local_product_formula(order: int, inverse_radius_squared: Iterable[Fraction]) -> Fraction:
    if not isinstance(order, int) or isinstance(order, bool):
        raise TypeError("order must be an ordinary integer")
    radii = tuple(
        exact_fraction(v, "inverse_radius_squared")
        for v in inverse_radius_squared
    )
    if len(radii) != 3 or order < 0 or order > 6:
        raise ValueError("three curvature scales and order 0,...,6 are required")
    ell = lambda p, r: (Fraction(1), 24 * r, 192 * r * r)[p]
    total = Fraction()
    for p in range(3):
        for q in range(3):
            for s in range(3):
                if p + q + s == order:
                    total += Fraction(
                        factorial(order), factorial(p) * factorial(q) * factorial(s)
                    ) * ell(p, radii[0]) * ell(q, radii[1]) * ell(s, radii[2])
    return total


EQUAL_RADIUS_COEFFICIENTS = (
    Fraction(1, 8),
    Fraction(9),
    Fraction(504),
    Fraction(20736),
    Fraction(580608),
    Fraction(9953280),
    Fraction(79626240),
)


def exact_self_check() -> dict:
    checks = 0

    # CP2 Ricci and curvature scalars from the explicit real tensor.
    for b in range(4):
        for d in range(4):
            expected = 6 if b == d else 0
            actual = sum(cp2_riemann_unit(a, b, a, d) for a in range(4))
            _require(actual == expected, "CP2 Ricci regression failed")
            checks += 1

    cp2 = cp2_curvature_block(0, Fraction(1), 4)
    cp2_lovelock = lovelock_densities(cp2, 4)
    _require(
        cp2_lovelock == (Fraction(1), Fraction(24), Fraction(192)),
        "CP2 Lovelock-density regression failed",
    )
    checks += 3

    # Twelve-dimensional direct double-form calculation at unequal rational radii.
    inverse_radii = (Fraction(2, 3), Fraction(3, 5), Fraction(5, 7))
    product_curvature: DoubleForm = {}
    for block, r in enumerate(inverse_radii):
        product_curvature.update(cp2_curvature_block(4 * block, r, 12))
    direct = lovelock_densities(product_curvature, 12)
    for order in range(7):
        _require(
            direct[order] == local_product_formula(order, inverse_radii),
            f"direct-product Lovelock regression failed at order {order}",
        )
        checks += 1

    # Unequal-radius integrated panel and equal-radius C00 regression.
    for order in range(7):
        poly = product_integral_polynomial(order)
        _require(
            evaluate_polynomial(poly, (1, 1, 1))
            == EQUAL_RADIUS_COEFFICIENTS[order],
            f"equal-radius coefficient regression failed at order {order}",
        )
        checks += 1

        # Full S3 invariance on an asymmetric exact witness.
        values = (Fraction(2), Fraction(3), Fraction(5))
        reference = evaluate_polynomial(poly, values)
        permutations = (
            (values[0], values[2], values[1]),
            (values[1], values[0], values[2]),
            (values[1], values[2], values[0]),
            (values[2], values[0], values[1]),
            (values[2], values[1], values[0]),
        )
        for permuted in permutations:
            _require(
                evaluate_polynomial(poly, permuted) == reference,
                f"S3 product symmetry regression failed at order {order}",
            )
            checks += 1

    _require(
        EQUAL_RADIUS_COEFFICIENTS[6] == 4 ** 6 * factorial(6) * 27,
        "Euler-characteristic oracle failed",
    )
    checks += 1

    return {
        "status": "PASS",
        "exact_checks": checks,
        "single_factor_lovelock": [str(v) for v in cp2_lovelock],
        "equal_radius_coefficients_over_pi6": [str(v) for v in EQUAL_RADIUS_COEFFICIENTS],
        "euler_characteristic_y": 27,
        "direct_product_orders": list(range(7)),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(exact_self_check(), indent=2, sort_keys=True))
