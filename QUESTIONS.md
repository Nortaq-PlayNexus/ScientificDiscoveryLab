# QUESTIONS

Master registry of scientific questions considered by this laboratory.
IDs: `Q-####`. Each candidate also has a fuller profile in
`02_CANDIDATE_PROBLEMS/MASTER_CANDIDATES.md`.

Status values:

- `OPEN` — registered, not yet investigated
- `INVESTIGATING` — has an active investigation in `03_INVESTIGATIONS/`
- `PARTIALLY_ANSWERED` — evidence exists but incomplete
- `ANSWERED_LOCALLY` — answered for our purposes (with controls)
- `CLOSED_LITERATURE` — the lab determined the question is already answered in
  the literature
- `WITHDRAWN` — dropped as not computable/not meaningful/duplicate

## Question table

Registered candidate questions and their status. Full profiles:
`02_CANDIDATE_PROBLEMS/MASTER_CANDIDATES.md`.

| ID | Field | Question | Feasibility | Status |
|---|---|---|---|---|
| Q-M001 | mathematics | Generalized Collatz stopping-time statistics | HIGH | OPEN |
| Q-M002 | mathematics | Prime gap distribution vs Poisson | HIGH | OPEN |
| Q-M003 | mathematics | Constant digit normalcy scan | HIGH | OPEN |
| Q-M004 | math/compsci | Abelian sandpile exponents | MEDIUM | OPEN |
| Q-M005 | mathematics | Feigenbaum universality in higher-order 1D maps | HIGH | ANSWERED_LOCALLY (z=2 validated: delta_n converges to 4.6692016091029 at n=8; z=3,4 partial — ongoing) |
| Q-M006 | mathematics | First-passage universality in correlated walks | HIGH | OPEN |
| Q-O001 | optics | Speckle contrast law C(M)=1/sqrt(M) | HIGH | ANSWERED_LOCALLY (EXP-0002) |
| Q-O002 | optics | Vortex density in random fields (Nye-Berry/Freund) | HIGH | ANSWERED_LOCALLY (EXP-0003; anisotropic-spectra & propagation sub-questions remain OPEN) |
| Q-O003 | optics | Propagation-invariance audit vs surrogate nulls | HIGH/MED | OPEN |
| Q-O006 | optics/computational science | When does discrete optical-vortex detection produce systematic topological-count bias? | HIGH | PARTIALLY_ANSWERED (EXP-0015; known numerical failure modes, no novelty) |
| Q-O004 | optics/infotheory | Speckle maximum decodable information | MEDIUM | OPEN |
| Q-O005 | optics/materials | Speckle spectrum vs layer roughness | MEDIUM | OPEN |
| Q-P001 | physics/math | Graph spectral statistics (GOE/Poisson transitions) | MEDIUM | OPEN |
| Q-P002 | physics | FPUT recurrence / thermalization scaling | MEDIUM | OPEN |
| Q-P003 | physics/optics | Quantum-looking classical correlations (falsification) | HIGH | OPEN |
| Q-P004 | physics | Percolation thresholds reproduction | HIGH | SUPPORTED_LIMITED (stored estimates anchor-compatible; EXP-0006 controls incomplete, EXP-0007 precision validation inconclusive) |
| Q-P009 | physics | Is the 2D site cluster-mass exponent biased by power-of-two lattice sizes? (audit N-005) | HIGH | ANSWERED_LOCALLY (EXP-0017: LATTICE_ARTIFACT_UNSUPPORTED, beta = -0.0014, 90% CI [-0.0039, +0.0008] vs preregistered margin +/-0.010) |
| Q-F001 | fluid | 2D turbulence dual cascade | LOW | OPEN |
| Q-F002 | fluid | Cylinder vortex-street St-Re map | LOW/MED | OPEN |
| Q-F003 | fluid | 1D Burgers shock scheme-dependence | MEDIUM | OPEN |
| Q-A001 | astronomy | Exoplanet transit re-detection | MEDIUM | OPEN |
| Q-A002 | astronomy | GAIA calibration reproduction | MEDIUM | OPEN |
| Q-A003 | cosmology | CMB anomaly reproduction | LOW | OPEN |
| Q-A004 | astronomy/earth | Fireball cluster scan-statistics | MEDIUM | OPEN |
| Q-C001 | climate | Paleoclimate reconstruction sensitivity | MEDIUM | OPEN |
| Q-C002 | climate | ENSO simple-model baseline skill | HIGH | OPEN |
| Q-Mx001 | materials | Band-gap model leakage audit | MEDIUM | OPEN |
| Q-B001 | biology | Gene-circuit bimodality (Gillespie) | MEDIUM | OPEN |
| Q-B002 | biology | GC-skew test power | MEDIUM | OPEN |
| Q-B003 | neuroscience | EEG 1/f slope reproducibility | LOW | OPEN |
| Q-I001 | infotheory | Compression pattern tests calibration | HIGH | OPEN |
| Q-I002 | compsci | Summation-order effect on pipeline metrics | HIGH | OPEN |
| Q-I003 | compsci | Causality estimator calibration | MEDIUM | OPEN |
| Q-I004 | compsci | PRNG statistical battery (lab RNG cert) | HIGH | ANSWERED_LOCALLY |
| Q-C001 | computational science / neuroscience | Can a preregistered, theory-collapsed indicator battery bound phenomenal-consciousness credence for AI systems, and does it pass known-answer calibration? | HIGH (instrument) | INVESTIGATING (EXP-C001 instrument built, 6/6 anchors; EXP-C003 robustness: ordering robust, absolutes not; 48 tests, CI green, PUBLISHED to github.com/Nortaq-PlayNexus/consciousness-indicator-battery; Zenodo DOI pending user upload; no system scored; F01 circularity OPEN; F08-F11 fixed) |

