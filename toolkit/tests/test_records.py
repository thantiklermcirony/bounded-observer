"""Independent finite matrix checks of the current Paper 4/8 record models.

Choi matrices, finite unitary twirls and direct GKSL exponentiation check the
implemented channels rather than merely repeating their scalar formulas.
These tests verify model mathematics, not physical identification or field data.
"""
import math

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.linalg import expm

from bounded import records


def random_state(d, rng, *, full_rank=True):
    matrix = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
    state = matrix @ matrix.conj().T
    if full_rank:
        state += np.eye(d)
    return state / np.trace(state)


def random_unitary(d, rng):
    matrix = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
    unitary, _ = np.linalg.qr(matrix)
    return unitary


def choi(channel, d):
    result = np.zeros((d * d, d * d), dtype=complex)
    for i in range(d):
        for j in range(d):
            unit = np.zeros((d, d), dtype=complex)
            unit[i, j] = 1
            result += np.kron(unit, channel(unit))
    return result


def assert_cptp(channel, d):
    matrix = choi(channel, d)
    assert np.allclose(matrix, matrix.conj().T, atol=2e-12)
    assert np.linalg.eigvalsh(matrix)[0] >= -2e-12
    output_trace = np.trace(matrix.reshape(d, d, d, d), axis1=1, axis2=3)
    assert np.allclose(output_trace, np.eye(d), atol=2e-12)


def gell_mann(d):
    """Independent Hilbert--Schmidt orthonormal traceless Hermitian jump basis."""
    result = []
    for i in range(d):
        for j in range(i + 1, d):
            upper = np.zeros((d, d), dtype=complex)
            upper[i, j] = 1
            result.append((upper + upper.conj().T) / np.sqrt(2))
            result.append(-1j * (upper - upper.conj().T) / np.sqrt(2))
    for k in range(1, d):
        diagonal = np.zeros(d)
        diagonal[:k] = 1
        diagonal[k] = -k
        result.append(np.diag(diagonal) / np.sqrt(k * (k + 1)))
    return result


def canonical_jumps(m, n, coefficients):
    x, y, z = coefficients
    aa, bb = gell_mann(m), gell_mann(n)
    return (
        [np.sqrt(x / m) * np.kron(a, np.eye(n)) for a in aa]
        + [np.sqrt(y / n) * np.kron(np.eye(m), b) for b in bb]
        + [np.sqrt(z / (m * n)) * np.kron(a, b) for a in aa for b in bb]
    )


def gksl_superoperator(hamiltonian, jumps):
    """Column-vectorized GKSL generator, constructed independently of sectors."""
    d = hamiltonian.shape[0]
    identity = np.eye(d)
    generator = -1j * (
        np.kron(identity, hamiltonian) - np.kron(hamiltonian.T, identity)
    )
    for jump in jumps:
        gram = jump.conj().T @ jump
        generator += np.kron(jump.conj(), jump)
        generator -= (np.kron(identity, gram) + np.kron(gram.T, identity)) / 2
    return generator


def evolved(generator, matrix, exposure):
    d = matrix.shape[0]
    return (expm(exposure * generator) @ matrix.ravel(order="F")).reshape(d, d, order="F")


def test_record_validation_and_normalization_preserve_the_positive_ray():
    original = np.array([[4, 1j], [-1j, 2]], dtype=complex)
    validated = records.validate_record(original)
    validated[0, 0] = 900
    assert original[0, 0] == 4
    normalized = records.normalize_record(original)
    assert np.allclose(6 * normalized, original)
    assert np.trace(normalized) == pytest.approx(1)
    records.validate_record(normalized, normalized=True)
    assert records.von_neumann_entropy(np.diag([1, 0])) == pytest.approx(0)
    assert records.von_neumann_entropy(np.eye(3) / 3) == pytest.approx(math.log(3))


@pytest.mark.parametrize("scale", [1e-300, 1e-100, 1.0, 1e100, 1e300])
def test_normalization_of_valid_complex_rays_is_scale_invariant(scale):
    # Analytically positive: determinant 7, trace 6. Expected normalized state
    # is computed from that exact ray, independently of the implementation.
    ray = np.array([[4, 1j], [-1j, 2]], dtype=complex)
    expected = np.array([[2 / 3, 1j / 6], [-1j / 6, 1 / 3]])
    normalized = records.normalize_record(scale * ray)
    assert np.allclose(normalized, expected, atol=2e-15, rtol=2e-15)
    assert np.linalg.eigvalsh(normalized)[0] > 0


