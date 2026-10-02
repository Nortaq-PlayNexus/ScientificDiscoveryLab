"""Summarize the root-level parallel runner without touching canonical outputs."""
from __future__ import annotations
import csv, hashlib, json, math
from pathlib import Path

ROOT = Path(r"C:\Users\natha\ScientificDiscoveryLab\AUDIT\SUBAGENT_EXP0003_BROADBAND_20260924")
P = (4, 6, 8, 12, 16, 24, 32, 48, 64)
SIGMAS = (0.10, 0.25, 0.50, 0.75)

def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))

def key(sig, p):
    return f"sigma_{sig:.2f}_p{p}"

def fnum(x, digits=6):
    return "NA" if x is None else f"{float(x):.{digits}f}"

def make_rows(which):
    d = load(f"primary_{which}_summary.json")
    out=[]
    for sig in SIGMAS:
        for p in P:
            x=d["grouped"][key(sig,p)]
            out.append({
                "route": which,
                "sigma_phys": sig,
                "p_pixels_per_wavelength": p,
                "n_fields": x["n_real_total"],
                "n_seeds": x["n_seeds"],
                "n_pred_discrete_px": x["n_pred_discrete_px"],
                "n_pred_continuum_px": x["n_pred_continuum_px"],
                "n_meas_px_mean": x["n_meas_px"]["mean"],
                "n_meas_px_ci95_low": x["n_meas_px"]["ci95"][0],
                "n_meas_px_ci95_high": x["n_meas_px"]["ci95"][1],
                "ratio_discrete_mean": x["ratio_discrete"]["mean"],
                "ratio_discrete_seedblock_ci95_low": x["seed_block_ratio_discrete"]["ci95"][0],
                "ratio_discrete_seedblock_ci95_high": x["seed_block_ratio_discrete"]["ci95"][1],
                "ratio_discrete_seedblock_ci99_low": x["seed_block_ratio_discrete"]["mean"] - 2.570581835636196 * x["seed_block_ratio_discrete"]["se"],
                "ratio_discrete_seedblock_ci99_high": x["seed_block_ratio_discrete"]["mean"] + 2.570581835636196 * x["seed_block_ratio_discrete"]["se"],
                "ratio_continuum_mean": x["ratio_continuum"]["mean"],
                "ratio_continuum_seedblock_ci95_low": x["seed_block_ratio_continuum"]["ci95"][0],
                "ratio_continuum_seedblock_ci95_high": x["seed_block_ratio_continuum"]["ci95"][1],
                "ratio_continuum_seedblock_ci99_low": x["seed_block_ratio_continuum"]["mean"] - 2.570581835636196 * x["seed_block_ratio_continuum"]["se"],
                "ratio_continuum_seedblock_ci99_high": x["seed_block_ratio_continuum"]["mean"] + 2.570581835636196 * x["seed_block_ratio_continuum"]["se"],
                "fd_over_discrete_mean": x["fd_pred_px"]["mean"] / x["n_pred_discrete_px"],
                "fft_over_discrete_mean": x["fft_pred_px"]["mean"] / x["n_pred_discrete_px"],
                "contour_over_discrete_mean": (x.get("contour_ratio_discrete") or {}).get("mean"),
                "naive_contour_over_discrete_mean": ((x.get("contour_naive_px") or {}).get("mean") / x["n_pred_discrete_px"] if x.get("contour_naive_px") else None),
                "half_shift_rel_mean": (x.get("shift_half_rel_delta") or {}).get("mean"),
                "irregular_shift_rel_mean": (x.get("shift_irregular_rel_delta") or {}).get("mean"),
                "charge_imbalance_mean": x["charge_imbalance"]["mean"],
            })
    return out

def write_csv(rows, path):
    fields=list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

def slope(vals):
    # ordinary least squares of ratio-1 against log2(P)
    xs=[math.log2(r["p_pixels_per_wavelength"]) for r in vals]
    ys=[r["ratio_continuum_mean"]-1 for r in vals]
    xm=sum(xs)/len(xs); ym=sum(ys)/len(ys)
    den=sum((x-xm)**2 for x in xs)
    return sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/den if den else float("nan")