---

## Next batch — derived from 2026-09-18 results (Q6/Q6f/Q7/Q8/Q9)

Full specs: `02_CANDIDATE_PROBLEMS/NEXT_BATCH_20260919.md`

| ID | Field | Question | Feasibility | Status |
|---|---|---|---|---|
| Q-P006 | physics | 2D percolation exponent precision (L=512–2048) | MEDIUM | CLOSED_INVALID (historical claim not accepted; tau/raw-tail provenance defective) |
| Q-P007 | physics | Lattice-artifact diagnostic (all geometric measures) | MEDIUM | REOPENED_FOR_REPAIR (N-001 infrastructure repaired; production tau/refined-p_c unresolved) |
| Q-P008 | physics | 3D percolation critical exponents | HIGH | INCONCLUSIVE_REPAIRED_INFRASTRUCTURE (historical 3D p_c/C7 invalid; corrected smoke only) |
| Q-S9-4 | perception | Cone-mosaic aliasing sober check | MEDIUM | PLANNED (prereg draft ready at cone_mosaic_aliasing/CONFIG/) |
| Q-M008 | math | Scaling test: prime gap deviation at 10^9/10^10 | HIGH | DESCRIPTIVE_ONLY (corrected 1e8 audit; no valid scale-persistence run) |
| Q-M007 | mathematics | Prime gap per-bin residual analysis | HIGH | DESCRIPTIVE_ONLY (historical p-values/BH invalid; first bin structurally empty) |
| Q-M008 | mathematics | Prime gap scaling (10^9, 10^10) | MEDIUM | DESCRIPTIVE_ONLY_NO_SCALE_PERSISTENCE |
| Q-S9-1 | perception | Minimum spectral structure for pareidolia | MEDIUM | OPEN |
| Q-S9-2 | perception | REBUS dose-response curve | MEDIUM | OPEN |
| Q-S9-3 | perception | Detector de-biasing (immune to pareidolia) | MEDIUM | OPEN |
| Q-S9-4 | perception | Cone-mosaic aliasing sober check (simulate) | MEDIUM | OPEN |
| Q-X1 | methods | Automated surrogate-null control generation | MEDIUM | OPEN |
| Q-X2 | methods | Continuous coherence-perception response curve | MEDIUM | OPEN |

---

Generated 2026-09-19 from Q6/Q6f/Q7/Q8/Q9 results.

Statuses: OPEN / INVESTIGATING / PARTIALLY_ANSWERED / ANSWERED_LOCALLY /
CLOSED_LITERATURE / WITHDRAWN.