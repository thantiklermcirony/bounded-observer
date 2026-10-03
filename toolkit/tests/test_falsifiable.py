"""Checks that could fail. Each computes a theorem's conclusion independently of the toolkit's
own formula for it, from its hypotheses, by quadrature, integration or simulation, and names
the theorem it checks. Several carry a negative control: the same check run on a deliberately
wrong version must fail, which shows that the check has the power to catch an error.
"""
import cmath
import math

import numpy as np
import pytest
from scipy.integrate import quad, solve_ivp
from scipy.special import expit, gamma as Gamma, gammainc, logit

from bounded import boundary, charts, disk, law, protocol


# ---------------------------------------------------------------- Proposition 3: max-ent averages
def _maxent_gap_and_var(theta, atom, a, c=1.0):
    """Reference measure on s in [0, 1], written in u = 1 - s: an atom of mass `atom` at u = 0
    (the ceiling) plus a density c u^a on (0, 1]. Tilt by e^{theta s}. Returns the gap
    delta = E[u] = s_max - m and the generator X(m) = Var(s), by exact incomplete-gamma integrals."""
    I = lambda k: c * gammainc(a + k + 1, theta) * Gamma(a + k + 1) / theta ** (a + k + 1)
    Z = atom + I(0)
    m1, m2 = I(1) / Z, I(2) / Z
    return m1, m2 - m1 ** 2


@pytest.mark.parametrize("atom,a,gamma_expected", [
    (0.0, 0.0, 2.0),           # density positive at the end: Langevin chart
    (0.0, 2.0, 2.0),           # density ~ u^2, still no atom
    (1.0, 0.0, 1.5),           # atom beside a density positive at the end: 1 + 1/(a+2)
    (1.0, 1.0, 1 + 1 / 3),
    (1.0, -0.5, 1 + 1 / 1.5),
])
def test_prop3_boundary_exponent_by_quadrature(atom, a, gamma_expected):
    # Proposition 3: X ~ (s_max - m)^gamma with gamma = 2 without an atom, 1 + 1/(a+2) with one.
    d1, x1 = _maxent_gap_and_var(1e5, atom, a)
    d2, x2 = _maxent_gap_and_var(2e5, atom, a)
    local_gamma = math.log(x2 / x1) / math.log(d2 / d1)
    assert local_gamma == pytest.approx(gamma_expected, abs=0.01)


def test_prop3_two_states_give_exponent_one():
    # Proposition 3: an isolated atom at the ceiling (two states, logit chart) gives gamma = 1.
    for theta in (5.0, 20.0, 40.0):
        delta = expit(-theta)                    # mass at s = 0 under the tilt, = s_max - m
        var = (1 - delta) * delta
        assert var / delta == pytest.approx(1 - delta, rel=1e-12)


def test_prop3_density_vanishing_faster_than_any_power_gives_exponent_three():
    # Proposition 3: a density e^{-1/u} at the end gives X ~ (s_max - m)^3 / 2.
    def moments(theta):
        u0 = 1 / math.sqrt(theta)
        f = lambda u, k: u ** k * math.exp(-1 / u - theta * u + 2 * math.sqrt(theta)) if u > 0 else 0.0
        Z, M1, M2 = (quad(f, 0, 1, args=(k,), points=[u0 / 4, u0, 4 * u0], limit=500)[0] for k in (0, 1, 2))
        return M1 / Z, M2 / Z - (M1 / Z) ** 2
    d1, x1 = moments(1e4)
    d2, x2 = moments(2e4)
    assert math.log(x2 / x1) / math.log(d2 / d1) == pytest.approx(3.0, abs=0.05)
    assert x1 / d1 ** 3 == pytest.approx(0.5, abs=0.02)


def test_prop3_variance_bound_on_random_measures():
    # Proposition 3: Var_theta(s) <= L (s_max - m) for every reference measure and every theta.
    rng = np.random.default_rng(3)
    worst = 0.0
    for _ in range(2000):
        n = rng.integers(2, 12)
        s = np.sort(rng.uniform(0, 1, n)); w = rng.dirichlet(np.ones(n))
        L, s_max = s[-1] - s[0], s[-1]
        for theta in (-30.0, -3.0, 0.0, 3.0, 30.0):
            q = w * np.exp(theta * (s - s_max)); q /= q.sum()
            gap = q @ (s_max - s)                # s_max - m, computed without cancellation
            var = q @ ((s - s_max) + gap) ** 2
            if gap > 0:
                worst = max(worst, var / (L * gap))
    assert worst <= 1.0 + 1e-12


