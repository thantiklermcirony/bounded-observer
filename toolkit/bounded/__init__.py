"""bounded: the mathematics of The Bounded Observer as runnable code.

Each module implements proven results of *Bounded Composition and Its Horizons* (v2.1)
and names the theorem it implements. The tests in toolkit/tests check every one numerically.

    law       the law, the horizon, the three forms, the one-horizon dial, the far side
    boundary  arrival or horizon: the boundary exponent
    disk      the Poincare disk: recentring, distance, gyration, room inside
    cones     channels: Hilbert distance and Birkhoff contraction
    coupling  locking of two rapidities; the bracket (order) test
    charts    named rapidity charts (logit, Bliss, Loewe, Einstein)
    protocol  the section 13 test protocol as functions
"""
from . import law, boundary, disk, cones, coupling, charts, protocol
from .charts import CHARTS, rapidity, from_rapidity, compose, hamacher_psi, hamacher_compose
from .protocol import (associativity_defect, fit_dial_alpha, invariance_i2, einstein_ceiling,
                       inertia_curvature, boundary_audit)

__version__ = "1.0.0"
