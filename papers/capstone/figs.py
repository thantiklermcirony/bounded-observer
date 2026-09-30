import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.integrate import quad
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':200})
INK='#15202b'; ACC='#2f58c9'; MUT='#7a8590'; GOOD='#2f7d57'; WARN='#a0691b'

# ---- Fig 1: equal rapidity steps, two views + the far side
fig,ax=plt.subplots(2,1,figsize=(6.4,2.6),gridspec_kw=dict(hspace=0.9))
psi=np.arange(0,9)*0.3
for a in ax: a.set_yticks([]); a.spines['left'].set_visible(False)
ax[0].hlines(0,0,3,color=MUT,lw=1); ax[0].plot(psi,0*psi,'o',color=ACC,ms=4); ax[0].set_xlim(-0.05,3.05); ax[0].set_xlabel(r'rapidity $\psi$: equal steps of 0.3',labelpad=1)
x=np.tanh(psi); ax[1].hlines(0,0,1,color=MUT,lw=1); ax[1].plot(x,0*x,'o',color=INK,ms=4); ax[1].axvline(1,color=ACC,ls='--',lw=1); ax[1].text(1.005,0.02,'horizon\n$x=1$',color=ACC,va='bottom',fontsize=8)
ax[1].set_xlim(-0.02,1.12); ax[1].set_xlabel(r'observed value $x=\tanh\psi$: the same steps, read from inside',labelpad=1)
fig.savefig('fig1_horizon.png',bbox_inches='tight'); plt.close()

# ---- Fig 2: trichotomy generators + the projective loop with inside and outside
fig,ax=plt.subplots(1,2,figsize=(6.6,2.7),gridspec_kw=dict(width_ratios=[1.1,1]))
u=np.linspace(-2.2,2.2,400)
for k,c,l in [(1,ACC,r'$\kappa=1$ hyperbolic: two horizons'),(0,INK,r'$\kappa=0$ parabolic: flat'),(-1,WARN,r'$\kappa=-1$ elliptic: wraps')]:
    ax[0].plot(u,1-k*u*u,color=c,lw=1.4,label=l)
ax[0].axhline(0,color=MUT,lw=0.8); ax[0].plot([-1,1],[0,0],'o',color=ACC,ms=4); ax[0].set_ylim(-3,4); ax[0].set_xlabel('$u$'); ax[0].set_ylabel(r'generator $X(u)=1-\kappa u^2$'); ax[0].legend(frameon=False,fontsize=7,loc='upper center')
# projective loop: x = tan(phi/2) mapped to a circle; inside |x|<1 is the arc phi in (-pi/2, pi/2)
th=np.linspace(0,2*np.pi,400); a=ax[1]; a.set_aspect('equal'); a.axis('off')
a.plot(np.cos(th),np.sin(th),color=MUT,lw=1)
ins=np.linspace(-np.pi/2,np.pi/2,200); a.plot(np.cos(ins),np.sin(ins),color=ACC,lw=3)
out=np.linspace(np.pi/2,3*np.pi/2,200); a.plot(np.cos(out),np.sin(out),color=WARN,lw=3)
for ang,lab in [(0,'$x=0$'),(np.pi/2,'$x=+1$'),(-np.pi/2,'$x=-1$'),(np.pi,r'$x=\infty$')]:
    a.plot(np.cos(ang),np.sin(ang),'o',color=INK,ms=4); a.text(1.18*np.cos(ang),1.18*np.sin(ang),lab,ha='center',va='center',fontsize=8)
a.text(0.42,0,'inside\n$|x|<1$\nhyperbolic\nstates',ha='center',va='center',color=ACC,fontsize=7.5)
a.text(-0.45,0,'outside\n$|x|>1$\nsame law,\ninverted chart',ha='center',va='center',color=WARN,fontsize=7.5)
a.text(0,-1.42,'The projective line: the two horizons are seams, not ends',ha='center',fontsize=8)
fig.savefig('fig2_trichotomy.png',bbox_inches='tight'); plt.close()

