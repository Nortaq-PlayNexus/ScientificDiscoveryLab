# Literature novelty matrix — EXP-0015 / EXP-0016

**Scope.** This is a targeted, not exhaustive, literature audit for discrete
optical-vortex detection bias, angular-spectrum sampling artifacts, and
continuous-versus-discrete topology. Searches were run on 2026-09-24 using
web search plus the existing sandbox literature files. “Not located” means
not located in the searched sources; it does not establish priority or novelty.

| Citation / source | Method and system | What it explains or measures | Match to EXP-0015 | What remains unresolved here |
|---|---|---|---|---|
| Nye & Berry (1974), *Dislocations in wave trains*; DOI/source cited in Berry review | Wavefront dislocations and phase singularities | Foundational continuous-wave dislocation/topology framework | Strong conceptual match; establishes that a vortex is a continuous phase winding around a zero, not any dark pixel | Does not prescribe a universal finite-grid detector or convergence law |
| Berry (1978), *Disruption of wavefronts: Statistics of dislocations in incoherent Gaussian random waves*, DOI `10.1088/0305-4470/11/1/007` | Random-wave dislocation statistics | Establishes statistical dislocation densities and fluctuations | Strong match to Null A/random-field controls | Does not test the specific DeepBeamScan-style plaquette output |
| Freund (1994), *Optical vortices in Gaussian random wave fields: Statistical probability densities*, DOI `10.1364/JOSAA.11.001644` | Gaussian random complex fields; vortex statistics | Gives optical-vortex probability-density theory | Strong match to Kac–Rice/Nye–Berry and matched-spectrum nulls | Does not resolve finite sampling and detector-specific bias |
| Berry & Dennis (2000), *Phase singularities in isotropic random waves*, DOI `10.1098/rspa.2000.0602` | Isotropic random waves | Topological singularity statistics and pair structure | Strong match to random-field structure and pair-correlation controls | Does not give a universal pixel-grid error curve |
| Arecchi et al. (1991), *Vortices and defect statistics in two-dimensional optical chaos*, DOI `10.1103/PhysRevLett.67.3749` | Optical chaos and defect statistics | Statistical birth/death and defect populations in optical fields | Moderate match; supports using pair/charge statistics rather than raw counts | Different ensemble and measurement protocol |
| Indebetouw (1993), *Optical vortices and their propagation*, DOI `10.1080/09500349314550101` | Optical vortex propagation | Establishes that free propagation can move, create, or annihilate vortex–antivortex structures | Strong match to the physical propagation control | Does not validate the historical `+1280 µm` count in this implementation |
| Roux (2013), *How to distinguish between the annihilation and creation of optical vortices?*, Optics Letters `38`, 3895, DOI `10.1364/OL.38.003895` | Optical vortex creation/annihilation diagnostics | Argues that local/topological information is needed to distinguish pair processes | Strong match to the tracker requirement | EXP-0015 performs a detector-event tracker and high-resolution control, but not a full continuous physical singularity locator |
| Eshaghi et al. (2022), *Phase memory of optical vortex beams*, DOI `10.1038/s41598-022-14074-4`, open access | Analytical model, numerical simulations, phase measurements | Quantifies how randomness/correlation length changes apparent vorticity; explicitly discusses Cartesian sampled phase and contour limitations | Very strong match to detector-resolution and contour-geometry controls | Does not study the historical 256² DBS implementation |
| Shen et al. (2019), *Optical vortices 30 years on*, DOI `10.1038/s41377-019-0194-2`, open access | Review of vortex generation, propagation, measurement | Provides continuous topological-charge definition and measurement context | Foundational context; not a numerical artifact paper | Review cannot certify a new detector-bias result |
| Lin et al. (2024), *Optical vortex-antivortex crystallization in free space*, DOI `10.1038/s41467-024-50458-y`, open access | Analytical paraxial model plus experiment | Shows real free-space VAV motion/crystallization and pair annihilation/creation for suitable structures | Strong physical positive control; argues against a blanket “propagation cannot create vortices” rule | Does not make the particular historical DBS count a physical count |
| Zeng & McGough (2008), *Evaluation of the angular spectrum approach for simulations of near-field pressures*, DOI `10.1121/1.2812579`, open access | FFT angular-spectrum simulations with finite windows and spectral restriction | Demonstrates spectral aliasing, edge/window errors, and zero-padding trade-offs in a related wave-propagation setting | Strong methodological match for padding and FFT-artifact controls | Acoustic implementation differs from scalar optical vortices |
| Heintzmann (2023), *Scalable angular spectrum propagation*, Optica `10`, 1407, DOI linked from Optica search result | FFT-based angular-spectrum implementation | Addresses scalable FFT propagation and numerical implementation choices | Moderate match for architecture/propagator controls | Does not address vortex-count bias directly |
| Talens et al. / zero-padding and scalar-diffraction literature (multiple search results) | FFT diffraction and zero-padding | Treats aliasing and sampling/zero-padding as numerical controls | Strong methodological match | Exact optical-vortex detector consequences remain implementation-specific |
| Bazen & Gerez (2002), *Systematic methods for the computation of directional fields and singular points of fingerprints*, DOI `10.1109/TPAMI.2002.1017618` | Discrete directional-field topology | Shows finite-step winding/index methods and their numerical limitations | Cross-domain match to discrete winding | Not optical and not a propagation study |
| Hoffmann & Sbalzarini (2021), *Robustness of topological defects in discrete domains*, DOI `10.1103/PhysRevE.103.012602`, open access | Robustness measures for discrete defects, localization, pair events | Establishes that discrete topological charge changes discontinuously under finite perturbations and proposes robustness/uncertainty measures | Very strong conceptual match to the detector-battery and red-team design | Does not prescribe optical sampling convergence |
| Dev (2023), *Probing topological charge of discrete vortices*, arXiv:2305.08410 | Discrete vortex charge measurement | Addresses charge extraction from discrete data | Moderate match; supports independent charge checks | Preprint/search coverage is not a complete priority audit |
| Pu et al. (2022), *Measurements of phase distributions of optical vortices*, Optics Continuum `1`, 2287, DOI linked from Optica search result | Realistic phase maps and detection error | Directly studies accuracy of topological-charge derivation from realistic sampled phase | Strong match to detector error and phase-map controls | Does not reproduce this project’s grid/padding matrix |
| Bussière et al. (2024), *Application of a Combinatorial Vortex Detection Algorithm*, MDPI Photonics `9`, 53 | Alternative vortex detector | Shows detector algorithm choice materially changes vortex detection/quantification | Strong match to detector-independence requirement | Does not establish a universal detector failure law |
| Popiołek-Masajada et al., *Subpixel localization of optical vortices using artificial neural networks* | Subpixel vortex localization | Confirms that localization is a separate issue from integer count | Moderate match to localization-error endpoint | Neural-network method is not a neutral topology reference for this study |

