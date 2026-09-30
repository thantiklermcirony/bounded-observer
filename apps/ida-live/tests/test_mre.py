"""The MRE pipeline: Φ by CTW, the Butterworth filter, the bit logger and the paper's analysis."""
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from mre_sim import simulate  # noqa: E402

from ida_live.analysis import mre  # noqa: E402
from ida_live.dsp import butter_bandpass_sos, sosfilt  # noqa: E402
from ida_live.mre.ctw import ctw_symbols, quantise  # noqa: E402
from ida_live.mre.qrng import BitLogger, ShamSource  # noqa: E402


def test_ctw_entropy_is_sane():
    rng = np.random.default_rng(0)
    u = ctw_symbols(rng.integers(0, 256, 512)) / 512          # uniform bytes: ~8 bits/sample
    g = ctw_symbols(quantise(rng.normal(size=512))) / 512      # Gaussian at 8 bits: less
    w = ctw_symbols(quantise(np.cumsum(rng.normal(size=512)))) / 512   # random walk: far less
    assert 7.6 < u < 8.3 and g < u and w < g


def test_butterworth_passes_the_band_and_stops_outside():
    sos = butter_bandpass_sos(1.0, 40.0, 256.0, 4)
    t = np.arange(0, 20, 1 / 256)
    amp = lambda f: np.abs(sosfilt(sos, np.sin(2 * np.pi * f * t))[-1024:]).max()
    assert amp(10) > 0.95 and amp(0.2) < 0.05 and amp(90) < 0.05


def test_permutation_distribution_matches_brute_force():
    rng = np.random.default_rng(1)
    R, F = rng.normal(size=40), rng.normal(size=40)
    T = mre.perm_distribution(R, F)
    bf = [sum(R[j] * F[(j + l) % 40] for j in range(40)) for l in range(40)]
    assert np.allclose(T, bf)


def test_null_is_not_claimed_and_real_effect_is_found(tmp_path):
    simulate(tmp_path / "null", c1_bins=30000, sessions=6, session_bins=10000, kappa=0.0, seed=7)
    a = mre.analyse(tmp_path / "null", 500)["arms"]["main"][0]
    assert not a["glm"]["claim"] and a["verdicts"]["F2"][0] == "passes"
    assert abs(a["C1"]["alpha0"] - 0.1) < 0.005                # one bit per 100 ms bin
    simulate(tmp_path / "eff", c1_bins=30000, sessions=6, session_bins=10000, kappa=4e-4, seed=8)
    b = mre.analyse(tmp_path / "eff", 500)["arms"]["main"][0]
    g = b["glm"]
    assert g["claim"] and g["kappa_ci99"][0] < 4e-4 < g["kappa_ci99"][1]


def test_bit_logger_writes_fixed_bins(tmp_path):
    ctx = lambda: {"connected": False, "eeg": False, "session": "", "phi": None, "clean": False}
    lg = BitLogger(tmp_path, ShamSource(3), ctx, lambda s: None, "main")
    lg.start()
    time.sleep(1.5)
    lg.stop()
    rows = (tmp_path / next(p.name for p in tmp_path.glob("bits_main_*.csv"))).read_text().splitlines()
    assert rows[0].startswith("wall,cond") and len(rows) >= 10
    cells = rows[1].split(",")
    assert cells[1] == "1" and cells[6] == "160" and cells[8] == "160"   # C1, 160 bits per stream


def test_booth_sees_a_planted_signal_and_not_noise_or_muscle(tmp_path):
    from booth_sim import booth_session
    from ida_live.analysis import booth
    for name, (b, o, want) in {"win": (0.8, 0.0, "window"), "body": (0.0, 1.0, "body"), "null": (0.0, 0.0, "nothing")}.items():
        root = tmp_path / name
        booth_session(root, "2026-09-26_100000_booth", minutes=12, brain=b, body=o, seed=21)
        booth_session(root, "2026-09-27_100000_booth", minutes=12, brain=b, body=o, seed=22)
        got = booth.analyse(root)["levers"]["flow"]["verdict"]
        assert got == want, (name, got)


def test_carry_falls_are_timed_from_the_brain(tmp_path):
    import numpy as np
    from ida_live.analysis.common import Table
    from ida_live.analysis.levels import carry_falls, carry_test
    rows = ["t,Fe,event"]
    for i in range(1200):
        t = i / 4
        dipped = (60 < t < 64) or (150 < t < 170)
        ev = "dip:carry" if abs(t - 61) < 0.13 else "dip:follow" if abs(t - 151) < 0.13 else ""
        rows.append(f"{t},{0.1 if dipped else 0.8},{ev}")
    (tmp_path / "level.csv").write_text("\n".join(rows))
    falls = carry_falls(Table(tmp_path / "level.csv"))
    assert [f["arm"] for f in falls] == ["carry", "follow"]
    assert falls[0]["back_s"] < falls[1]["back_s"] and 2 < falls[0]["back_s"] < 8 and 18 < falls[1]["back_s"] < 25
    assert carry_test(falls)["p"] is None          # too few falls to test


def test_search_finds_a_planted_sweet_spot_and_not_noise(tmp_path):
    from search_sim import search_session
    from ida_live.analysis import search
    for truth in ("coherence", None):
        root = tmp_path / str(truth)
        for i in range(6):
            search_session(root, f"2026-09-{10 + i}_120000_level-still", truth=truth, seed=10 + i)
        p = search.analyse(root)
        if truth:
            assert p["top"] == "coherence" and "coherence" in p["targets"] and abs(p["targets"]["coherence"] - 0.5) < 0.3
        else:
            assert p["status"] in ("no shape stands out yet", "a leader, not yet established") and p["status"] != "found (provisional)"
