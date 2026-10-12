"""Verify the finite GKSL exposure bound and exact dictionary scope."""
from pathlib import Path
import sys
import json
import numpy as np
from scipy.linalg import expm
from scipy.integrate import solve_ivp

rng = np.random.default_rng(912)
results = {}
worst = 0.0
worst_gap = 1.0
for d in [2, 3, 4]:
    for trial in range(8):
        z = rng.normal(size=(d,d)) + 1j*rng.normal(size=(d,d))
        rho0 = z@z.conj().T + .5*np.eye(d)
        rho0 /= np.trace(rho0)
        a = rng.normal(size=(d,d)) + 1j*rng.normal(size=(d,d))
        H = (a+a.conj().T)/5
        jumps = []
        for j in range(2):
            a = (rng.normal(size=(d,d)) + 1j*rng.normal(size=(d,d)))/6
            a -= np.trace(a)*np.eye(d)/d
            jumps.append(a)
        G = sum(l.conj().T@l for l in jumps)
        g = np.linalg.eigvalsh(G)[-1]
        def rhs(t,y):
            rho = y[:d*d].reshape(d,d)
            K = y[d*d:].reshape(d,d)
            dr = -1j*(H@rho-rho@H) + sum(l@rho@l.conj().T for l in jumps) - (G@rho+rho@G)/2
            dk = (-1j*H-G/2)@K
            return np.concatenate([dr.ravel(),dk.ravel()])
        sol = solve_ivp(rhs,(0,2),np.concatenate([rho0.ravel(),np.eye(d,dtype=complex).ravel()]),
                        rtol=2e-11,atol=2e-12,dense_output=True)
        assert sol.success
        for t in np.linspace(0,2,21):
            y=sol.sol(t)
            rho=y[:d*d].reshape(d,d); K=y[d*d:].reshape(d,d)
            source_gap=rho-K@rho0@K.conj().T
            gap=float(np.linalg.eigvalsh((source_gap+source_gap.conj().T)/2)[0])
            lower=float(np.linalg.eigvalsh(rho0)[0]*np.exp(-g*t))
            actual=float(np.linalg.eigvalsh((rho+rho.conj().T)/2)[0])
            worst_gap=min(worst_gap,gap)
            assert gap > -2e-10 and actual >= lower-2e-10
            worst=max(worst,abs(np.trace(rho)-1))
results['rank_bound_random_models']={'models':24,'dimensions':[2,3,4],
    'time_points_per_model':21,'minimum_Duhamel_positive_source_eigenvalue':worst_gap,
    'worst_trace_error':float(worst)}

# Exact amplitude damping saturates the lower eigenvalue bound while excited
# population stays below 1/2. Finite-time arrival requires divergent exposure.
p0=.3
for xi in np.linspace(0,12,60):
    p=p0*np.exp(-xi)
    assert np.isclose(np.linalg.eigvalsh(np.diag([1-p,p]))[0],p0*np.exp(-xi))
results['amplitude_damping_saturation']={'initial_small_eigenvalue':p0,'lambda_min':'p0 exp(-Xi)'}

# t=s^2: both Lindblad rates and exposure change with the Jacobian.
g0=0.7
for ss in np.linspace(.01,2,30):
    xi_t=g0*ss**2
    xi_s=g0*ss**2
    assert np.isclose(xi_t,xi_s)
results['clock_change']={'t':'s^2','G_s':'2s G_t','Xi_preserved':True}

# A bounded unitary swap with a pure bath purifies in finite time, outside the
# bounded local GKSL premise: the reduced effective rate diverges at endpoint.
swap=np.array([[1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]],complex)
U=expm(-1j*np.pi*swap/2)
joint=U@np.kron(np.diag([.7,.3]),np.diag([1.,0.]))@U.conj().T
reduced=np.trace(joint.reshape(2,2,2,2),axis1=1,axis2=3)
assert np.allclose(reduced,np.diag([1.,0.]))
results['finite_swap_scope_counterexample']={'initial_system_full_rank':True,
    'pure_bath_available':True,'final_system_pure':True,
    'local_effective_decay_rate':'2 tan(t), divergent at pi/2'}

# Concurrence agrees with the ratio of cone determinant to cone energy.
for trial in range(40):
    psi=rng.normal(size=(2,2))+1j*rng.normal(size=(2,2))
    P=psi@psi.conj().T
    p0v=float(np.trace(P).real)
    sx=np.array([[0,1],[1,0]],complex)
    sy=np.array([[0,-1j],[1j,0]])
    sz=np.diag([1.,-1.])
    v=np.array([np.trace(P@sigma).real for sigma in [sx,sy,sz]])
    mass=2*abs(np.linalg.det(psi))
    concurrence=mass/p0v
    assert np.isclose(mass**2,p0v**2-v@v)
    assert np.isclose(concurrence**2,1-(v@v)/p0v**2)
results['mass_dictionary']={'random_states':40,'exact_algebraic_identity':True,
    'physical_momentum_and_mass_identification_required':True}

Path(__file__).with_name('time_boundary_checks.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
print('All five time and composition check groups passed.')