# ---------------------------------------------------------------- Proposition 9(a): Osgood
@pytest.mark.parametrize("gamma", [0.0, 0.5, 0.9])
def test_prop9_arrival_in_finite_time_when_gamma_below_one(gamma):
    # Proposition 9(a): delta' = -delta^gamma reaches 0 at the time boundary.arrival_time gives.
    delta0 = 0.3
    hit = lambda t, y: y[0] - 1e-10
    hit.terminal, hit.direction = True, -1
    sol = solve_ivp(lambda t, y: [-max(y[0], 0.0) ** gamma], (0, 100), [delta0],
                    events=hit, rtol=1e-11, atol=1e-14, max_step=1e-3)
    assert sol.t_events[0].size == 1
    # the event fires at gap 1e-10, which the exact solution reaches arrival_time(1e-10) before the end
    expected = boundary.arrival_time(gamma, delta0) - boundary.arrival_time(gamma, 1e-10)
    assert sol.t_events[0][0] == pytest.approx(expected, rel=1e-6)


@pytest.mark.parametrize("gamma", [1.0, 1.5, 2.0])
def test_prop9_no_arrival_when_gamma_at_least_one(gamma):
    # Proposition 9(a): for gamma >= 1 the gap stays positive and matches boundary.room_left.
    delta0, T = 0.3, 50.0
    sol = solve_ivp(lambda t, y: [-y[0] ** gamma], (0, T), [delta0], rtol=1e-11, atol=1e-300, dense_output=True)
    for t in (1.0, 10.0, T):
        got = float(sol.sol(t)[0])
        assert got > 0
        assert got == pytest.approx(boundary.room_left(gamma, delta0, t), rel=1e-6)


# ---------------------------------------------------------------- Theorems 20-21: noise in rapidity
def test_ito_drift_of_theorem_20_with_negative_control():
    # Theorem 20: if d psi = k dt + sigma dW, then p = logistic(psi) obeys
    # dp = p(1-p)[k + sigma^2 (1-2p)/2] dt + sigma p(1-p) dW. Simulate p directly (Milstein) and
    # compare its quantiles with the exact law of logistic(psi). Removing the Ito term must fail.
    rng = np.random.default_rng(20)
    N, T, dt, k, s, p0 = 20_000, 1.0, 5e-4, 0.5, 1.5, 0.3
    q = np.array([0.1, 0.25, 0.5, 0.75, 0.9])
    exact = expit(logit(p0) + k * T + s * math.sqrt(T) * rng.standard_normal(200_000))

    def simulate(ito_term):
        p = np.full(N, p0)
        for _ in range(int(T / dt)):
            dW = math.sqrt(dt) * rng.standard_normal(N)
            g = p * (1 - p)
            drift = g * (k + (0.5 * s * s * (1 - 2 * p) if ito_term else 0.0))
            p = p + drift * dt + s * g * dW + 0.5 * (s * g) * (s * (1 - 2 * p)) * (dW ** 2 - dt)
            p = np.clip(p, 1e-12, 1 - 1e-12)
        return p

    ref = np.quantile(exact, q)
    assert np.abs(np.quantile(simulate(True), q) - ref).max() < 0.02
    assert np.abs(np.quantile(simulate(False), q) - ref).max() > 0.05      # negative control


def test_theorem_21_median_follows_the_deterministic_law_and_the_mean_does_not():
    # Theorem 21: p(t) is logit-normal; its median is logistic(psi0 + k t) exactly, its mean is not.
    rng = np.random.default_rng(21)
    psi0, k, s, t = logit(0.3), 0.5, 1.5, 1.0
    p = expit(psi0 + k * t + s * math.sqrt(t) * rng.standard_normal(400_000))
    target = expit(psi0 + k * t)
    se = p.std() / math.sqrt(p.size)
    assert abs(np.median(p) - target) < 0.005
    assert abs(p.mean() - target) > 10 * se


