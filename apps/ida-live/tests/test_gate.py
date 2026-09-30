import numpy as np

from ida_live.analysis import gate


def rows(informative, n_sessions=4, per=30, seed=0):
    rng = np.random.default_rng(seed)
    out = []
    for s in range(n_sessions):
        for i in range(per):
            y = float(rng.random() < 0.5)
            shift = 0.8 * (1 if y else -1) if informative else 0.0
            out.append({"session": f"s{s}", "y": y, "minutes": i * 1.2,
                        "alpha_theta": rng.normal(0, 1), "x": rng.normal(0, 0.3),
                        "y_": rng.normal(shift * 0.3, 0.3), "d": abs(rng.normal(1 + shift * 0.3, 0.4)),
                        "euc_x": rng.normal(0, 0.3), "euc_y": rng.normal(0, 0.3), "euc_d": abs(rng.normal(1, 0.4))})
    return out


def test_informative_map_beats_baselines():
    res = gate.evaluate(rows(True))
    assert res["M2 map"] > 0.7
    assert res["M2 map"] > res["M1 index"] + gate.MARGIN


def test_null_map_does_not_pass():
    res = gate.evaluate(rows(False, seed=5))
    assert res["M2 map"] < gate.MIN_AUC
