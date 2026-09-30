import cmath
import math

import pytest

from ida_live import geometry as g


def pts():
    return [0.3 + 0.2j, -0.5 + 0.1j, 0.05 - 0.7j, 0j]


def test_identity_and_inverse():
    for a in pts():
        assert abs(g.mobius_add(a, 0j) - a) < 1e-12
        assert abs(g.mobius_add(0j, a) - a) < 1e-12
        assert abs(g.mobius_add(-a, a)) < 1e-12


def test_left_cancellation():
    for a in pts():
        for b in pts():
            assert abs(g.mobius_add(-a, g.mobius_add(a, b)) - b) < 1e-10


def test_stays_in_disk():
    for a in pts():
        for b in pts():
            assert abs(g.mobius_add(a, b)) < 1.0


def test_rapidity_round_trip():
    for r in (0.0, 0.3, 1.0, 2.5):
        for th in (0.0, 1.0, -2.0):
            assert g.rapidity(g.from_rapidity(r, th)) == pytest.approx(r, abs=1e-9)


def test_collinear_rapidities_add():
    # along one direction Möbius addition is Einstein velocity addition: rapidities add
    a, b = g.from_rapidity(0.7, 0.4), g.from_rapidity(1.1, 0.4)
    assert g.rapidity(g.mobius_add(a, b)) == pytest.approx(1.8, abs=1e-9)


def test_distance_is_symmetric_and_isometric():
    a, b, c = 0.2 + 0.1j, -0.4 + 0.3j, 0.1 - 0.6j
    assert g.distance(a, b) == pytest.approx(g.distance(b, a), abs=1e-10)
    # left translation preserves distance
    assert g.distance(g.mobius_add(c, a), g.mobius_add(c, b)) == pytest.approx(g.distance(a, b), abs=1e-9)


def test_noncommutative_defect_positive():
    p = [g.from_rapidity(1.0, 0.0), g.from_rapidity(1.0, math.pi / 2)]
    assert g.composition_defect(p) > 1e-3
    assert g.composition_defect([p[0]]) == 0.0


def test_comparators_agree_on_single_axis():
    r, th = [1.2], [0.3]
    chain = g.compose(r, th, "mobius_chain")
    flat = g.compose(r, th, "euclidean_tangent")
    assert abs(chain - flat) < 1e-12
    assert abs(cmath.phase(g.compose(r, th, "einstein_midpoint")) - 0.3) < 1e-9
