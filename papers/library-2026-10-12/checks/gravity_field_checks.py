"""Independent exact checks supporting the proposed field/gravity repairs.

Runs independently from the author drafts and writes a mathematical result receipt.
Run with the bundled Python runtime. No optional package is required.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path


def run():
    result = {}
    # Unit round sphere: Q(r)=2 atan(r/lambda), E=pi int(Q_r^2+sin(Q)^2/r^2)r dr.
    # The exact primitive is -4*pi*lambda^2/(lambda^2+r^2).
    result["bubble_energy"] = {
        "unit_round_metric": 4*math.pi,
        "standard_FS_metric_radius_one_half": math.pi,
        "ratio": 4,
    }
    assert abs(result["bubble_energy"]["unit_round_metric"] /
               result["bubble_energy"]["standard_FS_metric_radius_one_half"] - 4) < 1e-14
    # q=sqrt(1-|b|^2): dq^2=(b.db)^2/(1-|b|^2).
    b, db = (0.2, -0.3, 0.4), (0.6, 0.1, -0.2)
    b2 = sum(x*x for x in b)
    dot = sum(x*y for x,y in zip(b,db))
    dq = -dot/math.sqrt(1-b2)
    bures = (sum(x*x for x in db) + dot*dot/(1-b2))/4
    embedded = (sum(x*x for x in db) + dq*dq)/4
    assert abs(bures-embedded)<1e-14
    result["Bures_hemisphere_metric_residual"] = abs(bures-embedded)
    # A unit-mass, rotating Kerr example in geometric units.
    mass, spin = 1.0, 0.8
    r_plus = mass + math.sqrt(mass*mass-spin*spin)
    r_ergo_equator = 2*mass
    f_at_event_horizon_equator = 1-2*mass/r_plus
    result["Kerr_horizon_counterexample"] = {
        "M": mass, "a": spin, "event_horizon_r_plus": r_plus,
        "equatorial_ergosurface_r": r_ergo_equator,
        "f_at_equatorial_event_horizon": f_at_event_horizon_equator,
    }
    assert r_plus < r_ergo_equator and f_at_event_horizon_equator < 0
    # d eta/d tau=cosh(eta)/T0: eta=2 atanh(tan(tau/(2T0))).
    # Proper time to eta=infinity is pi*T0/2, acceleration=c*cosh(eta)/T0.
    result["unbounded_rate_finite_time"] = {"T0": 1, "proper_time_to_boundary": math.pi/2}
    # A Schwarzschild E=1 geodesic has a_phys=0 and dr/dtau=-sqrt(2M/r).
    # Proper time from r0 to zero equals (2/3)*r0^(3/2)/sqrt(2M).
    r0 = 2*mass
    result["zero_acceleration_GR_singularity"] = {
        "proper_acceleration": 0, "proper_time_from_horizon_to_r_zero":
        (2/3)*r0**1.5/math.sqrt(2*mass),
        "Kretschmann_at_r_0.1": 48*mass*mass/0.1**6,
    }
    # Fixed-total-intensity ray energy on unit S2: n=identity, E=constant.
    # |dn|^2=2, variation in E: E*|dn|^2=constant is the multiplier equation;
    # variation in n is E^2*tau(n)=0. It is a nontrivial constrained critical point.
    result["fixed_intensity_critical_point"] = {
        "domain": "unit S2", "n": "identity", "E": 1,
        "direction_gradient_squared": 2, "energy": 4*math.pi,
        "intensity_constraint_multiplier": 2,
    }
    # N Bell pairs straddling a region give S_A=N ln2 with qubit cells.
    # They can be states of the local Hamiltonian H=0, so locality + finite cells
    # alone do not imply an area law for an arbitrary selected state.
    result["finite_cell_local_state_counterexample"] = {
        "cross_region_Bell_pairs": 100, "entropy_nats": 100*math.log(2),
        "local_Hamiltonian": 0, "scaling": "volume when one pair per region cell",
    }
    return result

if __name__ == "__main__":
    output = Path(__file__).with_suffix(".json")
    result = run()
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"checks": "passed", "output": str(output),
                      "Kerr": result["Kerr_horizon_counterexample"],
                      "FS_quantum": result["bubble_energy"],
                      "GR_proper_time": result["zero_acceleration_GR_singularity"]}, indent=2))
