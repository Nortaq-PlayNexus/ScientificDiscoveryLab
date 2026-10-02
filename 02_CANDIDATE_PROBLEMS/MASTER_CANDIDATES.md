# MASTER_CANDIDATES

Master registry of candidate scientific questions. Every entry targets a question
that is (as far as this list was built) genuinely open, computationally attackable
on this machine, falsifiable, and able to produce quantitative predictions.

Feasibility groupings (separate files):
- `HIGH_PRIORITY/` — feasible with current hardware/tools quickly
- `MEDIUM_PRIORITY/` — feasible with more effort or modest data
- `LONG_SHOTS/` — significant barriers (data, compute, or method)

Feasibility is about HOW EASY THE CONTROLLED TEST IS, never about scientific worth.
Priority ranking must not be confused with importance.

NOTE: these are CANDIDATES, not claims. Status of every entry below = UNTESTED.

---

## MATHEMATICS

### M1. Generalized Collatz-type maps — stopping-time statistics

- QUESTION_ID: Q-M001
- FIELD: mathematics
- QUESTION: Do generalized Collatz-like maps (n -> n/a if n % a==0 else n*b+c) show
  universal statistical structure in stopping times / cycle counts across parameter
  families?
- WHAT SCIENTISTS ALREADY KNOW: Classic Collatz (3n+1) unproven; "stopping time"
  statistics compiled empirically (see Lagarias). Total stopping time distribution
  has regularities; binary-tree structure (Collatz graph) has known structure.
- WHAT REMAINS UNKNOWN: Whether the observed statistical regularities extend to the
  full (a,b) family; which regularities are provably robust vs accidental.
- CURRENT THEORIES: Heuristic/probabilistic models (Wagon; relative logarithmic
  density). No complete theory.
- KNOWN METHODS: Direct simulation of orbits; log-scale tree traversal; probabilistic
  heuristic models; PARI/GP community results.
- AVAILABLE DATA: None needed — computed.
- COMPUTATIONAL REQUIREMENTS: Trivial-moderate; pure integer arithmetic.
- POSSIBLE EXPERIMENT: Fix small (a,c), sweep b, record stopping-time distributions
  for n < N; compare against heuristic model prediction.
- NULL HYPOTHESIS: No systematic deviation from the random-walk heuristic (growth
  factor (b/a)^(fraction value/odd)) across parameter families.
- ALTERNATIVE HYPOTHESIS: Parameter families show structured families of cycles /
  stopping-time families beyond the heuristic.
- FALSIFICATION TEST: Sweep parameters; count cycles; check divergence period; if a
  predicted family of cycles fails to appear with matched seeds, null stands.
- EXPECTED DIFFICULTY: Low (compute), the mathematics is deep — risk: reinventing
  known heuristics.
- LIKELY COMPUTATIONAL COST: CPU-minutes to hours.
- KNOWN PITFALLS: Overflow; treating numerics as proof; the heuristic "matches" most
  things — need controls at short N.
- RELEVANT PAPERS: Lagarias "The 3x+1 Problem" (AMS MathWorld), Wagon (1999).
- WHY AI COULD HELP: Systematic variant sweeping + honest statistical comparison at
  scale; strong controls discipline.
- WHAT WOULD COUNT AS A REAL RESULT: A new, reproducible parameter family with
  statistically solid deviation from the heuristic, robust across N and method.

### M2. Empirical statistical structure of prime gaps

- QUESTION_ID: Q-M002
- FIELD: mathematics
- QUESTION: Do prime gaps deviate from the Conrey-Goldston-Keating / Gallagher
  Poisson-model predictions in small-to-moderate ranges in a reproducible way?
- WHAT SCIENTISTS ALREADY KNOW: Gallagher's model predicts Poisson-distributed gaps;
  conditioned on Hardy-Littlewood it becomes the GPY-heuristic. Large gaps well
  studied.
- WHAT REMAINS UNKNOWN: Whether clean finite-range signatures match the "random
  model" prediction to expected sampling error, and where conditioning matters.
- CURRENT THEORIES: Poisson random model; lcm-conditioned models.
- KNOWN METHODS: Direct sieves; gap histograms; moment matching.
- AVAILABLE DATA: Computed primes via simple sieving.
- COMPUTATIONAL REQUIREMENTS: CPU, moderate (sieve to 1e7/1e8 comfortable).
- POSSIBLE EXPERIMENT: Gap histogram vs Poisson (gamma) prediction, with
  bootstrap confidence bands per range.
- NULL HYPOTHESIS: Gap distribution is consistent with the random-Poisson model in
  the tested range.
- ALTERNATIVE HYPOTHESIS: Reproducible systematic deviation not explained by
  conditioning on residue classes.
- FALSIFICATION TEST: Deviation must survive bootstrap bands across disjoint ranges.
- EXPECTED DIFFICULTY: Low (compute); novelty unlikely (this is classically studied).
- LIKELY COMPUTATIONAL COST: CPU-minutes.
- KNOWN PITFALLS: Correlation between nearby gaps; range effects; known small-prime
  correlations mistaken for signal.
- RELEVANT PAPERS: Gallagher (1976); Conrey, Goldston, Keating (2023-ish).
- WHY AI COULD HELP: Good hygiene: pre-registering windows, bootstrap, FDR.
- WHAT WOULD COUNT AS A REAL RESULT: Deviation that persists after residue-class
  conditioning across multiple independent ranges.

### M3. Normalcy statistics of constants — digit correlations in bases

- QUESTION_ID: Q-M003
- FIELD: mathematics
- QUESTION: Do the first N digits of pi/e/sqrt(2) show any empirically detectable
  cross-base or positional correlation, within what the literature's 10^13-digit
  and beyond analyses already bound?
- WHAT SCIENTISTS ALREADY KNOW: pi/e normalcy unknown for most: digit counts pass
  standard tests to enormous N (Yee & Kondo 10^13 digits; block statistics).
- WHAT REMAINS UNKNOWN: Whether any low-weight correlation exists at any finite
  scale (probably not).
- CURRENT THEORIES: Strong suspicion of normalcy but unproved.
- KNOWN METHODS: Digit extraction (Bailey-Borwein-Plouffe), block-count statistics.
- AVAILABLE DATA: Precomputed pi digits exist publicly; otherwise spigot code.
- COMPUTATIONAL REQUIREMENTS: Moderate (need digit stream).
- POSSIBLE EXPERIMENT: Autocorrelation of digit blocks; base-2..16 cross checks vs
  analytic expected counts with exact binomial bands.
- NULL HYPOTHESIS: No deviation beyond binomial sampling noise.
- ALTERNATIVE HYPOTHESIS: Reproducible bias.
- FALSIFICATION TEST: FDR across many block sizes/bases.
- EXPECTED DIFFICULTY: Very low compute; near-certain null (good educational run,
  unlikely real discovery).
- LIKELY COMPUTATIONAL COST: CPU-hours at most.
- KNOWN PITFALLS: Treating a p=0.01 among 1000 tests as discovery.
- RELEVANT PAPERS: BBP (1997); Yee & Kondo (2010).
- WHY AI COULD HELP: FDR-disciplined scanning.
- WHAT WOULD COUNT AS A REAL RESULT: A deviation surviving FDR across all tested
  scales — essentially would need to be huge.

### M4. Critical exponents in small Abelian sandpile models

- QUESTION_ID: Q-M004
- FIELD: mathematics / computational science
- QUESTION: On the Abelian sandpile model, do finite-size scaling exponents show
  clean universality across grid geometries and boundary types at accessible sizes?
- WHAT SCIENTISTS ALREADY KNOW: Exact exponents known in 1D; mean-field 2D results;
  2D exact exponents remain active; height correlations / avalanches well simulated.
- WHAT REMAINS UNKNOWN: Precise universal scaling in 2D on square vs other lattices
  at moderate sizes; robust exponent estimates.
- CURRENT THEORIES: Conformal-field-theory-inspired universality classes.
- KNOWN METHODS: Exact sampling, moment scaling, collapse.
- AVAILABLE DATA: None needed.
- COMPUTATIONAL REQUIREMENTS: CPU minimal-to-moderate (sizes ~10^3 manageable).
- POSSIBLE EXPERIMENT: Avalanche size/duration distributions on L=32..512 for square,
  hexagonal, triangular; estimate exponents with bootstrap.
