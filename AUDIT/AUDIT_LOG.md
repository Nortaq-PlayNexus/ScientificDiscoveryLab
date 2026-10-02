# Independent Audit Log — ScientificDiscoveryLab

This log records the independent audit initiated on 2026-09-24. Historical experiment outputs are preserved. Any reproduction that could overwrite outputs is run against a copied tree, not the original result directories.

## 2026-09-24T03:23:55+10:00 — Audit initialization and baseline execution

- **Experiment:** Repository baseline and prior-audit verification
- **Command:** `python -m pytest`
- **Working directory:** `C:\Users\natha\ScientificDiscoveryLab`
- **Environment:** Windows 10.0.19045; Python 3.14.7; NumPy 2.5.3; SciPy 1.18.1; scikit-image 0.26.0; scikit-learn 1.9.1
- **Seed:** Not applicable
- **Parameters:** Default `pytest.ini`; 287 collected tests
- **Result:** 287 passed, 411 deprecation warnings, 26.60 s
- **Discovery:** Software unit tests pass when invoked as `python -m pytest`. Invoking the `pytest` console script directly previously produced 29 collection errors because `src` was absent from `sys.path`; this is a launcher/import-path issue, not evidence that scientific experiments passed.
- **Error:** Historical unit tests exercise software behavior, not scientific validity or reproduction of published numerical results.
- **Decision:** Preserve original files; inspect code and result provenance; run reproductions in an isolated copy.
- **Generated output:** This log.

## 2026-09-24T03:23:55+10:00 — Prior audit preservation