def test_normalization_handles_finite_rays_with_an_overflowing_raw_trace():
    # Every entry is finite. Its physical cone ray is I, even though summing the
    # raw diagonal in float64 would overflow; the normalized answer is I/2.
    normalized = records.normalize_record(np.eye(2) * 1e308)
    assert np.array_equal(normalized, np.eye(2) / 2)


@pytest.mark.parametrize("scale", [1e-300, 1e-13, 1.0])
def test_normalization_rejects_materially_nonpositive_rays_at_every_scale(scale):
    with pytest.raises(ValueError, match="positive semidefinite"):
        records.normalize_record(scale * np.diag([-1.0, 2.0]))


@pytest.mark.parametrize("scale", [1e-300, 1e-13, 1.0])
def test_normalization_checks_hermiticity_before_any_raw_projection(scale):
    # A raw absolute check could hide this defect at tiny scale. In trace-one
    # units it is material, and symmetrizing before checking would change ray.
    ray = np.array([[1, 1j], [0, 1]], dtype=complex)
    with pytest.raises(ValueError, match="Hermitian"):
        records.normalize_record(scale * ray)


def test_normalization_rejects_a_tiny_materially_complex_trace():
    with pytest.raises(ValueError, match="Hermitian"):
        records.normalize_record(np.array([[1e-300 + 1e-300j]]))


@pytest.mark.parametrize("matrix", [
    [], [1, 2], [[1, 0, 0], [0, 1, 0]], np.zeros((2, 2)),
    np.diag([1.1, -0.1]), [[1, 1j], [1j, 1]], [[np.nan]], [[np.inf]],
])
def test_invalid_records_are_rejected(matrix):
    with pytest.raises(ValueError):
        records.validate_record(matrix)


def test_normalized_validation_does_not_silently_rescale():
    with pytest.raises(ValueError, match="trace one"):
        records.validate_record(np.eye(2), normalized=True)
    with pytest.raises(ValueError):
        records.validate_record(np.eye(2), atol=-1)


def test_diagonal_algebra_equals_independent_finite_unitary_twirl():
    rng = np.random.default_rng(404)
    d = 4
    algebra = records.RetainedAlgebra([(1, 1)] * d)
    matrix = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
    twirl = np.zeros_like(matrix)
    for power in range(d):
        phase = np.diag(np.exp(2j * np.pi * power * np.arange(d) / d))
        twirl += phase @ matrix @ phase.conj().T / d
    assert np.allclose(algebra.expectation(matrix), twirl, atol=2e-12)
    assert_cptp(algebra.expectation, d)


@pytest.mark.parametrize("blocks", [[(2, 2)], [(2, 2), (1, 2)], [(1, 3), (2, 1)]])
def test_block_algebra_preserves_every_declared_reading_and_is_cptp(blocks):
    rng = np.random.default_rng(405)
    d = sum(n * k for n, k in blocks)
    unitary = random_unitary(d, rng)
    algebra = records.RetainedAlgebra(blocks, unitary=unitary)
    state = random_state(d, rng)
    projected = algebra.expectation(state)
    assert_cptp(algebra.expectation, d)
    assert np.allclose(algebra.expectation(np.eye(d)), np.eye(d))
    assert np.allclose(algebra.expectation(projected), projected)
    assert np.linalg.eigvalsh(projected)[0] > 0
    # A basis of each complete retained block, including its support projector.
    start = 0
    for n, k in blocks:
        for i in range(n):
            for j in range(n):
                local = np.zeros((d, d), dtype=complex)
                elementary = np.zeros((n, n), dtype=complex)
                elementary[i, j] = 1
                local[start:start + n * k, start:start + n * k] = np.kron(elementary, np.eye(k))
                observable = unitary @ local @ unitary.conj().T
                assert np.trace(observable @ projected) == pytest.approx(
                    np.trace(observable @ state), abs=2e-12
                )
        start += n * k


