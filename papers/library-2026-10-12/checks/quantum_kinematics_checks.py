"""Independent checks for the proposed Paper 1 / Paper 2 theorem repairs.

Reads no author code or source data. Writes only a result receipt beside itself.
Analytic proofs, rather than these finite checks, establish the general claims.
"""
from pathlib import Path
import json
import math
import numpy as np

ROOT = Path(__file__).resolve().parent
RNG = np.random.default_rng(20261012)
RESULTS = {}


def herm(n):
    z = RNG.normal(size=(n, n)) + 1j * RNG.normal(size=(n, n))
    z = (z + z.conj().T) / 2
    return z - np.trace(z).real * np.eye(n) / n


def jordan(x, y):
    return (x @ y + y @ x) / 2


def deriv(x, y, alpha=0.5):
    return alpha * 1j * (x @ y - y @ x)


x, y, z = herm(3), herm(3), herm(3)
transpose_ad = deriv(x, y.T).T
same_sign = deriv(x.T, y)
antiunitary_residual = float(np.linalg.norm(transpose_ad + same_sign))
antiunitary_wrong_sign = float(np.linalg.norm(transpose_ad - same_sign))
assert antiunitary_residual < 1e-12 and antiunitary_wrong_sign > 1e-3
RESULTS["Q1_transpose_obstruction"] = {
    "correct_sign_residual": antiunitary_residual,
    "full_group_equivariance_failure": antiunitary_wrong_sign,
}

lc = jordan(x, jordan(y, z)) - jordan(y, jordan(x, z))
dc = deriv(x, deriv(y, z)) - deriv(y, deriv(x, z))
dc_uncalibrated = deriv(x, deriv(y, z, 1), 1) - deriv(y, deriv(x, z, 1), 1)
calibration_residual = float(np.linalg.norm(dc + lc))
uncalibrated_residual = float(np.linalg.norm(dc_uncalibrated + lc))
assert calibration_residual < 1e-12 and uncalibrated_residual > 1e-3
RESULTS["Q2_dynamical_calibration"] = {
    "alpha_half_residual": calibration_residual,
    "alpha_one_residual": uncalibrated_residual,
    "own_reading_derivative": float(abs(np.trace(x @ deriv(x, y)))),
}

pauli = np.array([
    [[0, 1], [1, 0]], [[0, -1j], [1j, 0]], [[1, 0], [0, -1]],
], dtype=complex)


def density(b):
    return (np.eye(2) + np.tensordot(b, pauli, axes=1)) / 2


metric_error = 0.0
for _ in range(250):
    b = RNG.normal(size=3)
    b *= RNG.uniform(0, 0.9) / np.linalg.norm(b)
    c = RNG.normal(size=3)
    c *= RNG.uniform(0, 0.9) / np.linalg.norm(c)
    a, bb = density(b), density(c)
    ev, vec = np.linalg.eigh(bb)
    invsqrt = (vec * ev**-0.5) @ vec.conj().T
    ratios = np.linalg.eigvalsh(invsqrt @ a @ invsqrt)
    order_distance = math.log(float(ratios[-1] / ratios[0]))
    arg = (1 - b @ c) / math.sqrt((1 - b @ b) * (1 - c @ c))
    hyperbolic = 2 * math.acosh(max(1.0, float(arg)))
    metric_error = max(metric_error, abs(order_distance - hyperbolic))
assert metric_error < 1e-11
RESULTS["Q3_order_hyperbolic_metric"] = {
    "pairs": 250, "max_absolute_error": metric_error,
}


def alternative_add(a, b):
    return 2 / math.pi * math.atan(math.tan(math.pi * a / 2) + math.tan(math.pi * b / 2))


a, b, c = 0.2, 0.4, -0.1
alternative = alternative_add(a, b)
einstein = (a + b) / (1 + a * b)
assoc_error = abs(alternative_add(alternative_add(a, b), c) - alternative_add(a, alternative_add(b, c)))
assert assoc_error < 1e-14 and abs(alternative - einstein) > 1e-3
RESULTS["Q4_bounded_law_counterexample"] = {
    "alternative": alternative, "einstein": einstein, "associativity_error": assoc_error,
}

A = np.array([[1, 0.5], [0, 0.5]])
B = np.array([[0.5, 0], [0.5, 1]])
initial = np.ones(2)
ab, ba = A @ B @ initial, B @ A @ initial
assert np.allclose(ab, [1.25, 0.75]) and np.allclose(ba, [0.75, 1.25])
RESULTS["B1_constant_conversion_order_effect"] = {
    "p_AB": float(ab[0] / sum(ab)), "p_BA": float(ba[0] / sum(ba)),
    "columns_conserve_counts": bool(np.allclose(A.sum(axis=0), 1) and np.allclose(B.sum(axis=0), 1)),
}


def log_count_mean_variance(s, rates, weights):
    lr = rates * s + np.log(weights)
    top = max(lr)
    e = np.exp(lr - top)
    tilted = e / sum(e)
    mean = float(tilted @ rates)
    var = float(tilted @ ((rates - mean) ** 2))
    return float(top + math.log(sum(e))), mean, var


