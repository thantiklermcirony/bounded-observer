"""The law itself: bounded composition, its horizon and its three forms.

Every function states the result it implements. Theorem numbers refer to
*Bounded Composition and Its Horizons*, version 2.1 (papers/capstone/).
"""
from __future__ import annotations

import math


def einstein(a: float, b: float, ceiling: float = 1.0) -> float:
    """Two-horizon law on (-c, c): a (+) b = (a + b) / (1 + ab/c^2). Theorems 1 and 7."""
    return (a + b) / (1.0 + a * b / ceiling ** 2)


def einstein_rapidity(x: float, ceiling: float = 1.0) -> float:
    """psi(x) = c artanh(x/c): Einstein composition becomes ordinary addition. Theorem 1."""
    return ceiling * math.atanh(x / ceiling)


def from_einstein_rapidity(psi: float, ceiling: float = 1.0) -> float:
    return ceiling * math.tanh(psi / ceiling)


def repeat(step: float, n: int, law=einstein) -> list[float]:
    """Compose the same change n times from rest. The values approach the ceiling and
    never reach it, while the rapidity climbs by equal steps (Theorem 1)."""
    out, x = [0.0], 0.0
    for _ in range(n):
        x = law(x, step)
        out.append(x)
    return out


def trichotomy(u: float, v: float, kappa: float) -> float:
    """u (+) v = (u + v)/(1 + kappa u v). kappa > 0 bounded (two horizons), kappa = 0 flat,
    kappa < 0 wraps through infinity (tan addition). Theorem 4."""
    den = 1.0 + kappa * u * v
    return math.inf if den == 0 else (u + v) / den


def trichotomy_type(kappa: float) -> str:
    return "hyperbolic" if kappa > 0 else ("parabolic" if kappa == 0 else "elliptic")


# ------------------------------------------------------------------ one horizon: the dial

def dial_compose(a: float, b: float, alpha: float) -> float:
    """One-horizon projective law resting at 0 with horizon at 1 (Theorem 8):
    a (+) b = (a + b - (1 + alpha) a b) / (1 - alpha a b), alpha <= 1.
    alpha = 0 Bliss independence; alpha -> 1 Loewe (odds add); alpha = -1 Einstein on [0, 1)."""
    return (a + b - (1.0 + alpha) * a * b) / (1.0 - alpha * a * b)


def dial_rapidity(e: float, alpha: float) -> float:
    """psi_alpha(e) = log[(1 - alpha e)/(1 - e)] / (1 - alpha); the alpha -> 1 limit is the odds e/(1-e)."""
    if abs(1.0 - alpha) < 1e-12:
        return e / (1.0 - e)
    return math.log((1.0 - alpha * e) / (1.0 - e)) / (1.0 - alpha)


def bliss(a: float, b: float) -> float:
    """Independent action: the chances of not acting multiply."""
    return 1.0 - (1.0 - a) * (1.0 - b)


def loewe_odds(a: float, b: float) -> float:
    """Loewe additivity for Hill slope 1 and full efficacy: the odds e/(1-e) add."""
    o = a / (1.0 - a) + b / (1.0 - b)
    return o / (1.0 + o)


# ------------------------------------------------------------------ the far side (Theorem 19)

def far_side_rapidity(x: float) -> complex:
    """For |x| > 1: artanh x = artanh(1/x) + i pi/2 (principal branch, A.19).
    An outside state is the reciprocal of an inside one, rapidity turned a quarter.
    The imaginary part is +i pi/2 on the whole far side, for x < -1 as well as x > 1,
    so additivity holds exactly when a composition passes through infinity."""
    if abs(x) <= 1:
        return complex(math.atanh(x), 0.0)
    return complex(math.atanh(1.0 / x), math.pi / 2)


def simultaneity_slope(v: float) -> float:
    """In 1+1 dimensions (c = 1) an observer at velocity v has simultaneity slope 1/v.
    A boost u sends 1/v to (1/v) (+) u = 1/(v (+) u): one law moves both (Theorem 19)."""
    return math.inf if v == 0 else 1.0 / v
