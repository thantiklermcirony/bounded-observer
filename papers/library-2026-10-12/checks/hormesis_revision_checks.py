"""Independent checks for Paper 2 and three distinct hormesis response models."""
import hashlib
import json
import math
from pathlib import Path
import numpy as np
import sympy as s

xa,xb,fa,fb = s.symbols("xa xb fa fb",positive=True)
bias = (xa-xb)/(xa+xb)
increment_bias = (fa-fb)/(fa+fb)
filtered_bias = (fa*xa-fb*xb)/(fa*xa+fb*xb)
assert s.factor(filtered_bias-(bias+increment_bias)/(1+bias*increment_bias)) == 0
t = s.symbols("t",real=True)
clock = s.Function("clock")(t)
theta = s.Function("theta")
speed = s.diff(clock,t)
corrected = (s.diff(theta(clock),t,2)-s.diff(speed,t)/speed*s.diff(theta(clock),t))/speed**2
# Use an independent dummy coordinate to avoid relying on a later symbol.
coordinate = s.symbols("coordinate",real=True)
assert s.simplify(corrected-s.Subs(s.diff(theta(coordinate),coordinate,2),coordinate,clock)) == 0

x,epsilon,A = s.symbols("x epsilon A",positive=True)
R = (1+(1+A)*x)/((1+x)*(1+epsilon*x))
numerator = A-epsilon-2*epsilon*x-epsilon*(1+A)*x*x
assert s.simplify(s.diff(R,x)*(1+x)**2*(1+epsilon*x)**2-numerator) == 0
assert s.simplify((R-1)-x*(A-epsilon-epsilon*x)/((1+x)*(1+epsilon*x))) == 0
Rstar = (s.sqrt(1+A-epsilon)-s.sqrt(A*epsilon))**2/(1-epsilon)**2
onset_coefficient = s.simplify(s.diff(Rstar,A,2).subs(A,epsilon)/2)
assert onset_coefficient == 1/(4*epsilon)

# Independent derivative/evaluation checks over a grid, including near onset.
product_reports = []
for eps in [0.02,0.2,0.8]:
    for amp in [eps+0.001,eps+0.2,eps+2]:
        peak = (amp-eps)/(eps+math.sqrt(eps*amp*(1+amp-eps)))
        measured = (1+(1+amp)*peak)/((1+peak)*(1+eps*peak))
        claimed = (math.sqrt(1+amp-eps)-math.sqrt(amp*eps))**2/(1-eps)**2
        derivative_numerator = amp-eps-2*eps*peak-eps*(1+amp)*peak**2
        assert abs(derivative_numerator) < 1e-12
        assert abs(measured-claimed) < 1e-11
        left = peak*0.9
        right = peak*1.1
        assert amp-eps-2*eps*left-eps*(1+amp)*left*left > 0
        assert amp-eps-2*eps*right-eps*(1+amp)*right*right < 0
        product_reports.append({"A":amp,"epsilon":eps,"peak_x":peak,"peak_response":measured})
assert numerator.subs(A,epsilon) == -2*epsilon*x-epsilon*(1+epsilon)*x*x
D,Ka,Kt,ha,ht = s.symbols("D Ka Kt ha ht",positive=True)
sa = D**ha/(D**ha+Ka**ha)
st = D**ht/(D**ht+Kt**ht)
unequal = (1+A*sa)*(1-st)
assert s.simplify(D*s.diff(unequal,D)/unequal-
                  (A*ha*sa*(1-sa)/(1+A*sa)-ht*st)) == 0
onset_errors = []
for delta in [0.01,0.001,0.0001]:
    eps = 0.2
    amp = eps+delta
    peak = delta/(eps+math.sqrt(eps*amp*(1+amp-eps)))
    value = (1+(1+amp)*peak)/((1+peak)*(1+eps*peak))
    scaled = (value-1)/(delta*delta/(4*eps))
    onset_errors.append(abs(scaled-1))
assert onset_errors[2] < onset_errors[1] < onset_errors[0]

