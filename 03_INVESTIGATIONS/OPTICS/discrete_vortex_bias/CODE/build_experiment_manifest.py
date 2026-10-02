#!/usr/bin/env python3
"""Create the hash-bound EXP-0015 result manifest."""
from __future__ import annotations
import hashlib, json, platform, sys, time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
LAB = EXP.parents[2]
RESULTS = EXP / "RESULTS"
CONFIG = EXP / "CONFIG"
sys.path.insert(0, str(LAB / "04_SHARED_ENGINE"))
from engine.hypothesis_testing.prereg import verify_frozen_config, verify_change_log


def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def main() -> int:
    prereg_path=CONFIG/'prereg_EXP-0015.json'
    prereg=verify_frozen_config(prereg_path, expected={'experiment_id':'EXP-0015','hypothesis_id':'HYP-OPT-DVB-001','question_id':'Q-O006'})
    changes=verify_change_log(CONFIG/'changes.jsonl')
    artifacts=[]
    for p in sorted(RESULTS.iterdir()):
        if p.is_file() and p.name!='experiment.json':
            artifacts.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
    result={
      'schema_version':'1.0',
      'experiment_id':'EXP-0015',
      'status':'PARTIAL / LEVEL 1 / NO_NOVELTY_CLAIM',
      'generated_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
      'preregistration':{'path':str(prereg_path),'config_sha256':prereg['config_sha256']},
      'change_log':{'path':str(CONFIG/'changes.jsonl'),'entries':len(changes),'head':changes[-1]['entry_hash'] if changes else None},
      'environment':{'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'numpy':np.__version__},
      'artifacts':artifacts,
      'note':'This manifest is a provenance index. It does not promote any candidate or authorize a physical claim.'
    }
    out=RESULTS/'experiment.json'; out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'Wrote {out} with {len(artifacts)} artifacts and {len(changes)} logged changes')
    return 0

if __name__=='__main__': raise SystemExit(main())