- **Experiment:** Preserve pre-existing audit material
- **Command:** PowerShell copy of all prior root-level `AUDIT` files and `AUDIT\REVISED_DOSSIERS` into `AUDIT\PRIOR_AUDIT_20260923`
- **Result:** 39 files copied before creation of the new audit deliverables.
- **Discovery:** The previous `FINAL_SCIENTIFIC_AUDIT_REPORT.md` calls the review complete but explicitly says experiments were not actually re-executed and several artifacts/data sources were not examined. Its reproduction matrix primarily rates code/config existence and prior independent-check reports rather than recording new observed values.
- **Decision:** Treat prior reports as claims to audit, not ground truth.
- **Generated output:** `AUDIT\PRIOR_AUDIT_20260923\`.

## 2026-09-24T03:24:00+10:00 — Inventory and baseline validation

- **Commands:** `python -m pytest`; recursive Python/JSON/file inventory; SQLite schema/count query; archive inspection.
- **Working directory:** `C:\Users\natha\ScientificDiscoveryLab`.
- **Environment:** Windows 10.0.19045; Python 3.14.7; NumPy 2.5.3; SciPy 1.18.1; scikit-image 0.26.0; scikit-learn 1.9.1; pytest invoked as a module.
- **Observed:** 287 tests passed, 411 warnings, 26.60 s. Baseline inventory 513 files / 221,270,825 bytes / 135 Python files. `sovereign_biolab.db` has 21 tables and zero rows in every table. `05_DATA/raw`, `processed`, `generated`, and `external_sources` are empty. `percolation.rar` is a percolation snapshot, not an independent dataset.
- **Discrepancy:** historical status and prior reports imply more data/provenance than the filesystem contains.
- **Decision:** treat generated outputs as unverified claims; preserve all historical files.

## 2026-09-24T03:25:00+10:00 — Isolated reproduction set

- **Command pattern:** copied the repository to `C:\Users\natha\AppData\Local\Temp\opencode\ScientificDiscoveryLab_audit_20260924_0325` and ran selected runners there.
- **Experiments:** EXP-0002, EXP-0003, EXP-0004, EXP-0005, EXP-0008 C7, EXP-0010, EXP-0014 stored result, and later EXP-0007.
- **Observed:** byte-identical deterministic reruns for EXP-0002 (`2e38b3...cec7`), EXP-0003 (`910657...8531`), EXP-0004 (`8c7c...`), EXP-0005 (`0995...`), EXP-0008/C7, EXP-0010, and stored EXP-0014. These establish determinism only; most use the same implementation.
- **Decision:** do not count a byte-identical rerun as independent validation; require alternate implementations/raw-data checks for primary claims.

## 2026-09-24T03:30:00+10:00 — EXP-0007 isolated rerun

- **Command:** `$log='C:\Users\natha\ScientificDiscoveryLab\AUDIT\INDEPENDENT_AUDIT_20260924\runs\percolation_exp0007.log'; & python '03_INVESTIGATIONS\PHYSICS\percolation\CODE\run_percolation_exp0007.py' *>&1 | Tee-Object -FilePath $log; exit $LASTEXITCODE`.
- **Working directory:** isolated temporary tree; historical result path remained untouched.
- **Observed:** decision `H0_SUPPORTED`; bond-wrap intercept `0.5006874530252672`; p50 values `{32:0.49866069517268136,48:0.4974502702853924,64:0.5003325765058546,96:0.4984955365005837,128:0.5012222892133987,192:0.4992417301851336}`; C4 shift `0.0011108652357739723`; C6 max deviation `0.0016798422002474167`; C8 `1/nu=0.7255466307593994`.
- **Comparison:** historical and isolated JSON SHA-256 both `a09e4f204dfef9cab7dbe5bb5769f94093d09ecab45f9a90fe6bbff79552553b`; semantic difference count 0.
- **Decision:** classify as deterministic reproduction compatible with exact bond `p_c=1/2`, not a precision validation.

## 2026-09-24T03:35:00+10:00 — EXP-0003 parallel sub-agent launch

- **Task file:** `AUDIT/INDEPENDENT_AUDIT_20260924/SUBAGENT_EXP0003_BROADBAND_TASK.md`.
- **First command:** `opencode run --agent general ...` without a model; failed before work with provider-credit error.
- **Correction:** listed available models, selected `opencode/space-bunny-free`, and launched a new background OpenCode session with the same task and isolated output directory.
- **Decision:** satisfy the explicit parallel-sub-agent requirement without changing the main audit or historical experiment tree.

## 2026-09-24T03:40:00+10:00 — EXP-0003 fixed-spectrum sweep

- **Command:** `python AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/CODE/run_broadband_convergence.py --realizations 4 --skip-controls`.
- **Parameters:** P={4,6,8,12,16,24,32,48,64}; sigma={0.10,0.25,0.50,0.75}; seeds={42,7,123,2023,314159,271828}; four realizations per seed; 2000 bootstrap draws; fixed physical Gaussian spectrum; 24 central wavelengths across the box.
- **Runtime/environment:** 205–206 s; Python 3.14.7; NumPy 2.5.3; SciPy 1.18.1; Windows 10.0.19045.
- **Observed ratios (discrete prediction):** sigma .10: `1.0183,1.0097,1.0091,1.0039,1.0041,1.0031,1.0027,0.9990,0.9980`; sigma .25: `0.9935,1.0029,0.9984,1.0017,1.0007,1.0031,1.0069,1.0047,0.9975`; sigma .50: `0.9146,0.9682,0.9854,0.9952,1.0007,0.9982,0.9957,1.0000,0.9971`; sigma .75: `0.8285,0.9262,0.9557,0.9781,0.9865,0.9953,0.9966,0.9984,0.9966` for P in the frozen order.
- **Interpretation:** broad-band deficit is strongest at low P and shrinks toward one; narrow sigma .10/.25 are already near one with a small finite-window bias.
- **Caveat:** the main run skipped controls; the first control run was not accepted without correction.

## 2026-09-24T03:45:00+10:00 — EXP-0003 controls and failed first implementation

- **Command:** `python AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/CODE/run_broadband_convergence.py --skip-main`.
- **Observed:** detail detector controls ran, but the process exited 255 during the larger control sequence. The raw interpolation output showed ratios near `0.06` for factor 2 and `0.004` for factor 4. Static inspection found the helper divided refined-cell density by `factor**2` after the refined grid already had `factor**2` times as many cells.
- **Sanity output:** exact synthetic vortex at a grid vertex gave zero winding and zero contour; this is a degenerate test geometry, not a valid detector null.
- **Decision:** preserve the failed raw run; do not cite it as a successful control. Write and run an audit-only corrected control script.

## 2026-09-24T03:50:00+10:00 — Corrected EXP-0003 controls

- **Command:** `python AUDIT/INDEPENDENT_AUDIT_20260924/broadband_controls_corrected.py`.
- **Correction:** refined winding density is converted to per-original-cell density by multiplying by `factor**2`; added regularized sub-cell/vertex-safe winding test, direct complex FFT fields, controlled low-pass spectra, and paired interpolation.
- **Runtime:** 57.5 s.
- **Observed corrected interpolation ratios:** P=4 sigma=.75 factor 2 mean `0.9664±0.0123`, factor 4 `0.9945±0.0108`; P=4 sigma=.50 factor 4 `0.9943±0.0185`; P=16 sigma=.75 factor 4 `0.9998±0.0069`. Direct-complex ratios at P=4 sigma=.75 mean `0.8301±0.0144`, rising to `1.0032±0.0191` at P=32. Low-pass controls show the same approach to one as the grid resolves the spectrum.
- **Synthetic test:** regularized unit vortex winding density `0.0003188776`, charge +1, max charge 1; contour result remains zero for the vertex-intersection geometry and is not treated as a failure.
- **Decision:** finite spectral support/sampling is the best-supported explanation for the observed broadband deficit; retain implementation caveats and do not claim novelty.

## 2026-09-24T03:55:00+10:00 — Percolation independent reanalysis

- **Command/method:** independent NumPy PCG64 site configurations with `scipy.ndimage.label`, free-boundary square site percolation; raw NPZ reanalysis with bootstrap slopes.
- **Observed:** EXP-0009 `D_f=1.87014±0.02229`, gamma/nu `1.75943±0.03266`, beta/nu `0.12986±0.02229`; EXP-0010 `D_f=1.89670±0.02882`. Independent non-power sequence `D_f=1.87747±0.02657`; matched even `1.86738±0.02809`; matched odd `1.93044±0.02823`; power/non-power difference about 0.97 SE.
- **Decision:** no power-of-two lattice artifact; EXP-0009 deviations are finite-sample/estimator effects.

## 2026-09-24T04:00:00+10:00 — Q-P006/Q-P007 audit and corrected tau

- **Static commands:** SHA-256 comparison of Q-P005/Q-P006 NPZ files; inspection of `run_phase2.py`; attempted cache reload.
- **Observed:** all three Q-P006 raw files are byte-identical to Q-P005; Q-P007 stores one nested size array per realization; `ss[1:]` discards every tail; current runner fails with `KeyError: sizes`.
- **Corrected command:** `python AUDIT/INDEPENDENT_AUDIT_20260924/corrected_tau_reanalysis.py`.
- **Method:** independent PCG64 + `scipy.ndimage.label`, largest cluster removed per realization, cumulative fits over multiple windows; L=128/256/512, n=80/60/30, canonical versus refined p_c with common random masks.
- **Observed:** corrected primary tau means approximately 1.813 (L=128), 1.927 (L=256), 1.930 (L=512); paired refined-minus-canonical changes `0`, `0`, and `3.0e-5`; raw compressed arrays saved as `corrected_tau_raw_L*.npz`.
- **Decision:** Q-P007 historical tau is invalid; p_c refinement does not explain the discrepancy at tested sizes.

## 2026-09-24T04:05:00+10:00 — Feigenbaum independent continuation

- **Initial diagnostic:** imported the historical engine and ran z=2/3/4; z=3 repeated the n=2 root and z=4 reversed to an earlier root. Global scan/fallback was insufficient.
- **Command:** `python AUDIT/INDEPENDENT_AUDIT_20260924/independent_feigenbaum_reanalysis.py`.
- **Method:** mpmath 100-digit arithmetic, first sign-changing root to the right of each verified preceding root, horizon scaled from previous step, bisection, first-return verification for all earlier powers.
- **Observed:** all periods verified and sequences strictly increasing. `delta_8`: z=2 `4.669060660648268`; z=3 `6.084672065631017`; z=4 `7.285086100551313`. Residuals approximately 1e-98 or smaller at 100-digit precision.
- **Discrepancy:** historical z=3 duplicates, z=4 rollback, invalid preregistration, nested result path, and hardcoded C3/C4/C6 pass fields.
- **Decision:** z=2 reproduction supported; historical higher-order claims contradicted; corrected roots recorded as independent evidence, not novelty.

## 2026-09-24T04:10:00+10:00 — Fresh RNG calibration

- **Initial command failed:** `python AUDIT/INDEPENDENT_AUDIT_20260924/rng_calibration_audit.py` -> `ModuleNotFoundError: No module named 'engine'` because the script was launched from the lab root without adding `04_SHARED_ENGINE` to `sys.path`.
- **Fix:** added the shared-engine path based on `Path(__file__).resolve().parents[2]`; reran the command.
- **Final command:** `python AUDIT/INDEPENDENT_AUDIT_20260924/rng_calibration_audit.py`.
- **Design:** exact historical battery, 80 fresh seeds (100000–100079) for G_LAB/G_PCG/G_MT, 1,920 p-values per generator, per-test marginal KS/rejection diagnostics, pooled diagnostics, and p-value correlations.
- **Runtime:** 85.6 s.
- **Observed:** pooled KS p-values G_LAB `0.3446`, G_PCG `0.5372`, G_MT `0.1120`; maximum absolute off-diagonal p-value correlation approximately `0.99` for each generator; 18–20 pairs with |correlation|≥0.3. G_LAB runs-test KS p≈`0.000413`; G_MT runs-test p≈`0.00173`; controls also show marginal failures.
- **Decision:** pooled “CERTIFIED” decision invalid; report battery dependence/calibration unresolved, not a uniquely defective lab RNG.

## 2026-09-24T04:15:00+10:00 — Prime-gap reanalysis and literature checks

- **Command/method:** independent sieve/reanalysis of stored 1e8 prime data; block diagnostics, lag correlations, structural first-bin check; deterministic 1e8/1e9 reruns.
- **Observed:** 5,761,455 primes to 1e8; variance ratio to Exp(1) `0.71925`; lag-1 autocorrelation `-0.03745`; block/iid SE ratios `0.269,0.521,0.611,0.718`; first bin structurally impossible; C7 agreement exact; 1e8/1e9 semantic rerun agreement.
- **Decision:** descriptive finite-range deviation; no novel mechanism or asymptotic claim.
- **Literature queries:** broad web search connector failed; Crossref/OpenAlex metadata queries used instead. Verified Nye/Berry DOI `10.1098/rspa.1974.0012`, Berry/Dennis `10.1098/rspa.2000.0602`, Rice `10.1002/j.1538-7305.1944.tb00874.x`, Newman/Ziff `10.1103/PhysRevLett.85.4104`, Gallagher `10.1112/S0025579300016442`, Feigenbaum `10.1007/BF01020332`, Hu/Mao `10.1103/PhysRevA.25.3259`, and NIST `10.6028/NIST.SP.800-22r1a`.
- **Search limitation:** metadata/abstract search, not a full systematic review; no exact EXP-0003 protocol match located, so novelty remains unresolved.

## 2026-09-24T04:20:00+10:00 — Current inventory refresh

- **Command:** fresh Python `pathlib.rglob` inventory excluding `__pycache__`, `.git`, and `.pytest_cache`; AST parse check.
- **Observed:** 606 files / 223,960,054 bytes; 149 Python files; 148 parsed; one BOM-related AST warning at `03_INVESTIGATIONS/MATHEMATICS/collatz/CODE/run_collatz.py`; 254 Markdown, 108 JSON, 20 NPZ, 35 logs, 6 CSV, 4 PNG, 1 DB, 1 RAR.
- **Generated output:** `AUDIT/INDEPENDENT_AUDIT_20260924/current_inventory.json`.
- **Decision:** distinguish baseline 513-file inventory from current audit-expanded inventory in all reports.

## 2026-09-24T04:23:50+10:00 — Required report deliverables

- **Files written/updated:** `PROJECT_INVENTORY.md`, `CLAIM_REGISTRY.md`, `REPRODUCTION_MATRIX.md`, `BUGS.md`, `NOVELTY_REVIEW.md`, `NEXT_EXPERIMENTS.md`, and `FINAL_SCIENTIFIC_AUDIT.md` under `AUDIT/`.
- **Final classification:** known-law reproductions and audit findings are supported where independently checked; novelty, 3D closure, Q-P007 tau, RNG certification, Collatz iff, and S9 empirical claims are not supported.
- **Next action:** execute Priority 0 repairs in `NEXT_EXPERIMENTS.md`; do not announce new discoveries from the current tree.

## 2026-09-24T04:24:00+10:00 — Historical-file preservation verification

- **Command:** compared current SHA-256 hashes for every non-`AUDIT` file in the baseline `file_manifest.json` against the recorded hashes.
- **Observed:** 433 non-audit baseline files checked; 0 changed; 0 missing.
- **Decision:** audit scripts and reports did not overwrite historical experiment files. New artifacts are isolated under `AUDIT/` and the approved temporary tree.

## 2026-09-24T04:25:00+10:00 — Deliverable validation

- **Command:** parsed every JSON file under `AUDIT/` and checked the eight required Markdown deliverables.
- **Observed:** 31 JSON files valid; 0 parse failures; 0 required files missing.
- **Decision:** report set is internally readable and complete at handoff.

## 2026-09-24T04:26:00+10:00 — EXP-0003 investigation addendum

- **Action:** added `03_INVESTIGATIONS/OPTICS/vortex_density/REPORT/AUDIT_ADDENDUM_EXP-0003_20260924.md` as a new, non-destructive report file.
- **Reason:** satisfy the parallel-sub-agent instruction to place complete findings in the appropriate EXP-0003 research area while preserving historical outputs.
- **Contents:** fixed-spectrum resolution table, controls, failed interpolation artifact, corrected control path, and conservative classification.
- **Decision:** historical EXP-0003 result files remain unchanged; the addendum points to the isolated audit evidence.

## 2026-09-24T04:27:00+10:00 — Literature retrieval details

- **Direct metadata endpoints attempted:** Crossref works/title-query endpoints for Nye–Berry, Berry–Dennis, Gallagher, Hu–Mao, percolation, and prime-gap references; OpenAlex title-filter endpoints for the same topics; NIST SP 800-22 Rev. 1a official page.
- **Failed/limited attempts:** the general web-search connector returned “Unable to search” for several queries; an initially guessed Nye–Berry DOI (`10.1098/rspa.1974.0188`) resolved to an unrelated Lovelock paper; an initially guessed Hu–Mao DOI (`10.1103/PhysRevA.26.3420`) returned 404; the old NIST `/r1/a/final` URL returned 404.
- **Corrections:** title-filtered metadata identified Nye–Berry DOI `10.1098/rspa.1974.0012`, Hu–Mao’s actual title/DOI `10.1103/PhysRevA.25.3259`, and the current NIST page `/pubs/sp/800/22/r1/upd1/final`.
- **Decision:** record failed guesses and search limitations rather than silently treating them as evidence; use only verified metadata in `NOVELTY_REVIEW.md`.

## 2026-09-24T04:28:00+10:00 — Final inventory refresh after controls/addendum

- **Command:** reran the cache-excluding recursive inventory after the corrected EXP-0003 controls and investigation addendum were written.
- **Observed:** 633 files / 225,411,614 bytes; 150 Python files; 149 parsed; one BOM-related AST warning; 262 Markdown, 116 JSON, 20 NPZ, 40 logs, 11 CSV, 4 PNG, 1 DB, and 1 RAR.
- **Correction:** `PROJECT_INVENTORY.md` and `current_inventory.json` now report this final count; the earlier 606-file entry remains as a timestamped intermediate inventory in the log.

## 2026-09-24T04:29:00+10:00 — Final JSON/deliverable recheck

- **Command:** reparsed all `AUDIT/**/*.json` and rechecked required report paths.
- **Observed:** 32 JSON files valid; 0 parse failures; 0 required deliverables missing.
- **Decision:** handoff artifacts are complete and machine-readable.

## 2026-09-24 — Priority repair implementation session

- Preserved historical outputs and added isolated Q-P007 N-001, historical 2D
  provenance, 3D percolation, and prime-gap repair areas.
- The prime-gap repair verifies lower-prime support, correct step-up BH/log
  tails, structural first-bin emptiness, and all 5,761,455 first-segment
  primes below 1e8; focused tests passed 14/14 and no scale run was launched.
- The 2D read-only audit verified 51/51 historical hashes before/after and
  regenerated available stored statistics while classifying missing controls
  and coupled checks precisely; focused tests passed 10/10.
- Corrected Q-P007 cumulative tau conversion to `1 - survival_slope`; the v2
  smoke validates and explicitly reports `scientific_result: null`.
- Added explicit 2D/3D spanning dimensions, opposite-plane C7, a disabled
  legacy 3D runner, exact sample accounting, ragged arrays, active tau size,
  realization-level bootstrap, raw hashes, and fail-closed scientific configs.
- Validated all 38 EXP-0003 broadband manifest entries while preserving the
  malformed source manifest.
- Hardened immutable preregistration, hash-chain change logs, and result hash
  scopes; corrected user-facing molecular/reaction evidence labels.
- Isolated pytest database state. Full suite passed 328 tests at the first
  integration run and the persistent database SHA-256 remained unchanged.
- No production scientific experiment was launched. Detailed handoff:
  `AUDIT/REPAIR_LOG_20260924.md`.
