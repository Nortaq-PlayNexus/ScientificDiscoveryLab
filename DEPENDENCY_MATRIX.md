# DEPENDENCY MATRIX

SOVEREIGN BIOCHEMICAL DISCOVERY LAB — Complete Dependency Assessment

Date: 2026-09-20

---

## Core Chemistry

| Dependency | Version Available | License | Python 3.14 | Windows | Offline | API Required | Install Risk | Status |
|---|---|---|---|---|---|---|---|---|
| RDKit | 2026.3.6 | BSD-3-Clause | ✅ | ✅ | ✅ | No | LOW | AVAILABLE |
| Open Babel | 3.2.1 | GPL-2.0 | ✅ | ✅ | ✅ | No | LOW | AVAILABLE |
| OpenMM | 8.6.1 | LGPL | ✅ | ✅ | ✅ | No | LOW | AVAILABLE |
| Psi4 | Unknown | LGPL | ⚠️ | ❌ | ✅ | No | HIGH | BLOCKED |
| PySCF | 2.14.0 | Apache-2.0 | ⚠️ | ⚠️ | ✅ | No | HIGH | BLOCKED |

## Biological / Database

| Dependency | Version Available | License | Python 3.14 | Windows | Offline | API Required | Install Risk | Status |
|---|---|---|---|---|---|---|---|---|
| Biopython | 1.88 | Biopython | ✅ | ✅ | Partial | Yes (optional) | LOW | AVAILABLE |
| PubChemPy | 1.0.5 | MIT | ✅ | ✅ | ❌ | Yes (PubChem) | VERY LOW | AVAILABLE |
| ChEMBL API | REST | CC BY-SA 3.0 | N/A | N/A | ❌ | Yes | N/A | AVAILABLE |
| ChEBI API | REST | CC BY-SA 4.0 | N/A | N/A | ❌ | Yes | N/A | AVAILABLE |
| RCSB PDB API | REST | Open Access | N/A | N/A | ❌ | Yes | N/A | AVAILABLE |
| NCBI E-utilities | REST | Public | N/A | N/A | ❌ | Yes | N/A | AVAILABLE |

## Numerical / Statistical

| Dependency | Version | License | Python 3.14 | Windows | Offline | API Required | Install Risk | Status |
|---|---|---|---|---|---|---|---|---|
| NumPy | 2.5.3 | BSD | ✅ | ✅ | ✅ | No | NONE | INSTALLED |
| SciPy | 1.18.1 | BSD | ✅ | ✅ | ✅ | No | NONE | INSTALLED |
| Pandas | 3.0.6 | BSD | ✅ | ✅ | ✅ | No | NONE | INSTALLED |
| scikit-learn | 1.9.1 | BSD | ✅ | ✅ | ✅ | No | NONE | INSTALLED |
| scikit-image | 0.26.0 | BSD | ✅ | ✅ | ✅ | No | NONE | INSTALLED |
| SymPy | 1.14.0 | BSD | ✅ | ✅ | ✅ | No | NONE | INSTALLED |
| NetworkX | 3.6.1 | BSD | ✅ | ✅ | ✅ | No | NONE | INSTALLED |
| Matplotlib | 3.11.2 | PSF | ✅ | ✅ | ✅ | No | NONE | INSTALLED |
| Plotly | 7.1.0 | MIT | ✅ | ✅ | ✅ | No | LOW | AVAILABLE |

## Machine Learning / DL

| Dependency | Version | License | Python 3.14 | Windows | Offline | GPU | Install Risk | Status |
|---|---|---|---|---|---|---|---|---|
| PyTorch | 2.14.0+cpu | BSD | ✅ | ✅ | ✅ | No | NONE | INSTALLED (CPU) |
| Torchvision | 0.29.0+cpu | BSD | ✅ | ✅ | ✅ | No | NONE | INSTALLED (CPU) |

## Web / API

| Dependency | Version Available | License | Python 3.14 | Windows | Install Risk | Status |
|---|---|---|---|---|---|---|
| FastAPI | 0.141.1 | MIT | ✅ | ✅ | LOW | AVAILABLE |
| SQLAlchemy | 2.0.54 | MIT | ✅ | ✅ | LOW | AVAILABLE |
| Dash | 4.4.1 | MIT | ✅ | ✅ | LOW | AVAILABLE |
| Streamlit | 1.64.0 | Apache-2.0 | ✅ | ✅ | MEDIUM | AVAILABLE |
| Starlette | 1.6.0 | (Starlette) | ✅ | ✅ | LOW | AVAILABLE |
| uvicorn | TBD | BSD | ✅ | ✅ | LOW | NEEDED |

## GUI

| Dependency | Version | License | Python 3.14 | Windows | Status |
|---|---|---|---|---|---|
| PySide6 | 6.11.2 | LGPL | ✅ | ✅ | INSTALLED |
| PyQt5 | 5.15.11 | GPL | ✅ | ✅ | INSTALLED |

## Utilities

| Dependency | Version | License | Python 3.14 | Windows | Status |
|---|---|---|---|---|---|
| requests | 2.34.2 | Apache-2.0 | ✅ | ✅ | INSTALLED |
| httpx | 0.28.1 | BSD | ✅ | ✅ | INSTALLED |
| h5py | 3.16.0 | BSD | ✅ | ✅ | AVAILABLE |
| psutil | 7.2.2 | BSD | ✅ | ✅ | AVAILABLE |
| PyYAML | 6.0.3 | MIT | ✅ | ✅ | INSTALLED |
| pytest | 9.1.1 | MIT | ✅ | ✅ | INSTALLED |

## Hardware Acceleration

| Component | Status | Notes |
|---|---|---|
| NVIDIA GPU | GTX 1080 (8 GB) | Present but CUDA toolkit status UNKNOWN |
| CUDA toolkit | UNKNOWN | ctypes.find_library returns None |
| cuDNN | UNKNOWN | Not verified |
| C/C++ Compiler | ABSENT | cl.exe not in PATH |
| Fortran Compiler | ABSENT | gfortran not found |
| CUDA wheel | NOT INSTALLED | torch installed as +cpu |

---

## Installation Priority

### Immediate (pip install verified)
```
rdkit==2026.3.6
openmm==8.6.1
openbabel==3.2.1
biopython==1.88
pubchempy==1.0.5
h5py==3.16.0
psutil==7.2.2
plotly==7.1.0
fastapi==0.141.1
sqlalchemy==2.0.54
uvicorn
wheel
```

### Deferred (requires compiler toolchain)
```
psi4>=2.14
pyscf>=2.14
```

### Already Installed
```
numpy==2.5.3
scipy==1.18.1
pandas==3.0.6
matplotlib==3.11.2
networkx==3.6.1
scikit-learn==1.9.1
scikit-image==0.26.0
sympy==1.14.0
torch==2.14.0+cpu
torchvision==0.29.0+cpu
PySide6==6.11.2
PyQt5==5.15.11
requests==2.34.2
httpx==0.28.1
PyYAML==6.0.3
pytest==9.1.1
```
