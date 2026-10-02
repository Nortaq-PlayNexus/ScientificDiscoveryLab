#!/usr/bin/env python3
"""Independent EXP-0016 replication.

No imports from the main experiment or historical sandbox. This uses a
separately written field sampler, NumPy winding, SciPy labeling, and a simple
complex interpolation contour.
"""
from __future__ import annotations
import json, math, time
from pathlib import Path
import numpy as np
from scipy import ndimage
from scipy import fft as sfft

OUT = Path(__file__).resolve().parent.parent / "RESULTS"
FOV = 64.0
WL = 694.3


def grid(n):
    p = FOV / n
    c = (np.arange(n) + 0.5) * p
    return np.meshgrid(c, c, indexing="xy"), p


def make_field(n, q, mode):
    (x, y), p = grid(n)
    i = n // 2
    x0 = (i + 0.5) * p
    y0 = (i + 0.5) * p
    if mode == "half":
        x0 += p / 2; y0 += p / 2
    elif mode == "quarter":
        x0 += p / 4; y0 += p / 4
    r2 = (x - x0) ** 2 + (y - y0) ** 2
    core = 1.0 - 0.98 * np.exp(-r2 / (2 * 2.0**2))
    if abs(q) > 1:
        core = core ** (abs(q) / 2)
    field = core * np.exp(1j * q * np.arctan2(y - y0, x - x0))
    field *= np.exp(-((x - FOV / 2) ** 2 + (y - FOV / 2) ** 2) / (2 * 22.0**2))
    field /= np.max(np.abs(field))
    return field, {"x": x0, "y": y0, "q": q}


def winding(field):
    ph = np.angle(field)
    a, b, c, d = ph[:-1, :-1], ph[:-1, 1:], ph[1:, 1:], ph[1:, :-1]
    step = lambda u, v: np.angle(np.exp(1j * (u - v)))
    curl = step(b, a) + step(c, b) + step(d, c) + step(a, d)
    return np.rint(curl / (2 * np.pi)).astype(np.int8)


def raw(field):
    q = winding(field); yy, xx = np.where(q != 0)
    return [{"x": float(x + .5), "y": float(y + .5), "q": int(q[y, x])} for y, x in zip(yy, xx)]


def clustered(field):
    q = winding(field); out=[]
    for sign in (-1, 1):
        mask=q==sign
        if not mask.any(): continue
        lab,num=ndimage.label(mask, structure=np.ones((3,3),int))
        for k in range(1,num+1):
            yy,xx=np.where(lab==k);out.append({"x":float(xx.mean()+.5),"y":float(yy.mean()+.5),"q":int(q[yy,xx].sum())})
    return out


def interp(field, y, x):
    h,w=field.shape
    if y<0 or x<0 or y>h-1 or x>w-1:return 0j
    y0=int(math.floor(y));x0=int(math.floor(x));y1=min(y0+1,h-1);x1=min(x0+1,w-1);fy=y-y0;fx=x-x0
    return (1-fy)*(1-fx)*field[y0,x0]+(1-fy)*fx*field[y0,x1]+fy*(1-fx)*field[y1,x0]+fy*fx*field[y1,x1]


def contour(field, radius=2.0):
    a=np.abs(field)**2; order=np.argsort(a.ravel()); out=[]; chosen=[]
    h,w=a.shape
    for flat in order[:400]:
        y,x=divmod(int(flat),w)
        if y<3 or x<3 or y>=h-3 or x>=w-3:continue
        if any((x-sx)**2+(y-sy)**2<9 for sx,sy in chosen):continue
        ph=[]
        for t in np.arange(32)*2*np.pi/32:ph.append(np.angle(interp(field,y+radius*np.sin(t),x+radius*np.cos(t))))
        ph=np.asarray(ph);q=int(np.rint(np.sum(np.angle(np.exp(1j*(np.roll(ph,-1)-ph))))/(2*np.pi)))
        if q:
            chosen.append((x,y));out.append({"x":float(x),"y":float(y),"q":q})
    return out


def metrics(rec, truth):
    if not rec:return {"count":0,"abs":0,"signed":0}
    q=np.array([r["q"] for r in rec]);return {"count":len(rec),"abs":int(abs(q).sum()),"signed":int(q.sum())}


def main():
    start=time.time();rows=[]
    for n in (32,64,128,256):
        for q in (-2,-1,1,2):
            for mode in ("exact","half","quarter"):
                field,truth=make_field(n,q,mode)
                for name,fn in (("raw",raw),("clustered",clustered),("contour",contour)):
                    rec=fn(field)
                    # Raw records are plaquette cells.  Use the separately
                    # written same-sign clustering as the location proxy.
                    loc = clustered(field) if name == "raw" else rec
                    m = metrics(rec, truth)
                    lm = metrics(loc, truth)
                    m.update({
                        "grid": n, "q": q, "mode": mode, "detector": name,
                        "record_count": m["count"], "raw_nonzero_cell_count": m["count"] if name == "raw" else None,
                        "winding_cell_count": m["count"] if name in ("raw", "clustered") else None,
                        "location_count": lm["count"], "component_count": lm["count"],
                        "location_absolute_charge": lm["abs"], "location_signed_charge": lm["signed"],
                        "truth_count": 1, "truth_abs": abs(q), "truth_signed": q,
                        "location_count_error": abs(lm["count"] - 1),
                        "absolute_charge_error": abs(m["abs"] - abs(q)),
                        "signed_charge_error": abs(m["signed"] - q),
                    })
                    rows.append(m)
    result={"experiment":"EXP-0016","implementation":"independent NumPy/SciPy","rows":rows,"runtime_s":time.time()-start}
    p=OUT/f"independent_topology_replication_{time.strftime('%Y%m%d_%H%M%S')}.json";p.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print('Wrote',p)
if __name__=='__main__':main()
