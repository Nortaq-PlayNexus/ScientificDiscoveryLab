# REPRODUCE — ScientificDiscoveryLab

**Audit date:** 2026-09-23
**Primary source:** `C:\Users\natha\ScientificDiscoveryLab`
**Auditor:** Automated forensic inventory (Phase 19 of 20)

---

## 1. Machine Setup

Per `REPRODUCIBILITY.md`:

```
OS: Windows 10 Home
CPU: Intel Core i7-8700 (6C/12T) @ 3.20 GHz
RAM: 24 GB
GPU: NVIDIA GTX 1080 8 GB
Free disk: ~1.5 TB (C:)
```

## 2. Software Installation

```bash
# Core scientific Python
pip install numpy==2.5.3 scipy==1.18.1 matplotlib==3.11.2
pip install scikit-image==0.26.0 scikit-learn==1.9.1 sympy==1.14.0
pip install Pillow==12.3.0 ImageIO==2.37.4
pip install torch==2.14.0+cpu torchvision==0.29.0+cpu --index-url https://download.pytorch.org/whl/cpu

# NOT installed (not needed): pandas, astropy, statsmodels, plotly, JAX, TensorFlow
```

**Note:** Python 3.14.7 specified. Other versions may produce slightly different results due to RNG implementation differences.

## 3. Reproducing Each Experiment

### 3.1 Infrastructure (EXP-0001)

```bash
cd 04_SHARED_ENGINE
python -m engine.tests.run_infra_validation
# Expected: 14/14 checks PASS
```

### 3.2 Speckle Contrast (EXP-0002, Q-O001)

```bash
cd 03_INVESTIGATIONS/OPTICS/speckle_contrast_law
python CODE/run_speckle_contrast.py       # ~2 min CPU; writes CONFIG/ + RESULTS/
python REPLICATION/independent_check.py    # independent route, ~1 min
python CODE/make_figure.py                 # FIGURES/EXP-0002_contrast_law.png
```

**Seeds:** 42 (ladder: 7, 123, 2023, 314159, 271828)
**Config:** CONFIG/prereg_EXP-0002.json (frozen)
**Key result:** r = C·sqrt(M) ∈ [0.9968, 1.0003] at N=256

### 3.3 Vortex Density (EXP-0003, Q-O002)

```bash
cd 03_INVESTIGATIONS/OPTICS/vortex_density
python CODE/run_vortex_density.py
python REPLICATION/independent_check.py
python CODE/make_figure.py
```

**Seeds:** 42
**Config:** CONFIG/prereg_EXP-0003.json (frozen)
**Key result:** n_meas/n_pred = 0.9952–1.0011 at N=1024 (narrow-band)

### 3.4 Percolation Thresholds (EXP-0005/0006/0007)

```bash
cd 03_INVESTIGATIONS/PHYSICS/percolation

# EXP-0005 (original)
python CODE/run_percolation.py --config CODE/CONFIG/EXP-0005_experiment.json

# EXP-0007 (resolved, extended L=96,128,192)
python CODE/run_percolation_exp0007.py

# Independent replication (C7)
python REPLICATION/independent_check.py
python REPLICATION/independent_check_exp0007.py
```

**Key result:** bond_wrap p_c = 0.500687; C7: 78/78 cells bit-identical

### 3.5 Percolation Exponents (EXP-0009/0010)

```bash
cd 03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents
python CODE/run_exp0009.py        # EXP-0009: large-scale run (~may take hours)
python CODE/run_exp0010.py        # EXP-0010: non-power-of-2 lattices
python REPLICATION/independent_check_exp0009.py
```

**Note:** _cells_L2048_n50.npz is 46.6 MB; regeneration takes significant time and disk.
**Key result:** D_f = 1.8962 ± 0.028 at non-power-of-2 L (theory 91/48)

### 3.6 Prime Gaps (EXP-0008, Q-M002)

```bash
cd 03_INVESTIGATIONS/MATHEMATICS/prime_gaps
python CODE/run_prime_gaps.py                    # ~38 min CPU
python REPLICATION/independent_check.py           # independent route
# C7 report: REPLICATION/C7_exp0008_report.json
```

**Seeds:** 42 (run1_pre_bhfix variant also available)
**Config:** CONFIG/prereg_EXP-0008.json (frozen, sha256 recorded)
**Key result:** χ²_red = 26,998; G1/G3 rejected after BH-FDR in 4/4 blocks

### 3.7 Feigenbaum Constants (EXP-0014, Q-M005)

