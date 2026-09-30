import pyreadr, numpy as np, pandas as pd, glob
def load(n): return list(pyreadr.read_r(n+".rda").values())[0]
sets={}
b=load("dat.bcg"); sets["bcg"]=pd.DataFrame(dict(a=b.tpos,n1=b.tpos+b.tneg,c=b.cpos,n2=b.cpos+b.cneg))
x=load("dat.axfors2021"); sets["axfors2021"]=pd.DataFrame(dict(a=x.hcq_arm_event,n1=x.hcq_arm_total,c=x.control_arm_event,n2=x.control_arm_total))
d=load("dat.damico2009"); sets["damico2009"]=pd.DataFrame(dict(a=d.xt,n1=d.nt,c=d.xc,n2=d.nc))
for n in ["anand1999","egger2001","graves2010","hine1989","laopaiboon2015","lau1992","lee2004","li2007","nielweise2007"]:
    df=load("dat."+n); sets[n]=pd.DataFrame(dict(a=df.ai,n1=df.n1i,c=df.ci,n2=df.n2i))
y=load("dat.yusuf1985")
for t,g in y.groupby("table"):
    if len(g)>=5: sets["yusuf1985_"+str(t)]=pd.DataFrame(dict(a=g.ai,n1=g.n1i,c=g.ci,n2=g.n2i))
c=load("dat.collins1985a"); sets["collins1985a"]=pd.DataFrame(dict(a=c["d.xti"],n1=c.nti,c=c["d.xci"],n2=c.nci))
def measures(df):
    df=df.dropna().astype(float); df=df[(df.n1>0)&(df.n2>0)]
    a,n1,c,n2=df.a.values,df.n1.values,df.c.values,df.n2.values
    z=(a==0)|(c==0)|(a==n1)|(c==n2); cc=np.where(z,0.5,0.0)
    a2,c2,n1b,n2b=a+cc,c+cc,n1+2*cc,n2+2*cc
    p1,p0=a2/n1b,c2/n2b
    out={}
    out["RD (flat)"]=(p1-p0, p1*(1-p1)/n1b+p0*(1-p0)/n2b)
    out["log RR"]=(np.log(p1/p0), (1-p1)/(n1b*p1)+(1-p0)/(n2b*p0))
    out["log OR (logit chart)"]=(np.log(p1/(1-p1))-np.log(p0/(1-p0)), 1/(n1b*p1*(1-p1))+1/(n2b*p0*(1-p0)))
    out["Bliss chart -log(1-p)"]=(np.log((1-p0)/(1-p1)), p1/(n1b*(1-p1))+p0/(n2b*(1-p0)))
    return out,p0
def I2(y,v):
    w=1/v; mu=np.sum(w*y)/np.sum(w); Q=np.sum(w*(y-mu)**2); k=len(y)
    return max(0,(Q-(k-1))/Q) if Q>0 else 0.0, Q, k
rows=[]
for name,df in sets.items():
    m,p0=measures(df)
    if len(p0)<5: continue
    r={"meta":name,"k":len(p0),"baseline range":f"{p0.min():.3f}-{p0.max():.3f}"}
    for k,(y,v) in m.items(): r[k]=I2(y,v)[0]
    rows.append(r)
T=pd.DataFrame(rows); cols=["RD (flat)","log RR","log OR (logit chart)","Bliss chart -log(1-p)"]
T["most homogeneous"]=T[cols].idxmin(axis=1)
pd.set_option("display.width",200); print(T.round(3).to_string(index=False))
print("\nwins:",T["most homogeneous"].value_counts().to_dict())
print("median I2:",T[cols].median().round(3).to_dict())
print("RD is least homogeneous in",(T[cols].idxmax(axis=1)=="RD (flat)").sum(),"of",len(T))
# paired sign test: rapidity charts vs RD
from scipy.stats import wilcoxon
for k in cols[1:]: print(k,"vs RD: Wilcoxon p =",round(wilcoxon(T[k],T["RD (flat)"]).pvalue,4), " lower in",(T[k]<T["RD (flat)"]).sum(),"/",len(T))
T.to_csv("h2_results.csv",index=False)
