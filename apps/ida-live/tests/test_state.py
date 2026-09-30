import numpy as np
import pytest

from ida_live.config import load_settings
from ida_live.state import Axis, ReferenceBuilder, StateEngine, StateMap


def smap():
    return StateMap("t", [Axis("a", 90), Axis("b", 0)], kappa=0.5)


def test_reference_needs_clean_data():
    b = ReferenceBuilder(["a", "b"], 0.4)
    for i in range(100):
        b.add({"a": 1.0, "b": 2.0}, clean=(i % 10 == 0))
    with pytest.raises(ValueError):
        b.freeze()


def test_reference_freezes_median_and_scale():
    rng = np.random.default_rng(0)
    b = ReferenceBuilder(["a", "b"], 0.4)
    for _ in range(200):
        b.add({"a": rng.normal(1, 0.1), "b": rng.normal(-2, 0.3)}, clean=True)
    ref = b.freeze()
    assert ref.median["a"] == pytest.approx(1.0, abs=0.05)
    assert ref.scale["b"] == pytest.approx(0.3, rel=0.25)
    assert len(ref.ref_id) == 12


def test_engine_holds_point_during_artifacts_and_tracks_return():
    s = load_settings()
    b = ReferenceBuilder(["a", "b"], 0.4)
    for _ in range(50):
        b.add({"a": 0.0, "b": 0.0}, clean=True)
        b.add({"a": 0.1, "b": 0.1}, clean=True)
    eng = StateEngine(smap(), b.freeze(), s)
    good = {"quality": ["good"] * 4}
    t = 0.0
    for _ in range(40):
        t += 0.25
        st = eng.update(t, {"a": 3.0, "b": 0.05}, good)
    assert st["clean"] and st["d"] > 0.5 and st["y"] > 0
    held = eng.update(t + 0.25, {"a": 0.0, "b": 0.0}, {"quality": ["good"] * 4, "blink": True})
    assert not held["clean"] and held["x"] == st["x"]
    eng.returns.mark(t, "probe")
    for _ in range(80):
        t += 0.25
        eng.update(t, {"a": 0.05, "b": 0.05}, good)
    assert eng.returns.last and eng.returns.last["kind"] == "probe"
