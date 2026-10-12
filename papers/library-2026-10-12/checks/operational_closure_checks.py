"""Finite checks of the capstone's known closure constructions, not proof substitutes."""
from pathlib import Path
import json
import numpy as np

rng=np.random.default_rng(20261012)
worst=0.0
def partial_environment(joint,d,e):
    return np.trace(joint.reshape(d,e,d,e),axis1=1,axis2=3)
for d in (2,3,4):
    e=3
    z=rng.normal(size=(d,d))+1j*rng.normal(size=(d,d))
    rho=z@z.conj().T;rho/=np.trace(rho)
    values,vectors=np.linalg.eigh(rho)
    amplitude=vectors@np.diag(np.sqrt(values))
    pure=amplitude.reshape(-1)
    marginal=partial_environment(np.outer(pure,pure.conj()),d,d)
    worst=max(worst,float(np.linalg.norm(marginal-rho)))
    z=rng.normal(size=(d*e,d))+1j*rng.normal(size=(d*e,d))
    isometry=np.linalg.qr(z)[0]
    kraus=[isometry.reshape(d,e,d)[:,j,:] for j in range(e)]
    assert np.linalg.norm(sum(k.conj().T@k for k in kraus)-np.eye(d))<1e-12
    dilation=isometry@rho@isometry.conj().T
    direct=sum(k@rho@k.conj().T for k in kraus)
    worst=max(worst,float(np.linalg.norm(partial_environment(dilation,d,e)-direct)))
    assert abs(np.trace(direct)-1)<1e-12
    assert np.linalg.eigvalsh(direct).min()>-1e-12
    outcome_probabilities=np.array([np.trace(k@rho@k.conj().T).real for k in kraus])
    assert abs(outcome_probabilities.sum()-1)<1e-12
    for p,k in zip(outcome_probabilities,kraus):
        if p>1e-14:assert abs(np.trace(k@rho@k.conj().T/p)-1)<1e-12
    # Composition has product Kraus operators and remains trace preserving.
    products=[a@b for a in kraus for b in kraus]
    assert np.linalg.norm(sum(k.conj().T@k for k in products)-np.eye(d))<1e-12
    # Tensor composition preserves Kraus completeness too.
    products=[np.kron(a,b) for a in kraus for b in kraus]
    assert np.linalg.norm(sum(k.conj().T@k for k in products)-np.eye(d*d))<1e-11
assert worst<1e-12
top_boundary=173.34+(125.20-129.6+0.5*(0.1180-0.1184)/0.0007)/2
assert abs(top_boundary-170.99714285714285)<1e-12
results={
    'status':'all checks passed',
    'dimensions':[2,3,4],
    'purification_and_Kraus_dilation_max_residual':worst,
    'instrument_probabilities_and_serial_parallel_completeness':'passed',
    'Buttazzo_Eq64_inverse_at_declared_inputs_GeV':top_boundary,
    'scope':'Finite checks of explicit constructions. The capstone proofs establish the general claims; the stability-fit inverse is not a new UHL mass prediction.'
}
Path(__file__).with_suffix('.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
print(json.dumps(results,indent=2))
