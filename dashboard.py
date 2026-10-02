"""Central dashboard for the AI Scientific Discovery Lab.

Scans the lab tree and renders a local HTML status page (evidence states, active
investigations, anomalies, experiments, machine info) + a console summary.

NO "discovery score". Evidence states only: UNTESTED / INITIAL RESULT / CONTROLLED /
REPLICATED / INDEPENDENTLY REPRODUCED / LITERATURE-CHECKED / EXTERNALLY VALIDATED.

Run:  python dashboard.py            (from ScientificDiscoveryLab)
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def _scan_investigations():
    base = os.path.join(ROOT, "03_INVESTIGATIONS")
    out = []
    if not os.path.isdir(base):
        return out
    for area in sorted(os.listdir(base)):
        area_path = os.path.join(base, area)
        if not os.path.isdir(area_path):
            continue
        for inv in sorted(os.listdir(area_path)):
            inv_path = os.path.join(area_path, inv)
            if os.path.isdir(inv_path):
                out.append({"area": area, "name": inv, "path": inv_path})
    return out


def _scan_anomalies():
    base = os.path.join(ROOT, "07_REPORTS", "anomaly_reports")
    out = []
    if os.path.isdir(base):
        for f in sorted(os.listdir(base)):
            if f.lower().startswith("anom-"):
                out.append(f)
    return out


def _scan_results():
    base = os.path.join(ROOT, "06_RESULTS")
    counts = {}
    if os.path.isdir(base):
        for d in ("confirmed", "inconclusive", "falsified", "anomalies"):
            p = os.path.join(base, d)
            counts[d] = len(os.listdir(p)) if os.path.isdir(p) else 0
    return counts


def _scan_registries():
    found = []
    for dirpath, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (
            ".git", "__pycache__", "05_DATA", "99_ARCHIVE")]
        for f in files:
            if f == "registry.jsonl":
                p = os.path.join(dirpath, f)
                n = 0
                with open(p, "r", encoding="utf-8") as fh:
                    for line in fh:
                        if line.strip():
                            n += 1
                found.append({"path": p, "rows": n})
    return found


def _machine():
    try:
        sys.path.insert(0, os.path.join(ROOT, "04_SHARED_ENGINE"))
        from engine.utilities.core import machine_info, version_info

        return {**machine_info(), "software": version_info()}
    except Exception as exc:  # pragma: no cover
        return {"error": str(exc)}


def console_report():
    inv = _scan_investigations()
    anom = _scan_anomalies()
    res = _scan_results()
    regs = _scan_registries()
    print("=" * 60)
    print("AI SCIENTIFIC DISCOVERY LAB — dashboard")
    print("=" * 60)
    print(f"Active investigations : {len(inv)}")
    for i in inv:
        print(f"  - {i['area']}/{i['name']}")
    print(f"Anomaly reports      : {len(anom)}")
    for a in anom:
        print(f"  - {a}")
    print("Result buckets       :")
    for k, v in res.items():
        print(f"  - {k}: {v}")
    print("Registries           :")
    for r in regs:
        print(f"  - {os.path.relpath(r['path'], ROOT)} ({r['rows']} rows)")
    print("Evidence ladder (lab max):")
    for s in ("UNTESTED", "INITIAL RESULT", "CONTROLLED", "REPLICATED",
              "INDEPENDENTLY REPRODUCED", "LITERATURE-CHECKED",
              "EXTERNALLY VALIDATED"):
        print(f"  - {s}")
    print("=" * 60)


def render_html():
    inv = _scan_investigations()
    anom = _scan_anomalies()
    res = _scan_results()
    regs = _scan_registries()
    m = _machine()

    rows = "\n".join(
        f"<tr><td>{i['area']}</td><td>{i['name']}</td><td>UNTESTED</td></tr>"
        for i in inv
    ) or "<tr><td colspan=3>none</td></tr>"

    anom_rows = "".join(f"<li>{a}</li>" for a in anom) or "<li>none</li>"

    res_rows = "".join(
        f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in res.items()
    )

    reg_rows = "".join(
        f"<tr><td>{os.path.relpath(r['path'], ROOT)}</td><td>{r['rows']}</td></tr>"
        for r in regs
    ) or "<tr><td colspan=2>none</td></tr>"

    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Discovery Lab Dashboard</title>
<style>
body{{font-family:Consolas,monospace;background:#101418;color:#dfe6ee;margin:2rem}}
h1{{color:#7ee2a8}}h2{{color:#8ab6ff;border-bottom:1px solid #2c3540;padding-bottom:.3rem}}
table{{border-collapse:collapse;margin:.5rem 0;width:100%;max-width:760px}}
td,th{{border:1px solid #2c3540;padding:.3rem .6rem;text-align:left;font-size:14px}}
th{{background:#1b232c}}td{{background:#131920}}
.ev{{color:#dfe6ee}}.warn{{color:#ffb86b}}ul{{line-height:1.6}}
</style></head><body>
<h1>AI Scientific Discovery Lab</h1>
<p>Evidence states only — no scores.</p>
<h2>Active investigations</h2>
<table><tr><th>Area</th><th>Investigation</th><th>Evidence</th></tr>{rows}</table>
<h2>Anomalies (ANOM-####)</h2><ul>{anom_rows}</ul>
<h2>Result buckets</h2><table>{res_rows}</table>
<h2>Registries</h2><table><tr><th>Registry</th><th>Rows</th></tr>{reg_rows}</table>
<h2>Evidence ladder (highest support a conclusion can claim here)</h2>
<ul><li>UNTESTED</li><li>INITIAL RESULT</li><li>CONTROLLED</li>
<li>REPLICATED</li><li>INDEPENDENTLY REPRODUCED</li><li>LITERATURE-CHECKED</li>
<li>EXTERNALLY VALIDATED</li></ul>
<h2>Machine</h2>
<pre>{json.dumps(m, indent=2, sort_keys=True)}</pre>
<p class="warn">Generated by dashboard.py · local only</p>
</body></html>"""
    out = os.path.join(ROOT, "dashboard.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    return out


if __name__ == "__main__":
    console_report()
    print("\nHTML ->", render_html())