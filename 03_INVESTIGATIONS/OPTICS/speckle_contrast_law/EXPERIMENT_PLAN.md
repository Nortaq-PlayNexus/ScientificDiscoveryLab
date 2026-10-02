# EXPERIMENT_PLAN — Speckle contrast law

Preregistered protocol for EXP-0002 (Q-O001 / HYP-001). Frozen before execution;
any later change logged in CONFIG/changelog.jsonl.

## Physics model

Fully-developed speckle: complex Fourier spectrum U(f) = A(f) * exp(i*phi(f)) with
random independent uniform phases and fixed disk aperture A. Inverse-transform to
field; intensity I = |E|^2. Repeat M times (independent ensembles A + phases),
sum intensities: I_sum = sum_m I_m. Contrast C = std(I_sum)/mean(I_sum).

Theoretical result (Goodman): I_m exponentially distributed (contrast 1);
I_sum -> gamma(M) contrast 1/sqrt(M).

## Implementation (CODE/run_speckle_contrast.py)

- Independent speckle pattern m: aperture support = pixels inside radius r
  (r = N/8) in Fourier plane; unit amplitude inside, zero outside; random phases
  from lab rng; E = ifft2(ftshift?...) — see code. intensity = |E|^2.
- All grids/realizations use the lab RNG; seeds recorded.
- Contrast computed per realisation and averaged; bootstrap CI (n_boot=2000) per
  (M, N) cell using realisation-level C values.
- Estimator C7: spatial contrast (full-grid std/mean within the interior region)
  vs ensemble contrast (across realisations) both computed; primary metric is the
  interior spatial contrast averaged over realisations.

## Steps

1. For each N in {32,64,128,256}, for each M in {1,2,4,8,16}:
   - generate 32 realisations; compute C_hat per realisation (interior ROI);
   - store C_hat vector; bootstrap CI; r = C*sqrt(M); deviation trend.
2. Positive/seed/generator checks (C1, C3, C5).
3. Write experiment.json + append registry rows (EXP-0002...).
4. REPLICATION: independent implementation (direct std-normal complex Gaussian
   speckle with same sum contrast interpreted analytically), compare.
5. Write TECHNICAL + PLAIN ENGLISH summaries into REPORT/.

## Decision rules (frozen)

- Claim H1 supported if, at N=256, all M cells have 99% bootstrap CI of r = C*sqrt(M)
  containing 1.0 AND FDR passes.
- Otherwise: B2 flag "resolution-persistent deviation", go to kill-the-hypothesis +
  independent implementation; cannot claim stronger than "controlled deviation" or
  "falsified prediction".