"""ANOVA ICC and within-class Pearson, whole-class/school stratified bootstrap.

Original numerical definitions retained; no student records or local paths.
"""
import numpy as np
import pandas as pd
from scipy import stats

def run(data, replicates=20000, seed=20261016):
    global B, rng
    B=replicates
    rng=np.random.default_rng(seed)
    variables=['AR','PC','DB','MC','KU']
    tests=['EDU_Matematyka_wynik','EDU_Polski_wynik']
    return {'icc':[icc(data,v) for v in tests+variables],
            'within':[assoc(data,v,t) for t in tests for v in variables]}

def weights(c,unit):
 # Resample whole classes or whole schools, preserving the number of units in each cohort stratum.
 units=c[unit].unique();u=pd.DataFrame({unit:units}).merge(c[[unit,'stratum']].drop_duplicates(),on=unit);assert not u[unit].duplicated().any()
 A=np.zeros((B,len(c)))
 for s,z in u.groupby('stratum'):
  names=z[unit].values;m=len(names);draw=rng.multinomial(m,np.full(m,1/m),size=B)
  for j,name in enumerate(names):A[:,np.flatnonzero(c[unit].values==name)]=draw[:,j,None]
 return A

def icc_calc(n,s,q,w):
 N=w@n;K=w.sum(axis=-1);total=w@s;ssw=w@(q-s*s/n);ssb=w@(s*s/n)-total*total/N
 msw=ssw/(N-K);msb=ssb/(K-1);n0=(N-(w@(n*n))/N)/(K-1);between=(msb-msw)/n0;raw=between/(between+msw)
 return np.maximum(0,raw),raw,between,msw

def icc(data,v):
 z=data.dropna(subset=[v]).copy();z['q']=z[v]**2;z['stratum']=np.where(z.group=='GN','GN','GE_GK')
 c=z.groupby('class_id',as_index=False).agg(n=(v,'size'),s=(v,'sum'),q=('q','sum'),school=('school','first'),stratum=('stratum','first'));n,s,q=[c[x].values for x in ['n','s','q']];value,raw,b,e=icc_calc(n,s,q,np.ones(len(c)));cw=weights(c,'class_id');sw=weights(c,'school');boot=icc_calc(n,s,q,cw)[0];sb=icc_calc(n,s,q,sw)[0]
 return dict(variable=v,n=len(z),classes=len(c),schools=z.school.nunique(),icc=float(value),raw=float(raw),variance_between=float(max(0,b)),variance_within=float(e),lo=float(np.quantile(boot,.025)),hi=float(np.quantile(boot,.975)),school_lo=float(np.quantile(sb,.025)),school_hi=float(np.quantile(sb,.975)),min_n=int(c.n.min()),max_n=int(c.n.max()))

def assoc(data,v,t):
 z=data.dropna(subset=[v,t]).copy();sz=z.groupby('class_id').size();excluded=int(sum(sz<2));z=z[z.class_id.isin(sz[sz>=2].index)].copy();z['x']=z[v]-z.groupby('class_id')[v].transform('mean');z['y']=z[t]-z.groupby('class_id')[t].transform('mean')
 for nm in ['x','y']:z[nm+'2']=z[nm]**2
 z['xy']=z.x*z.y;z['stratum']=np.where(z.group=='GN','GN','GE_GK');c=z.groupby('class_id',as_index=False).agg(xx=('x2','sum'),yy=('y2','sum'),xy=('xy','sum'),n=('id','size'),school=('school','first'),stratum=('stratum','first'));xx,yy,xy=[c[k].values for k in ['xx','yy','xy']]
 f=lambda w:(w@xy)/np.sqrt((w@xx)*(w@yy));r=float(f(np.ones(len(c))));assert abs(r-stats.pearsonr(z.x,z.y).statistic)<1e-12
 boot=f(weights(c,'class_id'));sb=f(weights(c,'school'));ranks=z[[v,t]].rank(method='average');ranks=ranks-ranks.groupby(z.class_id).transform('mean');rank=float(stats.pearsonr(ranks[v],ranks[t]).statistic)
 leave=[float((xy.sum()-xy[i])/np.sqrt((xx.sum()-xx[i])*(yy.sum()-yy[i]))) for i in range(len(c))]
 return dict(variable=v,test=t,n=len(z),classes=len(c),schools=z.school.nunique(),min_n=int(c.n.min()),max_n=int(c.n.max()),excluded_singleton_classes=excluded,r_within=r,lo=float(np.quantile(boot,.025)),hi=float(np.quantile(boot,.975)),sim_lo=float(np.quantile(boot,.0025)),sim_hi=float(np.quantile(boot,.9975)),school_lo=float(np.quantile(sb,.025)),school_hi=float(np.quantile(sb,.975)),school_sim_lo=float(np.quantile(sb,.0025)),school_sim_hi=float(np.quantile(sb,.9975)),rank_within=rank,r_pooled=float(stats.pearsonr(z[v],z[t]).statistic),rho_pooled=float(stats.spearmanr(z[v],z[t]).statistic),leave_min=min(leave),leave_max=max(leave))
