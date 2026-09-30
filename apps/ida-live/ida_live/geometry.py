"""Hyperbolic geometry for the state map.

Everything here is plain mathematics with no physiology in it. Points live in the
open unit disk (Poincaré model) and are represented as Python complex numbers.

Conventions
-----------
* A signed displacement ``r`` along a direction ``theta`` (a rapidity) becomes the
  disk point ``tanh(r / 2) * exp(i * theta)``. That point is at hyperbolic distance
  ``|r|`` from the origin, so the map's radius reads directly as rapidity.
* ``mobius_add(a, b) = (a + b) / (1 + conj(a) * b)`` is Möbius (gyro)addition.
  It is not commutative; the order of composition is declared in the map file
  and the order-dependence is reported as the "composition defect".
* Two comparators are provided so the calibration gate can ask whether the
  hyperbolic composition earns its place: the Einstein (gyro)midpoint, which is
  order-free, and a Euclidean tangent-space sum mapped once into the disk.
"""

from __future__ import annotations

import cmath
import math
from typing import Iterable, Sequence

EPS = 1e-12
MAX_RADIUS = 1.0 - 1e-9


def clamp_disk(p: complex) -> complex:
    """Keep a point strictly inside the unit disk."""
    r = abs(p)
    if r >= MAX_RADIUS:
        return p / r * MAX_RADIUS
    return p


def from_rapidity(r: float, theta: float) -> complex:
    """Disk point at hyperbolic distance |r| from 0 along theta (sign flips direction)."""
    return clamp_disk(math.tanh(r / 2.0) * cmath.exp(1j * theta))


def rapidity(p: complex) -> float:
    """Hyperbolic distance of p from the origin."""
    return 2.0 * math.atanh(min(abs(p), MAX_RADIUS))


def mobius_add(a: complex, b: complex) -> complex:
    """Möbius addition a ⊕ b in the Poincaré disk."""
    return clamp_disk((a + b) / (1.0 + a.conjugate() * b))


def mobius_neg(a: complex) -> complex:
    return -a


def distance(a: complex, b: complex) -> float:
    """Hyperbolic distance between two disk points."""
    return rapidity(mobius_add(mobius_neg(a), b))


def mobius_chain(points: Sequence[complex]) -> complex:
    """Left-to-right composition p1 ⊕ p2 ⊕ ... (declared order matters)."""
    acc = 0j
    for p in points:
        acc = mobius_add(acc, p)
    return acc


def composition_defect(points: Sequence[complex]) -> float:
    """Distance between forward and reverse composition: a measure of order-dependence."""
    if len(points) < 2:
        return 0.0
    return distance(mobius_chain(points), mobius_chain(list(reversed(points))))


def _poincare_to_klein(p: complex) -> complex:
    return 2.0 * p / (1.0 + abs(p) ** 2)


def _klein_to_poincare(k: complex) -> complex:
    return k / (1.0 + math.sqrt(max(0.0, 1.0 - abs(k) ** 2)))


def einstein_midpoint(points: Sequence[complex], weights: Iterable[float] | None = None) -> complex:
    """Weighted Einstein (gyro)midpoint, computed in the Klein model. Order-free."""
    pts = list(points)
    if not pts:
        return 0j
    ws = list(weights) if weights is not None else [1.0] * len(pts)
    num = 0j
    den = 0.0
    for p, w in zip(pts, ws):
        k = _poincare_to_klein(p)
        gamma = 1.0 / math.sqrt(max(EPS, 1.0 - abs(k) ** 2))
        num += w * gamma * k
        den += w * gamma
    if den <= EPS:
        return 0j
    return clamp_disk(_klein_to_poincare(num / den))


def euclidean_tangent(rapidities: Sequence[float], thetas: Sequence[float]) -> complex:
    """Euclidean comparator: add displacement vectors flat, then map once into the disk."""
    v = sum(r * cmath.exp(1j * t) for r, t in zip(rapidities, thetas))
    if abs(v) < EPS:
        return 0j
    return from_rapidity(abs(v), cmath.phase(v))


def compose(rapidities: Sequence[float], thetas: Sequence[float], method: str = "mobius_chain") -> complex:
    """Compose per-feature displacements into one disk point."""
    if method == "euclidean_tangent":
        return euclidean_tangent(rapidities, thetas)
    pts = [from_rapidity(r, t) for r, t in zip(rapidities, thetas)]
    if method == "einstein_midpoint":
        return einstein_midpoint(pts)
    if method == "mobius_chain":
        return mobius_chain(pts)
    raise ValueError(f"unknown composition method {method!r}")
