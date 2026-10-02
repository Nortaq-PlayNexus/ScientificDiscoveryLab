#!/usr/bin/env python3
"""Small-domain direct Fresnel reference for the propagation control."""
from __future__ import annotations
import json,time
from pathlib import Path
import numpy as np
from run_convergence import RESULTS_DIR,asm_numpy,cell_coordinates,make_known_field,utc_now

def direct_fresnel(u,z_um,dx_um,wl_nm):
    n=u.shape[0]; dx=dx_um*1e-6; lam=wl_nm*1e-9; z=z_um*1e-6; k=2*np.pi/lam
    coord=(np.arange(n)-(n-1)/2)*dx
    pref=np.exp(1j*k*z)/(1j*lam*z)
    out=np.zeros((n,n),complex)
    # Evaluate only an 8x8 central ROI against every input sample. This is a
    # deliberately small direct-space reference, not a production propagator.
    roi=np.arange(n//2-4,n//2+4)
    for oy in roi:
      for ox in roi:
        rp=np.sqrt((coord[ox]-coord[None,:])**2+(coord[oy]-coord[:,None])**2)
        kernel=np.exp(1j*np.pi/(lam*z)*rp**2)
        out[oy,ox]=pref*np.sum(u*kernel)*dx*dx
    return out

def main():
    t=time.time();rows=[]
    for n in (16,24,32):
      f,_,_=make_known_field((n,n),'four_vortex_lattice',amp_floor=.03)
      _,_,dy,dx=cell_coordinates((n,n))
      for z in (10.,50.,100.):
        a=asm_numpy(f,z*1e-6,dx,dy,694.3); d=direct_fresnel(f,z,dx,694.3)
        roi=np.s_[n//2-4:n//2+4,n//2-4:n//2+4]
        aa=a[roi].ravel();dd=d[roi].ravel()
        scale=np.vdot(aa,dd)/max(np.vdot(aa,aa),1e-30)
        residual=dd-scale*aa
        ncc=float(1-np.linalg.norm(residual)/max(np.linalg.norm(dd),1e-30))
        ia=np.abs(aa)**2;id=np.abs(dd)**2
        intensity_ncc=float(abs(np.vdot(ia-id,ia))/(np.linalg.norm(ia-id)*np.linalg.norm(id))) if np.linalg.norm(ia-id)>0 else 1.0
        rows.append({'grid':n,'z_um':z,'ncc_direct_vs_asm_after_scalar':ncc,'intensity_ncc_direct_vs_asm':intensity_ncc,'max_abs_error_after_scalar':float(np.max(np.abs(d[roi]-scale*a[roi]))) if ncc is not None else None})
    p=RESULTS_DIR/f"direct_reference_{time.strftime('%Y%m%d_%H%M%S')}.json";p.write_text(json.dumps({'experiment':'EXP-0015','stage':'direct_reference','rows':rows,'runtime_s':time.time()-t},indent=2)+'\n');print('Wrote',p)
if __name__=='__main__':main()