# ---- Fig 3: boundary exponent (Osgood) and the max-ent exponents
fig,ax=plt.subplots(1,2,figsize=(6.6,2.6))
g=np.linspace(0,1.6,161)
T=[quad(lambda e:(1-e)**(-gg),0,1,limit=200)[0] if gg<1 else np.inf for gg in g]
ax[0].plot(g[np.array(T)<np.inf],np.array(T)[np.array(T)<np.inf],color=INK,lw=1.4)
ax[0].axvline(1,color=ACC,ls='--',lw=1); ax[0].set_ylim(0,25); ax[0].text(1.03,20,r'$\gamma\geq1$: never arrives',color=ACC,fontsize=8); ax[0].text(0.12,20,r'$\gamma<1$: arrives',fontsize=8)
ax[0].set_xlabel(r'boundary exponent $\gamma$ in $X(e)\sim(1-e)^\gamma$'); ax[0].set_ylabel('time to reach the ceiling')
# max-ent: Var vs (1-m) on log-log for two-point (slope 1) and uniform (slope 2)
th_=np.linspace(0.5,8,200); m2=np.tanh(th_); v2=1-m2**2
mL=1/np.tanh(th_)-1/th_; vL=1/th_**2-1/np.sinh(th_)**2
ax[1].loglog(1-m2,v2,color=ACC,lw=1.4,label='two states (atom at the end): slope 1')
ax[1].loglog(1-mL,vL,color=WARN,lw=1.4,label='uniform continuum: slope 2')
ax[1].set_xlabel('distance to the ceiling, $1-m$'); ax[1].set_ylabel('generator $X=\mathrm{Var}_\\theta(s)$'); ax[1].legend(frameon=False,fontsize=7,loc='lower right')
fig.savefig('fig3_exponent.png',bbox_inches='tight'); plt.close()

# ---- Fig 4: exponential room, a tree in the disk, gyration triangle
fig,ax=plt.subplots(1,3,figsize=(7.2,2.5),gridspec_kw=dict(width_ratios=[1,1,1]))
r=np.linspace(0,6,200); ax[0].semilogy(r,2*np.pi*r,color=INK,lw=1.4,label='flat: $2\\pi r$'); ax[0].semilogy(r,2*np.pi*np.sinh(r),color=ACC,lw=1.4,label='hyperbolic: $2\\pi\\sinh r$')
ax[0].set_xlabel('radius $r$'); ax[0].set_ylabel('circumference'); ax[0].legend(frameon=False,fontsize=7)
# binary tree in Poincare disk: place nodes at hyperbolic radius depth*d, angles spread
a=ax[1]; a.set_aspect('equal'); a.axis('off'); a.plot(np.cos(th),np.sin(th),color=MUT,lw=1)
def pd(rh,ang): rr=np.tanh(rh/2); return rr*np.cos(ang),rr*np.sin(ang)
nodes={():(0,0)}; d=1.0
for depth in range(1,6):
    for k in range(2**depth):
        ang=2*np.pi*(k+0.5)/2**depth; nodes[(depth,k)]=(depth*d,ang)
def pdz(rh,ang): rr=np.tanh(rh/2); return rr*np.exp(1j*ang)
def geo(p,q,n=40):
    f=lambda z:(z-p)/(1-np.conj(p)*z); g=lambda w:(w+p)/(1+np.conj(p)*w); qq=f(q); return np.array([g(t*qq) for t in np.linspace(0,1,n)])