- NULL HYPOTHESIS: Observed exponent() becomes size-independent at quotes; equal to
  leading theoretical estimates within CI.
- ALTERNATIVE HYPOTHESIS: Lattice-dependent effective exponents persist at these L.
- FALSIFICATION TEST: Bootstrap CIs of exponents across L ranges; lattice comparison.
- EXPECTED DIFFICULTY: Low-moderate (standard physics territory — likely redoes known
  numerics; fine as a reproducibility verification project).
- LIKELY COMPUTATIONAL COST: CPU-hours.
- KNOWN PITFALLS: Avalanche sampling near criticality is slow; boundary dependence.
- RELEVANT PAPERS: Bak et al. (1987); Dhar (1999) review.
- WHY AI COULD HELP: Systematic grid of parameter sweeps + honest scale-collapse.
- WHAT WOULD COUNT AS A REAL RESULT: A clean quantitative exponent with tight CI
  that disagrees with published effective exponents — reproduction is the realistic win.

### M5. Feigenbaum universality in higher-order 1D maps

- QUESTION_ID: Q-M005
- FIELD: mathematics / physics
- QUESTION: Do higher-derivative 1D maps (e.g., z = f(z) with local extrema of order
  2, 3, 4) show Feigenbaum-like universal constants with clean convergence of
  delta/alpha estimates?
- WHAT SCIENTISTS ALREADY KNOW: For order-2 extrema delta~4.669; order-n extrema
  universality well studied (Feigenbaum; Hu & Mao) — delta depends on order but
  bifurcation convergence is universal within a class.
- WHAT REMAINS UNKNOWN: Precise delta for each local extremum order with tight
  numerics; convergence-rate subtleties at higher order.
- CURRENT THEORIES: Renormalization-group explanation.
- KNOWN METHODS: Superstable-cycle search, logarithmic convergence.
- AVAILABLE DATA: None.
- COMPUTATIONAL REQUIREMENTS: CPU, low.
- POSSIBLE EXPERIMENT: Compute delta_n -> delta infinity for maps f_c(x), repeat for
  extremum order 2,3,4; compare to published sequences.
- NULL HYPOTHESIS: Values match literature; no new structure.
- ALTERNATIVE HYPOTHESIS: Unexpected convergence anomaly.
- FALSIFICATION TEST: Increase rate of convergence iteration; epsilon sweep.
- EXPECTED DIFFICULTY: Low (mostly reproduction/hygiene).
- LIKELY COMPUTATIONAL COST: CPU-minutes.
- KNOWN PITFALLS: Losing accuracy when extremum order raises; underestimating needed
  precision.
- RELEVANT PAPERS: Feigenbaum (1978); Hu & Mao (1982).
- WHY AI COULD HELP: Precision control and honest convergence reporting.
- WHAT WOULD COUNT AS A REAL RESULT: A reproducible deviation from published
  constants with error bars — again reproduction is the realistic win.

### M6. Random walks — first-passage universality in correlated walks

- QUESTION_ID: Q-M006
- FIELD: mathematics / computational_science
- QUESTION: In 1D/2D walks with controlled memory (Markovian vs non-Markovian),
  do first-passage time distributions follow universal scaling away from the
  independent-step limit?
- WHAT SCIENTISTS ALREADY KNOW: Sparre Andersen theorem (1D, any step distribution);
  persistence in correlated walks studied (Majumdar).
- WHAT REMAINS UNKNOWN: Mixed regimes and finite-time corrections in computable
  parameter space.
- CURRENT THEORIES: Universal exponents for stationary processes.
- KNOWN METHODS: Exact numerics + analytic asymptotics.
- AVAILABLE DATA: None.
- COMPUTATIONAL REQUIREMENTS: CPU-moderate.
- POSSIBLE EXPERIMENT: Measure first-return exponent for AR(1)-style increments at
  varying memory; compare to 0.5 (1D) universality.
- NULL HYPOTHESIS: Exponent stays 1/2 for all stationary increment processes.
- ALTERNATIVE HYPOTHESIS: Reproducible deviations for specific families.
- FALSIFICATION TEST: Multiple process families, multiple sizes.
- EXPECTED DIFFICULTY: Low-moderate.
- LIKELY COMPUTATIONAL COST: CPU-hours.
- KNOWN PITFALLS: Finite-size correction sensitivity; short-times bias.
- RELEVANT PAPERS: Majumdar lectures; Sparre Andersen (1954).
- WHY AI COULD HELP: Systematic family sweep + robust exponent fitting.
- WHAT WOULD COUNT AS A REAL RESULT: Robust published-value reproduction or a
  well-controlled deviation.

---

## OPTICS

### O1. Speckle contrast vs number of illuminated modes (statistical optics validation)

- QUESTION_ID: Q-O001
- FIELD: optics
- QUESTION: For simulated fully-developed speckle, does contrast = 1/sqrt(M)
  (M = number of independent speckle patterns summed) hold quantitatively, and at
  what M do residual correlations break it?
- WHAT SCIENTISTS ALREADY KNOW: Goodman: contrast = 1 for fully-developed single
  speckle; M-fold (intensity) averaging gives 1/sqrt(M), with cross-correlation limits.
- WHAT REMAINS UNKNOWN: Clean quantified breakdown regimes in finite-aperture,
  finite-resolution simulations (grid + interpolation aliasing).
- CURRENT THEORIES: fully-developed speckle ensemble statistics are textbook.
- KNOWN METHODS: Monte Carlo random phase screen; intensity average over ensemble.
- AVAILABLE DATA: None needed.
- COMPUTATIONAL REQUIREMENTS: CPU/GPU low-to-moderate; vectorized.
- POSSIBLE EXPERIMENT: Generate N realisations, compute contrast distribution vs M;
  compare with 1/sqrt(M) ± CI; vary grid size.
- NULL HYPOTHESIS: contrast == 1/sqrt(M) within Monte Carlo error for all tested M.
- ALTERNATIVE HYPOTHESIS: Systematic overshoot at low M / resolution-induced bend.
- FALSIFICATION TEST: Seed/realisation sweeps; resolution ladder.
- EXPECTED DIFFICULTY: Low; strongly recommended first optics project (validates the
  sandbox engine + lab method simultaneously).
- LIKELY COMPUTATIONAL COST: CPU-minutes.
- KNOWN PITFALLS: Treating numerical correlation between neighbour pixels as physics;
  undersampling the phase screen.
- RELEVANT PAPERS: Goodman "Statistical Optics" (1985/2015).
- WHY AI COULD HELP: Automate realisation sweeps + report honest CIs.
- WHAT WOULD COUNT AS A REAL RESULT: Reproduction of the textbook law with
  quantified breakdown — "real" as a validated measurement, not a novelty.

### O2. Vortex statistics in random complex fields

- QUESTION_ID: Q-O002
- FIELD: optics / physics
- QUESTION: For zero-mean Gaussian complex random fields, does the number density of
  phase singularities (vortices) match the Nye-Berry / Freund prediction, and how
  does it respond to power-spectrum shaping (matched-spectrum surrogates)?
- WHAT SCIENTISTS ALREADY KNOW: Nye-Berry (1974): dislocation density ~
  (1/lambda) style scaling; Freund: dislocation density 4 pi / (sq 3) * eta^2 ...
  exact prefactors matter. Vortices form antipodal sign pairs and annihilate.
- WHAT REMAINS UNKNOWN: In finite discrete fields, grid/edge effects bias density
  estimates; the lab's sandbox already met exactly this trap (counts ~ grid-locked).
- CURRENT THEORIES: Topological charge neutrality; density laws in terms of
  correlation length.
- KNOWN METHODS: Winding-number counting on discrete grids; gradient estimator.
- AVAILABLE DATA: Computed.
- COMPUTATIONAL REQUIREMENTS: CPU low.
- POSSIBLE EXPERIMENT: Generate Gaussian fields with controlled correlation length;
  count vortices inside interior ROI; compare to analytic density vs correlation
  length; matched-spectrum control.
