#!/usr/bin/env python3
"""Fail-closed validation of the main EXP-0015 claims."""
from __future__ import annotations
import json,sys
from pathlib import Path
R=Path(__file__).resolve().parent.parent/'RESULTS'
def load(prefix):
    p=sorted(R.glob(prefix))[-1];return p,json.loads(p.read_text(encoding='utf-8'))

def main():
    checks=[]
    def check(name,condition,detail=''):
        checks.append({'check':name,'pass':bool(condition),'detail':detail})
    p,d=load('calibration_42_*.json')
    for case,truth in [('single_vortex',1),('vortex_pair',2),('four_vortex_lattice',4)]:
        rr=[r for r in d['rows'] if r['case']==case]
        check('calibration_'+case,all(r['count']==truth for r in rr),f'{len(rr)} rows')
    p,d=load('convergence_42_*.json')
    check('primary_convergence',all(r['count']==4 for r in d['grid_shift']),f'{len(d["grid_shift"])} grid/shift rows')
    check('primary_z_sweep',all(r['count']==4 for r in d['z_sweep']),f'{len(d["z_sweep"])} rows')
    p,d=load('oversample_42_*.json')
    check('square_reference_path',all(r['path_difference']==0 for r in d['rows']),f'{len(d["rows"])} rows')
    p,d=load('rectangular_reference_*.json')
    check('rectangular_reference',all(r['count']==4 for r in d['rows']),f'{len(d["rows"])} rows')
    p,d=load('independent_contour_*.json')
    check('independent_contour',all(r['count']==4 for r in d['rows']),f'{len(d["rows"])} rows')
    p,d=load('close_pair_reference_*.json')
    raw=[r for r in d['rows'] if r['detector']=='raw_winding' and r['grid']==256 and r['shift_px']==0]
    check('close_pair_transition',any(r['z_um']==240 and r['count']==2 for r in raw) and any(r['z_um']==320 and r['count']==0 for r in raw),f'{len(raw)} raw rows')
    p,d=load('exact_zero_*.json')
    pair=[r for r in d['rows'] if r['case']=='pair' and r['floor']==0 and r['detector']=='raw_winding']
    check('exact_zero_raw_pair',all(r['count']==2 for r in pair),f'{len(pair)} rows')
    result={'experiment':'EXP-0015','status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','checks':checks}
    (R/'validation_summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for x in checks: print(('PASS' if x['pass'] else 'FAIL'),x['check'],x['detail'])
    return 0 if result['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
