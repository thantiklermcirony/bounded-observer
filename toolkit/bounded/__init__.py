"""bounded: the mathematics of The Bounded Observer as runnable code.

The original modules implement the frozen v2.1 composition model. The records and
hormesis modules implement selected, explicitly scoped results of the October
2026 library. See RECORDS.md and HORMESIS.md for their premises and source links.

    law       the law, the horizon, the three forms, the one-horizon dial, the far side
    boundary  arrival or horizon: the boundary exponent
    disk      the Poincare disk: recentring, distance, gyration, room inside
    cones     channels: Hilbert distance and Birkhoff contraction
    coupling  locking of two rapidities; the bracket (order) test
    charts    named rapidity charts (logit, Bliss, Loewe, Einstein)
    protocol  the section 13 test protocol as functions
    records   supplied retained algebras, forgetting, local CP rate cones and bounds
    hormesis  exact laws and assay thresholds for specified response models
"""
from . import law, boundary, disk, cones, coupling, charts, protocol, records, hormesis
from .charts import CHARTS, rapidity, from_rapidity, compose, hamacher_psi, hamacher_compose
from .protocol import (associativity_defect, fit_dial_alpha, invariance_i2, einstein_ceiling,
                       inertia_curvature, boundary_audit)

__version__ = "1.1.0"
