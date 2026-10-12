"""Independent response tests for the three explicitly different hormesis laws."""

from dataclasses import replace
import math

import numpy as np
import pytest
from scipy.optimize import brentq, minimize_scalar
from scipy.special import expit

from bounded.hormesis import (
    AdditiveHill, AdditiveLinearLogistic, MultiplicativeHill, series_flux_fold,
)


HORMETIC = [
    AdditiveLinearLogistic(.2, 1, 2, 1, 5, 1),
    AdditiveLinearLogistic(.7, .6, 1.5, 2, 8, .7),
    AdditiveHill(.3, .6, 1.5, 1, 10, 2),
    AdditiveHill(.8, .5, 1, 2, 9, .8),
    MultiplicativeHill(.5, 1, 5, 2),
    MultiplicativeHill(2, 2, 7, .7),
]


def independent_response(model, dose):
    """Direct definitions, without implementation's peak or root expressions."""
    if isinstance(model, AdditiveLinearLogistic):
        repair = expit(model.slope * (dose - model.activation))
        damage = expit(model.slope * (dose - model.toxicity))
        repair0 = expit(-model.slope * model.activation)
        damage0 = expit(-model.slope * model.toxicity)
        increment = model.repair * (repair - repair0) - model.harm * (damage - damage0)
    else:
        x = np.asarray(dose) ** model.exponent
        repair = x / (x + model.activation ** model.exponent)
        damage = x / (x + model.toxicity ** model.exponent)
        if isinstance(model, MultiplicativeHill):
            return (1 + model.benefit * repair) * (1 - damage)
        increment = model.repair * repair - model.harm * damage
    baseline_logit = math.log(model.p0 / (1 - model.p0))
    return expit(baseline_logit + 2 * increment) / model.p0


@pytest.mark.parametrize("model", HORMETIC)
def test_response_has_exact_control_and_matches_direct_definition(model):
    grid = np.r_[0, np.geomspace(.001, 1000, 200)]
    assert float(model(0)) == pytest.approx(1, abs=2e-15)
    assert np.allclose(model(grid), independent_response(model, grid), atol=2e-14, rtol=2e-13)
    if not isinstance(model, MultiplicativeHill):
        assert np.all(model(grid) < 1 / model.p0)


@pytest.mark.parametrize("model", HORMETIC)
def test_analytic_peak_against_optimizer_and_direct_derivative(model):
    peak = model.peak()
    return_dose = model.return_to_control()
    assert model.has_beneficial_interval
    assert 0 < peak.dose < return_dose
    found = minimize_scalar(lambda d: -float(independent_response(model, d)),
                            bounds=(0, return_dose), method="bounded",
                            options={"xatol": 1e-11})
    assert found.success
    assert found.x == pytest.approx(peak.dose, rel=3e-7, abs=2e-7)
    assert -found.fun == pytest.approx(peak.response, abs=2e-13)
    step = peak.dose * 1e-4
    left = float(independent_response(model, peak.dose - step))
    right = float(independent_response(model, peak.dose + step))
    derivative = (right - left) / (2 * step)
    assert abs(derivative) < 3e-8
    assert left < peak.response and right < peak.response
    numerical_return = brentq(lambda d: float(independent_response(model, d)) - 1,
                             peak.dose, return_dose * 2, xtol=1e-11)
    assert numerical_return == pytest.approx(return_dose, rel=2e-10, abs=1e-10)
    assert float(model(return_dose * .95)) > 1
    assert float(model(return_dose * 1.05)) < 1


@pytest.mark.parametrize("model", HORMETIC)
def test_both_assay_crossings_match_numerical_roots(model):
    peak = model.peak()
    gain = (peak.response - 1) / 4
    interval = model.detectable_interval(gain)
    target = 1 + gain
    lower = brentq(lambda d: float(independent_response(model, d)) - target,
                   0, peak.dose, xtol=1e-12)
    upper = brentq(lambda d: float(independent_response(model, d)) - target,
                   peak.dose, model.return_to_control(), xtol=1e-12)
    assert interval.lower == pytest.approx(lower, rel=3e-10, abs=1e-10)
    assert interval.upper == pytest.approx(upper, rel=3e-10, abs=1e-10)
    assert 0 < interval.lower < peak.dose < interval.upper < model.return_to_control()
    assert float(model(interval.lower * .9)) < target
    assert float(model(interval.upper * 1.1)) < target
    assert float(model(math.sqrt(interval.lower * interval.upper))) > target
    assert interval.fold_width == pytest.approx(upper / lower, rel=3e-10)
    assert model.detectable_interval(peak.response - 1) is None
    assert model.detectable_interval(peak.response) is None