- NULL HYPOTHESIS: Density matches theory within grid-sampling correction.
- ALTERNATIVE HYPOTHESIS: Systematic mismatch that tracks grid/resolution (artifact).
- FALSIFICATION TEST: ROI padding; resolution ladder; surrogate control.
- EXPECTED DIFFICULTY: Low-moderate; directly builds on sandbox assets (the lab
  already knows its winding counter can be grid-locked).
- LIKELY COMPUTATIONAL COST: CPU-minutes.
- KNOWN PITFALLS: Grid-locked winding counter (sandbox precedent); boundary vortex
  creation; interpolation creating spurious phase sign flips.
- RELEVANT PAPERS: Nye & Berry (1974); Freund (1998); Berry (2007).
- WHY AI COULD HELP: Build on hard-won sandbox lessons; enforce ROI/boundary rules.
- WHAT WOULD COUNT AS A REAL RESULT: Quantitative match to Nye-Berry/Freund with
  bias corrected — or an honest quantification of grid artifacts.

### O3. Propagation invariance under discretization (beam "shape invariance" audit)

- QUESTION_ID: Q-O003
- FIELD: optics / computational_science
- QUESTION: Which families of coherent beams retain shape statistics under repeated
  numerical propagation, and how much "sameness" is a discretization artifact?
  (Continuation of the sandbox's closed "propagation-generates-order" question —
  now with pre-registered surrogates.)
- WHAT SCIENTISTS ALREADY KNOW: Bessel beams, LG modes, structured fields have known
  propagation properties. Numerically, ASM/Fresnel conserve energy but sampling and
  windowing change details; Talbot self-images known.
- WHAT REMAINS UNKNOWN: (a) honest, fully controlled quantitative statements about
  what is preserved under finite grids; (b) whether any "statistical invariant"
  beyond known physics survives matched-spectrum nulls.
- CURRENT THEORIES: All known effects are textbook (see sandbox audit).
- KNOWN METHODS: ASM propagation + surrogate-null discipline (sandbox precedent).
- AVAILABLE DATA: None.
- COMPUTATIONAL REQUIREMENTS: CPU/GPU (FFT based); moderate for grids <= 1024^2.
- POSSIBLE EXPERIMENT: Pre-registered: propagate candidate fields; measure intensity
  statistics vs null (matched-spectrum random) fields at every z plane; single-plane
  hypotheses only, declared before seeing data.
- NULL HYPOTHESIS: No statistical signature exceeds matched-spectrum null after
  FDR/control corrections at any plane.
- ALTERNATIVE HYPOTHESIS: An effect survives every control including independent
  implementation.
- FALSIFICATION TEST: D01/D02 surrogate nulls at every plane (seeds set, BH-FDR),
  resolution ladder, boundary padding.
- EXPECTED DIFFICULTY: Medium; THIS is the disciplined continuation of sandbox
  work — the realistic outcome is likely "null" or "known effect", which is the
  correct answer.
- LIKELY COMPUTATIONAL COST: GPU-hours.
- KNOWN PITFALLS: Detectors that count features on grids; unit-coincidences; viewing
  aliasing as physics. All documented in the sandbox audit.
- RELEVANT PAPERS: Goodman; silva/talbot references in sandbox literature files.
- WHY AI COULD HELP: The previous audit showed AI discipline is the strongest asset
  (it killed the preceding claim).
- WHAT WOULD COUNT AS A REAL RESULT: An effect that survives ALL controls including
  an independent implementation — then flag for literature + human review. Empty
  result is the likely honest outcome.

### O4. Information capacity of simulated coherent speckle patterns vs detectors

- QUESTION_ID: Q-O004
- FIELD: optics / information_theory
- QUESTION: How much Shannon/Hamming information survives in a speckle pattern from
  a structured input (e.g., a phase-mask letter) as a function of mask size, noise,
  and detector resolution? (Directly tests "code in the light" claims.)
- WHAT SCIENTISTS ALREADY KNOW: Information in coherent speckle for imaging is well
  studied (multiple-scattering; memory effect); single-frame speckle has limited
  degrees of freedom ~ aperture/speckle ratio.
- WHAT REMAINS UNKNOWN: Clean quantitative "max information a real detector can
  decode" boundaries for the DMT-laser type claims — the lab's dossier flagged this
  as decisively absent.
- CURRENT THEORIES: Speckle DOF counting (Goodman; collective speckle modes).
- KNOWN METHODS: Mutual-information estimators; decoding with correlation filters.
- AVAILABLE DATA: Synthetic.
- COMPUTATIONAL REQUIREMENTS: CPU-moderate.
- POSSIBLE EXPERIMENT: Embed known symbols in phase masks; propagate; simulate
  detector (with noise); decode via correlation; measure success vs symbol set size,
  speckle size, noise level.
- NULL HYPOTHESIS: Maximum decodable bits match physical speckle-DFT counting.
- ALTERNATIVE HYPOTHESIS: Structured input produces more decodable structure than
  speckle DOF counting permits (would be extraordinary).
- FALSIFICATION TEST: Add noise; change symbol sets; shuffled-symbol control.
- EXPECTED DIFFICULTY: Medium.
- LIKELY COMPUTATIONAL COST: CPU-hours.
- KNOWN PITFALLS: Fitting classifier to specific symbols (overfit); confusing
  decoding training set memorisation with information transfer.
- RELEVANT PAPERS: Goodman; Freund memory-effect refs; DMT dossier §4 (OVRAN).
- WHY AI COULD HELP: Runs the riskiest part (fair decoding benchmark with frozen
  holdout symbols).
- WHAT WOULD COUNT AS A REAL RESULT: A controlled numeric ceiling on decodeable
  bits — directly relevant to real claims without making them.

### O5. Static speckle power spectrum vs scattering-layer roughness statistics

- QUESTION_ID: Q-O005
- FIELD: optics / materials
- QUESTION: For simulated random-phase scattering layers with controlled roughness
  statistics (Gaussian vs exponential vs long-tail), does the far-field speckle
  power spectrum follow the layer's power spectrum in the predicted way, and do
  surrogate-null layers preserve it?
- WHAT SCIENTISTS ALREADY KNOW: Van Cittert-Zernike / first-order statistics; speckle
  spectrum from scattering-object correlation.
- WHAT REMAINS UNKNOWN: Quantified control behaviour for "matched-spectrum" synthetic
  layers — exactly aligns with the lab's surrogate discipline.
- CURRENT THEORIES: First-order statistics textbook; all predictions standard.
- KNOWN METHODS: Phase-screen propagation, power spectra.
- AVAILABLE DATA: None.
- COMPUTATIONAL REQUIREMENTS: CPU-moderate.
- POSSIBLE EXPERIMENT: Roughness statistics -> far-field spectra for several layer
  profiles with matched total energy; compare to analytic.
- NULL HYPOTHESIS: Spectrum tracks layer spectrum as predicted.
- ALTERNATIVE HYPOTHESIS: Reproducible residue beyond prediction.
- FALSIFICATION TEST: Ensemble over layer realisations; resolution/ROI ladders.
- EXPECTED DIFFICULTY: Low-moderate.
- LIKELY COMPUTATIONAL COST: CPU-hours.
- KNOWN PITFALLS: PSD estimation bias; windowing spectral leakage.
- RELEVANT PAPERS: Goodman (1985), scattering theory refs.
- WHY AI COULD HELP: Clean PSD pipeline + windowing controls.
- WHAT WOULD COUNT AS A REAL RESULT: Solid reproduction of predicted layer-to-speckle
  coupling with honest error bars.

---

## PHYSICS

### P1. Random-matrix universality in structured matrices (adjacency spectra)

- QUESTION_ID: Q-P001
- FIELD: physics / mathematics
- QUESTION: Do spectral statistics of large random graphs (Erdos-Renyi, Barabasi,
  random regular) exhibit GOE-like level repulsion beyond the Wigner semicircle,
  matching known results, with honest finite-size scaling?
- WHAT SCIENTISTS ALREADY KNOW: A lot: ER graph spectra -> semicircle (Wigner), level
  statistics near GOE in certain regimes; properties for sparse graphs debated; 1D
  localization effects.