def test_tensor_factor_expectation_matches_an_independent_pauli_twirl():
    rng = np.random.default_rng(406)
    state = random_state(4, rng)
    pauli = [np.eye(2), np.array([[0, 1], [1, 0]]),
             np.array([[0, -1j], [1j, 0]]), np.diag([1, -1])]
    twirl = sum(np.kron(np.eye(2), p) @ state @ np.kron(np.eye(2), p) / 4 for p in pauli)
    assert np.allclose(records.RetainedAlgebra([(2, 2)]).expectation(state), twirl)


def test_forgetting_semigroup_preserves_readings_and_increases_entropy():
    rng = np.random.default_rng(407)
    algebra = records.RetainedAlgebra([(2, 2), (1, 1)])
    state = random_state(5, rng)
    previous_entropy = records.von_neumann_entropy(state)
    for u in (0, 0.01, 0.2, 1, 10, 100):
        result = algebra.forget(state, u)
        assert np.allclose(algebra.expectation(result), algebra.expectation(state))
        assert np.trace(result) == pytest.approx(1)
        assert np.linalg.eigvalsh(result)[0] >= -2e-12
        entropy = records.von_neumann_entropy(result)
        assert entropy >= previous_entropy - 2e-12
        previous_entropy = entropy
    assert np.allclose(algebra.forget(algebra.forget(state, 0.7), 0.9), algebra.forget(state, 1.6))
    assert np.allclose(algebra.forget(state, 100), algebra.expectation(state))
    # The linear extension of the convex combination has a positive Choi matrix.
    weight = math.exp(-0.7)
    assert_cptp(lambda x: weight * x + (1 - weight) * algebra.expectation(x), 5)


def test_complete_retained_readings_give_the_entropy_identity():
    rng = np.random.default_rng(408)
    algebra = records.RetainedAlgebra([(2, 3), (1, 1)], unitary=random_unitary(7, rng))
    state = random_state(7, rng)
    selected = algebra.expectation(state)
    values, vectors = np.linalg.eigh(selected)
    logarithm = (vectors * np.log(values)) @ vectors.conj().T
    relative_entropy = -records.von_neumann_entropy(state) - np.trace(state @ logarithm).real
    difference = records.von_neumann_entropy(selected) - records.von_neumann_entropy(state)
    assert relative_entropy == pytest.approx(difference, abs=2e-12)
    assert relative_entropy > 0


def test_singular_selector_keeps_the_required_support():
    # The second block projector is retained, so zero weight there forces support.
    algebra = records.RetainedAlgebra([(2, 2), (1, 1)])
    state = np.zeros((5, 5), dtype=complex)
    state[:4, :4] = np.outer([1, 0, 0, 1], [1, 0, 0, 1]) / 2
    selected = algebra.expectation(state)
    assert np.allclose(selected, np.diag([0.25, 0.25, 0.25, 0.25, 0]))
    assert selected[4, 4] == 0
    assert algebra.forget(state, 0.4)[4, 4] == 0
    # The logarithm is used only on the common support; no artificial epsilon.
    relative_entropy = -records.von_neumann_entropy(state) - math.log(0.25)
    assert relative_entropy == pytest.approx(records.von_neumann_entropy(selected))


@pytest.mark.parametrize("blocks", [[], [(0, 1)], [(2, 0)], [(2.0, 1)], [(True, 1)], [(1, 2, 3)]])
def test_bad_retained_algebra_specifications_are_rejected(blocks):
    with pytest.raises(ValueError):
        records.RetainedAlgebra(blocks)


def test_algebra_checks_unitary_dimension_and_exposure():
    with pytest.raises(ValueError, match="unitary"):
        records.RetainedAlgebra([(2, 1)], unitary=np.diag([1, 2]))
    algebra = records.RetainedAlgebra([(2, 1)])
    with pytest.raises(ValueError):
        algebra.expectation(np.eye(3))
    with pytest.raises(ValueError):
        algebra.forget(np.eye(3) / 3, 1)
    for u in (-1, np.inf, np.nan):
        with pytest.raises(ValueError):
            algebra.forget(np.eye(2) / 2, u)


