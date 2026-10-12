"""Independent Doc32 hormesis checks; Python standard library only.

Run: python hormesis_doc32_supplemental_checks.py
Optional: --output report.json
No author manuscript, source data or existing check file is read or modified.
The proofs in coordination/doc32_hormesis_review.md establish the general scope.
"""
import argparse
from fractions import Fraction
import json
import math
from pathlib import Path


def logistic(z):
    if z >= 0:
        e = math.exp(-z)
        return 1.0 / (1.0 + e)
    e = math.exp(z)
    return e / (1.0 + e)


def viability(r):
    return logistic(2.0 * r)


def bisect_root(fn, lo, hi):
    fl, fh = fn(lo), fn(hi)
    assert fl * fh <= 0, (lo, hi, fl, fh)
    for _ in range(100):
        mid = (lo + hi) / 2
        fm = fn(mid)
        if fm == 0:
            return mid
        if fl * fm <= 0:
            hi = mid
        else:
            lo, fl = mid, fm
    return (lo + hi) / 2


def common_logistic_product_peak(Da, Dt, A, slope):
    """Closed stationary root, evaluated in logs to avoid flat-plateau argmax."""
    L = slope * (Dt - Da)
    temp = math.log1p(A) + L
    log_sqrt = 0.5 * (math.log(A) + temp + math.log1p(-math.exp(-temp)))
    if log_sqrt <= 0:
        return 0.0
    log_y = log_sqrt + math.log1p(-math.exp(-log_sqrt)) - math.log1p(A)
    dose = max(0.0, Da + log_y / slope)
    if dose > 0:
        # Divide the derivative numerator by a^2 exp(L), avoiding exp(L).
        residual = (-(1 + A) * math.exp(2 * log_y - L)
                    - 2 * math.exp(log_y - L) + A - math.exp(-L))
        assert abs(residual) < 1e-12, residual
    return dose


def relative_protocol_case(ratio, A, k=4.0):
    """Da=1; sa=k/Da and st=k/Dt. All derivative evaluations are stable."""
    def response(d):
        u = logistic(k * (d - 1))
        vc = logistic(-k * (d / ratio - 1))
        return (1 + A * u) * vc

    def log_derivative(d):
        za, zt = k * (d - 1), k * (d / ratio - 1)
        u, uc, v = logistic(za), logistic(-za), logistic(zt)
        return A * k * u * uc / (1 + A * u) - k * v / ratio

    assert log_derivative(0) > 0
    assert log_derivative(1) > 0
    peak = bisect_root(log_derivative, 1, ratio)
    peak_value = response(peak)
    assert peak_value > 1
    lower = bisect_root(lambda d: response(d) - 1, 0, peak)
    upper = bisect_root(lambda d: response(d) - 1, peak, ratio)
    z = logistic(-k)
    assert abs(response(0) - (1 + A * z) * (1 - z)) < 1e-14
    assert response(0) < 1
    return {"Dt_over_Da": ratio, "A": A, "k": k,
            "peak_over_Da": peak, "peak_response": peak_value,
            "R_at_zero": response(0), "nominal_lower_over_Da": lower,
            "nominal_upper_over_Da": upper, "nominal_width_fold": upper / lower,
            "actual_control_lower_edge": 0.0}


def hill_threshold_roots(alpha, beta, epsilon, threshold):
    height = (math.sqrt(alpha) - math.sqrt(beta * epsilon)) ** 2 / (1 - epsilon)
    assert 0 < threshold < height
    K = alpha - beta * epsilon - threshold * (1 + epsilon)
    c = epsilon * (beta - alpha + threshold)
    disc = K * K - 4 * c * threshold
    assert K > 0 and disc > 0
    rad = math.sqrt(disc)
    low, high = 2 * threshold / (K + rad), (K + rad) / (2 * c)
    gain = lambda u: alpha * u / (1 + u) - beta * epsilon * u / (1 + epsilon * u)
    assert abs(gain(low) - threshold) < 1e-13
    assert abs(gain(high) - threshold) < 1e-13
    assert gain(math.sqrt(low * high)) > threshold
    return low, high


