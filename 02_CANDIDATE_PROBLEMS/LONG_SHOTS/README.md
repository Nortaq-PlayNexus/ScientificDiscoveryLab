# LONG SHOTS candidates

Feasibility = significant barriers (data infrastructure, compute, external
dependencies, or specialised tooling) currently block well-controlled runs.

| ID | Field | Question | Barrier |
|---|---|---|---|
| Q-F001 | fluid | 2D turbulent dual-cascade spectra | CPU-only torch; needs GPU/CUDA |
| Q-F002 | fluid | Cylinder vortex-street St-Re map | solver cost / domain |
| Q-A003 | cosmology | CMB anomaly reproduction | HEALPix not installed; big downloads |
| Q-B003 | neuroscience | EEG 1/f slope reproducibility | multi-GB datasets; preprocessing |

These remain registered but are NOT queued. Reassess if/when: CUDA torch becomes
available, healpy installed + data cached, or a specific public dataset is curated.

Reality check: F-field entries are methodology/numerics projects (their science is
known); the honest win is a calibrated measurement, never a discovery.