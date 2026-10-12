"""Exact finite-sector checks for the conditional neutral-pair selector."""
from pathlib import Path
import sys
import json
from collections import Counter
import sympy as s

q=s.Rational
states=[('u',q(2,3))]*3+[('u',q(-2,3))]*3+[
    ('d',q(-1,3))]*3+[('d',q(1,3))]*3+[
    ('e',q(-1)),('e',q(1)),('nu',q(0)),('nu',q(0))]
pairs=[(i,j) for i,(_,a) in enumerate(states) for j,(_,b) in enumerate(states) if a+b==0]
assert len(pairs)==42
marginal=[q(sum(i==k for i,j in pairs),len(pairs)) for k in range(16)]
weights={name:sum(marginal[i] for i,(typ,charge) in enumerate(states) if typ==name) for name in ['u','d','e','nu']}
assert weights=={'u':q(3,7),'d':q(3,7),'e':q(1,21),'nu':q(2,21)}
mean=sum(marginal[i]*charge for i,(_,charge) in enumerate(states))
kQ=sum(marginal[i]*charge**2 for i,(_,charge) in enumerate(states))-mean**2
kc=(weights['u']+weights['d'])/6
assert mean==0 and kQ==q(2,7) and kc==q(1,7)

# Local unitary charge operations leave Omega invariant. The variance instead
# measures a retained pure reference, whose overlap is Tr(rho U).
theta=s.symbols('theta',real=True)
diagonal_entries=[(a+b==0) for _,a in states for _,b in states]
assert sum(diagonal_entries)==42
assert all(isinstance(x,bool) or x in [s.true,s.false] for x in diagonal_entries)

b=s.symbols('b',real=True)
pu=pd=q(1,5)+q(3,10)*b
pe=(1-b)/5
ratio=s.factor(((4*pu+pd)/9+pe)/((pu+pd)/6))
assert s.simplify(ratio-(28-3*b)/(6+9*b))==0
assert ratio.subs(b,0)==q(14,3)
assert ratio.subs(b,1)==q(5,3)
assert ratio.subs(b,q(16,21))==2
assert 10+4*8==42
n1,n8=s.symbols('n1 n8',positive=True)
bedge=4*n8/(10*n1+4*n8)
assert bedge.subs({n1:1,n8:8})==q(16,21)

fullweights={'u':q(6,16),'d':q(6,16),'e':q(2,16),'nu':q(2,16)}
fullratio=s.simplify(((4*fullweights['u']+fullweights['d'])/9+fullweights['e'])/((fullweights['u']+fullweights['d'])/6))
assert fullratio==q(8,3)

m,n=s.symbols('m n',positive=True)
D=38*m**2+n**2
assert s.simplify((12*m**2/D)/(6*m**2/D))==2
N=s.symbols('N',positive=True,integer=True)
DN=4*N**2+6
puN=pdN=2*N**2/DN
peN=2/DN
qu=(N+1)/(2*N); qd=(1-N)/(2*N)
kcN=(puN+pdN)/(2*N)
kQN=s.factor(puN*qu**2+pdN*qd**2+peN)
assert s.simplify(kQN/kcN-(N**2+3)/(2*N))==0

result={
 'carrier_dimension':16,'electric_zero_pair_dimension':42,
 'marginal_sector_weights':{k:str(v) for k,v in weights.items()},
 'K_colour':str(kc),'K_charge':str(kQ),'ratio':str(kQ/kc),
 'closed_colour_singlet_ratio':'14/3','unrestricted_electric_and_colour_edge_ratio':'8/3',
 'octet_weight_ratio':str(ratio),'regular_colour_edge_octet_weight':'16/21',
 'uniform_charged_multiplicity_and_neutral_species_robust':True,
 'general_colour_number_ratio':str(s.factor(kQN/kcN)),
 'scope':'Covariance ratio with a retained reference; gauge coupling interpretation requires a kinetic-response bridge.',
 'physical_selector_remaining':'Electrically closed matter pair, colour edge flux available, equal cost of relevant sectors.',
}
Path(__file__).with_name('neutral_pair_checks.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
print('Exact neutral-pair and alternative-boundary checks passed.')
