# EXP-0003 independent convergence table

Ratios are winding density divided by the continuous physical-spectrum Kac–Rice prediction; intervals are 99% bootstrap intervals over 24 fields per condition.

| sigma_k | P=4 | P=6 | P=8 | P=12 | P=16 | P=24 | P=32 | P=48 | P=64 | tail P>=16 within 3% |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| 0.10 | 1.0183 | 1.0097 | 1.0091 | 1.0039 | 1.0041 | 1.0031 | 1.0027 | 0.9990 | 0.9980 | yes |
| 0.25 | 0.9935 | 1.0029 | 0.9984 | 1.0017 | 1.0007 | 1.0031 | 1.0069 | 1.0047 | 0.9975 | yes |
| 0.50 | 0.9133 | 0.9682 | 0.9854 | 0.9952 | 1.0007 | 0.9982 | 0.9957 | 1.0000 | 0.9971 | yes |
| 0.75 | 0.7966 | 0.9261 | 0.9557 | 0.9781 | 0.9865 | 0.9953 | 0.9966 | 0.9984 | 0.9966 | yes |

## Endpoint and derivative diagnostics

| sigma_k | P4 full | P64 full | endpoint abs-error improvement | P4 FD forward | P64 FD forward | P4 FD central | P64 FD central |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0.10 | 1.0183 | 0.9980 | 0.0163 | 0.8588 | 1.0066 | 0.5238 | 1.0047 |
| 0.25 | 0.9935 | 0.9975 | 0.0040 | 0.8269 | 0.9995 | 0.4785 | 0.9974 |
| 0.50 | 0.9133 | 0.9971 | 0.0838 | 0.7779 | 0.9984 | 0.3784 | 0.9954 |
| 0.75 | 0.7966 | 0.9966 | 0.2000 | 0.7164 | 0.9993 | 0.2904 | 0.9950 |
