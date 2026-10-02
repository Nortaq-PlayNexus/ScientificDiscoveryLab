#!/usr/bin/env python3
"""Independent SciPy raw-winding check for the close-pair transition."""
from __future__ import annotations
import json,time
from pathlib import Path
import numpy as np
from scipy import fft as sfft

OUT=Path(__file__).resolve().parent.parent/'RESULTS'
FOV=256.;WL=694.3;SEP=8.;Z=(0.,160.,240.,280.,320.,360.,400.,640.,1280.)

def field(n,shift=0.):
    p=FOV/n;y,x=np.meshgrid((np.arange(n)+.5)*p,(np.arange(n)+.5)*p,indexing='ij');ph=np.zeros((n,n));core=np.ones((n,n))
    for x0,y0,q in ((128-SEP/2,128,1),(128+SEP/2,128,-1)):
        xx=x0+shift*p; yy=y0+shift*p; ph+=q*np.arctan2(y-yy,x-xx);core*=1-.98*np.exp(-((x-xx)**2+(y-yy)**2)/(2*4**2))
    env=np.exp(-((x-128)**2+(y-128)**2)/(2*55**2));return(.03+.97*env*np.maximum(core,.02))*np.exp(1j*ph)

def prop(u,n,z):
    p=FOV/n*1e-6;fx=sfft.fftfreq(n,d=p);fy=sfft.fftfreq(n,d=p);kx,ky=np.meshgrid(2*np.pi*fx,2*np.pi*fy,indexing='xy');q=(2*np.pi/(WL*1e-9))**2-kx*kx-ky*ky;h=np.zeros((n,n),complex);m=q>=0;h[m]=np.exp(1j*np.sqrt(q[m])*z*1e-6);return sfft.ifft2(sfft.fft2(u)*h)

def count(u):
    ph=np.angle(u);a,b,c,d=ph[:-1,:-1],ph[:-1,1:],ph[1:,1:],ph[1:,:-1];dd=lambda x,y:np.angle(np.exp(1j*(x-y)));q=np.rint((dd(b,a)+dd(c,b)+dd(d,c)+dd(a,d))/(2*np.pi));return int(np.count_nonzero(q)),int(q.sum())

def main():
    rows=[];t=time.time()
    for n in (128,256,512):
      for shift in (0.,.5):
       u0=field(n,shift)
       for z in Z:
        c,nq=count(prop(u0,n,z));rows.append({'grid':n,'shift_px':shift,'z_um':z,'count':c,'net_charge':nq})
    p=OUT/f"independent_close_{time.strftime('%Y%m%d_%H%M%S')}.json";p.write_text(json.dumps({'experiment':'EXP-0015','implementation':'independent SciPy FFT/raw winding','rows':rows,'runtime_s':time.time()-t},indent=2)+'\n');print('Wrote',p)
if __name__=='__main__':main()
