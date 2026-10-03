"""Checks for the signal quality, calibration guard, IDA/MRE measures and the control folder."""
import asyncio, json, os, sys, tempfile, time
from pathlib import Path

import numpy as np

os.environ.setdefault("IDA_LIVE_DATA", tempfile.mkdtemp())
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ida_live.config import load_settings  # noqa: E402
from ida_live.core import Buffers, Chunk  # noqa: E402
from ida_live.features import build_all, _lz76  # noqa: E402
from ida_live.state import ReferenceBuilder  # noqa: E402

FS = 256


def eeg(kind, seconds=4, seed=0):
    rng = np.random.default_rng(seed)
    n = int(seconds * FS)
    t = np.arange(n) / FS
    # pink-ish background: integrate white noise, then add alpha
    x = np.cumsum(rng.normal(0, 1, (n, 4)), axis=0)
    x -= np.linspace(x[0], x[-1], n)
    x = x / x.std() * 12 + 8 * np.sin(2 * np.pi * 10 * t)[:, None]
    if kind == "muscle":
        x += rng.normal(0, 40, (n, 4))
    if kind == "white":
        x = rng.normal(0, 20, (n, 4))
    return t, x + 800.0


def features(kind):
    s = load_settings()
    t, x = eeg(kind)
    b = Buffers(60)
    b.push(Chunk("EEG", t, x, ["TP9", "AF7", "AF8", "TP10"], FS))
    vals, flags = {}, {}
    for f in build_all(s):
        v, fl = f.compute(b, t[-1])
        vals.update(v)
        flags.update(fl)
    return vals, flags


def test_good_signal_is_good():
    v, f = features("good")
    assert f["quality"].count("good") >= 3, f
    assert v["readiness"] > 0.8
    assert 0 < v["lzc"] < 1.2 and v["phi"] > 0 and -1 < v["alt"] < 1


def test_muscle_bursts_are_caught_and_steady_floor_is_not():
    s = load_settings()
    feats = build_all(s)
    t, x = eeg("good", seconds=40, seed=3)
    x[:, [0, 3]] += np.random.default_rng(4).normal(0, 15, (len(t), 2))  # steady noisy ear floor
    burst = (t > 36) & (t < 40)
    x[burst, 0] += np.random.default_rng(5).normal(0, 90, burst.sum())    # a jaw burst on TP9
    qual = {}
    for k in range(512, len(t), 64):
        b = Buffers(60)
        b.push(Chunk("EEG", t[:k], x[:k], ["TP9", "AF7", "AF8", "TP10"], FS))
        vals, fl = {}, {}
        for f in feats:
            v, g = f.compute(b, t[k - 1])
            vals.update(v)
            fl.update(g)
        qual[round(t[k - 1], 2)] = fl["quality"]
    quiet = [q for tt, q in qual.items() if 12 < tt < 34]
    assert all(q[0] != "muscle" and q[3] != "muscle" for q in quiet), quiet[:5]
    assert any(q[0] == "muscle" for tt, q in qual.items() if tt > 37)


def test_noise_is_caught():
    s = load_settings()
    feats = build_all(s)
    t, x = eeg("white", seconds=24)
    labels, ready = [], []
    for k in range(512, len(t), 64):
        b = Buffers(60)
        b.push(Chunk("EEG", t[:k], x[:k], ["TP9", "AF7", "AF8", "TP10"], FS))
        vals, fl = {}, {}
        for f in feats:
            v, g = f.compute(b, t[k - 1])
            vals.update(v)
            fl.update(g)
        labels += fl["quality"]
        ready.append(vals["readiness"])
    assert labels.count("good") / len(labels) < 0.3, labels.count("good") / len(labels)
    assert np.mean(ready) < 0.5


