# TECHNICAL SUMMARY — EXP-0002 (Q-O001, HYP-001)

## Objective

Test whether simulated fully-developed speckle obeys the contrast law
C(M) = 1/sqrt(M) for M summed independent speckle intensities, and characterise
the finite-grid deviation.

## Methods

- **Speckle generator**: random-phase disk pupil of radius r = N/8 on an N×N grid;
  complex field E = ifft2(pupil·e^{iφ}), intensity I = |E|². For a random-phase
  pupil the image-plane field is complex Gaussian (CLT over ~π(N/8)² pupil cells),
  so I is exponentially distributed with spatially uniform mean — the
  fully-developed speckle limit.
- **Summed speckle**: for M = 1,2,4,8,16, sum M independent realisations
  I_sum = Σ_m I_m; contrast C = std(I_sum)/mean(I_sum).
- **Grid**: N ∈ {32, 64, 128, 256}; 32 independent realisations per (N,M) cell.
- **Estimators**: mean C over realisations; percentile bootstrap CI across
  realisations (n_boot = 500, alpha = 0.01); two-sided bootstrap p-value for
  r = C·sqrt(M) against the null r = 1; Benjamini–Hochberg FDR over the 20 cells.
- **Generator check**: KS test of the single-speckle intensity marginal
  (N=256, 20 000 subsampled pixels) against Exponential.
- **Seed ladder**: r at (N=128, M=8) re-measured at seeds {7, 123, 2023, 314159,
  271828}.
- **Interior control**: contrast recomputed on the central 80%-radius disk.

## Results

- r = C·sqrt(M) lies in [0.984, 1.005] over the whole 20-cell grid.
- **N = 256**: r = 0.9968 – 1.0003; all 99% bootstrap CIs contain 1.0 →
  H1 supported at the largest grid.
- **Deviation is resolution-dependent**: low-N cells show a slight deficit
  (worst N=32: r ≈ 0.985–0.994; N=64 M=2: r = 0.9840, the only FDR-flagged cell
  at alpha = 0.01). The deficit shrinks towards 1 as N rises — i.e. it behaves
  like a finite-grid/sampling effect, matching the preregistered prediction.
- **Generator check**: KS = 0.0071, p = 0.27 → exponential marginal not rejected.
- **Seed ladder**: r ∈ [0.9947, 1.0042] (range 0.0095), stable.
- **Interior vs full grid**: contrast agrees to ≲ 1% at N ≥ 128 (no boundary
  artifact).
- **Independent implementation** (direct complex-Gaussian speckle, independent
  RNG, no FFT): r = 1.0000 – 1.0005 ± 0.0012 (3σ) across M — reproduces the law.

## Decision

**H1_SUPPORTED**: C(M) = 1/sqrt(M) reproduced; residual low-N deviations are
consistent with finite-grid sampling and shrink with resolution (as predicted).

## Controls run

C1 positive control (M=1 → C≈1) ✓; C2 realisation bootstrap ✓; C3 seed ladder ✓;
C4 resolution ladder ✓; C5 generator KS ✓; C6 independent implementation ✓;
C7 ensemble-vs-space (interior) ✓; C8 FDR ✓.

## What this does NOT prove

- Nothing about real optical systems beyond the idealised model.
- Nothing novel: the law is textbook (Goodman).
- It does not certify that the lab's future optics claims are correct; only that
  the statistical + simulation pipeline behaves as specified for this case.

## Reproduction

```
cd 03_INVESTIGATIONS/OPTICS/speckle_contrast_law
python CODE/run_speckle_contrast.py        # ~2 min CPU; writes CONFIG/ + RESULTS/
python REPLICATION/independent_check.py    # independent route, ~1 min
python CODE/make_figure.py                 # FIGURES/EXP-0002_contrast_law.png
```

Config: CONFIG/prereg_EXP-0002.json (frozen), CONFIG/EXP-0002_experiment.json,
seed 42, lab RNG (sha256-derived). Registry: CONFIG/registry.jsonl (append-only).

## Limitations

- Single aperture fraction (1/8) and one estimator family tested.
- Statistical p-values are bootstrap-based and resolution-dependent; the FDR
  flag on N=64 M=2 should be read with the resolution ladder, not in isolation.
- CPU-only runtime; no GPU used.

## Note on process (honesty)

A bug in the engine's BH-FDR step-up indexing (flagged all cells) was found by the
infra validation suite mid-session, fixed, covered by a regression check, and the
experiment was re-run. The first run's FDR flags are superseded; the appended
registry keeps both rows.