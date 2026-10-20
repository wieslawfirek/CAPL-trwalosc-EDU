"""CLI pipeline: validated long CSV -> tables, diagnostics and figures."""
import argparse,hashlib,json,platform,sys,time
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import scipy
from .data import load,wide,demographics,supplemental_sample,VARIABLES,TESTS,LABELS
from .robust import robust,holm
from .mmrm import fit
from . import supplement

def associations(d, reps=3000, camsa_reps=5000):
    year=d[d.time==3];rows=[];rng=np.random.default_rng(20261015)
    # Preserve the original ten-pair order. CAMSA is a later, separate extension.
    pairs=[(v,t,rng,reps) for t in TESTS for v in ['AR','PC','DB','KU','MC']]
    camsa_rng=np.random.default_rng(20261017)
    pairs += [('CAMSA_sur',t,camsa_rng,camsa_reps) for t in TESTS]
    for v,t,rg,b in pairs:
        z=year.dropna(subset=[v,t]);x=z[v].to_numpy();y=z[t].to_numpy();cl=z.class_id.to_numpy(dtype=str)
        if len(z)<4 or len(np.unique(cl))<3 or np.std(x)==0 or np.std(y)==0:raise ValueError(f'Insufficient variation/classes: {v}, {t}')
        rx=stats.rankdata(x);ry=stats.rankdata(y);rx=(rx-rx.mean())/rx.std(ddof=1);ry=(ry-ry.mean())/ry.std(ddof=1)
        inf=robust(np.column_stack([np.ones(len(z)),rx]),ry,cl)['inference'][1]
        rho=float(stats.spearmanr(x,y).statistic)
        if not np.isclose(rho,inf['estimate'],atol=1e-10):raise ArithmeticError('Rank regression/Spearman disagreement')
        blocks=[np.flatnonzero(cl==c) for c in np.unique(cl)];boot=[]
        for _ in range(b):
            ix=np.concatenate([blocks[j] for j in rg.integers(0,len(blocks),len(blocks))]);boot.append(stats.spearmanr(x[ix],y[ix]).statistic)
        lo,hi=np.quantile(boot,[.025,.975])
        rows.append(dict(variable=v,test=t,n=len(z),classes=len(blocks),rho=rho,lo=lo,hi=hi,p=inf['p'],df=inf['df'],bootstrap=b))
    for row,p in zip(rows,holm([r['p'] for r in rows])):row['p_holm']=p
    return pd.DataFrame(rows)

def neutral(d):
    rows=[]
    for v in VARIABLES:
        z=d.loc[d.time==3].dropna(subset=[v]);centers=sorted(z.center.unique());X=np.column_stack([np.ones(len(z)),(z.group=='GE').astype(float),(z.group=='GK').astype(float)]+[(z.center==c).astype(float) for c in centers[1:]])
        f=robust(X,z[v].to_numpy(),z.class_id.to_numpy(dtype=str))
        for j,g in [(1,'GE'),(2,'GK')]:rows.append(dict(variable=v,contrast=g+' minus GN',n=len(z),classes=z.class_id.nunique(),**f['inference'][j]))
    for row,p in zip(rows,holm([r['p'] for r in rows])):row['p_holm']=p
    return pd.DataFrame(rows)

def longitudinal(d, sensitivity=False):
    w=wide(d);out={};residuals={}
    for v in VARIABLES:
        print('MMRM:',v,flush=True);m,res=fit(w,v);out[v]=m;residuals[v]=res
        if sensitivity:
            m['complete_case']=fit(w,v,complete=True)[0]
            sd,_=supplemental_sample(d);m['assignment_sensitivity']=fit(wide(sd),v)[0]
            if v in ['Plank_time','StepCount']:
                z=w.copy()
                for t in (1,2,3):z[f'{v}_{t}']=np.log(z[f'{v}_{t}'].where(z[f'{v}_{t}']>0))
                m['log_sensitivity']=fit(z,v)[0]
    # Seven original families, each nine outcomes. Sensitivities corrected separately.
    for variant in [None]+(['complete_case','assignment_sensitivity'] if sensitivity else []):
        for name in out['AR']['contrasts']:
            ms=[out[v] if variant is None else out[v][variant] for v in VARIABLES]
            for m,p in zip(ms,holm([m['contrasts'][name]['p'] for m in ms])):m['contrasts'][name]['p_holm']=p
    rows=[dict(variable=v,contrast=k,**a) for v,m in out.items() for k,a in m['contrasts'].items()]
    return out,pd.DataFrame(rows),residuals