def test_calibration_refuses_noise():
    b = ReferenceBuilder(["brain_slope", "alpha_tp"], 0.4)
    for _ in range(100):
        b.add({"brain_slope": 0.05, "alpha_tp": 1.0}, True)
    try:
        b.freeze()
    except ValueError as e:
        assert "noise" in str(e)
    else:
        raise AssertionError("noise calibration was accepted")


def test_lz76_known_values():
    assert _lz76(np.array([0, 0, 0, 0, 0, 0])) == 2
    assert _lz76(np.array([0, 1, 0, 1, 0, 1, 0, 1])) == 3
    rnd = np.random.default_rng(1).integers(0, 2, 4096)
    c = _lz76(rnd)
    assert 0.85 < c * np.log2(4096) / 4096 < 1.15


def test_control_folder_roundtrip(tmp_path, monkeypatch):
    from ida_live.engine import Engine
    from ida_live.control import ControlBridge
    # keep the control folder out of the working tree
    monkeypatch.setattr("ida_live.control.DATA_DIR", tmp_path)

    async def run():
        e = Engine(load_settings())
        br = ControlBridge(e)
        (br.inbox / "t1.json").write_text(json.dumps(
            [{"cmd": "set", "values": {"display.lens": "tunnel", "display.speed": 0.5}},
             {"cmd": "set", "values": {"reference.calibration_s": 5}},
             {"cmd": "help"}]))
        await br._process(br.inbox / "t1.json")
        out = json.loads((br.outbox / "t1.json").read_text())["results"]
        assert out[0]["ok"] and e.settings["display"]["lens"] == "tunnel"
        assert not out[1]["ok"] and "between" in out[1]["error"]
        assert "live.json" in out[2]["help"]
        assert (br.root / "live.json").exists()

    asyncio.run(run())


def test_breath_rate_and_pacer_lock():
    """Head rocking at 6 breaths a minute, locked to the pacer, reads as 6 bpm and high sync;
    the same rocking at 9 per minute does not lock."""
    from ida_live.features import Breath
    s = load_settings()
    s["audio"]["pacer_bpm"] = 6.0
    rate = 52.0
    for bpm, want_sync in ((6.0, True), (9.0, False)):
        b = Buffers(seconds=60.0)
        t = 1000.0 + np.arange(int(50 * rate)) / rate
        rng = np.random.default_rng(1)
        rock = np.sin(2 * np.pi * bpm / 60 * t)
        x = np.column_stack([0.01 * rock, 0.005 * rock, np.zeros_like(t), 0.8 * rock, 0.3 * rock, 0.1 * rock])
        x += rng.normal(scale=0.05, size=x.shape) * [0.001, 0.001, 0.001, 0.1, 0.1, 0.1]
        b.push(Chunk("ACCGYRO", t, x, ["ACC_X", "ACC_Y", "ACC_Z", "GYRO_X", "GYRO_Y", "GYRO_Z"], rate))
        vals, _ = Breath(s).compute(b, t[-1])
        assert abs(vals["breath_bpm"] - bpm) < 1.0, vals
        assert vals["breath_conf"] > 0.5, vals
        assert (vals["breath_sync"] > 0.8) == want_sync, vals


def test_attention_heldout_test_is_fair_under_null():
    """With no real difference between states, the held-out AUC centres on 0.5 and the gate
    (with its block permutation) rarely passes."""
    from ida_live.analysis.attention import _cv, _perm_p
    rng = np.random.default_rng(11)
    aucs, passes = [], 0
    for _ in range(12):
        blocks = np.repeat(np.arange(8), 40)
        y = (blocks % 2 == 0).astype(float)
        X = rng.normal(size=(320, 6)) + rng.normal(size=(8, 6))[blocks] * 0.5
        r = _cv(X, y, blocks, boot=False)
        aucs.append(r["auc"])
        passes += r["auc"] >= 0.6 and _perm_p(X, y, blocks, r["auc"], max_perm=35) < 0.05
    assert abs(np.mean(aucs) - 0.5) < 0.1
    assert passes <= 2