def positive_quadratic_roots(A, B, C):
    """Roots of A*x^2-B*x+C, with a stable smaller-root evaluation."""
    disc = B*B - 4*A*C
    assert A > 0 and B > 0 and C > 0 and disc > 0
    rad = math.sqrt(disc)
    lo, hi = 2*C/(B+rad), (B+rad)/(2*A)
    for x in (lo, hi):
        assert abs(A*x*x-B*x+C)/(A*x*x+B*x+C) < 1e-12
    return lo, hi


def normalized_assay_threshold_checks():
    reports = []
    for p0 in (0.2, 0.5, 0.8):
        r0 = 0.5*math.log(p0/(1-p0))
        alpha, beta, a, t = 1.0, 2.0, math.e, math.exp(5)
        C = alpha/(1+a)-beta/(1+t)
        P, Q = math.sqrt(alpha*a), math.sqrt(beta*t)
        xp = (P*t-Q*a)/(Q-P)
        gain = lambda x: alpha*x/(x+a)-beta*x/(x+t)-C
        response = lambda x: viability(r0+gain(x))/p0
        delta = (response(xp)-1)/4
        z = 0.5*math.log((1+delta)*(1-p0)/(1-p0*(1+delta)))
        assert p0*(1+delta) < 1
        assert abs(viability(r0+z)/p0-(1+delta)) < 1e-13
        c = C+z
        lo, hi = positive_quadratic_roots(beta-alpha+c,
                                         alpha*t-beta*a-c*(a+t),c*a*t)
        assert 1 < lo < xp < hi
        assert abs(response(lo)-(1+delta)) < 1e-12
        assert abs(response(hi)-(1+delta)) < 1e-12
        reports.append({'model':'linear_logistic','p0':p0,'normalized_threshold':delta,
                        'rapidity_threshold':z,'x_lower':lo,'x_upper':hi,
                        'dose_width_fold':math.log(hi)/math.log(lo)})

        alpha,beta,epsilon,h=.6,1.5,.01,2
        up=(math.sqrt(alpha)-math.sqrt(beta*epsilon))/(math.sqrt(beta*epsilon)-epsilon*math.sqrt(alpha))
        gain=lambda u: alpha*u/(1+u)-beta*epsilon*u/(1+epsilon*u)
        response=lambda u: viability(r0+gain(u))/p0
        delta=(response(up)-1)/4
        z=0.5*math.log((1+delta)*(1-p0)/(1-p0*(1+delta)))
        lo,hi=positive_quadratic_roots(epsilon*(beta-alpha+z),
                                      alpha-beta*epsilon-z*(1+epsilon),z)
        assert 0 < lo < up < hi
        assert abs(response(lo)-(1+delta)) < 1e-12
        assert abs(response(hi)-(1+delta)) < 1e-12
        reports.append({'model':'additive_Hill','p0':p0,'normalized_threshold':delta,
                        'rapidity_threshold':z,'u_lower':lo,'u_upper':hi,
                        'dose_width_fold':(hi/lo)**(1/h)})

    A,epsilon,h=.5,.04,2
    up=(A-epsilon)/(epsilon+math.sqrt(epsilon*A*(1+A-epsilon)))
    response=lambda u:(1+(1+A)*u)/((1+u)*(1+epsilon*u))
    delta=(response(up)-1)/4
    lo,hi=positive_quadratic_roots(epsilon*(1+delta),A-epsilon-delta*(1+epsilon),delta)
    assert 0 < lo < up < hi
    assert abs(response(lo)-(1+delta)) < 1e-12
    assert abs(response(hi)-(1+delta)) < 1e-12
    reports.append({'model':'product_Hill','normalized_threshold':delta,'u_lower':lo,'u_upper':hi,
                    'dose_width_fold':(hi/lo)**(1/h)})
    return reports


