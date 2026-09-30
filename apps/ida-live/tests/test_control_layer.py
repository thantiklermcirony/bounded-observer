import numpy as np
import pytest

from ida_live import knobs
from ida_live.actuators import MuseOptics, SimLED, ExternalLED, normalize, summary
from ida_live.config import load_settings
from ida_live.protocols.recipe import Condition, allocation, validate


class FakeEngine:
    def __init__(self):
        self.settings = load_settings()


def test_condition_language():
    c = Condition("clean and z_alpha_tp < -1.0 and abs(d - 1) <= 0.5")
    assert c({"clean": True, "z_alpha_tp": -1.5, "d": 1.2})
    assert not c({"clean": False, "z_alpha_tp": -1.5, "d": 1.2})
    assert not c({"clean": True, "d": 1.2})  # missing variable -> False, never an error
    assert c.names == ["clean", "d", "z_alpha_tp"]


@pytest.mark.parametrize("bad", ["__import__('os')", "open('x')", "a.b > 1", "[1,2]", "lambda: 1", "x if y else z"])
def test_condition_rejects_code(bad):
    with pytest.raises((ValueError, SyntaxError)):
        Condition(bad)


def test_patterns_normalise():
    b = normalize({"type": "burst", "pulse_hz": 10, "duty": 0.3, "duration_s": 2, "intensity": 0.2})
    assert len(b) == 20 and b[0][0] == pytest.approx(30.0) and b[0][1] == pytest.approx(70.0)
    r = normalize({"type": "ramp", "pulse_hz": 5, "duty": 0.5, "duration_s": 1, "intensity_from": 0.0, "intensity_to": 0.4})
    assert r[0][2] == 0.0 and r[-1][2] == pytest.approx(0.4)
    t = normalize({"type": "train", "repeat": 3, "gap_s": 1.0, "burst": {"type": "burst", "pulse_hz": 10, "duration_s": 1}})
    assert summary(t)["total_s"] == pytest.approx(5.0)


def test_headband_refuses_fast_pulses_but_led_accepts():
    e = FakeEngine()
    fast = {"type": "burst", "pulse_hz": 10, "duty": 0.5, "duration_s": 1}
    with pytest.raises(ValueError, match="cannot switch faster"):
        MuseOptics(e).check(fast)
    assert len(ExternalLED(e).check(fast)) == 10
    assert len(MuseOptics(e).check({"type": "steady", "duration_s": 5})) == 1


def test_limits_enforced():
    e = FakeEngine()
    with pytest.raises(ValueError, match="light on"):
        SimLED(e).check({"type": "steady", "duration_s": 60})
    e.settings["actuators"]["max_intensity"] = 0.3
    with pytest.raises(ValueError, match="intensity"):
        SimLED(e).check({"type": "steady", "duration_s": 1, "intensity": 0.5})


def test_led_sham_has_identical_timing_zero_intensity():
    led = ExternalLED(FakeEngine())
    segs = normalize({"type": "burst", "pulse_hz": 20, "duty": 0.5, "duration_s": 1, "intensity": 0.5})
    real, sham = led._runs(segs, False), led._runs(segs, True)
    assert [r[:3] for r in real] == [r[:3] for r in sham]
    assert all(r[3] == 0 for r in sham) and all(r[3] > 0 for r in real)


def test_recipe_validation_and_allocation():
    with pytest.raises(ValueError):
        validate({"name": "x", "actuator": "sim_led", "pattern": {"type": "steady", "duration_s": 1}, "trigger": {}})
    r = validate({"name": "x", "actuator": "sim_led", "pattern": {"type": "steady", "duration_s": 1},
                  "trigger": {"when": "d > 1"}})
    assert r["randomize"] == 0.5 and r["trigger"]["refractory_s"] == 20.0
    arms = allocation(40, 0.5, np.random.default_rng(0))
    assert arms.count("active") == 20
    assert allocation(5, 1.0, np.random.default_rng(0)) == ["active"] * 5


def test_knobs_every_leaf_is_addressable_and_ranges_hold():
    s = load_settings()
    smap = {"kappa": 0.5, "composition": "mobius_chain", "axes": [{"feature": "beta", "angle_deg": 0, "weight": 1.0, "label": ""}]}
    rows = knobs.describe(s, smap)
    paths = {r["path"] for r in rows}
    assert {"signal.blink_uv", "map.kappa", "map.axes.0.angle_deg", "ir_protocol.burst_s.small", "signal.bands.alpha.0"} <= paths
    old, new = knobs.set_value(s, "signal.blink_uv", "120")
    assert (old, new) == (150.0, 120.0)
    with pytest.raises(ValueError):
        knobs.set_value(s, "signal.blink_uv", 5000)
    with pytest.raises(ValueError):
        knobs.set_value(smap, "composition", "made_up", full="map.composition")
