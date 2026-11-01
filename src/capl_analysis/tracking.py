"""Paired category tracking from the reviewed wide workbook; writes local aggregates only."""
import argparse,json,math,hashlib
from pathlib import Path
import openpyxl
import numpy as np
from scipy import stats
from .robust import holm

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--input',type=Path,required=True)
 ap.add_argument('--age-file',type=Path,required=True)
 ap.add_argument('--output',type=Path,required=True)
 args=ap.parse_args()
 raw=list(openpyxl.load_workbook(args.input,data_only=True,read_only=True)['Arkusz1'].values)
 headers=raw[0];rows=[(i+2,r) for i,r in enumerate(raw[1:]) if r[0]]
 if len({str(r[0]).strip() for _,r in rows})!=len(rows):raise ValueError('Duplicate nonempty IDs; resolve locally')
 expected={0:'ID_ucznia_2026',5:'Gender',31:'CAMSA_sur_2',33:'PLANK_time_2',35:'PACER_odcinki_2',37:'PC_2',38:'StepCount_2',41:'DB_2',44:'KU_2',49:'MC_2',50:'AR_2',54:'CAMSA_sur_3',57:'Plank_time_3',59:'PACER_odcinki_3',61:'PC_3',66:'MC_3',69:'KU_3',70:'StepCount_3',73:'DB_3',74:'AR_3'}
 if any(headers[i]!=name for i,name in expected.items()):raise ValueError('Unexpected wide schema; verify mapping before analysis')
 cats=['Początkujący','Dokonujący postępów','Sprawny','Wyróżniający się']
 metrics=[('capl','Wynik ogólny AR',50,74,'capl_score'),('pc','Kompetencje fizyczne',37,61,'pc_score'),('db','Zachowania codzienne',41,73,'db_score'),('mc','Motywacja i pewność siebie',49,66,'mc_score'),('ku','Wiedza i zrozumienie',44,69,'ku_score'),('camsa','CAMSA (0–28 pkt)',31,54,'camsa_skill_time_score'),('pacer','PACER (odcinki 20 m)',35,59,'pacer_20m_laps'),('plank','Deska (sekundy)',33,57,'plank_time'),('steps','Kroki (średnia dzienna)',38,70,'step_average')]
 age_rows=list(openpyxl.load_workbook(args.age_file,data_only=True).active.values)[1:]
 ages={str(r[0]).strip():r[1] for r in age_rows if r[0] is not None}
 assert len(ages)==len([r for r in age_rows if r[0] is not None])
 assert all(isinstance(v,(int,float)) and v==int(v) and 9<=v<=12 for v in ages.values())
 lookup=json.loads(Path(__file__).with_name('norms.json').read_text())
 capl={k:{} for k,*_ in metrics};papl={}
 for row in lookup:
  k,label,_,_,pkey=next(m for m in metrics if m[1]==row['metric'])
  sex=1 if row['sex']=='Chłopiec' else 2
  if row['norm']=='CAPL':capl[k][(row['age'],sex)]=row['thresholds']
  else:papl[(pkey,row['age'],sex)]=row['thresholds']
 def num(v):return isinstance(v,(int,float)) and math.isfinite(v)
 def complete(r,t,key):
  ix={'pc':([32,34,36],[56,58,60]),'db':([39,40],[71,72]),'mc':([45,46,47,48],[62,63,64,65]),'ku':([42,43],[67,68])}
  if key=='capl':return all(complete(r,t,k) for k in ix)
  return all(num(r[j]) for j in ix.get(key,([],[]))[t])
 def value(r,t,k,idx):
  v=r[idx]
  if not num(v) or not complete(r,t,k):return None
  if k=='capl':
   # Sum complete domains to avoid partial totals and source rounding differences.
   indices=[37,41,49,44] if t==0 else [61,73,66,69]
   if not all(num(r[j]) for j in indices):return None
   v=sum(r[j] for j in indices)
  bounds={'capl':(0,100),'pc':(0,30),'db':(0,30),'mc':(0,30),'ku':(0,10),'camsa':(1,28),'pacer':(1,229),'plank':(0,float('inf')),'steps':(1000,30000)}
  lo,hi=bounds[k]
  return v if lo<=v<=hi else None
 def classify(v,k,pkey,sex,norm,age):
  if v is None or sex not in [1,2] or age not in range(8,13):return None
  b=capl[k][(age,sex)] if norm=='CAPL' else papl[(pkey,age,sex)]
  if norm=='PAPL': v=round(v,0 if k in ['camsa','pacer','steps'] else 1)
  if norm=='CAPL' and k=='steps': v=round(v)
  return 1 if v<b[0] else 2 if v<=b[1] else 3 if v<=b[2] else 4
 data=[]
 for k,label,a,b,pkey in metrics:
  for _,r in rows:
   age3=ages.get(str(r[0]).strip());age2=age3-1 if age3 is not None else None
   for norm in ['CAPL','PAPL']:
    c1=classify(value(r,0,k,a),k,pkey,r[5],norm,age2)
    c2=classify(value(r,1,k,b),k,pkey,r[5],norm,age3)
    if c1 and c2:data.append(dict(norm=norm,metric=label,group=r[4],post=c1,year=c2))
 summary=[];matrices=[];distribution=[];tests=[]
 for norm in ['CAPL','PAPL']:
  for k,label,*_ in metrics:
   z=[r for r in data if r['norm']==norm and r['metric']==label];n=len(z)
   m=np.zeros((4,4),int)
   for r in z:m[r['post']-1,r['year']-1]+=1
   low=int(m[:2,:2].sum());reach=int(m[:2,2:].sum());keep=int(m[2:,2:].sum());lost=int(m[2:,:2].sum())
   count=dict(down=int(np.tril(m,-1).sum()),same=int(np.trace(m)),up=int(np.triu(m,1).sum()),down_ge2=int(np.tril(m,-2).sum()),up_ge2=int(np.triu(m,2).sum()),below_both=low,reached=reach,kept=keep,lost=lost)
   summary.append(dict(norm=norm,metric=label,n=n,**count,**{key+'_percent':100*v/n if n else None for key,v in count.items()}))
   matrices.append(dict(norm=norm,metric=label,n=n,post_by_year=m.tolist()))
   distribution.append(dict(norm=norm,metric=label,n=n,post=m.sum(axis=1).tolist(),year=m.sum(axis=0).tolist()))
   if k=='capl':
    tab=[[int(sum(r['group']==g and np.sign(r['year']-r['post'])==sg for r in z)) for sg in [-1,0,1]] for g in ['GE','GK']]
    stat,p,df,expected=stats.chi2_contingency(tab,correction=False)
    tests.append(dict(norm=norm,table=tab,chi2=float(stat),df=int(df),p=float(p),min_expected=float(expected.min()),note='Exploratory Pearson chi-square; no class clustering or baseline-category adjustment'))
 for row,p in zip(tests,holm([r['p'] for r in tests])):row['p_holm']=float(p)
 payload=dict(summary=summary,matrices=matrices,distribution=distribution,group_tests=tests,notes=['post age = III age minus exactly one year','All nonempty unique source IDs, not the strict-ID MMRM registry','No missing age or sex imputed; percentages use all paired children per metric','CAPL thresholds from cran/capl get_capl_interpretation; PAPL from wieslawfirek/kalkulatorCAPL-PAPL data/papl_norms.csv and app.R','No individual records in this output'],input_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),age_sha256=hashlib.sha256(args.age_file.read_bytes()).hexdigest())
 args.output.mkdir(parents=True,exist_ok=True)
 (args.output/'tracking.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2,allow_nan=False))
 print('Saved local aggregates:',args.output)

if __name__=='__main__':main()