@pytest.mark.parametrize("m,n", [(2, 2), (2, 3), (3, 2)])
@pytest.mark.parametrize("coefficients", [(0.23, 0.71, 0.53), (0.4, 0.7, 0), (0, 0, 0.4), (0, 0, 0)])
def test_covariant_channel_matches_independent_gksl_exponential(m, n, coefficients):
    rng = np.random.default_rng(409)
    rates = records.local_covariant_sector_rates(m, n, coefficients)
    assert records.local_covariant_coefficients(m, n, rates, atol=1e-14) == pytest.approx(coefficients)
    generator = gksl_superoperator(np.zeros((m * n, m * n)), canonical_jumps(m, n, coefficients))
    # Every matrix unit tests the full linear map, including non-Hermitian inputs.
    for i in range(m * n):
        for j in range(m * n):
            unit = np.zeros((m * n, m * n), dtype=complex)
            unit[i, j] = 1
            assert np.allclose(records.local_covariant_channel(unit, m, n, rates, 0.31, atol=1e-14),
                               evolved(generator, unit, 0.31), atol=3e-12)
    assert_cptp(lambda x: records.local_covariant_channel(x, m, n, rates, 0.31, atol=1e-14), m * n)
    state = random_state(m * n, rng)
    u = np.kron(random_unitary(m, rng), random_unitary(n, rng))
    transformed = records.local_covariant_channel(u @ state @ u.conj().T, m, n, rates, 0.7, atol=1e-14)
    assert np.allclose(transformed, u @ records.local_covariant_channel(state, m, n, rates, 0.7, atol=1e-14) @ u.conj().T)


def test_rate_cone_matches_independent_inequalities_on_mixed_trials():
    rng = np.random.default_rng(410)
    for m, n in [(2, 2), (2, 3), (3, 3)]:
        for _ in range(250):
            a, b, c = rng.uniform(-1, 3, size=3)
            inequalities_hold = (
                c <= a + b and c >= b - a / (n * n - 1)
                and c >= a - b / (m * m - 1)
            )
            assert records.is_local_covariant_rate_triple(m, n, (a, b, c)) == inequalities_hold


def test_positive_sector_rates_can_violate_complete_positivity():
    invalid = (1, 1, 3)
    assert not records.is_local_covariant_rate_triple(2, 3, invalid)
    with pytest.raises(ValueError, match="cone"):
        records.local_covariant_coefficients(2, 3, invalid)
    with pytest.raises(ValueError, match="cone"):
        records.local_covariant_channel(np.eye(6) / 6, 2, 3, invalid, 0.01)
    # Independently build the forbidden linear map and exhibit negative Choi.
    time = 0.001
    def forbidden(matrix):
        tensor = matrix.reshape(2, 3, 2, 3)
        a = np.kron(np.einsum("abcb->ac", tensor), np.eye(3) / 3)
        b = np.kron(np.eye(2) / 2, np.einsum("abad->bd", tensor))
        zero = np.trace(matrix) * np.eye(6) / 6
        return (math.exp(-3 * time) * matrix
                + (math.exp(-time) - math.exp(-3 * time)) * (a + b)
                + (1 - 2 * math.exp(-time) + math.exp(-3 * time)) * zero)
    assert np.linalg.eigvalsh(choi(forbidden, 6))[0] < -1e-5


def test_covariant_channel_has_an_additive_generator_clock():
    rng = np.random.default_rng(411)
    rates = records.local_covariant_sector_rates(2, 3, (0.4, 0.2, 0.7))
    state = random_state(6, rng)
    first = records.local_covariant_channel(state, 2, 3, rates, 0.3)
    assert np.allclose(records.local_covariant_channel(first, 2, 3, rates, 0.8),
                       records.local_covariant_channel(state, 2, 3, rates, 1.1))
    # A common clock change rescales all rates and compensates exposure.
    assert np.allclose(records.local_covariant_channel(state, 2, 3, np.array(rates) * 4, 1.1 / 4),
                       records.local_covariant_channel(state, 2, 3, rates, 1.1))


@pytest.mark.parametrize("m,n,rates", [(1, 2, (1, 1, 2)), (2.0, 2, (1, 1, 2)),
                                      (2, 2, (1, 2)), (2, 2, (1, 2, np.inf))])
def test_bad_rate_models_are_rejected(m, n, rates):
    with pytest.raises(ValueError):
        records.is_local_covariant_rate_triple(m, n, rates)