@pytest.mark.parametrize("model", HORMETIC)
def test_dose_unit_changes_preserve_response_and_scale_all_edges(model):
    factor = 1000.0
    parameters = dict(activation=model.activation * factor, toxicity=model.toxicity * factor)
    if isinstance(model, AdditiveLinearLogistic):
        parameters["slope"] = model.slope / factor
    scaled = replace(model, **parameters)
    assert scaled.has_beneficial_interval == model.has_beneficial_interval
    grid = np.r_[0, np.geomspace(.001, 100, 70)]
    assert np.allclose(scaled(grid * factor), model(grid), rtol=2e-13, atol=2e-14)
    assert scaled.peak().dose == pytest.approx(model.peak().dose * factor, rel=1e-12)
    assert scaled.peak().response == pytest.approx(model.peak().response, abs=2e-14)
    assert scaled.return_to_control() == pytest.approx(model.return_to_control() * factor, rel=1e-12)
    gain = (model.peak().response - 1) / 4
    original, changed = model.detectable_interval(gain), scaled.detectable_interval(gain)
    assert changed.lower == pytest.approx(original.lower * factor, rel=3e-12)
    assert changed.upper == pytest.approx(original.upper * factor, rel=3e-12)
    assert changed.fold_width == pytest.approx(original.fold_width, rel=3e-12)


@pytest.mark.parametrize("model", [
    # Published threshold/high-dose conditions alone do not imply hormesis.
    AdditiveLinearLogistic(.5, .3, 1, 4, 5, 1),
    AdditiveHill(.5, .1, 1, 1, 2, 1),
    AdditiveHill(.5, .5, 1, 1, 2, 1),
    MultiplicativeHill(0, 1, 2, 1),
    MultiplicativeHill(.4, 1, 2, 1),
    MultiplicativeHill(.5, 1, 2, 1),
])
def test_absence_and_onset_boundary_give_no_beneficial_or_detectable_interval(model):
    grid = np.r_[0, np.geomspace(1e-5, 1e5, 500)]
    assert not model.has_beneficial_interval
    assert np.all(model(grid) <= 1 + 2e-15)
    assert model.peak().dose == 0 and model.peak().response == 1
    assert model.return_to_control() is None
    assert model.detectable_interval(.01) is None


def test_baseline_changes_amplitude_but_not_peak_or_return_location():
    for model in (HORMETIC[0], HORMETIC[2]):
        low, high = replace(model, p0=.1), replace(model, p0=.9)
        assert low.peak().dose == high.peak().dose
        assert low.return_to_control() == high.return_to_control()
        assert low.peak().response > high.peak().response > 1
        assert low(0) == pytest.approx(1) and high(0) == pytest.approx(1)
        assert high.detectable_interval(1 / high.p0 - 1) is None


def test_additive_and_product_amplitudes_and_peaks_are_not_interchangeable():
    additive = AdditiveHill(.5, .5, 1, 1, 5, 2)
    product = MultiplicativeHill(.5, 1, 5, 2)
    assert abs(additive.peak().dose - product.peak().dose) > .2
    assert additive.peak().response != pytest.approx(product.peak().response, rel=.001)
    assert abs(additive.peak().dose - 2 * additive.activation) > .1


def test_source_counterexample_product_shortcut_is_not_generally_conservative():
    # Amendment section 2.2: calibrate each curve to its ACTUAL control.
    activation, toxicity = 4.0, 4.0 + math.log(49)
    actual_control_rapidity = expit(-activation) - 20 * expit(-toxicity)
    actual_p0 = expit(2 * actual_control_rapidity)
    exact = AdditiveLinearLogistic(actual_p0, 1, 20, activation, toxicity, 1)
    amplitude = math.tanh(1)

    def product_logistic(dose):
        return ((1 + amplitude * expit(dose - activation))
                * expit(toxicity - dose))

    shortcut = product_logistic(activation) / product_logistic(0)
    assert float(exact(activation)) == pytest.approx(1.0882272, abs=5e-6)
    assert shortcut == pytest.approx(1.3353909, abs=5e-6)
    assert 1 < exact(activation) < shortcut


