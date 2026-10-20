"""Six report figures and Q-Q diagnostics; no source data or bundled fonts."""
from pathlib import Path
import textwrap,warnings
import numpy as np
import pandas as pd
from scipy import stats
from .data import VARIABLES,LABELS,TESTS
from .robust import robust

def plots(d,models,corr,extra,residuals,out,font_dir=None):
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager as fm
    if font_dir is not None:
        font_dir=Path(font_dir)
        if not font_dir.is_dir():raise ValueError('Font directory does not exist')
        for f in font_dir.iterdir():
            if f.suffix.lower()=='.ttf':fm.fontManager.addfont(str(f))
    available={f.name for f in fm.fontManager.ttflist}
    font='Times New Roman' if 'Times New Roman' in available else 'DejaVu Serif'
    if font!='Times New Roman':warnings.warn('Times New Roman unavailable; using DejaVu Serif. Use --font-dir for report typography.',stacklevel=2)
    plt.rcParams.update({'font.family':font,'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.unicode_minus':False})
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    wi=pd.DataFrame(extra['within']);ic=pd.DataFrame(extra['icc'])
    labels=LABELS.copy();labels['PC']='Kompetencje ruchowe';labels['StepCount']='Średnia dzienna liczba kroków'
    # MMRM-adjusted means for GE/GK; separate descriptive GN mean with CR2 CI.
    for num,vs in [(1,VARIABLES[:5]),(2,VARIABLES[5:])]:
     fig,axs=plt.subplots(3 if num==1 else 2,2,figsize=(9,9.2 if num==1 else 7))
     for ax,v in zip(axs.flat,vs):
      for g,col,marker in [('GE','#3D6B8D','o'),('GK','#B65E38','s'),('GN','#555555','D')]:
       if g!='GN':
        ms=models[v]['means'][g];xx=np.array([1,2,3])+(-.035 if g=='GE' else .035)
        yy=np.array([q['estimate'] for q in ms]);lo=np.array([q['lo'] for q in ms]);hi=np.array([q['hi'] for q in ms])
       else:
        z=d[(d.group=='GN') & (d.time==3)].dropna(subset=[v]);q=robust(np.ones((len(z),1)),z[v].to_numpy(),z.class_id.to_numpy(dtype=str))['inference'][0]
        xx=np.array([3.17]);yy=np.array([q['estimate']]);lo=np.array([q['lo']]);hi=np.array([q['hi']])
       ax.errorbar(xx,yy,yerr=[yy-lo,hi-yy],fmt=marker+'-' if g!='GN' else marker,color=col,label=g,lw=1.4,markersize=5,capsize=3)
      ax.set_title('\n'.join(textwrap.wrap(labels[v],27)),fontsize=12)
      ax.set_xticks([1,2,3],['Pretest','Posttest','Po roku']);ax.grid(axis='y',alpha=.2)
      ax.set_ylabel('Kroki / dobę' if v=='StepCount' else 'Sekundy' if v=='Plank_time' else 'Liczba odcinków' if v=='PACER_odcinki' else 'Punkty')
     for ax in axs.flat[len(vs):]:ax.axis('off')
     axs.flat[0].legend(ncol=3,fontsize=10);fig.tight_layout(h_pad=2,w_pad=2);fig.savefig(out/f'fig{num}.png',dpi=260);plt.close(fig)
    for num,t in [(3,TESTS[0]),(4,TESTS[1])]:
     fig,ax=plt.subplots(figsize=(9,5.3));vs=VARIABLES[:5]+['CAMSA_sur'];z=corr[corr.test==t].set_index('variable')
     for i,v in enumerate(vs):
      a=z.loc[v];ax.errorbar(a.rho,i,xerr=[[a.rho-a.lo],[a.hi-a.rho]],fmt='o',capsize=3,color='#3D6B8D' if a.p_holm<.05 else '#8D929A');ax.text(.61,i,f'n = {int(a.n)}',va='center',fontsize=10)
     ax.set_yticks(range(6),[labels[v] for v in vs]);ax.invert_yaxis();ax.axvline(0,color='gray',ls='--');ax.set_xlim(-.18,.75);ax.set_xticks([0,.2,.4,.6]);ax.set_title(LABELS[t]);ax.set_xlabel('Korelacja rang Spearmana i 95% przedział ufności');fig.tight_layout();fig.savefig(out/f'fig{num}.png',dpi=260);plt.close(fig)
    plt.rcParams.update({'font.size':16})
    fig,axs=plt.subplots(1,2,figsize=(13,5),sharey=True)
    for ax,t in zip(axs,TESTS):
     z=wi[wi.test==t].set_index('variable')
     for i,v in enumerate(VARIABLES[:5]):
      a=z.loc[v];ax.errorbar(a.r_within,i,xerr=[[a.r_within-a.lo],[a.hi-a.r_within]],fmt='o',capsize=3,color='#3D6B8D' if a.lo>0 else '#8D929A');ax.text(.60,i,f'n = {int(a.n)}',va='center',fontsize=14)
     ax.axvline(0,color='gray',ls='--');ax.set_xlim(-.15,.78);ax.set_xticks([0,.2,.4,.6]);ax.set_title(LABELS[t]);ax.set_xlabel('Korelacja Pearsona\ni 95% przedział ufności')
    axs[0].set_yticks(range(5),[labels[v] for v in VARIABLES[:5]]);axs[0].invert_yaxis();fig.tight_layout();fig.savefig(out/'fig5.png',dpi=260);plt.close(fig)
    fig,ax=plt.subplots(figsize=(12,5.8));
    for i,a in ic.iterrows():
     ax.errorbar(a.icc*100,i,xerr=[[100*(a.icc-a.lo)],[100*(a.hi-a.icc)]],fmt='o',capsize=3,color='#3D6B8D')
     ax.text(37,i,f'{a.icc*100:.1f}% [{a.lo*100:.1f}; {a.hi*100:.1f}]'.replace('.',','),va='center',fontsize=14)
     ax.text(64,i,f'{int(a.n)} / {int(a.classes)}',va='center',ha='center',fontsize=14)
    ax.text(37,-.8,'ICC [95% PU]',weight='bold');ax.text(64,-.8,'Uczniowie / klasy',ha='center',weight='bold');ax.set_yticks(range(len(ic)),[labels[v] for v in ic.variable]);ax.set_ylim(len(ic)-.5,-1.2);ax.set_xlim(-1,73);ax.set_xticks([0,10,20,30]);ax.spines['bottom'].set_bounds(0,30);ax.set_xlabel('Udział różnic między klasami (%)',x=.23);fig.tight_layout();fig.savefig(out/'fig6.png',dpi=260);plt.close(fig)
    plt.rcParams.update({'font.size':10})
    fig,axs=plt.subplots(3,3,figsize=(10,9))
    for ax,(v,e) in zip(axs.flat,residuals.items()):
        stats.probplot(e,dist='norm',plot=ax);ax.set_title(labels[v]);ax.set_xlabel('');ax.set_ylabel('')
    fig.tight_layout();fig.savefig(out/'diagnostics_qq.png',dpi=160);plt.close(fig)
    # Fail loudly if an exported image is empty or damaged.
    from PIL import Image
    for number in range(1,7):
        with Image.open(out/f'fig{number}.png') as img:img.verify()
    return font
