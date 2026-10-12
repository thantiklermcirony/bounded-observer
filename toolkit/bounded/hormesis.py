"""Three distinct, conditional dose-response laws from the hormesis amendment.

The additive models compose repair and damage in rapidity. The multiplicative
model instead multiplies a fractional benefit by a survival factor. Their
parameters and peak laws are not interchangeable. No model here establishes
that a biological system is hormetic or chooses its parameters.

Sources: ``papers/library-2026-10-12/papers/hormesis_amendment.md``, Theorems 1--4,
and the companion ``paper2.md``, Theorem 6. Methods use floating-point
arithmetic; an unrepresentable analytic dose raises ArithmeticError.
"""

from dataclasses import dataclass
import math
from numbers import Integral, Real

import numpy as np


__all__ = [
    "Peak", "DoseInterval", "AdditiveLinearLogistic", "AdditiveHill",
    "MultiplicativeHill", "series_flux_fold",
]


@dataclass(frozen=True)
class Peak:
    """Maximum on nonnegative doses, including the control boundary."""

    dose: float
    response: float


@dataclass(frozen=True)
class DoseInterval:
    """Open interval whose response is strictly above a specified assay cutoff."""

    lower: float
    upper: float

    @property
    def fold_width(self):
        return self.upper / self.lower


def _parameter(name, value, *, positive=True):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real number")
    if not math.isfinite(value) or (value <= 0 if positive else value < 0):
        qualifier = "positive" if positive else "nonnegative"
        raise ValueError(f"{name} must be finite and {qualifier}")


def _thresholds(activation, toxicity):
    _parameter("activation", activation)
    _parameter("toxicity", toxicity)
    if toxicity <= activation:
        raise ValueError("this theorem requires 0 < activation < toxicity")


def _additive_parameters(p0, repair, harm):
    _parameter("p0", p0)
    if p0 >= 1:
        raise ValueError("p0 must lie strictly between zero and one")
    _parameter("repair", repair)
    _parameter("harm", harm)
    if harm <= repair:
        raise ValueError("this theorem requires harm > repair > 0")