def test_log_domain_extreme_thresholds_keep_finite_doses_and_control():
    # Direct powers/exponentials overflow here; the analytic doses still exist.
    hill = AdditiveHill(.3, .6, 1.5, 1e-100, 1e100, 2)
    product = MultiplicativeHill(.5, 1e-100, 1e100, 2)
    linear = AdditiveLinearLogistic(.3, 1, 2, 4, 1000, 1)
    for model in (hill, product, linear):
        assert model.has_beneficial_interval
        peak = model.peak()
        assert math.isfinite(peak.dose) and peak.dose > 0
        assert math.isfinite(model.return_to_control())
        assert float(model(0)) == pytest.approx(1, abs=2e-15)
        interval = model.detectable_interval((peak.response - 1) / 2)
        assert 0 < interval.lower < peak.dose < interval.upper
        assert float(model(interval.lower)) == pytest.approx(1 + (peak.response - 1) / 2, rel=1e-12)
        assert float(model(interval.upper)) == pytest.approx(1 + (peak.response - 1) / 2, rel=1e-12)


def network_flux(conductances):
    """Solve internal node voltages for a chain between fixed voltages one/zero."""
    n = len(conductances)
    if n == 1:
        return conductances[0]
    matrix = np.zeros((n - 1, n - 1))
    forcing = np.zeros(n - 1)
    for j in range(n - 1):
        matrix[j, j] = conductances[j] + conductances[j + 1]
        if j > 0:
            matrix[j, j - 1] = -conductances[j]
        if j < n - 2:
            matrix[j, j + 1] = -conductances[j + 1]
    forcing[0] = conductances[0]
    voltages = np.linalg.solve(matrix, forcing)
    return conductances[0] * (1 - voltages[0])


@pytest.mark.parametrize("steps", [1, 2, 3, 6])
@pytest.mark.parametrize("gain", [0, .001, 1, 1.5, 100])
def test_finite_series_fold_against_independent_network_solution(steps, gain):
    initial = np.full(steps, 2.3)
    changed = initial.copy()
    changed[steps // 2] *= 1 + gain
    actual = network_flux(changed) / network_flux(initial)
    assert series_flux_fold(steps, gain) == pytest.approx(actual, rel=1e-12)


def test_local_control_does_not_fix_finite_flux_fold():
    steps, gain = 3, 1
    assert series_flux_fold(steps, gain) == pytest.approx(1.2)
    assert series_flux_fold(steps, gain) != pytest.approx(1 + gain / steps)
    # This homogeneous alternative has the same local coefficients 1/n.
    geometric_fold = (1 + gain) ** (1 / steps)
    assert geometric_fold != pytest.approx(series_flux_fold(steps, gain))
    infinitesimal = 1e-5
    assert (series_flux_fold(steps, infinitesimal) - 1) / infinitesimal == pytest.approx(1 / steps, rel=1e-5)


@pytest.mark.parametrize("dose", [-1, [0, -1], np.nan, np.inf, [0, np.nan], 1 + 2j])
@pytest.mark.parametrize("model", [HORMETIC[0], HORMETIC[2], HORMETIC[4]])
def test_invalid_doses_are_rejected(dose, model):
    with pytest.raises(ValueError):
        model(dose)


@pytest.mark.parametrize("model", [HORMETIC[0], HORMETIC[2], HORMETIC[4]])
@pytest.mark.parametrize("cutoff", [0, -.1, np.nan, np.inf, True])
def test_invalid_assay_cutoffs_are_rejected(model, cutoff):
    with pytest.raises(ValueError):
        model.detectable_interval(cutoff)


@pytest.mark.parametrize("parameters", [
    {"p0": 0}, {"p0": 1}, {"p0": np.nan}, {"repair": 0}, {"harm": 1},
    {"activation": 0}, {"toxicity": 1}, {"slope": 0}, {"slope": np.inf},
])
def test_invalid_linear_model_parameters_are_rejected(parameters):
    with pytest.raises(ValueError):
        replace(HORMETIC[0], **parameters)


@pytest.mark.parametrize("parameters", [
    {"p0": 1}, {"repair": -1}, {"harm": .6}, {"activation": 0},
    {"toxicity": 1}, {"exponent": 0}, {"exponent": np.inf},
])
def test_invalid_additive_hill_parameters_are_rejected(parameters):
    with pytest.raises(ValueError):
        replace(HORMETIC[2], **parameters)


@pytest.mark.parametrize("parameters", [
    {"benefit": -1}, {"benefit": np.nan}, {"activation": 0},
    {"toxicity": 1}, {"exponent": 0}, {"exponent": np.inf},
])
def test_invalid_product_model_parameters_are_rejected(parameters):
    with pytest.raises(ValueError):
        replace(HORMETIC[4], **parameters)


@pytest.mark.parametrize("steps,gain", [(0, 1), (2.0, 1), (True, 1), (2, -1), (2, np.inf)])
def test_invalid_series_model_parameters_are_rejected(steps, gain):
    with pytest.raises(ValueError):
        series_flux_fold(steps, gain)
