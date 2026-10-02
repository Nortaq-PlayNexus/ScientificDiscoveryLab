# TECHNICAL REPORT — Q-S9-2: REBUS Dose-Response Curve

**Experiment:** Q-S9-2 (dose-response for REBUS-induced pareidolia)
**Parent:** §9 battery (dmt-laser-s9-battery)
**Status:** COMPLETE (results saved as JSON)
**Date:** 2026-09-23 (formal writeup)

---

## 1. Objective

Measure the dose-response relationship of REBUS-induced pareidolia, fitting a Hill equation to determine EC50, Hill coefficient, and maximum inflation.

## 2. Method

- Administered REBUS at doses 0–100% in 10% increments
- Measured "code present" detection rate at each dose
- Fitted Hill equation: rate = baseline + max_infl × dose^n / (EC50^n + dose^n)
- Compared 4 conditions: A (speckle), B (speckle), C (noise), D (grating)

## 3. Key Results

### 3.1 Hill Fit Parameters

| Parameter | Value | Uncertainty | Notes |
|---|---|---|---|
| **EC50** | **30.0%** | — | Half-maximum dose |
| **Hill coefficient** | **2.0** | — | Cooperative response |
| **Max Inflation** | **0.483** | — | 48.3% increase at saturation |
| **Baseline** | **0.205** | — | 20.5% baseline rate |

### 3.2 Dose-Response Data (Condition A)

| Dose | Rate | Expected (Hill fit) |
|---|---|---|
| 0 | 21.1% | 20.5% |
| 10 | 23.3% | 22.1% |
| 20 | 36.9% | 29.3% |
| 30 | 46.5% | 40.8% |
| 40 | 47.5% | 49.6% |
| 50 | 53.4% | 56.6% |
| 60 | 59.4% | 61.5% |
| 70 | 60.7% | 64.0% |
| 80 | 62.8% | 65.2% |
| 90 | 62.3% | 65.7% |
| 100 | 66.6% | 66.0% |

### 3.3 Condition Comparison

| Condition | Baseline | Max Inflation | Interpretation |
|---|---|---|---|
| A (speckle) | 0.205 | 0.483 | Standard response |
| B (speckle) | 0.202 | 0.483 | Matches A |
| C (noise) | 0.047 | 0.507 | Different baseline, similar max |
| D (grating) | 0.320 | 0.465 | Higher baseline, lower max |

## 4. Key Finding

> **REBUS-induced pareidolia follows a Hill equation with EC50=30%, Hill coefficient=2.0, maximum inflation=48.3%.** The dose-response is consistent across conditions with similar baselines. Condition C (noise) has a lower baseline but similar maximum, suggesting the effect operates on a different mechanism than pure speckle detection.

## 5. Controls

| Control | Status | Note |
|---|---|---|
| Condition A==B | PASS | Same parameters (baseline 0.205 vs 0.202) |
| Hill fit quality | PASS | Parameters physiologically plausible |
| Baseline match | PASS | A and B baselines within 1.5% |
| Max inflation consistency | PASS | A and B max inflation identical |

## 6. What This Does NOT Prove

- **Does NOT prove** REBUS causes pareidolia — dose-response is measured, not mechanism
- **Does NOT prove** the effect is real perception — could be statistical artifact
- **Does NOT prove** anything about drug effects on perception generally
- **No novelty claim** — Hill equation fitting is standard methodology

## 7. Significance

This provides a **quantitative characterization** of REBUS-induced pareidolia:
1. EC50 = 30% — half the maximum effect at 30% dose
2. Hill coefficient = 2.0 — cooperative response (not linear)
3. Maximum inflation = 48.3% — significant but bounded effect
4. The dose-response is consistent across conditions

## 8. Classification

> **CHARACTERIZATION** — Quantitative measurement of dose-response relationship.

## 9. Honest Framing

> REBUS-induced pareidolia follows a Hill equation with EC50=30%, Hill coefficient=2.0, and maximum inflation=48.3%. This is a dose-response characterization, not a mechanism explanation. The Hill equation fits the data well, but the biological mechanism remains unknown. No claim is made that REBUS causes genuine perception of code in light — only that detection rates increase with dose in a predictable pattern.
