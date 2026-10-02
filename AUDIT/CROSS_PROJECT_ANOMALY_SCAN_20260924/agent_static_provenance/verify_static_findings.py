"""Safe, read-only candidate verification for the static/provenance audit.

No historical file is written.  The script only reads source/result artifacts,
runs small in-memory calculations, and writes evidence JSON/log files beside
this script.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import re
import tempfile
import sys
from pathlib import Path
from typing import Any

ROOT = Path(r"C:\Users\natha\ScientificDiscoveryLab")
OUT = Path(__file__).resolve().parent


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mtime(path: Path) -> str:
    return dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).isoformat()


def source_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8-sig").splitlines()


def interp_wrong(ps: list[float], ws: list[float]) -> float:
    below = [i for i, w in enumerate(ws) if w < 0.5]
    above = [i for i, w in enumerate(ws) if w > 0.5]
    i, j = below[-1], above[0]
    p0, p1, w0, w1 = ps[i], ps[j], ws[i], ws[j]
    # Literal historical EXP-0006 expression.
    return p0 + (0.5 - w0) * (p1 - p0) / (w1 - p0)


def interp_correct(ps: list[float], ws: list[float]) -> float:
    below = [i for i, w in enumerate(ws) if w < 0.5]
    above = [i for i, w in enumerate(ws) if w > 0.5]
    i, j = below[-1], above[0]
    p0, p1, w0, w1 = ps[i], ps[j], ws[i], ws[j]
    return p0 + (0.5 - w0) * (p1 - p0) / (w1 - w0)


def bootstrap_p50s(rows: list[dict[str, Any]], wrong: bool) -> list[float]:
    # Use the same deterministic binomial bootstrap shape as the historical
    # runner, but with a local Generator so no source/result file is touched.
    import numpy as np
    # Match the historical runner's named G_LAB stream, not an arbitrary RNG.
    import sys as _sys
    _sys.path.insert(0, str(ROOT / "04_SHARED_ENGINE"))
    from engine.utilities.core import rng
    ps = [float(r["p"]) for r in rows]
    ks = np.array([int(r["k_v"]) for r in rows], dtype=np.int64)
    ns = np.array([int(r["n"]) for r in rows], dtype=np.int64)
    gen = rng("perc-boot-exp0006", 42)
    vals = []
    fn = interp_wrong if wrong else interp_correct
    for _ in range(500):
        kb = gen.binomial(ns, ks / ns)
        try:
            vals.append(fn(ps, (kb / ns).tolist()))
        except (IndexError, ZeroDivisionError):
            pass
    return vals


def fss_from_p50(p50: dict[int, float]) -> dict[str, Any]:
    import numpy as np
    ls = sorted(p50)
    x = np.asarray(ls, dtype=float) ** (-3.0 / 4.0)
    y = np.asarray([p50[l] for l in ls], dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    return {"a": float(intercept), "b": float(slope), "L": ls}


def verify_exp0006() -> dict[str, Any]:
    path = ROOT / "03_INVESTIGATIONS/PHYSICS/percolation/CODE/RESULTS/EXP-0006_results.json"
    data = read_json(path)
    rows_by_l: dict[int, list[dict[str, Any]]] = {}
    for row in data["cells"]["bond_span"]:
        rows_by_l.setdefault(int(row["L"]), []).append(row)
    wrong_draws = {l: bootstrap_p50s(rows, True) for l, rows in rows_by_l.items()}
    correct_draws = {l: bootstrap_p50s(rows, False) for l, rows in rows_by_l.items()}
    wrong_means = {l: sum(v) / len(v) for l, v in wrong_draws.items()}
    correct_means = {l: sum(v) / len(v) for l, v in correct_draws.items()}
    wrong_fss = fss_from_p50(wrong_means)
    correct_fss = fss_from_p50(correct_means)
    return {
        "result": rel(path),
        "stored_p50": data.get("p50", {}).get("bond_span"),
        "stored_fss": data.get("fss", {}).get("bond_span"),
        "literal_wrong_expression": "p0 + (0.5-w0)*(p1-p0)/(w1-p0)",
        "correct_expression": "p0 + (0.5-w0)*(p1-p0)/(w1-w0)",
        "wrong_recomputed_means": wrong_means,
        "correct_recomputed_means": correct_means,
        "wrong_fss": wrong_fss,
        "correct_fss": correct_fss,
        "max_abs_p50_mean_difference": max(abs(wrong_means[l] - correct_means[l]) for l in wrong_means),
        "stored_vs_correct_intercept_abs": abs(float(data["fss"]["bond_span"]["a"]) - correct_fss["a"]),
    }


def verify_c2_hardcoded() -> dict[str, Any]:
    path = ROOT / "03_INVESTIGATIONS/PHYSICS/percolation/CODE/run_percolation_exp0006.py"
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    return {
        "path": rel(path),
        "line_290_294": lines[289:294],
        "has_same_value_subtraction": "fss_out[\"bond_span\"][\"a\"] - fss_out[\"bond_span\"][\"a\"]" in text,
        "has_literal_pass_true": '"pass": True' in text,
        "stored_result_c2": read_json(ROOT / "03_INVESTIGATIONS/PHYSICS/percolation/CODE/RESULTS/EXP-0006_results.json").get("c2"),
    }


def verify_3d_boundary() -> dict[str, Any]:
    # Reproduce the exact boundary index construction used by spanning_flags
    # for a 3-D LxLxL graph and compare with the intended z=0/z=L-1 planes.
    L = 4
    n = L**3
    flat_rows = [i // L for i in range(L * L)]
    flat_cols = [i % L for i in range(L * L)]
    top = [i for i, r in enumerate(flat_rows) if r == 0]
    bottom = [i for i, r in enumerate(flat_rows) if r == L - 1]
    left = [i for i, c in enumerate(flat_cols) if c == 0]
    right = [i for i, c in enumerate(flat_cols) if c == L - 1]
    expected_top = [x + L * y for y in range(L) for x in range(L)]
    expected_bottom = [x + L * y + L * L * (L - 1) for y in range(L) for x in range(L)]
    expected_left = [x + L * y for y in range(L) for x in range(L)]
    expected_right = [x + L * y + (L - 1) for y in range(L) for x in range(L)]
    return {
        "L": L,
        "N": n,
        "function_selected_top": top,
        "function_selected_bottom": bottom,
        "function_selected_left": left,
        "function_selected_right": right,
        "expected_3d_z0": expected_top,
        "expected_3d_z_last": expected_bottom,
        "selected_top_is_subset_of_z0": set(top).issubset(set(expected_top)),
        "selected_bottom_touches_z_last": bool(set(bottom) & set(expected_bottom)),
        "selected_max_index": max(bottom),
        "expected_z_last_min_index": min(expected_bottom),
        "note": "spanning_flags constructs flat_rows/flat_cols of length L^2, so for N=L^3 it never selects the z=L-1 plane.",
    }


def verify_nested_tau() -> dict[str, Any]:
    # Safe structural check using the exact construction in the 3-D runner.
    cl_sizes = [[1, 2, 3]]  # one realization, as run_span_cell_edges returns
    sizes_list = [cl_sizes]
    nested_tails = [ss[1:] for ss in sizes_list]
    return {
        "runner": "03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/run_exp0011.py:156,182",
        "sizes_list_type": type(sizes_list[0]).__name__,
        "tail_lengths": [len(x) for x in nested_tails],
        "all_tails_empty": all(len(x) == 0 for x in nested_tails),
        "report_claim": rel(ROOT / "03_INVESTIGATIONS/PHYSICS/percolation_3d/REPORT/PLAIN_EXP-0011.md"),
    }


def verify_3d_sample_count() -> dict[str, Any]:
    pre = read_json(ROOT / "03_INVESTIGATIONS/PHYSICS/percolation_3d/CONFIG/prereg_EXP-0011.json")
    runner = ROOT / "03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/run_exp0011.py"
    text = runner.read_text(encoding="utf-8-sig")
    configured = {k: v["n_each"] for k, v in pre["parameters"]["width_grid"].items()}
    actual = {k: max(4, v // 10) for k, v in configured.items()}
    return {
        "prereg": rel(pre_path := ROOT / "03_INVESTIGATIONS/PHYSICS/percolation_3d/CONFIG/prereg_EXP-0011.json"),
        "runner": rel(runner),
        "configured_n_each": configured,
        "actual_expression": "max(4, n_each // 10)",
        "actual_n_each": actual,
        "source_contains_division": "max(4, n_each // 10)" in text,
        "all_reduced": all(actual[k] < configured[k] for k in configured),
    }


def verify_result_hashes() -> list[dict[str, Any]]:
    pairs = [
        ("03_INVESTIGATIONS/OPTICS/speckle_contrast_law/CONFIG/EXP-0002_experiment.json", "03_INVESTIGATIONS/OPTICS/speckle_contrast_law/RESULTS/EXP-0002_results.json"),
        ("03_INVESTIGATIONS/OPTICS/vortex_density/CONFIG/EXP-0003_experiment.json", "03_INVESTIGATIONS/OPTICS/vortex_density/RESULTS/EXP-0003_results.json"),
        ("03_INVESTIGATIONS/OTHER/rng_certification/CONFIG/EXP-0004_experiment.json", "03_INVESTIGATIONS/OTHER/rng_certification/RESULTS/EXP-0004_results.json"),
        ("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/CONFIG/EXP-0008_experiment.json", "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/RESULTS/EXP-0008_results.json"),
    ]
    out = []
    for c, r in pairs:
        cp, rp = ROOT / c, ROOT / r
        rec = read_json(cp)
        out.append({"config": c, "result": r, "recorded_result_hash": rec.get("result_hash"), "actual_file_sha256": sha(rp), "match": rec.get("result_hash") == sha(rp)})
    return out


def verify_freeze_config() -> dict[str, Any]:
    # Demonstrate the documented immutable helper's write mode in a temp dir;
    # no repository file is touched.
    import sys
    sys.path.insert(0, str(ROOT / "04_SHARED_ENGINE"))
    from engine.hypothesis_testing.prereg import freeze_config
    with tempfile.TemporaryDirectory(dir=str(Path(tempfile.gettempdir()))) as td:
        p = Path(td) / "prereg.json"
        a = freeze_config(experiment_id="X", hypothesis_id="H", question_id="Q", seed=1, params={"x": 1}, out_path=p)
        first = sha(p)
        first_obj = read_json(p)
        b = freeze_config(experiment_id="X", hypothesis_id="H", question_id="Q", seed=1, params={"x": 2}, out_path=p)
        second = sha(p)
        second_obj = read_json(p)
        return {"first_hash": first, "second_hash": second, "changed": first != second, "first_params": first_obj["parameters"], "second_params": second_obj["parameters"], "helper_source": "04_SHARED_ENGINE/engine/hypothesis_testing/prereg.py:45-46"}


def verify_qm007() -> dict[str, Any]:
    data = read_json(ROOT / "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/q_m007_results.json")
    report = (ROOT / "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/REPORT/TECHNICAL_Q-M007.md").read_text(encoding="utf-8-sig")
    bin1 = data["bin_summary"]["1"]
    actual_mean = sum(bin1["std_residuals_per_block"]) / 4
    # Literal source formula and a two-sided chi-square(1) correction.
    import math
    literal = []
    two_sided = []
    for z in bin1["std_residuals_per_block"]:
        x = z * z
        zz = (x ** (1 / 6) * (1 - 2 / 9)) / math.sqrt(2 / 9)
        literal.append(0.5 * math.erfc(zz / math.sqrt(2)))
        two_sided.append(math.erfc(abs(zz) / math.sqrt(2)))
    return {
        "stored_mean_std_residual_bin1": bin1["mean_std_residual"],
        "recomputed_mean_std_residual_bin1": actual_mean,
        "report_line_39_claim": next((x for x in report.splitlines() if "| 1 | 0 |" in x), None),
        "source_approximation_comment": "compute_bhfr_40cell.py:27-40 says single-cell obs/exp unavailable and approximates from residuals",
        "literal_bin1_pvalues": literal,
        "two_sided_bin1_pvalues": two_sided,
        "literal_overcount_note": "source uses 0.5*erfc while chi-square upper tail is erfc for positive transformed statistic",
        "prereg": rel(ROOT / "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/prereg_BHFR_40cell.json"),
    }


def verify_duplicate_3d_payloads() -> dict[str, Any]:
    a = read_json(ROOT / "03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/RESULTS/EXP-0011_results.json")
    b = read_json(ROOT / "03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/RESULTS/EXP-0011_pilot_results.json")
    for x in (a, b):
        x.pop("elapsed", None)
    ca = read_json(ROOT / "03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/RESULTS/EXP-0011_combined.json")
    cb = read_json(ROOT / "03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/RESULTS/EXP-0011_pilot_combined.json")
    for x in (ca, cb):
        x.get("phase2_results", {}).pop("elapsed", None)
    return {"results_same_after_elapsed_removed": a == b, "combined_same_after_elapsed_removed": ca == cb, "result_elapsed_values": [read_json(ROOT / "03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/RESULTS/EXP-0011_results.json").get("elapsed"), read_json(ROOT / "03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/RESULTS/EXP-0011_pilot_results.json").get("elapsed")]}


def verify_duplicate_hashes() -> dict[str, Any]:
    groups = [
        ["03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/RESULTS/_cells_L512_n200.npz", "03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/CODE/RESULTS/_cells_L512_n200.npz"],
        ["03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/RESULTS/_cells_L1024_n100.npz", "03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/CODE/RESULTS/_cells_L1024_n100.npz"],
        ["03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/RESULTS/_cells_L2048_n50.npz", "03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/CODE/RESULTS/_cells_L2048_n50.npz"],
    ]
    return [{"paths": g, "hashes": [sha(ROOT / p) for p in g], "identical": len({sha(ROOT / p) for p in g}) == 1} for g in groups]


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    evidence = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "exp0006_interpolation": verify_exp0006(),
        "exp0006_hardcoded_c2": verify_c2_hardcoded(),
        "exp0011_3d_boundary": verify_3d_boundary(),
        "exp0011_nested_tau": verify_nested_tau(),
        "exp0011_width_sample_count": verify_3d_sample_count(),
        "result_hash_mismatches": verify_result_hashes(),
        "freeze_config_overwrite_demo": verify_freeze_config(),
        "qm007_approximation": verify_qm007(),
        "duplicate_3d_payloads": verify_duplicate_3d_payloads(),
        "qp005_qp006_duplicate_hashes": verify_duplicate_hashes(),
    }
    (OUT / "verified_candidate_evidence.json").write_text(json.dumps(evidence, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
