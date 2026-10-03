"""Every simulation on the website rests on one of these checks. Each test names its theorem."""
import cmath
import math

import numpy as np
import pytest

from bounded import law, boundary, disk, cones, coupling


# ---------------------------------------------------------------- Theorems 1-2: the horizon
def test_horizon_is_never_reached_and_rapidity_steps_are_equal():
    xs = law.repeat(0.5, 15)          # past ~19 steps a double rounds tanh to 1.0; the maths does not
    assert all(x < 1.0 for x in xs)
    psi = [law.einstein_rapidity(x) for x in xs[:15]]
    steps = np.diff(psi)
    assert np.allclose(steps, math.atanh(0.5))


def test_einstein_is_associative_and_commutative():
    a, b, c = 0.3, -0.55, 0.8
    assert math.isclose(law.einstein(law.einstein(a, b), c), law.einstein(a, law.einstein(b, c)))
    assert math.isclose(law.einstein(a, b), law.einstein(b, a))


# ---------------------------------------------------------------- Theorem 4: three forms
def test_trichotomy():
    assert law.trichotomy(0.5, 0.5, 0.0) == 1.0                           # flat
    assert law.trichotomy(0.5, 0.5, 1.0) == 0.8                           # bounded
    assert math.isclose(law.trichotomy(2, 2, -1), math.tan(2 * math.atan(2)))  # wraps: 2 (+) 2 = -4/3
    assert math.isclose(law.trichotomy(2, 2, -1), -4 / 3)


# ---------------------------------------------------------------- Theorem 8: the dial
@pytest.mark.parametrize("alpha", [-3.0, -1.0, 0.0, 0.5, 0.9])
def test_dial_is_addition_in_its_rapidity(alpha):
    a, b = 0.3, 0.45
    lhs = law.dial_rapidity(law.dial_compose(a, b, alpha), alpha)
    assert math.isclose(lhs, law.dial_rapidity(a, alpha) + law.dial_rapidity(b, alpha), rel_tol=1e-9)


def test_dial_landmarks():
    a, b = 0.3, 0.45
    assert math.isclose(law.dial_compose(a, b, 0.0), law.bliss(a, b))
    assert math.isclose(law.dial_compose(a, b, 1.0), law.loewe_odds(a, b))
    assert math.isclose(law.dial_compose(a, b, -1.0), law.einstein(a, b))


# ---------------------------------------------------------------- Proposition 9: arrival or horizon
def test_osgood():
    assert math.isclose(boundary.arrival_time(0.5, 1.0), 2.0)
    assert boundary.arrival_time(1.0, 1.0) == math.inf
    assert boundary.arrival_time(2.0, 1.0) == math.inf
    assert boundary.room_left(0.5, 1.0, 2.0) == 0.0
    assert boundary.room_left(1.0, 1.0, 50.0) > 0.0
    assert boundary.room_left(2.0, 1.0, 1e6) > 0.0


def test_maxent_exponents():
    assert boundary.maxent_exponent("atom") == 1
    assert boundary.maxent_exponent("power") == 2
    assert math.isclose(boundary.maxent_exponent("mixed", a=0), 1.5)


# ---------------------------------------------------------------- Theorem 19: the far side
def test_far_side():
    assert math.isclose(law.einstein(0.5, 2.0), 1.25)
    assert math.isclose(law.einstein(-0.9, 3.0), -1.2352941176, rel_tol=1e-9)
    z = law.far_side_rapidity(1.25)
    # the paper: artanh(0.5) + artanh(2) = artanh(1.25) = 1.0986 + i pi/2
    assert math.isclose(z.real, math.atanh(0.5) + math.atanh(1 / 2.0), rel_tol=1e-12)
    assert math.isclose(z.real, 1.0986122886681098, rel_tol=1e-9)
    assert math.isclose(z.imag, math.pi / 2)
    v, u = 0.3, 0.5
    assert math.isclose(law.einstein(1 / v, u), 1 / law.einstein(v, u))
    assert math.isclose(1 / law.einstein(v, u), 1.4375)


def test_far_side_rapidity_is_additive_through_infinity():
    # Theorem 19.2: rapidity(x + a) = rapidity(x) + rapidity(a) exactly for |x| > 1, |a| < 1,
    # including compositions that pass through infinity, e.g. (-3) + 0.5 = 5.
    assert law.far_side_rapidity(-3.0).imag == pytest.approx(math.pi / 2)
    assert law.einstein(-3.0, 0.5) == pytest.approx(5.0)
    rng = np.random.default_rng(19)
    for _ in range(10_000):
        a = rng.uniform(-0.99, 0.99)
        x = rng.choice([-1, 1]) / rng.uniform(0.01, 0.99)
        y = law.einstein(x, a)
        if abs(abs(y) - 1) < 1e-6 or not math.isfinite(y):
            continue
        lhs = law.far_side_rapidity(y)
        rhs = law.far_side_rapidity(x) + law.far_side_rapidity(a)
        assert abs(lhs - rhs) < 1e-8
        assert abs(lhs - cmath.atanh(y)) < 1e-8


