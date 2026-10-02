# figures/README.md — Figure Index

This folder does **not** contain copies of the figures. Every figure referenced
by this dossier already exists in the source projects and is **referenced here
by relative path**, so the dossier stays a text-only deliverable that points at
its evidence without duplicating binary files.

All figures in the index are **simulation renders** (deterministic computation),
not physical photographs. They illustrate the audit's mechanics; they are not
themselves the evidence. The evidence is the number files listed in
`DATA_INDEX.md` (§1–§4).

## 1. Sandbox — audit figure set

Source directory:
`sandbox\reports\figures\dossier\` (i.e.
`C:\Users\natha\code\coherent-optical-ai-sandbox\reports\figures\dossier\`)

| File | Content | Referenced by |
|---|---|---|
| `V01_resolution_independence.png` | feature counts vs grid resolution | Dossier §7 (A4); §5 EXP-4 |
| `V02_coherence_ladder.png` | coherence-ladder sweep | methods context |
| `V03_phase_randomization.png` | phase-randomisation identity | Dossier §3 (correction) |
| `V05_propagation_persistence.png` | feature persistence over z | Dossier §5 EXP-1/EXP-2 |
| `V06_wavelength_sweep.png` | wavelength sweep | Dossier §7 A6; wavelength claims AGAINST |
| `V07_winding_balance.png` | winding +24/−24 balance | Dossier R2; §9 |
| `V08_blind_confusion.png` | blind coded-field confusion matrix | Dossier §5.3; §8 |
| `V09_32um_grid_origin.png` | "32 µm" grid-origin artifact | Dossier R1; §7 A2 |
| `E07_anticheat_band_power.png` | anti-cheat band-power (C-control 0.595 INVALID) | Dossier §5.3; NEGATIVE §6 |
| `E08_information_ber.png` | information/error-rate channels | methods context |
| `E09_fourier_spectrum.png` | Fourier spectrum (41.66 c/mm blend) | Dossier §7 A6 |
| `M01_phase_confidence.png` | phase-confidence map | methods context |
| `M03_blind_100sample.png` | blind 100-sample trial | Dossier §5.3 |
| `M04_phase_runtime.png` | runtime statistics | methods context |

## 2. Sandbox — emergence-control figure set

Source directory:
`sandbox\reports\figures\emergence_control\` (i.e.
`C:\Users\natha\code\coherent-optical-ai-sandbox\reports\figures\emergence_control\`)

| File | Content | Referenced by |
|---|---|---|
| `fig01_input_intensity.png` | designed lattice input | Dossier §4; R1 |
| `fig02_propagated_160um.png` | 160 µm ASM-propagated intensity | Dossier §5/§9 |
| `fig03_ncc_vs_distance.png` | NCC vs propagation distance | Dossier §3 |
| `fig04_features_vs_distance.png` | feature counts vs distance | Dossier §5 |
| `fig05_pairwise_ncc.png` | pairwise NCC between planes | methods context |
| `fig06_fourier_bands.png` | Fourier band anti-cheat | Dossier §7 A6; NEGATIVE §6 |

## 3. Lab figure set (if the reviewer wants the matching lab plots)

The lab's plots live inside each investigation's `FIGURES\` folder, e.g.
`C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS\OPTICS\vortex_density\FIGURES\EXP-0003_*.png`
(vortex-density reproduction), `...\rng_certification\FIGURES\EXP-0004_pvalue_distribution.png`,
and the percolation `FIGURES\` under `03_INVESTIGATIONS\PHYSICS\percolation\`.

## 4. Copy policy

If this dossier is ever exported as a standalone package, copy the referenced
PNGs next to this README and mark each file's provenance in `DOSSIER_BUILD_REPORT.md`.
Do **not** relabel simulation renders as measurements in any export.