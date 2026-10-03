import rdata, numpy as np, pandas as pd, hashlib, json
base="raw/pkg_cran_mixtox/data/"
out={}
for ds in ['antibiotox','cytotox']:
    obj=list(rdata.read_rda(base+ds+'.rda').values())[0]
    keys=list(obj.keys()); info={'keys':keys}
    pct={k:obj[k] for k in keys if k.endswith('pct')}
    for k,v in pct.items():
        a=np.asarray(v); info[k+'_shape']=a.shape
        info[k+'_n_nonzero_components_per_mix']=(a>0).sum(axis=1).tolist() if a.ndim==2 else None
        try: info[k+'_dimnames']=[list(map(str,x)) if x is not None else None for x in v.attrs['dimnames']] if hasattr(v,'attrs') else None
        except Exception as e: info[k+'_dimnames']=str(e)
    rows=[];
    for k in keys:
        v=obj[k]
        if isinstance(v,dict) and 'x' in v and 'y' in v:
            typ=str(np.asarray(v['type']).ravel()[0]) if 'type' in v else '?'
            x=np.asarray(v['x'],float).ravel(); y=np.asarray(v['y'],float)
            if y.ndim==1: y=y.reshape(len(x),-1)
            for i,xi in enumerate(x):
                for j in range(y.shape[1]):
                    rows.append(dict(dataset=ds,substance=k,type=typ,conc=xi,rep=j+1,resp=y[i,j]))
            info.setdefault('substances',{})[k]=dict(type=typ,n_conc=len(x),n_rep=int(y.shape[1]))
    d=pd.DataFrame(rows)
    mix=d[d.type.str.contains('mix',case=False)|d.substance.str.contains('mix|udcr|eecr|U[0-9]|E[0-9]',case=False)]
    sp=f"sealed/pkg_mixtox_{ds}_mixtures.sealed.csv"; mix.to_csv(sp,index=False)
    info['sealed']=dict(path=sp,sha256=hashlib.sha256(open(sp,'rb').read()).hexdigest(),rows=len(mix),substances=sorted(mix.substance.unique().tolist()))
    sg=d.drop(mix.index); sg.to_csv(f"work/pkg/mixtox_{ds}_singles.csv",index=False)
    info['single_resp_range']={s:[float(g.resp.min()),float(g.resp.max())] for s,g in sg.groupby('substance')}
    del mix
    out[ds]=info
print(json.dumps(out,indent=1,default=str)); json.dump(out,open('work/pkg/mixtox_seal.json','w'),indent=1,default=str)
