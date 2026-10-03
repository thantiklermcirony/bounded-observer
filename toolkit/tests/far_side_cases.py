"""Generate site/far_side_cases.json: expected far-side rapidities from an independent oracle.

The oracle is r(x) = (1/2) Log((1 + x) / (1 - x)) with Python's principal complex logarithm,
which does not share code with toolkit/bounded/law.py or site/bo.js. Both implementations are
tested against this file (toolkit/tests/test_theorems.py and site/bo.test.mjs), so the
Python and browser maths cannot drift apart unnoticed.

    python toolkit/tests/far_side_cases.py      # rewrites site/far_side_cases.json
"""
import cmath
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "site" / "far_side_cases.json"

POINTS = [-1e6, -50.0, -5.0, -3.0, -1.25, -1.0001, -0.999, -0.5, 0.0, 0.3, 0.999,
          1.0001, 1.25, 2.0, 3.0, 5.0, 50.0, 1e6]
INSIDE_OUTSIDE = [(-3.0, 0.5), (3.0, -0.5), (-1.25, 0.9), (2.0, 0.5), (-0.9, 3.0), (10.0, -0.95)]
OUTSIDE_OUTSIDE = [(2.0, 2.0), (-3.0, 1.25), (7.0, -9.0), (-1.5, -4.0)]


def oracle(x: float) -> complex:
    return 0.5 * cmath.log((1 + x) / (1 - x))


def einstein(a: float, b: float) -> float:
    return (a + b) / (1 + a * b)


def cases() -> dict:
    pt = [{"x": x, "re": oracle(x).real, "im": oracle(x).imag} for x in POINTS]
    io = [{"x": x, "a": a, "y": einstein(x, a)} for x, a in INSIDE_OUTSIDE]
    oo = [{"x": x, "y": y, "z": einstein(x, y)} for x, y in OUTSIDE_OUTSIDE]
    return {
        "convention": "r(x) = (1/2) Log((1+x)/(1-x)), principal Log of the ratio; |x| != 1",
        "points": pt,
        "inside_outside": io,
        "inside_outside_rule": "r(y) = r(x) + r(a) exactly",
        "outside_outside": oo,
        "outside_outside_rule": "r(x) + r(y) = r(z) + i*pi (equality modulo i*pi only)",
    }


if __name__ == "__main__":
    OUT.write_text(json.dumps(cases(), indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