def unequal_equal_midpoint_example():
    # With st=3*sa, cosh(3z)/cosh(z)=4 cosh(z)^2-3 solves both roots exactly.
    alpha,beta,sa,st,midpoint,nominal_rho=.4,1.0,.2,.6,20.0,.5
    separation=10*math.acosh(math.sqrt((3+math.sqrt(beta*st/(alpha*sa)))/4))
    maximum,minimum=midpoint-separation,midpoint+separation
    gain=lambda d: alpha*logistic(sa*(d-midpoint))-beta*logistic(st*(d-midpoint))
    derivative=lambda d: (alpha*sa*logistic(sa*(d-midpoint))*logistic(-sa*(d-midpoint))
                          -beta*st*logistic(st*(d-midpoint))*logistic(-st*(d-midpoint)))
    assert abs(derivative(maximum)) < 1e-13
    assert abs(derivative(minimum)) < 1e-13
    assert derivative(0)>0 and derivative(midpoint)<0 and derivative(60)>0
    actual_rho=nominal_rho+gain(0)
    actual_baseline=viability(actual_rho)
    fold=viability(nominal_rho+gain(maximum))/actual_baseline
    assert 1.03048 < fold < 1.03050
    assert gain(minimum)<alpha-beta<gain(0)<gain(maximum)
    return {'Da':midpoint,'Dt':midpoint,'sa':sa,'st':st,'alpha':alpha,'beta':beta,
            'nominal_rho_b':nominal_rho,'actual_zero_rapidity':actual_rho,
            'actual_baseline_p0':actual_baseline,'D_maximum':maximum,
            'D_later_minimum':minimum,'actual_control_peak_ratio':fold,
            'scope':'Possible stimulation at equal midpoints; includes a later minimum and upward high-dose tail, so does not establish the equal-slope single-peak theorem.'}


