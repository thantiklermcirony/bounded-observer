"""Rapidity charts (capstone Theorems 1-8): psi turns a bounded law into addition."""
import numpy as np

def _clip(p, eps=1e-15):
    return np.clip(np.asarray(p, float), eps, 1 - eps)

# name: (psi, psi_inverse, description)
CHARTS = {
    "logit":  (lambda p: np.log(_clip(p) / (1 - _clip(p))), lambda y: 1 / (1 + np.exp(-np.asarray(y, float))),
               "two horizons (0,1); Einstein/logit; Theorem 7"),
    "bliss":  (lambda p: -np.log(1 - _clip(p)), lambda y: 1 - np.exp(-np.asarray(y, float)),
               "one horizon at 1, rest at 0; independent failure; alpha = 0"),
    "loewe":  (lambda p: _clip(p) / (1 - _clip(p)), lambda y: np.asarray(y, float) / (1 + np.asarray(y, float)),
               "one horizon at 1 (parabolic); shared site; alpha -> 1"),
    "multiplicative": (lambda p: -np.log(_clip(p)), lambda y: np.exp(-np.asarray(y, float)),
               "one horizon at 0, rest at 1; mirror of Bliss"),
    "einstein": (lambda s: np.arctanh(np.clip(np.asarray(s, float), -1 + 1e-15, 1 - 1e-15)), lambda y: np.tanh(np.asarray(y, float)),
               "two horizons (-1,1); velocity, belief s = 2P - 1"),
}

def rapidity(x, chart="logit"):
    return CHARTS[chart][0](x)

def from_rapidity(y, chart="logit"):
    return CHARTS[chart][1](y)

def compose(a, b, chart="logit", identity=None):
    """a (+) b = psi^{-1}(psi(a) + psi(b) - psi(e)); identity defaults to the chart's neutral state."""
    psi, inv, _ = CHARTS[chart]
    e0 = 0.0 if identity is None else psi(identity)
    return inv(psi(a) + psi(b) - e0)

def hamacher_psi(e, alpha):
    """One-horizon dial (Theorem 8): psi_alpha(e) = log[(1 - alpha e)/(1 - e)]/(1 - alpha), alpha <= 1."""
    e = _clip(e)
    if abs(1 - alpha) < 1e-9:
        return e / (1 - e)
    return np.log((1 - alpha * e) / (1 - e)) / (1 - alpha)

def hamacher_compose(a, b, alpha):
    """Closed form of the Hamacher t-conorm with lambda = 1 - alpha."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    return (a + b - (1 + alpha) * a * b) / (1 - alpha * a * b)
