from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(r"C:\Users\natha\ScientificDiscoveryLab")
COPY = Path(r"C:\Users\natha\AppData\Local\Temp\opencode\ScientificDiscoveryLab_audit_20260924_0325")
OUT = ROOT / "AUDIT" / "INDEPENDENT_AUDIT_20260924" / "percolation_reanalysis_results.json"
SEED = 20260924


def file_sha(path):
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def boot_slopes(Ls, arrays, draws=20000):
    g = np.random.default_rng(SEED)
    x = np.log(np.asarray(Ls, float))
    out = np.empty(draws)
    for d in range(draws):
        means = [np.asarray(a)[g.integers(0, len(a), len(a))].mean() for a in arrays]
        out[d] = np.polyfit(x, np.log(means), 1)[0]
    return out


def summary(draws):
    return {"mean": float(draws.mean()), "se": float(draws.std(ddof=1)),
            "ci95": [float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))]}


report = {}

# EXP-0009 and EXP-0010 stored raw-cell reanalysis.
base = ROOT / r"03_INVESTIGATIONS\PHYSICS\percolation\Q-P005_exponents\CODE\RESULTS"
for name, Ls, files in [
    ("EXP-0009", [128,256,512,1024], [base/'_cells_L128_n1500.npz',base/'_cells_L256_n700.npz',base/'_cells_L512_n150.npz',base/'_cells_L1024_n60.npz']),
    ("EXP-0010", [127,191,253,449], [base/f'_df_nontriv_L{L}_n200.npz' for L in [127,191,253,449]]),
]:
    masses=[]; chis=[]; pinfs=[]
    for f in files:
        z=np.load(f,allow_pickle=True); masses.append(z['masses'])
        if 'chis' in z: chis.append(z['chis']); pinfs.append(z['pinfs'])
    d={}
    for key,a,sign in [('Df',masses,1),('gamma_nu',chis,1),('beta_nu',pinfs,-1)]:
        if a: d[key]=summary(sign*boot_slopes(Ls,a))
    report[name]=d

# Q-P006 raw reanalysis and duplicate provenance.
q6=ROOT/r"03_INVESTIGATIONS\PHYSICS\percolation\Q-P006\CODE\RESULTS"
Ls=[512,1024,2048]
masses=[];chis=[];pinfs=[]
for L,n in zip(Ls,[200,100,50]):
    z=np.load(q6/f'_cells_L{L}_n{n}.npz',allow_pickle=True)
    masses.append(z['masses']);chis.append(z['chis']);pinfs.append(z['pinfs'])
report['Q-P006']={
    'Df':summary(boot_slopes(Ls,masses)),
    'gamma_nu':summary(boot_slopes(Ls,chis)),
    'beta_nu':summary(-boot_slopes(Ls,pinfs)),
    'raw_files_identical_to_Q-P005_directory':[file_sha(q6/f'_cells_L{L}_n{n}.npz')==file_sha(base/f'_cells_L{L}_n{n}.npz') for L,n in zip(Ls,[200,100,50])]
}

# Q-P007: reproduce published truncation and independent all-ragged reanalysis.
q7=ROOT/r"03_INVESTIGATIONS\PHYSICS\percolation\Q-P007\CODE\RESULTS"
Ls=[512,1024,2048]
masses=[];chis=[];pinfs=[]; structural=[]
for L,n in zip(Ls,[100,50,25]):
    z=np.load(q7/f'EXP-0009-pc_L{L}_cells.npz')
    masses.append(z['masses']);chis.append(z['chis']);pinfs.append(z['pinfs'])
    structural.append({
        'L':L,
        'recorded_cluster_count_per_realization':z['sizes_n'][:10].tolist(),
        'recorded_size_sum_field_is_array_not_total':bool(np.asarray(z['sizes_n_total']).ndim>0),
        'largest_mass_example':float(z['masses'][0]),
        'recorded_size_sum_example':float(np.asarray(z['sizes_n_total']).flat[0]),
        'actual_cluster_sizes_stored': 'sizes' in z.files,
    })
min_n=min(map(len,masses))
report['Q-P007']={
    'published_truncation_min_n':min_n,
    'published_truncation_Df':summary(boot_slopes(Ls,[a[:min_n] for a in masses])),
    'all_ragged_Df':summary(boot_slopes(Ls,masses)),
    'all_ragged_gamma_nu':summary(boot_slopes(Ls,chis)),
    'all_ragged_beta_nu':summary(-boot_slopes(Ls,pinfs)),
    'cache_structural_evidence':structural,
    'tau_bug': {
        'code': 'run_phase2.py appends cl_sizes (a list containing one size-array) instead of cl_sizes[0]',
        'consequence': 'len(ss)=1 for every realization; ss[1:] discards the entire cluster-size array; tau reports zero tail clusters',
        'current_runner_reproduction': 'KeyError: sizes when loading its own cache',
    }
}

# EXP-0007 p50 interpolation and fixed-exponent FSS directly from stored counts.
r7=json.loads((ROOT/r"03_INVESTIGATIONS\PHYSICS\percolation\CODE\RESULTS\EXP-0007_results.json").read_text(encoding='utf-8'))
def interp(ps, ws, target=.5):
    for i in range(len(ps)-1):
        if ws[i] < target <= ws[i+1]:
            return ps[i]+(target-ws[i])*(ps[i+1]-ps[i])/(ws[i+1]-ws[i])
    return None
rows=r7['cells']['bond_wrap']; p50={}
for L in sorted({int(x['L']) for x in rows}):
    rr=sorted([x for x in rows if int(x['L'])==L],key=lambda x:x['p'])
    ps=np.array([x['p'] for x in rr]); ws=np.array([x['k']/x['n'] for x in rr])
    p50[L]=interp(ps,ws)
Ls=sorted(p50); y=np.array([p50[L] for L in Ls]); se=np.array([r7['se'][str(L)] for L in Ls])
x=np.array(Ls,float)**(-3/4); X=np.c_[np.ones(len(x)),x]; W=np.diag(1/se); cov=np.linalg.inv(X.T@W@X); coef=np.linalg.lstsq(W@X,W@y,rcond=None)[0]
report['EXP-0007_threshold']={
    'direct_p50_by_L':p50,
    'fixed_exponent_WLS_intercept':float(coef[0]),
    'intercept_se_reported_scale':float(math.sqrt(cov[0,0])),
    'reported_intercept':r7['primary_fss']['a'],
    'reported_intercept_se':r7['primary_fss']['se_a'],
    'absolute_difference':abs(float(coef[0])-r7['primary_fss']['a']),
    'note': 'Point agreement is deterministic, but the reported SE is very broad; this is tolerance-level consistency, not precision reproduction of p_c=0.5.'
}

# Fresh EXP-0010 output in isolated copy after deleting all four cached cells.
orig=ROOT/r"03_INVESTIGATIONS\PHYSICS\percolation\Q-P005_exponents\CODE\RESULTS\EXP-0010_results.json"
fresh=COPY/r"03_INVESTIGATIONS\PHYSICS\percolation\Q-P005_exponents\CODE\RESULTS\EXP-0010_results.json"
if fresh.exists():
    import hashlib
    def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
    report['EXP-0010_fresh_copy']={'byte_identical':h(orig)==h(fresh),'original_sha256':h(orig),'fresh_sha256':h(fresh)}

OUT.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(OUT)
print(json.dumps(report,indent=2))
