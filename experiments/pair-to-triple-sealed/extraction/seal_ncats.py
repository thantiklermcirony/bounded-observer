import rdata, pandas as pd, numpy as np, hashlib, json
p="raw/pkg_shuyuzheng_synergyfinder/data/NCATS_screening_data.rda"
d=pd.DataFrame(list(rdata.read_rda(p).values())[0]); d.columns=[str(c) for c in d.columns]
cc=['conc1','conc2','conc3']; d['n_drugs']=(d[cc]>0).sum(axis=1)
tr=d[d.n_drugs>=3]; sp="sealed/pkg_synergyfinder_NCATS_screening_data.sealed.csv"; tr.to_csv(sp,index=False)
info=dict(path=sp,sha256=hashlib.sha256(open(sp,'rb').read()).hexdigest(),rows=len(tr),
  triple_dose_tuples_per_block=tr.groupby('block_id').size().to_dict(),
  drugs=tr.groupby('block_id')[['drug1','drug2','drug3']].first().to_dict('index'))
del tr
for c in cc: info[c+'_levels']=sorted(d[c].unique().tolist())
cal=d[d.n_drugs<=2].copy(); cal.to_csv("work/pkg/ncats_singles_pairs.csv",index=False)
info={k:({str(a):b for a,b in v.items()} if isinstance(v,dict) else v) for k,v in info.items()}; print(json.dumps(info,default=str,indent=1)); json.dump(info,open('work/pkg/ncats_seal.json','w'),default=str,indent=1)
for b,g in cal.groupby('block_id'):
    z=g[g.n_drugs==0].response
    for k,lab in [(1,'single'),(2,'pair')]:
        s=g[g.n_drugs==k]
        for c in cc if k==1 else []:
            ss=s[s[c]>0]; print(b,'single',c,g.loc[ss.index,'drug'+c[-1]].iloc[0],'n',len(ss),'resp min/max',ss.response.min(),ss.response.max())
        if k==2:
            for a,bb in [('conc1','conc2'),('conc1','conc3'),('conc2','conc3')]:
                ss=s[(s[a]>0)&(s[bb]>0)]; print(b,'pair',a,bb,'n',len(ss),'resp min/max',ss.response.min(),ss.response.max())
    print(b,'control',z.tolist())
