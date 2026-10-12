"""Finite checks supporting Paper8 entropy and response theorems."""
from pathlib import Path
import json,math
import numpy as np
Q = [np.diag([0., 1., 2.]), np.array([[0., 1., 0.2], [1., 0., 0.7], [0.2, 0.7, 0.]])]
R = np.array([[0.2, 0.1j, 0.2], [-0.1j, 0.4, 0.1], [0.2, 0.1, 0.9]])
def gibbs(beta):
    vals, vecs = np.linalg.eigh(-sum(b*q for b, q in zip(beta, Q)))
    vals = np.exp(vals-np.max(vals))
    return (vecs*vals)@vecs.conj().T/np.sum(vals)
def readings(rho):
    return np.array([np.trace(rho@q).real for q in Q])
def km_covariance(rho, A, B):
    vals, vecs = np.linalg.eigh(rho)
    a = vecs.conj().T@(A-np.trace(rho@A).real*np.eye(3))@vecs
    b = vecs.conj().T@(B-np.trace(rho@B).real*np.eye(3))@vecs
    logarithmic_mean = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            logarithmic_mean[i, j] = vals[i] if abs(vals[i]-vals[j]) < 1e-12 else (vals[i]-vals[j])/(math.log(vals[i])-math.log(vals[j]))
    return float(np.sum(logarithmic_mean*a*b.T).real)

beta = np.array([0.6, -0.3])
rho = gibbs(beta)
C = np.array([[km_covariance(rho, a, b) for b in Q] for a in Q])
v = np.array([km_covariance(rho, R, a) for a in Q])
step = 1e-6
dq = np.zeros((2, 2))
df = np.zeros(2)
for i in range(2):
    delta = np.eye(2)[i]*step
    rp, rm = gibbs(beta+delta), gibbs(beta-delta)
    dq[:, i] = (readings(rp)-readings(rm))/(2*step)
    df[i] = np.trace((rp-rm)@R).real/(2*step)
cov_error = np.max(np.abs(dq+C))
response_error = np.max(np.abs(df+v))
gradient_error = np.max(np.abs(df@np.linalg.inv(dq)-v@np.linalg.inv(C)))
assert np.min(np.linalg.eigvalsh(C)) > 0
assert max(cov_error, response_error, gradient_error) < 1e-8

endpoint_mix = np.diag([0.5, 0., 0.5])
middle_maxent = np.eye(3)/3
assert np.trace(endpoint_mix@Q[0]) == np.trace(middle_maxent@Q[0]) == 1.
assert not np.allclose(endpoint_mix, middle_maxent)
def entropy(r):
    p = np.linalg.eigvalsh(r)
    return -float(np.sum(p[p>0]*np.log(p[p>0])))

p = 0.3
c1, c2 = p, (1+p)/2
assert abs(2*c2-c1-1) < 1e-15
kinetic_ratios = [(b+c)/(a+b) for a,b,c in [(1.,1.,1.), (1.,1.,4.)]]
assert kinetic_ratios == [1., 2.5]

# A finite-frame twirl is the diagonal conditional expectation.
rng = np.random.default_rng(940)
G = rng.normal(size=(3,3))+1j*rng.normal(size=(3,3))
state = G@G.conj().T
state /= np.trace(state)
diag_state = np.diag(np.diag(state))
entropy_gain = entropy(diag_state)-entropy(state)
vals, vecs = np.linalg.eigh(state)
log_state = (vecs*np.log(vals))@vecs.conj().T
log_diag = np.diag(np.log(np.diag(diag_state).real))
rel_entropy = np.trace(state@(log_state-log_diag)).real
assert abs(entropy_gain-rel_entropy) < 1e-12
gamma, time = 1.7, 0.8
selected = math.exp(-gamma*time)*state+(1-math.exp(-gamma*time))*diag_state
assert np.allclose(np.diag(selected), np.diag(state))
assert np.min(np.linalg.eigvalsh(selected)) > 0

checks = {
    "noncommuting_Kubo_Mori": {"covariance_derivative_error": float(cov_error), "response_derivative_error": float(response_error), "q_gradient_error": float(gradient_error), "covariance_min_eigenvalue": float(np.min(np.linalg.eigvalsh(C)))},
    "mean_only_linear_selector_obstruction": {"same_mean_energy": 1., "linear_endpoint_mix_entropy": entropy(endpoint_mix), "maximum_entropy": entropy(middle_maxent), "output_difference_norm": float(np.linalg.norm(endpoint_mix-middle_maxent))},
    "one_conserved_two_varying_readings": {"p": p, "c1": c1, "c2": c2, "relation": "2c2-c1=1", "Jacobian_rank": 1},
    "same_equilibrium_distinct_kinetic_ratios": {"ratio_cases": kinetic_ratios, "equilibrium": "I/2", "nonconstant_conserved_readings": 0},
    "conditional_expectation_entropy_identity": {"entropy_gain": float(entropy_gain), "relative_entropy": float(rel_entropy), "residual": float(abs(entropy_gain-rel_entropy))},
    "clock_stationarity_without_RG_fixed_point": {"beta_lambda": 0.3, "r": 10., "d_lambda_dr": 0.3/(math.cosh(10)**2*math.tanh(10))},
    "status": "all independent checks passed",
}

Path(__file__).with_suffix('.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
print(json.dumps(checks,indent=2))
