#!/usr/bin/env python3
"""Independent SciPy circular-contour detector check; no main-module imports."""
from __future__ import annotations
import json,time
from pathlib import Path
import numpy as np
from scipy import fft as sfft
from scipy import ndimage

OUT=Path(__file__).resolve().parent.parent/'RESULTS';FOV=256.;WL=694.3

def field(shape,positions,shift=0.):
    h,w=shape;dx=FOV/w;dy=FOV/h;yy,xx=np.mgrid[:h,:w];x=(xx+.5)*dx;y=(yy+.5)*dy;ph=np.zeros(shape);core=np.ones(shape)
    for x0,y0,q in positions:
        x0+=shift*dx;y0+=shift*dy;ph+=q*np.arctan2(y-y0,x-x0);core*=1-.98*np.exp(-((x-x0)**2+(y-y0)**2)/(2*4**2))
    env=np.exp(-((x-FOV/2)**2+(y-FOV/2)**2)/(2*55**2));return(.03+.97*env*np.maximum(core,.02))*np.exp(1j*ph)

def prop(u,z,shape):
    dx=FOV/shape[1]*1e-6;dy=FOV/shape[0]*1e-6;fx=sfft.fftfreq(shape[1],d=dx);fy=sfft.fftfreq(shape[0],d=dy);kx,ky=np.meshgrid(2*np.pi*fx,2*np.pi*fy,indexing='xy');q=(2*np.pi/(WL*1e-9))**2-kx*kx-ky*ky;h=np.zeros(shape,complex);m=q>=0;h[m]=np.exp(1j*np.sqrt(q[m])*z*1e-6);return sfft.ifft2(sfft.fft2(u)*h)

def contour(u,radius=2.,points=32):
    a=np.abs(u)**2;mn=ndimage.minimum_filter(a,size=3,mode='nearest');yy,xx=np.where(a<=mn+1e-14);order=np.argsort(a[yy,xx]);yy=yy[order][:500];xx=xx[order][:500];sel=[];t=np.arange(points)*2*np.pi/points
    for y,x in zip(yy.tolist(),xx.tolist()):
        if y<3 or x<3 or y>=u.shape[0]-3 or x>=u.shape[1]-3:continue
        if any((y-sy)**2+(x-sx)**2<2.0 for sy,sx in sel):continue
        ph=[]
        for q in t:
            py=y+radius*np.sin(q);px=x+radius*np.cos(q);coords=np.array([[py],[px]])
            v=ndimage.map_coordinates(u.real,coords,order=1,mode='nearest')[0]+1j*ndimage.map_coordinates(u.imag,coords,order=1,mode='nearest')[0];ph.append(np.angle(v))
        ph=np.asarray(ph);w=np.rint(np.sum(np.angle(np.exp(1j*(np.roll(ph,-1)-ph))))/(2*np.pi)).astype(int)
        if abs(w)>=1:sel.append((y,x))
    return sel

def main():
    t=time.time();rows=[]
    for shape in ((64,64),(128,256),(256,128),(256,256)):
      for shift in (0.,.25,.5,.75):
        f=field(shape,[(100,100,1),(156,100,-1),(100,156,-1),(156,156,1)],shift)
        for z in (0.,1280.):
          u=f if z==0 else prop(f,z,shape);p=contour(u);rows.append({'shape':list(shape),'shift_px':shift,'z_um':z,'count':len(p),'positions':p})
    p=OUT/f"independent_contour_{time.strftime('%Y%m%d_%H%M%S')}.json";p.write_text(json.dumps({'experiment':'EXP-0015','implementation':'independent SciPy interpolation/contour','rows':rows,'runtime_s':time.time()-t},indent=2)+'\n');print('Wrote',p)
if __name__=='__main__':main()
