import pandas as pd, numpy as np, hashlib, json, shutil
R='/tmp/claude-0/stage1/triples/raw/bg_SvL-1_mixdra/'; SE='/tmp/claude-0/stage1/triples/sealed/'
d=pd.read_csv(R+'inst/extdata/ternary_ca_fbsa_cpf_imi_continuous.csv')
order=(d[['C1','C2','C3']]>0).sum(axis=1)
T=d[order>=3]; C=d[order<3]
out=SE+'bg_mixdra_vanloon2025_exp1_ternary.sealed.csv'; T.to_csv(out,index=False)
man={'source':'SvL-1/mixdra inst/extdata/ternary_ca_fbsa_cpf_imi_continuous.csv (C1=CPF,C2=FBSA,C3=IMI per oracle labels ec50_1=CPF, ec50_2=FBSA, ec50_3=IMI)',
 'rows':len(d),'order_counts':{int(k):int(v) for k,v in order.value_counts().items()},
 'sealed_path':out,'sha256':hashlib.sha256(open(out,'rb').read()).hexdigest()}
# triple doses only
td=T[['C1','C2','C3']].copy(); tot=td.sum(axis=1)
man['ternary_dose_tuples']=int(td.drop_duplicates().shape[0])
man['ternary_ratio_sets']=sorted({tuple(np.round(r/r.sum(),3)) for r in td.values},key=str)
man['ternary_reps_per_tuple']=td.groupby(['C1','C2','C3']).size().value_counts().to_dict()
# calibration structure
man['single_levels']={c:sorted(C.loc[(C[['C1','C2','C3']]>0).sum(axis=1)==1,c].unique().tolist()) for c in ['C1','C2','C3']}
pairs=C[(C[['C1','C2','C3']]>0).sum(axis=1)==2]
man['pair_rows']=len(pairs); man['pair_tuples']=int(pairs[['C1','C2','C3']].drop_duplicates().shape[0])
man['controls']=int((order==0).sum())
C.to_csv('mixdra_exp1_singles_pairs.csv',index=False)
del T,td
b=pd.read_csv(R+'inst/extdata/binary_ca_cpf_imi_fbsa_continuous.csv'); man['binary_file_rows']=len(b); man['binary_file_order_counts']={int(k):int(v) for k,v in (b[['C1','C2']]>0).sum(axis=1).value_counts().items()}
# workbook contains ternary data + fits: copy to sealed without reading values
wb=SE+'bg_mixdra_FBSA_CPF_IMI_ternary_workbook.sealed.xls'; shutil.copy(R+'FBSA CPF IMI ternary -simplified.xls',wb)
man['workbook_sealed']=wb; man['workbook_sha256']=hashlib.sha256(open(wb,'rb').read()).hexdigest()
man['oracles_note']='inst/validation/oracles.csv rows for ternary_fbsa_cpf_imi stage overall (objective on all 419 rows) is ternary-outcome-derived: values NOT read'
json.dump(man,open('seal_mixdra.json','w'),indent=1,default=str); print(json.dumps(man,indent=1,default=str))
