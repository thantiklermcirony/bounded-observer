"""Context-tree weighting (CTW) entropy estimation, as the Murray Reality Equation specifies Φ.

CTW (Willems, Shtarkov & Tjalkens 1995) mixes every tree source up to depth D with the
Krichevsky–Trofimov estimator at each node; its code length is within a small, known redundancy
of the best tree model in hindsight, which is why the MRE paper prefers it to LZ or spectral
entropy. Here an 8-bit-quantised window is serialised most-significant bit first and coded as a
binary sequence whose context is the previous D bits (D = 16 spans the two previous samples),
the usual binary decomposition. Returns the code length in bits: the entropy estimate of the
window, so Φ = bits / window seconds.
"""

from __future__ import annotations

import math
from typing import Dict

import numpy as np

LOG_HALF = math.log(0.5)


def _logaddexp(a: float, b: float) -> float:
    if a < b:
        a, b = b, a
    return a + math.log1p(math.exp(b - a))


def ctw_code_length(bits: np.ndarray, depth: int = 16) -> float:
    """Code length (bits) of a 0/1 sequence under binary CTW of the given depth."""
    b = np.asarray(bits, dtype=np.int8)
    n = len(b)
    if n == 0:
        return 0.0
    # per node: [count0, count1, log Pe, log Pw]
    nodes: Dict[int, list] = {}
    ctx = 0
    mask = (1 << depth) - 1
    total_log = 0.0
    for i in range(n):
        x = int(b[i])
        # the context path: node ids for depths D..0 (key = depth << 32 | suffix)
        path = []
        for d in range(depth, -1, -1):
            key = (d << 32) | (ctx & ((1 << d) - 1))
            path.append((d, key))
        # update from the leaf (depth D) up to the root
        child_logw = None
        for idx, (d, key) in enumerate(path):
            nd = nodes.get(key)
            if nd is None:
                nd = [0, 0, 0.0, 0.0]
                nodes[key] = nd
            a, c = nd[0], nd[1]
            # KT sequential update of the node's own estimate
            nd[2] += math.log(((c if x else a) + 0.5) / (a + c + 1.0))
            if x:
                nd[1] += 1
            else:
                nd[0] += 1
            if d == depth:
                nd[3] = nd[2]
            else:
                # the child on the path was just updated; the sibling is unchanged
                bit_below = (ctx >> d) & 1          # which child of this node lies on the path
                sib_key = ((d + 1) << 32) | ((ctx & ((1 << d) - 1)) | ((1 - bit_below) << d))
                sib = nodes.get(sib_key)
                sib_logw = sib[3] if sib is not None else 0.0
                nd[3] = LOG_HALF + _logaddexp(nd[2], child_logw + sib_logw)
            child_logw = nd[3]
        ctx = ((ctx << 1) | x) & mask
    root = nodes[(0 << 32) | 0]
    return -root[3] / math.log(2)


def ctw_symbols(q: np.ndarray, nbits: int = 8, history: int = 1) -> float:
    """Code length (bits) of 8-bit symbols by decomposed CTW (Tjalkens, Volf & Willems 1997):
    one context tree per bit position; the context of bit j of sample t is the bits of sample t
    already coded (most recent first) followed by the previous `history` samples, most
    significant bit first. This lets the model learn both the amplitude distribution and the
    dependence on the previous sample, which a flat bit context cannot within a 2 s window."""
    q = np.asarray(q, dtype=np.int64)
    trees = [dict() for _ in range(nbits)]
    total = 0.0
    prevbits = [0] * (nbits * history)
    for t in range(len(q)):
        v = int(q[t])
        cur = []
        for j in range(nbits):
            x = (v >> (nbits - 1 - j)) & 1
            ctx = list(reversed(cur)) + prevbits
            nodes = trees[j]
            D = len(ctx)
            # keys: tuple of the first d context bits
            keys = [tuple(ctx[:d]) for d in range(D + 1)]
            child_logw = None
            before = nodes.get((), [0, 0, 0.0, 0.0])[3]
            for d in range(D, -1, -1):
                key = keys[d]
                nd = nodes.get(key)
                if nd is None:
                    nd = [0, 0, 0.0, 0.0]
                    nodes[key] = nd
                a, c = nd[0], nd[1]
                nd[2] += math.log(((c if x else a) + 0.5) / (a + c + 1.0))
                if x:
                    nd[1] += 1
                else:
                    nd[0] += 1
                if d == D:
                    nd[3] = nd[2]
                else:
                    sib = nodes.get(key + (1 - ctx[d],))
                    nd[3] = LOG_HALF + _logaddexp(nd[2], child_logw + (sib[3] if sib is not None else 0.0))
                child_logw = nd[3]
            total += -(nodes[()][3] - before) / math.log(2)
            cur.append(x)
        prevbits = ([(v >> (nbits - 1 - k)) & 1 for k in range(nbits)] + prevbits)[: nbits * history]
    return total


def quantise(x: np.ndarray, levels: int = 256) -> np.ndarray:
    lo, hi = float(np.min(x)), float(np.max(x))
    if hi - lo < 1e-12:
        return np.zeros(len(x), dtype=np.int64)
    return np.clip(((x - lo) / (hi - lo) * (levels - 1)).round().astype(np.int64), 0, levels - 1)


def serialise(q: np.ndarray, nbits: int = 8) -> np.ndarray:
    """Most-significant bit first."""
    return ((q[:, None] >> np.arange(nbits - 1, -1, -1)[None, :]) & 1).reshape(-1)


def phi_ctw(x: np.ndarray, seconds: float) -> float:
    """Φ in bits per second for one window of (already filtered) EEG: decomposed CTW over the
    8-bit quantised samples, as the MRE specifies (2 s windows, 8-bit quantisation)."""
    return ctw_symbols(quantise(x)) / seconds
