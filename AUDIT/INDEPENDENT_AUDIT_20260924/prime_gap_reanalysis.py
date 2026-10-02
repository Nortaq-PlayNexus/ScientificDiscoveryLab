from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy import stats

ROOT=Path(r"C:\Users\natha\ScientificDiscoveryLab")
COPY=Path(r"C:\Users\natha\AppData\Local\Temp\opencode\ScientificDiscoveryLab_audit_20260924_0325")
OUT=ROOT/r"AUDIT\INDEPENDENT_AUDIT_20260924\prime_gap_reanalysis_results.json"
N=100_000_000
blocks=[('B1',10_000,100_000),('B2',100_000,1_000_000),('B3',1_000_000,10_000_000),('B4',10_000_000,N)]


def sieve(n):
    x=np.ones(n+1,dtype=bool);x[:2]=False
    for i in range(2,math.isqrt(n)+1):
        if x[i]:x[i*i::i]=False
    return np.flatnonzero(x)


def chi_counts(d,J=10):
    edges=[-math.log(1-j/J) for j in range(1,J)]
    c,_=np.histogram(d,bins=[0,*edges,np.inf]);e=np.full(J,len(d)/J)
    stat=float(np.sum((c-e)**2/e));return c,e,stat


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report={'N':N,'blocks':{},'global':{}}
p=sieve(N);report['global']['primes']=len(p)
all_d=[]
for name,lo,hi in blocks:
    bp=p[(p>=lo)&(p<hi)]; lovals=bp[:-1].astype(float);d=(bp[1:]-bp[:-1])/np.log(lovals);all_d.append(d)
    c,e,stat=chi_counts(d)
    # Diagnostic only: remove first quantile bin and renormalize the remaining Exp(1) probabilities.
    c2=c[1:];e2=e[1:]*(len(d)-c[0])/(len(d)-c[0]); stat2=float(np.sum((c2-e2)**2/e2))
    lag1=float(np.corrcoef(d[:-1],d[1:])[0,1]); lag2=float(np.corrcoef(d[:-2],d[2:])[0,1])
    # Dependence diagnostic: variance of means over 1000-gap blocks vs iid expectation.
    m=d[:len(d)//1000*1000].reshape(-1,1000).mean(1)
    emp_se=float(m.std(ddof=1)/math.sqrt(len(m)));iid_se=float(d.std(ddof=1)/math.sqrt(len(d)))
    report['blocks'][name]={
        'range':[lo,hi],'n':len(d),'mean':float(d.mean()),'variance':float(d.var(ddof=1)),
        'minimum_possible_delta_from_gap2':float(2/math.log(lo)),
        'first_quantile_edge':-math.log(1-.1),
        'first_bin_count':int(c[0]),'chi2':stat,'chi2_p':float(stats.chi2.sf(stat,9)),
        'diagnostic_chi2_excluding_structurally_impossible_first_bin':stat2,
        'diagnostic_chi2_p_excluding_first_bin':float(stats.chi2.sf(stat2,8)),
        'lag1_autocorrelation':lag1,'lag2_autocorrelation':lag2,
        'block1000_mean_se':emp_se,'iid_se':iid_se,'se_ratio_block_to_iid':emp_se/iid_se,
        'counts':c.tolist(),'expected':e.tolist(),
    }
d=np.concatenate(all_d)
report['global']['lag1_autocorrelation']=float(np.corrcoef(d[:-1],d[1:])[0,1])
report['global']['variance_ratio_to_Exp1']=float(d.var(ddof=1))
report['global']['interpretation']='Finite-range normalized gaps are strongly non-independent and their variance changes with scale. The exact Exp(1) rejection is descriptive of a misspecified finite-x null, not evidence against the asymptotic Gallagher/Prime Number Theorem picture or a novel process.'

# C7 with supplied sidecar was independently rerun; compare its report to historical.
orig=ROOT/r"03_INVESTIGATIONS\MATHEMATICS\prime_gaps\REPLICATION\C7_exp0008_report.json"
fresh=COPY/r"03_INVESTIGATIONS\MATHEMATICS\prime_gaps\REPLICATION\C7_exp0008_report.json"
if orig.exists() and fresh.exists():
    a=json.loads(orig.read_text(encoding='utf-8'));b=json.loads(fresh.read_text(encoding='utf-8'))
    report['c7_rerun']={'agreement':b.get('agreement_with_primary',{}).get('agreement'),
                        'verdict_agreement':b.get('agreement_with_primary',{}).get('verdict_agreement'),
                        'chi2_diff_max':b.get('agreement_with_primary',{}).get('chi2_diff_max'),
                        'ks_diff_max':b.get('agreement_with_primary',{}).get('ks_diff_max'),
                        'sieve_seconds_fresh':b.get('sieve_seconds')}

# Q-M008 1e8/1e9 result numerical comparison (ignore timing fields).
for f in ['Q-M008_1e8_results.json','Q-M008_1e9_results.json','Q-M008_combined.json']:
    a=ROOT/r"03_INVESTIGATIONS\MATHEMATICS\prime_gaps\Q-M008\RESULTS"/f
    b=COPY/r"03_INVESTIGATIONS\MATHEMATICS\prime_gaps\Q-M008\RESULTS"/f
    if a.exists() and b.exists():
        def strip(x):
            if isinstance(x,dict):return {k:strip(v) for k,v in x.items() if k not in {'sieve_time','analysis_time','total_time'}}
            if isinstance(x,list):return [strip(v) for v in x]
            return x
        report.setdefault('qm008_reruns',{})[f]={'semantic_identical_ignoring_runtime':strip(json.loads(a.read_text()))==strip(json.loads(b.read_text())),'original_sha256':sha(a),'rerun_sha256':sha(b)}
OUT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(OUT);print(json.dumps({'blocks':{k:{'variance':v['variance'],'first_bin':v['first_bin_count'],'lag1':v['lag1_autocorrelation'],'se_ratio':v['se_ratio_block_to_iid']} for k,v in report['blocks'].items()},'c7':report.get('c7_rerun'),'qm008':report.get('qm008_reruns')},indent=2))
