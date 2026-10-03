import numpy as np
src=open('/tmp/claude-0/stage1/h1/noise_modelfree.py').read().split('# ---- per-block analysis')[0]
ns={}; exec(src, ns)
H_W,H_T,GRID_W,LAMS_T,n,N=ns['H_W'],ns['H_T'],ns['GRID_W'],ns['LAMS_T'],ns['n'],ns['N']
y=ns['df'][(ns['df'].src=='192')&(ns['df'].PairIndex==5)].pivot_table(index='Conc1',columns='Conc2',values='e').values.ravel()
# Whittaker brute force
D=ns['d2'](N); P_r=np.kron(D,np.eye(N)); P_c=np.kron(np.eye(N),D)
l=400; lr,lc=GRID_W[l]; H=H_W[l]
assert np.allclose(H, np.linalg.inv(np.eye(n)+lr*P_r+lc*P_c))
k=17; w=np.ones(n); w[k]=0; A=np.diag(w)+lr*P_r+lc*P_c; f=np.linalg.solve(A,w*y)
u=H@y; loo=(y-u)/(1-np.diag(H)); Fk=u-H[k]*loo[k]
print('W downdate err', abs(f-Fk).max())
Hw=np.linalg.solve(A,np.diag(w)); Gd=np.diag(H)+H[k]**2/(1-H[k,k]); print('W inner leverage err', abs(np.diag(Hw)[np.arange(n)!=k]-Gd[np.arange(n)!=k]).max())
j=30; w2=w.copy(); w2[j]=0; f2=np.linalg.solve(np.diag(w2)+lr*P_r+lc*P_c,w2*y); print('inner LOO err', abs((y[j]-f2[j])-(y[j]-Fk[j])/(1-Gd[j])))
# TPS vs scipy
from scipy.interpolate import RBFInterpolator
IJ=ns['IJ']; lam=LAMS_T[20]
Hs=np.column_stack([RBFInterpolator(IJ,np.eye(n)[:,c],kernel='thin_plate_spline',smoothing=lam)(IJ) for c in range(n)])
print('TPS hat vs scipy max err', abs(Hs-H_T[20]).max(), 'scaled lam?')
for c in (8*np.pi, 1/(8*np.pi), 1.0):
    Hs=np.column_stack([RBFInterpolator(IJ,np.eye(n)[:,cc],kernel='thin_plate_spline',smoothing=lam*c)(IJ) for cc in range(n)]); print(c, abs(Hs-H_T[20]).max())
# TPS with 63 points vs downdate
keep=np.arange(n)!=k; fk=RBFInterpolator(IJ[keep],y[keep],kernel='thin_plate_spline',smoothing=lam)(IJ)
H=H_T[20]; u=H@y; loo=(y-u)/(1-np.diag(H)); print('TPS downdate err', abs(fk-(u-H[k]*loo[k])).max())
print('edf range W', np.einsum('lkk->l',H_W).min(), np.einsum('lkk->l',H_W).max(), 'T', np.einsum('lkk->l',H_T).min(), np.einsum('lkk->l',H_T).max())
# isotonic LOO check: monotone feasibility
r=ns['iso_cv'](y); print('iso', r['cv'], r['nlev'])
