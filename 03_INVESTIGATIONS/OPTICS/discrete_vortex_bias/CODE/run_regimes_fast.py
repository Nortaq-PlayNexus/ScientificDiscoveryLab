#!/usr/bin/env python3
"""Reduced close-pair/high-order regime map for quick falsification."""
from __future__ import annotations
import json,time
from pathlib import Path
from run_convergence import DETECTORS,RESULTS_DIR,BASE_WAVELENGTH_NM,asm_numpy,cell_coordinates,summarize,utc_now
from run_regimes import make_field

def main():
    t=time.time();rows=[]
    for sep in (2.,4.,6.,8.,12.,16.,24.,32.):
      positions=[(128-sep/2,128,1),(128+sep/2,128,-1)]
      for n in (32,64,128,256,512):
       for shift in (0.,.5):
        f,truth,_=make_field((n,n),positions,shift_px=shift);_,_,dy,dx=cell_coordinates((n,n))
        for z in (0.,1280.):
         out=asm_numpy(f,z*1e-6,dx,dy,BASE_WAVELENGTH_NM)
         for det in DETECTORS:
          r={'regime':'close_pair','separation_um':sep,'grid':n,'shift_px':shift,'z_um':z,'detector':det};r.update(summarize(out,det,truth if z==0 else [],(n,n)));rows.append(r)
    for q in (1,2,3,4,6):
      for n in (32,64,128,256,512):
       for shift in (0.,.5):
        f,truth,_=make_field((n,n),[(128,128,q)],shift_px=shift);_,_,dy,dx=cell_coordinates((n,n))
        for z in (0.,1280.):
         out=asm_numpy(f,z*1e-6,dx,dy,BASE_WAVELENGTH_NM)
         for det in DETECTORS:
          r={'regime':'high_order','charge':q,'grid':n,'shift_px':shift,'z_um':z,'detector':det};r.update(summarize(out,det,truth if z==0 else [],(n,n)));rows.append(r)
    p=RESULTS_DIR/f"regimes_fast_{time.strftime('%Y%m%d_%H%M%S')}.json";p.write_text(json.dumps({'experiment':'EXP-0015','stage':'regimes_fast','rows':rows,'runtime_s':time.time()-t},indent=2,allow_nan=False)+'\n');print('Wrote',p)
if __name__=='__main__':main()
