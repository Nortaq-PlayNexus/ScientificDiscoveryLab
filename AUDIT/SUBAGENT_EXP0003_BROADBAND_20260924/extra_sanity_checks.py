"""Small non-destructive sanity checks for the root-level EXP-0003 audit."""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import run_broadband_audit as a

def corrected_real(shape,S,g):
    ny,nx=shape
    z=np.sqrt(S)*(g.standard_normal(shape)+1j*g.standard_normal(shape))
    iy=(-np.arange(ny))%ny; ix=(-np.arange(nx))%nx
    z=.5*(z+np.conj(z[np.ix_(iy,ix)]))
    for j,i in {(0,0),(0,nx//2),(ny//2,0),(ny//2,nx//2)}:
        z[j,i]=np.sqrt(S[j,i])*g.standard_normal()
    return np.fft.ifft2(z).real

def main():
    out={"description":"Read-only implementation and determinism checks; no canonical output is touched."}
    # Exact same-stream rerun: same field and count, determinism only.
    shape=(128,128); s,kx,ky,kr,k0,sig=a.gaussian_spectrum(shape,4,.75)
    label="EXP-0003-extra-determinism-p4-sig0.75-s42"
    g1,_=a.make_gen("certified",label,42); g2,_=a.make_gen("certified",label,42)
    e1=a.complex_field_canonical(shape,s,g1); e2=a.complex_field_canonical(shape,s,g2)
    n1=a.winding_counts(e1,4)[0]; n2=a.winding_counts(e2,4)[0]
    out["same_stream"]={"field_bitwise_equal":bool(np.array_equal(e1,e2)),"max_abs_field_difference":float(np.max(np.abs(e1-e2))),"density_equal":n1==n2,"density":n1}
    # Historical nested normalization, with Parseval-compatible target power.
    g,_=a.make_gen("certified","EXP-0003-extra-normalization",42)
    e=a.complex_field_canonical(shape,s,g)
    # For ifft2 convention, target mean power is sum(S)/N^4; historical route is half.
    target=float(s.sum()/(shape[0]**4)); measured=float(np.mean(np.abs(e)**2))
    out["historical_normalization"]={"measured_over_target":measured/target,"target_mean_power":target,"measured_mean_power":measured}
    # Corrected real-component route calibration and self-conjugate power fraction.
    g,_=a.make_gen("pcg64","EXP-0003-extra-corrected",42)
    u=corrected_real(shape,s/2,g); v=corrected_real(shape,s/2,g)
    # Corrected real field uses S/2 per component; total E target is sum(S)/N^4.
    out["corrected_construction"]={"measured_over_target":float(np.mean(np.abs(u+1j*v)**2)/target)}
    ny,nx=shape; iy=(-np.arange(ny))%ny; ix=(-np.arange(nx))%nx
    selfmask=np.fromfunction(lambda i,j: (i==iy[i])&(j==ix[j]), (ny,nx), dtype=int).astype(bool)
    out["self_conjugate_power_fraction"]=float(s[selfmask].sum()/s.sum())
    out["self_conjugate_bins"]=int(selfmask.sum())
    # Principal edge phase diagnostic on one field.
    out["phase_edges"]=a.phase_edge_stats(e1)
    (HERE/"extra_sanity_results.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=="__main__": main()
