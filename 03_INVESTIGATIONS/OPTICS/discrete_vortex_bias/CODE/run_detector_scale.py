#!/usr/bin/env python3
"""EXP-0015 detector-size experiment for close known vortex pairs."""
from __future__ import annotations
import json, time
from pathlib import Path
import numpy as np
from run_convergence import RESULTS_DIR, FOV_UM, match_records, make_known_field, local_minimum_contour, utc_now

GRIDS=(64,96,128,192,256,384,512)
SEPARATIONS=(2.,4.,6.,8.,12.,16.,24.,32.,48.)
SHIFTS=(0.,.25,.5,.75)
RADII=(1.,1.5,2.,2.5,3.,4.,5.)

def main():
    start=time.time(); rows=[]
    for n in GRIDS:
        for sep in SEPARATIONS:
            for shift in SHIFTS:
                f,truth,meta=make_known_field((n,n),'vortex_pair',shift_px=shift)
                # Replace the default pair geometry with a controlled close
                # pair while keeping the same physical field conventions.
                yy,xx,dx,dy=__import__('run_convergence').cell_coordinates((n,n))
                phase=np.zeros((n,n)); core=np.ones((n,n));
                # Rebuild directly to avoid relying on the default separation.
                for x0,y0,q in ((128-sep/2,128,1),(128+sep/2,128,-1)):
                    x=x0+shift*dx; y=y0+shift*dy
                    phase += q*np.arctan2(yy-y,xx-x)
                    core *= 1-.98*np.exp(-((xx-x)**2+(yy-y)**2)/(2*4**2))
                env=np.exp(-((xx-128)**2+(yy-128)**2)/(2*55**2))
                f=(.03+.97*env*np.maximum(core,.02))*np.exp(1j*phase)
                truth=[{'x_um':128-sep/2+shift*dx,'y_um':128+shift*dy,'charge':1},{'x_um':128+sep/2+shift*dx,'y_um':128+shift*dy,'charge':-1}]
                for radius in RADII:
                    rec=local_minimum_contour(f,radius=radius,n_points=32,max_candidates=1000)
                    charges=[int(r['charge']) for r in rec]
                    row={'grid':n,'separation_um':sep,'pixels_per_separation':sep/dx,'shift_px':shift,'radius_px':radius,'count':len(rec),'net_charge':sum(charges),'absolute_charge':sum(abs(q) for q in charges),'truth':2}
                    row['match']=match_records(rec,truth,(n,n),tolerance_px=max(1.5,2*radius))
                    rows.append(row)
    result={'experiment':'EXP-0015','stage':'detector_size','timestamp_utc':utc_now(),'status':'EXPLORATORY_SCALING','parameters':{'grids':GRIDS,'separations_um':SEPARATIONS,'shifts':SHIFTS,'radii_px':RADII},'rows':rows,'runtime_s':time.time()-start}
    p=RESULTS_DIR/f"detector_size_{time.strftime('%Y%m%d_%H%M%S')}.json";p.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8');print('Wrote',p)

if __name__=='__main__':main()
