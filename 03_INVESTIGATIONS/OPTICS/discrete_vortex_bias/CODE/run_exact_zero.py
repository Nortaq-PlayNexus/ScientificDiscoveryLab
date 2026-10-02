#!/usr/bin/env python3
"""Exact-zero versus finite-floor analytical phase controls."""
from __future__ import annotations
import json,time
from pathlib import Path
import numpy as np
from run_convergence import DETECTORS,RESULTS_DIR,cell_coordinates,detect,match_records,utc_now

def make(shape,positions,floor,shift=0.):
    h,w=shape;yy,xx,dx,dy=cell_coordinates((h,w));ph=np.zeros(shape);amp=np.ones(shape);core=np.ones(shape)
    for x0,y0,q in positions:
        x=x0+shift*dx;y=y0+shift*dy;ph+=q*np.arctan2(yy-y,xx-x);core*=1-np.exp(-((xx-x)**2+(yy-y)**2)/(2*4**2))
    env=np.exp(-((xx-128)**2+(yy-128)**2)/(2*55**2));a=floor+(1-floor)*env*core;u=a*np.exp(1j*ph);u[np.abs(core)<1e-12]=0;return u

def main():
    rows=[];t=time.time();cases={'single':[(128,128,1)],'pair':[(124,128,1),(132,128,-1)],'four':[(100,104,1),(156,104,-1),(100,152,-1),(156,152,1)]}
    for name,pos in cases.items():
      for floor in (0.,.03):
       for n in (64,128,256,512):
        for shift in (0.,.25,.5,.75):
         u=make((n,n),pos,floor,shift);truth=[{'x_um':x+shift*(256/n),'y_um':y+shift*(256/n),'charge':q} for x,y,q in pos]
         for det in DETECTORS:
          rec=detect(u,det);charges=[int(r['charge']) for r in rec];rows.append({'case':name,'floor':floor,'grid':n,'shift_px':shift,'detector':det,'count':len(rec),'net_charge':sum(charges),'absolute_charge':sum(abs(q) for q in charges),'match':match_records(rec,truth,(n,n))})
    p=RESULTS_DIR/f"exact_zero_{time.strftime('%Y%m%d_%H%M%S')}.json";p.write_text(json.dumps({'experiment':'EXP-0015','stage':'exact_zero_control','rows':rows,'runtime_s':time.time()-t},indent=2)+'\n');print('Wrote',p)
if __name__=='__main__':main()
