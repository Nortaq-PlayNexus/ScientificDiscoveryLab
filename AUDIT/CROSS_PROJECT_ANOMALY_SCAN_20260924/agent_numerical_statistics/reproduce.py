#!/usr/bin/env python
"""Read-only numerical/statistical anomaly reproductions.

This script intentionally only reads files under ScientificDiscoveryLab and
prints evidence.  It never runs a historical experiment writer and never
creates or modifies files.  Run from the laboratory root or from anywhere:

    python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py
    python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case prime_first_bin
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import re
import sys
sys.dont_write_bytecode = True
from pathlib import Path
from typing import Any, Iterable

import numpy as np

ROOT = Path(__file__).resolve().parents[3]


def rel(path: str) -> Path:
    return ROOT / path


def read_json(path: str) -> Any:
    with rel(path).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def source_lines(path: str) -> list[str]:
    return rel(path).read_text(encoding="utf-8").splitlines()


def line_ref(path: str, needle: str, occurrence: int = 1) -> str:
    """Return a stable 1-based source reference for a matching line."""
    hits = [i for i, line in enumerate(source_lines(path), 1) if needle in line]
    if len(hits) < occurrence:
        return f"{path}:<not found:{needle!r}>"
    return f"{path}:{hits[occurrence - 1]}"


def jpath(*parts: Any) -> str:
    out = "$"
    for p in parts:
        if isinstance(p, int):
            out += f"[{p}]"
        elif isinstance(p, str) and p.startswith("["):
            out += p
        else:
            out += f".{p}"
    return out


def fmt(x: Any) -> str:
    if isinstance(x, float):
        if math.isnan(x):
            return "nan"
        if math.isinf(x):
            return "inf" if x > 0 else "-inf"
        return repr(x)
    return repr(x)


def section(name: str) -> None:
    print("\n" + "=" * 78)
    print(name)
    print("=" * 78)


def walk_values(obj: Any, path: str = "$") -> Iterable[tuple[str, Any]]:
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}"
            yield from walk_values(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_values(v, f"{path}[{i}]")
    else:
        yield path, obj


def collect_key(obj: Any, key: str, path: str = "$") -> list[tuple[str, Any]]:
    found: list[tuple[str, Any]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}"
            if k == key:
                found.append((p, v))
            found.extend(collect_key(v, key, p))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            found.extend(collect_key(v, key, f"{path}[{i}]"))
    return found


def without_key(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        return {k: without_key(v, key) for k, v in obj.items() if k != key}
    if isinstance(obj, list):
        return [without_key(v, key) for v in obj]
    return obj


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Prime-gap cases
# ---------------------------------------------------------------------------
def prime_first_bin() -> None:
    section("PRIME-0008 structural first-bin contradiction")
    exp = read_json("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/RESULTS/EXP-0008_results.json")
    qm = read_json("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/q_m007_results.json")
    edge = -math.log(1.0 - 1.0 / 10.0)
    lower_bound = 2.0 / math.log(1.0e8)
    print(f"first edge = {edge!r}")
    print(f"structural lower bound 2/ln(1e8) = {lower_bound!r}")
    print(f"margin = {lower_bound - edge!r}; relative margin = {(lower_bound-edge)/edge:.8%}")
    for b in exp["primary_results"]["blocks"]:
        print(
            f"{b['label']}: n={b['n_gaps']} edge0={b['edges'][0]!r} "
            f"count0={b['counts'][0]} expected0={b['expected'][0]!r}"
        )
    b1 = qm["bin_summary"]["1"]
    print(
        f"Q-M007 aggregate bin 1: obs_total={b1['obs_total']} "
        f"exp_total={b1['exp_total']!r} residuals={b1['std_residuals_per_block']}"
    )
    print(line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/CODE/run_prime_gaps.py", "deltas = (upper - lower)"))
    print(line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/compute_bhfr_40cell.py", '"bin_1_anomaly"'))


def qm007_pvalue() -> None:
    section("Q-M007 malformed chi-square p-value")
    from scipy.stats import chi2

    result = read_json("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/BHFR_40cell_results.json")
    cell = result["cells"][0]
    x = float(cell["chi2_cell"])
    code_z = ((x / 1.0) ** (1.0 / 6.0) * (1.0 - 2.0 / 9.0)) / math.sqrt(2.0 / 9.0)
    code_p = 0.5 * math.erfc(code_z / math.sqrt(2.0))
    exact_p = float(chi2.sf(x, 1))
    cube_z = ((x / 1.0) ** (1.0 / 3.0) * (1.0 - 2.0 / 9.0)) / math.sqrt(2.0 / 9.0)
    cube_p = 0.5 * math.erfc(cube_z / math.sqrt(2.0))
    print(f"cell={cell['bin']},{cell['block']} chi2_cell={x!r}")
    print(f"stored p={cell['p_value']!r}")
    print(f"code formula reproduced={code_p!r}; exact chi2.sf={exact_p!r}")
    print(f"stored/exact={cell['p_value']/exact_p:.6e}; code exponent=1/6, standard WH exponent=1/3; source correction operator=multiplication, standard= subtraction")
    print(f"even cube-root WH one-sided approximation={cube_p!r}")
    mismatches = 0
    for c in result["cells"]:
        xx = float(c["chi2_cell"])
        zz = ((xx / 1.0) ** (1.0 / 6.0) * (1.0 - 2.0 / 9.0)) / math.sqrt(2.0 / 9.0)
        pp = 0.5 * math.erfc(zz / math.sqrt(2.0))
        if pp != c["p_value"]:
            mismatches += 1
    print(f"cells whose stored p is not reproduced by source formula: {mismatches}/{len(result['cells'])}")
    print(line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/compute_bhfr_40cell.py", "z = ((chi2_cell"))


def qm008_method_mismatch() -> None:
    section("Q-M008 denominator and block-structure mismatch")
    prereg = read_json("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/CONFIG/prereg_EXP-0008.json")
    qm = read_json("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/RESULTS/Q-M008_1e8_results.json")
    print("EXP-0008 prereg blocks:")
    for b in prereg["parameters"]["blocks"]:
        print(f"  {b['label']}: [{b['lo']}, {b['hi']})")
    print("Q-M008 code block construction at limit=1e8:")
    for lo, hi in [(10**6, 10**7), (10**7, 5 * 10**7), (5 * 10**7, 8 * 10**7), (8 * 10**7, 10**8)]:
        print(f"  B?: [{lo}, {hi})")
    print("Q-M008 stored block sizes:", [(b["label"], b["n_gaps"]) for b in qm["blocks"]])
    p = np.array([3, 5, 7], dtype=float)
    lower_delta = (p[1:] - p[:-1]) / np.log(p[:-1])
    upper_delta = (p[1:] - p[:-1]) / np.log(p[1:])
    print(f"lower-prime normalization example: {lower_delta.tolist()}")
    print(f"upper-prime normalization example: {upper_delta.tolist()}")
    print(f"Q-M008 overall chi2={qm['overall']['chi2']['chi2']!r}")
    print("EXP-0008 combined chi2=971920.0236 (stored report value)")
    print(line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/CODE/run_prime_gaps.py", "deltas = (upper - lower)"))
    print(line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/CODE/run_exp0012.py", "log_p = np.log(primes[1:]"))
    print(line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/CODE/run_exp0012.py", "blocks = ["))


def qm008_pvalue_bh() -> None:
    section("Q-M008 survival-function and BH implementation checks")
    from scipy.stats import chi2, norm

    result = read_json("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/RESULTS/Q-M008_1e8_results.json")
    pvals = collect_key(result, "p_value")
    zeros = [(p, v) for p, v in pvals if v == 0.0]
    print(f"stored p_value fields={len(pvals)} exact zeros={len(zeros)}")
    print("first zero paths:", [p for p, _ in zeros[:8]])
    x = 100.0
    print(f"synthetic chi2 x={x}: 1-cdf={1.0-float(chi2.cdf(x,1))!r}; sf={float(chi2.sf(x,1))!r}")
    z = 10.0
    print(f"synthetic normal z={z}: 1-cdf={1.0-float(norm.cdf(z))!r}; sf={float(norm.sf(z))!r}")

    p = np.array([0.001, 0.008, 0.009])
    alpha = 0.01
    order = np.argsort(p)
    sorted_p = p[order]
    thresholds = np.arange(1, len(p) + 1) / len(p) * alpha
    individual = sorted_p <= thresholds
    valid = np.flatnonzero(individual)
    k = int(valid.max() + 1) if valid.size else 0
    step_up = np.zeros(len(p), dtype=bool)
    step_up[order[:k]] = True
    print(f"BH synthetic sorted p={sorted_p.tolist()} thresholds={thresholds.tolist()}")
    print(f"naive rank mask={individual.tolist()}; proper step-up rejects={step_up.tolist()} (k={k})")
    print(line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/CODE/run_exp0012.py", "p_value = 1 - sp_stats.chi2.cdf"))
    print(line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/CODE/run_exp0012.py", "significant = sorted_p <= critical"))


# ---------------------------------------------------------------------------
# Percolation cases
# ---------------------------------------------------------------------------
def qp006_duplicate() -> None:
    section("Q-P006/Q-P005 byte-identical raw cells")
    pairs = [
        (
            "03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/RESULTS/_cells_L512_n200.npz",
            "03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/CODE/RESULTS/_cells_L512_n200.npz",
        ),
        (
            "03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/RESULTS/_cells_L1024_n100.npz",
            "03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/CODE/RESULTS/_cells_L1024_n100.npz",
        ),
        (
            "03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/RESULTS/_cells_L2048_n50.npz",
            "03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/CODE/RESULTS/_cells_L2048_n50.npz",
        ),
    ]
    for a, b in pairs:
        ha, hb = sha256(rel(a)), sha256(rel(b))
        print(f"{Path(a).name}: {ha} == {hb}: {ha == hb}")
    prereg = read_json("03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/CONFIG/prereg_EXP-0009P.json")
    print("prereg note contains no-reuse statement:", "No cells from EXP-0009/EXP-0010 reused." in prereg["note"])
    print(line_ref("03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/CODE/run_q_p006.py", "if os.path.exists(path)"))


def qp007_sample() -> None:
    section("Q-P007 ragged-sample truncation")
    result = read_json("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/RESULTS/EXP-0009-pc_results.json")
    prereg = read_json("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CONFIG/prereg_EXP-0009PC.json")
    print("result n_real:", result["n_real"])
    print("prereg n_real:", prereg["parameters"]["n_real"])
    n_by_l = [int(prereg["parameters"]["n_real"][str(L)]) for L in prereg["parameters"]["L_list"]]
    min_n = min(n_by_l)
    retained_fractions = {L: min_n / int(prereg["parameters"]["n_real"][str(L)]) for L in prereg["parameters"]["L_list"]}
    print(f"effective aligned min_n={min_n}; retained fractions={retained_fractions}")
    for L in prereg["parameters"]["L_list"]:
        p = rel(f"03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/RESULTS/EXP-0009-pc_L{L}_cells.npz")
        if p.exists():
            with np.load(p, allow_pickle=True) as z:
                print(f"L={L} NPZ masses shape={z['masses'].shape}, n_real={prereg['parameters']['n_real'][str(L)]}")
    print(line_ref("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/run_phase2.py", "min_n = min(len(cells[L][\"masses\"])") )
    print(line_ref("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/run_phase2.py", "mmat_a = np.array"))


def qp007_cache() -> None:
    section("Q-P007 cache schema cannot reconstruct tau")
    result = read_json("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/RESULTS/EXP-0009-pc_results.json")
    print("stored tau:", result["exponents"]["tau"])
    print("stored tau_raw:", result["tau_raw"])
    for L in (512, 1024, 2048):
        p = rel(f"03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/RESULTS/EXP-0009-pc_L{L}_cells.npz")
        if p.exists():
            with np.load(p, allow_pickle=True) as z:
                totals = z["sizes_n_total"]
                print(f"L={L} keys={z.files}; sizes_present={'sizes' in z.files}; sizes_n_shape={z['sizes_n'].shape}; sizes_n_total_shape={totals.shape}; sizes_n_total_first_last_sum={totals[:3].tolist()}/{totals[-3:].tolist()}/{int(totals.sum())}")
    print(line_ref("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/run_phase2.py", "sizes_n=np.array"))
    print(line_ref("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/run_phase2.py", "return {\"masses\": z[\"masses\"]"))
    print(line_ref("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/run_phase2.py", "tsizes = [ss[1:] for ss in cells[tL][\"sizes\"]]") )


def qp007_pc() -> None:
    section("Q-P007 phase-2 p_c inputs are literals")
    result = read_json("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/RESULTS/EXP-0009-pc_results.json")
    p_c = np.array([result["p_c_measures"][str(L)] for L in (512, 1024, 2048)], dtype=float)
    inv_l = 1.0 / np.array([512, 1024, 2048], dtype=float)
    fit_slope, fit_intercept = np.polyfit(inv_l, p_c, 1)
    print("stored p_c_measures:", result["p_c_measures"])
    print("stored p_c_refined:", result["p_c_refined"])
    print(f"recomputed 1/L slope={fit_slope!r}; intercept={fit_intercept!r}")
    print("source p_c_sig literals:", re.findall(r"p_c_sig = \{([^}]+)\}", "\n".join(source_lines("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/run_phase2.py"))))
    print(line_ref("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/run_phase2.py", "p_c_measures = {512"))
    print(line_ref("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/run_phase2.py", "p_c_sig = {512") )


def three_d_boundary() -> None:
    section("3-D spanning boundary reproduction")
    engine_dir = rel("03_INVESTIGATIONS/PHYSICS/percolation/ENGINE")
    sys.path.insert(0, str(engine_dir))
    import perc_engine as pe  # type: ignore

    L = 4
    N = L**3
    for name, a, b in [
        ("z=0-plane connection", 1, (L - 1) * L + 1),
        ("opposite-z connection", 1, L * L + 1),
    ]:
        labels = np.arange(N, dtype=np.int64)
        labels[a] = 999
        labels[b] = 999
        flags = pe.spanning_flags(labels, N, L, bottom_rows=(L - 1,))
        actual_z = bool(set(labels[: L * L].tolist()) & set(labels[L * L :].tolist()))
        print(f"{name}: default spanning_flags={flags}; actual z-face connection={actual_z}")
    print(line_ref("03_INVESTIGATIONS/PHYSICS/percolation/ENGINE/perc_engine.py", "np.repeat(np.arange(L)"))
    print(line_ref("03_INVESTIGATIONS/PHYSICS/percolation/ENGINE/perc_engine.py", "v_span = bool(tset & bset)"))
    print(line_ref("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/REPLICATION/independent_check_EXP0011.py", "only check z=0 plane") )


def three_d_sample() -> None:
    section("3-D configured versus effective sample sizes")
    pilot_cfg = read_json("03_INVESTIGATIONS/PHYSICS/percolation_3d/CONFIG/prereg_EXP-0011.json")
    main_cfg = read_json("03_INVESTIGATIONS/PHYSICS/percolation_3d/CONFIG/prereg_EXP-0013.json")
    for label, cfg in (("EXP-0011 pilot", pilot_cfg), ("EXP-0013 main", main_cfg)):
        rows = []
        for L, info in cfg["parameters"]["width_grid"].items():
            n_each = int(info["n_each"])
            rows.append((L, n_each, max(4, n_each // 10)))
        print(f"{label} width n_each configured/effective: {rows}")
        ns = [int(v) for v in cfg["parameters"]["n_real"].values()]
        print(f"{label} exponent n_real={ns}, min_n used for ragged fit={min(ns)}")
    print(line_ref("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/run_exp0011.py", "max(4, n_each // 10)"))
    print(line_ref("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/run_exp0011.py", "min_n = min(len(cells[L][\"masses\"])") )


def three_d_provenance() -> None:
    section("3-D main result is a semantic pilot copy")
    main = read_json("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/RESULTS/EXP-0011_results.json")
    pilot = read_json("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/RESULTS/EXP-0011_pilot_results.json")
    print("main result L_list:", main["L_list"])
    print("pilot result L_list:", pilot["L_list"])
    print("semantic equality after removing elapsed:", without_key(main, "elapsed") == without_key(pilot, "elapsed"))
    print("elapsed values:", main.get("elapsed"), pilot.get("elapsed"))
    log = source_lines("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/LOG/run.log")
    print("main log tail:", log[:12])
    cfg = read_json("03_INVESTIGATIONS/PHYSICS/percolation_3d/CONFIG/prereg_EXP-0013.json")
    print("EXP-0013 prereg L_list:", cfg["parameters"]["L_list"])
    print(line_ref("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/run_exp0011.py", "PREC_PATHS = [") )


def exp0007_draws_precision() -> None:
    section("EXP-0007 bootstrap count and precision gate")
    summary = read_json("03_INVESTIGATIONS/PHYSICS/percolation/CODE/RESULTS/EXP-0007_summary.json")
    prereg = read_json("03_INVESTIGATIONS/PHYSICS/percolation/CONFIG/prereg_EXP-0007.json")
    boot = summary["estimator_diagnostics"]["width_route"]["bootstrap"]
    fss = summary["primary_results"]["fss_primary"]
    tol = summary["primary_results"]["in_tol"]["tol_pc"]
    dev = summary["primary_results"]["in_tol"]["d_bond_wrap"]
    print(f"prereg bootstrap n_draws={prereg['parameters']['bootstrap']['n_draws']}")
    print(f"stored bootstrap n_draws={boot['n_draws']}")
    print(f"FSS se_a={fss['se_a']!r}; tolerance={tol!r}; se_a/tol={fss['se_a']/tol:.6f}")
    print(f"point deviation={dev!r}; point deviation/tol={dev/tol:.6f}")
    print(line_ref("03_INVESTIGATIONS/PHYSICS/percolation/CODE/run_percolation_exp0007.py", "out.append(interp_p50"))
    print(line_ref("03_INVESTIGATIONS/PHYSICS/percolation/REPORT/TECHNICAL_EXP-0007.md", "500 draws") )


# ---------------------------------------------------------------------------
# Optics, Feigenbaum, S9, RNG, Collatz, and dependence cases
# ---------------------------------------------------------------------------
def optics_floor() -> None:
    section("Optics bootstrap p-value floor")
    eps = float(np.finfo(float).eps)
    s = read_json("03_INVESTIGATIONS/OPTICS/speckle_contrast_law/RESULTS/EXP-0002_results.json")
    v = read_json("03_INVESTIGATIONS/OPTICS/vortex_density/RESULTS/EXP-0003_results.json")
    for label, obj, key in (("EXP-0002", s, "p_two_sided_null_r_eq_1"), ("EXP-0003", v, "p_two_sided_ratio_eq_1")):
        hits = [(p, x) for p, x in walk_values(obj) if p.endswith(key) and x == eps]
        print(f"{label}: exact eps floors={len(hits)}; examples={[p for p, _ in hits[:5]]}")
    print("eps =", repr(eps), "; empirical bootstrap resolution is at least 1/N_BOOT, not eps")
    print(line_ref("03_INVESTIGATIONS/OPTICS/speckle_contrast_law/CODE/run_speckle_contrast.py", "p = min(1.0, p + np.finfo(float).eps)"))
    print(line_ref("03_INVESTIGATIONS/OPTICS/vortex_density/CODE/run_vortex_density.py", "p = min(1.0, p + np.finfo(float).eps)") )


def feigenbaum_results() -> None:
    section("EXP-0014 nonfinite/duplicate roots and control provenance")
    result = read_json("03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/CODE/03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/RESULTS/EXP-0014_results.json")
    for zkey in ("z2", "z3", "z4"):
        z = result[zkey]
        av = list(z["a_vals"].values())
        ds = list(z["deltas"].values())
        print(f"{zkey}: a_unique={len(set(av))}/{len(av)}, nonfinite_deltas={sum(not math.isfinite(float(x)) for x in ds)}, deltas={ds}")
    c4 = result["controls"]["C4"]
    print(f"stored C4: difference={c4['difference']!r}, pass={c4['pass']!r} (type={type(c4['pass']).__name__})")
    try:
        json.loads(rel("03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/CONFIG/prereg_EXP-0014.json").read_text(encoding="utf-8"))
        print("prereg JSON: valid")
    except Exception as exc:
        print("prereg JSON: INVALID:", type(exc).__name__, str(exc))
    print(line_ref("03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/CODE/feigenbaum_engine.py", "deltas[n] = float(\"inf\")"))
    print(line_ref("03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/CODE/run_feigenbaum.py", "\"pass\": True", occurrence=2))
    print(line_ref("03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/CODE/run_feigenbaum.py", "controls[\"C4\"] = c4") )


def s9_hardcoded() -> None:
    section("Q-S9-1/Q-S9-3 hard-coded result dictionaries")
    path = "save_q9results.py"
    tree = ast.parse("\n".join(source_lines(path)))
    values: dict[str, Any] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {"q_s9_1_results", "q_s9_3_results"}:
                    values[target.id] = ast.literal_eval(node.value)
    for name, value in values.items():
        print(f"{name}: literal keys={list(value.keys())}")
        if name == "q_s9_1_results":
            print("  complexity/rates:", [(x["complexity"], x["code_rate"]) for x in value["complexity_levels"]])
        else:
            raw = value["dose_response_debiased"]["raw_rates"]
            unbiased = value["dose_response_debiased"]["unbiased_rates"]
            print("  dose raw/unbiased equal count:", sum(a == b for a, b in zip(raw, unbiased)), "/", len(raw))
            print("  raw=", raw)
            print("  unbiased=", unbiased)
    print(line_ref(path, "q_s9_1_results = {"))
    print(line_ref(path, "q_s9_3_results = {") )


def s9_synthetic() -> None:
    section("Q-S9-2 synthetic dose-response generation")
    # Reimplement only the deterministic generation expression; do not execute its writer.
    def hill(x: float, ec50: float, hill_coeff: float, max_infl: float, baseline: float) -> float:
        return baseline + (max_infl * (x ** hill_coeff)) / ((ec50 ** hill_coeff) + (x ** hill_coeff))

    doses = np.linspace(0, 1, 11) * 100.0
    rates = np.array([hill(float(x), 30.0, 2.0, 0.483, 0.205) for x in doses])
    noise = np.random.default_rng(42).normal(0, 0.02, len(doses))
    observed = np.clip(rates + noise, 0, 1)
    stored = read_json("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-S9-2/dose_response_results.json")
    stored_values = np.array([stored["dose_response_A"][str(float(d))] for d in doses])
    print("generated first/last:", observed[0], observed[-1])
    print("stored first/last:", stored_values[0], stored_values[-1])
    print("stored/generated max abs diff:", float(np.max(np.abs(observed - stored_values))))
    print("source declares simulated data:", "Simulated dose-response data" in "\n".join(source_lines("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-S9-2/dose_response.py")))
    print(line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-S9-2/dose_response.py", "def generate_dose_response"))
    print(line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-S9-2/dose_response.py", "np.random.default_rng(42)") )


def s9_units() -> None:
    section("Q-S9-2 additive-versus-relative inflation units")
    baseline, max_infl = 0.205, 0.483
    saturation = baseline + max_infl
    relative_actual = (saturation - baseline) / baseline
    relative_intended_saturation = baseline * (1.0 + max_infl)
    print(f"source formula saturation={saturation!r}; relative increase={relative_actual:.12%}")
    print(f"if 0.483 means 48.3% relative, saturation={relative_intended_saturation!r}")
    print(f"absolute excess={saturation-relative_intended_saturation!r}")
    print(line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-S9-2/dose_response.py", "return baseline + (max_inflation"))
    print(line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-S9-2/dose_response.py", "30.4/20.5 - 1 = 48.3%") )
    print(line_ref("03_INVESTIGATIONS/OTHER/cone_mosaic_aliasing/REPORT/TECHNICAL_Q-S9-2.md", "48.3% increase at saturation") )


def rng_dependence() -> None:
    section("EXP-0004 pooled p-values reuse one stream")
    engine_dir = rel("04_SHARED_ENGINE")
    sys.path.insert(0, str(engine_dir))
    from engine.utilities.core import rng  # type: ignore
    from engine.validation.rng_battery import run_battery, streams_for  # type: ignore

    rows = []
    ids = None
    for seed in range(20):
        b, f, w, bits = streams_for(rng("Q-I004:cert", seed))
        vals = run_battery(bits, b, f, w)
        ids = [tid for tid, _ in vals]
        rows.append([p for _, p in vals])
    x = np.asarray(rows, dtype=float)
    corr = np.corrcoef(x, rowvar=False)
    corr = np.corrcoef(x.T)
    np.fill_diagonal(corr, 0.0)
    i, j = np.unravel_index(np.nanargmax(np.abs(corr)), corr.shape)
    print(f"fresh seeds=20; max |corr|={abs(corr[i,j]):.12f} between {ids[i]} and {ids[j]}")
    print("stored EXP-0004 decision:", read_json("03_INVESTIGATIONS/OTHER/rng_certification/RESULTS/EXP-0004_results.json")["decision"])
    print(line_ref("04_SHARED_ENGINE/engine/validation/rng_battery.py", "Each test consumes a fixed disjoint slice"))
    print(line_ref("04_SHARED_ENGINE/engine/validation/rng_battery.py", "out.append((\"T01_monobit\", t_monobit(bits)))"))
    print(line_ref("04_SHARED_ENGINE/engine/validation/rng_battery.py", "out.append((\"T11_bytes\", t_byte_chisq(bytes_arr)))"))
    print(line_ref("03_INVESTIGATIONS/OTHER/rng_certification/CODE/run_rng_cert.py", "merged = [p for per_seed"))


def collatz() -> None:
    section("Collatz timeout labels and incomplete family sweep")
    full = read_json("03_INVESTIGATIONS/MATHEMATICS/collatz/RESULTS/Q-M001_full_results.json")
    prereg = read_json("03_INVESTIGATIONS/MATHEMATICS/collatz/prereg_Q-M001.json")
    combos = [(a, b, c) for a in prereg["parameters"]["a_values"] for b in prereg["parameters"]["b_values"] for c in prereg["parameters"]["c_values"]]
    print(f"stored full result families={len(full['results'])} + pilot families={len(full['divergent_pilot'])}; prereg combinations={len(combos)}")
    print("full result family rows:", [(r["a"], r["b"], r["c"], r["N"]) for r in full["results"]])
    print("pilot family rows:", [(r["a"], r["b"], r["c"], r["N"]) for r in full["divergent_pilot"]])
    pilot = read_json("03_INVESTIGATIONS/MATHEMATICS/collatz/RESULTS/Q-M001_results.json")
    fam = pilot["results"][0]
    print(f"pilot first family cycles_found={fam['cycles_found']} while max_stopping_time={fam['max_stopping_time']}")
    n, a, b, c, M = 55, 3, 3, 1, 1000
    seen = set()
    repeated = False
    for _ in range(M):
        if n in seen:
            repeated = True
            break
        seen.add(n)
        n = n // a if n % a == 0 else n * b + c
    print(f"synthetic n0=55 family=(3,3,1): repeated_before_max_steps={repeated}; code would label timeout as cycle")
    print(line_ref("03_INVESTIGATIONS/MATHEMATICS/collatz/CODE/run_collatz_full.py", "return steps if n == 1 else max_steps"))
    print(line_ref("03_INVESTIGATIONS/MATHEMATICS/collatz/CODE/run_collatz_full.py", "cycles_found.append(n0)"))
    print(line_ref("03_INVESTIGATIONS/MATHEMATICS/collatz/CODE/run_collatz_full.py", "divergent = [(3,3,1)") )


def exp0009_c7_streams() -> None:
    section("EXP-0009 C7 uses identical frozen streams")
    source = "03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/REPLICATION/independent_check_exp0009.py"
    report = read_json("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/REPLICATION/C7_exp0009_report.json")
    result = read_json("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/RESULTS/EXP-0009_results.json")
    print("C7 stream declaration:", report.get("streams"))
    print("C7 per-L implementation comparison:", {k: {x: v[x] for x in ("Mmax_identical", "chi_identical")} for k, v in report["per_L"].items()})
    print("C7 D_f comparison:", report["D_f"])
    print("parent C7 gate:", result["primary_results"]["gates"]["C7"])
    print(line_ref(source, "Re-derives M_max and chi on the IDENTICAL frozen streams"))
    print(line_ref(source, "first 40 realizations"))


def r3_coupling() -> None:
    section("EXP-0009 R3 algebraic coupling")
    result = read_json("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/RESULTS/EXP-0009_results.json")
    df = result["primary_results"]["exponents"]["D_f"]["value"]
    beta = result["primary_results"]["exponents"]["beta_nu"]["value"]
    implied = 2.0 - df
    print(f"D_f={df!r}; beta/nu={beta!r}; 2-D_f={implied!r}; |D_f-(2-beta)|={abs(df-(2-beta))!r}")
    print("stored R3:", result["primary_results"]["relations"]["R3_Df=2-bn"])
    print(line_ref("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/run_exp0009.py", "pinfs = masses / float(N)"))
    print(line_ref("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/run_exp0009.py", "Bf_draws = -bootstrap_slope"))
    print(line_ref("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/run_exp0009.py", "R3 = abs(Df - (2.0 - Bf))"))
    print(line_ref("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CONFIG/prereg_EXP-0009.json", "algebraic comparison") )


CASES = {
    "prime_first_bin": prime_first_bin,
    "qm007_pvalue": qm007_pvalue,
    "qm008_method_mismatch": qm008_method_mismatch,
    "qm008_pvalue_bh": qm008_pvalue_bh,
    "qp006_duplicate": qp006_duplicate,
    "qp007_sample": qp007_sample,
    "qp007_cache": qp007_cache,
    "qp007_pc": qp007_pc,
    "three_d_boundary": three_d_boundary,
    "three_d_sample": three_d_sample,
    "three_d_provenance": three_d_provenance,
    "exp0007_draws_precision": exp0007_draws_precision,
    "optics_floor": optics_floor,
    "feigenbaum_results": feigenbaum_results,
    "s9_hardcoded": s9_hardcoded,
    "s9_synthetic": s9_synthetic,
    "s9_units": s9_units,
    "rng_dependence": rng_dependence,
    "collatz": collatz,
    "exp0009_c7_streams": exp0009_c7_streams,
    "r3_coupling": r3_coupling,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=sorted(CASES), action="append", help="run one or more cases (default: all)")
    args = parser.parse_args()
    selected = args.case or list(CASES)
    print(f"root={ROOT}")
    print(f"selected cases={selected}")
    for name in selected:
        try:
            CASES[name]()
        except Exception as exc:  # keep the full audit log useful if one optional import fails
            print(f"CASE_ERROR {name}: {type(exc).__name__}: {exc}")
            import traceback
            traceback.print_exc()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