- WHAT REMAINS UNKNOWN: Clean characterisation of sparse-regime statistics across
  average degree where Poisson-GOE transitions happen.
- CURRENT THEORIES: Random matrix + sparse-graph spectral theory = active area.
- KNOWN METHODS: Exact diagonalization (need matrix size <~ 4000 for nights).
- AVAILABLE DATA: None.
- COMPUTATIONAL REQUIREMENTS: numpy/scipy eigenvalues; moderate.
- POSSIBLE EXPERIMENT: d-regular graphs for d=2..20, n=200..4000, level-spacing
  histograms vs Poisson/GOE with unfolding; bootstrap CIs.
- NULL HYPOTHESIS: Statistics match reported transitions in literature within CI.
- ALTERNATIVE HYPOTHESIS: Reproducible deviations in an unexplored (d,n) region.
- FALSIFICATION TEST: Unfolding method; independent eigenvalue solvers; finite-size
  extrapolation.
- EXPECTED DIFFICULTY: Medium (numerics standard, novelty uncertain).
- LIKELY COMPUTATIONAL COST: CPU-hours to overnight.
- KNOWN PITFALLS: Unfolding bias; finite-size crossover misread as universal.
- RELEVANT PAPERS: Bordenave review; Erdős et al.; PhysRev E transition studies.
- WHY AI COULD HELP: Automated sweep + honest unfolding controls.
- WHAT WOULD COUNT AS A REAL RESULT: Reproducible deviation in a specific (d,n)
  region that survives finite-size check and method change.

### P2. FPUT recurrence — decay and revival in discrete lattices

- QUESTION_ID: Q-P002
- FIELD: physics / computational_science
- QUESTION: In the Fermi-Pasta-Ulam-Tsingou oscillator chain with weak nonlinearity,
  do recurrence/thermalization times follow the known 1/epsilon^2 scaling cleanly
  across system size, and what is the measured scaling of "super-recurrence"?
- WHAT SCIENTISTS ALREADY KNOW: FPUT recurrences; FPU -> KdV soliton connection;
  thermalization studies; known that small epsilon -> recurrences; epsilon^2 scaling
  seen.
- WHAT REMAINS UNKNOWN: Precise exponent across a broad epsilon/system-size grid
  with fixed conservation enforcement.
- CURRENT THEORIES: "High-frequency tail" and breather interpretations.
- KNOWN METHODS: Symplectic integrators (velocity-Verlet).
- AVAILABLE DATA: None.
- COMPUTATIONAL REQUIREMENTS: CPU-moderate.
- POSSIBLE EXPERIMENT: Chains N=16..1024, epsilon grid; measure first-recurrence and
  equipartition times.
- NULL HYPOTHESIS: Scaling exponents match published values (epsilon^-2 style)
  within CI.
- ALTERNATIVE HYPOTHESIS: Systematic deviation vs N at strong epsilon.
- FALSIFICATION TEST: Different integrators/timesteps; energy conservation check.
- EXPECTED DIFFICULTY: Medium.
- LIKELY COMPUTATIONAL COST: CPU-hours.
- KNOWN PITFALLS: Drift from non-symplectic integration; timescale ambiguity.
- RELEVANT PAPERS: FPUT (1955); Berman & Izrailev review.
- WHY AI COULD HELP: Parameter-grid hygiene + conservation reporting.
- WHAT WOULD COUNT AS A REAL RESULT: Reproducible published scalings; a new clean
  deviating region would need multiple method checks.

### P3. Quantum-inspired correlations in classical random fields (falsification/education)

- QUESTION_ID: Q-P003
- FIELD: physics / optics
- QUESTION: Can classical random fields (speckle-like) be made to produce
  intensity-correlation signatures that naively resemble "quantum" coincidence
  statistics, and how readily do surrogate controls expose that they are classical?
- WHAT SCIENTISTS ALREADY KNOW: "Quantum-like" thermal/classical correlations
  documented (Hanbury Brown-Twiss for thermal light); distinguishability vs
  entanglement criteria well established.
- WHAT REMAINS UNKNOWN: Nothing fundamental — this project is a didactic
  falsification exercise protecting against naive "entanglement-like" claims.
- CURRENT THEORIES: Cauchy-Schwarz and Glauber inequalities separate classical
  from non-classical.
- KNOWN METHODS: Intensity correlation g2, Cauchy-Schwarz violation tests.
- AVAILABLE DATA: None.
- COMPUTATIONAL REQUIREMENTS: CPU low.
- POSSIBLE EXPERIMENT: Build correlated classical fields; compute g2 and the CS
  inequality; demonstrate null and show where naive methods would be fooled.
- NULL HYPOTHESIS: All "quantum-looking" signatures are explainable classically.
- ALTERNATIVE HYPOTHESIS: (Impossible to defend here; included for discipline.)
- FALSIFICATION TEST: CS inequality; detector saturation; sampling.
- EXPECTED DIFFICULTY: Low.
- LIKELY COMPUTATIONAL COST: CPU-minutes.
- KNOWN PITFALLS: Saturation/clipping correlations; finite-sample bias upward in g2.
- RELEVANT PAPERS: Glauber (1963); HBT (1956).
- WHY AI COULD HELP: Guard-rail support — teaches the lab not to overclaim.
- WHAT WOULD COUNT AS A REAL RESULT: A clean demonstration + a documented naive-
  method pitfall; realistic win = education + tooling.

### P4. Percolation thresholds — finite-size scaling on small graphs

- QUESTION_ID: Q-P004
- FIELD: physics / computational_science
- QUESTION: Do bond/site percolation thresholds and exponents on gridded and random
  small graphs reproduce literature values (e.g., square lattice pc=0.5) with honest
  finite-size extrapolation at modest sizes (L<=1024)?
- WHAT SCIENTISTS ALREADY KNOW: Exact thresholds for several lattices; well studied.
- WHAT REMAINS UNKNOWN: Only effective exponents at moderate size and lattice
  variants — mostly known.
- CURRENT THEORIES: Conformal invariance, universality.
- KNOWN METHODS: Union-find flooding, cluster counting.
- AVAILABLE DATA: None.
- COMPUTATIONAL REQUIREMENTS: CPU-light.
- POSSIBLE EXPERIMENT: pc estimators (wrapping probability crossings) vs L for
  square, triangular, honeycomb.
- NULL HYPOTHESIS: Extrapolated pc matches exact values within CI.
- ALTERNATIVE HYPOTHESIS: Not anticipated; again a hygiene project.
- FALSIFICATION TEST: Multiple crossing estimators; periodic vs open BC.
- EXPECTED DIFFICULTY: Low.
- LIKELY COMPUTATIONAL COST: CPU-minutes.
- KNOWN PITFALLS: Wrapping probability bias; small L mis-extrapolation.
- RELEVANT PAPERS: Stauffer-Aharony book; Ziff (1992).
- WHY AI COULD HELP: Clean crossing-method pipelines.
- WHAT WOULD COUNT AS A REAL RESULT: Reproduction of known thresholds; low novelty.

---

## FLUID DYNAMICS

### F1. 2D turbulence inverse cascade decay (forced dissipative)

- QUESTION_ID: Q-F001
- FIELD: fluid_dynamics / computational_science
- QUESTION: Does a GPU-accelerated 2D forced turbulence simulation with
  hyperviscosity show the predicted k^-5/3 forward / k^-3 inverse spectrum regimes
  with clean statistical convergence at achievable resolutions (512^2..2048^2)?
- WHAT SCIENTISTS ALREADY KNOW: Kraichnan-Batchelor dual cascade; k^-5/3 and k^-3
  (with log corrections debated); numerics sensitive to forcing/viscosity ratio.
- WHAT REMAINS UNKNOWN: Nothing major; but a clean reproducible spectral survey on
  this hardware with error bars is a solid engineering win and a platform builder.
- CURRENT THEORIES: Dual-cascade phenomenology.
- KNOWN METHODS: Pseudospectral (FFT) with de-aliasing; Arakawa or vorticity-stream
  formulation.
- AVAILABLE DATA: None.
- COMPUTATIONAL REQUIREMENTS: GPU (torch CPU-only -> moderate CPU grids, or wait for
  CUDA torch). Cap sizes by time budget.
