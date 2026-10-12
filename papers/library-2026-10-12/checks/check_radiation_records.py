"""Distinguish an aberrated sky probability from bolometric radiation energy."""
from pathlib import Path
import sys
import json
import numpy as np
from scipy.integrate import quad
results=[]
for beta in [.1,.3,.6,.85]:
    # Azimuth already integrated: the distributions below integrate over mu.
    p2=lambda mu:(1-beta**2)/(2*(1-beta*mu)**2)
    p4=lambda mu:3*(1-beta**2)**3/(2*(3+beta**2)*(1-beta*mu)**4)
    norm2=quad(p2,-1,1,epsabs=1e-12)[0]
    norm4=quad(p4,-1,1,epsabs=1e-12)[0]
    f2=quad(lambda mu:mu*p2(mu),-1,1,epsabs=1e-12)[0]
    chi2=quad(lambda mu:mu**2*p2(mu),-1,1,epsabs=1e-12)[0]
    f4=quad(lambda mu:mu*p4(mu),-1,1,epsabs=1e-12)[0]
    chi4=quad(lambda mu:mu**2*p4(mu),-1,1,epsabs=1e-12)[0]
    f2_exact=1/beta-(1-beta**2)*np.arctanh(beta)/beta**2
    f4_exact=4*beta/(3+beta**2)
    chi4_exact=(1+3*beta**2)/(3+beta**2)
    assert np.isclose(norm2,1) and np.isclose(norm4,1)
    assert np.isclose(f2,f2_exact) and np.isclose(f4,f4_exact)
    assert np.isclose(chi4,chi4_exact)
    assert abs(f2-f4)>1e-3
    gamma=1/np.sqrt(1-beta**2)
    boost=np.array([[gamma,0,0,gamma*beta],[0,1,0,0],[0,0,1,0],[gamma*beta,0,0,gamma]])
    T=boost@np.diag([1.,1/3,1/3,1/3])@boost.T
    assert np.isclose(T[0,3]/T[0,0],f4)
    assert np.isclose(T[3,3]/T[0,0],chi4)
    results.append({'beta':beta,'sky_probability_flux':f2,'radiation_energy_flux':f4,
                    'sky_second_moment':chi2,'radiation_pressure':chi4})
out={'status':'All normalization, moment and stress-tensor checks passed.',
     'claim_repaired':'The squared Poisson kernel does not have the fourth-power radiation M1 moments.',
     'cases':results}
Path(__file__).with_name('radiation_record_checks.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
