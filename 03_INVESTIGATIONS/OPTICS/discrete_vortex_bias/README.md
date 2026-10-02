# EXP-0015 — Discrete optical-vortex detection bias

**Status:** preregistered discovery experiment; no novelty claim is authorized by
this directory alone.

## Question

Under what combinations of sampling, propagation, boundary conditions, and
 detector definition does a discrete optical-vortex detector produce a systematic
bias relative to a field whose continuous topological charge is known?

This investigation treats the historical `48 -> 176` DBS trajectory and the
`z=1280 um` excess as leads, not as established physical effects. The primary
goal is to separate propagation error from sampling/detection error.

## Source and isolation

- The historical sandbox remains at `C:\Users\natha\code\coherent-optical-ai-sandbox`.
- The corrected EXP-0007 audit remains at `C:\Users\natha\AI_RESEARCH\EXP-0007`.
- This directory is lab-native and does not modify either source project.
- New results are written only below `RESULTS/` and reports below `REPORT/`.

## Frozen protocol

`CONFIG/prereg_EXP-0015.json` is created with the laboratory's exclusive
preregistration API. Parameters and gates are not silently changed after
execution. Any necessary amendment is appended to `CONFIG/changes.jsonl` with a
hash chain.

## Planned stages

1. **Analytical calibration:** single vortex, ±1 pair, higher-charge vortex,
   and a known multi-vortex field at controlled subpixel offsets.
2. **Detector battery:** raw plaquette winding, same-sign connected-component
   clustering, intensity-supported clustering, and an independent local-minimum
   contour detector.
3. **Convergence matrix:** square, rectangular, and non-power-of-two grids;
   dense propagation sweep; padding; wavelength and physical-scale controls.
4. **Oversample → downsample:** a 2048² periodic reference field is propagated
   first, then sampled by the lower-resolution detectors. Direct continuous
   sampling is compared with propagated-reference sampling.
5. **Nulls and red-team controls:** matched-spectrum phase randomization,
   matched-amplitude phase randomization, random complex fields, sign/position
   controls, precision and implementation checks.
6. **Independent implementation:** a separately written NumPy/SciPy script
   repeats a decisive subset without importing the main detector code.

A result is promoted only if it survives convergence, detector independence,
padding, subpixel shifts, nulls, and independent implementation. Otherwise it is
reported as a detector/sampling artifact or an inconclusive result.

## Reproduction

From the laboratory root:

```powershell
python 03_INVESTIGATIONS\OPTICS\discrete_vortex_bias\CODE\run_convergence.py --stage calibration
python 03_INVESTIGATIONS\OPTICS\discrete_vortex_bias\CODE\run_convergence.py --stage convergence
python 03_INVESTIGATIONS\OPTICS\discrete_vortex_bias\CODE\run_convergence.py --stage oversample
python 03_INVESTIGATIONS\OPTICS\discrete_vortex_bias\CODE\run_convergence.py --stage full
python 03_INVESTIGATIONS\OPTICS\discrete_vortex_bias\CODE\independent_replication.py
python 03_INVESTIGATIONS\OPTICS\discrete_vortex_bias\CODE\run_regimes.py
python 03_INVESTIGATIONS\OPTICS\discrete_vortex_bias\CODE\run_geometry.py
python 03_INVESTIGATIONS\OPTICS\discrete_vortex_bias\CODE\run_detector_scale.py
python 03_INVESTIGATIONS\OPTICS\discrete_vortex_bias\CODE\run_tracker.py
python 03_INVESTIGATIONS\OPTICS\discrete_vortex_bias\CODE\run_reference_rectangular.py
python 03_INVESTIGATIONS\OPTICS\discrete_vortex_bias\CODE\run_close_reference.py
python 03_INVESTIGATIONS\OPTICS\discrete_vortex_bias\CODE\run_exact_zero.py
python 03_INVESTIGATIONS\OPTICS\discrete_vortex_bias\CODE\run_seed_ladder.py
```

The exact command, environment, hashes, and result paths are recorded in
`RESULTS/experiment.json` and the stage JSON files.