# Additive Hill model, rationalized through p=sqrt(A), q=sqrt(B epsilon).
u,p,q = s.symbols("u p q",positive=True)
delta_model = p*p*u/(1+u)-q*q*u/(1+epsilon*u)
ustar = (p-q)/(q-epsilon*p)
assert s.factor(s.diff(delta_model,u).subs(u,ustar)) == 0
assert s.factor(delta_model.subs(u,ustar)-(p-q)**2/(1-epsilon)) == 0
return_u = (p*p-q*q)/(q*q-epsilon*p*p)
assert s.factor(delta_model.subs(u,return_u)) == 0
alpha,beta = s.symbols("alpha beta",positive=True)
additive_peak = (s.sqrt(alpha)-s.sqrt(beta*epsilon))/(s.sqrt(beta*epsilon)-epsilon*s.sqrt(alpha))
additive_height = (s.sqrt(alpha)-s.sqrt(beta*epsilon))**2/(1-epsilon)
additive_onset_u = s.simplify(s.diff(additive_peak,alpha).subs(alpha,beta*epsilon))
additive_onset_height = s.simplify(s.diff(additive_height,alpha,2).subs(alpha,beta*epsilon)/2)
assert s.simplify(additive_onset_u-1/(2*beta*epsilon*(1-epsilon))) == 0
assert s.simplify(additive_onset_height-1/(4*beta*epsilon*(1-epsilon))) == 0
p0,small_increment = s.symbols("p0 small_increment",positive=True)
normalized_viability = s.exp(2*small_increment)/(1-p0+p0*s.exp(2*small_increment))
viability_linear = s.simplify(s.diff(normalized_viability,small_increment).subs(small_increment,0))
viability_quadratic = s.simplify(s.diff(normalized_viability,small_increment,2).subs(small_increment,0)/2)
assert s.simplify(viability_linear-2*(1-p0)) == 0
assert s.simplify(viability_quadratic-2*(1-p0)*(1-2*p0)) == 0

# Published equal-linear-dose logistic model.
a,b,P,Q = s.symbols("a b P Q",positive=True)
f = P*P/a*x/(x+a)-Q*Q/b*x/(x+b)
xstar = (P*b-Q*a)/(Q-P)
assert s.factor(s.diff(f,x).subs(x,xstar)) == 0
assert s.factor(f.subs(x,xstar)-(P*b-Q*a)**2/(a*b*(b-a))) == 0
assert s.factor(xstar-1-(P*(1+b)-Q*(1+a))/(Q-P)) == 0
C = f.subs(x,1)
ret = C*a*b/(C-P*P/a+Q*Q/b)
assert s.factor(f.subs(x,ret)-C) == 0

def linear_case(Da,Dt,slope,benefit,harm):
    aa,bb = math.exp(slope*Da),math.exp(slope*Dt)
    pp,qq = math.sqrt(benefit*aa),math.sqrt(harm*bb)
    initial = slope*(benefit*aa/(1+aa)**2-harm*bb/(1+bb)**2)
    root = (pp*bb-qq*aa)/(qq-pp)
    f0 = benefit/(1+aa)-harm/(1+bb)
    def increment(dose):
        xx = np.exp(slope*np.asarray(dose))
        return benefit*xx/(xx+aa)-harm*xx/(xx+bb)-f0
    grid = np.linspace(0,30,30001)
    values = increment(grid)
    if initial > 1e-10:
        peak_dose = math.log(root)/slope
        assert peak_dose > 0
        observed = float(increment(peak_dose))
        assert observed > 0
        assert abs(float(values.max())-observed) < 1e-6
    else:
        peak_dose = 0.0
        assert float(values.max()) < 1e-10
    rho0 = 0.7
    response = (1+np.tanh(rho0+values))/(1+math.tanh(rho0))
    assert abs(response[0] - 1) < 1e-14
    return {"Da":Da,"Dt":Dt,"s":slope,"A":benefit,"B":harm,
            "initial_derivative":initial,"interior_peak":initial>1e-10,
            "peak_dose":peak_dose,"grid_maximum_increment":float(values.max())}

linear_reports = [linear_case(1,2,1,1,10),linear_case(1,3,1,1,2),
                  linear_case(1,10,1,1,2),linear_case(4,5,1,0.3,1)]
