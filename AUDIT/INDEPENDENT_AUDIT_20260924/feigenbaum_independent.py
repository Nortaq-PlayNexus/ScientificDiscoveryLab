from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

ROOT=Path(r"C:\Users\natha\ScientificDiscoveryLab")
OUT=ROOT/r"AUDIT\INDEPENDENT_AUDIT_20260924\feigenbaum_independent_results.json"


def f(x,a,z):return 1-a*abs(x)**z

def residual(a,z,n):
    x=0.0
    for _ in range(2**n):x=f(x,a,z)
    return x

def first_return(a,z,maxk):
    x=0.0
    for k in range(1,maxk+1):
        x=f(x,a,z)
        if abs(x)<1e-11:return k
    return None

def root_local(z,n,a_prev,a_prev2=None):
    if n==1:return 1.0
    if a_prev2 is None:half=0.5
    else:half=max(0.01,5*abs(a_prev-a_prev2))
    lo=max(1e-6,a_prev-half);hi=a_prev+half
    xs=np.linspace(lo,hi,12001);rs=np.array([residual(x,z,n) for x in xs])
    candidates=[]
    for i in range(len(xs)-1):
        if np.isfinite(rs[i]) and np.isfinite(rs[i+1]) and rs[i]*rs[i+1]<0:
            r=brentq(lambda a:residual(a,z,n),xs[i],xs[i+1],xtol=5e-15,rtol=1e-14)
            if first_return(r,z,2**n)==2**n:candidates.append(r)
    if not candidates:
        # Deterministic shrinking scan around predecessor.
        for fac in (2,4,8,16):
            x=np.linspace(max(1e-6,a_prev-fac*half),a_prev+fac*half,40001)
            r=np.array([residual(v,z,n) for v in x])
            for i in range(len(x)-1):
                if r[i]*r[i+1]<0:
                    q=brentq(lambda a:residual(a,z,n),x[i],x[i+1])
                    if first_return(q,z,2**n)==2**n:candidates.append(q)
            if candidates:break
    if not candidates:raise RuntimeError(f'No verified root z={z} n={n}')
    return min(candidates,key=lambda a:abs(a-a_prev))


def run(z,nmax=10):
    a={1:1.0};period={1:2}
    for n in range(2,nmax+1):a[n]=root_local(z,n,a[n-1],a.get(n-2));period[n]=first_return(a[n],z,2**n)
    delta={n:(a[n-1]-a[n-2])/(a[n]-a[n-1]) for n in range(3,nmax+1)}
    return a,period,delta
report={'method':'Independent local continuation + Brent root finding + exact-period verification; no project engine import.'}
for z in (2,3,4):
    a,pd,de=run(z,10)
    report[f'z{z}']={'a':a,'period':pd,'delta':de,'delta_last':de[max(de)],'strictly_monotonic_delta':all(de[n]<de[n+1] for n in range(3,max(de)))}
report['comparison']={
    'z2_delta10':report['z2']['delta_last'],'z2_reference':4.6692016091029,
    'z3_delta10':report['z3']['delta_last'],'z3_project_claimed_infinite':4.894,
    'z4_delta10':report['z4']['delta_last'],'z4_project_claimed_infinite':5.168,
    'current_project_z3_reproduced_delta':'Infinity (same root selected for all n)',
    'current_project_z4_reproduced_delta':'Infinity (nonmonotone/repeated roots)',
}
OUT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(OUT);print(json.dumps(report['comparison'],indent=2))
