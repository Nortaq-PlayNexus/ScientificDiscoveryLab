# N-003 Feigenbaum audit repair (z=3/z=4)

This is an isolated Priority 0 repair for **N-003**. It does not touch the
historical `EXP-0014` engine, reports, preregistration, or result files. The
historical files remain evidence and are not overwritten.

## Scope and convention

The solver uses the explicit map

```text
f_a(x) = 1 - a*abs(x)**z,       x_0 = 0
```

Here `z` is the extremum exponent (2, 3, or 4), while `n` labels the
period-doubling level and the requested exact period is `P_n = 2**n`. The odd
case deliberately means `abs(x)**3`, not `x**3`.

For each `n`, the implementation starts from the previously verified
`a_(n-1)`, scans to its right, refines sign-changing brackets, and accepts a
root only when both direct and separately grouped power-of-two first-return
checks return exactly `P_n`. It uses 100-digit `mpmath` arithmetic by default;
the allowed preregistered range is 80--100 digits. A doubled-resolution scan is
required for every accepted root.

## Layout

- `requirements.txt` — isolated dependency pin (`mpmath==1.3.0`).
- `CODE/feigenbaum_n003_solver.py` — self-contained high-precision solver and
  period/sequence diagnostics.
- `CODE/freeze_prereg_n003.py` — creates the new protocol with exclusive
  create mode (`open(..., "x")`) and refuses to overwrite it.
- `CONFIG/prereg_N-003_feigenbaum_audit_repair.json` — frozen N-003 protocol;
  it is not the historical EXP-0014 preregistration.
- `CODE/run_n003_audit.py` — reads only the new protocol, runs z=2,3,4 through
  n=10, and exclusively creates the isolated result/report artifacts.
- `tests/test_n003_feigenbaum_audit_repair.py` — tiny-case, inherited-period,
  continuation, z=2 smoke, alpha-omission, and exclusive-freeze tests.
- `RESULTS/` and `REPORT/` — immutable-style outputs from this repair only.
- `RESULTS/INTEGRATION_REVIEW_20260924.json` — independent hash/consistency
  review of the finite repair result; it does not create a convergence claim.

## Reproduction

From `C:\Users\natha\ScientificDiscoveryLab`:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m pytest -q "03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/AUDIT_REPAIR_N003_FEIGENBAUM/tests/test_n003_feigenbaum_audit_repair.py"
python "03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/AUDIT_REPAIR_N003_FEIGENBAUM/CODE/run_n003_audit.py"
```

The runner refuses to overwrite its result/report files. A repeated production
run therefore requires an explicit archival decision rather than silently
replacing evidence.

## Interpretation

The z=2 result is a reproduction of the published Feigenbaum delta, not a
discovery. The z=3/z=4 parameter sequences are strictly increasing and all
completed periods pass the two independent certificates, but their finite
`delta_n` ratios are not monotone over n=2..10. Accordingly, this repair does
not claim a monotone convergence result for those families. No alpha is
reported because no spatial scaling variable is defined.

The actual Hu & Mao paper is *Period doubling: Universality and critical-point
order*, Phys. Rev. A **25**, 3259--3261 (1982), DOI
`10.1103/PhysRevA.25.3259`. It studies `f(x)=1-a*x**z` for even z=2,4,6,8 and
reports displayed delta values 4.669, 7.284, 9.296, and 10.948. It does not
provide a z=3 table entry; the historical z=3/z=4 pair is therefore not used
as a Hu & Mao comparison.