for depth in range(1,6):
    for k in range(2**depth):
        p=(depth-1,k//2) if depth>1 else ()
        z0=pdz(*nodes[p]) if p!=() else 0j; z1=pdz(*nodes[(depth,k)]); sgm=geo(z0,z1); a.plot(sgm.real,sgm.imag,color=ACC,lw=0.7)
        a.plot(z1.real,z1.imag,'o',color=INK,ms=1.2)
a.set_title('a binary tree, 63 nodes,\nequal hyperbolic edge lengths',fontsize=8)
# gyration triangle
a=ax[2]; a.set_aspect('equal'); a.axis('off'); a.plot(np.cos(th),np.sin(th),color=MUT,lw=1)
A,B=0.4+0.2j,0.7*np.exp(2j); mob=lambda p,q:(p+q)/(1+np.conj(p)*q)
def geod(p,q,n=60):
    # hyperbolic segment via Mobius map to origin
    f=lambda z:(z-p)/(1-np.conj(p)*z); g=lambda w:(w+p)/(1+np.conj(p)*w); qq=f(q); return np.array([g(t*qq) for t in np.linspace(0,1,n)])
for p,q in [(0,A),(A,mob(A,B)),(mob(A,B),0)]:
    s=geod(complex(p),complex(q)); a.plot(s.real,s.imag,color=ACC,lw=1.3)
s=geod(0j,B); a.plot(s.real,s.imag,color=MUT,lw=0.8,ls='--')
for z,l in [(0,'0'),(A,'$a$'),(mob(A,B),'$a\\oplus b$'),(B,'$b$')]:
    a.plot(z.real,z.imag,'o',color=INK,ms=3); a.text(z.real+0.06,z.imag+0.06,l,fontsize=8)
a.set_title('gyr$[a,b]$ = area of $(0,a,a\\oplus b)$\n= 0.600 rad here',fontsize=8)
fig.savefig('fig4_room.png',bbox_inches='tight'); plt.close()

# ---- Fig 5: the dial
fig,ax=plt.subplots(figsize=(4.2,2.6)); e=np.linspace(0,0.999,300)
for al,c,l in [(1-1e-6,WARN,r'$\alpha\to1$ Loewe (odds add)'),(0,INK,r'$\alpha=0$ Bliss'),(-1,ACC,r'$\alpha=-1$ Einstein conorm'),(-4,MUT,r'$\alpha=-4$')]:
    ax.plot(e,(2*e-(1+al)*e*e)/(1-al*e*e),color=c,lw=1.3,label=l)
ax.set_xlabel('single-agent effect $e$ (both agents)'); ax.set_ylabel('combined effect $e\\oplus_\\alpha e$'); ax.legend(frameon=False,fontsize=7); ax.set_ylim(0,1)
fig.savefig('fig5_dial.png',bbox_inches='tight'); plt.close()

# ---- Fig 6: empirical: I2 medians and H1 alpha by overlap
import pandas as pd, json
fig,ax=plt.subplots(1,2,figsize=(6.8,2.6),gridspec_kw=dict(width_ratios=[1,1]))
meas=['risk difference\n(flat)','Bliss-chart\ndifference','log odds\nratio','log risk\nratio']; med=[0.52,0.50,0.19,0.17]
ax[0].barh(meas,med,color=[MUT,MUT,ACC,ACC]); ax[0].set_xlabel('median $I^2$ across 19 meta-analyses'); ax[0].invert_yaxis()
R=pd.read_csv('/tmp/claude-0/-home-claude/24aa060f-dc23-5cf0-ba31-21c46ef61c81/scratchpad/h1/h1_pairs.csv')
data=[R[R.level==L].alpha.values for L in (0,1,2)]
ax[1].boxplot(data,widths=0.5,medianprops=dict(color=ACC)); ax[1].set_xticks([1,2,3],['distinct\n(25 pairs)','same axis\n(10)','shared target\n(1)']); ax[1].set_ylabel(r'dial position $\alpha$ (pair median)'); ax[1].axhline(0,color=MUT,lw=0.7,ls=':'); ax[1].axhline(1,color=MUT,lw=0.7,ls=':')
ax[1].set_title(r'H1 on DECREASE: $\rho=-0.12$, $p=0.76$',fontsize=8)
fig.savefig('fig6_empirical.png',bbox_inches='tight'); plt.close()
print('figs done')
