"""Independent algebraic and finite-matrix QA for publication Paper 6."""
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
import sympy as s

N,a,b,h = s.symbols("N a b h", nonzero=True)
u,d,e,n = a+h,a-h,b-h,b+h
gravity = N*(2*a-u-d) + 2*b-e
cubic = N*(2*a**3-u**3-d**3) + 2*b**3-e**3
assert s.expand(cubic.subs(b,-N*a) - (h-N*a)**3) == 0
assert s.simplify(gravity.subs(b,-N*a) - (h-N*a)) == 0
assert s.simplify((gravity-n)) == 0
assert s.simplify((cubic-n**3) + 6*h**2*(N*a+b)) == 0
qbl,lbl = 1/N,-1
mixed_y2_bl = N*qbl*(2*a*a-u*u-d*d) + lbl*(2*b*b-e*e-n*n)
mixed_y_bl2 = N*qbl*qbl*(2*a-u-d) + lbl*lbl*(2*b-e-n)
assert s.simplify(mixed_y2_bl) == 0
assert s.simplify(mixed_y_bl2) == 0

weights = {"H":(0,1,3),"Q":(1,1,1),"uR":(1,0,4),
           "dR":(1,0,-2),"L":(0,1,-3),"eR":(0,0,-6),"nuR":(0,0,0)}
assert all((q+2*t+3*p)%6 == 0 for t,p,q in weights.values())
for k in range(6):
    for t,p,q in weights.values():
        phase = np.exp(2j*np.pi*k*t/3)*(-1)**(k*p)*np.exp(1j*np.pi*k*q/3)
        assert abs(phase-1) < 1e-12
assert (2*(2+1))%2 == 0 and (1*(2+1))%2 == 1

def allowed(count, maximum):
    charges = list(range(-maximum,maximum+1,2))
    result = []
    for qs in itertools.combinations_with_replacement(charges,count):
        if sum(qs) == 0 and all(-q not in qs for q in qs):
            result.append(qs)
    return result
assert allowed(2,3) == []
assert allowed(4,1) == []
minimal = allowed(4,3)
assert set(minimal) == {(-3,1,1,1),(-1,-1,-1,3)}

g,gp,v = s.symbols("g gp v", positive=True, real=True)
paulis = [s.Matrix([[0,1],[1,0]]),s.Matrix([[0,-s.I],[s.I,0]]),s.diag(1,-1)]
vacuum = s.Matrix([0,v/s.sqrt(2)])
gens = [g*p/2 for p in paulis] + [gp*s.eye(2)/2]
mass = s.Matrix(4,4,lambda i,j:s.simplify((vacuum.conjugate().T*(gens[i]*gens[j]+gens[j]*gens[i])*vacuum)[0]))
expected = v*v/4*s.Matrix([[g*g,0,0,0],[0,g*g,0,0],[0,0,g*g,-g*gp],[0,0,-g*gp,gp*gp]])
assert mass == expected
assert s.simplify(mass.det()) == 0
assert s.simplify(mass[2:4,2:4].trace()-(g*g+gp*gp)*v*v/4) == 0

rng = np.random.default_rng(61012)
raw = rng.normal(size=(4,4))+1j*rng.normal(size=(4,4))
rho = raw@raw.conj().T
rho /= np.trace(rho)
raw_a = rng.normal(size=(4,4))+1j*rng.normal(size=(4,4))
A = (raw_a+raw_a.conj().T)/2
mean = np.trace(rho@A).real
variance = np.trace(rho@A@A).real - mean*mean
w,U = np.linalg.eigh(A)
eps = 1e-4
W = (U*np.exp(1j*eps*w))@U.conj().T
assert abs((1-abs(np.trace(rho@W))**2)/(eps*eps)-variance) < 1e-6
shift = A+7*np.eye(4)
assert abs((np.trace(rho@shift@shift).real-np.trace(rho@shift).real**2)-variance) < 1e-12
Y = np.eye(2)/2
assert np.trace(Y@Y).real/2 == 0.25
assert np.trace(Y@Y).real/2 - (np.trace(Y).real/2)**2 == 0

charge_dimensions = {s.Rational(2,3):3,s.Rational(-2,3):3,
                     s.Rational(1,3):3,s.Rational(-1,3):3,
                     s.Integer(1):1,s.Integer(-1):1,s.Integer(0):2}
pair_dimension = sum(dim*charge_dimensions[-q] for q,dim in charge_dimensions.items())
assert pair_dimension == 42
pu,pd,pe,pnu = s.Rational(3,7),s.Rational(3,7),s.Rational(1,21),s.Rational(2,21)
kc = (pu+pd)/6
kq = (4*pu+pd)/9+pe
assert pu+pd+pe+pnu == 1 and kc == s.Rational(1,7) and kq/kc == 2
closed_ratio = ((4*s.Rational(1,5)+s.Rational(1,5))/9+s.Rational(1,5))/(2*s.Rational(1,5)/6)
assert closed_ratio == s.Rational(14,3)
octet = s.Rational(32,42)
assert (28-3*octet)/(6+9*octet) == 2
assert s.Rational(4*8,10*1+4*8) == octet

paper = Path(__file__).resolve().parents[1]/"papers"/"paper6.md"
text = paper.read_text(encoding="utf-8")
assert "C:/" not in text and "plugin://" not in text
assert text.count("**Theorem ") == 9
assert sum(line.startswith("[") and "] " in line for line in text.splitlines()) == 16
report = {
    "status":"all checks passed",
    "paper_sha256":hashlib.sha256(paper.read_bytes()).hexdigest(),
    "verified":["centred covariance and scalar-generator degeneracy",
                "Higgs mass matrix","SM Z6 weights and kernel phases",
                "anomaly cubic with and without right-handed neutrino",
                "mixed Y/B-L coefficients","total-generation parity counterexample",
                "minimal U2 charge multisets","neutral-pair dimension and response",
                "closed-colour and regular-edge alternatives","publication path hygiene"],
    "minimal_multisets":minimal,
    "neutral_pair_dimension":pair_dimension,
    "neutral_pair_ratio":str(kq/kc),
    "closed_colour_ratio":str(closed_ratio),
    "primary_reference_count":16
}
print(json.dumps(report,indent=2))
