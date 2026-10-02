# Fast regime analysis — EXP-0015

**Source:** `RESULTS/regimes_fast_20260924_140842.json` (1,040 rows, exploratory)

## Close pair

At z=0, raw/clustered/supported detectors range from 0 to 2 features as the
pair separation and grid change; the local contour ranges from 0 to 4. At
256², raw winding is two for every tested separation ≥2 µm, while the contour
detector returns three for the 2 µm pair at one tested shift. The full result
shows that the raw estimator is not a universal physical locator either: it
can miss a close pair at sufficiently coarse grids, while its charge balance
can remain correct.

## Higher charge

At z=0, a charge-q singularity is represented differently by the detectors:

| Charge | Raw winding | Clustered | Local contour |
|---:|---:|---:|---:|
| +1 | 1 | 1 | 1 |
| +2 | 2–4 | 1–2 | 1 |
| +3 | 3–5 | 1–2 | 1 |
| +4 | 4 | 1–2 | 1 |
| +6 | 6–10 | 2–4 | 1 |

The total net charge is generally preserved even when feature count is not.
This is a semantic decomposition effect, not a physical birth of additional
vortices.

## Status

The reduced map confirms that detector choice and charge representation are
first-order variables. It does not establish a universal scaling law or a new
physical phenomenon. The full dense/random map and multi-seed null distribution
remain separate exploratory results.