## EXP-0016 targeted measurement-definition audit (2026-09-24)

A supplemental search was run for discrete optical-vortex detection, contour
methods, subpixel localization, and accuracy of vortex-detection algorithms.
The search reinforces the need to name the measurement observable; it does not
establish priority for this implementation.

| Source/search lead | Relevance to EXP-0016 | Limitation |
|---|---|---|
| Wang et al. (2019), “Topological Charge Detection Using Generalized Contour…” (Applied Sciences 9, 3956) | Contour-sum charge measurement is a detector definition with geometry and interpolation choices | Not the present raw/cluster/Jacobian comparison or phase diagram |
| Khorin, Khonina, Porfirev, Kazanskiy (2022), Sensors 22, 7365, DOI `10.3390/s22197365` | Explicitly distinguishes vortex phase singularities/topological charge and uses multiple measurement geometries | Optical experiment uses engineered astigmatic transformations, not finite-grid raw winding |
| “Analysis of Accuracy of Optical Vortex Detection Algorithms” (search-indexed record) | Direct indication that algorithm choice affects vortex-detection accuracy | Search metadata was not treated as a complete priority audit |
| Shen et al. (2019), “Optical vortices 30 years on” | Foundational continuous-topology and measurement context | Review does not certify a universal finite-grid count law |
| Hoffmann & Sbalzarini (2021), discrete-defect robustness | Conceptual basis for discontinuous discrete charge and robustness reporting | Cross-domain theory; not an optical sampling law |
| Eshaghi et al. (2022), phase-memory study; Indebetouw (1993), vortex propagation | Support contour/sampling and propagation controls | Neither studies the historical detector or EXP-0016 exact matrix |

The search did not identify a paper establishing the exact combination of
historical DeepBeamScan code, 256² periodic ASM, and the historical +1280 µm
count as a new physical phenomenon. More importantly for EXP-0016, the
measurement-definition warning is already motivated by established contour,
phase-singularity, subpixel-localization, and discrete-topology literatures.
The present result is therefore classified as a controlled numerical
methodological result, not a novelty claim.

## Search conclusion

The searched literature already explains several pieces that the historical
project treated as suspicious: continuous phase winding, finite-sampling
uncertainty, contour geometry, FFT aliasing/windowing, and genuine
propagation-driven vortex-pair dynamics. I did **not** locate a paper that
establishes the exact combination “this historical DeepBeamScan detector,
this 256² periodic ASM, and this `+1280 µm` count” as a new physical
phenomenon. That is only a statement about the searches performed.

The strongest plausible contribution of EXP-0015/0016 is therefore narrower:
a reproducible characterization of when discrete topological-count
measurements become grid-, contour-, charge-representation-, or
downsampling-dependent, with an explicit separation of detector error from
propagation error. EXP-0016 passes its registered numerical controls, but the
result remains **no novelty claim**: the observed behavior is a known
measurement-definition/detector-semantics result, not a new physical law.
