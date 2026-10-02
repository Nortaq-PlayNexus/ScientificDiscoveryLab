#!/usr/bin/env python3
"""High-resolution reference for the close-pair tracker anomaly."""
from __future__ import annotations
import json,time
from pathlib import Path
import numpy as np
from run_convergence import DETECTORS,RESULTS_DIR,FOV_UM,BASE_WAVELENGTH_NM,asm_numpy,cell_coordinates,downsample_reference,summarize,utc_now
from run_regimes import make_field

Z=(0.,160.,240.,280.,320.,360.,400.,640.,1280.)
SHIFTS=(0.,.5)
REF=2048
TARGETS=(128,256,512)
SEP=8.0

def main():
    start=time.time(); rows=[]
    for shift in SHIFTS:
        # Reference is generated at high resolution with the same physical
        # coordinates and fixed 4um core depression.
        ref0,_,_=make_field((REF,REF),[(128-SEP/2,128,1),(128+SEP/2,128,-1)],shift_px=shift)
        _,_,dyr,dxr=cell_coordinates((REF,REF))
        for z in Z:
            ref=asm_numpy(ref0,z*1e-6,dxr,dyr,BASE_WAVELENGTH_NM)
            for n in TARGETS:
                sampled=downsample_reference(ref,(n,n))
                direct0,truth,_=make_field((n,n),[(128-SEP/2,128,1),(128+SEP/2,128,-1)],shift_px=shift)
                _,_,dy,dx=cell_coordinates((n,n)); direct=asm_numpy(direct0,z*1e-6,dx,dy,BASE_WAVELENGTH_NM)
                for det in DETECTORS:
                    a={'path':'reference_downsample','grid':n,'shift_px':shift,'z_um':z,'detector':det}
                    a.update(summarize(sampled,det,[] if z else truth,(n,n)))
                    b={'path':'direct_coarse','grid':n,'shift_px':shift,'z_um':z,'detector':det}
                    b.update(summarize(direct,det,[] if z else truth,(n,n)))
                    a['direct_count']=b['count'];a['path_difference']=a['count']-b['count'];rows.append(a)
    result={'experiment':'EXP-0015','stage':'close_pair_reference','timestamp_utc':utc_now(),'status':'CONFIRMATORY_RED_TEAM','separation_um':SEP,'reference_grid':REF,'z_um':Z,'shifts':SHIFTS,'grids':TARGETS,'rows':rows,'runtime_s':time.time()-start}
    p=RESULTS_DIR/f"close_pair_reference_{time.strftime('%Y%m%d_%H%M%S')}.json";p.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8');print('Wrote',p)

if __name__=='__main__':main()
