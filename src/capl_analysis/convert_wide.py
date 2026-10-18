"""Local conversion of the study's wide XLSX/CSV to canonical long CSV.

Usage: python -m capl_analysis.convert_wide --input data_private/source.xlsx
       --output data_private/capl_long.csv [--age-file data_private/age.xlsx]
No database is downloaded or uploaded by this program.
"""
import argparse,re
from pathlib import Path
import numpy as np
import pandas as pd
from .data import VARIABLES,TESTS

CITIES={'1':'Katowice','2':'Kraków','3':'Poznań','4':'Warszawa','5':'Wrocław'}
def read(p):return pd.read_excel(p) if p.suffix.lower() in ['.xlsx','.xls'] else pd.read_csv(p,float_precision="round_trip")

def convert(source,ages=None):
    source=source.copy();source=source.rename(columns={source.columns[0]:'id'})
    valid=source.id.astype(str).str.fullmatch(r'O[1-5][A-Z]_\d[A-Z]_(GE|GK|GN)_\d{3}')
    excluded=int((~valid).sum());source=source.loc[valid].copy()
    if source.id.duplicated().any():raise ValueError('Duplicate stable IDs; resolve before conversion')
    if ages is not None:
        a=ages.iloc[:,:2].copy();a.columns=['id','age_year'];a.id=a.id.astype(str).str.strip()
        if a.id.duplicated().any():raise ValueError('Duplicate ID in age file')
        source=source.merge(a,on='id',how='left',validate='one_to_one')
    rows=[]
    for _,z in source.iterrows():
        school,cl,g,_=z.id.split('_')
        for t in ([3] if g=='GN' else [1,2,3]):
            a=dict(id=z.id,group=g,school=school,class_id=school+'_'+cl,center=CITIES[school[1]],sex={1:'M',2:'F'}.get(z.get('Gender')),time=t,age_year=z.get('age_year',np.nan) if t==3 else np.nan)
            for v in VARIABLES:
                col=f'PLANK_time_{t}' if v=='Plank_time' and t<3 else f'{v}_{t}'
                if col not in source:raise ValueError('Missing source column '+col)
                a[v]=z[col]
            for test in TESTS:
                if test not in source:raise ValueError('Missing source column '+test)
                a[test]=z[test] if t==3 else np.nan
            rows.append(a)
    return pd.DataFrame(rows),excluded

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--age-file',type=Path);a=ap.parse_args()
    d,n=convert(read(a.input),read(a.age_file) if a.age_file else None);a.output.parent.mkdir(parents=True,exist_ok=True);d.to_csv(a.output,index=False)
    print(f'Converted {d.id.nunique()} unique students; excluded {n} rows without a valid stable ID. Saved locally: {a.output}')
if __name__=='__main__':main()
