# Extract singles+pairs (calibration) and seal triples (and higher) for Lozano-Huntelman 2021 data.
import pandas as pd, numpy as np, glob, os, re, hashlib, itertools, json
base="/tmp/claude-0/stage1/triples/raw/raphael_chimeric-epistasis/drug_data/Lozano-HuntelmanEtAl2021"
gdir=base+"/Raw Data and Growth Rate/Raw Data/Final_data_growthrates"
calib=[]; sealed=[]; trip_ids=set(); n_trip_obs=0
for f in sorted(glob.glob(gdir+"/*.csv")):
    d=pd.read_csv(f,header=None,dtype=str)
    lab=d[0].fillna('')
    starts=list(lab[lab.str.match(r'^[A-Z]{3}\d')].index)
    hdr=list(d.iloc[0,1:])
    for s in starts:
        combo=lab[s]; doses=dict(re.findall(r'([A-Z]{3})(\d)',combo))
        block=d.iloc[s+1:s+5,1:]
        assert list(d.iloc[s,1:])==hdr
        for j,cond in enumerate(hdr):
            drugs=cond.split('+')
            vals=pd.to_numeric(block.iloc[:,j],errors='coerce').values
            key=dict(file=os.path.basename(f),block_label=combo,condition='+'.join(f"{x}{doses[x]}" for x in drugs),n_drugs=len(drugs))
            for r,v in enumerate(vals):
                row=dict(key,rep=r+1,value=v)
                if len(drugs)<=2: calib.append(row)
                else:
                    sealed.append(row)
                    if len(drugs)==3: trip_ids.add(key['condition']); n_trip_obs+=1
cal=pd.DataFrame(calib); cal.to_csv("/tmp/claude-0/stage1/triples/work/lozano2021_singles_pairs.csv",index=False)
os.makedirs("/tmp/claude-0/stage1/triples/sealed",exist_ok=True)
sp="/tmp/claude-0/stage1/triples/sealed/lozano_huntelman2021.sealed.csv"
pd.DataFrame(sealed).to_csv(sp,index=False)
# also seal summary 3/4/5-drug tables
extra={}
for fn in ['3Drug.xlsx','4Drugs.xlsx','5Drug.xlsx']:
    x=pd.read_excel(base+"/Python Data and Code/"+fn)
    out=f"/tmp/claude-0/stage1/triples/sealed/lozano_huntelman2021_{fn.split('.')[0]}_summary.sealed.csv"
    x.to_csv(out,index=False); extra[fn]=(len(x),hashlib.sha256(open(out,'rb').read()).hexdigest(),out)
    if fn=='3Drug.xlsx':
        ids3=set(tuple(sorted(r)) for r in x[['Drug-A','Drug-B','Drug-C']].values.tolist())
        n3drugsets=len(set(tuple(sorted(re.sub(r'\d','',a) for a in t)) for t in ids3))
    del x
h=hashlib.sha256(open(sp,'rb').read()).hexdigest()
nsealed=len(sealed); del sealed
dsets=set(tuple(sorted(re.sub(r'\d','',a) for a in c.split('+'))) for c in trip_ids)
print(json.dumps(dict(sealed_path=sp,sha256=h,n_sealed_rows_all_orders=nsealed,n_triple_obs=n_trip_obs,
  n_unique_triple_dose_conditions=len(trip_ids),n_triple_drug_sets=len(dsets),
  summary_files={k:dict(rows=v[0],sha256=v[1],path=v[2]) for k,v in extra.items()},
  summary_3drug_unique_conditions=len(ids3),summary_3drug_drugsets=n3drugsets),indent=1))
