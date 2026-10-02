#!/usr/bin/env python3
"""EXP-0015 independent-seed ladder for random and surrogate fields."""
from __future__ import annotations
import json,time,statistics
from pathlib import Path
import numpy as np
from run_convergence import DETECTORS,RESULTS_DIR,BASE_WAVELENGTH_NM,asm_numpy,cell_coordinates,make_known_field,make_matched_amplitude_surrogate,make_matched_spectrum_surrogate,summarize,utc_now

SEEDS=(42,7,123,2023,314159,271828)
GRIDS=(128,256)
BANDS=(0.05,0.10,0.20,0.35)
Z=(0.,1280.)

def main():
    start=time.time();rows=[]
    for n in GRIDS:
      for band in BANDS:
       for seed in SEEDS:
        # The main constructor handles the random case through its explicit
        # branch; random_band is not exposed there, so generate a local field
        # with the same band-limited construction here.
        rng=np.random.default_rng(seed);u=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n));fy=np.fft.fftfreq(n)[None,:];fx=np.fft.fftfreq(n)[:,None];k2=(2*np.pi*fx)**2+(2*np.pi*fy)**2;u=np.fft.ifft2(np.fft.fft2(u)*np.exp(-.5*(k2/(2*np.pi*band))**2));u/=np.max(np.abs(u))
        _,_,dy,dx=cell_coordinates((n,n))
        for z in Z:
         out=asm_numpy(u,z*1e-6,dx,dy,BASE_WAVELENGTH_NM)
         for det in DETECTORS:
          row={'grid':n,'band':band,'seed':seed,'z_um':z,'detector':det};row.update(summarize(out,det));rows.append(row)
    # Summary by cell; no p-values are computed because seeds are the only
    # independent replicates and the matrix is deliberately descriptive.
    groups={}
    for r in rows:
      key=(r['grid'],r['band'],r['z_um'],r['detector']);groups.setdefault(key,[]).append(r['count'])
    summary=[]
    for key,vals in sorted(groups.items()): summary.append({'grid':key[0],'band':key[1],'z_um':key[2],'detector':key[3],'n':len(vals),'mean':statistics.mean(vals),'sd':statistics.stdev(vals) if len(vals)>1 else 0,'cv':statistics.stdev(vals)/statistics.mean(vals) if len(vals)>1 and statistics.mean(vals) else 0,'min':min(vals),'max':max(vals)})
    result={'experiment':'EXP-0015','stage':'seed_ladder','timestamp_utc':utc_now(),'seeds':SEEDS,'grids':GRIDS,'bands':BANDS,'z_um':Z,'rows':rows,'summary':summary,'runtime_s':time.time()-start}
    p=RESULTS_DIR/f"seed_ladder_{time.strftime('%Y%m%d_%H%M%S')}.json";p.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8');print('Wrote',p)

if __name__=='__main__':main()
