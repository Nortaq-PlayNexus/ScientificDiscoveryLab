# NOVELTY REVIEW — ScientificDiscoveryLab

**Audit date:** 2026-09-24  
**Scope:** claims in the laboratory files, prior audit reports, and the completed EXP-0003 broadband sub-audit.  
**Standard applied:** a claim is not called novel unless the search located prior work and the laboratory result is both reproducible and distinguishable from it. “No match found” is not evidence of novelty.

## Search method and limitations

The review used the laboratory `LITERATURE.md` files as a starting point, then queried Crossref REST metadata and OpenAlex metadata for the following topics:

- random-wave phase singularities, Kac–Rice/Nye–Berry density, optical vortex detection, and sampling resolution;
- fully developed speckle and summed-speckle contrast;
- two- and three-dimensional percolation thresholds and exponents;
- prime gaps in short intervals and Gallagher/Poisson models;
- period-doubling Feigenbaum constants for higher-order extrema;
- NIST SP 800-22 and PRNG statistical testing.

The web-search connector was unavailable or returned no results for several broad queries. Crossref/OpenAlex searches were therefore metadata/abstract searches rather than a formal Scopus/Web-of-Science/Google Scholar systematic review. Publisher full text was not uniformly available. The exact absence of a search hit is therefore recorded as **unknown**, not as novelty.

## Claim-by-claim assessment

| Laboratory claim | Prior art located | Independent evidence in this audit | Classification |
|---|---|---|---|
| EXP-0002: `C(M)=1/sqrt(M)` for summed independent speckle intensities | Goodman, *Statistical Optics* / *Speckle Phenomena in Optics*; standard fully developed speckle theory | Independent PCG64 complex-Gaussian and pupil-FFT tests over 255/256/257 and rectangular grids give the square-root law within sampling error | **Known-law reproduction; not novel** |
| EXP-0003: vortex density follows the Kac–Rice/Nye–Berry prediction in resolved random waves | Nye & Berry (1974); Berry & Dennis (2000/2001); Rice/Kac–Rice theory | Fixed-physical-spectrum P=4…64 sweep shows the broad-band deficit shrinking toward 1 as P increases; corrected controls are consistent with finite spectral support/aliasing and detector limitations | **Known-law reproduction plus a useful numerical resolution audit; exact laboratory protocol not verified as novel** |
| EXP-0003 “broadband resolution effect is a new discovery” | No exact match located in the searches; foundational resolution/detection literature is extensive | The sub-audit’s interpolation control initially had a factor-of-`P²` normalization bug, and its synthetic-vortex sanity control failed; corrected controls are required before a strong mechanistic claim | **Novelty unresolved; do not claim** |
| EXP-0005–0007: bond/site percolation thresholds and finite-size behavior | Kesten/Sykes–Essam for exact 2D bond `p_c=1/2`; Newman & Ziff (2000); percolation reviews | EXP-0007 isolated rerun is byte-identical; p_c estimates are compatible with known thresholds. Power-of-two versus non-power-of-two `D_f` differences are not statistically separated | **Known-law reproduction; “LATTICE_ARTIFACT” diagnosis not supported** |
| EXP-0009/0010: 2D critical exponents | Exact 2D exponents `D_f=91/48`, `gamma/nu=43/24`, `beta/nu=5/48`, `tau=187/91`; standard scaling theory | Raw-cache reanalysis and independent non-power-of-two simulations overlap the theoretical values; EXP-0009’s deviations are finite-sample/estimator effects, not a new universality class | **Known-law reproduction; anomaly diagnosis overclaimed** |
| Q-P007: a refined `p_c` explains the exponent/tau deviations | Threshold uncertainty and finite-size effects are standard percolation issues | The Q-P007 nested cache is malformed and its tau tail is empty; corrected paired reanalysis shows only a tiny p_c effect at L=128–512 | **Invalid historical result; no discovery** |
| EXP-0011/0013: 3D percolation exponents | Published 3D estimates and Monte Carlo studies (e.g. Deng & Blöte, 2005; modern high-dimensional work) | EXP-0011 is a tiny pilot; the main run is not complete. No 3D discovery can be assessed | **Pilot/operational evidence only** |
| EXP-0008/Q-M007/Q-M008: normalized prime gaps deviate from `Exp(1)` | Gallagher’s theorem concerns primes in short intervals under the Hardy–Littlewood framework; Poisson is a standard baseline | Reanalysis finds strong finite-range dependence, structural exclusion of the first bin, and scale-dependent variance. The finite-bin chi-square rejection is not a novel prime process | **Descriptive finite-range deviation; mechanism/novelty unestablished** |
| EXP-0014: Feigenbaum delta for z=2,3,4 | Feigenbaum (1978) for z=2; Hu & Mao (1982), “Period doubling: Universality and critical-point order,” for higher-order extrema | Independent arbitrary-precision continuation obtains period-verified sequences (`z=3 delta_8≈6.08467`, `z=4 delta_8≈7.28509`) and exposes historical root-selection failures | **Known universality reproduction; historical higher-order output invalid, not novel** |
| EXP-0004: “CERTIFIED” RNG | NIST SP 800-22 Rev. 1a explicitly says statistical tests cannot certify a generator | Fresh 80-seed marginal calibration shows dependent p-values and test-specific calibration failures; the pooled decision assumption is false | **Methodological claim withdrawn; no novelty** |
| Q-S9-1/2/3: AI pareidolia threshold, dose response, detector de-biasing | No external-data reproduction is present in the laboratory | Q-S9-1/3 writers hard-code values; Q-S9-2 generates synthetic Hill data from assumed parameters | **Not empirically reproduced; no discovery claim** |
| Q-M001: generalized Collatz “iff `a=b=c`” | No external source is needed to assess the local code | The saved full result contains only three convergent families; the runner treats every `max_steps` trajectory as a cycle and the claimed full sweep is not present | **Incomplete/invalidly diagnosed; no discovery claim** |
| External dossier R1–R8 | Source documents/results are outside the audited laboratory tree | Cannot be regenerated or checked from the files supplied | **Out of scope / not independently verified** |

