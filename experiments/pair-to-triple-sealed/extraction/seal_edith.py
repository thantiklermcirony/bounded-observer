import openpyxl, pandas as pd, numpy as np, hashlib, json
p="raw/pkg_mathilde-robin_EDITH/inst/extdata/3drugs.xlsx"
wb=openpyxl.load_workbook(p,data_only=True)
recs=[]; struct={}
for ws in wb.worksheets:
    rows=[list(r) for r in ws.iter_rows(values_only=True)]
    while rows and all(v in (None,'',' ') for v in rows[-1]): rows.pop()
    names=[str(rows[0][i]) for i in range(3)]
    body=rows[1:]
    blocks=[];cur=[]
    for r in body:
        if all(v in (None,'',' ') for v in r):
            if cur: blocks.append(cur); cur=[]
        else: cur.append(r)
    if cur: blocks.append(cur)
    blocks=[b for b in blocks if len(b)>=4]
    struct[ws.title]=dict(drugs=names,n_rows=len(rows),n_cols=max(len(r) for r in rows),n_blocks=len(blocks))
    for rep,b in enumerate(blocks,1):
        ncol=max(i for i,v in enumerate(b[0]) if v not in (None,''))+1  # header width
        last=max(max(i for i,v in enumerate(r) if v not in (None,'')) for r in b[1:])
        bconc=[float(v) for v in b[0][1:last]]
        for r in b[1:]:
            a=float(r[0]); c=float(r[last])
            for j,bc in enumerate(bconc):
                v=r[1+j]
                recs.append(dict(sheet=ws.title,replicate=rep,drugA=names[0],drugB=names[1],drugC=names[2],concA=a,concB=bc,concC=c,viability=(float(v) if v not in (None,'') else np.nan)))
d=pd.DataFrame(recs); d['n_drugs']=(d[['concA','concB','concC']]>0).sum(axis=1)
tr=d[d.n_drugs>=3]; sp="sealed/pkg_EDITH_3drugs.sealed.csv"; tr.to_csv(sp,index=False)
info=dict(struct=struct,path=sp,sha256=hashlib.sha256(open(sp,'rb').read()).hexdigest(),triple_rows=len(tr),
  triple_dose_tuples=int(tr[['sheet','concA','concB','concC']].drop_duplicates().shape[0]),
  triple_missing=int(tr.viability.isna().sum()))
del tr
info['order_counts']=d.n_drugs.value_counts().sort_index().to_dict()
info['levels']={c:sorted(d[c].unique().tolist()) for c in ['concA','concB','concC']}
info['reps_per_sheet']=d.groupby('sheet').replicate.nunique().to_dict()
info={k:({str(a):b for a,b in v.items()} if isinstance(v,dict) else v) for k,v in info.items()}
print(json.dumps(info,indent=1,default=str)); json.dump(info,open('work/pkg/edith_seal.json','w'),indent=1,default=str)
cal=d[d.n_drugs<=2]; cal.to_csv('work/pkg/edith_singles_pairs.csv',index=False)
for (s,rep),g in cal.groupby(['sheet','replicate']):
    z=g[g.n_drugs==0].viability
    out=[f'{s} rep{rep} ctrl n={len(z)} {z.round(1).tolist()}']
    for c in ['concA','concB','concC']:
        x=g[(g.n_drugs==1)&(g[c]>0)].viability; out.append(f'single {c}: n={len(x)} min={x.min():.1f} max={x.max():.1f}')
    for a,b in [('concA','concB'),('concA','concC'),('concB','concC')]:
        x=g[(g.n_drugs==2)&(g[a]>0)&(g[b]>0)].viability; out.append(f'pair {a}{b}: n={len(x)} min={x.min():.1f} max={x.max():.1f}')
    print(' | '.join(out))
