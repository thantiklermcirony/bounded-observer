"""Can the ceiling be reached? The boundary exponent decides (Proposition 9, Proposition 3).

Near the ceiling write delta = 1 - e for the room left, and suppose the approach runs
d(delta)/dt = -k delta**gamma. Osgood (1898): the ceiling is reached in finite time
exactly when gamma < 1. The rapidity psi = integral de / X(e) diverges exactly when
gamma >= 1, so a horizon is Osgood's criterion read backwards.
"""
from __future__ import annotations

import math


def arrival_time(gamma: float, delta0: float, k: float = 1.0) -> float:
    """Time to use up the room delta0 under d(delta)/dt = -k delta**gamma; inf when gamma >= 1."""
    if gamma >= 1.0:
        return math.inf
    return delta0 ** (1.0 - gamma) / (k * (1.0 - gamma))


def room_left(gamma: float, delta0: float, t: float, k: float = 1.0) -> float:
    """Closed-form room left at time t (0 once reached, which happens only for gamma < 1)."""
    if gamma == 1.0:
        return delta0 * math.exp(-k * t)
    base = delta0 ** (1.0 - gamma) - (1.0 - gamma) * k * t
    if gamma < 1.0:
        return 0.0 if base <= 0 else base ** (1.0 / (1.0 - gamma))
    return base ** (1.0 / (1.0 - gamma))  # gamma > 1: base grows, delta decays like a power


def maxent_exponent(kind: str, a: float | None = None) -> float:
    """Boundary exponent of the maximum-entropy generator (Proposition 3; A.8):
    'atom'   an isolated state at the end (e.g. two states)          -> 1
    'power'  a density that is a power of the distance to the end     -> 2
    'mixed'  an atom beside a density u**a                            -> 1 + 1/(a + 2)
    There is no upper bound: an essential zero such as exp(-1/u) gives 3."""
    if kind == "atom":
        return 1.0
    if kind == "power":
        return 2.0
    if kind == "mixed":
        if a is None:
            raise ValueError("give the density exponent a")
        return 1.0 + 1.0 / (a + 2.0)
    raise ValueError(kind)
