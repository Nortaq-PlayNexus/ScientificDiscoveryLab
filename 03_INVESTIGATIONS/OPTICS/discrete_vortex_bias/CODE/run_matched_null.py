#!/usr/bin/env python3
"""Multi-seed matched-spectrum/amplitude null distribution for EXP-0015."""
from __future__ import annotations
import json,time,statistics
from pathlib import Path
import numpy as np
from run_convergence import RESULTS_DIR,FOV_UM,BASE_WAVELENGTH_NM,asm_numpy,cell_coordinates,make_known_field,make_matched_amplitude_surrogate,make_matched_spectrum_surrogate,summarize,utc_now

SEEDS=tuple(range(1000,1050)); GRIDS=(128,256); Z=(0.,1280.)

def main():
    start=time.time();rows=[]
    for n in GRIDS:
        target,truth,_=make_known_field((n,n),'four_vortex_lattice',seed=42)
        _,_,dy,dx=cell_coordinates((n,n))
        for z in Z:
            for variant in ('matched_spectrum','matched_amplitude','random_complex_gaussian'):
                reps=SEEDS if variant=='matched_spectrum' else SEEDS[:20]
                for seed in reps:
                    if variant=='matched_spectrum': u=make_matched_spectrum_surrogate(target,seed)
                    elif variant=='matched_amplitude': u=make_matched_amplitude_surrogate(target,seed)
                    else: u=make_known_field((n,n),'random_complex_gaussian',seed=seed)[0]
                    out=u if z==0 else asm_numpy(u,z*1e-6,dx,dy,BASE_WAVELENGTH_NM)
                    # Local contour is bounded to keep the null tractable;
                    # raw/clustered/supported are the primary null estimators.
                    for det in ('raw_winding','clustered_winding','supported_clustered_winding','local_minimum_contour'):
                        row={'grid':n,'z_um':z,'variant':variant,'seed':seed,'detector':det}
                        row.update(summarize(out,det));rows.append(row)
    # Empirical upper-tail and two-sided descriptive p-values, with +1 correction.
    groups={}
    for r in rows:
        key=(r['grid'],r['z_um'],r['variant'],r['detector']);groups.setdefault(key,[]).append(r['count'])
    target_counts={}
    for n in GRIDS:
        target,_,_=make_known_field((n,n),'four_vortex_lattice',seed=42)
        _,_,dy,dx=cell_coordinates((n,n))
        for z in Z:
            out=target if z==0 else asm_numpy(target,z*1e-6,dx,dy,BASE_WAVELENGTH_NM)
            for det in ('raw_winding','clustered_winding','supported_clustered_winding','local_minimum_contour'):
                target_counts[(n,z,det)]=summarize(out,det)['count']
    tests=[]
    for n in GRIDS:
      for z in Z:
       for variant in ('matched_spectrum','matched_amplitude','random_complex_gaussian'):
        for det in ('raw_winding','clustered_winding','supported_clustered_winding','local_minimum_contour'):
            vals=groups.get((n,z,variant,det),[]); obs=target_counts[(n,z,det)]
            if vals:
                upper=(1+sum(v>=obs for v in vals))/(1+len(vals));two=(1+sum(abs(v-statistics.mean(vals))>=abs(obs-statistics.mean(vals)) for v in vals))/(1+len(vals))
            else: upper=two=None
            tests.append({'grid':n,'z_um':z,'variant':variant,'detector':det,'observed':obs,'null_n':len(vals),'null_mean':statistics.mean(vals) if vals else None,'null_sd':statistics.stdev(vals) if len(vals)>1 else 0,'p_upper_descriptive':upper,'p_two_sided_descriptive':two})
    result={'experiment':'EXP-0015','stage':'matched_null_distribution','timestamp_utc':utc_now(),'status':'EXPLORATORY_DESCRIPTIVE','seeds':SEEDS,'grids':GRIDS,'z_um':Z,'rows':rows,'tests':tests,'runtime_s':time.time()-start}
    p=RESULTS_DIR/f"matched_null_{time.strftime('%Y%m%d_%H%M%S')}.json";p.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8');print('Wrote',p)
if __name__=='__main__':main()