aa,bb = math.e,math.exp(2)
boundary_B = aa/(1+aa)**2*(1+bb)**2/bb
linear_reports.append(linear_case(1,2,1,1,boundary_B))
assert not linear_reports[0]["interior_peak"]
assert abs(linear_reports[-1]["initial_derivative"]) < 1e-12

# Exact series-resistance finite perturbation and distinct homogeneous alternative.
n,m,F = s.symbols("n m F",positive=True)
fold = n/(n-1+1/F)
assert s.factor(fold-n*F/(1+(n-1)*F)) == 0
eta = s.factor((F-1)/(fold-1))
assert s.factor(eta-(n+(n-1)*(F-1))) == 0
multitarget = n/(n-m+m/F)
assert s.factor(multitarget-1-m*(F-1)/(n+(n-m)*(F-1))) == 0
resistance_reports = []
for count in [2,3,5]:
    for amplitude in [0.1,1,2]:
        series_fold = count*(1+amplitude)/(count+(count-1)*amplitude)
        geometric_fold = (1+amplitude)**(1/count)
        exact_eta = amplitude/(series_fold-1)
        assert abs(exact_eta-(count+(count-1)*amplitude)) < 1e-12
        assert abs(series_fold-geometric_fold) > 1e-5
        resistance_reports.append({"n":count,"A":amplitude,"series_fold":series_fold,
                                  "geometric_mean_fold":geometric_fold,"series_eta":exact_eta})

# Moment recurrence / rank checks and the mixture-cancellation counterexample.
z = s.symbols("z",real=True)
mixA = s.exp(z)+s.exp(3*z)
mixB = 1+s.exp(2*z)
assert s.simplify(mixA-s.exp(z)*mixB) == 0
variance_a = s.diff(mixA,z,2)/mixA-(s.diff(mixA,z)/mixA)**2
variance_b = s.diff(mixB,z,2)/mixB-(s.diff(mixB,z)/mixB)**2
assert s.simplify(variance_a-variance_b) == 0
assert variance_a.subs(z,0) == 1 and variance_b.subs(z,0) == 1
atoms,weights = [s.Integer(-1),s.Integer(2),s.Integer(4)],[s.Integer(1),s.Integer(2),s.Integer(3)]
moments = [sum(w*r**j for r,w in zip(atoms,weights)) for j in range(9)]
H = s.Matrix(5,5,lambda i,j:moments[i+j])
assert H.rank() == 3
poly = s.Poly(s.prod(z-r for r in atoms),z)
for j in range(6):
    assert sum(coeff*moments[j+power[0]] for power,coeff in poly.terms()) == 0
gaussian_moments = [s.Integer(0) if j%2 else s.factorial2(j-1) for j in range(7)]
assert s.Matrix(4,4,lambda i,j:gaussian_moments[i+j]).det() > 0

package = Path(__file__).resolve().parents[1]
paper2 = package/"papers"/"paper2.md"
report = {
    "status":"all checks passed",
    "paper2_sha256":hashlib.sha256(paper2.read_bytes()).hexdigest(),
    "product_Hill_checks":product_reports,
    "product_Hill_onset_coefficient":str(onset_coefficient),
    "product_Hill_onset_errors":onset_errors,
    "linear_logistic_checks":linear_reports,
    "additive_Hill_exact_identities":"peak derivative, peak amplitude and return dose verified",
    "additive_Hill_onset_u_coefficient":str(additive_onset_u),
    "additive_Hill_onset_height_coefficient":str(additive_onset_height),
    "normalized_viability_Taylor_linear":str(viability_linear),
    "normalized_viability_Taylor_quadratic":str(viability_quadratic),
    "series_resistance_checks":resistance_reports,
    "moment_Hankel_rank":H.rank(),
    "continuous_Gaussian_Hankel_positive":True,
    "additional_exact_checks":["projective filter bias composition","variable-clock curvature",
                               "unequal-Hill derivative condition","nonzero mixture variances cancel"],
    "known_reference_fix":"Price 1972 DOI is 10.1111/j.1469-1809.1972.tb00764.x"
}
print(json.dumps(report,indent=2))
