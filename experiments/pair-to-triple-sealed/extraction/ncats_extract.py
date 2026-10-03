import rdata, pandas as pd, numpy as np, hashlib, json
p="/tmp/claude-0/stage1/triples/raw/bioc_synergyfinder/data/NCATS_screening_data.rda"
d=list(rdata.read_rda(p).values())[0]
d=pd.DataFrame(d)
print('columns',list(d.columns),'rows',len(d))
for c in ['drug1','drug2','drug3','conc_unit1','conc_unit2','conc_unit3','block_id']: print(c, d[c].unique()[:10])
for b,g in d.groupby('block_id'):
    print('block',b,'rows',len(g),{c: sorted(g[c].unique().tolist()) for c in ['conc1','conc2','conc3']})
nz=(d[['conc1','conc2','conc3']]>0).sum(1)
d['n_drugs']=nz
print('order counts', d.groupby(['block_id','n_drugs']).size().to_dict())
# replicates: duplicates of conc tuple
dup=d.groupby(['block_id','conc1','conc2','conc3']).size()
print('obs per dose-tuple', dup.value_counts().to_dict())
cal=d[d.n_drugs<=2]; cal.to_csv("/tmp/claude-0/stage1/triples/work/ncats_tact_singles_pairs.csv",index=False)
tr=d[d.n_drugs==3]; sp="/tmp/claude-0/stage1/triples/sealed/ncats_malaria_tact_synergyfinder.sealed.csv"; tr.to_csv(sp,index=False)
print(json.dumps(dict(path=sp,sha256=hashlib.sha256(open(sp,'rb').read()).hexdigest(),rows=len(tr))))
del tr
# calibration summary
for b,g in cal.groupby('block_id'):
    s=g[g.n_drugs==1]; pr=g[g.n_drugs==2]; z=g[g.n_drugs==0]
    print('block',b,'control rows',len(z),'control resp',z.response.round(2).tolist()[:6],'| single resp range',round(s.response.min(),2),round(s.response.max(),2),'| pair resp range',round(pr.response.min(),2),round(pr.response.max(),2), 'n singles',len(s),'n pairs',len(pr))
