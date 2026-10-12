"""Finite complex records for the library's explicitly stated channel models.

Sources: Paper 4, Theorems 5--6; Paper 8, Theorem 5, in
``papers/library-2026-10-12``. These operations assume complex matrix records,
complete positivity and the specified retained algebra or GKSL model. They do
not derive a physical interpretation, choose an algebra, or turn an arbitrary
list of conserved means into a linear maximum-entropy channel.

Only NumPy is required. Validation tolerances are numerical tolerances, not
relaxations of the mathematical premises. No negative eigenvalue is clipped to
repair an invalid record; a negligible anti-Hermitian roundoff part is removed
after the Hermiticity check. Use application-appropriate tolerances explicitly.
"""
from __future__ import annotations

import math
from collections.abc import Iterable, Sequence

import numpy as np


def _nonnegative(value: float, name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite nonnegative real number") from exc
    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{name} must be a finite nonnegative real number")
    return result


def _dimension(value: int, name: str, minimum: int = 1) -> int:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise ValueError(f"{name} must be an integer at least {minimum}")
    if value < minimum:
        raise ValueError(f"{name} must be an integer at least {minimum}")
    return int(value)


def _matrix(matrix, dimension: int | None = None) -> np.ndarray:
    try:
        result = np.array(matrix, dtype=complex, copy=True)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("matrix must be a finite square complex array") from exc
    if result.ndim != 2 or result.shape[0] == 0 or result.shape[0] != result.shape[1]:
        raise ValueError("matrix must be a nonempty square array")
    if dimension is not None and result.shape != (dimension, dimension):
        raise ValueError(f"matrix must have shape ({dimension}, {dimension})")
    if not np.isfinite(result).all():
        raise ValueError("matrix entries must be finite")
    return result


def validate_record(matrix, *, normalized: bool = False, atol: float = 1e-12) -> np.ndarray:
    """Return a checked Hermitian PSD record with strictly positive trace.

    ``atol`` is an absolute tolerance on this supplied matrix. If
    ``normalized=True``, trace must also equal one within ``atol``. The returned
    array is independent of the input; validation never normalizes it. To check
    a cone ray independent of its raw magnitude, use ``normalize_record``, which
    validates the trace-one candidate before removing roundoff. Zero records are
    excluded because their normalized readings are undefined.
    """
    tolerance = _nonnegative(atol, "atol")
    record = _matrix(matrix)
    if np.max(np.abs(record - record.conj().T)) > tolerance:
        raise ValueError("record must be Hermitian")
    record = (record + record.conj().T) / 2
    eigenvalues = np.linalg.eigvalsh(record)
    if eigenvalues[0] < -tolerance:
        raise ValueError("record must be positive semidefinite")
    trace = float(np.trace(record).real)
    if not math.isfinite(trace) or trace <= 0:
        raise ValueError("record must have finite strictly positive trace")
    if normalized and abs(trace - 1) > tolerance:
        raise ValueError("normalized record must have trace one")
    return record


def normalize_record(matrix, *, atol: float = 1e-12) -> np.ndarray:
    """Validate and normalize a positive cone ray independent of raw magnitude.

    The supplied absolute ``atol`` applies to the trace-one candidate, not the
    raw matrix. Thus a tiny raw negative or anti-Hermitian component cannot be
    amplified into a materially invalid normalized state. Positive rescaling
    before computing the trace avoids overflow/underflow in otherwise valid
    finite input rays. No eigenvalue is clipped and no Hermitian projection is
    performed until the normalized candidate has passed its Hermiticity check.
    """
    tolerance = _nonnegative(atol, "atol")
    record = _matrix(matrix)
    # Scale the real and imaginary components separately: direct complex
    # division can overflow its internal reciprocal for a subnormal divisor.
    scale = float(max(np.max(np.abs(record.real)), np.max(np.abs(record.imag))))
    if scale == 0:
        raise ValueError("record must have strictly positive trace")
    scaled = record.real / scale + 1j * (record.imag / scale)
    trace = float(np.trace(scaled).real)
    if not math.isfinite(trace) or trace <= 0:
        raise ValueError("record must have finite strictly positive trace")
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        normalized = scaled.real / trace + 1j * (scaled.imag / trace)
    return validate_record(normalized, normalized=True, atol=tolerance)


def von_neumann_entropy(matrix, *, atol: float = 1e-12) -> float:
    """Entropy in natural-log units for a trace-one PSD record (0 log 0 = 0)."""
    record = validate_record(matrix, normalized=True, atol=atol)
    eigenvalues = np.linalg.eigvalsh(record)
    positive = eigenvalues[eigenvalues > 0]
    return float(-np.dot(positive, np.log(positive)))


class RetainedAlgebra:
    """A supplied finite unital *-subalgebra in canonical block representation.

    ``blocks=[(n_1,k_1), ...]`` specifies
    A = direct_sum_i (M_{n_i}(C) tensor I_{k_i}) acting on dimension
    d = sum_i n_i*k_i. Coordinates are contiguous blocks in that order.
    An optional supplied unitary U specifies U A U^dagger instead.

    All finite matrix *-subalgebras have such a representation; this constructor
    requires it as input and does not infer it from readouts. For example,
    [(2,3)] retains a two-dimensional factor, while [(1,1)] * d retains only
    diagonal readings. The algebra includes its block support projectors.
    """

    def __init__(
        self,
        blocks: Sequence[tuple[int, int]],
        *,
        unitary=None,
        atol: float = 1e-12,
    ):
        self.atol = _nonnegative(atol, "atol")
        try:
            pairs = tuple(tuple(block) for block in blocks)
        except TypeError as exc:
            raise ValueError("blocks must contain positive integer pairs (n, k)") from exc
        if not pairs or any(len(pair) != 2 for pair in pairs):
            raise ValueError("blocks must contain positive integer pairs (n, k)")
        self.blocks = tuple(
            (_dimension(n, "block n"), _dimension(k, "block k")) for n, k in pairs
        )
        self.dimension = sum(n * k for n, k in self.blocks)
        basis = np.eye(self.dimension, dtype=complex) if unitary is None else _matrix(
            unitary, self.dimension
        )
        if np.max(np.abs(basis.conj().T @ basis - np.eye(self.dimension))) > self.atol:
            raise ValueError("supplied basis change must be unitary")
        self._unitary = basis

    def expectation(self, matrix) -> np.ndarray:
        """Apply the tracial conditional expectation E_A to any complex operator.

        E deletes cross-block coherences and replaces each multiplicity factor
        by I_k/k: E(X)_i = Tr_{k_i}(X_ii) tensor I_{k_i}/k_i.
        It is linear, unital, trace preserving, completely positive and
        idempotent. PSD input validation is intentionally not imposed here:
        linear channels must also act on non-Hermitian matrix units.
        """
        matrix = _matrix(matrix, self.dimension)
        local = self._unitary.conj().T @ matrix @ self._unitary
        output = np.zeros_like(local)
        start = 0
        for n, k in self.blocks:
            stop = start + n * k
            block = local[start:stop, start:stop].reshape(n, k, n, k)
            marginal = np.einsum("abcb->ac", block)
            output[start:stop, start:stop] = np.kron(marginal, np.eye(k) / k)
            start = stop
        return self._unitary @ output @ self._unitary.conj().T

    def forget(self, record, exposure: float) -> np.ndarray:
        """Apply T_u = exp(-u) id + (1-exp(-u)) E_A to a normalized record.

        u is a supplied nonnegative cumulative exposure, not an assumed
        physical clock. Its additive composition gives T_u T_v = T_{u+v}.
        The unique limit is E_A(record), preserving the full retained algebra.
        """
        record = validate_record(record, normalized=True, atol=self.atol)
        if record.shape != (self.dimension, self.dimension):
            raise ValueError("record dimension must match the retained algebra")
        exposure = _nonnegative(exposure, "exposure")
        forgotten_weight = -math.expm1(-exposure)
        return math.exp(-exposure) * record + forgotten_weight * self.expectation(record)


def _local_dimensions(m: int, n: int) -> tuple[int, int]:
    return _dimension(m, "m", 2), _dimension(n, "n", 2)


def _triple(values, name: str) -> tuple[float, float, float]:
    try:
        result = tuple(float(value) for value in values)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must contain three finite real numbers") from exc
    if len(result) != 3 or not all(math.isfinite(value) for value in result):
        raise ValueError(f"{name} must contain three finite real numbers")
    return result


def local_covariant_sector_rates(m: int, n: int, coefficients) -> tuple[float, float, float]:
    """Convert nonnegative canonical GKSL coefficients (x,y,z) to rates A,B,C.

    Paper 8 Theorem 5 assumes a time-homogeneous trace-preserving quantum
    Markov generator covariant under all local unitaries on C^m tensor C^n.
    These canonical coefficients are supplied content, not selected constants.
    """
    m, n = _local_dimensions(m, n)
    x, y, z = _triple(coefficients, "coefficients")
    if min(x, y, z) < 0:
        raise ValueError("canonical GKSL coefficients must be nonnegative")
    rates = (
        x + (1 - n**-2) * z,
        y + (1 - m**-2) * z,
        x + y + (1 - m**-2 - n**-2) * z,
    )
    if not all(math.isfinite(rate) for rate in rates):
        raise ValueError("sector rates overflowed finite floating-point range")
    return rates


def local_covariant_coefficients(
    m: int, n: int, rates, *, atol: float = 0.0
) -> tuple[float, float, float]:
    """Invert the rate map, rejecting rates outside the complete-positivity cone.

    The default checks nonnegativity strictly. An explicitly supplied ``atol``
    admits only that much floating-point roundoff in reconstructed coefficients;
    those small negative residues are then set to zero. This is not a fit or a
    general projection onto the cone. Positive decay rates alone are insufficient.
    """
    m, n = _local_dimensions(m, n)
    a, b, c = _triple(rates, "rates")
    tolerance = _nonnegative(atol, "atol")
    z = a + b - c
    coefficients = (a - (1 - n**-2) * z, b - (1 - m**-2) * z, z)
    if not all(math.isfinite(value) for value in coefficients):
        raise ValueError("canonical coefficients overflowed finite floating-point range")
    if min(coefficients) < -tolerance:
        raise ValueError("rates are outside the locally covariant GKSL cone")
    return tuple(max(0.0, value) for value in coefficients)


def is_local_covariant_rate_triple(m: int, n: int, rates, *, atol: float = 0.0) -> bool:
    """Check cone membership; malformed dimensions, values or tolerances raise."""
    m, n = _local_dimensions(m, n)
    rates = _triple(rates, "rates")
    tolerance = _nonnegative(atol, "atol")
    try:
        local_covariant_coefficients(m, n, rates, atol=tolerance)
    except ValueError:
        return False
    return True


def _local_sectors(matrix, m: int, n: int) -> tuple[np.ndarray, ...]:
    matrix = _matrix(matrix, m * n)
    tensor = matrix.reshape(m, n, m, n)
    marginal_a = np.einsum("abcb->ac", tensor)
    marginal_b = np.einsum("abad->bd", tensor)
    scalar = np.trace(matrix) * np.eye(m * n) / (m * n)
    a = np.kron(marginal_a, np.eye(n) / n) - scalar
    b = np.kron(np.eye(m) / m, marginal_b) - scalar
    return scalar, a, b, matrix - scalar - a - b


def local_covariant_channel(
    matrix, m: int, n: int, rates, exposure: float, *, atol: float = 0.0
) -> np.ndarray:
    """Exponentiate an admissible locally covariant generator on any operator.

    Acts by 1, exp(-lambda_A*u), exp(-lambda_B*u), exp(-lambda_C*u) on the
    identity, A-only, B-only and correlation sectors. Rates must belong to the
    Paper 8 cone; the resulting map is CPTP. If ``atol`` is explicitly supplied,
    accepted reconstruction roundoff is handled as in
    ``local_covariant_coefficients`` and rates are recomputed from the checked
    nonnegative coefficients. u is in the supplied generator's clock units.
    A generator itself need not be a positive map.
    """
    m, n = _local_dimensions(m, n)
    rates = _triple(rates, "rates")
    coefficients = local_covariant_coefficients(m, n, rates, atol=atol)
    rates = local_covariant_sector_rates(m, n, coefficients)
    exposure = _nonnegative(exposure, "exposure")
    sectors = _local_sectors(matrix, m, n)
    return sectors[0] + sum(
        math.exp(-rate * exposure) * sector for rate, sector in zip(rates, sectors[1:])
    )


def gksl_exposure_rate(jumps: Iterable, *, dimension: int | None = None) -> float:
    """Return ||sum L_k^dagger L_k||_op for a supplied GKSL jump representation.

    Integrating this rate in a well-defined finite-dimensional time-local GKSL
    evolution gives Xi. The representation is part of the premise: scalar
    shifts of jumps can change Xi for the same evolution. An empty family needs
    an explicit dimension. No Hamiltonian or physical clock is inferred.
    """
    if dimension is not None:
        dimension = _dimension(dimension, "dimension")
    try:
        matrices = tuple(_matrix(jump, dimension) for jump in jumps)
    except TypeError as exc:
        raise ValueError("jumps must be an iterable of finite square matrices") from exc
    if not matrices:
        if dimension is None:
            raise ValueError("an empty jump family requires an explicit dimension")
        return 0.0
    dimension = matrices[0].shape[0]
    if any(jump.shape != (dimension, dimension) for jump in matrices):
        raise ValueError("all jumps must have the same dimension")
    with np.errstate(over="ignore", invalid="ignore"):
        gram = sum(jump.conj().T @ jump for jump in matrices)
    if not np.isfinite(gram).all():
        raise ValueError("jump Gram matrix overflowed finite floating-point range")
    return float(np.linalg.eigvalsh((gram + gram.conj().T) / 2)[-1])


def log_full_rank_lower_bound(record, exposure: float, *, atol: float = 1e-12) -> float:
    """Return log(p0)-Xi, the Paper 4 lower bound on log lambda_min(rho(T)).

    Requires a full-rank normalized initial record and a supplied finite Xi >= 0
    computed from the stated GKSL representation. This function evaluates the
    bound; it does not certify that proposed dynamics have those premises.
    Logarithmic output avoids numerical underflow at large finite exposure.
    """
    record = validate_record(record, normalized=True, atol=atol)
    p0 = float(np.linalg.eigvalsh(record)[0])
    if p0 <= 0:
        raise ValueError("initial record must be strictly positive (full rank)")
    return math.log(p0) - _nonnegative(exposure, "exposure")


def qubit_rapidity_upper_bound(record, exposure: float, *, atol: float = 1e-12) -> float:
    """Bound determinant-normalized qubit rapidity under the same GKSL premises."""
    record = _matrix(record, 2)
    log_p = log_full_rank_lower_bound(record, exposure, atol=atol)
    return 0.5 * (math.log1p(-math.exp(log_p)) - log_p)
