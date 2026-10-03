import numpy as np
src=open('noise_forensic.py').read()
i=src.index('def iso_last'); j=src.index('# null for lag-1')
from scipy.optimize import isotonic_regression
rng=np.random.default_rng(7)
exec(src[i:j])
d=np.r_[0, 3.0**np.arange(7)]
def surf(ec1,ec2,n1,n2,em1,em2):
    a=em1*d**n1/(ec1**n1+d**n1); b=em2*d**n2/(ec2**n2+d**n2)
    A,B=np.meshgrid(a,b,indexing='ij'); return A+B-A*B
for name,T in [('flat-ish (ec high)',surf(3000,3000,1,1,.6,.6)),('typical',surf(100,30,1,1.5,.8,.7)),('steep',surf(10,10,2,2,1,1))]:
    for sg in (0.02,0.04,0.08):
        lb=[];cal=[];real=[]
        for _ in range(6):
            eps=sg*rng.standard_normal(T.shape); Y=T+eps
            l=np.sqrt(np.mean((Y-iso2d(Y))**2)); lb.append(l); real.append(np.sqrt(np.mean(eps**2))); cal.append(iso_cal(Y,l))
        print(f'{name:20s} sigma={sg}: realised {np.mean(real):.4f} iso_lb {np.mean(lb):.4f} iso_cal {np.mean(cal):.4f} (sd {np.std(cal):.4f})')
