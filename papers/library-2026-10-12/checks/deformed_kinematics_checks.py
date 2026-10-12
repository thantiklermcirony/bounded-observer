"""Exact formula checks accompanying the proposed kinematics correction.

Run with Python 3 and SymPy installed:
    python deformed_kinematics_checks.py

The module reads no manuscript, private path or observational dataset. These
symbolic checks supplement the differentiation proofs printed in the notice.
"""

import json

import sympy as sp


def exact_checks():
    kappa, radius = sp.symbols("kappa radius", positive=True)
    h = sp.tanh(kappa * radius) / (kappa * radius)

    # The radial eigenvalue is the derivative of the bounded radial readout.
    radial_remainder = sp.simplify(
        h + radius * sp.diff(h, radius) - sp.sech(kappa * radius) ** 2
    )
    assert radial_remainder == 0

    transverse_series = sp.series(h, kappa, 0, 4).removeO()
    rank_one_series = sp.series(sp.diff(h, radius) / radius, kappa, 0, 4).removeO()
    assert sp.simplify(transverse_series - (1 - kappa**2 * radius**2 / 3)) == 0
    assert sp.simplify(rank_one_series + 2 * kappa**2 / 3) == 0

    # The apparent origin singularities in the displayed radial formulas are
    # removable; they give the smooth extension used by the canonical model.
    assert sp.limit(h, radius, 0) == 1
    assert sp.limit(sp.diff(h, radius) / radius, radius, 0) == -2 * kappa**2 / 3

    # Verify the Cartesian chain rule independently for a generic radial h.
    coordinates = sp.symbols("pi_1 pi_2 pi_3", real=True)
    norm = sp.sqrt(sum(value**2 for value in coordinates))
    generic_h = sp.Function("h")
    cartesian_remainders = []
    for i, pi_i in enumerate(coordinates):
        for j, pi_j in enumerate(coordinates):
            exact = sp.diff(generic_h(norm) * pi_j, pi_i)
            expected = (
                generic_h(norm) * int(i == j)
                + sp.Subs(sp.diff(generic_h(radius), radius), radius, norm)
                * pi_i * pi_j / norm
            )
            remainder = sp.simplify(exact - expected)
            assert remainder == 0
            cartesian_remainders.append(str(remainder))

    # The retained one-dimensional chart identity and its measure Jacobian.
    pi = sp.symbols("pi", real=True)
    p_of_pi = sp.tanh(kappa * pi) / kappa
    one_dimensional_remainder = sp.simplify(
        sp.diff(p_of_pi, pi) - (1 - kappa**2 * p_of_pi**2)
    )
    assert one_dimensional_remainder == 0
    p = sp.symbols("p", real=True)
    pi_of_p = sp.atanh(kappa * p) / kappa
    measure_remainder = sp.simplify(
        sp.diff(pi_of_p, p) - 1 / (1 - kappa**2 * p**2)
    )
    assert measure_remainder == 0

    return {
        "all_exact_checks_pass": True,
        "radial_eigenvalue_remainder": str(radial_remainder),
        "transverse_expansion": str(transverse_series),
        "rank_one_expansion_coefficient": str(rank_one_series),
        "origin_extension_checked": True,
        "nine_cartesian_chain_rule_remainders": cartesian_remainders,
        "one_dimensional_commutator_remainder": str(one_dimensional_remainder),
        "one_dimensional_measure_remainder": str(measure_remainder),
        "interpretation": "Exact formula verification; no observational analysis",
    }


if __name__ == "__main__":
    print(json.dumps(exact_checks(), indent=2))
