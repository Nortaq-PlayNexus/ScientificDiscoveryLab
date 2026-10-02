# T03_runs corrected re-derivation of the N-004 cell

- prereg `T03-RECALIBRATION` (`3d03a118ff948b99`)
- shared battery unmodified since N-004: True

| Bits | Variant | n | KS p | rej@0.01 | mean p | scorable |
|---|---|---|---|---|---|---|
| 2^18 | as_implemented | 200 | 1.413e-05 | 0 | 0.5991 | True |
| 2^18 | sqrt2_corrected | 200 | 3.431e-01 | 1 | 0.4885 | True |
| 2^18 | sqrt2_corrected_and_applicability_gated | 0 | n/a | n/a | n/a | False |
| 2^22 | as_implemented | 200 | 8.811e-06 | 0 | 0.6035 | True |
| 2^22 | sqrt2_corrected | 200 | 9.558e-01 | 3 | 0.4930 | True |
| 2^22 | sqrt2_corrected_and_applicability_gated | 0 | n/a | n/a | n/a | False |

## SP 800-22 applicability

| Bits | tau | applicable seeds | mean abs(pi-1/2) |
|---|---|---|---|
| 2^18 | 0.003906 | **0/200** | 0.000815 |
| 2^22 | 0.000977 | **0/200** | 0.000201 |

## Status of record

| Bits | N-004 recorded | Corrected status | Changed |
|---|---|---|---|
| 2^18 | calibrated | **UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION** | True |
| 2^22 | calibrated | **UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION** | True |

## Claim boundary

- that G_LAB failed a test; it did not, the test was unusable
- that any generator is certified
- that the EXP-0004 certificate is reinstated
- that the defect's non-detection at 2^22 shows the estimator is fine

N-004 recorded 0 of 24 tests miscalibrated for G_LAB, counting T03_runs as calibrated. The corrected status is UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION at both lengths, so the accurate statement is 23 of 24 per-test cells calibrated, 0 miscalibrated, and 1 unresolvable because the standard's own precondition is never met.
