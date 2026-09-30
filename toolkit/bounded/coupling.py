"""Two coupled rapidities, and the order of two small changes.

Theorem 16 (locking): the gap D between two rapidities obeys dD/dt = Phi - 2 beta u(D).
  u = sinh (or any strictly increasing unbounded u): one stable lock for every drive Phi.
  u = tanh (bounded): a lock only while |Phi| < 2 beta; beyond it the gap drifts at |Phi| - 2 beta.
  u = sin (periodic): a lock only while |Phi| < 2 beta; beyond it the phase slips with
      period 2 pi / sqrt(Phi^2 - 4 beta^2) (Adler 1946).
The bracket test (section 5, order effects): applying flow f for time eps then g for eta,
against the reverse order, differs at x by eps*eta*(f g' - g f') to leading order.
If that vanishes everywhere, g = c f and both flows share one rapidity psi = integral dx/f.
"""
from __future__ import annotations

import math

U = {"sinh": math.sinh, "tanh": math.tanh, "sin": math.sin, "linear": lambda d: d}


def lock_gap(phi: float, beta: float, u: str) -> float | None:
    """The locked gap, or None when there is no lock."""
    s = phi / (2.0 * beta)
    if u == "sinh":
        return math.asinh(s)
    if u == "linear":
        return s
    if abs(s) >= 1.0:
        return None
    return math.atanh(s) if u == "tanh" else math.asin(s)


def relaxation_rate(phi: float, beta: float, u: str) -> float | None:
    """Rate 2 beta u'(D*) of return to the lock; for tanh it is 2 beta [1 - (Phi/2beta)^2] (critical slowing)."""
    d = lock_gap(phi, beta, u)
    if d is None:
        return None
    du = {"sinh": math.cosh(d), "tanh": 1 - math.tanh(d) ** 2, "sin": math.cos(d), "linear": 1.0}[u]
    return 2.0 * beta * du


def unlocked_drift(phi: float, beta: float, u: str) -> float:
    """Long-run mean rate of change of the gap once there is no lock (0 while locked)."""
    if abs(phi) < 2.0 * beta or u in ("sinh", "linear"):
        return 0.0
    if u == "tanh":
        return math.copysign(abs(phi) - 2.0 * beta, phi)
    return math.copysign(math.sqrt(phi * phi - 4.0 * beta * beta), phi)  # sin: 2 pi / slip period


def simulate(phi: float, beta: float, u: str, d0: float = 0.0, T: float = 20.0, dt: float = 1e-3) -> list[float]:
    f, d, out = U[u], d0, [d0]
    for _ in range(int(T / dt)):
        d += dt * (phi - 2.0 * beta * f(d))
        out.append(d)
    return out


def order_effect(f, g, x: float, eps: float, eta: float, steps: int = 2000) -> float:
    """(g for eta after f for eps) minus (f for eps after g for eta), integrated with RK4."""
    def flow(h, x0, t):
        n = max(1, int(steps * abs(t)))
        dt = t / n
        y = x0
        for _ in range(n):
            k1 = h(y); k2 = h(y + dt * k1 / 2); k3 = h(y + dt * k2 / 2); k4 = h(y + dt * k3)
            y += dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        return y
    return flow(g, flow(f, x, eps), eta) - flow(f, flow(g, x, eta), eps)


def bracket(f, g, x: float, h: float = 1e-6) -> float:
    """Leading-order prediction f g' - g f' at x (numerical derivatives)."""
    fp = (f(x + h) - f(x - h)) / (2 * h)
    gp = (g(x + h) - g(x - h)) / (2 * h)
    return f(x) * gp - g(x) * fp