def _dose_array(dose):
    if np.iscomplexobj(dose):
        raise ValueError("dose must be real")
    try:
        values = np.asarray(dose, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("dose must be a finite nonnegative real array") from exc
    if np.any(~np.isfinite(values)) or np.any(values < 0):
        raise ValueError("dose must be finite and nonnegative")
    return values


def _sigmoid(z):
    return np.exp(-np.logaddexp(0.0, -np.asarray(z, dtype=float)))


def _log_sigmoid(z):
    return -float(np.logaddexp(0.0, -z))


def _hill_argument(dose, midpoint, exponent):
    values = _dose_array(dose)
    with np.errstate(divide="ignore", over="ignore"):
        return exponent * (np.log(values) - math.log(midpoint))


def _viability_fold(increment, p0):
    # Equivalent to logistic(logit(p0) + 2*increment)/p0, without overflow.
    return np.exp(-np.logaddexp(math.log(p0), math.log1p(-p0) - 2 * increment))


def _log_difference(log_a, log_b):
    """log(exp(log_a)-exp(log_b)), requiring the difference to be positive."""
    if not log_a > log_b:
        raise ArithmeticError("a required positive difference is unresolved")
    return log_a + math.log(-math.expm1(log_b - log_a))


def _exp_dose(log_dose):
    try:
        dose = math.exp(log_dose)
    except OverflowError as exc:
        raise ArithmeticError("analytic dose exceeds floating-point range") from exc
    if not math.isfinite(dose) or dose <= 0:
        raise ArithmeticError("analytic dose is outside floating-point range")
    return dose


def _quadratic_log_roots(log_b, k, log_c):
    """Log roots of B*x^2-K*x+C=0, avoiding cancellation at the smaller root."""
    if not k > 0:
        raise ArithmeticError("assay roots are unresolved at this precision")
    log_k = math.log(k)
    ratio = math.exp(math.log(4.0) + log_b + log_c - 2 * log_k)
    if ratio >= 1:
        raise ArithmeticError("distinct assay roots are unresolved at this precision")
    log_sum = log_k + math.log1p(math.sqrt(1 - ratio))
    return math.log(2.0) + log_c - log_sum, log_sum - math.log(2.0) - log_b


def _rapidity_cutoff(gain, p0):
    return 0.5 * (math.log1p(gain) + math.log1p(-p0)
                  - math.log(1 - p0 * (1 + gain)))


def _cutoff_available(model, gain):
    _parameter("gain", gain)
    if hasattr(model, "p0") and model.p0 * (1 + gain) >= 1:
        return False
    return model.has_beneficial_interval and gain < model.peak().response - 1


def _interval(lower, upper, peak):
    if not (math.isfinite(lower) and math.isfinite(upper)
            and 0 < lower < peak < upper):
        raise ArithmeticError("ordered assay doses are unresolved at this precision")
    return DoseInterval(lower, upper)


@dataclass(frozen=True)
class AdditiveLinearLogistic:
    """Equal slopes in *linear dose*, with exact zero-dose control.

    Parameters: baseline viability 0 < p0 < 1; harm > repair > 0; positive
    slope; 0 < activation < toxicity. Repair and harm are rapidity amplitudes.
    Different sigmoid slopes are outside this class's single-peak theorem.
    """

    p0: float
    repair: float
    harm: float
    activation: float
    toxicity: float
    slope: float

    def __post_init__(self):
        _additive_parameters(self.p0, self.repair, self.harm)
        _thresholds(self.activation, self.toxicity)
        _parameter("slope", self.slope)
        if not math.isfinite(self.slope * self.toxicity):
            raise ValueError("slope * toxicity must be finite")

    @property
    def has_beneficial_interval(self):
        a, t = self.slope * self.activation, self.slope * self.toxicity
        benefit = math.log(self.repair) + _log_sigmoid(a) + _log_sigmoid(-a)
        damage = math.log(self.harm) + _log_sigmoid(t) + _log_sigmoid(-t)
        return benefit > damage

    def rapidity_increment(self, dose):
        d = _dose_array(dose)
        with np.errstate(over="ignore"):
            a = _sigmoid(self.slope * (d - self.activation))
            t = _sigmoid(self.slope * (d - self.toxicity))
        return (self.repair * (a - _sigmoid(-self.slope * self.activation))
                - self.harm * (t - _sigmoid(-self.slope * self.toxicity)))

    def __call__(self, dose):
        return _viability_fold(self.rapidity_increment(dose), self.p0)

    def peak(self):
        if not self.has_beneficial_interval:
            return Peak(0.0, 1.0)
        a, t = self.slope * self.activation, self.slope * self.toxicity
        log_k = 0.5 * (math.log(self.harm) - math.log(self.repair) + t - a)
        log_x = _log_difference(t, log_k + a) - _log_difference(log_k, 0.0)
        dose = log_x / self.slope
        if not math.isfinite(dose) or dose <= 0:
            raise ArithmeticError("positive peak dose is unresolved at this precision")
        return Peak(dose, float(self(dose)))

    def _log_control_tail(self):
        return _log_difference(
            math.log(self.repair) + _log_sigmoid(-self.slope * self.activation),
            math.log(self.harm) + _log_sigmoid(-self.slope * self.toxicity))

    def return_to_control(self):
        """Positive return dose, or None when there is no beneficial interval."""
        if not self.has_beneficial_interval:
            return None
        log_c = self._log_control_tail()
        log_denominator = float(np.logaddexp(math.log(self.harm - self.repair), log_c))
        dose = (log_c + self.slope * (self.activation + self.toxicity)
                - log_denominator) / self.slope
        if not math.isfinite(dose) or dose <= self.peak().dose:
            raise ArithmeticError("return dose is unresolved at this precision")
        return dose

    def detectable_interval(self, gain):
        """Open interval R > 1+gain; None at or above the peak.

        Gain is a declared assay cutoff, not a statistical significance test.
        """
        if not _cutoff_available(self, gain):
            return None
        z = _rapidity_cutoff(gain, self.p0)
        c = math.exp(self._log_control_tail()) + z
        a, t = self.slope * self.activation, self.slope * self.toxicity
        ratio = math.exp(a - t)
        b = self.harm - self.repair + c
        k = self.repair - self.harm * ratio - c * (1 + ratio)
        # y = exp(slope*dose)/exp(slope*toxicity) avoids huge exponentials.
        low, high = _quadratic_log_roots(math.log(b), k, math.log(c) + a - t)
        return _interval((low + t) / self.slope, (high + t) / self.slope,
                         self.peak().dose)


@dataclass(frozen=True)
class AdditiveHill:
    """Common-exponent Hill occupancies, added as rapidity increments.

    0 < p0 < 1; harm > repair > 0; 0 < activation < toxicity; exponent > 0.
    A beneficial interval exists exactly when repair > harm*(activation/toxicity)^exponent.
    """

    p0: float
    repair: float
    harm: float
    activation: float
    toxicity: float
    exponent: float

    def __post_init__(self):
        _additive_parameters(self.p0, self.repair, self.harm)
        _thresholds(self.activation, self.toxicity)
        _parameter("exponent", self.exponent)
        if not math.isfinite(self._log_epsilon):
            raise ValueError("log threshold separation must be finite")

    @property
    def _log_epsilon(self):
        return self.exponent * (math.log(self.activation) - math.log(self.toxicity))

    @property
    def has_beneficial_interval(self):
        return math.log(self.repair) > math.log(self.harm) + self._log_epsilon

    def rapidity_increment(self, dose):
        return (self.repair * _sigmoid(_hill_argument(dose, self.activation, self.exponent))
                - self.harm * _sigmoid(_hill_argument(dose, self.toxicity, self.exponent)))

    def __call__(self, dose):
        return _viability_fold(self.rapidity_increment(dose), self.p0)

    def peak(self):
        if not self.has_beneficial_interval:
            return Peak(0.0, 1.0)
        p = 0.5 * math.log(self.repair)
        q = 0.5 * (math.log(self.harm) + self._log_epsilon)
        log_u = _log_difference(p, q) - _log_difference(q, self._log_epsilon + p)
        dose = _exp_dose(math.log(self.activation) + log_u / self.exponent)
        return Peak(dose, float(self(dose)))

    def return_to_control(self):
        if not self.has_beneficial_interval:
            return None
        log_u = (_log_difference(math.log(self.repair), math.log(self.harm) + self._log_epsilon)
                 - self._log_epsilon - math.log(self.harm - self.repair))
        return _exp_dose(math.log(self.activation) + log_u / self.exponent)

    def detectable_interval(self, gain):
        """Open interval R > 1+gain, or None when no strict interval exists."""
        if not _cutoff_available(self, gain):
            return None
        z = _rapidity_cutoff(gain, self.p0)
        epsilon = math.exp(self._log_epsilon)
        log_b = self._log_epsilon + math.log(self.harm - self.repair + z)
        k = self.repair - self.harm * epsilon - z * (1 + epsilon)
        low, high = _quadratic_log_roots(log_b, k, math.log(z))
        return _interval(_exp_dose(math.log(self.activation) + low / self.exponent),
                         _exp_dose(math.log(self.activation) + high / self.exponent),
                         self.peak().dose)


@dataclass(frozen=True)
class MultiplicativeHill:
    """(1 + benefit*Hill_activation) * (1 - Hill_toxicity).

    Benefit is a nonnegative fractional functional gain, not a rapidity.
    0 < activation < toxicity and exponent > 0. The zero-dose response is one.
    A beneficial interval exists exactly when benefit > (activation/toxicity)^exponent.
    """

    benefit: float
    activation: float
    toxicity: float
    exponent: float

    def __post_init__(self):
        _parameter("benefit", self.benefit, positive=False)
        _thresholds(self.activation, self.toxicity)
        _parameter("exponent", self.exponent)
        if not math.isfinite(self._log_epsilon):
            raise ValueError("log threshold separation must be finite")

    @property
    def _log_epsilon(self):
        return self.exponent * (math.log(self.activation) - math.log(self.toxicity))

    @property
    def has_beneficial_interval(self):
        return self.benefit > 0 and math.log(self.benefit) > self._log_epsilon

    def __call__(self, dose):
        activation = _sigmoid(_hill_argument(dose, self.activation, self.exponent))
        survival = _sigmoid(-_hill_argument(dose, self.toxicity, self.exponent))
        return (1 + self.benefit * activation) * survival

    def peak(self):
        if not self.has_beneficial_interval:
            return Peak(0.0, 1.0)
        epsilon = math.exp(self._log_epsilon)
        log_numerator = _log_difference(math.log(self.benefit), self._log_epsilon)
        log_sqrt = 0.5 * (self._log_epsilon + math.log(self.benefit)
                          + math.log(1 + self.benefit - epsilon))
        log_u = log_numerator - float(np.logaddexp(self._log_epsilon, log_sqrt))
        dose = _exp_dose(math.log(self.activation) + log_u / self.exponent)
        return Peak(dose, float(self(dose)))

    def return_to_control(self):
        if not self.has_beneficial_interval:
            return None
        log_u = _log_difference(math.log(self.benefit), self._log_epsilon) - self._log_epsilon
        return _exp_dose(math.log(self.activation) + log_u / self.exponent)

    def detectable_interval(self, gain):
        if not _cutoff_available(self, gain):
            return None
        epsilon = math.exp(self._log_epsilon)
        k = self.benefit - epsilon - gain * (1 + epsilon)
        low, high = _quadratic_log_roots(self._log_epsilon + math.log1p(gain), k, math.log(gain))
        return _interval(_exp_dose(math.log(self.activation) + low / self.exponent),
                         _exp_dose(math.log(self.activation) + high / self.exponent),
                         self.peak().dose)


def series_flux_fold(steps, molecular_gain):
    """Exact finite fold for changing one rate in an equal-resistance series chain.

    The model has ``steps`` equal positive baseline rates and a fixed driving
    drop; one rate is multiplied by 1+molecular_gain. steps is a positive
    integer and molecular_gain is finite and nonnegative. This is not inferred
    from the local metabolic-control summation theorem alone.
    """
    if isinstance(steps, bool) or not isinstance(steps, Integral) or steps < 1:
        raise ValueError("steps must be a positive integer")
    _parameter("molecular_gain", molecular_gain, positive=False)
    return steps / (steps - 1 + 1 / (1 + molecular_gain))
