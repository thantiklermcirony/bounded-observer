#!/usr/bin/env python3
"""Verify locally covariant quantum rates and angular photon number density.

Run with Python 3 and NumPy:
    python local_covariant_rate_checks.py
    python local_covariant_rate_checks.py --output results.json

The default JSON is written beside this file. These are finite matrix and
quadrature checks of stated conditional models, not empirical validation.
No external data, private paths, network access or author code is required.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


SEED = 20261013
MATRIX_TOLERANCE = 5e-12
CHOI_TOLERANCE = 1e-10
ANGULAR_TOLERANCE = 1e-10


def hermitian_traceless_basis(dimension: int) -> list[np.ndarray]:
    """Return a trace-orthonormal Hermitian basis of the traceless matrices."""
    basis = []
    for i in range(dimension):
        for j in range(i + 1, dimension):
            symmetric = np.zeros((dimension, dimension), dtype=complex)
            symmetric[i, j] = symmetric[j, i] = 1 / np.sqrt(2)
            basis.append(symmetric)
            antisymmetric = np.zeros((dimension, dimension), dtype=complex)
            antisymmetric[i, j] = -1j / np.sqrt(2)
            antisymmetric[j, i] = 1j / np.sqrt(2)
            basis.append(antisymmetric)
    for k in range(1, dimension):
        diagonal = np.zeros((dimension, dimension), dtype=complex)
        diagonal[np.arange(k), np.arange(k)] = 1 / np.sqrt(k * (k + 1))
        diagonal[k, k] = -k / np.sqrt(k * (k + 1))
        basis.append(diagonal)
    return basis


def rates_from_parameters(m: int, n: int, x: float, y: float, z: float):
    return (
        x + (1 - n**-2) * z,
        y + (1 - m**-2) * z,
        x + y + (1 - m**-2 - n**-2) * z,
    )


def parameters_from_rates(m: int, n: int, rates):
    rate_a, rate_b, rate_c = rates
    z = rate_a + rate_b - rate_c
    return rate_a - (1 - n**-2) * z, rate_b - (1 - m**-2) * z, z


def rate_inequality_slacks(m: int, n: int, rates):
    rate_a, rate_b, rate_c = rates
    return (
        rate_a + rate_b - rate_c,
        rate_c - rate_b + rate_a / (n * n - 1),
        rate_c - rate_a + rate_b / (m * m - 1),
    )


def canonical_jump_families(m: int, n: int, parameters):
    x, y, z = parameters
    if min(parameters) < 0:
        raise ValueError("GKSL jump coefficients must be nonnegative")
    aa, bb = hermitian_traceless_basis(m), hermitian_traceless_basis(n)
    return (
        [np.sqrt(x / m) * np.kron(a, np.eye(n)) for a in aa],
        [np.sqrt(y / n) * np.kron(np.eye(m), b) for b in bb],
        [np.sqrt(z / (m * n)) * np.kron(a, b) for a in aa for b in bb],
    )


def dissipator(matrix: np.ndarray, jumps: list[np.ndarray]):
    output = np.zeros_like(matrix, dtype=complex)
    for jump in jumps:
        gram = jump.conj().T @ jump
        output += jump @ matrix @ jump.conj().T
        output -= (gram @ matrix + matrix @ gram) / 2
    return output


def reset_a(matrix: np.ndarray, m: int, n: int):
    tensor = matrix.reshape(m, n, m, n)
    marginal_b = np.einsum("abad->bd", tensor)
    return np.kron(np.eye(m) / m, marginal_b)


def reset_b(matrix: np.ndarray, m: int, n: int):
    tensor = matrix.reshape(m, n, m, n)
    marginal_a = np.einsum("abcb->ac", tensor)
    return np.kron(marginal_a, np.eye(n) / n)


def invariant_channel(matrix: np.ndarray, m: int, n: int, rates, time: float):
    """Exponential of the four-sector invariant linear generator.

    The formula defines a trace-preserving Hermiticity-preserving map for any
    real rates. Complete positivity is checked rather than assumed.
    """
    rate_a, rate_b, rate_c = rates
    decay_a, decay_b, decay_c = np.exp(-time * np.asarray(rates))
    d = m * n
    return (
        decay_c * matrix
        + (decay_b - decay_c) * reset_a(matrix, m, n)
        + (decay_a - decay_c) * reset_b(matrix, m, n)
        + (1 - decay_a - decay_b + decay_c) * np.trace(matrix) * np.eye(d) / d
    )


def choi_matrix(m: int, n: int, rates, time: float):
    """Unnormalized Choi matrix: sum_ij |i><j| tensor Phi(|i><j|)."""
    d = m * n
    choi = np.zeros((d * d, d * d), dtype=complex)
    for i in range(d):
        for j in range(d):
            elementary = np.zeros((d, d), dtype=complex)
            elementary[i, j] = 1
            choi += np.kron(elementary, invariant_channel(elementary, m, n, rates, time))
    return choi


def matrix_checks(rng: np.random.Generator):
    cases = []
    for m, n in ((2, 2), (2, 3), (3, 3)):
        aa, bb = hermitian_traceless_basis(m), hermitian_traceless_basis(n)
        sectors = (
            [np.kron(a, np.eye(n)) for a in aa],
            [np.kron(np.eye(m), b) for b in bb],
            [np.kron(a, b) for a in aa for b in bb],
        )
        coefficients = [(0.23, 0.71, 0.53), (0.4, 0.7, 0.0)]
        coefficients.extend(tuple(rng.uniform(0.02, 1.0, size=3)) for _ in range(4))
        for parameters in coefficients:
            families = canonical_jump_families(m, n, parameters)
            jumps = [jump for family in families for jump in family]
            rates = rates_from_parameters(m, n, *parameters)
            residual = max(
                float(np.linalg.norm(dissipator(matrix, jumps) + rate * matrix))
                for sector, rate in zip(sectors, rates)
                for matrix in sector
            )
            identity_residual = float(np.linalg.norm(dissipator(np.eye(m * n), jumps)))
            inverse_residual = float(np.max(np.abs(
                np.asarray(parameters_from_rates(m, n, rates)) - parameters
            )))
            slacks = rate_inequality_slacks(m, n, rates)
            minimum_choi = min(float(np.linalg.eigvalsh(
                choi_matrix(m, n, rates, time)
            ).min()) for time in (0.001, 0.2, 2.0))
            passed = (
                residual < MATRIX_TOLERANCE
                and identity_residual < MATRIX_TOLERANCE
                and inverse_residual < MATRIX_TOLERANCE
                and min(slacks) >= -MATRIX_TOLERANCE
                and minimum_choi >= -CHOI_TOLERANCE
            )
            cases.append({
                "dimensions": [m, n],
                "parameters_x_y_z": [float(v) for v in parameters],
                "jump_family_sizes": [len(family) for family in families],
                "rates_A_B_C": [float(v) for v in rates],
                "sector_basis_counts": [len(sector) for sector in sectors],
                "sector_eigenvalue_residual_max": residual,
                "identity_residual": identity_residual,
                "parameter_reconstruction_error": inverse_residual,
                "inequality_slacks": [float(v) for v in slacks],
                "minimum_choi_eigenvalue_over_test_times": minimum_choi,
                "passed": passed,
            })
    return cases


def cone_checks(rng: np.random.Generator):
    checked = 0
    mismatches = 0
    for m, n in ((2, 2), (2, 3), (3, 3)):
        for _ in range(1000):
            rates = tuple(rng.uniform(-1.0, 3.0, size=3))
            parameter_condition = min(parameters_from_rates(m, n, rates)) >= 0
            inequality_condition = min(rate_inequality_slacks(m, n, rates)) >= 0
            checked += 1
            mismatches += parameter_condition != inequality_condition
    m, n, time = 2, 3, 0.001
    invalid_rates = (1.0, 1.0, 3.0)
    eigs = np.linalg.eigvalsh(choi_matrix(m, n, invalid_rates, time))
    predicted_negative = (1 - 2 * np.exp(-time) + np.exp(-3 * time)) / (m * n)
    return {
        "sampled_rate_triples": checked,
        "cone_equivalence_mismatches": int(mismatches),
        "invalid_case": {
            "dimensions": [m, n],
            "rates_A_B_C": list(invalid_rates),
            "all_three_decay_rates_positive": True,
            "reconstructed_parameters_x_y_z": list(parameters_from_rates(m, n, invalid_rates)),
            "time": time,
            "choi_normalization": "unnormalized; trace equals input dimension",
            "choi_minimum_eigenvalue": float(eigs.min()),
            "predicted_negative_eigenvalue": float(predicted_negative),
            "negative_eigenvalue_count": int(np.count_nonzero(eigs < -CHOI_TOLERANCE)),
            "predicted_negative_multiplicity": (m * m - 1) * (n * n - 1),
        },
        "passed": bool(
            mismatches == 0
            and eigs.min() < -CHOI_TOLERANCE
            and abs(eigs.min() - predicted_negative) < MATRIX_TOLERANCE
            and np.count_nonzero(eigs < -CHOI_TOLERANCE) == (m * m - 1) * (n * n - 1)
        ),
    }


def photon_number_density_checks():
    cosine, weights = np.polynomial.legendre.leggauss(256)
    cases = []
    for beta in (-0.8, -0.25, 0.0, 0.01, 0.25, 0.8, 0.95):
        # Azimuth has been integrated: 2*pi*P3(mu) is the density on [-1,1].
        marginal = (1 - beta * beta)**2 / (2 * (1 - beta * cosine)**3)
        normalization = float(weights @ marginal)
        mean = float(weights @ (cosine * marginal))
        gamma = 1 / np.sqrt(1 - beta * beta)
        doppler = 1 / (gamma * (1 - beta * cosine))
        doppler_mass = float(2 * np.pi * (weights @ doppler**3))
        cases.append({
            "beta": beta,
            "normalization": normalization,
            "mean_direction_cosine": mean,
            "normalization_error": abs(normalization - 1),
            "mean_error": abs(mean - beta),
            "doppler_cubed_angular_mass": doppler_mass,
            "predicted_doppler_cubed_mass": float(4 * np.pi * gamma),
            "passed": bool(
                abs(normalization - 1) < ANGULAR_TOLERANCE
                and abs(mean - beta) < ANGULAR_TOLERANCE
                and abs(doppler_mass - 4 * np.pi * gamma) < ANGULAR_TOLERANCE
            ),
        })
    return {
        "model": "Local angular photon number density of an isotropic-rest gas, sampled on the observer's equal-time hypersurface",
        "density": "P3(mu)=(1-beta^2)^2/[4*pi*(1-beta*mu)^3]",
        "required_scope": "Number-current and hypersurface sampling premises; no assertion for arbitrary detector crossing counts or fixed recorded sky samples",
        "quadrature": "256-point Gauss-Legendre in direction cosine, analytic azimuth integration",
        "cases": cases,
        "passed": all(case["passed"] for case in cases),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_suffix(".json"))
    arguments = parser.parse_args()
    rng = np.random.default_rng(SEED)
    cases = matrix_checks(rng)
    cone = cone_checks(rng)
    photon = photon_number_density_checks()
    report = {
        "schema_version": 1,
        "script": Path(__file__).name,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "seed": SEED,
        "numpy_version": np.__version__,
        "scope": "Exact conditional finite-dimensional quantum Markov and isotropic photon-gas models; mathematical checks, not empirical validation",
        "rate_formula": {
            "A": "x+(1-1/n^2)z",
            "B": "y+(1-1/m^2)z",
            "correlation": "x+y+(1-1/m^2-1/n^2)z",
            "parameters": "x,y,z>=0",
        },
        "matrix_cases": cases,
        "cone_checks": cone,
        "photon_number_density": photon,
        "tolerances": {
            "matrix_absolute": MATRIX_TOLERANCE,
            "choi_eigenvalue_absolute": CHOI_TOLERANCE,
            "angular_absolute": ANGULAR_TOLERANCE,
        },
        "references": ["https://doi.org/10.1007/BF01608499"],
        "all_passed": bool(all(case["passed"] for case in cases) and cone["passed"] and photon["passed"]),
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_passed": report["all_passed"],
        "matrix_case_count": len(cases),
        "maximum_sector_residual": max(case["sector_eigenvalue_residual_max"] for case in cases),
        "cone_equivalence_trials": cone["sampled_rate_triples"],
        "invalid_case_minimum_choi_eigenvalue": cone["invalid_case"]["choi_minimum_eigenvalue"],
        "maximum_photon_normalization_error": max(case["normalization_error"] for case in photon["cases"]),
        "maximum_photon_mean_error": max(case["mean_error"] for case in photon["cases"]),
        "output_filename": arguments.output.name,
    }, indent=2))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
