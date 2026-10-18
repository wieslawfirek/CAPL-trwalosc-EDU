"""Generate artificial students independently of all actual study records."""
from pathlib import Path
import numpy as np
import pandas as pd

def generate(seed=8675309):
    rng=np.random.default_rng(seed);rows=[];i=0
    for center in range(1,6):
        for g in ['GE','GK','GN']:
            school=f'DEMO_S{center}_'+('NEW' if g=='GN' else 'FOLLOWED')
            for cl in range(2):
                shift=rng.normal(0,.45)
                for student in range(10):
                    i+=1;ability=rng.normal();base=rng.normal(size=4);sex=rng.choice(['F','M']);age=rng.choice([10,11,12],p=[.1,.8,.1])
                    for t in ([3] if g=='GN' else [1,2,3]):
                        PC=np.clip(18+3*base[0]+shift+1.0*(t-1)+rng.normal(0,1.5),0,30)
                        DB=np.clip(16+4*base[1]+shift+(1.5 if t==2 else 0)+rng.normal(0,2),0,30)
                        MC=np.clip(25+2*base[2]+.2*ability+rng.normal(0,1),0,30)
                        KU=np.clip(6+1.2*base[3]+.6*ability+.3*(t-1)+rng.normal(0,.6),0,10)
                        a=dict(id=f'DEMO_{i:04}',group=g,school=school,class_id=f'{school}_{g}_C{cl+1}',center=f'DEMO_{center}',sex=sex,time=t,age_year=age if t==3 else np.nan,
                            PC=PC,DB=DB,MC=MC,KU=KU,AR=PC+DB+MC+KU,CAMSA_sur=np.clip(PC+.6*(t-1)+rng.normal(0,2),0,28),Plank_time=rng.lognormal(4.5+.12*base[0],.45),PACER_odcinki=max(0,int(rng.normal(26+3*base[0]+t,8))),StepCount=max(0,rng.normal(10000+600*base[1],1800)),EDU_Matematyka_wynik=np.clip(round(10+2*ability+.2*(PC-18)+shift+rng.normal(0,2)),0,18) if t==3 else np.nan,EDU_Polski_wynik=np.clip(round(11+2*ability+.4*(KU-6)+shift+rng.normal(0,2)),0,18) if t==3 else np.nan)
                        # Incomplete series and individual missing trials, not copied from the study.
                        if rng.random()<.035:
                            for v in ['PC','DB','MC','KU','AR','CAMSA_sur','Plank_time','PACER_odcinki','StepCount']:a[v]=np.nan
                        elif rng.random()<.08:a['DB']=a['AR']=np.nan;a['StepCount']=np.nan
                        rows.append(a)
    return pd.DataFrame(rows)

if __name__=='__main__':generate().to_csv(Path(__file__).with_name('capl_synthetic_long.csv'),index=False,float_format='%.10g')
