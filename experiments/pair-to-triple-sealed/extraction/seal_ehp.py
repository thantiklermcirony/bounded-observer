import pandas as pd, hashlib, json
R='/tmp/claude-0/stage1/triples/raw/bg_nanhung_EHP7600/datasets/'
m=pd.read_csv(R+'mixture_data.csv')
out='/tmp/claude-0/stage1/triples/sealed/bg_EHP7600_mixtures.sealed.csv'
m.to_csv(out,index=False)
info=pd.read_csv(R+'mixture_info.csv')
man={'sealed_path':out,'sha256':hashlib.sha256(open(out,'rb').read()).hexdigest(),'rows':len(m),
 'mixtures':sorted(m['mixture'].astype(str).unique().tolist()),
 'dilutions':sorted(m['Dilution'].astype(str).unique().tolist()),
 'replications':sorted(m['Replication'].astype(str).unique().tolist()),
 'celltypes':sorted(m['celltype'].unique().tolist()),'n_phenotypes':int(m['phenotype'].nunique()),
 'n_components_nonzero_per_mixture_column':{c:int((pd.to_numeric(info[c],errors='coerce')>0).sum()) for c in info.columns if c not in('Chemical','Class')}}
del m
c=pd.read_csv(R+'chem_data.csv')
man['singles']={'rows':len(c),'n_chem':int(c['chemical'].nunique()),'n_conc':int(c['Concentration'].nunique()),'reps':sorted(c['Replication'].astype(str).unique().tolist()),'celltypes':sorted(c['celltype'].unique().tolist()),'n_phenotypes':int(c['phenotype'].nunique())}
json.dump(man,open('seal_ehp.json','w'),indent=1); print(json.dumps(man,indent=1))