def run():
    # Matched endpoint chord signs, only for the repair-only slice.
    chord_cases = 0
    for r in (0.0, 0.2, 1.0):
        for a in (0.1, 0.5, 1.0):
            A = viability(r + a) / viability(r) - 1
            for i in range(101):
                u = i / 100
                assert viability(r + a * u) / viability(r) >= 1 + A * u - 1e-13
                chord_cases += 1
    for r, a in ((-2.0, 0.5), (-1.0, 1.0), (-0.8, 0.3)):
        A = viability(r + a) / viability(r) - 1
        for i in range(101):
            u = i / 100
            assert viability(r + a * u) / viability(r) <= 1 + A * u + 1e-13
            chord_cases += 1

    # Full logistic repair-damage comparison with actual zero-dose controls.
    r, a, b, Da, slope = 0.0, 1.0, 20.0, 4.0, 1.0
    Dt = Da + math.log(49)
    A = viability(r + a) / viability(r) - 1
    def exact(d):
        return viability(r + a * logistic(slope * (d - Da))
                         - b * logistic(slope * (d - Dt)))
    def product(d):
        return (1 + A * logistic(slope * (d - Da))) * logistic(-slope * (d - Dt))
    zero_rapidity = r + a * logistic(-slope * Da) - b * logistic(-slope * Dt)
    exact_normalized, product_normalized = exact(Da) / exact(0), product(Da) / product(0)
    assert zero_rapidity >= 0 and 1 < exact_normalized < product_normalized
    full_counterexample = {"rho_b": r, "repair_rapidity": a, "damage_rapidity": b,
                          "s": slope, "Da": Da, "Dt": Dt, "repair_A_endpoint_matched": A,
                          "actual_zero_rapidity": zero_rapidity,
                          "dose": Da, "exact_actual_control_response": exact_normalized,
                          "product_actual_control_response": product_normalized}

    # A sufficient full conservative bound needs more than the repair curvature.
    # Calibrate both saturation fractions and keep the damage interval nonnegative.
    full_bound_cases = 0
    for r, a, b in ((1.0, 0.2, 0.5), (2.0, 0.8, 1.5)):
        A = viability(r + a) / viability(r) - 1
        H = 1 - viability(r - b) / viability(r)
        for i in range(21):
            for j in range(21):
                u, v = i / 20, j / 20
                ex = viability(r + a * u - b * v) / viability(r)
                chord = (1 + A * u) * (1 - H * v)
                assert ex >= chord - 1e-13
                full_bound_cases += 1

    # Exact finite-resistance flux ceilings, not universal endpoint peak estimates.
    finite = []
    for n in (2, 3):
        for Am in (Fraction(4, 5), Fraction(3, 2)):
            fold = 1 + Am / (n + (n - 1) * Am)
            finite.append({"n": n, "A_mol": float(Am), "flux_fold": float(fold),
                           "flux_fold_exact": str(fold)})
    assert min(x["flux_fold"] for x in finite) == float(Fraction(27, 23))
    assert max(x["flux_fold"] for x in finite) == float(Fraction(10, 7))

    # Repair-only maximum viability ceiling must use actual baseline control.
    ceilings = [{"reported_percent_of_control": pct, "necessary_actual_baseline_upper": 100/pct}
                for pct in (145, 200, 300)]

    protocol = [relative_protocol_case(r, A) for r in (5, 10, 20) for A in (0.3, 0.5, 0.8)]
    protocol_summary = []
    for A in (0.3, 0.5, 0.8):
        selected = [x for x in protocol if x["A"] == A]
        protocol_summary.append({"A": A,
                                 "minimum_nominal_width": min(x["nominal_width_fold"] for x in selected),
                                 "maximum_nominal_width": max(x["nominal_width_fold"] for x in selected)})
    absolute = []
    for slope in (0.5, 1.0, 2.0):
        cases = [common_logistic_product_peak(Da, Da*ratio, A, slope)/Da
                 for Da in (2, 5, 10, 20) for ratio in (5, 10, 20) for A in (0.3, 0.5, 0.8)]
        absolute.append({"common_s": slope, "minimum_exact_peak_over_Da": min(cases),
                         "maximum_exact_peak_over_Da": max(cases),
                         "ratio_10_A_point_5_peak_over_Da_by_Da": [
                             common_logistic_product_peak(Da,10*Da,0.5,slope)/Da for Da in (2,5,10,20)]})

    threshold_report = []
    alpha, beta, epsilon, h = 0.6, 1.5, 0.01, 2.0
    return_u = (alpha - beta * epsilon) / (epsilon * (beta - alpha))
    for threshold in (0.05, 0.01, 0.001):
        lo, hi = hill_threshold_roots(alpha, beta, epsilon, threshold)
        threshold_report.append({"rapidity_threshold": threshold, "u_lower": lo, "u_upper": hi,
                                 "true_threshold_width_fold": (hi / lo) ** (1/h),
                                 "mixed_zero_upper_width_fold": (return_u / lo) ** (1/h)})
    asymptotic_error = []
    for delta in (1e-3, 1e-4, 1e-5):
        lo, hi = hill_threshold_roots(alpha, beta, epsilon, delta)
        prediction = ((alpha-beta*epsilon)**2 / (epsilon*(beta-alpha)*delta))**(1/h)
        asymptotic_error.append(abs((hi/lo)**(1/h)/prediction-1))
    assert asymptotic_error[2] < asymptotic_error[1] < asymptotic_error[0]

    return {"status":"all supplemental checks passed", "stdlib_only":True,
            "repair_only_chord_cases":chord_cases, "full_product_counterexample":full_counterexample,
            "sufficient_full_calibrated_bound_cases":full_bound_cases,
            "finite_resistance_flux_folds":finite,
            "necessary_actual_control_baseline_ceilings":ceilings,
            "relative_k4_protocol_cases":protocol, "relative_k4_width_summary":protocol_summary,
            "common_absolute_s_exact_peak_grid":absolute,
            "additive_Hill_detection_widths":threshold_report,
            "normalized_assay_threshold_quadratics":normalized_assay_threshold_checks(),
            "unequal_slope_equal_midpoint_example":unequal_equal_midpoint_example(),
            "detection_width_asymptotic_errors":asymptotic_error,
            "scope":"Model/proof checks; no biological data reanalysis, no published approximation protocol inferred uniquely, and no SSRN citation-content certification."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = json.dumps(run(), indent=2) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
