#!/usr/bin/env python3
"""High-resolution rectangular reference check for DVB-001."""
from __future__ import annotations
import json, time
from pathlib import Path
import numpy as np
from run_convergence import DETECTORS, RESULTS_DIR, FOV_UM, BASE_WAVELENGTH_NM, asm_numpy, cell_coordinates, downsample_reference, make_known_field, summarize, utc_now

SHAPES=((128,256),(256,128),(256,512),(512,256))
SHIFTS=(0.0,0.25,0.5,0.75)
Z=(640.0,1280.0)
REF=2048

def main():
    start=time.time(); rows=[]
    ref0,_,_=make_known_field((REF,REF),'four_vortex_lattice',shift_px=0.0,fov_um=FOV_UM)
    _,_,dyr,dxr=cell_coordinates((REF,REF))
    for z in Z:
        ref=asm_numpy(ref0,z*1e-6,dxr,dyr,BASE_WAVELENGTH_NM)
        for shape in SHAPES:
            for shift in SHIFTS:
                sampled=downsample_reference(ref,shape)
                direct0,truth,_=make_known_field(shape,'four_vortex_lattice',shift_px=shift)
                _,_,dy,dx=cell_coordinates(shape)
                direct=asm_numpy(direct0,z*1e-6,dx,dy,BASE_WAVELENGTH_NM)
                for det in DETECTORS:
                    a={"path":"reference_downsample","shape":list(shape),"shift_px":shift,"z_um":z,"detector":det}
                    a.update(summarize(sampled,det,[] if z else truth,shape))
                    b={"path":"direct_coarse","shape":list(shape),"shift_px":shift,"z_um":z,"detector":det}
                    b.update(summarize(direct,det,[] if z else truth,shape))
                    a["direct_count"]=b["count"]; a["path_difference"]=a["count"]-b["count"]
                    rows.append(a)
    result={"experiment":"EXP-0015","stage":"rectangular_reference_control","timestamp_utc":utc_now(),"reference_grid":REF,"shapes":SHAPES,"shifts":SHIFTS,"z_um":Z,"rows":rows,"runtime_s":time.time()-start,"status":"CONFIRMATORY_RED_TEAM"}
    p=RESULTS_DIR/f"rectangular_reference_{time.strftime('%Y%m%d_%H%M%S')}.json"; p.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8'); print('Wrote',p)

if __name__=='__main__': main()