## Verified authoritative references

1. J. F. Nye and M. V. Berry, “Dislocations in wave trains,” *Proceedings of the Royal Society A* **336**, 165–190 (1974), DOI: [10.1098/rspa.1974.0012](https://doi.org/10.1098/rspa.1974.0012). Foundational phase-singularity/dislocation source; not a finite-grid convergence benchmark.
2. M. V. Berry and M. R. Dennis, “Phase singularities in isotropic random waves,” *Proceedings of the Royal Society A* **456**, 2059–2079 (2000/2001), DOI: [10.1098/rspa.2000.0602](https://doi.org/10.1098/rspa.2000.0602), with indexed erratum [10.1098/rspa.2000.0602.erratum](https://doi.org/10.1098/rspa.2000.0602.erratum). Spectral random-wave singularity statistics.
3. S. O. Rice, “Mathematical Analysis of Random Noise,” *Bell System Technical Journal* (1944), DOI: [10.1002/j.1538-7305.1944.tb00874.x](https://doi.org/10.1002/j.1538-7305.1944.tb00874.x). Primary Kac–Rice/Rice source.
4. M. L. M. Balistreri et al., “Local Observations of Phase Singularities in Optical Fields in Waveguide Structures,” *Physical Review Letters* **85**, 294–297 (2000), DOI: [10.1103/PhysRevLett.85.294](https://doi.org/10.1103/PhysRevLett.85.294); and R. Dändliker et al., “Measuring optical phase singularities at subwavelength resolution,” *Journal of Optics A* **6**, S189–S196 (2004), DOI: [10.1088/1464-4258/6/5/009](https://doi.org/10.1088/1464-4258/6/5/009). Relevant prior art showing that sampling scale and coherent detection matter.
5. M. E. J. Newman and R. M. Ziff, “Efficient Monte Carlo Algorithm and High-Precision Results for Percolation,” *Physical Review Letters* **85**, 4104–4107 (2000), DOI: [10.1103/PhysRevLett.85.4104](https://doi.org/10.1103/PhysRevLett.85.4104). Percolation method reference.
6. M. F. Sykes and J. W. Essam, “Exact Critical Percolation Probabilities for Site and Bond Problems in Two Dimensions,” *Journal of Mathematical Physics* **5**, 1117–1127 (1964), DOI: [10.1063/1.1704215](https://doi.org/10.1063/1.1704215). Exact 2D thresholds.
7. Y. Deng and H. W. J. Blöte, “Monte Carlo study of the site-percolation model in two and three dimensions,” *Physical Review E* **72**, 016126 (2005), DOI: [10.1103/PhysRevE.72.016126](https://doi.org/10.1103/PhysRevE.72.016126). 3D site-percolation reference.
8. P. X. Gallagher, “On the distribution of primes in short intervals,” *Mathematika* **23** (1976), DOI: [10.1112/S0025579300016442](https://doi.org/10.1112/S0025579300016442). The laboratory’s “Gallagher” attribution should use this title rather than the unrelated “The differences between consecutive primes, II.”
9. M. J. Feigenbaum, “Quantitative universality for a class of nonlinear transformations,” *Journal of Statistical Physics* **19**, 25–52 (1978), DOI: [10.1007/BF01020332](https://doi.org/10.1007/BF01020332).
10. B. Hu and J. M. Mao, “Period doubling: Universality and critical-point order,” *Physical Review A* **25**, 3259–3261 (1982), DOI: [10.1103/PhysRevA.25.3259](https://doi.org/10.1103/PhysRevA.25.3259). This corrects the title/DOI mismatch in the laboratory literature file.
11. NIST, *SP 800-22 Rev. 1*, DOI [10.6028/NIST.SP.800-22r1a](https://doi.org/10.6028/NIST.SP.800-22r1a), official page [CSRC](https://csrc.nist.gov/pubs/sp/800/22/r1/upd1/final). NIST explicitly states that statistical testing cannot absolutely certify a generator.

## Novelty verdict

No laboratory result in the audited tree meets a defensible novelty standard. The strongest contributions are **independent reproductions, artifact discoveries, and corrected negative controls**. The EXP-0003 fixed-spectrum convergence experiment is potentially useful as a methods/control study, but the exact protocol was not matched in the metadata search and the first control implementation had a normalization defect. It must be described as an **audit result with novelty unresolved**, never as a confirmed new physical law.
