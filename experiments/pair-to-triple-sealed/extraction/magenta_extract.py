import pandas as pd, numpy as np, hashlib, json, os
R="/tmp/claude-0/stage1/triples/raw/"; S="/tmp/claude-0/stage1/triples/sealed/"; W="/tmp/claude-0/stage1/triples/work/"
def sha(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()
out={}
# --- raw DiaMOND-style plates: triplets
x=pd.ExcelFile(R+"sriram_MAGENTA/data/Ecoli-triplets.xlsx")
drugs=x.parse('drugs'); dmap=dict(zip(drugs['drug#'],drugs['drug name']))
cal=[]; sealed=[]; trip_ids=[]
for s in ['Plate1','Plate2','Plate3','Plate4']:
    d=x.parse(s,header=None)
    for i in range(1,len(d)):
        ids=[int(v) for v in d.iloc[i,:3] if not pd.isna(v)]
        vals=d.iloc[i,3:].astype(float).values
        rec=dict(plate=s,row=i,drugs='+'.join(str(k) for k in ids),n_drugs=len(ids))
        if len(ids)<=2:
            for j,v in enumerate(vals): cal.append(dict(rec,dose_step=j,od=v))
        else:
            trip_ids.append(tuple(ids))
            for j,v in enumerate(vals): sealed.append(dict(rec,dose_step=j,od=v))
nsteps=len(vals)
pd.DataFrame(cal).to_csv(W+"magenta_triplet_plates_singles.csv",index=False)
sp=S+"magenta_cokol2018_triplet_plates.sealed.csv"; pd.DataFrame(sealed).to_csv(sp,index=False)
out['triplet_plates']=dict(path=sp,sha256=sha(sp),rows=len(sealed),n_triples=len(set(trip_ids)),dose_steps=nsteps)
del sealed
# --- triple score sheets (seal whole sheet)
for f,sh,tag in [("sriram_MAGENTA/data/Ecoli-triplets.xlsx","inx_scores","magenta_triplets_inx_scores"),
                 ("sriram_MAGENTA/data/MAGENTA_supplementary_dataset.xlsx","triplet predictions","magenta_suppl_triplet_predictions"),
                 ("sriram_CARAMeL/data/ecoli_interactions.xlsx","MAGENTA_triplet","caramel_MAGENTA_triplet")]:
    d=pd.read_excel(R+f,sheet_name=sh); p=S+tag+".sealed.csv"; d.to_csv(p,index=False); out[tag]=dict(path=p,sha256=sha(p),rows=len(d)); del d
# rows of order>=3 in mixed sheets
def seal_mixed(f,sh,idcols,tag,header=0):
    d=pd.read_excel(R+f,sheet_name=sh,header=header)
    ids=d[idcols].astype(str).replace({'nan':np.nan,'NaN':np.nan})
    k=ids.notna().sum(1); hi=d[k>=3]; p=S+tag+".sealed.csv"; hi.to_csv(p,index=False)
    lo=d[k<3]; lo.to_csv(W+tag+"_order_le2.csv",index=False)
    out[tag]=dict(path=p,sha256=sha(p),rows_order_ge3=len(hi),rows_order_le2=len(lo),order_counts=k.value_counts().sort_index().to_dict()); del d,hi
seal_mixed("sriram_CARAMeL/data/ecoli_interactions.xlsx","Russ_2018",[f"Drug_{i}" for i in range(1,10)],"caramel_Russ2018")
seal_mixed("sriram_CARAMeL/data/mtb_interactions.xlsx","data",[f"Drug_{i}" for i in range(1,6)],"caramel_mtb")
for sh in ['Katzir','Russ','Cokol']:
    seal_mixed("sriram_M2D2/M2D2_stage2ML_traintest/drugInteractions/drugInteractions_allsources.xlsx",sh,[0,1,2],"m2d2_"+sh,header=None)
json.dump(out,open(W+"sealed_manifest_magenta_etc.json","w"),indent=1,default=str)
print(json.dumps(out,indent=1,default=str))
