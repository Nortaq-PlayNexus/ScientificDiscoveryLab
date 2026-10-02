"""Summarize EXP-0003 independent audit outputs into concise tables."""
from __future__ import annotations
import csv, json, math
from pathlib import Path
from collections import defaultdict
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RES = ROOT / "RESULTS"


def read_csv(name):
    p = RES / name
    if not p.exists():
        return []
    with p.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def f(r, k, default=float("nan")):
    try:
        return float(r[k])
    except Exception:
        return default


def mean(vals):
    vals = [float(x) for x in vals if x is not None and np.isfinite(float(x))]
    return float(np.mean(vals)) if vals else float("nan")


def main():
    main_rows = read_csv("main_summary.csv")
    verdicts = []
    for s in (0.1, 0.25, 0.5, 0.75):
        rr = sorted([r for r in main_rows if abs(f(r, "sigma_exp_rad_per_pixel_at_P4") - s) < 1e-9], key=lambda r: f(r, "p_pixels_per_wavelength"))
        byp = {int(round(f(r, "p_pixels_per_wavelength"))): r for r in rr}
        rec = {"sigma_k": s, "n_conditions": len(rr), "p_values": [int(round(f(r, "p_pixels_per_wavelength"))) for r in rr]}
        for p in (4, 6, 8, 12, 16, 24, 32, 48, 64):
            if p in byp:
                r = byp[p]
                rec[f"P{p}_ratio_full"] = f(r, "ratio_cont_full_mean")
                rec[f"P{p}_ratio_full_ci99_low"] = f(r, "ratio_cont_full_ci99_low")
                rec[f"P{p}_ratio_full_ci99_high"] = f(r, "ratio_cont_full_ci99_high")
                rec[f"P{p}_ratio_discrete"] = f(r, "ratio_discrete_mean")
                rec[f"P{p}_fd_forward_over_discrete"] = f(r, "fd_forward_over_discrete_mean")
                rec[f"P{p}_fd_central_over_discrete"] = f(r, "fd_central_over_discrete_mean")
        if rr:
            r0, rlast = rr[0], rr[-1]
            rec.update({
                "trend_slope_per_doubling": f(r0, "ratio_cont_full_trend_slope_per_doubling"),
                "trend_pvalue": f(r0, "ratio_cont_full_trend_pvalue"),
                "endpoint_improvement_abs_error": f(r0, "ratio_cont_full_endpoint_improvement"),
                "P4_ratio_discrete": f(r0, "ratio_discrete_mean"),
                "P64_ratio_discrete": f(rlast, "ratio_discrete_mean"),
                "P4_ratio_full": f(r0, "ratio_cont_full_mean"),
                "P64_ratio_full": f(rlast, "ratio_cont_full_mean"),
                "P4_fd_forward": f(r0, "fd_forward_over_discrete_mean"),
                "P64_fd_forward": f(rlast, "fd_forward_over_discrete_mean"),
                "P4_fd_central": f(r0, "fd_central_over_discrete_mean"),
                "P64_fd_central": f(rlast, "fd_central_over_discrete_mean"),
            })
            # A deliberately conservative operational flag: the last four
            # resolutions are all within 3% of one in point estimate.
            tail = [f(r, "ratio_cont_full_mean") for r in rr if f(r, "p_pixels_per_wavelength") >= 16]
            rec["tail_P_ge_16_all_within_3pct"] = bool(tail and max(abs(x - 1) for x in tail) <= 0.03)
            rec["systematic_endpoint_improvement"] = bool(rec["endpoint_improvement_abs_error"] > 0)
        verdicts.append(rec)
    (RES / "condition_verdicts.json").write_text(json.dumps(verdicts, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (RES / "condition_verdicts.csv").open("w", newline="", encoding="utf-8") as fh:
        keys = []
        for r in verdicts:
            for k in r:
                if k not in keys: keys.append(k)
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(verdicts)

    controls = {}
    detail = read_csv("detail_controls.csv")
    if detail:
        controls["detail_by_sigma_P"] = []
        for key in sorted({(f(r, "p_pixels_per_wavelength"), f(r, "sigma_exp_rad_per_pixel_at_P4")) for r in detail}):
            rr = [r for r in detail if (f(r, "p_pixels_per_wavelength"), f(r, "sigma_exp_rad_per_pixel_at_P4")) == key]
            controls["detail_by_sigma_P"].append({
                "P": key[0], "sigma_k": key[1], "n": len(rr),
                "D1_ratio_discrete": mean(f(r, "ratio_discrete") for r in rr),
                "D2_ratio_discrete": mean(f(r, "ratio_contour_discrete") for r in rr),
                "D2_over_D1": mean((f(r, "ratio_contour_discrete") / f(r, "ratio_discrete")) for r in rr),
                "max_half_shift_rel_delta": max(f(r, "shift_0p5_0p5_rel_delta") for r in rr),
                "max_arbitrary_shift_rel_delta": max(max(f(r, "shift_0p37_0p13_rel_delta"), f(r, "shift_minus0p23_0p41_rel_delta")) for r in rr),
                "fd_forward_over_discrete": mean(f(r, "fd_forward_over_discrete") for r in rr),
                "fd_central_over_discrete": mean(f(r, "fd_central_over_discrete") for r in rr),
            })
    interp = read_csv("interpolation_controls.csv")
    if interp:
        controls["interpolation"] = []
        for key in sorted({(f(r, "p_pixels_per_wavelength"), f(r, "sigma_exp_rad_per_pixel_at_P4"), f(r, "refinement_factor")) for r in interp}):
            rr = [r for r in interp if (f(r, "p_pixels_per_wavelength"), f(r, "sigma_exp_rad_per_pixel_at_P4"), f(r, "refinement_factor")) == key]
            controls["interpolation"].append({"P": key[0], "sigma_k": key[1], "factor": key[2], "n": len(rr), "original_ratio": mean(f(r, "ratio_original") for r in rr), "refined_ratio": mean(f(r, "ratio_refined") for r in rr), "gain": mean(f(r, "refinement_gain") for r in rr)})
    low = read_csv("lowpass_controls.csv")
    if low:
        controls["lowpass"] = []
        for key in sorted({(f(r, "p_pixels_per_wavelength"), f(r, "sigma_exp_rad_per_pixel_at_P4"), f(r, "cutoff_over_k0")) for r in low}):
            rr = [r for r in low if (f(r, "p_pixels_per_wavelength"), f(r, "sigma_exp_rad_per_pixel_at_P4"), f(r, "cutoff_over_k0")) == key]
            controls["lowpass"].append({"P": key[0], "sigma_k": key[1], "cutoff_over_k0": key[2], "n": len(rr), "ratio_discrete": mean(f(r, "ratio_discrete") for r in rr), "ratio_cont_trunc": mean(f(r, "ratio_cont_trunc") for r in rr), "ratio_cont_full": mean(f(r, "ratio_cont_full") for r in rr)})
    fixed = read_csv("fixed_field_controls.csv")
    if fixed:
        controls["fixed_field"] = []
        for key in sorted({(f(r, "p_pixels_per_wavelength"), f(r, "sigma_exp_rad_per_pixel_at_P4")) for r in fixed}):
            rr = [r for r in fixed if (f(r, "p_pixels_per_wavelength"), f(r, "sigma_exp_rad_per_pixel_at_P4")) == key]
            controls["fixed_field"].append({"P": key[0], "sigma_k": key[1], "n": len(rr), "ratio_cont_full": mean(f(r, "ratio_cont_full") for r in rr), "ratio_to_master_d1": mean(f(r, "ratio_to_master_d1") for r in rr), "ratio_discrete": mean(f(r, "ratio_discrete") for r in rr), "alias_power_fraction": mean(f(r, "alias_power_fraction_master_above_coarse_nyquist") for r in rr)})
    nonsquare = read_csv("non_square_controls.csv")
    if nonsquare:
        controls["non_square"] = []
        for label in sorted({r.get("grid_label", "") for r in nonsquare}):
            rr = [r for r in nonsquare if r.get("grid_label", "") == label]
            controls["non_square"].append({"grid": label, "n": len(rr), "ratio_discrete": mean(f(r, "ratio_discrete") for r in rr), "ratio_cont_full": mean(f(r, "ratio_cont_full") for r in rr)})
    construction = read_csv("construction_controls.csv")
    if construction:
        controls["independent_construction"] = []
        for key in sorted({(f(r, "p_pixels_per_wavelength"), f(r, "sigma_exp_rad_per_pixel_at_P4")) for r in construction}):
            rr = [r for r in construction if (f(r, "p_pixels_per_wavelength"), f(r, "sigma_exp_rad_per_pixel_at_P4")) == key]
            controls["independent_construction"].append({"P": key[0], "sigma_k": key[1], "n": len(rr), "corrected_ratio": mean(f(r, "corrected_real_component_ratio") for r in rr), "direct_complex_ratio": mean(f(r, "direct_complex_fourier_ratio") for r in rr), "direct_minus_corrected": mean(f(r, "direct_minus_corrected") for r in rr), "difference_sd": float(np.std([f(r, "direct_minus_corrected") for r in rr], ddof=1)) if len(rr) > 1 else 0.0})
    margins = read_csv("margin_controls.csv")
    if margins:
        controls["roi_margin"] = []
        for key in sorted({(f(r, "p_pixels_per_wavelength"), f(r, "sigma_exp_rad_per_pixel_at_P4"), f(r, "margin_wavelengths")) for r in margins}):
            rr = [r for r in margins if (f(r, "p_pixels_per_wavelength"), f(r, "sigma_exp_rad_per_pixel_at_P4"), f(r, "margin_wavelengths")) == key]
            controls["roi_margin"].append({"P": key[0], "sigma_k": key[1], "margin_wavelengths": key[2], "n": len(rr), "ratio_discrete": mean(f(r, "ratio_discrete") for r in rr)})
    window_path = RES / "large_window_validation_summary.json"
    if window_path.exists():
        controls["large_window_validation"] = json.loads(window_path.read_text(encoding="utf-8"))
    for name in ("sanity_controls.json", "run_summary.json"):
        p = RES / name
        if p.exists(): controls[name[:-5]] = json.loads(p.read_text(encoding="utf-8"))
    (RES / "control_summary.json").write_text(json.dumps(controls, indent=2, sort_keys=True, default=lambda x: float(x) if isinstance(x, (np.floating, np.integer)) else str(x)) + "\n", encoding="utf-8")

    lines = ["# EXP-0003 independent convergence table", "", "Ratios are winding density divided by the continuous physical-spectrum Kac–Rice prediction; intervals are 99% bootstrap intervals over 24 fields per condition.", "", "| sigma_k | P=4 | P=6 | P=8 | P=12 | P=16 | P=24 | P=32 | P=48 | P=64 | tail P>=16 within 3% |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|"]
    for r in verdicts:
        vals = [r.get(f"P{p}_ratio_full", float("nan")) for p in (4,6,8,12,16,24,32,48,64)]
        lines.append("| " + f"{r['sigma_k']:.2f}" + " | " + " | ".join("—" if not np.isfinite(v) else f"{v:.4f}" for v in vals) + f" | {'yes' if r.get('tail_P_ge_16_all_within_3pct') else 'no'} |")
    lines += ["", "## Endpoint and derivative diagnostics", "", "| sigma_k | P4 full | P64 full | endpoint abs-error improvement | P4 FD forward | P64 FD forward | P4 FD central | P64 FD central |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in verdicts:
        lines.append(f"| {r['sigma_k']:.2f} | {r.get('P4_ratio_full',float('nan')):.4f} | {r.get('P64_ratio_full',float('nan')):.4f} | {r.get('endpoint_improvement_abs_error',float('nan')):.4f} | {r.get('P4_fd_forward',float('nan')):.4f} | {r.get('P64_fd_forward',float('nan')):.4f} | {r.get('P4_fd_central',float('nan')):.4f} | {r.get('P64_fd_central',float('nan')):.4f} |")
    (RES / "convergence_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"verdicts": verdicts, "control_sections": list(controls)}, indent=2, default=float))

if __name__ == "__main__":
    main()