def test_full_rank_log_bound_for_independent_noncommuting_gksl_evolution():
    rng = np.random.default_rng(412)
    for d in (2, 3):
        initial = random_state(d, rng)
        raw = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
        hamiltonian = (raw + raw.conj().T) / 3
        jumps = [0.3 * (rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))) for _ in range(2)]
        generator = gksl_superoperator(hamiltonian, jumps)
        rate = records.gksl_exposure_rate(jumps)
        for time in (0, 0.1, 0.7, 2):
            final = evolved(generator, initial, time)
            smallest = np.linalg.eigvalsh((final + final.conj().T) / 2)[0]
            assert math.log(smallest) >= records.log_full_rank_lower_bound(initial, rate * time) - 2e-12
            assert np.trace(final) == pytest.approx(1, abs=2e-12)


def test_amplitude_damping_saturates_rank_and_qubit_rapidity_bounds():
    initial = np.diag([0.7, 0.3])
    gamma = 0.8
    jump = np.array([[0, math.sqrt(gamma)], [0, 0]], dtype=complex)
    generator = gksl_superoperator(np.zeros((2, 2)), [jump])
    assert records.gksl_exposure_rate([jump]) == pytest.approx(gamma)
    for time in (0, 0.2, 1, 6):
        final = evolved(generator, initial, time)
        eigenvalues = np.linalg.eigvalsh(final)
        exposure = gamma * time
        assert math.log(eigenvalues[0]) == pytest.approx(records.log_full_rank_lower_bound(initial, exposure))
        rapidity = 0.5 * math.log(eigenvalues[1] / eigenvalues[0])
        assert rapidity == pytest.approx(records.qubit_rapidity_upper_bound(initial, exposure))


def test_gksl_resource_integral_is_preserved_under_a_clock_change():
    gamma, endpoint = 0.7, 1.6
    jump = np.array([[0, math.sqrt(gamma)], [0, 0]], dtype=complex)
    # t=s^2, L_s=sqrt(dt/ds) L_t. Integrate the actual rescaled Gram norm.
    transformed = quad(lambda s: records.gksl_exposure_rate([math.sqrt(2 * s) * jump]), 0, endpoint)[0]
    original = quad(lambda t: records.gksl_exposure_rate([jump]), 0, endpoint**2)[0]
    assert transformed == pytest.approx(original, abs=2e-12)


def test_logarithmic_resource_bound_does_not_underflow():
    state = np.diag([0.7, 0.3])
    log_bound = records.log_full_rank_lower_bound(state, 1000)
    assert math.isfinite(log_bound) and log_bound < -1000
    assert math.exp(log_bound) == 0  # floating-point loss, not mathematical rank loss
    assert math.isfinite(records.qubit_rapidity_upper_bound(state, 1000))


def test_finite_swap_is_outside_the_finite_local_gksl_exposure_premise():
    initial = np.diag([0.7, 0.3])
    swap = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex)
    unitary = expm(-1j * np.pi * swap / 2)
    joint = unitary @ np.kron(initial, np.diag([1, 0])) @ unitary.conj().T
    reduced = np.trace(joint.reshape(2, 2, 2, 2), axis1=1, axis2=3)
    assert np.allclose(reduced, np.diag([1, 0]), atol=2e-12)
    # Its local amplitude-damping exposure diverges as the endpoint approaches.
    exposures = [quad(lambda t: 2 * math.tan(t), 0, np.pi / 2 - epsilon)[0]
                 for epsilon in (0.1, 0.01, 0.001)]
    assert exposures[0] < exposures[1] < exposures[2]
    assert exposures[-1] > 13


def test_invalid_gksl_resource_inputs_are_rejected():
    with pytest.raises(ValueError, match="full rank"):
        records.log_full_rank_lower_bound(np.diag([1, 0]), 1)
    for exposure in (-1, np.inf, np.nan):
        with pytest.raises(ValueError):
            records.log_full_rank_lower_bound(np.eye(2) / 2, exposure)
    with pytest.raises(ValueError):
        records.qubit_rapidity_upper_bound(np.eye(3) / 3, 1)
    with pytest.raises(ValueError):
        records.gksl_exposure_rate([])
    with pytest.raises(ValueError):
        records.gksl_exposure_rate([np.eye(2), np.eye(3)])
    assert records.gksl_exposure_rate([], dimension=2) == 0