def second_fd(f, s, h=0.001):
    return (-f(s + 2*h) + 16*f(s + h) - 30*f(s) + 16*f(s - h) - f(s - 2*h)) / (12*h*h)


growth_error, clock_error = 0.0, 0.0
for _ in range(40):
    ra, rb = RNG.uniform(-0.7, 1, 5), RNG.uniform(-0.7, 1, 4)
    wa, wb = RNG.uniform(0.1, 1, 5), RNG.uniform(0.1, 1, 4)
    s = float(RNG.uniform(0, 2))
    f = lambda ss: log_count_mean_variance(ss, ra, wa)[0] - log_count_mean_variance(ss, rb, wb)[0]
    expected = log_count_mean_variance(s, ra, wa)[2] - log_count_mean_variance(s, rb, wb)[2]
    growth_error = max(growth_error, abs(second_fd(f, s) - expected))
    t = float(RNG.uniform(0.2, 1.2))
    exposure = t + t*t
    aa = 1 + 2*t
    ma = log_count_mean_variance(exposure, ra, wa)
    mb = log_count_mean_variance(exposure, rb, wb)
    lab = lambda tt: f(tt + tt*tt)
    expected_lab = aa*aa*(ma[2] - mb[2]) + 2*(ma[1] - mb[1])
    clock_error = max(clock_error, abs(second_fd(lab, t) - expected_lab))
assert growth_error < 2e-7 and clock_error < 2e-7
RESULTS["B2_tilted_variance_identity"] = {"cases": 40, "max_fd_error": growth_error}
RESULTS["B3_clock_correction"] = {"cases": 40, "max_fd_error": clock_error}

shift_a = log_count_mean_variance(1, np.array([1., 3.]), np.array([0.5, 0.5]))
shift_b = log_count_mean_variance(1, np.array([0., 2.]), np.array([0.5, 0.5]))
assert abs(shift_a[0] - shift_b[0] - 1) < 1e-14
assert shift_a[2] > 0.4 and abs(shift_a[2] - shift_b[2]) < 1e-14
RESULTS["B4_hidden_variance_cancellation"] = {
    "logit": shift_a[0] - shift_b[0],
    "variance_A": shift_a[2], "variance_B": shift_b[2],
}

rates = np.array([-0.3, 0.2, 0.7])
weights = np.array([0.2, 0.3, 0.5])
moments = np.array([weights @ rates**k for k in range(12)])
hankel = np.array([[moments[i+j] for j in range(5)] for i in range(5)])
rank = int(np.linalg.matrix_rank(hankel, tol=1e-12))
poly = np.poly(rates)
recurrence_error = max(abs(sum(poly[j] * moments[k+3-j] for j in range(4))) for k in range(6))
gaussian_moments = [1, 0, 1, 0, 3, 0, 15, 0, 105]
gaussian_hankel = np.array([[gaussian_moments[i+j] for j in range(5)] for i in range(5)], float)
gaussian_min_eigenvalue = float(min(np.linalg.eigvalsh(gaussian_hankel)))
assert rank == 3 and recurrence_error < 1e-12 and gaussian_min_eigenvalue > 0
RESULTS["B5_linear_moment_closure"] = {
    "finite_atomic_rank": rank, "recurrence_error": recurrence_error,
    "continuous_gaussian_H5_min_eigenvalue": gaussian_min_eigenvalue,
    "continuous_gaussian_nonlinear_closure": "mean'=variance, variance'=0 under exponential tilting",
}


def response_y(y, amp, eps):
    return (1 + (1 + amp)*y) / ((1+y)*(1+eps*y))


peak_residual, rmax_error, crossing_error = 0., 0., 0.
peak_cases, monotone_cases = 0, 0
for eps in [1e-6, 1e-3, 0.02, 0.2, 0.7, 0.99]:
    for amp in [eps*(1+1e-6), eps*1.2, 0.1, 1, 10, 100]:
        if amp <= eps:
            for y in [1e-8, 0.1, 1, 100]:
                assert amp-eps-2*eps*y-eps*(1+amp)*y*y < 0
            monotone_cases += 1
            continue
        ystar = (amp-eps)/(eps + math.sqrt(eps*amp*(1+amp-eps)))
        terms = [amp-eps, -2*eps*ystar, -eps*(1+amp)*ystar*ystar]
        peak_residual = max(peak_residual, abs(sum(terms))/max(abs(v) for v in terms))
        rstar = response_y(ystar, amp, eps)
        rmax = ((math.sqrt(1+amp-eps)-math.sqrt(amp*eps))/(1-eps))**2
        rmax_error = max(rmax_error, abs(rstar-rmax))
        assert rstar + 1e-11 >= response_y(0.7*ystar, amp, eps)
        assert rstar + 1e-11 >= response_y(1.3*ystar, amp, eps)
        crossing_error = max(crossing_error, abs(response_y((amp-eps)/eps, amp, eps)-1))
        peak_cases += 1
