import pandas as pd, numpy as np, hashlib, json, os
base='/tmp/claude-0/stage1/triples/raw/bg_NIEHS_RGCA/inst/extdata/'
SE='/tmp/claude-0/stage1/triples/sealed/'; WK='/tmp/claude-0/stage1/triples/work/bg/'
g=pd.read_excel(base+'AllMixtureComponentsARER.xls')
names=g.iloc[69].to_dict()
g=g[g['CAS'].astype(str).str.startswith('NOCAS')].copy()
chemcols=[c for c in g.columns if c not in ('Mixture name','CAS','Description')]
g['ncomp']=(g[chemcols].apply(pd.to_numeric,errors='coerce').fillna(0)>0).sum(axis=1)
print('mixtures by #components:', g['ncomp'].value_counts().sort_index().to_dict())
mixcas=dict(zip(g['CAS'],g['ncomp']))
man={'chem_names':{k:names[k] for k in chemcols},'guide_rows':len(g),'ncomp_counts':{int(k):int(v) for k,v in g['ncomp'].value_counts().items()},'n_chemicals':len(chemcols)}
sealed=[];calib=[]
for a in ['AR-bla','AR-luc','ER-bla','ER-luc']:
    d=pd.read_csv(base+a+'.txt',sep='\t')
    d['ncomp']=d['CAS'].map(lambda c: mixcas.get(c,1))
    ismix_unknown=d['CAS'].astype(str).str.startswith('NOCAS') & ~d['CAS'].isin(mixcas.keys())
    hi=d[(d['ncomp']>=3)|ismix_unknown]; lo=d[~((d['ncomp']>=3)|ismix_unknown)]
    hi=hi.assign(file=a); lo=lo.assign(file=a)
    sealed.append(hi); calib.append(lo)
    concs=[c for c in d.columns if c.startswith('CONC')]
    man[a]={'rows':len(d),'rows_ncomp_ge3':len(hi),'rows_unknown_nocas':int(ismix_unknown.sum()),
            'rows_single':int((lo['ncomp']==1).sum()),'rows_pair':int((lo['ncomp']==2).sum()),
            'n_conc_points':len(concs),'n_single_chems':int(lo.loc[lo.ncomp==1,'CAS'].nunique()),
            'n_mix_ge3':int(hi['CAS'].nunique()),'n_pair_mix':int(lo.loc[lo.ncomp==2,'CAS'].nunique()),
            'replicatesets_per_sample':lo.groupby('CAS')['ReplicateSet'].nunique().describe().to_dict()}
S=pd.concat(sealed); out=SE+'bg_tox21_RGCA_ARER_mixtures.sealed.csv'; S.to_csv(out,index=False)
man['sealed_path']=out; man['sha256']=hashlib.sha256(open(out,'rb').read()).hexdigest()
man['sealed_mixture_ids']=sorted(S['CAS'].unique().tolist())
C=pd.concat(calib); C.to_csv(WK+'tox21_RGCA_singles_pairs.csv',index=False)
# record doses of sealed rows (no responses)
man['sealed_conc_range']={k:[float(np.nanmin(S[[c for c in S.columns if c.startswith('CONC')]].values)),float(np.nanmax(S[[c for c in S.columns if c.startswith('CONC')]].values))] for k in ['all']}
del S,sealed
json.dump(man,open(WK+'seal_rgca.json','w'),indent=1,default=str)
print(json.dumps({k:v for k,v in man.items() if k!='sealed_mixture_ids'},indent=1,default=str))
