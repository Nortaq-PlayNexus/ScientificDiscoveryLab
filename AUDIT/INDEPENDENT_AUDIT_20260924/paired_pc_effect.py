from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy import ndimage

ROOT=Path(r"C:\Users\natha\ScientificDiscoveryLab")
OUT=ROOT/r"AUDIT\INDEPENDENT_AUDIT_20260924\paired_pc_effect_results.json"
P1=0.59274605079210
P2=0.5927289999999997
STRUCT=ndimage.generate_binary_structure(2,1)
SEED=20260924


def masses_at_two_p(L,n,seed):
    g=np.random.default_rng(seed)
    a=np.empty(n);b=np.empty(n)
    for i in range(n):
        u=g.random((L,L))
        for p,out in [(P1,a),(P2,b)]:
            lab,c=ndimage.label(u<p,structure=STRUCT)
            if c:
                s=np.bincount(lab.ravel()); out[i]=s[1:].max()
            else: out[i]=0
    return a,b


def boot(Ls,aa,bb=None,draws=20000):
    g=np.random.default_rng(SEED+sum(Ls));x=np.log(np.asarray(Ls,float));sa=np.empty(draws);sb=np.empty(draws) if bb is not None else None
    for d in range(draws):
        ma=[];mb=[]
        for j,A in enumerate(aa):
            idx=g.integers(0,len(A),len(A));ma.append(A[idx].mean())
            if bb is not None: mb.append(bb[j][idx].mean())
        sa[d]=np.polyfit(x,np.log(ma),1)[0]
        if bb is not None: sb[d]=np.polyfit(x,np.log(mb),1)[0]
    out={'p_canonical_Df_mean':float(sa.mean()),'p_canonical_Df_se':float(sa.std(ddof=1))}
    if bb is not None:
        delta=sb-sa
        out.update({'p_refined_Df_mean':float(sb.mean()),'p_refined_Df_se':float(sb.std(ddof=1)),
                    'paired_Df_change_refined_minus_canonical':float(delta.mean()),
                    'paired_Df_change_se':float(delta.std(ddof=1)),
                    'paired_ci95':[float(np.percentile(delta,2.5)),float(np.percentile(delta,97.5))]})
    return out

report={'canonical_p':P1,'refined_p':P2,'delta_p':P2-P1,'method':'Paired common-random-number site percolation; same uniform field thresholded at both p values.','tests':{}}
for name,Ls,ns,offset in [
    ('EXP0009_like',[128,256,512,1024],[800,400,200,60],1000),
    ('QP007_like',[512,1024,2048],[100,50,25],2000),
]:
    aa=[];bb=[]
    for L,n in zip(Ls,ns):
        a,b=masses_at_two_p(L,n,SEED+offset+L*1009);aa.append(a);bb.append(b)
        print(name,L,n,float(a.mean()),float(b.mean()),flush=True)
    report['tests'][name]={'sizes':Ls,'n':ns,**boot(Ls,aa,bb)}
OUT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(OUT);print(json.dumps(report,indent=2))