- POSSIBLE EXPERIMENT: Fixed forcing band; measure energy/inverse and enstrophy
  spectra; Reynolds sweep.
- NULL HYPOTHESIS: Measured exponents match k^-5/3 / k^-3 expectation (pdf of fit
  exponent with CIs).
- ALTERNATIVE HYPOTHESIS: Deviation that survives resolution/convergence controls.
- FALSIFICATION TEST: Resolution ladder (512,1024,2048); dealiasing ON/OFF;
  dissipation scaling; multiple forcing realisations.
- EXPECTED DIFFICULTY: High (numerics first, physics second). Long shot on CPU.
- LIKELY COMPUTATIONAL COST: CPU-days unless a GPU-accelerated numpy/torch path is
  available (torch is CPU-only here) — realistic ceiling: 512^2 reliable, 1024^2
  slow.
- KNOWN PITFALLS: Dealising (3/2 rule) mistakes; insufficient inertial range;
  confusing stirring-scale with inertial-range effects.
- RELEVANT PAPERS: Kraichnan (1967); Boffetta & Ecke review (2012).
- WHY AI COULD HELP: Offer a rigorous forcing/viscosity tuning loop with
  convergence checks.
- WHAT WOULD COUNT AS A REAL RESULT: Clean reproducible dual-cascade spectra with
  quantified error; not a discovery claim; still a genuinely useful measurement.

### F2. Von Kármán vortex street shedding frequency vs Reynolds number

- QUESTION_ID: Q-F002
- FIELD: fluid_dynamics
- QUESTION: In 2D flow past a cylinder, does the Strouhal-Reynolds relationship
  (St ~ 0.2 with known curve) reproduce with a simple GPU/CPU lattice-Boltzmann or
  finite-difference solver, and what are the honest accuracy limits on this
  hardware?
- WHAT SCIENTISTS ALREADY KNOW: The St-Re curve is empirical and well mapped.
- WHAT REMAINS UNKNOWN: Solver-specific accuracy vs architecture for hobby hardware —
  a solver benchmark project.
- CURRENT THEORIES: Empirical St-Re correlation.
- KNOWN METHODS: Lattice Boltzmann, immersed boundary, pseudo-spectral DNS.
- AVAILABLE DATA: None.
- COMPUTATIONAL REQUIREMENTS: CPU-moderate at coarse grids (256^2-ish).
- POSSIBLE EXPERIMENT: Parameter sweep Re 50..200; St from lift oscillation; compare
  to published curve.
- NULL HYPOTHESIS: St within CI bands of published mapping.
- ALTERNATIVE HYPOTHESIS: Systematic solver bias to quantify.
- FALSIFICATION TEST: Grid refinement; domain-size checks; two different discretisations.
- EXPECTED DIFFICULTY: High for a clean box.
- LIKELY COMPUTATIONAL COST: CPU-days at quadratic grids.
- KNOWN PITFALLS: Blockage ratio; insufficient wake length; num diffusivity.
- RELEVANT PAPERS: Roshko (1954); Williamson (1996) review.
- WHY AI COULD HELP: Systematic Re sweep + grid-convergence bookkeeping.
- WHAT WOULD COUNT AS A REAL RESULT: A published-curve reproduction within stated
  limits, plus honest accuracy map.

### F3. 1D Burgers equation shock statistics with random forcing

- QUESTION_ID: Q-F003
- FIELD: fluid_dynamics / mathematics
- QUESTION: In forced 1D Burgers turbulence, do shock structures and the
  multifractal energy exponent reproduce known results, and how does shock counting
  respond to numerical scheme (conservative vs upwind)?
- WHAT SCIENTISTS ALREADY KNOW: Burgers statistics known analytically in several
  regimes (Bec & Frisch review); multifractal spectrum computed.
- WHAT REMAINS UNKNOWN: Mostly known; residual: scheme-dependent small-scale
  statistics — a natural controls project.
- CURRENT THEORIES: Shock statistics via instantons; Burgers = the exact solvable
  model.
- KNOWN METHODS: High-res conservative schemes, spectral with viscosity.
- AVAILABLE DATA: None.
- COMPUTATIONAL REQUIREMENTS: CPU-moderate (1D).
- POSSIBLE EXPERIMENT: Number/strength of shocks vs forcing amplitude; scheme A vs B
  comparison.
- NULL HYPOTHESIS: PDF exponents match analytic for dissipative range.
- ALTERNATIVE HYPOTHESIS: Scheme-dependent artefacts distinguishable from physics.
- FALSIFICATION TEST: Two schemes, resolution ladder, machine-precision forcing,
  different seed sets.
- EXPECTED DIFFICULTY: Medium.
- LIKELY COMPUTATIONAL COST: CPU-hours.
- KNOWN PITFALLS: Numerical viscosity dominating; wrong shock-capturing.
- RELEVANT PAPERS: Bec & Frisch (2003) review.
- WHY AI COULD HELP: Clean scheme-comparison bookkeeping.
- WHAT WOULD COUNT AS A REAL RESULT: Quantified scheme-dependence — a useful
  numerical-science measurement.

---

## ASTRONOMY / COSMOLOGY

### A1. Public exoplanet transit detection from archival light curves

- QUESTION_ID: Q-A001
- FIELD: astronomy
- QUESTION: Can archivally available photometric light curves (public TESS/K2-like)
  yield clean, independently re-detected exoplanet transits using a simple folded-box
  search, and what is the honest detection limit?
- WHAT SCIENTISTS ALREADY KNOW: Planet catalogs exist; transit methods standard.
- WHAT REMAINS UNKNOWN: For us: whether usable public files are reliably
  downloadable + processable on this machine.
- CURRENT THEORIES: N/A (methodology project).
- KNOWN METHODS: Box-least-squares (BLS) search, phase folding.
- AVAILABLE DATA: Public archives (Mast, ExoFOP); requires internet and download
  management — flag as external dependency.
- COMPUTATIONAL REQUIREMENTS: CPU-moderate per star; archive big => curation needed.
- POSSIBLE EXPERIMENT: Download a small vetted set; re-detect known planets; measure
  SNR for detection; maybe search a small untargeted sample.
- NULL HYPOTHESIS: We only recover known signals (no novel candidates).
- ALTERNATIVE HYPOTHESIS: A genuinely new candidate transit in a small unbiased
  sample (rare; needs backend confirmation; not publishable alone).
- FALSIFICATION TEST: Fake-inject-recover tests; artifact checks (systematics).
- EXPECTED DIFFICULTY: Medium (data access is the real hurdle).
- LIKELY COMPUTATIONAL COST: CPU-hours.
- KNOWN PITFALLS: Systematics masquerading as transits; in-sample catalogs
  contaminating "new" claims.
- RELEVANT PAPERS: BLS (Kovács et al. 2002); TESS papers.
- WHY AI COULD HELP: Reproducible pipeline + fake-injection honesty.
- WHAT WOULD COUNT AS A REAL RESULT: Reproduced known detections + quantified
  recoverability curve. Novel candidate would need external vetting.

### A2. Catalogue cross-checks — magnitude/colour/systematics reproducibility

- QUESTION_ID: Q-A002
- FIELD: astronomy
- QUESTION: In public star catalogues (e.g., GAIA DR3 photometry), do colour-colour
  and period-luminosity relationships reproduce published scatter with the reported
  selection cuts on a random subsample?
- WHAT SCIENTISTS ALREADY KNOW: Calibrations are survey-maintained.
- WHAT REMAINS UNKNOWN: Reproducing them independently (short-run hygiene project,
  also exercises external-data pipeline).
- CURRENT THEORIES: N/A.
- KNOWN METHODS: Selection cuts, robust fits.
- AVAILABLE DATA: GAIA public (large; subsample).
- COMPUTATIONAL REQUIREMENTS: Low-moderate (subsample).
- POSSIBLE EXPERIMENT: Take a public subsample; fit P-L; compare slope/intercept
  CIs with published.
