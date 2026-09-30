"""The Section 13 protocol of the UHL manuscript, as functions."""
import numpy as np
from .charts import CHARTS, rapidity, hamacher_compose

def associativity_defect(ab_c, a_bc):
    """Step 2. Grouping test: mean and max |(a+b)+c - a+(b+c)| from paired measurements.
    Non-zero beyond noise = hidden state (memory/feedback), Theorem 10 corollary."""
    d = np.asarray(ab_c, float) - np.asarray(a_bc, float)
    return {"mean_defect": float(d.mean()), "max_abs_defect": float(np.abs(d).max()), "n": int(d.size)}

def fit_dial_alpha(eA, eB, eAB, grid=None):
    """Step 3. Fit the one-horizon dial position alpha (Theorem 8) to single-agent and combination effects.
    alpha = 0 Bliss, alpha -> 1 Loewe. Returns best alpha and sum of squared error."""
    grid = np.linspace(-20, 0.999, 4000) if grid is None else grid
    eA, eB, eAB = map(lambda x: np.asarray(x, float), (eA, eB, eAB))
    sse = np.array([np.sum((hamacher_compose(eA, eB, a) - eAB) ** 2) for a in grid])
    i = int(np.argmin(sse))
    return {"alpha": float(grid[i]), "sse": float(sse[i])}

def _i2(y, v):
    w = 1 / v; mu = np.sum(w * y) / np.sum(w); Q = np.sum(w * (y - mu) ** 2); k = len(y)
    return max(0.0, (Q - (k - 1)) / Q) if Q > 0 else 0.0

def invariance_i2(a, n1, c, n2):
    """Step 5. I^2 heterogeneity of four effect scales across trials (Theorem 12, H2).
    a/n1 events/total in treated, c/n2 in control. Lower I^2 = more invariant scale."""
    a, n1, c, n2 = map(lambda x: np.asarray(x, float), (a, n1, c, n2))
    z = (a == 0) | (c == 0) | (a == n1) | (c == n2); cc = np.where(z, 0.5, 0.0)
    a, c, n1, n2 = a + cc, c + cc, n1 + 2 * cc, n2 + 2 * cc
    p1, p0 = a / n1, c / n2
    out = {
        "risk_difference (flat)": _i2(p1 - p0, p1*(1-p1)/n1 + p0*(1-p0)/n2),
        "log_risk_ratio (multiplicative)": _i2(np.log(p1/p0), (1-p1)/(n1*p1) + (1-p0)/(n2*p0)),
        "log_odds_ratio (logit)": _i2(np.log(p1/(1-p1)) - np.log(p0/(1-p0)), 1/(n1*p1*(1-p1)) + 1/(n2*p0*(1-p0))),
        "bliss_difference": _i2(np.log((1-p0)/(1-p1)), p1/(n1*(1-p1)) + p0/(n2*(1-p0))),
    }
    return out

def einstein_ceiling(a, b, a_plus_b):
    """Step 6. Ceiling from small combinations in the Einstein chart (Theorem 17, exact):
    l^2 = a b (a+b) / (a + b - a(+)b)."""
    a, b, s = map(lambda x: np.asarray(x, float), (a, b, a_plus_b))
    return np.sqrt(a * b * s / (a + b - s))

def inertia_curvature(t, x, chart="logit"):
    """Step 4. Fit psi(x(t)) = c0 + c1 t + c2 t^2. c2 != 0 beyond error = feedback or changing drive (Theorem 11).
    Fit to medians where noise is present (Theorem 20)."""
    t = np.asarray(t, float); y = rapidity(np.asarray(x, float), chart)
    X = np.vstack([np.ones_like(t), t, t**2]).T
    coef, res, *_ = np.linalg.lstsq(X, y, rcond=None)
    dof = max(1, len(t) - 3); s2 = float(res[0]) / dof if res.size else 0.0
    cov = s2 * np.linalg.inv(X.T @ X)
    return {"c0": coef[0], "c1": coef[1], "c2": coef[2], "c2_se": float(np.sqrt(cov[2, 2]))}

def boundary_audit(event_description):
    """Step 7. Theorem 18 checklist: an arrival at a limit must match one broken condition."""
    return {"event": event_description,
            "check_one_of": ["associativity failed (hidden state, feedback, memory)",
                             "strict monotonicity failed (switch, bistability, saturation at the boundary)",
                             "continuity failed (discrete jump, finite-number noise, absorbing event)",
                             "drive unbounded", "law changed over time"]}
