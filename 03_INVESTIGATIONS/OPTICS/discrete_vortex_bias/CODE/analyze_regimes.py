#!/usr/bin/env python3
"""Summarize the latest exploratory regime map without promotion logic."""
from __future__ import annotations
import glob,json,statistics
from pathlib import Path
from run_convergence import RESULTS_DIR, utc_now

files=sorted(glob.glob(str(RESULTS_DIR/'exploratory_regime_map_*.json')))
if not files: raise SystemExit('no exploratory regime result yet')
d=json.loads(Path(files[-1]).read_text(encoding='utf-8'))
rows=d['rows']
summary={}
for regime in sorted(set(r['regime'] for r in rows)):
    rr=[r for r in rows if r['regime']==regime]
    by={}
    for det in sorted(set(r['detector'] for r in rr)):
        dr=[r for r in rr if r['detector']==det]
        by[det]={
            'rows':len(dr),
            'count_min':min(r['count'] for r in dr),
            'count_max':max(r['count'] for r in dr),
            'count_mean':statistics.mean(r['count'] for r in dr),
            'net_charge_min':min(r['net_charge'] for r in dr),
            'net_charge_max':max(r['net_charge'] for r in dr),
            'absolute_charge_min':min(r.get('absolute_charge',r['count']) for r in dr),
            'absolute_charge_max':max(r.get('absolute_charge',r['count']) for r in dr),
        }
    summary[regime]=by
# close-pair resolution table at z=0, where truth is valid
close=[r for r in rows if r['regime']=='close_pair' and r['z_um']==0]
resolution={}
for det in sorted(set(r['detector'] for r in close)):
    resolution[det]={}
    for n in sorted(set(r['grid'] for r in close)):
        vals=[]
        for sep in sorted(set(r['separation_um'] for r in close)):
            cell=[r for r in close if r['detector']==det and r['grid']==n and r['separation_um']==sep]
            if cell and all(r['count']==2 for r in cell): vals.append(sep)
        resolution[det][str(n)]={'min_resolved_separation_um':min(vals) if vals else None,'all_shifts_resolved':bool(vals)}
# detector disagreement cells
by_key={}
for r in rows:
    key=tuple(r.get(k) for k in ('regime','grid','shift_px','z_um','separation_um','charge','pitch_um','random_band'))
    by_key.setdefault(key,[]).append(r)
disagreements=[]
for key,rr in by_key.items():
    counts={r['detector']:r['count'] for r in rr}
    if len(set(counts.values()))>1:
        disagreements.append({'key':list(key),'counts':counts})
summary={'experiment':'EXP-0015','stage':'regime_analysis','timestamp_utc':utc_now(),'source':files[-1],'by_regime':summary,'close_pair_resolution':resolution,'disagreement_cell_count':len(disagreements),'disagreement_examples':disagreements[:100]}
out=RESULTS_DIR/'regime_analysis.json';out.write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n',encoding='utf-8')
md=['# Exploratory regime analysis','',f'Source: `{files[-1]}`','', 'This is descriptive; it is not a promoted confirmatory result.','', '## Detector disagreement cells','',f'Disagreement cells: **{len(disagreements)}**. This counts cells where detector outputs differ, not independent hypothesis tests.','', '| Regime | Detector | Count range | Mean count | Net-charge range |', '|---|---|---:|---:|---:|']
for regime,by in summary['by_regime'].items():
 for det,v in by.items(): md.append(f"| {regime} | {det} | {v['count_min']}–{v['count_max']} | {v['count_mean']:.3f} | {v['net_charge_min']}–{v['net_charge_max']} |")
md += ['', '## Close-pair resolution (z=0 only)', '', '| Detector | Grid | Minimum separation resolved for all shifts |', '|---|---:|---:|']
for det,by in resolution.items():
 for n,v in by.items(): md.append(f"| {det} | {n} | {v['min_resolved_separation_um']} |")
md += ['', '## Interpretation guard', '', 'A count disagreement is not automatically a physical discrepancy. Charge representation, contour radius, initial-position truth, and detector semantics must be checked first. The 2048² reference controls are the arbiter for downsampling artifacts.']
(RESULTS_DIR/'REGIME_ANALYSIS.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print('Wrote',out)