- NULL HYPOTHESIS: Match within CI.
- ALTERNATIVE HYPOTHESIS: Systematic flux/stellar-type offset.
- FALSIFICATION TEST: Different subsampling, cuts, estimators.
- EXPECTED DIFFICULTY: Low-moderate.
- LIKELY COMPUTATIONAL COST: CPU-minutes-hours.
- KNOWN PITFALLS: Selection bias; contamination; magnitude calibrations.
- RELEVANT PAPERS: GAIA DR3 release papers.
- WHY AI COULD HELP: Pipeline hygiene.
- WHAT WOULD COUNT AS A REAL RESULT: Independent reproduction of published relations.

### A3. CMB public-data anomaly reproduction (WMAP/Planck)

- QUESTION_ID: Q-A003
- FIELD: cosmology
- QUESTION: Using publicly available processed CMB maps/estimators, can the famous
  reported anomalies (hemispherical power asymmetry, cold spot) be reproduced with
  their claimed significance from the public products, and what does a control-based
  analysis add?
- WHAT SCIENTISTS ALREADY KNOW: Anomalies reported by Planck/others; significance
  debated; many papers.
- WHAT REMAINS UNKNOWN: The exercise is mostly about rigorous reproduction; the
  physical interpretation remains open/contested.
- CURRENT THEORIES: Possible systematics vs cosmological explanations.
- KNOWN METHODS: Spherical harmonic power estimation, needlets, etc.
- AVAILABLE DATA: Planck/HEALPix public maps (large files; HEALPix needs install).
- COMPUTATIONAL REQUIREMENTS: Needs healpy/healpy install (not present) + large
  downloads. Flag as long-shot on data infra until confirmed.
- POSSIBLE EXPERIMENT: Download cut-sky maps; compute power asymmetry statistics
  with (many) simulations; compare with published p-values.
- NULL HYPOTHESIS: Anomalies reproduce at published significance OR are null under
  control simulations — either honest outcome is valuable.
- ALTERNATIVE HYPOTHESIS: (none to defend here).
- FALSIFICATION TEST: Simulation-based significance; mask/cut variations.
- EXPECTED DIFFICULTY: High (data + spherical tooling).
- LIKELY COMPUTATIONAL COST: Downloads + CPU-hours; machine can do it but setup is real.
- KNOWN PITFALLS: Cutting sky needs careful masks; pipeline-specific estimates.
- RELEVANT PAPERS: Planck Papers XXIII/XXIV; CDS anomaly reviews.
- WHY AI COULD HELP: Strict simulation-based significance bookkeeping is core.
- WHAT WOULD COUNT AS A REAL RESULT: Honest reproduction table (whose p-values
  survive controls) — a strong methodological service, not a cosmology discovery.

### A4. Meteor/event data: statistical clustering checks on public fireball catalogs

- QUESTION_ID: Q-A004
- FIELD: astronomy / earth_science
- QUESTION: In public meteor/fireball observational catalogs, are there seasonal or
  spatial clusters that exceed Poisson nulls (accounting for observability biases)?
- WHAT SCIENTISTS ALREADY KNOW: Meteor showers are known/periodic; biases dominate.
- WHAT REMAINS UNKNOWN: Whether any residual clustering survives bias models.
- CURRENT THEORIES: Shower activity; sporadic background.
- KNOWN METHODS: Poisson/scan statistics, bias weighting.
- AVAILABLE DATA: Public fireball networks (AMS, CAMS) — availability must be checked.
- COMPUTATIONAL REQUIREMENTS: Low.
- POSSIBLE EXPERIMENT: Scan statistics vs nulls with detection-bias weights.
- NULL HYPOTHESIS: No clustering beyond showers + bias model.
- ALTERNATIVE HYPOTHESIS: Residual anomaly.
- FALSIFICATION TEST: Bias-model variation; scan window size sweeps.
- EXPECTED DIFFICULTY: Medium (data availability + bias modelling).
- LIKELY COMPUTATIONAL COST: CPU-hours.
- KNOWN PITFALLS: Observability/weather bias mimicking clusters.
- RELEVANT PAPERS: Fireball survey papers.
- WHY AI COULD HELP: Bias-aware scan-statistic discipline.
- WHAT WOULD COUNT AS A REAL RESULT: A cluster that survives bias models — then
  literature check (most likely already known shower).

---

## CLIMATE / EARTH SCIENCE

### C1. Paleoclimate reconstruction reproducibility audit (public proxies)

- QUESTION_ID: Q-C001
- FIELD: climate_science
- QUESTION: Using public paleoclimate proxy compilations, do simple calibration
  workflows reproduce published temperature reconstruction statistical behaviour
  (uncertainty envelopes), testing the public reproducibility of the methods?
- WHAT SCIENTISTS ALREADY KNOW: Reconstruction methods are debated (Mann 2008-style
  critiques); many public compilations.
- WHAT REMAINS UNKNOWN: Cleaner independent numbers on method sensitivity.
- CURRENT THEORIES: N/A.
- KNOWN METHODS: Calibration regression, PSD pairing (Mann et al. 2008).
- AVAILABLE DATA: Public compilations (PAGES etc.).
- COMPUTATIONAL REQUIREMENTS: Amino acids; needs downloads.
- POSSIBLE EXPERIMENT: Re-run a standard calibration on a public set; compare
  spectrum/amplitude stats with published.
- NULL HYPOTHESIS: Methods reproduce their own published outputs.
- ALTERNATIVE HYPOTHESIS: Sensitivity to arbitrary code choices (a methodological
  finding — often the real truth in this field).
- FALSIFICATION TEST: Hyperparameter variation; library differences.
- EXPECTED DIFFICULTY: Medium.
- LIKELY COMPUTATIONAL COST: CPU-hours.
- KNOWN PITFALLS: Cherry-picking proxy sets; misuse of "hockey stick" framing.
- RELEVANT PAPERS: Mann et al.; Ammann & Wahl; Li, Nychka, Ammann.
- WHY AI COULD HELP: Systematic sensitivity sweeps for a computationally simple
  method class.
- WHAT WOULD COUNT AS A REAL RESULT: Quantified sensitivity map of a public method —
  a solid reproducibility contribution.

### C2. Simple ENSO forecast skill (public SSTA data)

- QUESTION_ID: Q-C002
- FIELD: climate_science
- QUESTION: Can a simple autoregressive/lagged-regression model of public SST
  anomalies (Nino3.4) reproduce the published "moderate skill at several months"
  results, and what does honest out-of-sample scoring give?
- WHAT SCIENTISTS ALREADY KNOW: ENSO predictability measured (limit ~ seasons);
  simple linear models get baseline skill.
- WHAT REMAINS UNKNOWN: Reproducing the baseline on this machine with public data.
- CURRENT THEORIES: N/A.
- KNOWN METHODS: AR, linear inverse models (LIM).
- AVAILABLE DATA: Public (NOAA/CPC) time series.
- COMPUTATIONAL REQUIREMENTS: Low.
- POSSIBLE EXPERIMENT: Fit LIM/AR on training window; walk-forward test; compare
  correlations with published.
- NULL HYPOTHESIS: Skill consistent with published baseline studies.
- ALTERNATIVE HYPOTHESIS: (baseline reproduction; no big claim intended).
- FALSIFICATION TEST: Different train/test splits, decade sub-samples.
- EXPECTED DIFFICULTY: Low-medium.
- LIKELY COMPUTATIONAL COST: CPU-minutes.
- KNOWN PITFALLS: Overlapping window skill inflation; trend leakage.
- RELEVANT PAPERS: Penland & Magorian (1993); Chen et al.
- WHY AI COULD HELP: Clean walk-forward harness.
- WHAT WOULD COUNT AS A REAL RESULT: Repro of baseline skill numbers.

---

## MATERIALS / CHEMISTRY

### Mx1. Band-gap statistics on public stoichiometric data — descriptor reproduction

- QUESTION_ID: Q-Mx001
- FIELD: materials_science
- QUESTION: Using public OQMD/Materials-Project-style tabular summaries, do simple
  composition descriptors reproduce published band-gap model scores, and how much of
  the "predictive power" is composition-frequency baselines?
- WHAT SCIENTISTS ALREADY KNOW: Machine-learned band-gap models with reported MAE;
  composition-only baselines weaker but surprisingly competitive.
- WHAT REMAINS UNKNOWN: Honestly re-benchmarking baseline-vs-model (short project,
  service value).