```bash
cd 03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants
python CODE/run_feigenbaum.py
# Deterministic; no RNG; no seeds needed
```

**Key result:** δ_8 = 4.66906 vs published 4.6692016091029 (dev = 1.4e-4)

### 3.8 RNG Certification (EXP-0004, Q-I004)

```bash
cd 03_INVESTIGATIONS/OTHER/rng_certification
python CODE/run_rng_cert.py
python CODE/plot_battery.py
python REPLICATION/independent_check.py
```

**Key result:** CERTIFIED — KS uniformity + binomial band + BH-FDR all PASS; C7 30/30

### 3.9 3D Percolation (EXP-0011/0013, Q-P008)

```bash
cd 03_INVESTIGATIONS/PHYSICS/percolation_3d
python CODE/run_exp0011.py
# EXP-0013 running (as of 2026-09-23)
```

### 3.10 Cone Mosaic Aliasing (EXP-0012, OTHER)

```bash
# Limited documentation; prereg only
# CONFIG/prereg_EXP-0012.json exists
# No CODE/ or REPLICATION/ directory documented
```

## 4. Shared Engine Usage

```bash
cd 04_SHARED_ENGINE

# Engine imports
from engine.utilities.rng import label, seed   # sha256-derived PCG64
from engine.statistics.testers import BH_FDR   # Benjamini-Hochberg
from engine.simulation.controls import Controls # Control framework
from engine.datasets.manifest import manifest   # Dataset management

# Infrastructure validation
python -m engine.tests.run_infra_validation    # 14/14 checks

# Dashboard
python dashboard.py  # Open http://127.0.0.1:8008
```

## 5. Random Seed Protocol

All experiments use `engine.utilities.rng(label, seed)` — sha256-derived Generator, independent of Python's `hash()` salt. Verified stable across fresh processes.

**Standard seeds:** 42 (primary), 7, 123, 2023, 314159, 271828 (ladder)
**Independent streams:** 101, 202, 303 (EXP-0007 extension)

## 6. Data File Locations

| Data Type | Location |
|---|---|
| Experiment config | `*/CONFIG/EXP-####_experiment.json` |
| Frozen prereg | `*/CONFIG/prereg_*.json` |
| Results | `*/RESULTS/EXP-####_results.json` |
| Raw results | `*/RESULTS/EXP-####_raw.json` |
| Independent replication | `*/REPLICATION/` |
| Reports | `*/REPORT/TECHNICAL_*.md` |
| Figures | `*/FIGURES/*.png` |
| Registry | `*/CONFIG/registry.jsonl` |

## 7. Reproduction Verification Checklist

For each experiment, confirm:

- [ ] Prereg file exists and matches frozen state
- [ ] Code is accessible and readable
- [ ] Independent implementation exists
- [ ] Config file has all parameters recorded
- [ ] Results JSON has all gates and controls
- [ ] Report has TECHNICAL and PLAIN summaries
- [ ] Registry entry is present
- [ ] Figure is reproducible
- [ ] Seed is recorded
- [ ] Deterministic reproduction matches (within stated tolerances)

## 8. Known Reproduction Issues

| Issue | Experiment | Workaround |
|---|---|---|
| Large npz files (46.6 MB) | EXP-0009 | May need significant disk; existing files are in RESULTS/ |
| _cells files saved to wrong directory | Q-P006 | Already fixed; files COPIED |
| Python version sensitivity | All | Use Python 3.14.7 per REPRODUCIBILITY.md |
| pandas not installed | — | Not needed; shared code avoids it |
| BH-FDR bug (fixed) | EXP-0002 | Fixed in 04_SHARED_ENGINE/ |

## 9. Time Estimates

| Experiment | Approximate Runtime |
|---|---|
| EXP-0001 (Infra) | Seconds |
| EXP-0002 (Speckle) | ~2 min CPU |
| EXP-0003 (Vortex) | ~5–10 min CPU |
| EXP-0004 (RNG) | ~5–15 min CPU |
| EXP-0005/0006/0007 (Percolation) | Minutes to hours depending on L |
| EXP-0009 (Percolation exponents) | Hours (L=1024, n=50+100) |
| EXP-0008 (Prime gaps) | ~38 min CPU |
| EXP-0010 (Lattice artifact) | ~30 min CPU |
| EXP-0014 (Feigenbaum) | Minutes (deterministic) |

## 10. Contact for Reproduction Issues

Per CHANGELOG.md and project structure, contact: Nathan (DJ PhantomTape)
Via: Research group infrastructure (details in FOLLOWUP_EMAIL.md)