def stepcount_pre_year(models):
    """Exploratory year-minus-pre contrasts; raw p, outside the seven Holm families."""
    model=models['StepCount'];rows=[]
    for group,z in [('GE',model['contrasts']['GE_pre_year']),
                    ('GK',model['exploratory_contrasts']['GK_pre_year'])]:
        rows.append(dict(variable='StepCount',group=group,contrast='year minus pre',
                         **{k:z[k] for k in ['estimate','se','df','t','p','lo','hi']},
                         p_adjustment='none; exploratory'))
    return pd.DataFrame(rows)

def save_json(obj,path):
    # Convert numpy scalars, arrays and nonfinite floats without JSON NaN extensions.
    def clean(x):
        if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
        if isinstance(x,(list,tuple,np.ndarray)):return [clean(v) for v in x]
        if isinstance(x,(np.integer,)):return int(x)
        if isinstance(x,(float,np.floating)):return float(x) if np.isfinite(x) else None
        if isinstance(x,np.bool_):return bool(x)
        return x
    path.write_text(json.dumps(clean(obj),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,default=Path('outputs'));ap.add_argument('--quick',action='store_true',help='200 bootstrap samples; demonstration only');ap.add_argument('--font-dir',type=Path,help='Optional directory with locally licensed Times New Roman TTF files');ap.add_argument('--sensitivity',action='store_true',help='Complete cases, mixed-class omission and log raw scores');args=ap.parse_args()
    start=time.perf_counter();d,audit=load(args.input);out=args.output;out.mkdir(parents=True,exist_ok=True)
    for name,tab in demographics(d).items():tab.to_csv(out/(name+'.csv'),index=False)
    models,contrasts,res=longitudinal(d,args.sensitivity);contrasts.to_csv(out/'longitudinal_contrasts.csv',index=False);save_json(models,out/'longitudinal_models.json')
    stepcount_pre_year(models).to_csv(out/'stepcount_pre_year.csv',index=False)
    gn=neutral(d);gn.to_csv(out/'GN_comparisons.csv',index=False)
    corr=associations(d,200 if args.quick else 3000,200 if args.quick else 5000);corr.to_csv(out/'spearman.csv',index=False)
    sd,omitted=supplemental_sample(d);extra=supplement.run(sd[sd.time==3],200 if args.quick else 20000);extra['omitted_ambiguous_students']=omitted
    for name in ['icc','within']:pd.DataFrame(extra[name]).to_csv(out/(name+'.csv'),index=False)
    save_json(extra,out/'supplemental.json')
    from .figures import plots
    font=plots(d,models,corr,extra,res,out,args.font_dir)
    manifest=dict(input_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),python=sys.version,numpy=np.__version__,pandas=pd.__version__,scipy=scipy.__version__,platform=platform.platform(),figure_font=font,quick=args.quick,sensitivity=args.sensitivity,elapsed_seconds=time.perf_counter()-start,audit=audit,seeds=dict(spearman=20261015,CAMSA=20261017,supplemental=20261016),families=dict(longitudinal='9 per contrast',GN=18,spearman=12),note='No scores imputed. Outputs may contain confidential model details; not tracked by Git.')
    save_json(manifest,out/'run_manifest.json');print('Saved:',out.resolve())

if __name__=='__main__':main()
