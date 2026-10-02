#!/usr/bin/env python3
"""Exploratory individual-feature tracker across propagation planes.

The tracker reports detector events, not physical creation/annihilation. A
birth/death label is retained only as a detector-event label until an
oversampled complex-field reference and independent locator confirm it.
"""
from __future__ import annotations
import json,time
from pathlib import Path
import numpy as np
from scipy.optimize import linear_sum_assignment
from run_convergence import RESULTS_DIR, BASE_WAVELENGTH_NM, asm_numpy, cell_coordinates, detect, make_known_field, utc_now

Z=(0.,40.,80.,120.,160.,200.,240.,320.,400.,480.,560.,640.,720.,800.,880.,960.,1040.,1120.,1200.,1280.,1360.,1440.,1520.,1600.)


def track(rows, previous, max_step=8.0):
    current=[(float(r['x']),float(r['y']),int(r['charge'])) for r in rows]
    matches=[]; births=[]; deaths=[]
    if previous and current:
        cost=np.array([[np.hypot(x-px,y-py) for px,py,_ in previous] for x,y,_ in current])
        ri,ci=linear_sum_assignment(cost)
        usedp=set(); usedc=set()
        for i,j in zip(ri,ci):
            if cost[i,j] <= max_step and previous[j][2]==current[i][2]:
                matches.append({'previous_index':int(j),'current_index':int(i),'distance_px':float(cost[i,j]),'charge':int(current[i][2])})
                usedp.add(j);usedc.add(i)
        births=[{'current_index':i,'x':current[i][0],'y':current[i][1],'charge':current[i][2]} for i in range(len(current)) if i not in usedc]
        deaths=[{'previous_index':j,'x':previous[j][0],'y':previous[j][1],'charge':previous[j][2]} for j in range(len(previous)) if j not in usedp]
    else:
        births=[{'current_index':i,'x':current[i][0],'y':current[i][1],'charge':current[i][2]} for i in range(len(current))]
        deaths=[{'previous_index':j,'x':previous[j][0],'y':previous[j][1],'charge':previous[j][2]} for j in range(len(previous))]
    return current,matches,births,deaths

def main():
    start=time.time(); all_rows=[]
    for case,sep in [('four_vortex_lattice',None),('vortex_pair',8.0)]:
        for detector in ('raw_winding','clustered_winding','supported_clustered_winding','local_minimum_contour'):
            previous=[]; prev_z=None
            for z in Z:
                n=256
                if sep is None:
                    f,truth,_=make_known_field((n,n),case,shift_px=0.0)
                else:
                    yy,xx,dx,dy=cell_coordinates((n,n)); phase=np.zeros((n,n)); core=np.ones((n,n))
                    for x0,y0,q in ((128-sep/2,128,1),(128+sep/2,128,-1)):
                        phase+=q*np.arctan2(yy-y0,xx-x0); core*=1-.98*np.exp(-((xx-x0)**2+(yy-y0)**2)/(2*4**2))
                    env=np.exp(-((xx-128)**2+(yy-128)**2)/(2*55**2)); f=(.03+.97*env*np.maximum(core,.02))*np.exp(1j*phase)
                _,_,dy,dx=cell_coordinates((n,n)); out=asm_numpy(f,z*1e-6,dx,dy,BASE_WAVELENGTH_NM); rec=detect(out,detector); current,matches,births,deaths=track(rec,previous)
                all_rows.append({'case':case,'separation_um':sep,'detector':detector,'z_um':z,'count':len(current),'net_charge':sum(q for _,_,q in current),'positions':current,'matches':matches,'births':births,'deaths':deaths})
                previous=current;prev_z=z
    result={'experiment':'EXP-0015','stage':'individual_tracker','timestamp_utc':utc_now(),'status':'EXPLORATORY_DETECTOR_EVENTS','z_um':Z,'rows':all_rows,'runtime_s':time.time()-start}
    p=RESULTS_DIR/f"tracker_{time.strftime('%Y%m%d_%H%M%S')}.json";p.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8');print('Wrote',p)

if __name__=='__main__':main()
