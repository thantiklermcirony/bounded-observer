"""The room inside: the Poincare disk, the observer's recentring and holonomy.

Points are complex numbers with |z| < 1. Mobius addition is the two-dimensional
bounded law; it is not commutative and not associative, and what it keeps of the
order of changes is a rotation, the gyration (section 5.2, Theorem 26).
"""
from __future__ import annotations

import cmath
import math


def add(a: complex, b: complex) -> complex:
    """Mobius addition a (+) b = (a + b)/(1 + conj(a) b)."""
    return (a + b) / (1 + a.conjugate() * b)


def neg(a: complex) -> complex:
    return -a


def recentre(observer: complex, x: complex) -> complex:
    """What an observer at `observer` sees at x: (-observer) (+) x. Theorem 29, item 2."""
    return add(-observer, x)


def distance(a: complex, b: complex) -> float:
    """Rapidity distance 2 artanh |(-a) (+) b|: every observer agrees on it (Theorem 29, item 3).
    Curvature -1 convention (metric 4|dz|^2/(1-|z|^2)^2)."""
    return 2.0 * math.atanh(min(abs(recentre(a, b)), 1 - 1e-15))


def gyration(a: complex, b: complex) -> complex:
    """gyr[a, b] as a unit complex number: a (+) (b (+) z) = (a (+) b) (+) gyr[a,b] z."""
    return (1 + a * b.conjugate()) / (1 + a.conjugate() * b)


def gyration_angle(a: complex, b: complex) -> float:
    return cmath.phase(gyration(a, b))


def circle_circumference(r: float) -> float:
    """Circumference of a hyperbolic circle of radius r (curvature -1): 2 pi sinh r (section 8.4)."""
    return 2.0 * math.pi * math.sinh(r)


def _unit_tangent(p: complex, q: complex) -> complex:
    """Unit tangent at p of the geodesic from p to q."""
    w = recentre(p, q)                       # q seen from p, where geodesics are straight
    return w / abs(w)                        # the recentring map is conformal with positive derivative at 0 up to rotation


def triangle_area(p: complex, q: complex, r: complex) -> float:
    """Area of the geodesic triangle pqr (curvature -1): pi minus the sum of its angles."""
    def angle_at(x, y, z):
        # rotate so that x is at the origin; angles are preserved by the (conformal) map
        u, v = recentre(x, y), recentre(x, z)
        return abs(cmath.phase(v / u))
    return math.pi - (angle_at(p, q, r) + angle_at(q, r, p) + angle_at(r, p, q))


def geodesic(a: complex, b: complex, n: int = 64) -> list[complex]:
    """Points along the geodesic from a to b: a (+) (t * w) with w = (-a) (+) b in rapidity steps."""
    w = recentre(a, b)
    if w == 0:
        return [a] * n
    rho = math.atanh(abs(w))
    return [add(a, math.tanh(rho * i / (n - 1)) * w / abs(w)) for i in range(n)]