# ---------------------------------------------------------------- Theorem 29: the observer is the centre
def test_observer_centrality():
    o, x, y = 0.4 + 0.3j, -0.2 + 0.6j, 0.5 - 0.1j
    assert abs(disk.recentre(o, o)) < 1e-15                              # each observer sits at its own centre
    assert abs(disk.recentre(o, x) - x) > 0.1                             # raw values differ between observers
    d_here = disk.distance(x, y)
    d_there = disk.distance(disk.recentre(o, x), disk.recentre(o, y))
    assert math.isclose(d_here, d_there, rel_tol=1e-9)                   # but distances agree


# ---------------------------------------------------------------- section 5.2, Theorem 26: holonomy
def test_gyration_equals_triangle_area():
    a, b = 0.4 + 0.2j, 0.7 * cmath.exp(2j)
    ang = abs(disk.gyration_angle(a, b))
    area = disk.triangle_area(0j, a, disk.add(a, b))
    assert math.isclose(ang, 0.600, abs_tol=5e-4)
    assert math.isclose(ang, area, rel_tol=1e-6)


def test_gyration_is_the_order_memory():
    a, b, z = 0.3 + 0.1j, -0.2 + 0.5j, 0.1 - 0.4j
    lhs = disk.add(a, disk.add(b, z))
    rhs = disk.add(disk.add(a, b), disk.gyration(a, b) * z)
    assert abs(lhs - rhs) < 1e-12


# ---------------------------------------------------------------- section 8.4: the room inside
def test_room_inside():
    assert math.isclose(disk.circle_circumference(1), 7.38, abs_tol=0.01)
    assert math.isclose(disk.circle_circumference(5), 466.3, abs_tol=0.1)
    assert disk.circle_circumference(10) > 6.9e4


# ---------------------------------------------------------------- Theorem 25: channels
def test_reversible_channels_keep_distance():
    P = np.array([[0, 2.0, 0], [0, 0, 0.5], [3.0, 0, 0]])                # positive diagonal times permutation
    assert cones.is_reversible(P)
    x, y = np.array([1, 2, 3.0]), np.array([2, 1, 1.0])
    assert math.isclose(cones.hilbert_distance(P @ x, P @ y), cones.hilbert_distance(x, y))


def test_forward_only_channels_contract_by_birkhoff():
    rng = np.random.default_rng(1)
    for _ in range(200):
        M = rng.uniform(0.1, 1.0, (3, 3))
        k = cones.birkhoff_coefficient(M)
        x, y = rng.uniform(0.01, 1, 3), rng.uniform(0.01, 1, 3)
        assert cones.hilbert_distance(M @ x, M @ y) <= k * cones.hilbert_distance(x, y) + 1e-12


def test_forward_only_need_not_commute():
    A, B = np.array([[2, 1], [1, 2.0]]), np.array([[3, 1], [1, 1.0]])
    assert not np.allclose(A @ B, B @ A)


# ---------------------------------------------------------------- Theorem 16: locking
def test_locking():
    phi, beta = 1.2, 1.0
    for u in ("sinh", "tanh", "sin"):
        d = coupling.simulate(phi, beta, u, T=30)[-1]
        assert math.isclose(d, coupling.lock_gap(phi, beta, u), abs_tol=1e-3)
    assert math.isclose(coupling.relaxation_rate(phi, beta, "tanh"), 2 * beta * (1 - (phi / (2 * beta)) ** 2))
    assert coupling.lock_gap(3.0, 1.0, "tanh") is None
    assert coupling.lock_gap(3.0, 1.0, "sinh") is not None                  # sinh always locks
    tr = coupling.simulate(3.0, 1.0, "tanh", T=40)
    rate = (tr[-1] - tr[-10001]) / 10.0
    assert math.isclose(rate, 1.0, rel_tol=1e-3)                            # drifts at |Phi| - 2 beta


# ---------------------------------------------------------------- the bracket test
def test_bracket_predicts_order_effect():
    f, g = (lambda x: 1 - x * x), (lambda x: x)
    x, eps, eta = 0.2, 1e-3, 2e-3
    measured = coupling.order_effect(f, g, x, eps, eta)
    assert math.isclose(measured, eps * eta * coupling.bracket(f, g, x), rel_tol=1e-2)


def test_shared_rapidity_means_no_order_effect():
    f = lambda x: 1 - x * x
    g = lambda x: 2.5 * (1 - x * x)
    assert abs(coupling.order_effect(f, g, 0.3, 0.05, 0.07)) < 1e-10