def main():
    cert=make_rows("certified")
    pcg=make_rows("pcg64")
    rows=cert+pcg
    write_csv(rows, ROOT/"our_primary_convergence.csv")
    # Full table, with 95% seed-block intervals for the primary route.
    lines=[]
    lines += ["# Root-level parallel-runner numerical table", "",
              "Ratios are winding density / Kac–Rice prediction. `CI95` is the interval across six seed-block means; each seed has 8 realizations in the certified route and 4 in the PCG64 validation route. The CSV also contains normal-approximation 99% seed-block intervals (t critical value 2.57058). The full-spectrum denominator is the continuous Gaussian prediction; `D` is the sampled-mode denominator.", "",
              "## Certified route (primary)", "",
              "| sigma | P | n_pred(D) | n_pred(full) | ratio D [CI95] | ratio full [CI95] | FD/D | FFT/D | contour/D |", "|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in cert:
        c="NA" if r["contour_over_discrete_mean"] is None else fnum(r["contour_over_discrete_mean"],4)
        lines.append(f"| {r['sigma_phys']:.2f} | {r['p_pixels_per_wavelength']} | {fnum(r['n_pred_discrete_px'])} | {fnum(r['n_pred_continuum_px'])} | {fnum(r['ratio_discrete_mean'],5)} [{fnum(r['ratio_discrete_seedblock_ci95_low'],5)}, {fnum(r['ratio_discrete_seedblock_ci95_high'],5)}] | {fnum(r['ratio_continuum_mean'],5)} [{fnum(r['ratio_continuum_seedblock_ci95_low'],5)}, {fnum(r['ratio_continuum_seedblock_ci95_high'],5)}] | {fnum(r['fd_over_discrete_mean'],4)} | {fnum(r['fft_over_discrete_mean'],4)} | {c} |")
    lines += ["", "## Selected measured densities and predictions", "", "Values are per pixel cell; intervals are 95% field-bootstrap intervals in the raw root summary.", "", "| sigma | P | measured n | full prediction n | sampled prediction n | measured/full |", "|---:|---:|---:|---:|---:|---:|"]
    for sig in SIGMAS:
        for p in (4, 16, 64):
            r=next(x for x in cert if x["sigma_phys"]==sig and x["p_pixels_per_wavelength"]==p)
            lines.append(f"| {sig:.2f} | {p} | {fnum(r['n_meas_px_mean'])} [{fnum(r['n_meas_px_ci95_low'])}, {fnum(r['n_meas_px_ci95_high'])}] | {fnum(r['n_pred_continuum_px'])} | {fnum(r['n_pred_discrete_px'])} | {fnum(r['ratio_continuum_mean'],5)} |")
    lines += ["", "## Trends (certified route, full-spectrum ratio)", "", "| sigma | endpoint P4 | endpoint P64 | absolute-error improvement | OLS slope per doubling of P |", "|---:|---:|---:|---:|---:|"]
    for sig in SIGMAS:
        rr=[r for r in cert if r["sigma_phys"]==sig]
        a=rr[0]["ratio_continuum_mean"]-1; z=rr[-1]["ratio_continuum_mean"]-1
        lines.append(f"| {sig:.2f} | {fnum(rr[0]['ratio_continuum_mean'],5)} | {fnum(rr[-1]['ratio_continuum_mean'],5)} | {fnum(abs(a)-abs(z),5)} | {fnum(slope(rr),5)} |")
    lines += ["", "## PCG64 validation route", "", "| sigma | P4 | P6 | P8 | P12 | P16 | P24 | P32 | P48 | P64 |", "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for sig in SIGMAS:
        rr=[r for r in pcg if r["sigma_phys"]==sig]
        vals=[rr[P.index(r["p_pixels_per_wavelength"])] ["ratio_discrete_mean"] for r in rr]
        lines.append(f"| {sig:.2f} | "+" | ".join(fnum(v,5) for v in vals)+" |")
    lines += ["", "## Control artifacts from this root runner", "",
              "- `primary_certified_raw.csv`: 1,728 field rows; `primary_pcg64_raw.csv`: 864 validation rows.",
              "- `common_field_ref64_raw.csv` and `common_field_ref48_raw.csv`: exact nested common-field controls.",
              "- `lowpass_raw.csv`, `nonstandard_raw.csv`, `plane_wave_check_raw.csv`: targeted diagnostics.",
              "- Numerical negative values in continuum tail fractions in the raw diagnostics are quadrature roundoff (the true tail is zero at the quoted precision), not physical negative power.",
              ""]
    (ROOT/"REPORT").mkdir(exist_ok=True)
    (ROOT/"REPORT"/"EXP0003_BROADBAND_ROOT_RUN_TABLES.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    # Hash all root-run artifacts that are not shared with the other namespaced runner.
    names=["run_broadband_audit.py","run_environment.json","run_summary.json","primary_certified_raw.csv","primary_certified_summary.json","primary_pcg64_raw.csv","primary_pcg64_summary.json","common_field_ref64_raw.csv","common_field_ref64_summary.json","common_field_ref48_raw.csv","common_field_ref48_summary.json","lowpass_raw.csv","lowpass_summary.json","nonstandard_raw.csv","nonstandard_summary.json","plane_wave_check_raw.csv","plane_wave_check_summary.json","full_run.log","LITERATURE_SEARCH.md","CANONICAL_HASHES_NON_DESTRUCTIVE.json","extra_sanity_checks.py","extra_sanity_results.json","extra_sanity.log"]
    manifest={}
    for n in names:
        p=ROOT/n
        if p.exists(): manifest[n]={"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
    (ROOT/"OUR_ROOT_RUN_MANIFEST.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(ROOT/"REPORT"/"EXP0003_BROADBAND_ROOT_RUN_TABLES.md")

if __name__ == "__main__": main()