- CURRENT THEORIES: N/A.
- KNOWN METHODS: Gradient boosting on composition features.
- AVAILABLE DATA: Public aggregate tables (download required; verify terms).
- COMPUTATIONAL REQUIREMENTS: Low.
- POSSIBLE EXPERIMENT: Train simple model + naive-frequency baseline on a curated
  split; compare honest MAEs to published.
- NULL HYPOTHESIS: Model beats baseline by published amount.
- ALTERNATIVE HYPOTHESIS: "Model skill" is mostly data leakage / baseline reachable.
- FALSIFICATION TEST: Strict temporal/formula splits; leakage audit.
- EXPECTED DIFFICULTY: Medium (data curation + leakage discipline).
- LIKELY COMPUTATIONAL COST: CPU-minutes-hours.
- KNOWN PITFALLS: Duplicate materials, formula parsing bugs, leakage via similar
  compositions.
- RELEVANT PAPERS: Ward et al.; recent MatBench papers.
- WHY AI COULD HELP: Strict split + baseline audit = novelty-testing practice.
- WHAT WOULD COUNT AS A REAL RESULT: Leakage-safe re-benchmarking numbers.

---

## BIOLOGY / NEUROSCIENCE

### B1. Stochastic gene-expression circuits — bimodality regimes (Gillespie)

- QUESTION_ID: Q-B001
- FIELD: biology / computational_science
- QUESTION: For simple positive-feedback gene circuits simulated with the Gillespie
  algorithm, do the published bimodal parameter regimes reproduce exactly, and how
  do finite-time counting effects shift apparent histograms?
- WHAT SCIENTISTS ALREADY KNOW: Gurney/Ferrell positive-feedback bistability; exact
  stochastic simulation standard.
- WHAT REMAINS UNKNOWN: Rechecking known regimes is the realistic deliverable.
- CURRENT THEORIES: Deterministic bistability from nonlinear feedback.
- KNOWN METHODS: Gillespie SSA; tau-leaping.
- AVAILABLE DATA: None.
- COMPUTATIONAL REQUIREMENTS: CPU-light.
- POSSIBLE EXPERIMENT: Parameter grid; histogram modality detection; compare to ODE
  bifurcation prediction.
- NULL HYPOTHESIS: SSA histograms match deterministic regions at equilibrium.
- ALTERNATIVE HYPOTHESIS: Deep deviation near boundaries (known as finite-population
  "smearing").
- FALSIFICATION TEST: Long-runs; multiple seeds; tau-leap vs exact SSA cross-check.
- EXPECTED DIFFICULTY: Medium.
- LIKELY COMPUTATIONAL COST: CPU-hours.
- KNOWN PITFALLS: Counting statistics near switches; extinction; reaction constant
  units.
- RELEVANT PAPERS: Ferrell (2002); Gillespie (1977); Warren & ten Wolde.
- WHY AI COULD HELP: Modality classification hygiene.
- WHAT WOULD COUNT AS A REAL RESULT: Clean reproduction of known bifurcation smear
  — methodology, not biology discovery.

### B2. GC-skew / CpG statistics on public genomes — reproducibility

- QUESTION_ID: Q-B002
- FIELD: biology / information_theory
- QUESTION: On a few publicly downloadable completed bacterial genomes, do GC-skew
  and CpG-island statistical signatures reproduce published expectations, and what
  is the genuine statistical power of these tests on small sequences?
- WHAT SCIENTISTS ALREADY KNOW: GC skew associated with replication; strand bias
  known; CpG island detection methods standard.
- WHAT REMAINS UNKNOWN: Reproducibility via independent code (power/significance
  honesty).
- CURRENT THEORIES: N/A.
- KNOWN METHODS: Sliding-window skew, hidden Markov CpG islands.
- AVAILABLE DATA: Public NCBI genomes, small files.
- COMPUTATIONAL REQUIREMENTS: Low.
- POSSIBLE EXPERIMENT: Download 3-5 genomes; compute skew; bootstrap p-values;
  compare to published null behaviour.
- NULL HYPOTHESIS: Skew tests have the stated false-positive rate.
- ALTERNATIVE HYPOTHESIS: Reported strand-bias "significance" is inflated by
  autocorrelation (known trap).
- FALSIFICATION TEST: Permutation blocks; length scaling.
- EXPECTED DIFFICULTY: Low-medium.
- LIKELY COMPUTATIONAL COST: CPU-minutes.
- KNOWN PITFALLS: Autocorrelation inflating significance; window-size shopping.
- RELEVANT PAPERS: Lobry (1996); genome papers.
- WHY AI COULD HELP: Block-permutation discipline.
- WHAT WOULD COUNT AS A REAL RESULT: Quantified false-positive rates of skew tests.

### B3. Resting EEG 1/f scaling on public recordings

- QUESTION_ID: Q-B003
- FIELD: neuroscience
- QUESTION: On publicly available resting-state EEG datasets, does the power-spectrum
  1/f slope and alpha-peak structure reproduce standard published values, with
  honest accounting of pre-processing (eye blink artifacts, notch filters)?
- WHAT SCIENTISTS ALREADY KNOW: 1/f + alpha peak EEG structure well characterized.
- WHAT REMAINS UNKNOWN: Independent reproduction on this machine (dataset availability
  + size are big unknowns; preprocessing pipeline heavy).
- CURRENT THEORIES: N/A.
- KNOWN METHODS: Welch PSD, spectral slope fits (fit 1/f + oscillations).
- AVAILABLE DATA: Public EEG repositories (requires download; multi-GB).
- COMPUTATIONAL REQUIREMENTS: CPU-moderate; needs the dataset.
- POSSIBLE EXPERIMENT: Reanalyze a small subset; report slope/alpha vs published.
- NULL HYPOTHESIS: Slopes match published medians within CI.
- ALTERNATIVE HYPOTHESIS: Preprocessing sensitivity dominates (likely).
- FALSIFICATION TEST: Different preprocessing chains; artifact threshold sweeps.
- EXPECTED DIFFICULTY: High (data + preprocessing).
- LIKELY COMPUTATIONAL COST: CPU-hours + download.
- KNOWN PITFALLS: 50/60Hz notch vs 1/f bias; blink contamination; montage effects.
- RELEVANT PAPERS: Buzsaki; FOOOF paradigm (Donoghue et al. 2020).
- WHY AI COULD HELP: Systematic preprocessing sensitivity table.
- WHAT WOULD COUNT AS A REAL RESULT: Quantified sensitivity of slope estimates —
  methodological value.

---

## INFORMATION THEORY / COMPUTATIONAL SCIENCE

### I1. Compression-based pattern tests on public corpora

- QUESTION_ID: Q-I001
- FIELD: information_theory
- QUESTION: On a public, static text corpus (e.g., Project Gutenberg subset), do
  compression-ratio tests across random text permutations detect "structure"
  differences in a reproducible, statistically sound way, and how do size effects
  inflate naive conclusions?
- WHAT SCIENTISTS ALREADY KNOW: Kolmogorov-complexity surrogates (LZ) are used and
  abused; statistical issues well documented.
- WHAT REMAINS UNKNOWN: Clean power analysis of these tests as a "suspicious
  structure" screen on a fixed machine.
- CURRENT THEORIES: N/A.
- KNOWN METHODS: LZ77 ratio, gzip ratio, permutation baselines.
- AVAILABLE DATA: Public corpus.
- COMPUTATIONAL REQUIREMENTS: Low-moderate.
- POSSIBLE EXPERIMENT: Bits-per-symbol on chunks; block-shuffle nulls; effect sizes.
- NULL HYPOTHESIS: Compression differences vanish under permutation nulls.
- ALTERNATIVE HYPOTHESIS: Interpretable systematic differences (e.g., language vs
  code corpora — known).
- FALSIFICATION TEST: Multiple corpora, chunk sizes, compressors.
- EXPECTED DIFFICULTY: Low.
- LIKELY COMPUTATIONAL COST: CPU-hours.
- KNOWN PITFALLS: Overclaiming "message" from compression; concatenation artifacts.
- RELEVANT PAPERS: Lempel & Ziv; Vitanyi; Zenil practical complexity essays.
- WHY AI COULD HELP: Turn a sloppy heuristic into an honest calibrated screen.
- WHAT WOULD COUNT AS A REAL RESULT: Power/calibration table; realistic deliverable =
  reusability tooling for the lab.