assert peak_residual < 1e-12 and rmax_error < 1e-9 and crossing_error < 1e-12
RESULTS["B6_exact_hormesis_peak"] = {
    "peak_cases": peak_cases, "monotone_cases": monotone_cases,
    "max_derivative_relative_residual": peak_residual,
    "max_Rmax_error": rmax_error, "max_beneficial_endpoint_error": crossing_error,
}

eps, delta = 0.2, 0.00002
amp = eps + delta
y = delta/(eps + math.sqrt(eps*amp*(1+amp-eps)))
onset_y_ratio = y/(delta/(2*eps))
excess = y*(delta-eps*y)/((1+y)*(1+eps*y))
onset_excess_ratio = excess/(delta*delta/(4*eps))
assert abs(onset_y_ratio-1) < 1e-3 and abs(onset_excess_ratio-1) < 1e-3
RESULTS["B7_hormesis_onset_scaling"] = {
    "peak_y_over_onset_asymptotic": onset_y_ratio,
    "peak_excess_over_onset_asymptotic": onset_excess_ratio,
}

unequal_error = 0.
for ha, ht in [(2., 1.), (3., 1.), (4., 2.)]:
    da, dt = 1., 5.
    d = da*((ha-ht)/ht)**(1/ha)
    crit = (da/dt)**ht * ha/(ha-ht)*((ha-ht)/ht)**(ht/ha)
    occupancy = d**ha/(d**ha+da**ha)
    survival = dt**ht/(d**ht+dt**ht)
    unequal_error = max(unequal_error, abs((1+crit*occupancy)*survival-1))
    assert (1+1.1*crit*occupancy)*survival > 1
assert unequal_error < 1e-12
RESULTS["B8_unequal_exponent_threshold"] = {"cases": 3, "max_critical_response_error": unequal_error}

quad_u, quad_w = np.polynomial.legendre.leggauss(200)
sky_error = 0.
for beta in [0.05, 0.2, 0.5, 0.85]:
    for power in [2, 4]:
        density = (1-beta*quad_u)**(-power)
        norm = np.dot(quad_w, density)
        flux = np.dot(quad_w, quad_u*density)/norm
        pressure = np.dot(quad_w, quad_u**2*density)/norm
        if power == 2:
            target_f = 1/beta-(1-beta**2)*math.atanh(beta)/beta**2
            target_p = (2*beta-beta**3-2*(1-beta**2)*math.atanh(beta))/beta**3
        else:
            target_f = 4*beta/(3+beta**2)
            target_p = (1+3*beta**2)/(3+beta**2)
        sky_error = max(sky_error, abs(flux-target_f), abs(pressure-target_p))
assert sky_error < 2e-11
RESULTS["L1_direction_vs_energy_moments"] = {
    "models": ["normalized angular pushforward exponent 2", "bolometric energy exponent 4"],
    "beta_cases": 4, "max_quadrature_error": sky_error,
}

landau_residual = 0.
for dipole in [0.001, 0.2, 0.8]:
    beta = dipole/(2+math.sqrt(4-dipole*dipole))
    landau_residual = max(landau_residual, abs(dipole*(1+beta*beta)-4*beta))
assert landau_residual < 1e-14
RESULTS["L2_dipole_Landau_frame"] = {
    "cases": 3, "max_zero_flux_residual": landau_residual,
    "small_dipole_beta_over_dipole": (0.001/(2+math.sqrt(4-0.001**2)))/0.001,
}

parabolic_shortcut = 2*math.acosh(1.5)-math.acosh(3)
assert parabolic_shortcut > 0.1
RESULTS["C1_commuting_parabolic_not_geodesic"] = {
    "adjacent_distance": math.acosh(1.5), "endpoint_distance": math.acosh(3),
    "strict_triangle_gap": parabolic_shortcut,
}

joint_eigenvalues = np.array([0.4, 0.1, 0.1, 0.4])
mutual_info = 2*math.log(2)+float(np.dot(joint_eigenvalues, np.log(joint_eigenvalues)))
binary_entropy = -0.8*math.log(0.8)-0.2*math.log(0.2)
assert abs(mutual_info-(math.log(2)-binary_entropy)) < 1e-14
assert mutual_info > 0 and np.min(joint_eigenvalues) > 0
RESULTS["C2_full_rank_correlation_record"] = {
    "initial_system": "I/2", "initial_memory": "diag(0.8,0.2)",
    "operation": "CNOT", "output_joint_min_eigenvalue": 0.1,
    "both_output_marginals": "I/2", "mutual_information_nats": mutual_info,
}

RESULTS["status"] = "all independent checks passed"
RESULTS["scope"] = "Finite numerical checks and explicit counterexamples; general statements are proved in the revised manuscripts."
target = ROOT / "quantum_kinematics_checks.json"
target.write_text(json.dumps(RESULTS, indent=2) + "\n", encoding="utf-8")
print(json.dumps(RESULTS, indent=2))
