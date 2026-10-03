import pandas as pd, numpy as np, hashlib, json, openpyxl
R='/tmp/claude-0/stage1/triples/raw/bg_Fazmin_Triple-Synergy-Plot-3D/'
rows=[]; man={}
for f in ['ndmKPC.csv','ndmKPC_2.csv','ndmCTX.csv','ndmCTX_2.csv','3drug.csv','3ddata.csv']:
    d=pd.read_csv(R+f,encoding='latin1'); cols=d.columns[1:4]
    X=d[cols].apply(pd.to_numeric,errors='coerce')
    order=(X.fillna(0)>0).sum(axis=1)
    man[f]={'rows':len(d),'cols':[str(c) for c in d.columns],'n_nonzero_coord_counts':{int(k):int(v) for k,v in order.value_counts().items()}}
    d=d.astype(str); d.insert(0,'file',f); rows.append(d)
for f in ['3D data for Faz 030816.xlsx','3D data for Faz 080816.xlsx']:
    wb=openpyxl.load_workbook(R+f,data_only=True)
    for ws in wb.worksheets:
        vals=[[c.value for c in r] for r in ws.iter_rows()]
        if len(vals)<4: continue
        d=pd.DataFrame(vals[3:],columns=['c1','c2','c3']); X=d.apply(pd.to_numeric,errors='coerce')
        order=(X.fillna(0)>0).sum(axis=1)
        man[f+'::'+ws.title]={'rows':len(d),'n_nonzero_coord_counts':{int(k):int(v) for k,v in order.value_counts().items()}}
        d=d.astype(str); d.insert(0,'file',f+'::'+ws.title); rows.append(d)
S=pd.concat(rows,ignore_index=True)
out='/tmp/claude-0/stage1/triples/sealed/bg_fazmin_3D_checkerboard_isosurface.sealed.csv'; S.to_csv(out,index=False)
man['sealed_path']=out; man['sha256']=hashlib.sha256(open(out,'rb').read()).hexdigest()
man['note']='files contain only (meropenem, avibactam, AMA) coordinates; no response column -> coordinates presumed to be inhibitory/isosurface points (outcome-bearing), so all sealed'
del S,rows
json.dump(man,open('seal_fazmin.json','w'),indent=1); print(json.dumps(man,indent=1))
