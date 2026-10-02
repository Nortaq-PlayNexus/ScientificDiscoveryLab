# EXP-0003 broadband resolution audit — literature/novelty search log

**Search date:** 2026-09-24 (UTC)
**Scope:** phase-singularity/vortex density in complex Gaussian random waves; Kac–Rice/Nye–Berry prediction; numerical contour/winding detection; sampling, aliasing, Nyquist limits, and finite-resolution validation.

## Search method and limitations

I attempted live searches in parallel with the numerical run using the available web-search integration and direct HTTP metadata/landing-page retrieval. The generic web-search endpoint returned no results for the initial queries. Direct Crossref and OpenAlex metadata endpoints were reachable for selected records; Semantic Scholar returned HTTP 429 and some publisher pages returned 403/429. Therefore this is a targeted, reproducible metadata/primary-source search, not a claim of an exhaustive systematic review. Search strings included:

- `phase singularities isotropic random waves`
- `dislocations in wave trains Nye Berry`
- `phase singularities complex arithmetic random waves`
- `optical vortex Gaussian random wave fields Freund`
- `numerical phase singularity detection sampling aliasing`
- `aliasing phase singularity numerical random wave fields`
- `Kac-Rice formula complex Gaussian field zero density two dimensional spectral density`

No novelty claim is made. The numerical resolution-convergence result should be regarded as an implementation/methodological audit unless a later systematic search establishes otherwise.

## Primary/authoritative sources located

1. **Nye, J. F. & Berry, M. V. (1974), “Dislocations in wave trains,” Proc. R. Soc. A 336, 165–190.**  
   DOI: <https://doi.org/10.1098/rspa.1974.0012>  
   Crossref metadata and abstract retrieved. Foundational identification of phase singularities/wave dislocations and zero amplitude at dislocation lines. Crossref records the abstract and bibliographic details.

2. **Berry, M. V. (1978), “Disruption of wavefronts: statistics of dislocations in incoherent Gaussian random waves,” J. Phys. A 11, 27–37.**  
   DOI: <https://doi.org/10.1088/0305-4470/11/1/007>  
   DOI metadata retrieved. Directly relevant precedent for dislocation statistics in incoherent Gaussian random waves.

3. **Berry, M. V. & Dennis, M. R. (2000/2001), “Phase singularities in isotropic random waves,” Proc. R. Soc. A 456, 2059–2079.**  
   DOI: <https://doi.org/10.1098/rspa.2000.0602>  
   Crossref and OpenAlex metadata retrieved. OpenAlex abstract states that the paper calculates dislocation statistics for isotropically random Gaussian plane-wave superpositions, including density and pair correlations, for general spectra and a monochromatic specialization. This is the closest primary precedent to EXP-0003's density law.

4. **Freund, I. (1994), “Optical vortices in Gaussian random wave fields: statistical probability densities,” JOSA A 11, 1644.**  
   DOI: <https://doi.org/10.1364/JOSAA.11.001644>  
   DOI metadata retrieved; title and venue establish a direct optical Gaussian-random-wave precedent.

5. **Shvartsman, N. & Freund, I. (1994), “Wave-field phase singularities: near-neighbor correlations and anticorrelations,” JOSA A 11, 2710–2718.**  
   DOI: <https://doi.org/10.1364/JOSAA.11.002710>  
   DOI metadata retrieved. Relevant to statistical structure of phase singularities, though not specifically to this audit's resolution ladder.

6. **Azaïs, J.-M., León, J. R. & Wschebor, M. (2011), “Rice formulae and Gaussian waves,” Bernoulli 17(1), 170–193.**  
   DOI: <https://doi.org/10.3150/10-BEJ265>  
   DOI metadata retrieved. Authoritative Rice/Kac formula reference for Gaussian-wave zero/level-crossing statistics.

7. **Dalmao, F., Nourdin, I., Peccati, G. & Rossi, M. (2019), “Phase singularities in complex arithmetic random waves,” Electron. J. Probab. 24.**  
   DOI: <https://doi.org/10.1214/19-EJP321>  
   Metadata was returned in the Crossref search result. It is a more recent rigorous random-wave phase-singularity reference, although its model is arithmetic random waves rather than the present isotropic Fourier-Gaussian construction.

8. **De Angelis, L. & Kuipers, C. (2021), “Effective pair-interaction of phase singularities in random waves,” Optics Letters 46, 2734.**  
   DOI: <https://doi.org/10.1364/OL.422910>  
   Metadata/abstract was returned through Crossref/OpenAlex searches. Relevant to modern random-wave singularity studies; not a direct resolution-convergence study located here.

9. **Shannon, C. E. (1949), “Communication in the Presence of Noise,” Proc. IRE 37, 10–21.**  
   Canonical sampling theorem source. The accessible secondary summary and sampling/aliasing statement were checked at <https://en.wikipedia.org/wiki/Nyquist%E2%80%93Shannon_sampling_theorem>; the original DOI was not reliably resolved by the DOI endpoint during this run. The relevant mathematical fact used in the audit is that a uniformly sampled band-limited field is recoverable only when its occupied bandwidth is below the Nyquist rate; unresolved high-frequency content aliases.

## What the search supports

- The Kac–Rice/Nye–Berry density and phase-singularity statistics in Gaussian/isotropic random waves are established physics, not a novel hypothesis.
- The literature search located foundational theory and Gaussian-wave applications, but did not locate a paper matching this exact combined protocol: fixed physical spectrum, 4/6/8/12/16/24/32/48/64 pixels-per-wavelength ladder, winding-versus-contour comparison, low-pass controls, nested common-field sampling, and six-seed uncertainty audit.
- That absence is **not evidence of novelty**. The resolution-convergence result is best labeled an audit/methodological characterization. Any potentially distinctive feature (for example, a quantitative broadband convergence curve for this implementation) must be flagged for the main auditor rather than advertised as new physics.

## Reproducible URLs queried

- Crossref work metadata: <https://api.crossref.org/works/10.1098/rspa.2000.0602>
- Crossref work metadata: <https://api.crossref.org/works/10.1098/rspa.1974.0012>
- OpenAlex work metadata/abstract: <https://api.openalex.org/works/https://doi.org/10.1098/rspa.2000.0602>
- Crossref query endpoint: <https://api.crossref.org/works?query.bibliographic=phase%20singularities%20isotropic%20random%20waves&rows=3&select=DOI,title,author,published,URL,container-title>
- OpenAlex search endpoint: <https://api.openalex.org/works?search=phase%20singularities%20random%20waves&per-page=10&select=id,doi,title,publication_year,authorships,primary_location>

The numerical audit report records the exact run command, software versions, seed streams, raw tables, and any deviations from this planned scope.