### I2. Summation-order effects on emergent statistics

- QUESTION_ID: Q-I002
- FIELD: computational_science
- QUESTION: For long-running Monte Carlo pipelines, how much do floating-point
  summation order and reduction topology bias emergent statistics (means, covariances,
  peak counts), and which pipeline orders are reproducibly safe?
- WHAT SCIENTISTS ALREADY KNOW: FP error accumulation studied (Higham); Kahan/
  pairwise summation improve; but end-to-end "emergent" metric sensitivity is
  under-documented.
- WHAT REMAINS UNKNOWN: Quantified end-to-end bias for the lab's own pipelines —
  a control-technique project with real payoff.
- CURRENT THEORIES: N/A.
- KNOWN METHODS: Kahan, pairwise, NumPy reductions; changing order via permutation.
- AVAILABLE DATA: None.
- COMPUTATIONAL REQUIREMENTS: Low.
- POSSIBLE EXPERIMENT: Feed a known-construction pipeline; compare reduce orders;
  quantify worst-case drift on outputs vs analytic.
- NULL HYPOTHESIS: Drift is below declared numerical tolerance at lab scales.
- ALTERNATIVE HYPOTHESIS: A lab-scale emergent metric shows >tol sensitivity to order.
- FALSIFICATION TEST: Different summation methods; wider dtype cross-check.
- EXPECTED DIFFICULTY: Low.
- LIKELY COMPUTATIONAL COST: CPU-hours.
- KNOWN PITFALLS: Confusing deterministic-but-order-dependent with physics.
- RELEVANT PAPERS: Higham (2002); Knuth (art of programming FP).
- WHY AI COULD HELP: Codify numeric hygiene into the lab engine.
- WHAT WOULD COUNT AS A REAL RESULT: A quantitative safety map for lab pipelines.

### I3. Causality-inference benchmarking on synthetic systems

- QUESTION_ID: Q-I003
- FIELD: computational_science / information_theory
- QUESTION: On synthetic pair processes with known couplings/lags, do correlation,
  Granger, and transfer-entropy estimators recover the ground truth with what sample
  sizes and, crucially, at what false-positive rates on null systems?
- WHAT SCIENTISTS ALREADY KNOW: Transfer entropy and Granger equivalence debated;
  false positives (conditional effects) known.
- WHAT REMAINS UNKNOWN: Honest, reproducible power/false-positive maps on this
  machine for the estimators this lab might use (important given the lab's
  "clustering/causality" ambitions).
- CURRENT THEORIES: N/A.
- KNOWN METHODS: Granger (VAR), TE (KDE/estimation methods), partial correlation.
- AVAILABLE DATA: Generated.
- COMPUTATIONAL REQUIREMENTS: Low-moderate.
- POSSIBLE EXPERIMENT: Null systems (independent AR) -> FP rates across estimators;
  coupled systems -> power curves vs coupling and sample size.
- NULL HYPOTHESIS: All estimators meet their nominal FP rate.
- ALTERNATIVE HYPOTHESIS: Some poorly calibrated (likely TE under data drought).
- FALSIFICATION TEST: Independent implementations; time-reversal nulls.
- EXPECTED DIFFICULTY: Medium.
- LIKELY COMPUTATIONAL COST: CPU-hours.
- KNOWN PITFALLS: Non-stationarity; conditioning choice; estimator bandwidth luck.
- RELEVANT PAPERS: Schreiber (2000); Barnett et al. reviews.
- WHY AI COULD HELP: Annual suspicion — the lab should pre-verify any "causal"
  claim engine before using it on real correlations.
- WHAT WOULD COUNT AS A REAL RESULT: Calibration table for chosen estimators; the
  lab's own "causality is hard" reference doc.

### I4. Pseudorandom generator statistical quality (lab RNG vs std default)

- QUESTION_ID: Q-I004
- FIELD: computational_science
- QUESTION: Does the lab's sha256-seeded Generator (and NumPy default) pass standard
  statistical PRNG test batteries (e.g., NIST-style / simple empirical suites) at
  lab scales, so the lab can safely attribute anomalies to science and not RNG?
- WHAT SCIENTISTS ALREADY KNOW: PCG64/MT well tested; NIST suite standard.
- WHAT REMAINS UNKNOWN: A light-weight reproducible test bundle for this machine.
- CURRENT THEORIES: N/A.
- KNOWN METHODS: Frequency, runs, serial, chi-square, spectral.
- AVAILABLE DATA: None.
- COMPUTATIONAL REQUIREMENTS: Low.
- POSSIBLE EXPERIMENT: Feed the lab RNG into a battery; thresholds; multiple seeds.
- NULL HYPOTHESIS: Passes at borderline p-value distributions.
- ALTERNATIVE HYPOTHESIS: Failure (red flag for the whole lab).
- FALSIFICATION TEST: Longer streams; different seeds; cross-Generator comparison.
- EXPECTED DIFFICULTY: Low.
- LIKELY COMPUTATIONAL COST: CPU-minutes.
- KNOWN PITFALLS: Underpowered batteries; harvesting artefacts.
- RELEVANT PAPERS: NIST SP 800-22; Marsaglia DIEHARD.
- WHY AI COULD HELP: Baseline trust for EVERY pipeline (cheap, high value).
- WHAT WOULD COUNT AS A REAL RESULT: A green calibration certificate for the lab RNG.

---

## SUMMARY TABLE — feasibility groupings

| ID | Question | Feasibility | Main barrier |
|---|---|---|---|
| Q-M001 | Generalized Collatz statistics | HIGH | none (compute-only) |
| Q-M002 | Prime gap statistics | HIGH | none |
| Q-M003 | Constant digit normalcy | HIGH | digit stream acquisition |
| Q-M005 | Feigenbaum higher-order | HIGH | none |
| Q-M006 | First-passage universality | HIGH | none |
| Q-O001 | Speckle contrast law | HIGH | none (uses sandbox engine) |
| Q-O002 | Vortex statistics | HIGH | none (sandbox asset) |
| Q-O003 | Propagation invariance audit | HIGH/MED | nothing but discipline |
| Q-O004 | Speckle info capacity | MEDIUM | fair-decoding benchmark design |
| Q-O005 | Speckle spectrum vs roughness | MEDIUM | PSD windowing care |
| Q-P001 | RMT graph spectra | MEDIUM | diagonalization budget |
| Q-P002 | FPUT recurrence | MEDIUM | none |
| Q-P003 | Quantum-looking classical correlations | HIGH | none |
| Q-P004 | Percolation thresholds | HIGH | none |
| Q-M004 | Sandpile exponents | MEDIUM | slow near criticality |
| Q-F001 | 2D turbulence | LOW | CPU-only torch |
| Q-F002 | Cylinder shedding | LOW/MED | solver cost |
| Q-F003 | Burgers shocks | MEDIUM | none |
| Q-A001 | Exoplanet transits | MEDIUM (data) | archive download |
| Q-A002 | GAIA catalogue checks | MEDIUM (data) | large downloads |
| Q-A003 | CMB anomalies | LOW (infra) | HEALPix + big data |
| Q-A004 | Fireball clusters | MEDIUM | data availability + bias |
| Q-C001 | Paleoclimate repro audit | MEDIUM | data + methods |
| Q-C002 | ENSO skill baseline | HIGH | none (small public data) |
| Q-Mx001 | Band-gap leakage audit | MEDIUM | curation + leakage |
| Q-B001 | Gene circuit bimodality | MEDIUM | none |
| Q-B002 | GC-skew power | MEDIUM | genome download |
| Q-B003 | EEG 1/f scaling | LOW (data) | dataset size |
| Q-I001 | Compression pattern tests | HIGH | none |
| Q-I002 | Summation-order effects | HIGH | none |
| Q-I003 | Causality benchmarking | MEDIUM | none |
| Q-I004 | PRNG battery | HIGH | none |

Priority files per feasibility are generated from this table. Nothing here is a
finding; all entries UNTESTED.