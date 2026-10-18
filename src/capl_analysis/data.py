"""Canonical long CSV input and deterministic validation, without imputation."""
from pathlib import Path
import numpy as np
import pandas as pd

VARIABLES = ['AR','PC','DB','MC','KU','CAMSA_sur','Plank_time','PACER_odcinki','StepCount']
TESTS = ['EDU_Matematyka_wynik','EDU_Polski_wynik']
META = ['id','group','school','class_id','center','sex']
MAXIMUM = dict(AR=100,PC=30,DB=30,MC=30,KU=10,CAMSA_sur=28)
LABELS = dict(AR='Alfabetyzacja ruchowa',PC='Kompetencje fizyczne',DB='Zachowania codzienne',MC='Motywacja i pewność siebie',KU='Wiedza i zrozumienie',CAMSA_sur='CAMSA',Plank_time='Plank',PACER_odcinki='Beep test',StepCount='Liczba kroków',EDU_Matematyka_wynik='Matematyka',EDU_Polski_wynik='Język polski')

def load(path):
    d=pd.read_csv(path,dtype={c:'string' for c in META},keep_default_na=True,float_precision="round_trip")
    needed=META+['time','age_year']+VARIABLES+TESTS
    if set(needed)-set(d):raise ValueError('Missing columns: '+', '.join(sorted(set(needed)-set(d))))
    if d[['id','group','school','class_id','center']].isna().any().any():raise ValueError('Missing identifiers or group')
    if d.duplicated(['id','time']).any():raise ValueError('Duplicate student/time')
    if not d.group.isin(['GE','GK','GN']).all():raise ValueError('Groups must be GE/GK/GN')
    if not d.time.isin([1,2,3]).all():raise ValueError('time must be 1,2,3')
    if ((d.group=='GN') & (d.time!=3)).any():raise ValueError('GN must have time=3 only')
    if not d.sex.dropna().isin(['F','M']).all():raise ValueError('sex must be F/M/blank')
    for c in META[1:]:
        if (d.groupby('id')[c].nunique(dropna=True)>1).any():raise ValueError('Inconsistent student metadata: '+c)
    for c in ['school','center']:
        if (d.groupby('class_id')[c].nunique()>1).any():raise ValueError('Class IDs must be globally unique')
    if (d.groupby('school').center.nunique()>1).any():raise ValueError('School spans centers')
    audit={'rows':len(d),'students':d.id.nunique(),'missing_code':-999,'invalid_replaced':{},'AR_incomplete_removed':0}
    for c in VARIABLES+TESTS+['age_year']:
        d[c]=pd.to_numeric(d[c],errors='raise').replace(-999,np.nan)
        hi=18 if c in TESTS else MAXIMUM.get(c,np.inf)
        invalid=d[c].notna() & ((d[c]<0)|(d[c]>hi)|~np.isfinite(d[c]))
        audit['invalid_replaced'][c]=int(invalid.sum());d.loc[invalid,c]=np.nan
    if d.loc[d.time!=3,TESTS].notna().any().any():raise ValueError('EDU belongs to time=3, not repeated outcomes')
    incomplete=d.AR.notna() & d[['PC','DB','MC','KU']].isna().any(axis=1)
    audit['AR_incomplete_removed']=int(incomplete.sum());d.loc[incomplete,'AR']=np.nan
    good=d.AR.notna();diff=abs(d.loc[good,'AR']-d.loc[good,['PC','DB','MC','KU']].sum(axis=1))
    if (diff>.051).any():raise ValueError('AR does not equal the sum of domains within rounding tolerance')
    mixed=d.groupby('class_id').group.nunique();audit['mixed_group_classes']=int((mixed>1).sum())
    return d,audit

def wide(d):
    meta=d[META].drop_duplicates('id').rename(columns={'class_id':'class'})
    w=d.pivot(index='id',columns='time',values=VARIABLES).reindex(columns=pd.MultiIndex.from_product([VARIABLES,[1,2,3]]))
    w.columns=[f'{v}_{t}' for v,t in w.columns]
    return meta.merge(w.reset_index(),on='id',validate='one_to_one')

def supplemental_sample(d):
    """Match documented supplemental policy: omit minority group records in mixed classes."""
    remove=set()
    for _,z in d[['id','class_id','group']].drop_duplicates().groupby('class_id'):
        counts=z.group.value_counts()
        if len(counts)>1:
            if counts.iloc[0]==counts.iloc[1]:raise ValueError('Mixed class has tied groups: resolve locally')
            remove.update(z.loc[z.group!=counts.index[0],'id'])
    return d.loc[~d.id.isin(remove)].copy(),len(remove)

def demographics(d):
    active=d.loc[d[VARIABLES].notna().any(axis=1)].copy();out={}
    for name,keys in [('group_sex',['time','group']),('center_sex',['time','center'])]:
        rows=[]
        for key,z in active.groupby(keys):
            rows.append(dict(zip(keys,key),n=z.id.nunique(),girls=int((z.sex=='F').sum()),boys=int((z.sex=='M').sum()),sex_missing=int(z.sex.isna().sum())))
        out[name]=pd.DataFrame(rows)
    rows=[]
    for g,z in d.groupby('group'):
        for v in VARIABLES:
            a=z.pivot(index='id',columns='time',values=v).reindex(columns=[1,2,3])
            rows.append(dict(group=g,variable=v,pre=int(a[1].notna().sum()),post=int(a[2].notna().sum()),year=int(a[3].notna().sum()),complete3=int(a.notna().all(axis=1).sum())))
    out['outcome_counts']=pd.DataFrame(rows)
    out['descriptive']=d.melt(id_vars=['id','time','group'],value_vars=VARIABLES,var_name='variable',value_name='value').groupby(['group','time','variable']).value.agg(n='count',mean='mean',sd='std',median='median').reset_index()
    a=active.loc[active.time==3]
    out['age_year']=a.groupby('group').age_year.agg(n='count',mean='mean',sd='std',min='min',max='max').reset_index()
    return out