# ---------------------------------------------------------------- Theorem 26: holonomy is area
def test_gyration_angle_equals_area_on_random_pairs():
    # Theorem 26 / section 5.2: |gyr[a, b]| = area of the geodesic triangle (0, a, a (+) b),
    # with the sign opposite to the orientation of (a, b).
    rng = np.random.default_rng(26)
    checked = 0
    for _ in range(5000):
        a, b = complex(*rng.uniform(-0.7, 0.7, 2)), complex(*rng.uniform(-0.7, 0.7, 2))
        if min(abs(a), abs(b)) < 1e-3:
            continue
        g = disk.gyration_angle(a, b)
        area = disk.triangle_area(0, a, disk.add(a, b))
        assert abs(abs(g) - area) < 1e-10
        orientation = (a.conjugate() * b).imag
        if abs(orientation) > 1e-9:
            assert math.copysign(1, g) == -math.copysign(1, orientation)
        checked += 1
    assert checked > 4900


# ---------------------------------------------------------------- Theorems 1-8: the charts module
def test_charts_hamacher_matches_law_dial_and_adds_in_its_rapidity():
    # Theorem 8: charts.hamacher_* and law.dial_* are independent codings of the same dial.
    rng = np.random.default_rng(8)
    for _ in range(2000):
        alpha = rng.uniform(-5, 0.95)
        a, b = rng.uniform(0, 0.95, 2)
        c = charts.hamacher_compose(a, b, alpha)
        assert c == pytest.approx(law.dial_compose(a, b, alpha), rel=1e-10, abs=1e-12)
        assert charts.hamacher_psi(c, alpha) == pytest.approx(
            charts.hamacher_psi(a, alpha) + charts.hamacher_psi(b, alpha), rel=1e-8, abs=1e-10)


def test_charts_compose_gives_the_classical_laws():
    # Theorems 7-8: Bliss multiplies survivals, Loewe adds odds, logit adds log-odds about 1/2,
    # Einstein is (a + b)/(1 + ab); each is associative.
    rng = np.random.default_rng(7)
    for _ in range(500):
        a, b, c = rng.uniform(0.01, 0.9, 3)
        assert charts.compose(a, b, "bliss") == pytest.approx(1 - (1 - a) * (1 - b), rel=1e-12)
        odds = a / (1 - a) + b / (1 - b)
        assert charts.compose(a, b, "loewe") == pytest.approx(odds / (1 + odds), rel=1e-12)
        x, y = 2 * a - 1, 2 * b - 1
        assert charts.compose(x, y, "einstein") == pytest.approx((x + y) / (1 + x * y), rel=1e-10)
        for name in ("logit", "bliss", "loewe"):
            left = charts.compose(charts.compose(a, b, name), c, name)
            right = charts.compose(a, charts.compose(b, c, name), name)
            assert left == pytest.approx(right, rel=1e-9)
    assert charts.compose(0.3, 0.5, "logit") == pytest.approx(0.3)      # 1/2 is the resting state


# ---------------------------------------------------------------- Theorem 12, H2: the protocol
def test_invariance_i2_finds_the_scale_that_was_held_constant():
    # Theorem 12 / protocol step 5: trials that share one true log risk ratio across varied
    # baselines must show log-RR I^2 near 0 and risk-difference I^2 well above it.
    rng = np.random.default_rng(12)
    p0 = np.array([0.02, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35])
    p1 = 0.5 * p0
    n = np.full(p0.size, 200_000.0)
    c = rng.binomial(n.astype(int), p0).astype(float)
    a = rng.binomial(n.astype(int), p1).astype(float)
    out = protocol.invariance_i2(a, n, c, n)
    assert out["log_risk_ratio (multiplicative)"] < 0.3
    assert out["risk_difference (flat)"] > 0.9


def test_einstein_ceiling_recovers_the_ceiling():
    # Theorem 17: l^2 = ab(a (+) b)/(a + b - a (+) b) recovers the ceiling of an Einstein law exactly.
    for ell in (1.0, 3.0, 299_792.458):
        rng = np.random.default_rng(17)
        a, b = rng.uniform(0.01, 0.5, 2) * ell
        ab = (a + b) / (1 + a * b / ell ** 2)
        assert protocol.einstein_ceiling(a, b, ab) == pytest.approx(ell, rel=1e-9)
