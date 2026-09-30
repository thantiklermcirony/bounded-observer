"""The observer's channels: reversible updates keep distances, forward-only ones shrink them.

Theorem 25, item 4 (Birkhoff 1957; Bushell 1973): a linear map that sends the positive
orthant into itself never increases the Hilbert projective distance, and if its image
has finite projective diameter Delta it shrinks every distance by at least tanh(Delta/4).
"""
from __future__ import annotations

import itertools
import math

import numpy as np


def hilbert_distance(x, y) -> float:
    """Hilbert projective distance on the positive orthant: log(max(x/y) / min(x/y))."""
    r = np.asarray(x, float) / np.asarray(y, float)
    return float(math.log(r.max() / r.min()))


def projective_diameter(M) -> float:
    """Diameter of M(orthant): the largest distance between two columns (the image's extreme rays)."""
    M = np.asarray(M, float)
    if (M <= 0).any():
        return math.inf
    cols = [M[:, j] for j in range(M.shape[1])]
    return max(hilbert_distance(a, b) for a, b in itertools.combinations(cols, 2))


def birkhoff_coefficient(M) -> float:
    """The guaranteed contraction factor tanh(Delta/4); 1 means no guarantee."""
    d = projective_diameter(M)
    return 1.0 if math.isinf(d) else math.tanh(d / 4.0)


def is_reversible(M, tol: float = 1e-12) -> bool:
    """An orthant automorphism is a positive diagonal map times a permutation: one positive entry per row and column."""
    M = np.asarray(M, float)
    pos = M > tol
    return bool((M >= -tol).all() and (pos.sum(0) == 1).all() and (pos.sum(1) == 1).all())
