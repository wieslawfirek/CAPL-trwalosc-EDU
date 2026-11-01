"""Stroop associations on a locally prepared long CSV; no raw data are published."""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from .data import load,supplemental_sample
from .robust import robust,holm

VARIABLES=['AR','CAMSA_sur','PACER_odcinki']
TESTS=['KZ','KN','KN_minus_KZ']

def within(z,v,t,reps,rng):
    z=z.dropna(subset=[v,t]).copy()
    sizes=z.groupby('class_id').size()
    z=z[z.class_id.isin(sizes[sizes>=2].index)].copy()
    x=z[v]-z.groupby('class_id')[v].transform('mean')
    y=z[t]-z.groupby('class_id')[t].transform('mean')
    z['xx']=x*x;z['yy']=y*y;z['xy']=x*y
    z['stratum']=np.where(z.group=='GN','GN','GE_GK')
    c=z.groupby('class_id').agg(xx=('xx','sum'),yy=('yy','sum'),xy=('xy','sum'),stratum=('stratum','first'))
    if len(c)<3 or c.xx.sum()<=0 or c.yy.sum()<=0:raise ValueError('Insufficient within-class variation')
    weights=np.zeros((reps,len(c)))
    for _,g in c.groupby('stratum'):
        ix=c.index.get_indexer(g.index);m=len(ix)
        weights[:,ix]=rng.multinomial(m,np.full(m,1/m),size=reps)
    vals=(weights@c.xy.to_numpy())/np.sqrt((weights@c.xx.to_numpy())*(weights@c.yy.to_numpy()))
    if not np.isfinite(vals).all():raise ValueError('Degenerate class bootstrap')
    lo,hi=np.quantile(vals,[.025,.975])
    alpha=.05/9;simlo,simhi=np.quantile(vals,[alpha/2,1-alpha/2])
    return dict(variable=v,test=t,n=len(z),classes=len(c),r=float(c.xy.sum()/np.sqrt(c.xx.sum()*c.yy.sum())),lo=float(lo),hi=float(hi),sim_lo=float(simlo),sim_hi=float(simhi),significant_bonferroni=bool(simlo>0 or simhi<0),bootstrap=reps)

def analyze(d,reps=5000,within_reps=20000,quick=False):
    year=d[d.time==3].copy()
    if 'AR_stroop' in year:year['AR']=pd.to_numeric(year['AR_stroop'],errors='raise').replace(-999,np.nan)
    for c in ['KZ','KN']:
        if c not in year:raise ValueError('Missing Stroop column: '+c)
        year[c]=pd.to_numeric(year[c],errors='raise').replace(-999,np.nan)
        year.loc[(year[c]<0)|~np.isfinite(year[c]),c]=np.nan
    year['KN_minus_KZ']=year.KN-year.KZ
    rows=[];rng=np.random.default_rng(20261029)
    for v in VARIABLES:
        for t in TESTS:
            z=year.dropna(subset=[v,t]);x=z[v].to_numpy();y=z[t].to_numpy();cl=z.class_id.to_numpy(dtype=str)
            if len(z)<4 or len(set(cl))<3 or np.std(x)==0 or np.std(y)==0:raise ValueError('Insufficient variation/classes')
            rho,p=stats.spearmanr(x,y)
            ranks=np.column_stack([stats.rankdata(x),stats.rankdata(y)])
            ranks=(ranks-ranks.mean(axis=0))/ranks.std(axis=0,ddof=1)
            inf=robust(np.column_stack([np.ones(len(z)),ranks[:,0]]),ranks[:,1],cl)['inference'][1]
            if not np.isclose(rho,inf['estimate'],atol=1e-10):raise ArithmeticError('Rank regression disagrees with rho')
            blocks=[np.flatnonzero(cl==c) for c in np.unique(cl)]
            for mode in ['independent','CR2']:
                b=reps if mode=='independent' or v!='AR' else (reps if quick else 3000)
                boot=[]
                for _ in range(b):
                    ix=rng.integers(0,len(z),len(z)) if mode=='independent' else np.concatenate([blocks[i] for i in rng.integers(0,len(blocks),len(blocks))])
                    boot.append(stats.spearmanr(x[ix],y[ix]).statistic)
                if not np.isfinite(boot).all():raise ValueError('Degenerate bootstrap')
                lo,hi=np.quantile(boot,[.025,.975])
                rows.append(dict(variable=v,test=t,mode=mode,n=len(z),classes=len(blocks),rho=float(rho),p=float(p if mode=='independent' else inf['p']),lo=float(lo),hi=float(hi),bootstrap=b))
    for mode in ['independent','CR2']:
        sub=[r for r in rows if r['mode']==mode]
        for r,p in zip(sub,holm([r['p'] for r in sub])):r['p_holm']=float(p)
    sd=year;omitted=0;rng=np.random.default_rng(20261031)
    w=[within(sd,v,t,within_reps,rng) for v in VARIABLES for t in TESTS]
    return dict(spearman=rows,within=w,omitted_ambiguous_students=omitted,note='95% nominal CI; within-class simultaneous CI 1-0.05/9; bootstrap estimates can vary with seed/order')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--quick',action='store_true')
    args=ap.parse_args();d,audit=load(args.input)
    result=analyze(d,100 if args.quick else 5000,100 if args.quick else 20000,args.quick)
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'stroop.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    for key in ['spearman','within']:pd.DataFrame(result[key]).to_csv(args.output/('stroop_'+key+'.csv'),index=False)
if __name__=='__main__':main()
