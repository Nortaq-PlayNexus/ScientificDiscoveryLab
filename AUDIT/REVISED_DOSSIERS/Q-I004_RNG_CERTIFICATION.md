# REVISED DOSSIER: Q-I004 — RNG Certification

**Revised by:** Forensic Audit, 2026-09-23
**Original:** 03_INVESTIGATIONS/OTHER/rng_certification/
**Changes:** Documented separately from original; original preserved

---

## 1. What This Investigation IS

A certification of the lab's sha256-derived PCG64 random number generator against a standard statistical battery.

## 2. What This Investigation DOES NOT Prove

- **Does NOT prove** the RNG passes ALL standard batteries — only a lightweight battery was tested
- **NIST SP 800-22** has not been run
- **Does NOT prove** suitability for cryptographic purposes

## 3. Key Numbers

| Test | Result |
|---|---|
| KS uniformity | PASS |
| Binomial band | PASS |
| BH-FDR | PASS |
| C7 independent | 30/30 agreement |
| p-value distribution | Uniform (FIGURES/EXP-0004_pvalue_distribution.png) |

## 4. Controls

- **C1**: KS uniformity PASS
- **C2**: Binomial band PASS
- **C3**: Seed ladder (multiple seeds, consistent)
- **C4**: Resolution variation PASS
- **C5**: Method agreement PASS (BH-FDR vs other methods)
- **C6**: Independent implementation PASS (30/30)
- **C7**: 30/30 agreement with independent check

## 5. Known Issues

- **Limited battery**: Only KS + binomial + BH-FDR tested; NIST SP 800-22 not run
- **Stream length**: Tested at lab stream lengths only; longer streams not verified
- **CPU-only**: No GPU RNG tested

## 6. Reproduction Status

- **Deterministic**: RNG is stochastic; seed varies per test
- **Independent implementation**: PASS (independent_check.py, 30/30)
- **Full instructions**: REPORT/TECHNICAL_SUMMARY.md

## 7. Recommended Wording

> The lab's sha256-derived PCG64 random number generator passes KS uniformity, binomial band, and BH-FDR tests at lab stream lengths, with an independent implementation agreeing 30/30 across all tested batteries. Note: only a lightweight battery was tested; NIST SP 800-22 has not been run.
